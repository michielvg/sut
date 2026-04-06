from sut.messages.message import Msg, MsgType
from sut.messages.telemetry import TelemetryMsg

class TelemetryMsg(TelemetryMsg):
    FORMAT = '4B'  # example: seq, len, cmd, pad, voltage, 3 temperatures
    FIELDS = ['b4', 'b5', 'b6', 'b7']

    def __init__(self, b4 = 0, b5 = 0, b6 = 0, b7 = 0):
        self.sender = 0X40

        self.b4 = b4
        self.b5 = b5
        self.b6 = b6
        self.b7 = b7

        super().__init__()