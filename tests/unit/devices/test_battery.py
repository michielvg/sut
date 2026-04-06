# tests/devices/test_battery.py
import pytest
from unittest.mock import MagicMock

from sut.devices.battery import Battery
from sut.devices.device import Device
from sut.message_dispatcher import MessageDispatcher

# ------------------------
# Test that Battery is a subclass of Device
# ------------------------
def test_battery_is_device_subclass():
    assert issubclass(Battery, Device)