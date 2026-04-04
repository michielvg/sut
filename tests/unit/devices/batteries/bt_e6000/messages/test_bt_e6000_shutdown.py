# tests/test_bt_e6000_ShutdownMsg.py
import pytest
from sut.messages.message import MsgType
from sut.devices.batteries.bt_e6000.messages.shutdown import BT_E6000_ShutdownMsg

# ------------------------
# Smoke test: ShutdownMsg
# ------------------------
def test_ShutdownMsg_initialization():
    msg = BT_E6000_ShutdownMsg()
    assert msg.type == MsgType.SHUTDOWN
    assert msg.b4 == 0x25
    assert msg.b5 == 0xFF

def test_ShutdownMsg_fields_settable():
    msg = BT_E6000_ShutdownMsg(b4=1, b5=2)
    assert msg.b4 == 1
    assert msg.b5 == 2

def test_ShutdownMsg_pack_length():
    msg = BT_E6000_ShutdownMsg()
    packed = msg.pack()
    # 17 bytes payload + header (seq, len, type) + 2 CRC bytes
    assert len(packed) >= 2 + 5  # rough check

# ------------------------
# Test ShutdownMsg pack/unpack round-trip
# ------------------------
def test_ShutdownMsg_pack_unpack_roundtrip():
    msg = BT_E6000_ShutdownMsg(b4=1, b5=2)
    packed = msg.pack()
    unpacked_msg, status = BT_E6000_ShutdownMsg.unpack(packed)

    for field in BT_E6000_ShutdownMsg.FIELDS:
        assert getattr(msg, field) == getattr(unpacked_msg, field)