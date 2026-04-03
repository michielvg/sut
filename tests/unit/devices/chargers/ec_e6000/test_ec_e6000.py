# tests/devices/chargers/test_ec_e6000.py
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
    return EC_E6000(dispatcher=mock_dispatcher)


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
    msg = MagicMock(spec=Msg)
    msg.sender = 0x40 | 0x80
    charger.msg_30_response_handler(msg, None, MessageDirection.RX)
    assert charger.state == ChargerState.MSG_30_RESP_RECEIVED


def test_msg_31_response_transitions(charger):
    charger.state = ChargerState.MSG_30_RESP_RECEIVED
    msg = MagicMock(spec=Msg)
    msg.sender = 0x40 | 0x80
    charger.msg_31_response_handler(msg, None, MessageDirection.RX)
    assert charger.state == ChargerState.POLLING


def test_telemetry_response_does_nothing(charger):
    msg = MagicMock(spec=Msg)
    msg.sender = 0x40 | 0x80
    # Just makes sure telemetry handler doesn't crash
    charger.telemetry_response_handler(MagicMock(spec=Msg), None, MessageDirection.RX)


# ------------------------
# Poll behavior
# ------------------------
@patch("time.time")
def test_poll_disconnected_sends_empty(mock_time, charger, mock_dispatcher):
    charger.state = ChargerState.DISCONNECTED
    charger.last_poll_time = 0
    mock_time.return_value = 10

    charger.poll()
    sent_msg = mock_dispatcher.send_message.call_args[0][0]
    assert isinstance(sent_msg, Msg)


def test_empty_response_triggers_msg_30(charger, mock_dispatcher):
    from devices.chargers.ec_e6000.messages.msg_30 import EC_E6000_Msg_30

    charger.state = ChargerState.DISCONNECTED

    msg = MagicMock(spec=Msg)
    msg.sender = 0x40 | 0x80

    charger.empty_response_handler(msg, mock_dispatcher, MessageDirection.RX)

    sent_msg = mock_dispatcher.send_message.call_args[0][0]
    assert isinstance(sent_msg, EC_E6000_Msg_30)

def test_msg_30_response_triggers_msg_31(charger, mock_dispatcher):
    from devices.chargers.ec_e6000.messages.msg_31 import EC_E6000_Msg_31

    charger.state = ChargerState.CONNECTED

    msg = MagicMock(spec=Msg)
    msg.sender = 0x40 | 0x80

    charger.msg_30_response_handler(msg, mock_dispatcher, MessageDirection.RX)

    sent_msg = mock_dispatcher.send_message.call_args[0][0]
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
    mock_time.return_value = 10
    charger.poll()

    # Second call within 1 second → should NOT send
    mock_time.return_value = 10.5
    charger.poll()
    assert mock_dispatcher.send_message.call_count == 1


# ------------------------
# Edge cases
# ------------------------
def test_empty_response_wrong_sender_does_not_connect(charger):
    charger.state = ChargerState.DISCONNECTED
    msg = MagicMock(spec=Msg)
    msg.sender = 0x00  # Not the expected sender

    charger.empty_response_handler(msg, None, MessageDirection.RX)
    assert charger.state == ChargerState.DISCONNECTED


def test_poll_unknown_state_sends_nothing(mock_dispatcher, charger):
    # Force an invalid state
    charger.state = None
    charger.last_poll_time = 0
    from time import time
    t0 = time()
    with patch("time.time", return_value=t0):
        charger.poll()
    assert not mock_dispatcher.send_message.called

# ------------------------
# Test full state flow (event-driven)
# ------------------------
def test_full_handshake_flow(charger, mock_dispatcher):
    """Charger should progress through full handshake and send correct messages."""

    from devices.chargers.ec_e6000.messages.msg_30 import EC_E6000_Msg_30
    from devices.chargers.ec_e6000.messages.msg_31 import EC_E6000_Msg_31
    from devices.chargers.ec_e6000.messages.telemetry import EC_E6000_TelemetryMsg

    # Start disconnected
    charger.state = ChargerState.DISCONNECTED

    # Step 1: receive EMPTY response → CONNECTED + send MSG_30
    empty_msg = MagicMock(spec=Msg)
    empty_msg.sender = 0x40 | 0x80

    charger.empty_response_handler(empty_msg, mock_dispatcher, MessageDirection.RX)

    assert charger.state == ChargerState.CONNECTED
    sent_msg = mock_dispatcher.send_message.call_args_list[-1][0][0]
    assert isinstance(sent_msg, EC_E6000_Msg_30)

    # Step 2: receive MSG_30 → MSG_30_RESP_RECEIVED + send MSG_31
    msg30 = MagicMock(spec=Msg)
    msg30.sender = 0x40 | 0x80

    charger.msg_30_response_handler(msg30, mock_dispatcher, MessageDirection.RX)

    assert charger.state == ChargerState.MSG_30_RESP_RECEIVED
    sent_msg = mock_dispatcher.send_message.call_args_list[-1][0][0]
    assert isinstance(sent_msg, EC_E6000_Msg_31)

    # Step 3: receive MSG_31 → POLLING + send TELEMETRY
    msg31 = MagicMock(spec=Msg)
    msg31.sender = 0x40 | 0x80
    
    charger.msg_31_response_handler(msg31, mock_dispatcher, MessageDirection.RX)

    assert charger.state == ChargerState.POLLING
    sent_msg = mock_dispatcher.send_message.call_args_list[-1][0][0]
    assert isinstance(sent_msg, EC_E6000_TelemetryMsg)