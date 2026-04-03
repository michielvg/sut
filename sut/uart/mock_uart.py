from sut.uart.uart_interface import UARTInterface

class MockUART(UARTInterface):
    def __init__(self):
        self.buffer = bytearray()

    def read(self, size: int = 1) -> bytes:
        data = self.buffer[:size]
        self.buffer = self.buffer[size:]
        return bytes(data)

    def write(self, data: bytes) -> int:
        self.buffer.extend(data) # echo input
        return len(data)
    
    def close(self):
        pass
    
    @property
    def in_waiting(self) -> int:
        return len(self.buffer)