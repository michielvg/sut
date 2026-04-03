# tests/test_ec_e6000_msg_31.py
import pytest
from messages.message import MsgType
from devices.chargers.ec_e6000.messages.msg_31 import EC_E6000_Msg_31

# ------------------------
# Smoke test: MSG_31 message
# ------------------------
def test_msg_31_initialization():
    msg = EC_E6000_Msg_31()
    assert msg.type == MsgType.MSG_31
    assert msg.b4 == 0x9F
    assert msg.b5 == 0x01
    assert msg.b6 == 0xA9
    assert msg.b7 == 0x01
    assert msg.b12 == 0x1F
    assert msg.b13 == 0x00

# ------------------------
# Field assignment
# ------------------------
def test_msg_31_fields_settable():
    msg = EC_E6000_Msg_31(
        b4=1, b5=2, b6=3, b7=4, b8=5, b9=6, b10=7, b11=8, b12=9, b13=10
    )
    for i, field in enumerate(EC_E6000_Msg_31.FIELDS, start=1):
        assert getattr(msg, field) == i

# ------------------------
# Pack length
# ------------------------
def test_msg_31_pack_length():
    msg = EC_E6000_Msg_31()
    packed = msg.pack()
    # Payload 10 bytes + header (seq, len, type) + 2 CRC bytes
    assert len(packed) >= 10 + 5  # rough check

# ------------------------
# Pack/unpack round-trip
# ------------------------
def test_msg_31_pack_unpack_roundtrip():
    msg = EC_E6000_Msg_31(
        b4=1, b5=2, b6=3, b7=4, b8=5, b9=6, b10=7, b11=8, b12=9, b13=10
    )
    packed = msg.pack()
    unpacked_msg, status = EC_E6000_Msg_31.unpack(packed)

    for field in EC_E6000_Msg_31.FIELDS:
        assert getattr(msg, field) == getattr(unpacked_msg, field)