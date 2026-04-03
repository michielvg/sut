# tests/test_ec_e6000_msg_30.py
import pytest
from messages.message import MsgType
from devices.chargers.ec_e6000.messages.msg_30 import EC_E6000_Msg_30

# ------------------------
# Smoke test: MSG_30 message
# ------------------------
def test_msg_30_initialization():
    msg = EC_E6000_Msg_30()
    assert msg.type == MsgType.MSG_30
    assert msg.b4 == 0x02
    assert msg.b5 == 0x01
    assert msg.b6 == 0x9E
    assert msg.b7 == 0x9E
    assert msg.b18 == 0xD0
    assert msg.b19 == 0x08

# ------------------------
# Field assignment
# ------------------------
def test_msg_30_fields_settable():
    msg = EC_E6000_Msg_30(
        b4=1, b5=2, b6=3, b7=4, b8=5, b9=6, b10=7, b11=8,
        b12=9, b13=10, b14=11, b15=12, b16=13, b17=14, b18=15, b19=16
    )
    for i, field in enumerate(EC_E6000_Msg_30.FIELDS, start=1):
        assert getattr(msg, field) == i

# ------------------------
# Pack length
# ------------------------
def test_msg_30_pack_length():
    msg = EC_E6000_Msg_30()
    packed = msg.pack()
    # Payload 16 bytes + header (seq, len, type) + 2 CRC bytes
    assert len(packed) >= 16 + 5  # rough check

# ------------------------
# Pack/unpack round-trip
# ------------------------
def test_msg_30_pack_unpack_roundtrip():
    msg = EC_E6000_Msg_30(
        b4=1, b5=2, b6=3, b7=4, b8=5, b9=6, b10=7, b11=8,
        b12=9, b13=10, b14=11, b15=12, b16=13, b17=14, b18=15, b19=16
    )
    packed = msg.pack()
    unpacked_msg, status = EC_E6000_Msg_30.unpack(packed)

    for field in EC_E6000_Msg_30.FIELDS:
        assert getattr(msg, field) == getattr(unpacked_msg, field)