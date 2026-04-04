# tests/test_bt_e6000_Msg_11.py
import pytest
from sut.messages.message import MsgType
from sut.devices.batteries.bt_e6000.messages.msg_11 import BT_E6000_Msg_11

# ------------------------
# Smoke test: Msg_11
# ------------------------
def test_Msg_11_initialization():
    msg = BT_E6000_Msg_11()
    assert msg.type == MsgType.MSG_11
    assert msg.b4 == 0x25
    assert msg.b5 == 0x47
    assert msg.b11 == 0x64

def test_Msg_11_fields_settable():
    msg = BT_E6000_Msg_11(b4=1, b5=2, b11=3)
    assert msg.b4 == 1
    assert msg.b5 == 2
    assert msg.b11 == 3

def test_Msg_11_pack_length():
    msg = BT_E6000_Msg_11()
    packed = msg.pack()
    # 17 bytes payload + header (seq, len, type) + 2 CRC bytes
    assert len(packed) >= 8 + 5  # rough check

# ------------------------
# Test Msg_11 pack/unpack round-trip
# ------------------------
def test_Msg_11_pack_unpack_roundtrip():
    msg = BT_E6000_Msg_11(b4=1, b5=2, b6=3, b7=4, b8=5)
    packed = msg.pack()
    unpacked_msg, status = BT_E6000_Msg_11.unpack(packed)

    for field in BT_E6000_Msg_11.FIELDS:
        assert getattr(msg, field) == getattr(unpacked_msg, field)