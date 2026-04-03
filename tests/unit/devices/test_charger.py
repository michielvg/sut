# tests/devices/test_charger.py
import pytest
from unittest.mock import MagicMock
from sut.devices.charger import Charger
from sut.devices.device import Device

# ------------------------
# Test that Charger is a subclass of Device
# ------------------------
def test_charger_is_device_subclass():
    assert issubclass(Charger, Device)

# ------------------------
# Test abstract enforcement
# ------------------------
def test_charger_abstract_enforcement():
    mock_dispatcher = MagicMock()
    from sut.devices.charger import ChargerModel

    with pytest.raises(TypeError):
        Charger(model=ChargerModel.EC_E6000, dispatcher=mock_dispatcher)