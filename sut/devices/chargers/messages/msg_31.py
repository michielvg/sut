from sut.messages.message import Msg, MsgType

class Msg_31(Msg):
    FORMAT = '10B'  # example: seq, len, cmd, pad, voltage, 3 temperatures
    FIELDS = ['b4', 'b5', 'b6', 'b7',
              'b8', 'b9', 'b10', 'b11',
              'b12', 'b13']
    TYPE = MsgType.MSG_31

    # h9F h01 hA9 h01 h01 h00 h02 h00 h1F h00 
    def __init__(self, b4 = 0x9F, b5 = 0x01, b6 = 0xA9, b7 = 0x01,
                 b8 = 0x01, b9 = 0x00, b10 = 0x00, b11 = 0x02,
                 b12 = 0x1F, b13 = 0x00):
        super().__init__(Msg_31.TYPE)

        self.sender = 0x40

        self.b4 = b4
        self.b5 = b5
        self.b6 = b6
        self.b7 = b7
        self.b8 = b8
        self.b9 = b9
        self.b10 = b10
        self.b11 = b11
        self.b12 = b12
        self.b13 = b13


