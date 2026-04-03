# tests/test_bt_e6000_msg_31.py
import pytest
from messages.message import MsgType
from devices.batteries.bt_e6000.messages.msg_31 import BT_E6000_Msg_31

# ------------------------
# Smoke test: Msg_31
# ------------------------
def test_msg_31_initialization():
    msg = BT_E6000_Msg_31()
    assert msg.type == MsgType.MSG_31
    assert msg.b4 == 0x00
    assert msg.b5 == 0x9F
    assert msg.b20 == 0x00

def test_msg_31_fields_settable():
    msg = BT_E6000_Msg_31(b4=1, b5=2, b20=3)
    assert msg.b4 == 1
    assert msg.b5 == 2
    assert msg.b20 == 3

def test_msg_31_pack_length():
    msg = BT_E6000_Msg_31()
    packed = msg.pack()
    # 17 bytes payload + header (seq, len, type) + 2 CRC bytes
    assert len(packed) >= 17 + 5  # rough check

# ------------------------
# Test Msg_31 pack/unpack round-trip
# ------------------------
def test_msg_31_pack_unpack_roundtrip():
    msg = BT_E6000_Msg_31(b4=1, b5=2, b6=3, b7=4, b8=5)
    packed = msg.pack()
    unpacked_msg, status = BT_E6000_Msg_31.unpack(packed)

    for field in BT_E6000_Msg_31.FIELDS:
        assert getattr(msg, field) == getattr(unpacked_msg, field)