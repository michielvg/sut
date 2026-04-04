from sut.messages.message import Msg, MsgType

class ProxyMsg(Msg):
    FORMAT = '' 
    FIELDS = []
    TYPE = MsgType.PROXY

    # 
    def __init__(self):
        super().__init__(ProxyMsg.TYPE)


