from sut.messages.message import Msg, MsgType 

class ShutdownMsg(Msg):
    FORMAT = ''  # example: seq, len, cmd, pad, voltage, 3 temperatures
    FIELDS = []
    TYPE = MsgType.SHUTDOWN

    def __init__(self):
        super().__init__(ShutdownMsg.TYPE)