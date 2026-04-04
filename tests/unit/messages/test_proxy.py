# tests/messages/test_proxy_msg.py
import pytest
from sut.messages.message import Msg, MsgType
from sut.messages.proxy import ProxyMsg

# ------------------------
# Test ProxyMsg instantiation
# ------------------------
def test_proxy_msg_init():
    msg = ProxyMsg()
    assert isinstance(msg, ProxyMsg)
    assert isinstance(msg, Msg)
    assert msg.TYPE == MsgType.PROXY
    # data should be empty initially
    assert msg.data == b''

# ------------------------
# Test packing with empty payload
# ------------------------
def test_proxy_msg_pack_empty():
    msg = ProxyMsg()
    packed = msg.pack()
    assert isinstance(packed, bytes)
    assert len(packed) == 0

# ------------------------
# Test unpack arbitrary payload
# ------------------------
def test_proxy_msg_unpack_arbitrary():
    # Construct arbitrary message:
    # Header: 0x00 0xHH 0xLL TYPE
    # Payload: 5 bytes
    # CRC: 2 bytes (just zeros for test)
    arbitrary_payload = bytes([1, 2, 3, 4, 5])
    raw_msg = bytes([0x00, 0x00, len(arbitrary_payload)]) + arbitrary_payload + bytes([0, 0])
    
    msg, status = ProxyMsg.unpack(raw_msg)
    assert isinstance(msg, ProxyMsg)
    # ProxyMsg should store raw payload in data
    assert msg.data[3:8] == arbitrary_payload
    assert msg.data[8] != 0
    assert msg.data[9] != 0

# ------------------------
# Test round-trip pack/unpack
# ------------------------
def test_proxy_msg_round_trip():
    payload = bytes([10, 20, 30, 40])
    raw_msg = bytes([0x00, 0x00, len(payload)]) + payload + bytes([0, 0])

    msg, status = ProxyMsg.unpack(raw_msg)
    packed = msg.pack()

    # Length should be consistent
    assert len(packed) == len(raw_msg)
    # Payload preserved
    assert packed[3:-2] == payload