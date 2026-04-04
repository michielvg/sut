import os
from sut.uart.uart_interface import UARTInterface

class PipeUART(UARTInterface):
    """Reads/writes from a pipe (FIFO)."""
    def __init__(self, path: str = '/tmp/sut_pipe'):
        in_path = path + '_in'
        out_path = path + '_out'
        # Open FIFO
        if not os.path.exists(in_path):
            os.mkfifo(in_path)
        self.fd_in_read = os.open(in_path, os.O_RDONLY | os.O_NONBLOCK)
        # Open a write end in the same process to prevent EOF
        self.fd_in_write = os.open(in_path, os.O_WRONLY | os.O_NONBLOCK)

        if not os.path.exists(out_path):
            os.mkfifo(out_path)

        self.fd_out_read = os.open(out_path, os.O_RDONLY | os.O_NONBLOCK)
        self.fd_out_write = os.open(out_path, os.O_WRONLY | os.O_NONBLOCK)

    def read(self, size: int = 1) -> bytes:
        try:
            return os.read(self.fd_in_read, size)
        except BlockingIOError:
            return b''

    def write(self, data: bytes) -> int:
        return os.write(self.fd_out_write, data)

    @property
    def in_waiting(self) -> int:
        """Return number of bytes available to read."""
        return 1024 # Pipe uses non blocking read, otherwise whe have no way of knowing.
    
    def close(self):
        """Close both ends of the pipe cleanly."""
        try:
            os.close(self.fd_in_read)
        except Exception:
            pass
        try:
            os.close(self.fd_out_read)
        except Exception:
            pass