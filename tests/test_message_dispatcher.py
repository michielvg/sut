# tests/test_message_dispatcher.py
import pytest
from unittest.mock import MagicMock
from datetime import datetime, timedelta

from messages.message import Msg, MsgType, MsgStatus
from uart.uart_interface import UARTInterface
from devices.batteries.bt_e6000.messages.telemetry import BT_E6000_TelemetryMsg
from message_dispatcher import MessageDispatcher, MessageDirection


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

    from message_dispatcher import MessageDispatcher

    leaves = MessageDispatcher._leaf_subclasses(Base)
    assert SubSub in leaves
    assert Sub2 in leaves
    assert Sub1 not in leaves