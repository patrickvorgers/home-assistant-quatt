"""Constants for quatt."""

from logging import Logger, getLogger
from typing import Final

LOGGER: Logger = getLogger(__package__)

NAME = "Quatt"
DOMAIN = "quatt"
ATTRIBUTION = "marcoboers"

CONF_POWER_SENSOR = "power_sensor"

DEVICE_CIC_ID = "cic"
DEVICE_FLOWMETER_ID = "flowmeter"
DEVICE_BOILER_ID = "boiler"
DEVICE_THERMOSTAT_ID = "thermostat"
DEVICE_HEATPUMP1_ID = "heatpump_1"
DEVICE_HEATPUMP2_ID = "heatpump_2"

DEVICE_LIST = [
    {"name": "CIC", "id": DEVICE_CIC_ID},
    {"name": "Boiler", "id": DEVICE_BOILER_ID},
    {"name": "Thermostat", "id": DEVICE_THERMOSTAT_ID},
    {"name": "Flowmeter", "id": DEVICE_FLOWMETER_ID},
    {"name": "Heatpump 1", "id": DEVICE_HEATPUMP1_ID},
    {"name": "Heatpump 2", "id": DEVICE_HEATPUMP2_ID},
]

# Defaults
DEFAULT_SCAN_INTERVAL: Final = 10
MIN_SCAN_INTERVAL: Final = 5
MAX_SCAN_INTERVAL: Final = 600
