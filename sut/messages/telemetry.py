from enum import Enum

from sut.messages.message import Msg, MsgType 

class TelemetryMsg(Msg):
    FORMAT = ''  # example: seq, len, cmd, pad, voltage, 3 temperatures
    FIELDS = []
    TYPE = MsgType.TELEMETRY

    def __init__(self):
        super().__init__(TelemetryMsg.TYPE)