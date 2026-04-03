# tests/test_ec_e6000_messages.py
import pytest
from sut.messages.message import MsgType
from sut.devices.chargers.ec_e6000.messages.telemetry import EC_E6000_TelemetryMsg

# ------------------------
# Smoke test: telemetry message
# ------------------------
def test_telemetry_msg_initialization():
    msg = EC_E6000_TelemetryMsg()
    assert msg.type == MsgType.TELEMETRY
    assert msg.b4 == 0
    assert msg.b5 == 0
    assert msg.b6 == 0
    assert msg.b7 == 0

def test_telemetry_msg_fields_settable():
    msg = EC_E6000_TelemetryMsg(b4=1, b5=2, b6=3, b7=4)
    assert msg.b4 == 1
    assert msg.b5 == 2
    assert msg.b6 == 3
    assert msg.b7 == 4

def test_telemetry_msg_pack_length():
    msg = EC_E6000_TelemetryMsg()
    packed = msg.pack()
    # 4 bytes payload + header (seq, len, type) + 2 CRC bytes
    assert len(packed) >= 4 + 5  # rough sanity check

# ------------------------
# Pack/unpack round-trip
# ------------------------
def test_telemetry_msg_pack_unpack_roundtrip():
    msg = EC_E6000_TelemetryMsg(b4=10, b5=20, b6=30, b7=40)
    packed = msg.pack()
    unpacked_msg, status = EC_E6000_TelemetryMsg.unpack(packed)

    # Check that unpacked fields match the original
    for field in EC_E6000_TelemetryMsg.FIELDS:
        assert getattr(msg, field) == getattr(unpacked_msg, field)