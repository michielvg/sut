from messages.message import Msg, MsgType

class BT_E6000_Msg_31(Msg):
    FORMAT = '17B' 
    FIELDS = ['b4', 'b5', 'b6', 'b7',
              'b8', 'b9', 'b10', 'b11',
              'b12', 'b13', 'b14', 'b15',
              'b16', 'b17', 'b18', 'b19',
              'b20']
    TYPE = MsgType.MSG_31
    
    #  h00 h9F h01 hA9 h01 h01 h00 h05 h00 h28 h00 h88 h00 h43 h01 h78 h00 
    def __init__(self, 
                 b4 = 0x00, 
                 b5 = 0x9F, 
                 b6 = 0x01, 
                 b7 = 0xA9,
                 b8 = 0x01, 
                 b9 = 0x01, 
                 b10 = 0x00, 
                 b11 = 0x05,
                 b12 = 0x00, 
                 b13 = 0x28, 
                 b14 = 0x00, 
                 b15 = 0x88,
                 b16 = 0x00, 
                 b17 = 0x43, 
                 b18 = 0x01, 
                 b19 = 0x78,
                 b20 = 0x00):
        super().__init__(BT_E6000_Msg_31.TYPE)

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


