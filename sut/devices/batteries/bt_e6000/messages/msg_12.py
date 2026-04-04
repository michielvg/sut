from sut.messages.message import Msg, MsgType

class BT_E6000_Msg_12(Msg):
    FORMAT = '9B' 
    FIELDS = ['b4', 'b5', 'b6', 'b7',
              'b8', 'b9', 'b10', 'b11',
              'b12']
    TYPE = MsgType.MSG_12

    # 25 00 E1 00 00 90 10 0F 00
    def __init__(self, 
                 b4 = 0x00, 
                 b5 = 0x54, 
                 b6 = 0x33, 
                 b7 = 0x81,
                 b8 = 0x44, 
                 b9 = 0x83, 
                 b10 = 0x53, 
                 b11 = 0x92,
                 b12 = 0x0B):
        super().__init__(BT_E6000_Msg_12.TYPE)

        self.b4 = b4
        self.b5 = b5
        self.b6 = b6
        self.b7 = b7
        self.b8 = b8
        self.b9 = b9
        self.b10 = b10
        self.b11 = b11
        self.b12 = b12


