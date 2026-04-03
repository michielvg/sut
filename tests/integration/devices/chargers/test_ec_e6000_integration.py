# tests/integration/devices/chargers/test_ec_e6000_integration.py
import pytest
import time

from devices.charger import ChargerState
from devices.chargers.ec_e6000.ec_e6000 import EC_E6000
from devices.chargers.ec_e6000.messages.telemetry import EC_E6000_TelemetryMsg
from devices.chargers.ec_e6000.messages.msg_30 import EC_E6000_Msg_30
from devices.chargers.ec_e6000.messages.msg_31 import EC_E6000_Msg_31
from message_dispatcher import MessageDispatcher, MessageDirection
from uart.mock_uart import MockUART
from messages.message import Msg, MsgType


@pytest.fixture
def mock_uart():
    return MockUART()


@pytest.fixture
def dispatcher(mock_uart):
    return MessageDispatcher(uart=mock_uart)


@pytest.fixture
def charger(dispatcher):
    ec = EC_E6000(dispatcher)
    return ec


def test_charger_initial_state(charger):
    assert charger.state == ChargerState.DISCONNECTED


def test_charger_state_transition_empty_response(charger, dispatcher):
    # Charger should go from DISCONNECTED -> CONNECTED upon receiving proper EMPTY response
    msg = Msg()
    msg.type = MsgType.EMPTY
    msg.sender = 0xC0  # 0x40 | 0x80 to trigger empty_response_handler

    charger.empty_response_handler(msg, dispatcher, MessageDirection.RX)
    assert charger.state == ChargerState.CONNECTED


def test_charger_state_transition_msg_30(charger, dispatcher):
    # Simulate charger is CONNECTED
    charger.state = ChargerState.CONNECTED
    msg = Msg()
    msg.sender = 0x40 | 0x80

    charger.msg_30_response_handler(msg, dispatcher, MessageDirection.RX)
    assert charger.state == ChargerState.MSG_30_RESP_RECEIVED


def test_charger_state_transition_msg_31(charger, dispatcher):
    # Simulate charger is MSG_30_RESP_RECEIVED
    charger.state = ChargerState.MSG_30_RESP_RECEIVED
    msg = Msg()
    msg.sender = 0x40 | 0x80

    charger.msg_31_response_handler(msg, dispatcher, MessageDirection.RX)
    assert charger.state == ChargerState.POLLING


def test_charger_full_flow(charger, dispatcher):
    from devices.chargers.ec_e6000.messages.msg_30 import EC_E6000_Msg_30
    from devices.chargers.ec_e6000.messages.msg_31 import EC_E6000_Msg_31
    from devices.chargers.ec_e6000.messages.telemetry import EC_E6000_TelemetryMsg

    # ------------------------
    # Step 1: poll() → send EMPTY
    # ------------------------
    charger.state = ChargerState.DISCONNECTED
    charger.last_poll_time = 0
    charger.poll() # enqueues initial ping, and should do that ever n time until it gets a reply.
    dispatcher.poll() # forwards data to uart buffer.
    assert dispatcher.uart.buffer == b'\x00\x40\x00\x21\x49'
    dispatcher.uart.buffer.clear()

    # ------------------------
    # Step 2: receive EMPTY response → send MSG_30
    # ------------------------
    msg = Msg()
    msg.sender = 0x40 | 0x80

    charger.empty_response_handler(msg, dispatcher, MessageDirection.RX) # enqueus new message
    assert charger.state == ChargerState.CONNECTED
    dispatcher.poll() # forward to uart buffer
    assert dispatcher.uart.buffer == EC_E6000_Msg_30().pack()
    dispatcher.uart.buffer.clear()

    # ------------------------
    # Step 3: receive MSG_30 → send MSG_31
    # ------------------------
    msg = Msg()
    msg.type = MsgType.MSG_30
    msg.sender = 0x40 | 0x80

    charger.msg_30_response_handler(msg, dispatcher, MessageDirection.RX)
    assert charger.state == ChargerState.MSG_30_RESP_RECEIVED
    
    dispatcher.poll() # forward to uart buffer
    assert dispatcher.uart.buffer == EC_E6000_Msg_31().pack()
    dispatcher.uart.buffer.clear()

    # ------------------------
    # Step 4: receive MSG_31 → send TELEMETRY
    # ------------------------
    msg = Msg()
    msg.type = MsgType.MSG_31
    msg.sender = 0x40 | 0x80

    charger.msg_31_response_handler(msg, dispatcher, MessageDirection.RX)
    assert charger.state == ChargerState.POLLING
    
    dispatcher.poll() # forward to uart buffer
    assert dispatcher.uart.buffer == EC_E6000_TelemetryMsg().pack()
    dispatcher.uart.buffer.clear()

    # ------------------------
    # Step 5: poll() in POLLING → send TELEMETRY again
    # ------------------------
    charger.last_poll_time = 0
    charger.poll()

    dispatcher.poll() # forward to uart buffer
    assert dispatcher.uart.buffer == EC_E6000_TelemetryMsg().pack()
    dispatcher.uart.buffer.clear()
