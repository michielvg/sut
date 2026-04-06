# tests/devices/batteries/test_bt_e6000.py
import pytest
from unittest.mock import MagicMock

from sut.devices.batteries import BT_E6000
from sut.devices.batteries.bt_e6000.messages import *
from sut.devices.batteries.bt_e6000.messages.msg_11 import BT_E6000_Msg_11
from sut.devices.batteries.bt_e6000.messages.msg_12 import BT_E6000_Msg_12
from sut.devices.batteries.bt_e6000.messages.shutdown import BT_E6000_ShutdownMsg
from sut.devices.batteries.bt_e6000.messages.timestamp import BT_E6000_TimeStampMsg
from sut.messages import Msg, MsgType
from sut.message_dispatcher import MessageDispatcher, MessageDirection
from sut.messages.empty import EmptyMsg


# ------------------------
# Fixtures
# ------------------------
@pytest.fixture
def mock_dispatcher():
    dispatcher = MagicMock(spec=MessageDispatcher)
    return dispatcher


@pytest.fixture
def bt_e6000(mock_dispatcher):
    return BT_E6000(mock_dispatcher)


# ------------------------
# Test request handlers
# ------------------------
@pytest.mark.parametrize("msg_type,msg_cls", [
    (MsgType.EMPTY, EmptyMsg),
    (MsgType.TELEMETRY, BT_E6000_TelemetryMsg),
    (MsgType.MSG_11, BT_E6000_Msg_11),
    (MsgType.MSG_12, BT_E6000_Msg_12),
    (MsgType.SHUTDOWN, BT_E6000_ShutdownMsg),
    (MsgType.MSG_30, BT_E6000_Msg_30),
    (MsgType.MSG_31, BT_E6000_Msg_31),
    (MsgType.TIMESTAMP, BT_E6000_TimeStampMsg)
])
def test_generic_request_handler_replies(bt_e6000, mock_dispatcher, monkeypatch, msg_type, msg_cls):
    msg = MagicMock(spec=Msg)
    msg.type = msg_type
    msg.seq = 0
    msg.sender = 0x40

    reply_msg = MagicMock(spec=msg_cls)

    monkeypatch.setattr(
        msg_cls,
        "reply_for_msg",
        MagicMock(return_value=reply_msg)
    )

    bt_e6000._msg_map[msg_type] = msg_cls

    bt_e6000._generic_request_handler(msg, mock_dispatcher, MessageDirection.RX)

    msg_cls.reply_for_msg.assert_called_once_with(msg)
    mock_dispatcher.send_message.assert_called_once_with(reply_msg)

# ------------------------
# Test request handlers with no reply
# ------------------------
@pytest.mark.parametrize("msg_type,msg_cls", [
    (MsgType.EMPTY, EmptyMsg),
    (MsgType.TELEMETRY, BT_E6000_TelemetryMsg),
    (MsgType.MSG_11, BT_E6000_Msg_11),
    (MsgType.MSG_12, BT_E6000_Msg_12),
    (MsgType.SHUTDOWN, BT_E6000_ShutdownMsg),
    (MsgType.MSG_30, BT_E6000_Msg_30),
    (MsgType.MSG_31, BT_E6000_Msg_31),
    (MsgType.TIMESTAMP, BT_E6000_TimeStampMsg)
])
def test_generic_request_handler_no_replies(bt_e6000, mock_dispatcher, monkeypatch, msg_type, msg_cls):
    msg = MagicMock(spec=Msg)
    msg.type = msg_type
    msg.seq = 0
    msg.sender = 0x40

    reply_msg = MagicMock(spec=msg_cls)

    monkeypatch.setattr(
        msg_cls,
        "reply_for_msg",
        MagicMock(return_value=None)
    )

    bt_e6000._msg_map[msg_type] = msg_cls

    bt_e6000._generic_request_handler(msg, mock_dispatcher, MessageDirection.RX)

    mock_dispatcher.send_message.assert_not_called()

# ------------------------
# Test setup subscription
# ------------------------
@pytest.mark.parametrize("msg_type,msg_cls", [
    (MsgType.EMPTY, EmptyMsg),
    (MsgType.TELEMETRY, BT_E6000_TelemetryMsg),
    (MsgType.MSG_11, BT_E6000_Msg_11),
    (MsgType.MSG_12, BT_E6000_Msg_12),
    (MsgType.SHUTDOWN, BT_E6000_ShutdownMsg),
    (MsgType.MSG_30, BT_E6000_Msg_30),
    (MsgType.MSG_31, BT_E6000_Msg_31),
    (MsgType.TIMESTAMP, BT_E6000_TimeStampMsg)
])
def test_setup_subscribes_handlers(mock_dispatcher, msg_type, msg_cls):
    bt = BT_E6000(dispatcher=mock_dispatcher)

    mock_dispatcher.subscribe.assert_any_call(msg_type, bt._generic_request_handler, MessageDirection.RX)

# ------------------------
# Test setup idempotence
# ------------------------
def test_setup_idempotent(bt_e6000):
    # Calling setup multiple times should not raise
    bt_e6000.setup()
    bt_e6000.setup()


# ------------------------
# Test request handlers called with different MsgType
# ------------------------
@pytest.mark.parametrize("msg_type,msg_cls", [
    (MsgType.EMPTY, EmptyMsg),
    (MsgType.TELEMETRY, BT_E6000_TelemetryMsg),
    (MsgType.MSG_11, BT_E6000_Msg_11),
    (MsgType.MSG_12, BT_E6000_Msg_12),
    (MsgType.SHUTDOWN, BT_E6000_ShutdownMsg),
    (MsgType.MSG_30, BT_E6000_Msg_30),
    (MsgType.MSG_31, BT_E6000_Msg_31),
    (MsgType.TIMESTAMP, BT_E6000_TimeStampMsg)
])
def test_request_handler_wrong_type(bt_e6000, mock_dispatcher, msg_type, msg_cls):
    msg = MagicMock(spec=Msg)
    msg.sender = 0x40
    msg.type = MsgType.PROXY  # call empty handler with wrong type
    msg.reply_for_msg.return_value = MagicMock()

    # Should not crash
    bt_e6000._generic_request_handler(msg, mock_dispatcher, MessageDirection.RX)