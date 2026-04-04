from datetime import datetime
from enum import Enum
import struct

import crcmod.predefined

class MsgStatus(Enum):
    NA = -1
    OK = 0
    PREFIX_ERROR = 1
    CRC_ERROR = 2
    INCOMPLETE = 3
    WRONG_TYPE = 4

class MsgType(Enum):
    PROXY = -2
    EMPTY = -1
    MSG_10 = 0x10
    TELEMETRY = MSG_10
    MSG_11 = 0x11 # From DU -> START
    MSG_12 = 0x12 # From DU -> START
    MSG_21 = 0x21 # From DU -> END/TIMEOUT
    SHUTDOWN = MSG_21
    MSG_30 = 0X30
    MSG_31 = 0X31
    MSG_32 = 0X32
    TIMESTAMP = MSG_32

    
class Msg:
    PREFIX_VALUE = 0x00   # example prefix byte
    
    FORMAT = ''           # subclasses override
    FIELDS = []           # attribute names in order
    TYPE = MsgType.EMPTY

    crc_func = crcmod.predefined.mkCrcFun('x-25')

    def __init__(self, type:MsgType = MsgType.EMPTY):
        self.status: MsgStatus = MsgStatus.NA
        self.status_info: str = '' # calc={calc:04X} recv={msg.crc:04X}
        self.sent_at: datetime | None = None
        self.received_at: datetime | None = None

        self.data: bytes =  bytes()
        
        self.sender: int = 0x00
        self.seq: int = 0x00
        self.type: MsgType = type
        self.crc: int | None = None

    def __str__(self):
        return " ".join(f"{b:02X}" for b in self.data)

    @classmethod
    def reply_for_msg(cls, msg:"Msg"):
        result = cls()
        result.type = msg.type
        result.seq = msg.seq 
        result.sender = msg.sender | 0x80

        return result

    def pack(self):
        if self.type != MsgType.PROXY:
            # 1. Collect payload values
            values = [getattr(self, f) for f in self.FIELDS]
            values = [v.value if isinstance(v, Enum) else v for v in values]
            
            # 2. Pack payload
            values_bytes = struct.pack(self.FORMAT, *values)
            length = len(values_bytes)
            if (self.type != MsgType.EMPTY):
                length += 1
            prefix_bytes = struct.pack("BB", (self.sender | self.seq) & 0xFF, length)
            if (self.type != MsgType.EMPTY):
                prefix_bytes += bytes([self.type.value])
            payload_bytes = prefix_bytes + values_bytes

            # 3. Calculate CRC over payload (or include prefix if your protocol does)
            crc_value = Msg.crc_func(payload_bytes)
            crc_bytes = struct.pack('<H', crc_value)  # little-endian CRC

            # 4. Prepend prefix and append CRC
            self.data = bytes([self.PREFIX_VALUE]) + payload_bytes + crc_bytes

        return self.data

    @classmethod
    def unpack(cls, data: bytes):
        if len(data) < 5:  # minimal message size
            return None, MsgStatus.INCOMPLETE

        prefix = data[0]
        header = data[1]
        length = data[2]

        total_size = 1 + 2 + length + 2  # prefix + header+length + payload + CRC
        if len(data) < total_size:
            return None, MsgStatus.INCOMPLETE
        
        payload_bytes = data[1:3 + length]  # header + payload
        
        # Skip msg types that do not fit
        # TODO: simplify this logic
        if  cls.TYPE != MsgType.PROXY and (
            (length == 0 and cls.TYPE != MsgType.EMPTY) or \
            (length > 0 and cls.TYPE.value != payload_bytes[2])):
            return None, MsgStatus.WRONG_TYPE
        
        # TODO: Skip message types by payload length.

        crc_bytes = data[3 + length:3 + length + 2]

        if prefix != cls.PREFIX_VALUE:
            return None, MsgStatus.PREFIX_ERROR

        received_crc = struct.unpack('<H', crc_bytes)[0]
        calculated_crc = Msg.crc_func(payload_bytes)
        if received_crc == 0:
            received_crc = calculated_crc
        if received_crc != calculated_crc:
            return None, MsgStatus.CRC_ERROR

        obj = cls()

        if length > 0 and cls.TYPE != MsgType.PROXY:
            obj.type = MsgType(payload_bytes[2])

            values_bytes = payload_bytes[3:]  # skip header
            values = struct.unpack(cls.FORMAT, values_bytes)

            for field, value in zip(cls.FIELDS, values):
                # Use current attribute to detect enum type
                current_attr = getattr(obj, field)
                if isinstance(current_attr, Enum):
                    enum_type = type(current_attr)
                    setattr(obj, field, enum_type(value))
                else:
                    setattr(obj, field, value)

        obj.seq = header & 0x0F
        obj.sender = header & 0xF0

        obj.data = bytes([obj.PREFIX_VALUE]) + payload_bytes + struct.pack('<H', received_crc) # TODO: This was quickly done to make the PROXY type work. Clean this up.
        obj.crc = received_crc
        obj.status = MsgStatus.OK

        return obj, MsgStatus.OK