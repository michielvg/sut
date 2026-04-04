# tests/unit/uart/test_pyserial_uart.py
import pytest
from unittest.mock import MagicMock, patch
from sut.uart.pyserial_uart import PySerialUART

# ------------------------
# Fixtures
# ------------------------
@pytest.fixture
def mock_serial():
    with patch("sut.uart.pyserial_uart.serial.Serial") as mock_ser_cls:
        mock_ser = MagicMock()
        mock_ser.read.return_value = b"x"
        mock_ser.write.return_value = 1
        mock_ser.in_waiting = 42
        mock_ser_cls.return_value = mock_ser
        yield mock_ser, mock_ser_cls

@pytest.fixture
def pyserial_uart(mock_serial):
    mock_ser, _ = mock_serial
    uart = PySerialUART(port="/dev/null")
    return uart, mock_ser

# ------------------------
# Initialization tests
# ------------------------
def test_init_calls_serial(mock_serial):
    _, mock_ser_cls = mock_serial
    uart = PySerialUART(port="/dev/null", baudrate=115200, bytesize=7, parity='E', stopbits=2, timeout=0.2)
    mock_ser_cls.assert_called_once_with(
        "/dev/null",
        115200,
        bytesize=7,
        parity='E',
        stopbits=2,
        timeout=0.2
    )

def test_from_config_calls_init(mock_serial):
    _, mock_ser_cls = mock_serial
    cfg = {"port": "/dev/ttyUSB0", "baud": 4800, "timeout": 0.5}
    uart = PySerialUART.from_config(cfg)
    mock_ser_cls.assert_called_once_with(
        "/dev/ttyUSB0",
        4800,
        bytesize=8,
        parity='N',
        stopbits=1,
        timeout=0.5
    )

# ------------------------
# Read tests
# ------------------------
def test_read_returns_bytes(pyserial_uart):
    uart, mock_ser = pyserial_uart
    data = uart.read(3)
    mock_ser.read.assert_called_once_with(3)
    assert data == b"x"

# ------------------------
# Write tests
# ------------------------
def test_write_returns_written_length(pyserial_uart):
    uart, mock_ser = pyserial_uart
    n = uart.write(b"abc")
    mock_ser.write.assert_called_once_with(b"abc")
    assert n == 1

# ------------------------
# in_waiting tests
# ------------------------
def test_in_waiting_property(pyserial_uart):
    uart, mock_ser = pyserial_uart
    assert uart.in_waiting == 42

# ------------------------
# Close tests
# ------------------------
def test_close_calls_serial_close(pyserial_uart):
    uart, mock_ser = pyserial_uart
    uart.close()
    mock_ser.close.assert_called_once()

def test_close_exception_handled(pyserial_uart):
    uart, mock_ser = pyserial_uart

    # Make close() raise an exception
    mock_ser.close.side_effect = Exception("test error")

    # Should not raise, just swallow
    uart.close()

    # Ensure close was called
    mock_ser.close.assert_called_once()