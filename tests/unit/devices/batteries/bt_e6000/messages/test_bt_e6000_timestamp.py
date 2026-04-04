# tests/test_bt_e6000_TimestampMsg.py
import pytest
from sut.messages.message import MsgType
from sut.devices.batteries.bt_e6000.messages.timestamp import BT_E6000_TimeStampMsg

# ------------------------
# Smoke test: ShutdownMsg
# ------------------------
def test_TimestampMsg_initialization():
    msg = BT_E6000_TimeStampMsg()
    assert msg.type == MsgType.TIMESTAMP
    assert msg.b4 == 0x25

def test_TimestampMsg_fields_settable():
    msg = BT_E6000_TimeStampMsg(b4=1)
    assert msg.b4 == 1

def test_TimestampMsg_pack_length():
    msg = BT_E6000_TimeStampMsg()
    packed = msg.pack()
    # 17 bytes payload + header (seq, len, type) + 2 CRC bytes
    assert len(packed) >= 1 + 5  # rough check

# ------------------------
# Test TimestampMsg pack/unpack round-trip
# ------------------------
def test_TimestampMsg_pack_unpack_roundtrip():
    msg = BT_E6000_TimeStampMsg(b4=1)
    packed = msg.pack()
    unpacked_msg, status = BT_E6000_TimeStampMsg.unpack(packed)

    for field in BT_E6000_TimeStampMsg.FIELDS:
        assert getattr(msg, field) == getattr(unpacked_msg, field)