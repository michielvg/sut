from abc import ABC, abstractmethod
from enum import Enum

from sut.message_dispatcher import MessageDispatcher

class Device(ABC):
    def __init__(self, model: str, dispatcher: MessageDispatcher):
        self.model = model
        self.dispatcher = dispatcher
        self.setup()
     
    @abstractmethod
    def setup(self):
        """Initialize the device."""