
import time

from messages.message import Msg, MsgType
from devices.charger import Charger, ChargerModel, ChargerState
from message_dispatcher import MessageDirection, MessageDispatcher

class EC_E6000(Charger):
    def __init__(self, dispatcher: MessageDispatcher):
        self.last_poll_time = 0
        super().__init__(ChargerModel.EC_E6000, dispatcher)
 
    def empty_response_handler(self, msg: Msg, disp: MessageDispatcher, direction: MessageDirection):
        if (self.state == ChargerState.DISCONNECTED
            and msg.sender == (0x40 | 0x80)):
            self.state = ChargerState.CONNECTED

            from .messages.msg_30 import EC_E6000_Msg_30
            self.dispatcher.send_message(EC_E6000_Msg_30())
    def msg_30_response_handler(self, msg: Msg, disp: MessageDispatcher, direction: MessageDirection):
        if (self.state == ChargerState.CONNECTED
            and msg.sender == (0x40 | 0x80)):
            self.state = ChargerState.MSG_30_RESP_RECEIVED

            from .messages.msg_31 import EC_E6000_Msg_31
            self.dispatcher.send_message(EC_E6000_Msg_31())
    def msg_31_response_handler(self, msg: Msg, disp: MessageDispatcher, direction: MessageDirection):
        if (self.state == ChargerState.MSG_30_RESP_RECEIVED
            and msg.sender == (0x40 | 0x80)):
            self.state = ChargerState.POLLING

            from .messages.telemetry import EC_E6000_TelemetryMsg
            self.dispatcher.send_message(EC_E6000_TelemetryMsg())
    def telemetry_response_handler(self, msg: Msg, disp: MessageDispatcher, direction: MessageDirection):
        # Do something with telemetry from battery.
        pass 

    def setup(self):
        self.dispatcher.subscribe(MsgType.EMPTY, self.empty_response_handler, MessageDirection.RX)
        self.dispatcher.subscribe(MsgType.MSG_30, self.msg_30_response_handler, MessageDirection.RX)
        self.dispatcher.subscribe(MsgType.MSG_31, self.msg_31_response_handler, MessageDirection.RX)
        self.dispatcher.subscribe(MsgType.TELEMETRY, self.telemetry_response_handler, MessageDirection.RX)
    
        self.register_message_types()

    def register_message_types(self):
        from .messages.msg_30 import EC_E6000_Msg_30
        from .messages.msg_31 import EC_E6000_Msg_31
        from .messages.telemetry import EC_E6000_TelemetryMsg

        self.dispatcher.register_type(MsgType.MSG_30, EC_E6000_Msg_30)
        self.dispatcher.register_type(MsgType.MSG_31, EC_E6000_Msg_31)
        self.dispatcher.register_type(MsgType.TELEMETRY, EC_E6000_TelemetryMsg)


    def poll(self) -> None:
        now = time.time()
        # Only proceed if at least 1 second has passed since last poll
        if now - self.last_poll_time < 1.0:
            return
        self.last_poll_time = now

        from .messages.telemetry import EC_E6000_TelemetryMsg
        
        # POLLING first, will be active most of the time.
        if (self.state == ChargerState.POLLING): # Send telemetry request.
            self.dispatcher.send_message(EC_E6000_TelemetryMsg())
            return
        if (self.state == ChargerState.DISCONNECTED): # Send PING/Empty Message
            msg = Msg()         # Emtpy message
            msg.sender = 0x40   # 0x40 as sender
            self.dispatcher.send_message(msg)
            return


