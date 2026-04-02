from messages.message import Msg, MsgType

class TimestampMsg(Msg):
    FORMAT = '6B' 
    FIELDS = ['year', 'month', 'day', 'hour', 'min', 'sec']
    TYPE = MsgType.TIMESTAMP

    # h19 h09 h05 h0E h07 h00
    def __init__(self, 
                 year: int = 0,
                 month: int = 0,
                 day: int = 0,
                 hour: int = 0,
                 min: int = 0,
                 sec: int = 0):
        super().__init__(TimestampMsg.TYPE)

        self.year = year & 0xFF
        self.month = month & 0xFF
        self.day = day & 0xFF
        self.hour = hour & 0xFF
        self.min = min & 0xFF
        self.sec = sec & 0xFF


