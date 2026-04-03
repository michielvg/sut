# tests/devices/test_device.py
import pytest
from sut.devices.device import Device
from unittest.mock import MagicMock

# ------------------------
# Test that Device cannot be instantiated directly
# ------------------------
def test_device_abstract_enforcement():
    from sut.devices.device import Device
    with pytest.raises(TypeError):
        Device(model="X", dispatcher=MagicMock())

# ------------------------
# Test concrete subclass stores model and dispatcher and calls setup
# ------------------------
def test_device_concrete_subclass_initialization():
    mock_dispatcher = MagicMock()
    setup_called = []

    class MyDevice(Device):
        def setup(self):
            setup_called.append(True)

    device = MyDevice(model="MyModel", dispatcher=mock_dispatcher)

    assert device.model == "MyModel"
    assert device.dispatcher == mock_dispatcher
    assert setup_called == [True]