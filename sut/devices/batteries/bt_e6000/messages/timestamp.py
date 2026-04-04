from enum import Enum

from sut.messages.message import Msg, MsgType
from sut.messages.timestamp import TimestampMsg

class BT_E6000_TelemetryState(Enum):
    UNKNOWN = 0x00
    DISCHARGING = 0x01
    CHARGING = 0X03
    

class BT_E6000_TimeStampMsg(TimestampMsg):
    FORMAT = 'B'  # example: seq, len, cmd, pad, voltage, 3 temperatures
    FIELDS = ['b4']

    def __init__(self, b4 = 0x25):
        super().__init__()

        self.b4 = b4