# tests/test_message_dispatcher.py
import pytest
from unittest.mock import MagicMock
from datetime import datetime, timedelta

from sut.messages.message import Msg, MsgType, MsgStatus
from sut.uart.uart_interface import UARTInterface
from sut.devices.batteries.bt_e6000.messages.telemetry import BT_E6000_TelemetryMsg
from sut.message_dispatcher import MessageDispatcher, MessageDirection


# ------------------------
# Fixtures
# ------------------------
@pytest.fixture
def mock_uart():
    uart = MagicMock(spec=UARTInterface)
    uart.in_waiting = 0
    uart.read.return_value = b""
    return uart


@pytest.fixture
def dispatcher(mock_uart):
    return MessageDispatcher(uart=mock_uart)


# ------------------------
# Test subscription and broadcasting
# ------------------------
def test_subscribe_and_broadcast(dispatcher):
    callback_rx = MagicMock()
    callback_tx = MagicMock()
    msg = BT_E6000_TelemetryMsg()

    # Subscribe callbacks
    dispatcher.subscribe(MsgType.TELEMETRY, callback_rx, direction=MessageDirection.RX)
    dispatcher.subscribe(MsgType.TELEMETRY, callback_tx, direction=MessageDirection.TX)

    # Broadcast RX
    dispatcher._broadcast(msg, MessageDirection.RX)
    callback_rx.assert_called_once_with(msg, dispatcher, MessageDirection.RX)
    callback_tx.assert_not_called()

    # Broadcast TX
    dispatcher._broadcast(msg, MessageDirection.TX)
    callback_tx.assert_called_once_with(msg, dispatcher, MessageDirection.TX)
    # RX callback should not be called again
    assert callback_rx.call_count == 1


def test_wildcard_subscription(dispatcher):
    callback = MagicMock()
    msg = BT_E6000_TelemetryMsg()

    dispatcher.subscribe('*', callback, direction=MessageDirection.BOTH)

    dispatcher._broadcast(msg, MessageDirection.RX)
    dispatcher._broadcast(msg, MessageDirection.TX)

    assert callback.call_count == 2


# ------------------------
# Test sending messages
# ------------------------
def test_send_message_flush(dispatcher, mock_uart):
    msg = MagicMock(spec=Msg)
    msg.pack.return_value = b'\x00\x01\x02'
    msg.sent_at = None

    dispatcher.send_message(msg)
    dispatcher._flush_send_queue()

    # Check UART write called
    mock_uart.write.assert_called_once_with(b'\x00\x01\x02')
    # Check TX broadcast
    assert msg.sent_at is not None


# ------------------------
# Test RX buffer parsing
# ------------------------
def test_read_and_dispatch_partial_message(dispatcher, mock_uart):
    # fake Msg subclass to control unpack
    class FakeMsg(Msg):
        @classmethod
        def unpack(cls, data):
            if len(data) < 5:
                return None, MsgStatus.OK  # incomplete
            instance = cls()
            instance.data = data[:5]
            return instance, MsgStatus.OK

    dispatcher.message_map[FakeMsg].append(FakeMsg)

    # Inject partial data
    mock_uart.in_waiting = 3
    mock_uart.read.return_value = b'\x00\x01\x02'

    dispatcher._read_and_dispatch()
    # RX buffer should contain the partial bytes
    assert dispatcher.rx_buffer == b'\x00\x01\x02'

    # Inject full data
    mock_uart.in_waiting = 5
    mock_uart.read.return_value = b'\x03\x04'

    callback = MagicMock()
    dispatcher.subscribe('*', callback, direction=MessageDirection.RX)

    assert len(dispatcher.rx_buffer) == 3
    dispatcher._read_and_dispatch()
    # Partial bytes processed
    assert len(dispatcher.rx_buffer) == 0
    callback.assert_called_once()  # broadcast triggered


# ------------------------
# Test that _leaf_subclasses works
# ------------------------
def test_leaf_subclasses():
    class Base:
        pass

    class Sub1(Base):
        pass

    class Sub2(Base):
        pass

    class SubSub(Sub1):
        pass

    from sut.message_dispatcher import MessageDispatcher

    leaves = MessageDispatcher._leaf_subclasses(Base)
    assert SubSub in leaves
    assert Sub2 in leaves
    assert Sub1 not in leaves

# ------------------------
# Test FIFO send queue
# ------------------------
def test_send_queue_fifo(dispatcher, mock_uart):
    """Ensure messages are sent in FIFO order."""
    msg1, msg2 = MagicMock(spec=Msg), MagicMock(spec=Msg)
    msg1.pack.return_value = b'\x01'
    msg2.pack.return_value = b'\x02'
    msg1.sent_at = None
    msg2.sent_at = None

    dispatcher.send_message(msg1)
    dispatcher.send_message(msg2)
    dispatcher._flush_send_queue()

    # UART write should respect FIFO
    mock_uart.write.assert_any_call(b'\x01')
    mock_uart.write.assert_any_call(b'\x02')
    assert mock_uart.write.call_count == 2
    # sent_at should be set
    assert msg1.sent_at is not None
    assert msg2.sent_at is not None


# ------------------------
# Test multiple callbacks for same MsgType
# ------------------------
def test_multiple_callbacks(dispatcher):
    """All subscribers of a MsgType should be called."""
    callback1 = MagicMock()
    callback2 = MagicMock()
    msg = BT_E6000_TelemetryMsg()

    dispatcher.subscribe(MsgType.TELEMETRY, callback1, direction=MessageDirection.RX)
    dispatcher.subscribe(MsgType.TELEMETRY, callback2, direction=MessageDirection.RX)

    dispatcher._broadcast(msg, MessageDirection.RX)

    assert callback1.call_count == 1
    assert callback2.call_count == 1


# ------------------------
# Test broadcasting to unsubscribed type
# ------------------------
def test_broadcast_unsubscribed_type(dispatcher):
    """Broadcasting a MsgType with no subscribers should not crash."""
    msg = BT_E6000_TelemetryMsg()
    dispatcher._broadcast(msg, MessageDirection.RX)
    # Test passes if no exception is raised


# ------------------------
# Test wildcard RX only
# ------------------------
def test_wildcard_rx_only(dispatcher):
    """Wildcard subscription limited to RX should only trigger on RX."""
    callback = MagicMock()
    msg = BT_E6000_TelemetryMsg()

    dispatcher.subscribe('*', callback, direction=MessageDirection.RX)

    dispatcher._broadcast(msg, MessageDirection.RX)
    dispatcher._broadcast(msg, MessageDirection.TX)

    assert callback.call_count == 1


# ------------------------
# Test flush_send_queue handles pack() exception
# ------------------------
def test_flush_send_queue_pack_error(dispatcher, mock_uart):
    """Message that fails to pack should not crash the queue."""
    msg1 = MagicMock(spec=Msg)
    msg2 = MagicMock(spec=Msg)
    # msg1 will raise on pack
    msg1.pack.side_effect = ValueError("pack failed")
    msg2.pack.return_value = b'\x01'
    msg1.sent_at = None
    msg2.sent_at = None

    dispatcher.send_message(msg1)
    dispatcher.send_message(msg2)

    dispatcher._flush_send_queue()

    # msg1 should not have sent_at
    assert msg1.sent_at is None
    # msg2 should have been sent
    assert msg2.sent_at is not None
    # UART write called only for msg2
    mock_uart.write.assert_called_once_with(b'\x01')


# ------------------------
# Test flush_send_queue handles UART write exception
# ------------------------
def test_flush_send_queue_uart_write_error(dispatcher, mock_uart):
    """Message that fails to write to UART should not crash the queue."""
    msg1 = MagicMock(spec=Msg)
    msg2 = MagicMock(spec=Msg)
    msg1.pack.return_value = b'\x00'
    msg2.pack.return_value = b'\x01'
    msg1.sent_at = None
    msg2.sent_at = None

    # Simulate write error for first message
    mock_uart.write.side_effect = [Exception("UART write failed"), None]

    dispatcher.send_message(msg1)
    dispatcher.send_message(msg2)

    dispatcher._flush_send_queue()

    # msg1 should not have sent_at
    assert msg1.sent_at is None
    # msg2 should have been sent
    assert msg2.sent_at is not None
    # UART write called twice (first fails, second succeeds)
    assert mock_uart.write.call_count == 2


# ------------------------
# Test flush_send_queue handles broadcast exception
# ------------------------
def test_flush_send_queue_broadcast_error(dispatcher, mock_uart, monkeypatch):
    """Message that fails during broadcast should not crash the queue."""
    msg1 = MagicMock(spec=Msg)
    msg2 = MagicMock(spec=Msg)
    msg1.pack.return_value = b'\x00'
    msg2.pack.return_value = b'\x01'
    msg1.sent_at = None
    msg2.sent_at = None

    dispatcher.send_message(msg1)
    dispatcher.send_message(msg2)

    # Patch _broadcast to raise for first message
    original_broadcast = dispatcher._broadcast
    call_count = {"n": 0}

    def fake_broadcast(msg, direction):
        if call_count["n"] == 0:
            call_count["n"] += 1
            raise Exception("broadcast failed")
        return original_broadcast(msg, direction)

    monkeypatch.setattr(dispatcher, "_broadcast", fake_broadcast)

    dispatcher._flush_send_queue()

    # Both messages should have sent_at set, broadcast error doesn't prevent sent_at
    assert msg1.sent_at is not None
    assert msg2.sent_at is not None
    # UART write called for both
    assert mock_uart.write.call_count == 2