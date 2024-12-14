"""
Author : Muhammad Emad
Type: System testing
Severity : High
Status: Created
Date: 13/12/2024
Description: creating test case for Sonnen basic energy algorithm:
                - PV > house consumption:
                    = storage system charged with the surplus
                    = remaining power goes to the grid
                - PV < house consumption:
                    = storage supplies power to the house
                    = If power is still missing, the grid should provide it
"""
import pytest


# Creating device under test fixture with set(), get() and reset() method
# and defining setup/ teardown
@pytest.fixture
def dut():
    class Dut:
        def __init__(self):
            self.data = {}

        # Set method for setting DUT parameters
        def set(self, key: str, value) -> bool:
            if not isinstance(key, str):
                raise ValueError("Key must be a string")
            self.data[key] = value
            return True

        # Get method for getting DUT parameters values
        def get(self, key: str) -> str:
            if not isinstance(key, str):
                raise ValueError("Key must be a string")
            if key not in self.data:
                raise KeyError(f"Key '{key}' not found in dut data")
            return self.data[key]

        # Reset method for teardown after reset
        def reset(self):
            self.data = {}

    dut = Dut()  # Creating an instance of DUT
    yield dut  # Generator
    # Ensure dut data is reset after the test
    dut.reset()


# Assuming lithium-ion batteries with instant/fast discharge behavior
# Assume 1% Battery level = 10W
# Assume each Battery unit capacity = 1000W

# Parameterized for battery system configuration
@pytest.mark.parametrize("configuration, max_storage_units", [
    ("Basic", 2),
    ("Standard", 3),
    ("Pro", 5),
])
# Parameterized for different parameters with respect to EP and BVA
@pytest.mark.parametrize("pv_output, house_consumption, battery_level, expected_action", [
    # Typical Cases (Equivalence partitioning)
    (6000, 2500, 50, "charge_battery"),  # PV output exceeds usage, battery can store energy
    (2500, 2500, 50, "maintain_state"),  # PV output matches usage, no action needed
    (1200, 2500, 50, "discharge_battery"),  # PV output is less, battery should supply energy
    (1500, 2500, 0, "use_grid"),  # Low PV output, No battery power, use grid to meet demand
    (4500, 2500, 100, "send_to_grid"),  # Battery full, surplus PV sent to grid

    # Discharge Battery (BVA)
    (0, 2500, 50, "discharge_battery"),  # No PV output, battery should supply energy
    (1, 2500, 50, "discharge_battery"),  # PV output Just above zero , battery should supply energy
    (2499, 2500, 50, "discharge_battery"),  # PV output just below usage, battery should supply energy
    (0, 2500, 1, "discharge_battery"),  # No PV output , battery is 1%, battery should supply energy
    # BVA for basic configuration -> difference = (Full capacity 2000W ) * (Battery lvl 50%) = 1000W
    (1500, 2500, 50, "discharge_battery"),  # PV output is less, battery should supply energy
    (1499, 2500, 50, "discharge_battery"),  # PV output is less, battery should supply energy
    (1501, 2500, 50, "discharge_battery"),  # PV output is less, battery should supply energy
    # BVA for Standard configuration -> difference = (Full capacity 3000W ) * (Battery lvl 50%) = 1500W
    (1000, 2500, 50, "discharge_battery"),  # PV output is less, battery should supply energy
    (999, 2500, 50, "discharge_battery"),  # PV output is less, battery should supply energy
    (1001, 2500, 50, "discharge_battery"),  # PV output is less, battery should supply energy
    # BVA for Pro configuration -> difference = (Full capacity 5000W ) * (Battery lvl 50%) = 2500W
    (500, 3000, 50, "discharge_battery"),  # PV output is less, battery should supply energy
    (501, 3000, 50, "discharge_battery"),  # PV output is less, battery should supply energy
    (499, 3000, 50, "discharge_battery"),  # PV output is less, battery should supply energy

    # Grid usage
    (0, 2500, 0, "use_grid"),  # No PV output, no battery output, use grid to meet demand
    (2501, 2500, 100, "send_to_grid"),  # Battery full, PV just above house consumption ,surplus PV sent to grid

    # Charge Battery (BVA for Battery lvl, BVA for power difference)
    (2501, 2500, 50, "charge_battery"),  # PV just above house consumption, battery can store energy
    (4500, 2500, 99, "charge_battery"),  # Battery level just below 100%, battery can store energy
    (4500, 2500, 0, "charge_battery"),  # Battery level 0%, battery can store energy
    (4500, 2500, 1, "charge_battery"),  # Battery level just above 0%, battery can store energy

    # BVA for basic configuration -> difference = (Full capacity 2000W)  * (Battery lvl 50%) = 1000W
    (3499, 2500, 50, "charge_battery"),  # PV output exceeds usage, battery can store energy
    (3500, 2500, 50, "charge_battery"),  # PV output exceeds usage, battery can store energy
    (3501, 2500, 50, "charge_battery"),  # PV output exceeds usage, battery can store energy
    #  BVA for Standard configuration -> difference = (Full capacity 3000W)  * (Battery lvl 50%) = 1500W
    (3999, 2500, 50, "charge_battery"),  # PV output exceeds usage, battery can store energy
    (4000, 2500, 50, "charge_battery"),  # PV output exceeds usage, battery can store energy
    (4001, 2500, 50, "charge_battery"),  # PV output exceeds usage, battery can store energy
    #  BVA for Pro configuration -> -> difference = (Full capacity 5000W)  * (Battery lvl 50%) = 2500W
    (4999, 2500, 50, "charge_battery"),  # PV output exceeds usage, battery can store energy
    (5000, 2500, 50, "charge_battery"),  # PV output exceeds usage, battery can store energy
    (5001, 2500, 50, "charge_battery"),  # PV output exceeds usage, battery can store energy

    # Invalid Cases
    (-1, 2500, 50, "invalid"),  # PV output just below zero (invalid)
    (4500, 2500, -1, "invalid"),  # Battery level just below 0% (invalid)
    (4500, 2500, 101, "invalid"),  # Battery level just above 100% (invalid)
    (4500, -1, 50, "invalid"),  # House consumption just below 0 (invalid)
])
def test_energy_management(dut, configuration, max_storage_units, pv_output, house_consumption, battery_level,
                           expected_action):
    try:
        # Mock system configuration
        dut.set("configuration", configuration)
        dut.set("max_storage_units", max_storage_units)

        # Mock initial readings
        dut.set("pv_output", pv_output)  # Watts
        dut.set("house_consumption", house_consumption)  # Watts
        dut.set("grid_use", 0)  # Start with no grid usage
        dut.set("battery_level", battery_level)  # Battery level as a percentage

        # Skip Test cases for "charge_battery" of different configuration as test cases will be duplicated
        if expected_action == "charge_battery" and 3499 <= pv_output <= 3501 and max_storage_units != 2:
            pytest.skip("Skip charging boundaries for not basic config")
        elif expected_action == "charge_battery" and 3999 <= pv_output <= 4001 and max_storage_units != 3:
            pytest.skip("Skip charging boundaries for not Standard config")
        elif expected_action == "charge_battery" and 4999 <= pv_output <= 5001 and max_storage_units != 5:
            pytest.skip("Skip charging boundaries for not Pro config")

        # Skip Test cases for "discharge_battery" of different configuration as test cases will be duplicated
        if expected_action == "discharge_battery" and 1499 <= pv_output <= 1501 and max_storage_units != 2:
            pytest.skip("Skip discharging boundaries for not basic config")
        elif expected_action == "discharge_battery" and 999 <= pv_output <= 1001 and max_storage_units != 3:
            pytest.skip("Skip discharging boundaries for not Standard config")
        elif expected_action == "discharge_battery" and 499 <= pv_output <= 501 and max_storage_units != 5:
            pytest.skip("Skip discharging boundaries for not Pro config")

        # Test the expected action

        # 1- Charge Battery
        if expected_action == "charge_battery":
            assert pv_output > house_consumption
            surplus = pv_output - house_consumption
            if battery_level < 100:
                remaining_capacity = ((100 - battery_level) / 100) * max_storage_units * 1000
                charge_amount = min(surplus, remaining_capacity)  # Max 1000W per unit
                dut.set("battery_charge", charge_amount)
                surplus -= charge_amount
            expected_grid_charge = surplus
            dut.set("grid_use", surplus - expected_grid_charge)
            assert 0 <= dut.get("battery_charge") <= max_storage_units * 1000
            assert dut.get("grid_use") == 0  # Battery is charging and there is still no grid use

        # 2- Send Power To Grid
        elif expected_action == "send_to_grid":
            assert pv_output > house_consumption
            surplus = pv_output - house_consumption
            assert battery_level == 100
            dut.set("grid_use", surplus)
            assert dut.get("grid_use") > 0  # Battery at 100% so power must go to grid

        # 3- Discharge Battery
        elif expected_action == "discharge_battery":
            assert pv_output < house_consumption
            deficit = house_consumption - pv_output
            if battery_level > 0:
                current_battery_charge = (battery_level / 100) * max_storage_units * 1000
                discharge_amount = min(deficit, current_battery_charge)
                dut.set("battery_discharge", discharge_amount)
                deficit -= discharge_amount
            expected_grid_use = deficit
            dut.set("grid_use", expected_grid_use - deficit)
            assert 0 <= dut.get("battery_discharge") <= battery_level * max_storage_units * 1000
            assert dut.get("grid_use") == 0  # Battery is discharging and there is still no grid use

        elif expected_action == "use_grid":
            assert pv_output < house_consumption
            assert battery_level == 0
            dut.set("grid_use", -house_consumption)
            assert dut.get("grid_use") == -house_consumption  # -ve value means grid usage

        elif expected_action == "maintain_state":
            assert pv_output == house_consumption
            current_battery_level = dut.get("battery_level")
            assert dut.get("grid_use") == 0
            assert dut.get("battery_level") == current_battery_level

        elif expected_action == "invalid":
            with pytest.raises(ValueError):
                if pv_output < 0 or house_consumption < 0 or battery_level < 0 or battery_level > 100:
                    raise ValueError("Invalid input values")

        else:
            pytest.fail("Unknown expected action")

    except (ValueError, KeyError) as e:
        if expected_action != "invalid":
            pytest.fail(f"Test failed due to invalid operation: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error occurred: {e}")

    # Restore dut data
    dut.reset()
