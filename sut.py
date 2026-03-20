#!/usr/bin/env python3
import serial
import crcmod.predefined
import os
import select
import time
from parser import UARTParser
import traceback

# ---------- CONFIG ----------
DEVICE = "/dev/serial0"
BAUD = 9600
PIPE = "/tmp/sut_pipe"
MSG_TIMEOUT = 0.5  # seconds for incomplete message

# Colors
RED = "\033[91m"    # CRC error
YELLOW = "\033[93m" # incomplete / timeout
RESET = "\033[0m"

# ---------- STATIC VARS ----------
START_BYTE = 0x00

# ---------- OPEN UART ----------
ser = serial.Serial(DEVICE, BAUD, bytesize=8, parity='N', stopbits=1, timeout=0.1)

# ---------- OPEN FIFO ----------
if not os.path.exists(PIPE):
    os.mkfifo(PIPE)
pipe_fd = os.open(PIPE, os.O_RDONLY | os.O_NONBLOCK)

# ---------- CRC ----------
crc16_func = crcmod.predefined.mkCrcFun('x-25')  # matches your working parser
#crc16_func = crcmod.mkCrcFun(0x11021, rev=True, initCrc=0xFFFF, xorOut=0x0000)

def handle_result(result):
    kind = result[0]

    if kind == "OK":
        _, msg = result
        msg_hex = " ".join(f"{b:02X}" for b in msg)
        print(f"{RESET}R: {msg_hex}{RESET}")

    elif kind == "CRC_ERROR":
        _, msg, calc, recv = result
        msg_hex = " ".join(f"{b:02X}" for b in msg)
        print(f"{RED}R: CRC ERROR {msg_hex} (calc={calc:04X} recv={recv:04X}){RESET}")

    elif kind == "INCOMPLETE":
        _, msg = result
        msg_hex = " ".join(f"{b:02X}" for b in msg)
        print(f"{YELLOW}R: INCOMPLETE {msg_hex}{RESET}")

def handle_pipe_input(pipe_fd, ser):
    try:
        msg_str = os.read(pipe_fd, 1024)
        if not msg_str:
            return

        payload = (
            msg_str
            .decode('unicode_escape')
            .encode('latin1')
        )

        msg = bytearray([START_BYTE]) + payload
        crc = crc16_func(msg[1:])
        msg += bytes([crc & 0xFF, (crc >> 8) & 0xFF])

        ser.write(msg)

        print("S:", " ".join(f"{b:02X}" for b in msg))

    except BlockingIOError:
        # This is normal for non-blocking reads; just ignore
        pass
    except Exception as e:
        print("PIPE ERROR:", repr(e))

        # show raw input if available
        try:
            print("RAW:", msg_str)
        except UnboundLocalError:
            print("RAW: <not read>")

        # optional: decoded attempt
        try:
            print("AS TEXT:", msg_str.decode(errors="replace"))
        except Exception:
            pass

        # full traceback (very useful while debugging)
        traceback.print_exc()

parser = UARTParser(crc16_func, MSG_TIMEOUT)

try:
    while True:
        rlist, _, _ = select.select([ser, pipe_fd], [], [], 0.1)

        for fd in rlist:
            if fd == ser:
                data = ser.read(ser.in_waiting or 1)
                if not data:
                    continue

                for result in parser.feed(data):
                    handle_result(result)

            elif fd == pipe_fd:
                handle_pipe_input(pipe_fd, ser)
except KeyboardInterrupt:
    print("\nExiting…")
finally:
    ser.close()
    os.close(pipe_fd)