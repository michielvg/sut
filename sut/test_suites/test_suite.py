from abc import ABC, abstractmethod

from sut.logger import NDJSONLogger
from sut.message_dispatcher import MessageDispatcher
from sut.tui import TUI


class TestSuite(ABC):
    def __init__(self, dispatcher: MessageDispatcher, logger: NDJSONLogger, tui: TUI):
        self.dispatcher = dispatcher
        self.logger = logger
        self.tui = tui

    @abstractmethod
    def info(self):
        """Provide information about the test suite."""
     
    @abstractmethod
    def run(self):
        """Run the test. Setup correct logging"""