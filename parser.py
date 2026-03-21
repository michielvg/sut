from enum import Enum
import time
from logger import NDJSONLogger

START_BYTE = 0x00

STATE_WAIT_START = 0
STATE_HEADER = 1
STATE_LENGTH = 2

PROGRESS = object()

class ParserMode(Enum):
    RX = "RX"
    TX = "TX"

class UARTParser:
    def __init__(self, crc_func, timeout, mode=ParserMode.RX):
        self.buffer = bytearray()
        self.state = STATE_WAIT_START
        self.msg_start_time = None
        self.crc_func = crc_func
        self.timeout = timeout
        self.mode = mode

    def feed(self, data):
        self.buffer.extend(data)
        messages = []

        # mark start time
        if self.state == STATE_WAIT_START and self.buffer and self.buffer[-1] == START_BYTE:
            self.msg_start_time = time.time()

        self._check_timeout(messages)

        while True:
            result = self._parse_one()

            if result is None:
                break
            elif result is PROGRESS:
                continue
            else:
                messages.append(result)

        return messages

    def _check_timeout(self, messages):
        if self.msg_start_time and (time.time() - self.msg_start_time > self.timeout):
            if self.buffer:
                messages.append(("INCOMPLETE", bytes(self.buffer)))
            self._reset()

    def _reset(self):
        self.buffer.clear()
        self.state = STATE_WAIT_START
        self.msg_start_time = None

    def _parse_one(self):
        if self.state == STATE_WAIT_START:
            return self._handle_wait_start()
        elif self.state == STATE_HEADER:
            return self._handle_header()
        elif self.state == STATE_LENGTH:
            return self._handle_length()
        else:
            self._reset()
            return None

    def _handle_wait_start(self):
        while self.buffer and self.buffer[0] != START_BYTE:
            self.buffer.pop(0)

        if not self.buffer:
            return None

        self.state = STATE_HEADER
        return PROGRESS

    def _handle_header(self):
        if len(self.buffer) < 2:
            return None
        self.state = STATE_LENGTH
        return PROGRESS

    def _handle_length(self):
        if len(self.buffer) < 3:
            return None

        length = self.buffer[2]

        base_len = 1 + 1 + 1 + length  # START + CMD + LEN + DATA
        total_len = base_len + (2 if self.mode == ParserMode.RX else 0)

        if len(self.buffer) < total_len:
            return None

        msg = self.buffer[:total_len]
        self.buffer = self.buffer[total_len:]

        self.state = STATE_WAIT_START
        self.msg_start_time = None

        # TX mode → compute and append CRC
        if self.mode == ParserMode.TX:
            # msg = [START][CMD][LEN][DATA...]
            crc = self.crc_func(msg[1:])
            msg = bytearray(msg)  # ensure mutable
            msg += bytes([crc & 0xFF, (crc >> 8) & 0xFF])
            return ("OK", bytes(msg))


        if self.mode == ParserMode.RX:
            # RX mode → CRC is always validated
            crc_calc = self.crc_func(msg[1:-2])
            crc_msg = msg[-2] | (msg[-1] << 8)

            if crc_calc == crc_msg:
                return ("OK", msg)
            else:
                return ("CRC_ERROR", msg, crc_calc, crc_msg)