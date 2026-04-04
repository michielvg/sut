# tests/test_bt_e6000_Msg_12.py
import pytest
from sut.messages.message import MsgType
from sut.devices.batteries.bt_e6000.messages.msg_12 import BT_E6000_Msg_12

# ------------------------
# Smoke test: Msg_11
# ------------------------
def test_Msg_11_initialization():
    msg = BT_E6000_Msg_12()
    assert msg.type == MsgType.MSG_12
    assert msg.b4 == 0x00
    assert msg.b5 == 0x54
    assert msg.b12 == 0x0B

def test_Msg_12_fields_settable():
    msg = BT_E6000_Msg_12(b4=1, b5=2, b12=3)
    assert msg.b4 == 1
    assert msg.b5 == 2
    assert msg.b12 == 3

def test_Msg_12_pack_length():
    msg = BT_E6000_Msg_12()
    packed = msg.pack()
    # 17 bytes payload + header (seq, len, type) + 2 CRC bytes
    assert len(packed) >= 9 + 5  # rough check

# ------------------------
# Test Msg_12 pack/unpack round-trip
# ------------------------
def test_Msg_12_pack_unpack_roundtrip():
    msg = BT_E6000_Msg_12(b4=1, b5=2, b6=3, b7=4, b8=5)
    packed = msg.pack()
    unpacked_msg, status = BT_E6000_Msg_12.unpack(packed)

    for field in BT_E6000_Msg_12.FIELDS:
        assert getattr(msg, field) == getattr(unpacked_msg, field)