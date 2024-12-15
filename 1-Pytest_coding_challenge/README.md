# Solar Energy Management System

## Project Overview

This project implements an advanced energy management system for solar and battery storage configurations. The system intelligently manages energy flow between solar panel output, house consumption, battery storage, and grid interaction.

## Features

- Supports multiple energy system configurations (Basic, Standard, Pro)
- Battery charging and discharging management
- Grid interaction optimization
- Comprehensive test suite using pytest

## System Configurations

The system supports three energy configuration levels:
- Basic: 2 storage units
- Standard: 3 storage units
- Pro: 5 storage units

### Python Version
- Python 3.8+

### Required Libraries
- `pytest` (for running tests)
- `configuration` module (custom configuration management)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/Emadsion/sonnen_coding_challenge.git
cd 1-Pytest_coding_challenge
```

2. Install dependencies:
```bash
pip install pytest
```

## Running Tests

To run the test suite, execute:
```bash
pytest test-energy-management.py
```

## Test Scenarios Covered

The test suite covers The basic energy algorithm :
-  PV output exceeds consumption and battery is not full -> Charging battery 
- PV output exceeds consumption and battery is full -> Sending surplus energy to grid
- PV output is insufficient for consumption and battery has charge -> Discharging battery 
- PV output is insufficient for consumption and battery is drained -> Grid usage 
- Boundary value analysis for the three different configurations

## Configuration Parameters

- `pv_output`: Solar panel energy output (watts)
- `house_consumption`: Energy consumed by the house (watts)
- `battery_level`: Current battery charge percentage (0-100)

## Expected Actions

- `charge_battery`: Store excess solar energy
- `send_to_grid`: Export surplus energy
- `discharge_battery`: Use stored battery energy
- `use_grid`: Draw power from the electrical grid
- `maintain_state`: No action required

## Contact

Muhammad Emad - [muhammad7emad98@gmail.com]

Project Link: [https://github.com/Emadsion/sonnen_coding_challenge.git](https://github.com/Emadsion/sonnen_coding_challenge.git)
