# tests/unit/uart/test_uart_interface.py
import pytest
from sut.uart.uart_interface import UARTInterface

# ------------------------
# Abstract class tests
# ------------------------
def test_cannot_instantiate_abstract_class():
    with pytest.raises(TypeError):
        UARTInterface()

# ------------------------
# Subclass enforcement tests
# ------------------------
class DummyUART(UARTInterface):
    def read(self, size: int = 1) -> bytes:
        return b"x"

    def write(self, data: bytes) -> int:
        return len(data)

    def close(self):
        return None

    @property
    def in_waiting(self) -> int:
        return 0

def test_subclass_implements_all_methods():
    uart = DummyUART()
    # read
    data = uart.read(5)
    assert data == b"x"
    # write
    n = uart.write(b"abc")
    assert n == 3
    # close
    uart.close()  # should not raise
    # in_waiting
    assert uart.in_waiting == 0