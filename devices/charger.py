
from enum import Enum

from device import Device
from message_dispatcher import MessageDispatcher


class ChargerModel(Enum):
    EC_E6000 = "EC-E6000"

class ChargerState(Enum):
    DISCONNECTED = 0
    CONNECTED = 1 # PONG received.
    MSG_30_RESP_RECEIVED = 2
    POLLING = 3

class Charger(Device):
    def __init__(self, model: ChargerModel, dispatcher: MessageDispatcher):
        self.state = ChargerState.DISCONNECTED
        super().__init__(model, dispatcher)