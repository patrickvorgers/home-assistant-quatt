"""Binary sensor platform for quatt."""
from __future__ import annotations

import logging

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.core import HomeAssistant

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
from .entity import QuattBinarySensorEntityDescription, QuattEntity

BINARY_SENSORS = {
    DEVICE_HEATPUMP1_ID: [
        QuattBinarySensorEntityDescription(
            name="Silentmode",
            key="hp1.silentModeStatus",
            translation_key="hp_silentModeStatus",
            icon="mdi:sleep",
        ),
        QuattBinarySensorEntityDescription(
            name="Limited by COP",
            key="hp1.limitedByCop",
            translation_key="hp_silentModeStatus",
            icon="mdi:arrow-collapse-up",
        ),
        QuattBinarySensorEntityDescription(
            name="Defrost",
            key="hp1.computedDefrost",
            translation_key="hp_silentModeStatus",
            icon="mdi:snowflake",
        ),
    ],
    DEVICE_HEATPUMP2_ID: [
        QuattBinarySensorEntityDescription(
            name="Silentmode",
            key="hp2.silentModeStatus",
            translation_key="hp_silentModeStatus",
            icon="mdi:sleep",
        ),
        QuattBinarySensorEntityDescription(
            name="Limited by COP",
            key="hp2.limitedByCop",
            translation_key="hp_silentModeStatus",
            icon="mdi:arrow-collapse-up",
        ),
        QuattBinarySensorEntityDescription(
            name="Defrost",
            key="hp2.computedDefrost",
            icon="mdi:snowflake",
        ),
    ],
    DEVICE_BOILER_ID: [
        QuattBinarySensorEntityDescription(
            name="Boiler",
            key="boiler.otFbChModeActive",
            icon="mdi:heating-coil",
            quatt_opentherm=True,
        ),
        QuattBinarySensorEntityDescription(
            name="Domestic hot water",
            key="boiler.otFbDhwActive",
            icon="mdi:water-boiler",
            quatt_opentherm=True,
        ),
        QuattBinarySensorEntityDescription(
            name="Flame",
            key="boiler.otFbFlameOn",
            icon="mdi:fire",
            quatt_opentherm=True,
        ),
        QuattBinarySensorEntityDescription(
            name="Heating",
            key="boiler.otTbCH",
            icon="mdi:heating-coil",
        ),
        QuattBinarySensorEntityDescription(
            name="On/off mode",
            key="boiler.oTtbTurnOnOffBoilerOn",
            icon="mdi:water-boiler",
        ),
    ],
    DEVICE_THERMOSTAT_ID: [
        QuattBinarySensorEntityDescription(
            name="Heating",
            key="thermostat.otFtChEnabled",
            icon="mdi:home-thermometer",
        ),
        QuattBinarySensorEntityDescription(
            name="Domestic hot water",
            key="thermostat.otFtDhwEnabled",
            icon="mdi:water-thermometer",
        ),
        QuattBinarySensorEntityDescription(
            name="Cooling",
            key="thermostat.otFtCoolingEnabled",
            icon="mdi:snowflake-thermometer",
        ),
    ],
    DEVICE_CIC_ID: [
        QuattBinarySensorEntityDescription(
            name="QC pump protection",
            key="qc.stickyPumpProtectionEnabled",
            icon="mdi:shield-refresh-outline",
        ),
    ],
}

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry, async_add_devices):
    """Set up the binary_sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    device_sensors = []

    for device in DEVICE_LIST:
        device_id = device["id"]
        if device_id not in BINARY_SENSORS:
            continue

        if device_id == DEVICE_HEATPUMP2_ID and not coordinator.heatpump2Active():
            continue

        for entity_description in BINARY_SENSORS[device_id]:
            if entity_description.quatt_opentherm and not coordinator.boilerOpenTherm():
                continue

            device_sensors.append(
                QuattBinarySensor(
                    coordinator=coordinator,
                    device_name=device["name"],
                    device_id=device_id,
                    sensor_key=entity_description.key,
                    entity_description=entity_description,
                )
            )

    async_add_devices(device_sensors)


class QuattBinarySensor(QuattEntity, BinarySensorEntity):
    """quatt binary_sensor class."""

    def __init__(
        self,
        device_name: str,
        device_id : str,
        sensor_key: str,
        coordinator: QuattDataUpdateCoordinator,
        entity_description: QuattBinarySensorEntityDescription,
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
        return self.entity_description.entity_registry_enabled_default


    @property
    def is_on(self) -> bool:
        """Return true if the binary_sensor is on."""
        return self.coordinator.getValue(self.entity_description.key)
