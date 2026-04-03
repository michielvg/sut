# tests/messages/test_timestamp.py
import pytest
from messages.timestamp import TimestampMsg
from messages.message import Msg

# ------------------------
# Test TimestampMsg pack
# ------------------------
def test_timestamp_msg_pack():
    msg = TimestampMsg(year=21, month=4, day=3, hour=15, min=30, sec=45)
    packed = msg.pack()  # should produce 11 bytes: header + payload + CRC

    assert isinstance(packed, bytes)
    assert len(packed) == 12  # header (4) + payload (6) + CRC (2)

    # Payload is in the middle (after 3-byte header, before 2-byte CRC)
    payload = packed[4:-2]
    assert packed[3] == TimestampMsg.TYPE.value
    assert list(payload) == [21, 4, 3, 15, 30, 45]

    # Check masking behavior with out-of-range values
    msg = TimestampMsg(year=300, month=256, day=-1, hour=260, min=-5, sec=500)
    packed = msg.pack()
    payload = packed[4:-2]
    assert list(payload) == [300 & 0xFF, 256 & 0xFF, (-1) & 0xFF, 260 & 0xFF, (-5) & 0xFF, 500 & 0xFF]