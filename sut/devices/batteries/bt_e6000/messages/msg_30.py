from sut.messages.message import Msg, MsgType

class BT_E6000_Msg_30(Msg):
    FORMAT = '17B' 
    FIELDS = ['b4', 'b5', 'b6', 'b7',
              'b8', 'b9', 'b10', 'b11',
              'b12', 'b13', 'b14', 'b15',
              'b16', 'b17', 'b18', 'b19',
              'b20']
    TYPE = MsgType.MSG_30

    # h00 h54 h33 h81 h44 h83 h53 h92 h0B h47 hC2 hEF h13 hF5 h3B hC7 hC5 
    def __init__(self, 
                 b4 = 0x00, 
                 b5 = 0x54, 
                 b6 = 0x33, 
                 b7 = 0x81,
                 b8 = 0x44, 
                 b9 = 0x83, 
                 b10 = 0x53, 
                 b11 = 0x92,
                 b12 = 0x0B, 
                 b13 = 0x47, 
                 b14 = 0xC2, 
                 b15 = 0xEF,
                 b16 = 0x13, 
                 b17 = 0xF5, 
                 b18 = 0x3B, 
                 b19 = 0xC7,
                 b20 = 0xC5):
        super().__init__(BT_E6000_Msg_30.TYPE)

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
        self.b20 = b20


