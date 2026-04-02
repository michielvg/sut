import pytest
from unittest.mock import MagicMock, patch

from devices.chargers import EC_E6000
from devices.charger import ChargerState
from messages.message import Msg, MsgType
from message_dispatcher import MessageDirection


# ------------------------
# Fixtures
# ------------------------
@pytest.fixture
def mock_dispatcher():
    return MagicMock()


@pytest.fixture
def charger(mock_dispatcher):
    ch = EC_E6000(dispatcher=mock_dispatcher)
    return ch


# ------------------------
# Setup tests
# ------------------------
def test_setup_subscribes_handlers(charger, mock_dispatcher):
    charger.setup()

    mock_dispatcher.subscribe.assert_any_call(MsgType.EMPTY, charger.empty_response_handler, MessageDirection.RX)
    mock_dispatcher.subscribe.assert_any_call(MsgType.MSG_30, charger.msg_30_response_handler, MessageDirection.RX)
    mock_dispatcher.subscribe.assert_any_call(MsgType.MSG_31, charger.msg_31_response_handler, MessageDirection.RX)
    mock_dispatcher.subscribe.assert_any_call(MsgType.TELEMETRY, charger.telemetry_response_handler, MessageDirection.RX)


# ------------------------
# Handler state transitions
# ------------------------
def test_empty_response_transitions_to_connected(charger):
    charger.state = ChargerState.DISCONNECTED

    msg = MagicMock(spec=Msg)
    msg.sender = 0x40 | 0x80

    charger.empty_response_handler(msg, None, MessageDirection.RX)

    assert charger.state == ChargerState.CONNECTED


def test_msg_30_response_transitions(charger):
    charger.state = ChargerState.CONNECTED

    charger.msg_30_response_handler(MagicMock(spec=Msg), None, MessageDirection.RX)

    assert charger.state == ChargerState.MSG_30_RESP_RECEIVED


def test_msg_31_response_transitions(charger):
    charger.state = ChargerState.MSG_30_RESP_RECEIVED

    charger.msg_31_response_handler(MagicMock(spec=Msg), None, MessageDirection.RX)

    assert charger.state == ChargerState.POLLING


# ------------------------
# Poll behavior
# ------------------------
@patch("time.time")
def test_poll_disconnected_sends_empty(mock_time, charger, mock_dispatcher):
    charger.state = ChargerState.DISCONNECTED
    charger.last_poll_time = 0

    mock_time.return_value = 10

    charger.poll()

    assert mock_dispatcher.send_message.called


@patch("time.time")
def test_poll_connected_sends_msg_30(mock_time, charger, mock_dispatcher):
    charger.state = ChargerState.CONNECTED
    charger.last_poll_time = 0

    mock_time.return_value = 10

    charger.poll()

    sent_msg = mock_dispatcher.send_message.call_args[0][0]
    from devices.chargers.ec_e6000.messages.msg_30 import EC_E6000_Msg_30
    assert isinstance(sent_msg, EC_E6000_Msg_30)


@patch("time.time")
def test_poll_msg_30_received_sends_msg_31(mock_time, charger, mock_dispatcher):
    charger.state = ChargerState.MSG_30_RESP_RECEIVED
    charger.last_poll_time = 0

    mock_time.return_value = 10

    charger.poll()

    sent_msg = mock_dispatcher.send_message.call_args[0][0]
    from devices.chargers.ec_e6000.messages.msg_31 import EC_E6000_Msg_31
    assert isinstance(sent_msg, EC_E6000_Msg_31)


@patch("time.time")
def test_poll_polling_sends_telemetry(mock_time, charger, mock_dispatcher):
    charger.state = ChargerState.POLLING
    charger.last_poll_time = 0

    mock_time.return_value = 10

    charger.poll()

    sent_msg = mock_dispatcher.send_message.call_args[0][0]
    from devices.chargers.ec_e6000.messages.telemetry import EC_E6000_TelemetryMsg
    assert isinstance(sent_msg, EC_E6000_TelemetryMsg)


@patch("time.time")
def test_poll_rate_limiting(mock_time, charger, mock_dispatcher):
    charger.state = ChargerState.POLLING

    # First call
    mock_time.return_value = 10
    charger.poll()

    # Second call within 1 second → should NOT send
    mock_time.return_value = 10.5
    charger.poll()

    assert mock_dispatcher.send_message.call_count == 1