from collections import defaultdict, deque
from itertools import chain
from typing import Callable, Deque, Dict, List
from messages.empty import EmptyMsg
from messages.message import Msg, MsgStatus, MsgType
from uart.uart_interface import UARTInterface
from enum import Flag, auto
from datetime import datetime

class MessageDirection(Flag):
    RX = auto()    # subscriber wants incoming messages
    TX = auto()    # subscriber wants outgoing messages
    BOTH = RX | TX # convenience flag
    

# --- Event-driven Dispatcher ---
class MessageDispatcher:

    # ----------------------------
    def _leaf_subclasses(cls):
        leaves = set()

        def walk(c):
            subs = c.__subclasses__()
            if not subs:
                leaves.add(c)
            else:
                for s in subs:
                    walk(s)

        walk(cls)
        return leaves
    
    # ----------------------------
    def _register_message_types(self) -> None:
        """Associate a type byte with a Msg subclass."""
        # message_types = MessageDispatcher._leaf_subclasses(Msg)
        # for message_type in message_types:
        #     self.message_map[message_type].append(message_type)
        
        self.message_map[MsgType.EMPTY].append(EmptyMsg)

    # ----------------------------
    def __init__(self, uart: UARTInterface) -> None:
        """
        uart: any object implementing UARTInterface (e.g., pyserial.Serial or a mock)
        """
        self.uart: UARTInterface = uart
        # Maps command byte or '*' → list of callbacks
        self.subscribers: Dict[MsgType | str, List[tuple[Callable[[Msg, "MessageDispatcher", MessageDirection], None], MessageDirection]]] = defaultdict(list)
        # Maps command byte → Msg subclass
        self.message_map: Dict[MsgType, List[type[Msg]]] = defaultdict(list)
        # Receive buffer for partial messages
        self.rx_buffer: bytearray = bytearray()
        # FIFO send queue
        self.tx_queue: Deque[Msg] = deque()

        self._register_message_types()

    # ----------------------------
    def subscribe(
        self,
        type: MsgType | str,
        callback: Callable[[Msg, "MessageDispatcher", MessageDirection], None],
        direction: MessageDirection = MessageDirection.RX
    ) -> None:
        """
        Subscribe a callback to a specific command.

        Parameters:
        - type: int type or '*' for wildcard subscription
        - callback: function taking three arguments:
            1. Msg object
            2. Dispatcher instance
            3. MessageDirection (RX or TX)
        - direction: MessageDirection flag indicating when to call the subscriber
                    (RX, TX, or BOTH)
        """
        self.subscribers[type].append((callback, direction))
    
    # ----------------------------
    def register_type(self, msg_type: MsgType, msg_cls: type):
        # Ensure the key exists first
        self.message_map.setdefault(msg_type, [])
    
        if msg_cls not in self.message_map[msg_type]:
            self.message_map[msg_type].append(msg_cls)

    # ----------------------------
    def send_message(self, msg_obj: Msg) -> None:
        """
        Append a message object to the TX queue. The dispatcher will call
        pack() when sending and broadcast TX events after writing.
        """
        if msg_obj is not None:
            self.tx_queue.append(msg_obj)
    
    # ----------------------------
    def poll(self) -> None:
        """
        Process one iteration of the dispatcher.

        This is the method the application should call repeatedly
        in its main loop. It performs two main tasks:

        1. Reads incoming bytes from UART and dispatches any complete messages
        to subscribers. Partial messages are buffered internally.
        2. Flushes any outgoing messages in the TX queue to the UART, ensuring
        that messages queued by subscribers are sent sequentially.

        Usage:
            while True:
                dispatcher.poll()
                # other application logic
        """
        # Handle incoming messages
        self._read_and_dispatch()

        # Handle outgoing messages
        self._flush_send_queue()

    # ----------------------------
    def _broadcast(
        self, 
        msg_obj: Msg, 
        direction: MessageDirection
    ) -> None:
        """
        Broadcast a message to all subscribers based on its command and the given direction.

        Subscribers registered for a specific command are called if the message has a 'type' attribute.
        Wildcard subscribers ('*') are always called. Each subscriber is only called if
        its MessageDirection flag matches the provided direction.

        Parameters:
        - msg_obj: The message object being broadcast
        - direction: MessageDirection.RX or MessageDirection.TX
        """
        # Determine command if available
        type: MsgType | None = getattr(msg_obj, 'type', None)

        # Broadcast to specific command subscribers
        if type in self.subscribers:
            for cb, dir_flag in self.subscribers[type]:
                if direction in dir_flag:
                    cb(msg_obj, self, direction)

        # Broadcast to wildcard subscribers
        for cb, dir_flag in self.subscribers.get('*', []):
            if direction in dir_flag:
                cb(msg_obj, self, direction)

    # ----------------------------
    def _flush_send_queue(self) -> None:
        """
        Send queued messages to UART.
        Catch exceptions so one bad message doesn't stop the queue.
        Distinguish between pack errors and UART write errors.
        """
        while self.tx_queue:
            msg_obj = self.tx_queue.popleft()

            # Step 1: pack the message
            try:
                msg_bytes = msg_obj.pack()
            except Exception as e:
                print(f"Error packing message {msg_obj}: {e}")
                continue  # skip to next message

            # Step 2: write to UART
            try:
                self.uart.write(msg_bytes)
                msg_obj.sent_at = datetime.now()
            except Exception as e:
                print(f"Error writing message {msg_obj} to UART: {e}")
                continue  # skip to next message

            # Step 3: broadcast TX
            try:
                self._broadcast(msg_obj, MessageDirection.TX)
            except Exception as e:
                print(f"Error broadcasting message {msg_obj}: {e}")
                # continue, broadcasting should not stop other messages

    # ----------------------------
    def _read_and_dispatch(self) -> None:
        """
        Read bytes from UART, parse complete messages, and broadcast to subscribers.
        Partial messages are buffered until complete.
        """
        # Check how many bytes are available
        available_bytes = self.uart.in_waiting
        if available_bytes > 0:
            data = self.uart.read(available_bytes)
            self.rx_buffer.extend(data)

        while True:
            # Minimum message size = 5 bytes (prefix + header + length + CRC)
            if len(self.rx_buffer) < 5:
                break
            # Check prefix
            if self.rx_buffer[0] != 0x00:
                # discard until next possible prefix
                self.rx_buffer.pop(0)
                continue

            handled: bool = False
            error: bool = False
            # Try all registered Msg classes to unpack
            for msg_cls in chain.from_iterable(self.message_map.values()):
                try:
                    msg_obj, status = msg_cls.unpack(self.rx_buffer)
                except Exception as e:
                    # Log the error, skip this message class
                    print(f"[WARN] Failed to unpack {msg_cls.__name__}: {e}")
                    continue

                if status == MsgStatus.OK:
                    msg_obj.received_at = datetime.now()
                    # Remove processed bytes from buffer
                    total_len: int = len(msg_obj.data)
                    self.rx_buffer = self.rx_buffer[total_len:]

                    self._broadcast(msg_obj, MessageDirection.RX)

                    handled = True
                    break  # message processed
                elif status in [ MsgStatus.CRC_ERROR, MsgStatus.PREFIX_ERROR ]:
                    error = True
            
            # TODO: clean this up, this will be slow and skips unknown types
            if not handled:
                # TODO: this makes receiving a rolling window, but CRC error would take a couple of polls to filter through
                # Not enough bytes yet or CRC error
                # Cleanup: prevent runaway buffer, only discard if too long or error
                if not handled and (len(self.rx_buffer) > 1024 or error):
                    self.rx_buffer.pop(0)
                break