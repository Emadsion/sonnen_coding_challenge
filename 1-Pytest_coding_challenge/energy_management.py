"""
Author : Muhammad Emad
Status: Created
Date: 13/12/2024
"""
from configuration import EnergySystemConfiguration


class EnergyManagementSystem:

    # Manages energy flow in a solar + storage system.
    def __init__(self, configuration="Basic"):
        """
        Initialize the energy management system with a specific configuration.
        :param configuration: System configuration type
        """
        self.config = EnergySystemConfiguration.get_configuration(configuration)
        self.reset()

    def reset(self):
        """
        Reset the system state.
        """
        self.data = {
            "pv_output": 0,
            "house_consumption": 0,
            "battery_level": 0,
            "grid_use": 0,
            "battery_charge": 0,
            "battery_discharge": 0
        }

    def validate_input(self, pv_output, house_consumption, battery_level):
        """
        Validate input parameters.
        :raises ValueError: If any input is invalid
        """
        if (pv_output < 0 or pv_output > 100000 or house_consumption < 0 or house_consumption > 100000 or
                battery_level < 0 or battery_level > 100):

            raise ValueError("Invalid input values")

    def determine_energy_action(self, pv_output, house_consumption, battery_level):
        """
        Determine the appropriate energy management action.
        :return: Action to be taken
        """
        self.validate_input(pv_output, house_consumption, battery_level)

        # PV output exceeds house consumption
        if pv_output > house_consumption:
            # Battery is not full
            if battery_level < 100:
                return "charge_battery"
            else:
                # Battery is full
                return "send_to_grid"

        # PV output less than house consumption
        elif pv_output < house_consumption:
            # Battery has charge
            if battery_level > 0:
                return "discharge_battery"
            else:
                # No battery, use grid
                return "use_grid"

        # PV output exactly matches house consumption
        else:
            return "maintain_state"

    def manage_energy(self, pv_output, house_consumption, battery_level):
        """
        Manage energy based on current system state.
        :return: Updated system state
        """
        action = self.determine_energy_action(pv_output, house_consumption, battery_level)

        # Implement action-specific logic
        if action == "charge_battery":
            surplus = pv_output - house_consumption
            max_capacity = (100 - battery_level) / 100 * self.config['max_storage_units'] * self.config['unit_capacity']
            charge_amount = min(surplus, max_capacity)

            self.data['battery_charge'] = charge_amount
            self.data['grid_use'] = 0

        elif action == "send_to_grid":
            surplus = pv_output - house_consumption
            self.data['grid_use'] = surplus

        elif action == "discharge_battery":
            deficit = house_consumption - pv_output
            current_battery_charge = (battery_level / 100) * self.config['max_storage_units'] * self.config[
                'unit_capacity']
            discharge_amount = min(deficit, current_battery_charge)

            self.data['battery_discharge'] = discharge_amount
            self.data['grid_use'] = 0

        elif action == "use_grid":
            self.data['grid_use'] = -house_consumption

        return self.data
