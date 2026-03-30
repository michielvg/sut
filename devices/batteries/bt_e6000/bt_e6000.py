
from devices.battery import Battery, BatteryModel
from message import Msg, MsgType
from message_dispatcher import MessageDirection, MessageDispatcher


class BT_E6000(Battery):
    def __init__(self, dispatcher: MessageDispatcher):
        super().__init__(BatteryModel.BT_E6000, dispatcher)

    def empty_request_handler(self, msg: Msg, disp: MessageDispatcher, direction: MessageDirection):
        pass 

    def telemetry_request_handler(self, msg: Msg, disp: MessageDispatcher, direction: MessageDirection):
        pass

    def msg_11_request_handler(self, msg: Msg, disp: MessageDispatcher, direction: MessageDirection):
        pass

    def msg_12_request_handler(self, msg: Msg, disp: MessageDispatcher, direction: MessageDirection):
        pass

    def msg_21_request_handler(self, msg: Msg, disp: MessageDispatcher, direction: MessageDirection):
        pass

    def msg_30_request_handler(self, msg: Msg, disp: MessageDispatcher, direction: MessageDirection):
        pass

    def timestamp_request_handler(self, msg: Msg, disp: MessageDispatcher, direction: MessageDirection):
        pass
    
    def setup(self):
        self.dispatcher.subscribe(MsgType.EMPTY, self.empty_request_handler, MessageDirection.RX, self)
        self.dispatcher.subscribe(MsgType.TELEMETRY, self.telemetry_request_handler, MessageDirection.RX, self)
        self.dispatcher.subscribe(MsgType.MSG_11, self.msg_11_request_handler, MessageDirection.RX, self)
        self.dispatcher.subscribe(MsgType.MSG_12, self.msg_12_request_handler, MessageDirection.RX, self)
        self.dispatcher.subscribe(MsgType.MSG_21, self.msg_21_request_handler, MessageDirection.RX, self)
        self.dispatcher.subscribe(MsgType.MSG_30, self.msg_30_request_handler, MessageDirection.RX, self)
        self.dispatcher.subscribe(MsgType.TIMESTAMP, self.timestamp_request_handler, MessageDirection.RX, self)


