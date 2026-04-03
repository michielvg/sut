# tests/unit/uart/test_mock_uart.py
import pytest
from uart.mock_uart import MockUART

# ------------------------
# Fixtures
# ------------------------
@pytest.fixture
def mock_uart():
    return MockUART()


# ------------------------
# Initialization tests
# ------------------------
def test_mock_uart_initial_buffers(mock_uart):
    assert mock_uart.buffer == bytearray()
    assert mock_uart.in_waiting == 0


# ------------------------
# Write tests
# ------------------------
def test_write_echoes_to_in_buffer(mock_uart):
    data = b'hello'
    bytes_written = mock_uart.write(data)

    assert bytes_written == len(data)
    # Because write echoes to in_buffer
    assert mock_uart.buffer == data


# ------------------------
# Read tests
# ------------------------
def test_read_consumes_in_buffer(mock_uart):
    # Preload in_buffer
    mock_uart.buffer.extend(b'abcde')
    
    # Read 3 bytes
    result = mock_uart.read(3)
    assert result == b'abc'
    assert mock_uart.buffer == b'de'
    
    # Read more than remaining
    result = mock_uart.read(5)
    assert result == b'de'
    assert mock_uart.buffer == b''


# ------------------------
# in_waiting property
# ------------------------
def test_in_waiting_reflects_out_buffer_length(mock_uart):
    assert mock_uart.in_waiting == 0
    mock_uart.buffer.extend(b'12345')
    assert mock_uart.in_waiting == 5


# ------------------------
# Close method
# ------------------------
def test_close_does_nothing(mock_uart):
    # Should not raise any exception
    mock_uart.close()