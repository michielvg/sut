from sut.devices.battery import Battery, BatteryModel
from sut.messages.empty import EmptyMsg
from sut.messages.message import MsgType

class BT_E6000(Battery):
    def __init__(self, dispatcher):
        from .messages.telemetry import BT_E6000_TelemetryMsg
        from .messages.msg_11 import BT_E6000_Msg_11
        from .messages.msg_12 import BT_E6000_Msg_12
        from .messages.shutdown import BT_E6000_ShutdownMsg
        from .messages.msg_30 import BT_E6000_Msg_30
        from .messages.msg_31 import BT_E6000_Msg_31
        from .messages.timestamp import BT_E6000_TimeStampMsg

        self._msg_map = {
            MsgType.EMPTY: EmptyMsg,
            MsgType.TELEMETRY: BT_E6000_TelemetryMsg,
            MsgType.MSG_11: BT_E6000_Msg_11,
            MsgType.MSG_12: BT_E6000_Msg_12,
            MsgType.SHUTDOWN: BT_E6000_ShutdownMsg,
            MsgType.MSG_30: BT_E6000_Msg_30,
            MsgType.MSG_31: BT_E6000_Msg_31,
            MsgType.TIMESTAMP: BT_E6000_TimeStampMsg,
        }

        super().__init__(BatteryModel.BT_E6000, dispatcher)