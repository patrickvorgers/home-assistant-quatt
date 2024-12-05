"""Binary sensor platform for quatt."""
from __future__ import annotations

import logging

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorEntityDescription,
)

from .const import (
    DEVICE_BOILER_ID,
    DEVICE_CIC_ID,
    DEVICE_HEATPUMP1_ID,
    DEVICE_HEATPUMP2_ID,
    DEVICE_LIST,
    DEVICE_THERMOSTAT_ID,
    DOMAIN,
)
from .coordinator import QuattDataUpdateCoordinator
from .entity import QuattEntity, QuattSensorEntityDescription

BINARY_SENSORS = [
    # Heatpump 1
    QuattSensorEntityDescription(
        name="Silentmode",
        key="hp1.silentModeStatus",
        translation_key="hp_silentModeStatus",
        icon="mdi:sleep",
        quatt_device_info=DEVICE_HEATPUMP1_ID,
    ),
    QuattSensorEntityDescription(
        name="Limited by COP",
        key="hp1.limitedByCop",
        translation_key="hp_silentModeStatus",
        icon="mdi:arrow-collapse-up",
        quatt_device_info=DEVICE_HEATPUMP1_ID,
    ),
    QuattSensorEntityDescription(
        name="Defrost",
        key="hp1.computedDefrost",
        translation_key="hp_silentModeStatus",
        icon="mdi:snowflake",
        quatt_device_info=DEVICE_HEATPUMP1_ID,
    ),
    # Heatpump 2
    QuattSensorEntityDescription(
        name="Silentmode",
        key="hp2.silentModeStatus",
        translation_key="hp_silentModeStatus",
        icon="mdi:sleep",
        quatt_duo=True,
        quatt_device_info=DEVICE_HEATPUMP2_ID,
    ),
    QuattSensorEntityDescription(
        name="Limited by COP",
        key="hp2.limitedByCop",
        translation_key="hp_silentModeStatus",
        icon="mdi:arrow-collapse-up",
        quatt_duo=True,
        quatt_device_info=DEVICE_HEATPUMP2_ID,
    ),
    QuattSensorEntityDescription(
        name="Defrost",
        key="hp2.computedDefrost",
        icon="mdi:snowflake",
        quatt_duo=True,
        quatt_device_info=DEVICE_HEATPUMP2_ID,
    ),
    # Boiler
    QuattSensorEntityDescription(
        name="Boiler",
        key="boiler.otFbChModeActive",
        icon="mdi:heating-coil",
        quatt_device_info=DEVICE_BOILER_ID,
    ),
    QuattSensorEntityDescription(
        name="Domestic hot water",
        key="boiler.otFbDhwActive",
        icon="mdi:water-boiler",
        quatt_device_info=DEVICE_BOILER_ID,
    ),
    QuattSensorEntityDescription(
        name="Flame",
        key="boiler.otFbFlameOn",
        icon="mdi:fire",
        quatt_device_info=DEVICE_BOILER_ID,
    ),
    QuattSensorEntityDescription(
        name="Heating",
        key="boiler.otTbCH",
        icon="mdi:heating-coil",
        quatt_device_info=DEVICE_BOILER_ID,
    ),
    QuattSensorEntityDescription(
        name="On/off mode",
        key="boiler.oTtbTurnOnOffBoilerOn",
        icon="mdi:water-boiler",
        quatt_device_info=DEVICE_BOILER_ID,
    ),
    # Thermostat
    QuattSensorEntityDescription(
        name="Heating",
        key="thermostat.otFtChEnabled",
        icon="mdi:home-thermometer",
        quatt_device_info=DEVICE_THERMOSTAT_ID,
    ),
    QuattSensorEntityDescription(
        name="Domestic hot water",
        key="thermostat.otFtDhwEnabled",
        icon="mdi:water-thermometer",
        quatt_device_info=DEVICE_THERMOSTAT_ID,
    ),
    QuattSensorEntityDescription(
        name="Cooling",
        key="thermostat.otFtCoolingEnabled",
        icon="mdi:snowflake-thermometer",
        quatt_device_info=DEVICE_THERMOSTAT_ID,
    ),
    # QC
    QuattSensorEntityDescription(
        name="QC pump protection",
        key="qc.stickyPumpProtectionEnabled",
        icon="mdi:shield-refresh-outline",
        quatt_device_info=DEVICE_CIC_ID,
    ),
]

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_devices):
    """Set up the binary_sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    device_sensors = [
        QuattBinarySensor(
            coordinator=coordinator,
            device_name=device["name"],
            device_id=device["id"],
            sensor_key=entity_description.key,
            entity_description=entity_description
        )
        for device in DEVICE_LIST
        for entity_description in BINARY_SENSORS
        if entity_description.quatt_device_info == device["id"]
    ]
    async_add_devices(device_sensors)


class QuattBinarySensor(QuattEntity, BinarySensorEntity):
    """quatt binary_sensor class."""

    def __init__(
        self,
        device_name: str,
        device_id : str,
        sensor_key: str,
        coordinator: QuattDataUpdateCoordinator,
        entity_description: QuattSensorEntityDescription,
    ) -> None:
        """Initialize the binary_sensor class."""
        super().__init__(coordinator, sensor_key)
        self.entity_description = entity_description
        self._device_name = device_name
        self._device_id = device_id
#        self._sensor_type = sensor_type
#        self._attr_name = f"{device_name} {sensor_key}"
        self._attr_unique_id = f"{device_id}_{sensor_key}"


    @property
    def entity_registry_enabled_default(self):
        """Return whether the sensor should be enabled by default."""
        # Only check the duo property when set, enable when duo found
        if self.entity_description.entity_registry_enabled_default and self.entity_description.quatt_duo:
            return self.coordinator.heatpump2Active()

        # For all other sensors
        return self.entity_description.entity_registry_enabled_default


    @property
    def is_on(self) -> bool:
        """Return true if the binary_sensor is on."""
        if not self.entity_description.quatt_duo or self.coordinator.heatpump2Active():
            return self.coordinator.getValue(self.entity_description.key)
        return False
