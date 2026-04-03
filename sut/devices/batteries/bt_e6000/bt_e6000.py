
from sut.messages import Msg, MsgType
from sut.devices import Battery, BatteryModel
from sut.message_dispatcher import MessageDispatcher, MessageDirection

# Battery doesn't need to be a state machine, it just replies to requests.
class BT_E6000(Battery):
    def __init__(self, dispatcher: MessageDispatcher):
        super().__init__(BatteryModel.BT_E6000, dispatcher)

    def empty_request_handler(self, msg: Msg, disp: MessageDispatcher, direction: MessageDirection):
        if msg is not None and msg.sender == 0x40:
            reply = msg.reply_for_msg(msg)
            if reply is not None:
                disp.send_message(reply)

    def telemetry_request_handler(self, msg: Msg, disp: MessageDispatcher, direction: MessageDirection):
        from .messages.telemetry import BT_E6000_TelemetryMsg
        if type(msg) is not BT_E6000_TelemetryMsg:
            reply = BT_E6000_TelemetryMsg.reply_for_msg(msg)
            if reply is not None:
                disp.send_message(reply)

    def msg_11_request_handler(self, msg: Msg, disp: MessageDispatcher, direction: MessageDirection):
        pass

    def msg_12_request_handler(self, msg: Msg, disp: MessageDispatcher, direction: MessageDirection):
        pass

    def msg_21_request_handler(self, msg: Msg, disp: MessageDispatcher, direction: MessageDirection):
        pass

    def msg_30_request_handler(self, msg: Msg, disp: MessageDispatcher, direction: MessageDirection):
        from .messages.msg_30 import BT_E6000_Msg_30
        if type(msg) is not BT_E6000_Msg_30:
            reply = BT_E6000_Msg_30.reply_for_msg(msg)
            disp.send_message(reply)
    
    def msg_31_request_handler(self, msg: Msg, disp: MessageDispatcher, direction: MessageDirection):
        from .messages.msg_31 import BT_E6000_Msg_31
        if type(msg) is not BT_E6000_Msg_31:
            reply = BT_E6000_Msg_31.reply_for_msg(msg)
            disp.send_message(reply)

    def timestamp_request_handler(self, msg: Msg, disp: MessageDispatcher, direction: MessageDirection):
        pass
    
    def setup(self):
        self.dispatcher.subscribe(MsgType.EMPTY, self.empty_request_handler, MessageDirection.RX)
        self.dispatcher.subscribe(MsgType.TELEMETRY, self.telemetry_request_handler, MessageDirection.RX)
        self.dispatcher.subscribe(MsgType.MSG_11, self.msg_11_request_handler, MessageDirection.RX)
        self.dispatcher.subscribe(MsgType.MSG_12, self.msg_12_request_handler, MessageDirection.RX)
        self.dispatcher.subscribe(MsgType.MSG_21, self.msg_21_request_handler, MessageDirection.RX)
        self.dispatcher.subscribe(MsgType.MSG_30, self.msg_30_request_handler, MessageDirection.RX)
        self.dispatcher.subscribe(MsgType.MSG_31, self.msg_31_request_handler, MessageDirection.RX)
        self.dispatcher.subscribe(MsgType.TIMESTAMP, self.timestamp_request_handler, MessageDirection.RX)

        self.register_message_types()

    def register_message_types(self):
        from .messages.msg_30 import BT_E6000_Msg_30
        from .messages.msg_31 import BT_E6000_Msg_31
        from .messages.telemetry import BT_E6000_TelemetryMsg
        self.dispatcher.register_type(MsgType.MSG_30, BT_E6000_Msg_30)
        self.dispatcher.register_type(MsgType.MSG_31, BT_E6000_Msg_31)
        self.dispatcher.register_type(MsgType.TELEMETRY, BT_E6000_TelemetryMsg)

