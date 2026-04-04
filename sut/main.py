#!/usr/bin/env python3
"""
UART / Pipe Test Harness

- Reads messages from a serial device and/or pipe.
- Dispatches messages to handlers for printing, logging, or forwarding.
- Supports empty messages (Ping/Pong) and TX/RX correlation.
"""

import select
import sys
import time
from collections import deque
from datetime import datetime, timedelta
import traceback
import crcmod.predefined

from sut.config import Config
from sut.logger import NDJSONLogger
from sut.messages.message import Msg, MsgStatus, MsgType
from sut.message_dispatcher import MessageDirection, MessageDispatcher
from sut.messages.proxy import ProxyMsg
from sut.uart.mock_uart import MockUART
from sut.uart.pipe_uart import PipeUART
from sut.uart.pyserial_uart import PySerialUART
from sut.tui import TUI, Style

# ---------- CONFIG ----------
DEVICE = "/dev/serial0"
BAUD = 9600
PIPE = "/tmp/sut_pipe"
MSG_TIMEOUT = 0.5  # seconds for incomplete message
TX_TIMEOUT = 1     # seconds for TX/RX timeout

# ---------- CRC ----------
crc16_func = crcmod.predefined.mkCrcFun('x-25')  # matches parser
tui = TUI()

# ---------- HELPERS ----------
def make_logger(config_section: dict | bool | None) -> NDJSONLogger | None:
    """Return an NDJSONLogger based on config, prompt user if needed."""
    if config_section is False:
        return None
    if config_section is None:
        if tui.ask_bool("Enable logger", default=True):
            return NDJSONLogger()
        return None
    return NDJSONLogger(config=config_section)

# ---------- GLOBAL QUEUES ----------
tx_queue: dict[int, Msg] = {}  # map sequence → Msg for TX/RX correlation
logger = None

# ---------- MESSAGE HANDLERS ----------
def print_rx_result(msg: Msg):
    """Print RX message to console with color based on status."""
    style = Style.RESET
    message: str = ""

    if msg.status == MsgStatus.OK:
        message = f"{msg}"
    elif msg.status == MsgStatus.INCOMPLETE:
        style = Style.YELLOW
        message = f"INCOMPLETE {msg}"
    elif msg.status == MsgStatus.CRC_ERROR:
        style = Style.RED
        message = f"CRC ERROR {msg} ({msg.status_info})"
    elif msg.status == MsgStatus.NA:
        style = Style.RED
        message = f"NA {msg}"

    print(f"R: {message}", style)

def print_handler(msg: Msg, disp: MessageDispatcher, direction: MessageDirection):
    """Print all messages to stdout."""
    if direction & MessageDirection.RX:
        print_rx_result(msg)
    if direction & MessageDirection.TX:
        print(f"S: {msg}", Style.DIM)

def log_handler(msg: Msg, disp: MessageDispatcher, direction: MessageDirection):
    """Log TX/RX pairs and manage TX queue."""
    global tx_queue, logger
    if direction & MessageDirection.TX:
        if msg.seq in tx_queue:
            print(f"TX sequence collision: {msg.seq}", Style.RED)
        tx_queue[msg.seq] = msg
    if direction & MessageDirection.RX:
        tx_msg = tx_queue.pop(msg.seq, None)
        if logger:
            logger.log(tx=f"{tx_msg}", rx=f"{msg}", notes=msg.status.name if msg.status else "")

def clean_tx_queue():
    """Remove TX messages older than TX_TIMEOUT."""
    now = datetime.now()
    old_keys = [seq for seq, msg in tx_queue.items() if getattr(msg, 'sent_at', now) < now - timedelta(seconds=TX_TIMEOUT)]
    for seq in old_keys:
        tx_msg = tx_queue.pop(seq)
        if logger:
            logger.log(tx=f"{tx_msg}", rx="", notes="TIMEOUT")

def ping_handler(msg: Msg, disp: MessageDispatcher, direction: MessageDirection):
    """Reply to empty messages with a 'pong'."""
    if direction & MessageDirection.RX:
        reply = Msg.reply_for_msg(msg)
        disp.send_message(reply)

def make_pipe_forwarder(target_dispatcher: MessageDispatcher):
    """Return a handler that forwards RX messages from one dispatcher to another."""
    def handler(msg: Msg, disp: MessageDispatcher, direction: MessageDirection):
        if direction & MessageDirection.RX:
            target_dispatcher.send_message(msg)
    return handler

# --------- COMMAND HANLDER ---------
def handle_user_command(line: str, dispatcher: MessageDispatcher) -> None:
    """
    Handle a line typed by the user.
    Example: send a Ping, print status, or other commands.
    """
    line = line.strip()
    if not line:
        return
    
    # Example commands
    if line.lower() == "ping":
        print("-- User requested PING")
        ping = Msg()
        ping.sender = 0x40
        ping.seq = 0x01
        dispatcher.send_message(ping)
    elif line.lower() == "status":
        print(f"-- TX queue size:{len(tx_queue)}")
    elif line.lower().startswith("send"):
        pass
    else:
        print(f"Unknown command: {line}")

# ---------- MAIN ----------
def main():
    global logger

    # Load config and logger
    config = Config("config.json")
    logger = make_logger(config.get_section("logger"))

    # Open serial device
    try:
        serial_uart = PySerialUART.from_config(config.get_section("uart"))
        #serial_uart = MockUART()
    except Exception as e:
        print(f"Serial problem", Style.RED)
        sys.exit(1)

    dispatcher = MessageDispatcher(serial_uart)
    dispatcher.register_type(MsgType.PROXY, ProxyMsg)
    dispatcher.subscribe('*', print_handler, direction=MessageDirection.BOTH)
    dispatcher.subscribe('*', log_handler, direction=MessageDirection.BOTH)
    # dispatcher.subscribe(None, ping_handler, direction=MessageDirection.RX) # TODO: avoid infinite loop

    # Open pipe
    try:
        pipe_uart = PipeUART(PIPE)
    except Exception:
        print(f"Pipe problem", Style.RED)
        sys.exit(1)

    pipe_dispatcher = MessageDispatcher(pipe_uart)
    pipe_dispatcher.register_type(MsgType.PROXY, ProxyMsg)
    pipe_dispatcher.subscribe('*', make_pipe_forwarder(dispatcher), direction=MessageDirection.RX)

    # Main loop
    try:
        tui.print_prompt()  # print prompt again for next input
        while True:
            dispatcher.poll()
            pipe_dispatcher.poll()
            clean_tx_queue()
            
            # Check for user input
            user_line = tui.input_poll()
            if user_line is not None:
                handle_user_command(user_line, dispatcher)
                
            time.sleep(0.01)  # prevent 100% CPU spin
    except KeyboardInterrupt:
        print("\nExiting…")
    finally:
        pipe_uart.close()
        serial_uart.close()
        if logger:
            logger.flush()

if __name__ == "__main__":
    main()
