# tests/test_bt_e6000_messages.py
import pytest
from messages.message import MsgType
from devices.batteries.bt_e6000.messages.telemetry import BT_E6000_TelemetryMsg, BT_E6000_TelemetryState

# ------------------------
# Smoke test: telemetry message
# ------------------------
def test_telemetry_msg_initialization():
    msg = BT_E6000_TelemetryMsg()
    assert msg.type == MsgType.TELEMETRY
    assert msg.state == BT_E6000_TelemetryState.UNKNOWN

def test_telemetry_msg_pack_length():
    msg = BT_E6000_TelemetryMsg()
    packed = msg.pack()
    # Format: 5B3H10B → payload 18 bytes + header bytes
    # Assume: 0x00 prefix + seq + len + type + CRC 2 bytes
    assert len(packed) >= 18 + 5  # rough check

def test_telemetry_msg_fields_settable():
    msg = BT_E6000_TelemetryMsg(
        b4=1, state=BT_E6000_TelemetryState.CHARGING,
        voltage_mv=12000, max_cell_voltage_mv=4100
    )
    assert msg.b4 == 1
    assert msg.state == BT_E6000_TelemetryState.CHARGING
    assert msg.voltage_mv == 12000
    assert msg.max_cell_voltage_mv == 4100

# ------------------------
# Test pack/unpack round-trip
# ------------------------
def test_telemetry_msg_pack_unpack():
    # Create a message with non-default values
    msg = BT_E6000_TelemetryMsg(
        b4=5,
        state=BT_E6000_TelemetryState.CHARGING,
        b6=10,
        b7=20,
        b8=30,
        voltage_mv=12345,
        max_cell_voltage_mv=4100,
        min_cell_volgate_mv=4000,
        max_temp_c=45,
        avg_temp_c=35,
        th002_temp_c=25,
        state_of_charge_pct=80,
        charge_counter=5,
        b20=1,
        b21=2,
        b22=3,
        b23=4,
        b24=5
    )

    packed = msg.pack()
    # Unpack into a new object
    msg2, msg_status = BT_E6000_TelemetryMsg.unpack(packed)

    # Compare all fields
    for field in msg.FIELDS:
        original_val = getattr(msg, field)
        unpacked_val = getattr(msg2, field)
        # If enum, compare enum types and values
        if isinstance(original_val, BT_E6000_TelemetryState):
            assert isinstance(unpacked_val, BT_E6000_TelemetryState)
            assert original_val == unpacked_val
        else:
            assert original_val == unpacked_val

# ------------------------
# Test default unpack works
# ------------------------
def test_telemetry_msg_unpack_defaults():
    # Pack default message
    msg = BT_E6000_TelemetryMsg()
    packed = msg.pack()
    msg2, msg_status = BT_E6000_TelemetryMsg.unpack(packed)
    
    # Ensure defaults are preserved
    assert msg2.b4 == 0
    assert msg2.state == BT_E6000_TelemetryState.UNKNOWN
    assert msg2.voltage_mv == 0