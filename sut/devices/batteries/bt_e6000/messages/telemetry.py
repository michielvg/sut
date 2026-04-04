from enum import Enum

from sut.messages.message import Msg, MsgType
from sut.messages.telemetry import TelemetryMsg

class BT_E6000_TelemetryState(Enum):
    UNKNOWN = 0x00
    DISCHARGING = 0x01
    CHARGING = 0X03
    

class BT_E6000_TelemetryMsg(TelemetryMsg):
    FORMAT = '<5B3H10B'  # example: seq, len, cmd, pad, voltage, 3 temperatures
    FIELDS = ['b4', 'state', 'b6', 'b7', 'b8', 
              'voltage_mv', 'max_cell_voltage_mv', 'min_cell_volgate_mv',
              'max_temp_c', 'avg_temp_c', 'th002_temp_c', 'state_of_charge_pct',
              'charge_counter', 'b20', 'b21', 'b22', 'b23', 'b24']

    def __init__(self, b4 = 0, state=BT_E6000_TelemetryState.UNKNOWN,
                 b6 = 0, b7 = 0, b8 = 0, voltage_mv = 0, max_cell_voltage_mv = 0,
                 min_cell_volgate_mv = 0, max_temp_c=0, avg_temp_c=0, th002_temp_c=0,
                 state_of_charge_pct = 0, charge_counter = 0, b20 = 0, b21=0, 
                 b22 = 0, b23 = 0, b24=0):
        super().__init__()

        self.b4 = b4
        self.state = state
        self.b6 = b6
        self.b7 = b7
        self.b8 = b8
        self.voltage_mv = voltage_mv
        self.max_cell_voltage_mv = max_cell_voltage_mv
        self.min_cell_volgate_mv = min_cell_volgate_mv
        self.max_temp_c = max_temp_c
        self.avg_temp_c = avg_temp_c
        self.th002_temp_c = th002_temp_c
        self.state_of_charge_pct = state_of_charge_pct
        self.charge_counter = charge_counter
        self.b20 = b20
        self.b21 = b21
        self.b22 = b22
        self.b23 = b23
        self.b24 = b24