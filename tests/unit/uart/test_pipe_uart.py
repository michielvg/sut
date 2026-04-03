# tests/unit/uart/test_pipe_uart.py
import os
import pytest
from uart.pipe_uart import PipeUART

# ------------------------
# Fixtures
# ------------------------
@pytest.fixture
def pipe_path(tmp_path):
    """Provide a temporary FIFO path."""
    return tmp_path / "sut_pipe"


@pytest.fixture
def pipe_uart(pipe_path):
    uart = PipeUART(str(pipe_path))
    yield uart
    uart.close()
    if os.path.exists(pipe_path):
        os.remove(pipe_path)


# ------------------------
# Initialization tests
# ------------------------
def test_pipe_uart_creates_fifo(pipe_path):
    assert not os.path.exists(pipe_path)
    uart = PipeUART(str(pipe_path))
    uart.close()
    assert os.path.exists(pipe_path)
    os.remove(pipe_path)


# ------------------------
# Read tests
# ------------------------
def test_read_returns_bytes(pipe_uart):
    # Write some data to the pipe using the write end
    os.write(pipe_uart.fd_write, b'abc')
    data = pipe_uart.read(2)
    assert data == b'ab'
    # Remaining byte
    data = pipe_uart.read(2)
    assert data == b'c'
    # Reading more than available returns b''
    data = pipe_uart.read(5)
    assert data == b''


def test_read_nonblocking_returns_empty(pipe_uart):
    # No data available → should return b'' without blocking
    data = pipe_uart.read(5)
    assert data == b''


# ------------------------
# in_waiting tests
# ------------------------
def test_in_waiting_returns_constant(pipe_uart):
    # Returns fixed value as implemented
    assert pipe_uart.in_waiting == 1024


# ------------------------
# Close tests
# ------------------------
def test_close_closes_fds(pipe_uart):
    fd_read = pipe_uart.fd_read
    fd_write = pipe_uart.fd_write
    pipe_uart.close()
    # FDs should be closed → attempting to os.read should fail
    with pytest.raises(OSError):
        os.read(fd_read, 1)
    with pytest.raises(OSError):
        os.write(fd_write, b'x')