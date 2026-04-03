# tests/integration/devices/chargers/test_ec_e6000_integration.py
import pytest

from devices.batteries.bt_e6000.bt_e6000 import BT_E6000
from devices.batteries.bt_e6000.messages.msg_30 import BT_E6000_Msg_30
from devices.batteries.bt_e6000.messages.msg_31 import BT_E6000_Msg_31
from devices.batteries.bt_e6000.messages.telemetry import BT_E6000_TelemetryMsg
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
def battery(dispatcher):
    ec = BT_E6000(dispatcher)
    return ec

def test_empty_request_handler(dispatcher, battery):
    msg = Msg()
    msg.sender = 0x40
    msg.type = MsgType.EMPTY

    dispatcher.send_message(msg)
    dispatcher.poll() # Sends the message
    dispatcher.poll() # receives, passes to battery, replies, sends reply

    reply = Msg()
    reply.sender = 0x40 | 0x80
    reply.type = MsgType.EMPTY

    assert dispatcher.uart.buffer == reply.pack()

def test_telemetry_request_handler(dispatcher, battery):
    class FakeTelemetryMsg(Msg):
        FORMAT = ''  # example: seq, len, cmd, pad, voltage, 3 temperatures
        FIELDS = []
        TYPE = MsgType.TELEMETRY

        def __init__(self):
            super().__init__(FakeTelemetryMsg.TYPE)

    dispatcher.register_type(MsgType.TELEMETRY, FakeTelemetryMsg)

    msg = FakeTelemetryMsg()
    msg.sender = 0x40

    dispatcher.send_message(msg)
    dispatcher.poll() # Sends the message
    dispatcher.poll() # receives, passes to battery, replies, sends reply

    reply = BT_E6000_TelemetryMsg()
    reply.sender = 0x40 | 0x80

    assert dispatcher.uart.buffer == reply.pack()

def test_msg_11_request_handler(dispatcher, battery):
    pass
def test_msg_12_request_handler(dispatcher, battery):
    pass
def test_msg_21_request_handler(dispatcher, battery):
    pass
def test_msg_30_request_handler(dispatcher, battery):
    class FakeMsg30(Msg):
        FORMAT = ''  # example: seq, len, cmd, pad, voltage, 3 temperatures
        FIELDS = []
        TYPE = MsgType.MSG_30

        def __init__(self):
            super().__init__(FakeMsg30.TYPE)

    dispatcher.register_type(MsgType.MSG_30, FakeMsg30)

    msg = FakeMsg30()
    msg.sender = 0x40

    dispatcher.send_message(msg)
    dispatcher.poll() # Sends the message
    dispatcher.poll() # receives, passes to battery, replies, sends reply

    reply = BT_E6000_Msg_30()
    reply.sender = 0x40 | 0x80

    assert dispatcher.uart.buffer == reply.pack()

def test_msg_31_request_handler(dispatcher, battery):
    class FakeMsg31(Msg):
        FORMAT = ''  # example: seq, len, cmd, pad, voltage, 3 temperatures
        FIELDS = []
        TYPE = MsgType.MSG_31

        def __init__(self):
            super().__init__(FakeMsg31.TYPE)

    dispatcher.register_type(MsgType.MSG_30, FakeMsg31)

    msg = FakeMsg31()
    msg.sender = 0x40

    dispatcher.send_message(msg)
    dispatcher.poll() # Sends the message
    dispatcher.poll() # receives, passes to battery, replies, sends reply

    reply = BT_E6000_Msg_31()
    reply.sender = 0x40 | 0x80

    assert dispatcher.uart.buffer == reply.pack()

def test_timestamp_request_handler(dispatcher, battery):
    pass