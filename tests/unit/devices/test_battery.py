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

# ------------------------
# Test that Battery cannot be instantiated directly (setup not implemented)
# ------------------------
def test_battery_abstract_enforcement():
    mock_dispatcher = MagicMock(spec=MessageDispatcher)
    from sut.devices.battery import Battery
    from sut.devices.battery import BatteryModel

    with pytest.raises(TypeError):
        Battery(model=BatteryModel.BT_E6000, dispatcher=mock_dispatcher)