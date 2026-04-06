import time

from sut.logger import NDJSONLogger
from sut.message_dispatcher import MessageDirection, MessageDispatcher
from sut.messages.message import Msg
from sut.test_suites.test_suite import TestSuite
from sut.tui import TUI, Style


class BatteryTestSuite(TestSuite):

    WAIT_TIME = 1

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
        
        return self._command_sniffer_000()

    def _command_sniffer_000(self):
        self.tui.print(
            "This test will try to sniff out the device known commands, one every second."
        )
        if not self.tui.input_bool("Continue?"):
            yield from self._end()
            return

        self.logger.intent = "Command sniffing"

        next_time = time.time()
        from sut.messages.proxy import ProxyMsg

        for i in range(0x00, 0x100):
            next_time += BatteryTestSuite.WAIT_TIME
            # Wait until it's time
            while time.time() < next_time:
                yield

            msg, _ = ProxyMsg.unpack(bytes([0x00, 0x40 | (i % 4), 0x05, i, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]))

            self.dispatcher.send_message(msg)

            self.pause = True
            yield 

        yield from self._ping_000()
       
    def _ping_000(self):
        self.tui.print(
            "This test will send a ping message every second,\nincrementing the header byte by one each time."
        )
        if not self.tui.input_bool("Continue?"):
            yield from self._end()
            return

        self.logger.intent = "HEADER INC"

        next_time = time.time()

        for i in range(0x00, 0x100):
            next_time += BatteryTestSuite.WAIT_TIME
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
            yield from self._end()
            return

        self.logger.intent = "MSG_30 DIFF PLAYBACK"

        next_time = time.time()

        from sut.devices.chargers.messages.msg_30 import Msg_30
        for i in range(20):
            next_time += BatteryTestSuite.WAIT_TIME
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
            yield from self._end()
            return

        self.logger.intent = "MSG_30 polling"

        next_time = time.time()
        from sut.devices.chargers.messages.msg_30 import Msg_30
        messages = [
            Msg_30(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
            Msg_30(b6 = 0, b7 = 0, b8 = 0),
            Msg_30(b10 = 0, b11 = 0, b12 = 0, b13 = 0),
        ]

        messages.extend([Msg_30(b4=i) for i in range(0x00, 0x100)])
        messages.extend([Msg_30(b5=i) for i in range(0x00, 0x100)])
        messages.extend([Msg_30(b6=i) for i in range(0x00, 0x100)])
        messages.extend([Msg_30(b7=i) for i in range(0x00, 0x100)])
        messages.extend([Msg_30(b8=i) for i in range(0x00, 0x100)])
        messages.extend([Msg_30(b9=i) for i in range(0x00, 0x100)])
        messages.extend([Msg_30(b10=i) for i in range(0x00, 0x100)])
        messages.extend([Msg_30(b11=i) for i in range(0x00, 0x100)])
        messages.extend([Msg_30(b12=i) for i in range(0x00, 0x100)])
        messages.extend([Msg_30(b13=i) for i in range(0x00, 0x100)])
        messages.extend([Msg_30(b14=i) for i in range(0x00, 0x100)])
        messages.extend([Msg_30(b15=i) for i in range(0x00, 0x100)])
        messages.extend([Msg_30(b16=i) for i in range(0x00, 0x100)])
        messages.extend([Msg_30(b17=i) for i in range(0x00, 0x100)])
        messages.extend([Msg_30(b18=i) for i in range(0x00, 0x100)])
        messages.extend([Msg_30(b19=i) for i in range(0x00, 0x100)])

        for i, msg in enumerate(messages):
            next_time += BatteryTestSuite.WAIT_TIME
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
            yield from self._end()
            return

        self.logger.intent = "MSG_30 DIFF PLAYBACK"

        next_time = time.time()

        from sut.devices.chargers.messages.msg_31 import Msg_31
        for i in range(20):
            next_time += BatteryTestSuite.WAIT_TIME
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
            yield from self._end()
            return

        self.logger.intent = "MSG_31 polling"

        next_time = time.time()
        from sut.devices.chargers.messages.msg_31 import Msg_31
        messages = [
            Msg_31(0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
        ]

        messages.extend([Msg_31(b4=i) for i in range(0x00, 0x100)])
        messages.extend([Msg_31(b5=i) for i in range(0x00, 0x100)])
        messages.extend([Msg_31(b6=i) for i in range(0x00, 0x100)])
        messages.extend([Msg_31(b7=i) for i in range(0x00, 0x100)])
        messages.extend([Msg_31(b8=i) for i in range(0x00, 0x100)])
        messages.extend([Msg_31(b9=i) for i in range(0x00, 0x100)])
        messages.extend([Msg_31(b10=i) for i in range(0x00, 0x100)])
        messages.extend([Msg_31(b11=i) for i in range(0x00, 0x100)])
        messages.extend([Msg_31(b12=i) for i in range(0x00, 0x100)])
        messages.extend([Msg_31(b13=i) for i in range(0x00, 0x100)])

        for i, msg in enumerate(messages):
            next_time += BatteryTestSuite.WAIT_TIME
            # Wait until it's time
            while time.time() < next_time:
                yield

            msg.seq = i % 4

            self.dispatcher.send_message(msg)

            self.pause = True
            yield 

        yield from self._telemetry_000()

    def _telemetry_000(self):
        self.tui.print(
            "This test will send a telemetry message every second. 20 in total. (Playback)"
        )
        if not self.tui.input_bool("Continue?"):
            yield from self._end()
            return

        self.logger.intent = "TELEMETRY DIFF PLAYBACK"

        next_time = time.time()

        from sut.devices.chargers.messages.telemetry import TelemetryMsg
        for i in range(20):
            next_time += BatteryTestSuite.WAIT_TIME
            # Wait until it's time
            while time.time() < next_time:
                yield

            msg = TelemetryMsg()
            msg.seq = i % 4

            self.dispatcher.send_message(msg)

            self.pause = True
            yield 

        yield from self._telemetry_001()
    
    def _telemetry_001(self):
        self.tui.print(
            "This test will send a 4 * 255 of telemetry messages, one every second. Probing the battery."
        )
        if not self.tui.input_bool("Continue?"):
            yield from self._end()
            return

        self.logger.intent = "TELEMETRY polling"

        next_time = time.time()
        from sut.devices.chargers.messages.telemetry import TelemetryMsg
        messages = []

        messages.extend([TelemetryMsg(b4=i) for i in range(0x01, 0x100)])
        messages.extend([TelemetryMsg(b5=i) for i in range(0x01, 0x100)])
        messages.extend([TelemetryMsg(b6=i) for i in range(0x01, 0x100)])
        messages.extend([TelemetryMsg(b7=i) for i in range(0x01, 0x100)])

        for i, msg in enumerate(messages):
            next_time += BatteryTestSuite.WAIT_TIME
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
        