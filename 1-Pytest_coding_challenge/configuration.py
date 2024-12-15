"""
Author : Muhammad Emad
Status: Created
Date: 13/12/2024
"""


class EnergySystemConfiguration:
    # Represents different configurations of energy storage systems.
    CONFIGURATIONS = {
        "Basic": {
            "max_storage_units": 2,
            "unit_capacity": 1000  # Watts
        },
        "Standard": {
            "max_storage_units": 3,
            "unit_capacity": 1000  # Watts
        },
        "Pro": {
            "max_storage_units": 5,
            "unit_capacity": 1000  # Watts
        }
    }

    @classmethod
    def get_configuration(cls, config_name):
        """
        Retrieve configuration details for a given system type.
        :param config_name: Name of the configuration
        :return: Configuration dictionary
        :raises ValueError: If configuration is not found
        """
        if config_name not in cls.CONFIGURATIONS:
            raise ValueError(f"Invalid configuration: {config_name}")
        return cls.CONFIGURATIONS[config_name]
