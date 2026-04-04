# tests/unit/uart/test_pipe_uart.py
import os
import pytest
from sut.uart.pipe_uart import PipeUART

# ------------------------
# Fixtures
# ------------------------
@pytest.fixture
def pipe_path(tmp_path):
    return tmp_path / "sut_pipe"

@pytest.fixture
def pipe_in_path(pipe_path):
    return pipe_path.with_name(pipe_path.stem + "_in")

@pytest.fixture
def pipe_out_path(pipe_path):
    return pipe_path.with_name(pipe_path.stem + "_out")

@pytest.fixture
def pipe_uart(pipe_path, pipe_in_path, pipe_out_path):
    uart = PipeUART(str(pipe_path))
    yield uart
    uart.close()
    if os.path.exists(pipe_in_path):
        os.remove(pipe_in_path)
    if os.path.exists(pipe_out_path):
        os.remove(pipe_out_path)

# ------------------------
# Initialization tests
# ------------------------
def test_pipe_uart_creates_fifo(pipe_path, pipe_in_path, pipe_out_path):
    # Remove if already exists
    if os.path.exists(pipe_in_path):
        os.remove(pipe_in_path)
    if os.path.exists(pipe_out_path):
        os.remove(pipe_out_path)

    uart = PipeUART(str(pipe_path))
    uart.close()

    assert os.path.exists(pipe_in_path)
    assert os.path.exists(pipe_out_path)

# ------------------------
# Read tests
# ------------------------
def test_read_returns_bytes(pipe_uart, pipe_in_path):
    # Write directly to the read FIFO
    fd_write = os.open(pipe_in_path, os.O_WRONLY | os.O_NONBLOCK)
    os.write(fd_write, b'abc')
    os.close(fd_write)

    # Read via PipeUART
    data = pipe_uart.read(2)
    assert data == b'ab'
    data = pipe_uart.read(2)
    assert data == b'c'
    data = pipe_uart.read(5)
    assert data == b''

def test_read_nonblocking_returns_empty(pipe_uart):
    # No data available → should return b'' without blocking
    data = pipe_uart.read(5)
    assert data == b''

# ------------------------
# Write tests
# ------------------------
def test_write_sends_bytes(pipe_uart, pipe_out_path):
    # Open read end of output pipe
    fd_read = os.open(pipe_out_path, os.O_RDONLY | os.O_NONBLOCK)

    # Write via PipeUART
    written = pipe_uart.write(b'xyz')
    assert written == 3  # os.write returns number of bytes written

    # Read what was written
    data = os.read(fd_read, 10)
    assert data == b'xyz'

    os.close(fd_read)

# ------------------------
# in_waiting tests
# ------------------------
def test_in_waiting_returns_constant(pipe_uart):
    assert pipe_uart.in_waiting == 1024

# ------------------------
# Close tests
# ------------------------
def test_close_closes_fds(pipe_uart):
    fds = [pipe_uart.fd_in_read, pipe_uart.fd_in_write,
           pipe_uart.fd_out_read, pipe_uart.fd_out_write]

    pipe_uart.close()

    # All FDs should be closed → reading/writing raises OSError
    for fd in fds:
        with pytest.raises(OSError):
            os.read(fd, 1)
        with pytest.raises(OSError):
            os.write(fd, b'x')