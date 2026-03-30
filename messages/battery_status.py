from msg import Msg

class BatteryStatusMsg(Msg):
    PREFIX_VALUE = 0x00
    FORMAT = 'BBBxH3B'  # example: seq, len, cmd, pad, voltage, 3 temperatures
    FIELDS = ['seq', 'length', 'cmd', 'voltage', 'temp1', 'temp2', 'temp3']

    def __init__(self, seq=0, length=0, cmd=0x10, voltage=0, temp1=0, temp2=0, temp3=0):
        self.seq = seq
        self.length = length
        self.cmd = cmd
        self.voltage = voltage
        self.temp1 = temp1
        self.temp2 = temp2
        self.temp3 = temp3