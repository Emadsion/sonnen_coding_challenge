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
from energy_management import EnergyManagementSystem


def is_valid_boundary_test(configuration, max_storage_units, pv_output, expected_action):
    """
    Determine if a boundary test is valid for the current configuration
    """
    # Charging boundary tests
    if expected_action == "charge_battery":
        boundaries = {
            2: (3499, 3501),  # Basic config
            3: (3999, 4001),  # Standard config
            5: (4999, 5001)  # Pro config
        }

        # Check if the test's boundary matches the current configuration
        if any(boundary[0] <= pv_output <= boundary[1] and max_storage_units != config_max_units
               for config_max_units, boundary in boundaries.items()):
            return False

    # Discharging boundary tests
    elif expected_action == "discharge_battery":
        boundaries = {
            2: (1499, 1501),  # Basic config
            3: (999, 1001),  # Standard config
            5: (499, 501)  # Pro config
        }

        # Check if the test's boundary matches the current configuration
        if any(boundary[0] <= pv_output <= boundary[1] and max_storage_units != config_max_units
               for config_max_units, boundary in boundaries.items()):
            return False

    return True


@pytest.mark.parametrize("configuration, max_storage_units", [
    ("Basic", 2),
    ("Standard", 3),
    ("Pro", 5),
])
@pytest.mark.parametrize("pv_output, house_consumption, battery_level, expected_action", [
    # Typical Cases (Equivalence partitioning)
    (6000, 2500, 50, "charge_battery"),  # PV output exceeds usage, battery can store energy
    (2500, 2500, 50, "maintain_state"),  # PV output matches usage, no action needed
    (1200, 2500, 50, "discharge_battery"),  # PV output is less, battery should supply energy
    (1500, 2500, 0, "use_grid"),  # Low PV output, No battery power, use grid to meet demand
    (4500, 2500, 100, "send_to_grid"),  # Battery full, surplus PV sent to grid

    # Grid usage
    (0, 2500, 0, "use_grid"),  # No PV output, no battery output, use grid to meet demand
    (2501, 2500, 100, "send_to_grid"),  # Battery full, PV just above house consumption ,surplus PV sent to grid

    # Charging Boundary Tests
    (2501, 2500, 50, "charge_battery"),  # PV just above house consumption
    (4500, 2500, 99, "charge_battery"),  # Battery level just below 100%
    (4500, 2500, 0, "charge_battery"),  # Battery level 0%
    (4500, 2500, 1, "charge_battery"),  # Battery level just above 0%

    # Specific Boundary Value Analysis (BVA) for Charge
    (3499, 2500, 50, "charge_battery"),  # Basic config boundary
    (3500, 2500, 50, "charge_battery"),
    (3501, 2500, 50, "charge_battery"),

    (3999, 2500, 50, "charge_battery"),  # Standard config boundary
    (4000, 2500, 50, "charge_battery"),
    (4001, 2500, 50, "charge_battery"),

    (4999, 2500, 50, "charge_battery"),  # Pro config boundary
    (5000, 2500, 50, "charge_battery"),
    (5001, 2500, 50, "charge_battery"),

    # Discharging Boundary Tests
    (0, 2500, 50, "discharge_battery"),
    (1, 2500, 50, "discharge_battery"),
    (2499, 2500, 50, "discharge_battery"),
    (0, 2500, 1, "discharge_battery"),

    # Specific Boundary Value Analysis (BVA) for Charge
    (1499, 2500, 50, "discharge_battery"),  # Basic config boundary
    (1500, 2500, 50, "discharge_battery"),
    (1501, 2500, 50, "discharge_battery"),

    (999, 3000, 50, "discharge_battery"),  # Standard config boundary
    (1000, 3000, 50, "discharge_battery"),
    (1001, 3000, 50, "discharge_battery"),

    (499, 3000, 50, "discharge_battery"),  # Pro config boundary
    (500, 3000, 50, "discharge_battery"),
    (501, 3000, 50, "discharge_battery"),

])
def test_energy_management_boundaries(configuration, max_storage_units,
                                      pv_output, house_consumption, battery_level, expected_action):
    """
    Parameterized test for boundary scenarios across different configurations
    """
    # Skip tests that don't match the current configuration's boundary conditions
    if not is_valid_boundary_test(configuration, max_storage_units, pv_output, expected_action):
        pytest.skip(f"Boundary test not valid for {configuration} configuration")

    # Set up the system with specific configuration
    energy_system = EnergyManagementSystem(configuration)

    # Determine the action for the given scenario
    action = energy_system.determine_energy_action(pv_output, house_consumption, battery_level)

    # Assert the expected action
    assert action == expected_action, (
        f"Failed for config: {configuration}, "
        f"PV: {pv_output}, "
        f"Consumption: {house_consumption}, "
        f"Battery: {battery_level}"
    )
