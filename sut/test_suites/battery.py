import time

from sut.logger import NDJSONLogger
from sut.message_dispatcher import MessageDirection, MessageDispatcher
from sut.messages.message import Msg
from sut.test_suites.test_suite import TestSuite
from sut.tui import TUI, Style


class BatteryTestSuite(TestSuite):

    # def msg_handler(self, msg: Msg, disp: MessageDispatcher, direction: MessageDirection):
    #     pass

    def __init__(self, dispatcher: MessageDispatcher, logger: NDJSONLogger, tui: TUI):
        self.pause = False
        self.running = False
        # self.dispatcher.subscribe('*', self.msg_handler, MessageDirection.RX)
        super().__init__(dispatcher, logger, tui)
    
    def info(self):
        self.tui.print("SUT wil act as charger or drive and try to snoop out the battery's reactions.")

    def run(self):
        """Initialize the test. Setup correct logging"""
        self.tui.print("Please make sure the battery is connected before continuing.")
        if not self.tui.input_bool("Continue?"):
            return
        
        self.running = True
        
        return self._msg_30_000()
       
    def _ping_000(self):
        self.tui.print(
            "This test will send a ping message every second,\nincrementing the header byte by one each time."
        )
        if not self.tui.input_bool("Continue?"):
            return

        self.logger.intent = "HEADER INC"

        next_time = time.time()

        for i in range(0x00, 0x100):
            next_time += 1
            # Wait until it's time
            while time.time() < next_time:
                yield

            msg = Msg()
            msg.sender = 0xF0 & i
            msg.seq = 0x0F & i

            self.dispatcher.send_message(msg)

            self.pause = True
            yield 

        yield from self._msg_30_000()

    def _msg_30_000(self):
        self.tui.print(
            "This test will send a 0x30 message every second. 20 in total. (Playback)"
        )
        if not self.tui.input_bool("Continue?"):
            return

        self.logger.intent = "MSG_30 DIFF PLAYBACK"

        next_time = time.time()

        from sut.devices.chargers.messages.msg_30 import Msg_30
        for i in range(20):
            next_time += 1
            # Wait until it's time
            while time.time() < next_time:
                yield

            msg = Msg_30()
            msg.seq = i % 4

            self.dispatcher.send_message(msg)

            self.pause = True
            yield 

        yield from self._msg_30_001()

    def _msg_30_001(self):
        self.tui.print(
            "This test will send a couple of 0x30 messages, one every second. Probing the battery."
        )
        if not self.tui.input_bool("Continue?"):
            return

        self.logger.intent = "MSG_30 polling"

        next_time = time.time()
        from sut.devices.chargers.messages.msg_30 import Msg_30
        messsages = [
            Msg_30(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
            Msg_30(b4 = 0),
            Msg_30(b5 = 0),
            Msg_30(b6 = 0),
            Msg_30(b7 = 0),
            Msg_30(b8 = 0),
            Msg_30(b9 = 0),
            Msg_30(b10 = 0),
            Msg_30(b11 = 0),
            Msg_30(b12 = 0),
            Msg_30(b13 = 0),
            Msg_30(b14 = 0),
            Msg_30(b15 = 0),
            Msg_30(b16 = 0),
            Msg_30(b17 = 0),
            Msg_30(b18 = 0),
            Msg_30(b19 = 0),
            Msg_30(b6 = 0, b7 = 0, b8 = 0),
            Msg_30(b10 = 0, b11 = 0, b12 = 0, b13 = 0),
        ]
        for i, msg in enumerate(messsages):
            next_time += 1
            # Wait until it's time
            while time.time() < next_time:
                yield

            msg.seq = i % 4

            self.dispatcher.send_message(msg)

            self.pause = True
            yield 

        yield from self._msg_31_000()

    def _msg_31_000(self):
        self.tui.print(
            "This test will send a 0x30 message every second. 20 in total. (Playback)"
        )
        if not self.tui.input_bool("Continue?"):
            return

        self.logger.intent = "MSG_30 DIFF PLAYBACK"

        next_time = time.time()

        from sut.devices.chargers.messages.msg_31 import Msg_31
        for i in range(20):
            next_time += 1
            # Wait until it's time
            while time.time() < next_time:
                yield

            msg = Msg_31()
            msg.seq = i % 4

            self.dispatcher.send_message(msg)

            self.pause = True
            yield 

        yield from self._msg_31_001()
    
    def _msg_31_001(self):
        self.tui.print(
            "This test will send a couple of 0x31 messages, one every second. Probing the battery."
        )
        if not self.tui.input_bool("Continue?"):
            return

        self.logger.intent = "MSG_31 polling"

        next_time = time.time()
        from sut.devices.chargers.messages.msg_31 import Msg_31
        messsages = [
            Msg_31(0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
            Msg_31(b4 = 0),
            Msg_31(b5 = 0),
            Msg_31(b6 = 0),
            Msg_31(b7 = 0),
            Msg_31(b8 = 0),
            Msg_31(b9 = 0),
            Msg_31(b10 = 0),
            Msg_31(b11 = 0),
            Msg_31(b12 = 0),
            Msg_31(b13 = 0)
        ]
        for i, msg in enumerate(messsages):
            next_time += 1
            # Wait until it's time
            while time.time() < next_time:
                yield

            msg.seq = i % 4

            self.dispatcher.send_message(msg)

            self.pause = True
            yield 

        yield from self._end()

    def _end(self):
        yield
        self.running = False
        self.pause = False
        self.logger.flush()
        self.tui.print(
            "-- Test(s) finished.", Style.BOLD
        )
        