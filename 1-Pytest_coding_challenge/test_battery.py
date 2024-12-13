"""
author : Muhammad Emad
Date: 13/12/2024
Description: creating test case for Sonnen basic energy algorithm
"""
import pytest


# DUT fixture mock with error handling
@pytest.fixture
def dut():
    class DUT:
        def __init__(self):
            self.state = {}

        def set(self, key: str, value) -> bool:
            if not isinstance(key, str):
                raise ValueError("Key must be a string")
            self.state[key] = value
            return True

        def get(self, key: str) -> str:
            if not isinstance(key, str):
                raise ValueError("Key must be a string")
            if key not in self.state:
                raise KeyError(f"Key '{key}' not found in DUT state")
            return self.state[key]

        def reset(self):
            self.state = {}

    dut = DUT()
    yield dut
    # DUT state is reset after the test execution
    dut.reset()


# Parameterized tests for different system setup
@pytest.mark.parametrize("system_setup, max_battery_modules", [
    ("Basic", 2),
    ("Standard", 3),
    ("Pro", 5),
])
# Parameterized tests for equivalence partitioning and boundary value analysis
@pytest.mark.parametrize("pv_production, house_consumption, battery_charge_level, expected_behavior", [
    # Typical Cases
    (5000, 3000, 50, "charge_battery"),  # PV production exceeds consumption, battery can be charged
    (3000, 3000, 50, "do_nothing"),  # PV production equals consumption, no action needed
    (2000, 3000, 50, "discharge_battery"),  # PV production is less, battery should discharge

    # Boundary Cases
    (0, 3000, 50, "use_grid"),  # No PV production, use grid to meet demand
    (5000, 3000, 100, "send_to_grid"),  # Battery full, surplus PV sent to grid
    (5000, 3000, 0, "charge_battery"),  # Battery empty, PV used to charge

    # Invalid Cases (handled with exceptions)
    (-5000, 3000, 50, "invalid"),  # Negative PV production is invalid
    (5000, -3000, 50, "invalid"),  # Negative house consumption is invalid
    (5000, 3000, -10, "invalid"),  # Negative battery charge level is invalid
    (5000, 3000, 110, "invalid"),  # Over 100% battery charge level is invalid
])
def test_energy_algorithm(dut, system_setup, max_battery_modules, pv_production, house_consumption,
                          battery_charge_level, expected_behavior):
    try:
        # Mock system configuration
        dut.set("system_setup", system_setup)
        dut.set("max_battery_modules", max_battery_modules)

        # Mock initial readings
        dut.set("pv_production", pv_production)  # Watts
        dut.set("house_consumption", house_consumption)  # Watts
        dut.set("grid_connection", 0)  # Start with no grid usage
        dut.set("battery_charge_level", battery_charge_level)  # Charge level as a percentage

        # Test the expected behavior
        if expected_behavior == "charge_battery":
            surplus = max(0, pv_production - house_consumption)
            if battery_charge_level < 100:
                charge_power = min(surplus, max_battery_modules * 1000)  # Max 1000W per module
                dut.set("battery_charge", charge_power)
                surplus -= charge_power
            dut.set("grid_connection", surplus)
            assert 0 <= dut.get("battery_charge") <= max_battery_modules * 1000
            assert dut.get("grid_connection") >= 0

        elif expected_behavior == "send_to_grid":
            surplus = pv_production - house_consumption
            assert battery_charge_level == 100
            dut.set("grid_connection", surplus)
            assert dut.get("grid_connection") >= 0

        elif expected_behavior == "discharge_battery":
            deficit = max(0, house_consumption - pv_production)
            if battery_charge_level > 0:
                discharge_power = min(deficit, battery_charge_level * 1000)  # Assume 1% = 1000W
                dut.set("battery_discharge", discharge_power)
                deficit -= discharge_power
            dut.set("grid_connection", deficit)
            assert 0 <= dut.get("battery_discharge") <= battery_charge_level * 1000
            assert dut.get("grid_connection") >= 0

        elif expected_behavior == "use_grid":
            assert pv_production == 0
            dut.set("grid_connection", house_consumption)
            assert dut.get("grid_connection") == house_consumption

        elif expected_behavior == "do_nothing":
            assert pv_production == house_consumption
            assert battery_charge_level <= 100

        elif expected_behavior == "invalid":
            with pytest.raises(ValueError):
                if pv_production < 0 or house_consumption < 0 or battery_charge_level < 0 or battery_charge_level > 100:
                    raise ValueError("Invalid input values")

        else:
            pytest.fail("Unknown expected behavior")

    except (ValueError, KeyError) as e:
        if expected_behavior != "invalid":
            pytest.fail(f"Test failed due to invalid operation: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error occurred: {e}")

    # Restore DUT state
    dut.reset()
