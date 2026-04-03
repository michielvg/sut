# tests/messages/test_empty.py
import pytest
from messages.empty import EmptyMsg

# ------------------------
# Smoke test for EmptyMsg
# ------------------------
def test_empty_msg_pack():
    msg = EmptyMsg()
    packed = msg.pack()  # 3 header + 0 payload + 2 CRC = 5 bytes total

    assert isinstance(packed, bytes)
    assert len(packed) == 5

    # Header bytes
    start_byte, msg_id, length_byte = packed[:3]
    assert start_byte == 0x00          # start byte
    assert length_byte == 0x00         # payload length is 0

    # CRC bytes exist
    crc = packed[-2:]
    assert len(crc) == 2