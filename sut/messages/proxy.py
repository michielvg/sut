from sut.messages.message import Msg, MsgType

class ProxyMsg(Msg):
    FORMAT = '' 
    FIELDS = []
    TYPE = MsgType.PROXY

    # 
    def __init__(self, data: bytes = bytes()):
        super().__init__(ProxyMsg.TYPE)
        self.data = data


