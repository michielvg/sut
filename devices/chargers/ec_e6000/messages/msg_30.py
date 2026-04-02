from messages.message import Msg, MsgType

class EC_E6000_Msg_30(Msg):
    FORMAT = '16B'  # example: seq, len, cmd, pad, voltage, 3 temperatures
    FIELDS = ['b4', 'b5', 'b6', 'b7',
              'b8', 'b9', 'b10', 'b11',
              'b12', 'b13', 'b14', 'b15',
              'b16', 'b17', 'b18', 'b19']

    # h02 h01 h9E h9E h9E h9F hF6 hF6 hF6 hF6 h9F h9F h9F h9F hD0 h08
    def __init__(self, b4 = 0x02, b5 = 0x01, b6 = 0x9E, b7 = 0x9E,
                 b8 = 0x9E, b9 = 0x9F, b10 = 0xF6, b11 = 0xF6,
                 b12 = 0xF6, b13 = 0xF6, b14 = 0x9F, b15 = 0x9F,
                 b16 = 0x9F, b17 = 0x9F, b18 = 0xD0, b19 = 0x08):
        super().__init__(MsgType.MSG_30)

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
        self.b14 = b14
        self.b15 = b15
        self.b16 = b16
        self.b17 = b17
        self.b18 = b18
        self.b19 = b19


