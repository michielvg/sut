# tests/integration/test_charger_battery_interaction.py
import pytest
from sut.devices.chargers.ec_e6000.ec_e6000 import EC_E6000
from sut.devices.chargers.ec_e6000.messages.msg_30 import EC_E6000_Msg_30
from sut.devices.chargers.ec_e6000.messages.msg_31 import EC_E6000_Msg_31
from sut.devices.chargers.ec_e6000.messages.telemetry import EC_E6000_TelemetryMsg
from sut.devices.batteries.bt_e6000.bt_e6000 import BT_E6000
from sut.devices.batteries.bt_e6000.messages.msg_30 import BT_E6000_Msg_30
from sut.devices.batteries.bt_e6000.messages.msg_31 import BT_E6000_Msg_31
from sut.devices.batteries.bt_e6000.messages.telemetry import BT_E6000_TelemetryMsg
from sut.messages.message import Msg, MsgType
from sut.message_dispatcher import MessageDispatcher, MessageDirection
from sut.devices.charger import ChargerState
from sut.uart.mock_uart import MockUART


@pytest.fixture
def dispatcher():
    uart = MockUART()
    return MessageDispatcher(uart)

@pytest.fixture
def charger(dispatcher):
    ec = EC_E6000(dispatcher)
    return ec

@pytest.fixture
def battery(dispatcher):
    bt = BT_E6000(dispatcher)
    return bt


def test_charger_battery_interaction(charger, battery, dispatcher):
    """
    Simulate a simple charger ↔ battery interaction using the dispatcher
    """

    # Step 1: Charger is disconnected, first poll sends EMPTY
    charger.state = ChargerState.DISCONNECTED
    charger.poll() # Enqueues ping msg
    dispatcher.poll() # Sends the message to UART
    msg = Msg()
    msg.sender = 0x40
    assert dispatcher.uart.buffer == msg.pack()
    dispatcher.poll() # Handle reception of charger message, sends to battery, enqueues battery message. 
    # dispatcher handles flush after receive, so the batteries message should directly be in the uart.
    msg = Msg()
    msg.sender = 0x40 | 0x80
    assert dispatcher.uart.buffer == msg.pack()
    
    dispatcher.poll() # reception of battery message, send to charger, enqueue charger message.
    assert dispatcher.uart.buffer == EC_E6000_Msg_30().pack() # Charger enqueues out msg 30
    assert charger.state == ChargerState.CONNECTED

    dispatcher.poll() # reception of charger message, send to battery, enqueue battery message.
    msg = BT_E6000_Msg_30()
    msg.sender = 0x40 | 0x80
    assert dispatcher.uart.buffer == msg.pack()

    dispatcher.poll() # reception of battery message, send to charger, enqueue charger message.
    assert dispatcher.uart.buffer == EC_E6000_Msg_31().pack() # Charger enqueues out msg 30
    assert charger.state == ChargerState.MSG_30_RESP_RECEIVED

    dispatcher.poll() # reception of charger message, send to battery, enqueue battery message.
    msg = BT_E6000_Msg_31()
    msg.sender = 0x40 | 0x80
    assert dispatcher.uart.buffer == msg.pack()

    dispatcher.poll() # reception of battery message, send to charger, enqueue charger message.
    assert dispatcher.uart.buffer == EC_E6000_TelemetryMsg().pack() # Charger enqueues out msg 30
    assert charger.state == ChargerState.POLLING

    dispatcher.poll() # reception of charger message, send to battery, enqueue battery message.
    msg = BT_E6000_TelemetryMsg()
    msg.sender = 0x40 | 0x80
    assert dispatcher.uart.buffer == msg.pack()