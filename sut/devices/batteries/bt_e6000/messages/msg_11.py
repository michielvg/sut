from sut.messages.message import Msg, MsgType

class BT_E6000_Msg_11(Msg):
    FORMAT = '8B' 
    FIELDS = ['b4', 'b5', 'b6', 'b7',
              'b8', 'b9', 'b10', 'b11']
    TYPE = MsgType.MSG_11

    # 25 47 00 0F 03 00 00 64
    def __init__(self, 
                 b4 = 0x25, 
                 b5 = 0x47, 
                 b6 = 0x00, 
                 b7 = 0x0F,
                 b8 = 0x03, 
                 b9 = 0x00, 
                 b10 = 0x00, 
                 b11 = 0x64):
        super().__init__(BT_E6000_Msg_11.TYPE)

        self.b4 = b4
        self.b5 = b5
        self.b6 = b6
        self.b7 = b7
        self.b8 = b8
        self.b9 = b9
        self.b10 = b10
        self.b11 = b11


