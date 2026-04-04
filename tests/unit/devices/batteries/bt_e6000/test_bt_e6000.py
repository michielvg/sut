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
def test_empty_request_handler(bt_e6000, mock_dispatcher):
    msg = MagicMock(spec=Msg)
    msg.type = MsgType.EMPTY
    msg.seq = 0
    msg.sender = 0x40
    reply_msg = MagicMock(spec=Msg)
    msg.reply_for_msg.return_value = reply_msg

    bt_e6000.empty_request_handler(msg, mock_dispatcher, MessageDirection.RX)

    msg.reply_for_msg.assert_called_once_with(msg)
    mock_dispatcher.send_message.assert_called_once_with(reply_msg)

def test_11_msg_request_handler(bt_e6000, mock_dispatcher):
    msg = MagicMock(spec=Msg)
    reply_msg = MagicMock(spec=BT_E6000_Msg_11)
    BT_E6000_Msg_11.reply_for_msg = MagicMock(return_value=reply_msg)

    bt_e6000.msg_11_request_handler(msg, mock_dispatcher, MessageDirection.RX)

    BT_E6000_Msg_11.reply_for_msg.assert_called_once_with(msg)
    mock_dispatcher.send_message.assert_called_once_with(reply_msg)

def test_12_msg_request_handler(bt_e6000, mock_dispatcher):
    msg = MagicMock(spec=Msg)
    reply_msg = MagicMock(spec=BT_E6000_Msg_12)
    BT_E6000_Msg_12.reply_for_msg = MagicMock(return_value=reply_msg)

    bt_e6000.msg_12_request_handler(msg, mock_dispatcher, MessageDirection.RX)

    BT_E6000_Msg_12.reply_for_msg.assert_called_once_with(msg)
    mock_dispatcher.send_message.assert_called_once_with(reply_msg)

def test_telemetry_request_handler(bt_e6000, mock_dispatcher):
    msg = MagicMock(spec=Msg)
    reply_msg = MagicMock(spec=BT_E6000_TelemetryMsg)
    BT_E6000_TelemetryMsg.reply_for_msg = MagicMock(return_value=reply_msg)

    bt_e6000.telemetry_request_handler(msg, mock_dispatcher, MessageDirection.RX)

    BT_E6000_TelemetryMsg.reply_for_msg.assert_called_once_with(msg)
    mock_dispatcher.send_message.assert_called_once_with(reply_msg)

def test_shutdown_request_handler(bt_e6000, mock_dispatcher):
    msg = MagicMock(spec=Msg)
    reply_msg = MagicMock(spec=BT_E6000_ShutdownMsg)
    BT_E6000_ShutdownMsg.reply_for_msg = MagicMock(return_value=reply_msg)

    bt_e6000.shutdown_request_handler(msg, mock_dispatcher, MessageDirection.RX)

    BT_E6000_ShutdownMsg.reply_for_msg.assert_called_once_with(msg)
    mock_dispatcher.send_message.assert_called_once_with(reply_msg)

def test_msg_30_request_handler(bt_e6000, mock_dispatcher):
    msg = MagicMock(spec=Msg)
    reply_msg = MagicMock(spec=BT_E6000_Msg_30)
    BT_E6000_Msg_30.reply_for_msg = MagicMock(return_value=reply_msg)

    bt_e6000.msg_30_request_handler(msg, mock_dispatcher, MessageDirection.RX)

    BT_E6000_Msg_30.reply_for_msg.assert_called_once_with(msg)
    mock_dispatcher.send_message.assert_called_once_with(reply_msg)


def test_msg_31_request_handler(bt_e6000, mock_dispatcher):
    msg = MagicMock(spec=Msg)
    reply_msg = MagicMock(spec=BT_E6000_Msg_31)
    BT_E6000_Msg_31.reply_for_msg = MagicMock(return_value=reply_msg)

    bt_e6000.msg_31_request_handler(msg, mock_dispatcher, MessageDirection.RX)

    BT_E6000_Msg_31.reply_for_msg.assert_called_once_with(msg)
    mock_dispatcher.send_message.assert_called_once_with(reply_msg)

def test_timestamp_request_handler(bt_e6000, mock_dispatcher):
    msg = MagicMock(spec=Msg)
    reply_msg = MagicMock(spec=BT_E6000_TimeStampMsg)
    BT_E6000_TimeStampMsg.reply_for_msg = MagicMock(return_value=reply_msg)

    bt_e6000.timestamp_request_handler(msg, mock_dispatcher, MessageDirection.RX)

    BT_E6000_TimeStampMsg.reply_for_msg.assert_called_once_with(msg)
    mock_dispatcher.send_message.assert_called_once_with(reply_msg)

# ------------------------
# Test request handlers with no reply
# ------------------------
def test_request_handler_no_reply(bt_e6000, mock_dispatcher):
    msg = MagicMock(spec=Msg)
    msg.sender = 0x40
    msg.reply_for_msg.return_value = None

    bt_e6000.empty_request_handler(msg, mock_dispatcher, MessageDirection.RX)
    mock_dispatcher.send_message.assert_not_called()


# ------------------------
# Test setup subscription
# ------------------------
def test_setup_subscribes_handlers(mock_dispatcher):
    bt = BT_E6000(dispatcher=mock_dispatcher)
    bt.setup()

    mock_dispatcher.subscribe.assert_any_call(MsgType.EMPTY, bt.empty_request_handler, MessageDirection.RX)
    mock_dispatcher.subscribe.assert_any_call(MsgType.TELEMETRY, bt.telemetry_request_handler, MessageDirection.RX)
    mock_dispatcher.subscribe.assert_any_call(MsgType.MSG_30, bt.msg_30_request_handler, MessageDirection.RX)
    mock_dispatcher.subscribe.assert_any_call(MsgType.MSG_31, bt.msg_31_request_handler, MessageDirection.RX)

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
def test_request_handler_wrong_type(bt_e6000, mock_dispatcher):
    msg = MagicMock(spec=Msg)
    msg.sender = 0x40
    msg.type = MsgType.MSG_30  # call empty handler with wrong type
    msg.reply_for_msg.return_value = MagicMock()

    # Should not crash
    bt_e6000.empty_request_handler(msg, mock_dispatcher, MessageDirection.RX)