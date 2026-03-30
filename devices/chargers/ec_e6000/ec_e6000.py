
import time

from devices.charger import Charger, ChargerModel, ChargerState
from devices.chargers.ec_e6000.messages.msg_30 import EC_E6000_Msg_30
from devices.chargers.ec_e6000.messages.msg_31 import EC_E6000_Msg_31
from devices.chargers.ec_e6000.messages.telemetry import EC_E6000_TelemetryMsg
from message import Msg, MsgType
from message_dispatcher import MessageDirection, MessageDispatcher

class EC_E6000(Charger):
    def __init__(self, dispatcher: MessageDispatcher):
        self.last_poll_time = 0
        super().__init__(ChargerModel.EC_E6000, dispatcher)
 
    def empty_response_handler(self, msg: Msg, disp: MessageDispatcher, direction: MessageDirection):
        if (self.state == ChargerState.DISCONNECTED):
            self.state = ChargerState.CONNECTED
    def msg_30_response_handler(self, msg: Msg, disp: MessageDispatcher, direction: MessageDirection):
        if (self.state == ChargerState.CONNECTED):
            self.state = ChargerState.MSG_30_RESP_RECEIVED
    def msg_31_response_handler(self, msg: Msg, disp: MessageDispatcher, direction: MessageDirection):
        if (self.state == ChargerState.MSG_30_RESP_RECEIVED):
            self.state = ChargerState.POLLING
    def telemetry_response_handler(self, msg: Msg, disp: MessageDispatcher, direction: MessageDirection):
        # Do something with telemetry from battery.
        pass 

    def setup(self):
        self.dispatcher.subscribe(MsgType.EMPTY, self.empty_response_handler, MessageDirection.RX)
        self.dispatcher.subscribe(MsgType.MSG_30, self.msg_30_response_handler, MessageDirection.RX)
        self.dispatcher.subscribe(MsgType.MSG_31, self.msg_31_response_handler, MessageDirection.RX)
        self.dispatcher.subscribe(MsgType.TELEMETRY, self.telemetry_response_handler, MessageDirection.RX)

    def poll(self) -> None:
        now = time.time()
        # Only proceed if at least 1 second has passed since last poll
        if now - self.last_poll_time < 1.0:
            return
        self.last_poll_time = now
        
        # POLLING first, will be active most of the time.
        if (self.state == ChargerState.POLLING): # Send telemetry request.
            self.dispatcher.send_message(EC_E6000_TelemetryMsg())
            return
        if (self.state == ChargerState.DISCONNECTED): # Send PING/Empty Message
            self.dispatcher.send_message(Msg())
            return
        if (self.state == ChargerState.CONNECTED):    # Send 0X30
            self.dispatcher.send_message(EC_E6000_Msg_30())
            return
        if (self.state == ChargerState.MSG_30_RESP_RECEIVED): # Send 0X31
            self.dispatcher.send_message(EC_E6000_Msg_31())
            return

