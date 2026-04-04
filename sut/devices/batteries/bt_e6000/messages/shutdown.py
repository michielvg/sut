from sut.messages.shutdown import ShutdownMsg

class BT_E6000_ShutdownMsg(ShutdownMsg):
    FORMAT = '2B'  # example: seq, len, cmd, pad, voltage, 3 temperatures
    FIELDS = ['b4', 'b5']

    # 25 FF
    def __init__(self, b4 = 0x25, b5 = 0xFF):
        super().__init__()

        self.b4 = b4
        self.b5 = b5