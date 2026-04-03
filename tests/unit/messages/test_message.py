import pytest
import struct

from messages.message import Msg, MsgStatus, MsgType


# ------------------------
# Test helper subclass
# ------------------------
class FakeMsg(Msg):
    FORMAT = "<B"           # one byte payload
    FIELDS = ["value"]
    TYPE = MsgType.MSG_30

    def __init__(self, value=0x12):
        super().__init__(type=self.TYPE)
        self.value = value


# ------------------------
# pack()
# ------------------------
def test_pack_creates_valid_message():
    msg = FakeMsg(value=0x42)
    msg.sender = 0x40
    msg.seq = 0x01

    data = msg.pack()

    # Starts with prefix
    assert data[0] == Msg.PREFIX_VALUE

    # Header + length
    header = data[1]
    length = data[2]

    assert header == (msg.sender | msg.seq)
    assert length == 2  # type + one byte payload

    # Type byte exists (non-empty)
    assert data[3] == MsgType.MSG_30.value

    # Payload value
    assert data[4] == 0x42

    # CRC exists (last 2 bytes)
    assert len(data) == 1 + 2 + 1 + 1 + 2  # prefix + header/len + type + payload + crc


# ------------------------
# unpack()
# ------------------------
def test_unpack_valid_message():
    msg = FakeMsg(value=0x55)
    msg.sender = 0x40
    msg.seq = 0x02

    data = msg.pack()

    unpacked, status = FakeMsg.unpack(data)

    assert status == MsgStatus.OK
    assert unpacked.value == 0x55
    assert unpacked.sender == 0x40
    assert unpacked.seq == 0x02
    assert unpacked.status == MsgStatus.OK


def test_unpack_incomplete():
    data = b"\x00\x40\x01"  # too short

    obj, status = FakeMsg.unpack(data)

    assert obj is None
    assert status == MsgStatus.INCOMPLETE


def test_unpack_prefix_error():
    msg = FakeMsg(value=0x33)
    data = bytearray(msg.pack())

    data[0] = 0xFF  # wrong prefix

    obj, status = FakeMsg.unpack(bytes(data))

    assert obj is None
    assert status == MsgStatus.PREFIX_ERROR


def test_unpack_crc_error():
    msg = FakeMsg(value=0x22)
    data = bytearray(msg.pack())

    # Corrupt CRC
    data[-1] ^= 0xFF

    obj, status = FakeMsg.unpack(bytes(data))

    assert obj is None
    assert status == MsgStatus.CRC_ERROR


# ------------------------
# reply_for_msg()
# ------------------------
def test_reply_for_msg():
    original = FakeMsg(value=0x11)
    original.sender = 0x40
    original.seq = 0x03

    reply = FakeMsg.reply_for_msg(original)

    assert reply is not None

    assert reply.type == original.type
    assert reply.seq == original.seq
    assert reply.sender == (original.sender | 0x80)


# ------------------------
# __str__()
# ------------------------
def test_str_representation():
    msg = FakeMsg(value=0xAA)
    msg.sender = 0x40
    msg.seq = 0x01

    data = msg.pack()

    s = str(msg)

    # Should be hex string
    assert all(len(byte) == 2 for byte in s.split())