# tests/test_bt_e6000.py
import pytest
from unittest.mock import MagicMock

from devices.batteries import BT_E6000
from devices.batteries.bt_e6000.messages import *
from messages import Msg, MsgType
from message_dispatcher import MessageDispatcher, MessageDirection


@pytest.fixture
def mock_dispatcher():
    dispatcher = MagicMock(spec=MessageDispatcher)
    return dispatcher

@pytest.fixture
def bt_e6000(mock_dispatcher):
    return BT_E6000(mock_dispatcher)


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


def test_telemetry_request_handler(bt_e6000, mock_dispatcher):
    msg = MagicMock(spec=Msg)
    reply_msg = MagicMock(spec=BT_E6000_TelemetryMsg)
    BT_E6000_TelemetryMsg.reply_for_msg = MagicMock(return_value=reply_msg)

    bt_e6000.telemetry_request_handler(msg, mock_dispatcher, MessageDirection.RX)

    BT_E6000_TelemetryMsg.reply_for_msg.assert_called_once_with(msg)
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


def test_setup_subscribes_handlers(mock_dispatcher):
    from devices.batteries import BT_E6000
    bt = BT_E6000(dispatcher=mock_dispatcher)

    bt.setup()

    mock_dispatcher.subscribe.assert_any_call(MsgType.EMPTY, bt.empty_request_handler, MessageDirection.RX, bt)
    mock_dispatcher.subscribe.assert_any_call(MsgType.TELEMETRY, bt.telemetry_request_handler, MessageDirection.RX, bt)
    mock_dispatcher.subscribe.assert_any_call(MsgType.MSG_30, bt.msg_30_request_handler, MessageDirection.RX, bt)
    mock_dispatcher.subscribe.assert_any_call(MsgType.MSG_31, bt.msg_31_request_handler, MessageDirection.RX, bt)