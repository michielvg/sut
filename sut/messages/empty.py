from sut.messages.message import Msg, MsgType

class EmptyMsg(Msg):
    FORMAT = '' 
    FIELDS = []
    TYPE = MsgType.EMPTY

    # 
    def __init__(self):
        super().__init__(EmptyMsg.TYPE)


