"""Sensor platform for quatt."""

from __future__ import annotations

import logging

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import EntityCategory, UnitOfTemperature
from homeassistant.core import HomeAssistant
import homeassistant.util.dt as dt_util

from .const import (
    DEVICE_BOILER_ID,
    DEVICE_CIC_ID,
    DEVICE_FLOWMETER_ID,
    DEVICE_HEATPUMP1_ID,
    DEVICE_HEATPUMP2_ID,
    DEVICE_LIST,
    DEVICE_THERMOSTAT_ID,
    DOMAIN,
)
from .coordinator import QuattDataUpdateCoordinator
from .entity import QuattEntity, QuattSensorEntityDescription


def create_heatpump_sensor_entity_descriptions(prefix: str):
    """Create the heatpump sensor entity descriptions based on the prefix."""
    return [
        QuattSensorEntityDescription(
            name="Workingmode",
            key=f"{prefix}.getMainWorkingMode",
            icon="mdi:auto-mode",
        ),
        QuattSensorEntityDescription(
            name="Temperature outside",
            key=f"{prefix}.temperatureOutside",
            icon="mdi:thermometer",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            device_class=SensorDeviceClass.TEMPERATURE,
            suggested_display_precision=2,
            state_class=SensorStateClass.MEASUREMENT,
        ),
        QuattSensorEntityDescription(
            name="Temperature water in",
            key=f"{prefix}.temperatureWaterIn",
            icon="mdi:thermometer",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            device_class=SensorDeviceClass.TEMPERATURE,
            suggested_display_precision=2,
            state_class=SensorStateClass.MEASUREMENT,
        ),
        QuattSensorEntityDescription(
            name="Temperature water out",
            key=f"{prefix}.temperatureWaterOut",
            icon="mdi:thermometer",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            device_class=SensorDeviceClass.TEMPERATURE,
            suggested_display_precision=2,
            state_class=SensorStateClass.MEASUREMENT,
        ),
        QuattSensorEntityDescription(
            name="Water delta",
            key=f"{prefix}.computedWaterDelta",
            icon="mdi:thermometer-water",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            device_class=SensorDeviceClass.TEMPERATURE,
            suggested_display_precision=2,
            state_class=SensorStateClass.MEASUREMENT,
        ),
        QuattSensorEntityDescription(
            name="Power input",
            key=f"{prefix}.powerInput",
            icon="mdi:lightning-bolt",
            native_unit_of_measurement="W",
            device_class=SensorDeviceClass.POWER,
            suggested_display_precision=0,
            state_class=SensorStateClass.MEASUREMENT,
        ),
        QuattSensorEntityDescription(
            name="Power",
            key=f"{prefix}.power",
            icon="mdi:heat-wave",
            native_unit_of_measurement="W",
            device_class=SensorDeviceClass.POWER,
            suggested_display_precision=0,
            state_class=SensorStateClass.MEASUREMENT,
        ),
        QuattSensorEntityDescription(
            name="Quatt COP",
            key=f"{prefix}.computedQuattCop",
            icon="mdi:heat-pump",
            native_unit_of_measurement="CoP",
            suggested_display_precision=2,
            state_class="measurement",
        ),
    ]

SENSORS = {
    DEVICE_CIC_ID: [
        QuattSensorEntityDescription(
            name="Timestamp last update",
            key="time.tsHuman",
            entity_category=EntityCategory.DIAGNOSTIC,
            device_class=SensorDeviceClass.TIMESTAMP,
            entity_registry_enabled_default=False,
        ),
        QuattSensorEntityDescription(
            name="Heat power",
            key="computedHeatPower",
            icon="mdi:heat-wave",
            native_unit_of_measurement="W",
            device_class=SensorDeviceClass.POWER,
            suggested_display_precision=0,
            state_class=SensorStateClass.MEASUREMENT,
        ),
        QuattSensorEntityDescription(
            name="COP",
            key="computedCop",
            icon="mdi:heat-pump",
            native_unit_of_measurement="CoP",
            suggested_display_precision=2,
            state_class=SensorStateClass.MEASUREMENT,
        ),
        QuattSensorEntityDescription(
            name="Total power input",
            key="computedPowerInput",
            icon="mdi:lightning-bolt",
            native_unit_of_measurement="W",
            device_class=SensorDeviceClass.POWER,
            suggested_display_precision=0,
            state_class=SensorStateClass.MEASUREMENT,
        ),
        QuattSensorEntityDescription(
            name="Total power",
            key="computedPower",
            icon="mdi:heat-wave",
            native_unit_of_measurement="W",
            device_class=SensorDeviceClass.POWER,
            suggested_display_precision=0,
            state_class=SensorStateClass.MEASUREMENT,
        ),
        QuattSensorEntityDescription(
            name="Total system power",
            key="computedSystemPower",
            icon="mdi:heat-wave",
            native_unit_of_measurement="W",
            device_class=SensorDeviceClass.POWER,
            suggested_display_precision=0,
            state_class=SensorStateClass.MEASUREMENT,
        ),
        QuattSensorEntityDescription(
            name="Total water delta",
            key="computedWaterDelta",
            icon="mdi:thermometer-water",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            device_class=SensorDeviceClass.TEMPERATURE,
            suggested_display_precision=2,
            state_class=SensorStateClass.MEASUREMENT,
        ),
        QuattSensorEntityDescription(
            name="Total Quatt COP",
            key="computedQuattCop",
            icon="mdi:heat-pump",
            native_unit_of_measurement="CoP",
            suggested_display_precision=2,
            state_class=SensorStateClass.MEASUREMENT,
        ),
        QuattSensorEntityDescription(
            name="QC supervisory control mode code",
            key="qc.supervisoryControlMode",
        ),
        QuattSensorEntityDescription(
            name="QC supervisory control mode",
            key="qc.computedSupervisoryControlMode",
        ),
        # System
        QuattSensorEntityDescription(
            name="System hostname",
            key="system.hostName",
            entity_category=EntityCategory.DIAGNOSTIC,
        ),
    ],
    DEVICE_HEATPUMP1_ID: create_heatpump_sensor_entity_descriptions("hp1"),
    DEVICE_HEATPUMP2_ID: create_heatpump_sensor_entity_descriptions("hp2"),
    DEVICE_BOILER_ID: [
        QuattSensorEntityDescription(
            name="Temperature water inlet",
            key="boiler.otFbSupplyInletTemperature",
            icon="mdi:thermometer",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            device_class=SensorDeviceClass.TEMPERATURE,
            suggested_display_precision=2,
            state_class=SensorStateClass.MEASUREMENT,
            quatt_opentherm=True,
        ),
        QuattSensorEntityDescription(
            name="Temperature water outlet",
            key="boiler.otFbSupplyOutletTemperature",
            icon="mdi:thermometer",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            device_class=SensorDeviceClass.TEMPERATURE,
            suggested_display_precision=2,
            state_class=SensorStateClass.MEASUREMENT,
            quatt_opentherm=True,
        ),
        QuattSensorEntityDescription(
            name="Heat power",
            key="boiler.computedBoilerHeatPower",
            icon="mdi:heat-wave",
            native_unit_of_measurement="W",
            device_class=SensorDeviceClass.POWER,
            suggested_display_precision=0,
            state_class=SensorStateClass.MEASUREMENT,
        ),
    ],
    DEVICE_FLOWMETER_ID: [
        QuattSensorEntityDescription(
            name="Temperature",
            key="flowMeter.waterSupplyTemperature",
            icon="mdi:thermometer",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            device_class=SensorDeviceClass.TEMPERATURE,
            suggested_display_precision=2,
            state_class=SensorStateClass.MEASUREMENT,
        ),
        QuattSensorEntityDescription(
            name="Flowrate",
            key="qc.flowRateFiltered",
            icon="mdi:gauge",
            native_unit_of_measurement="L/h",
            suggested_display_precision=0,
            state_class=SensorStateClass.MEASUREMENT,
        ),
    ],
    DEVICE_THERMOSTAT_ID: [
        QuattSensorEntityDescription(
            name="Control setpoint",
            key="thermostat.otFtControlSetpoint",
            icon="mdi:thermometer",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            device_class=SensorDeviceClass.TEMPERATURE,
            suggested_display_precision=2,
            state_class=SensorStateClass.MEASUREMENT,
        ),
        QuattSensorEntityDescription(
            name="Room setpoint",
            key="thermostat.otFtRoomSetpoint",
            icon="mdi:thermometer",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            device_class=SensorDeviceClass.TEMPERATURE,
            suggested_display_precision=1,
            state_class=SensorStateClass.MEASUREMENT,
        ),
        QuattSensorEntityDescription(
            name="Room temperature",
            key="thermostat.otFtRoomTemperature",
            icon="mdi:thermometer",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            device_class=SensorDeviceClass.TEMPERATURE,
            suggested_display_precision=2,
            state_class=SensorStateClass.MEASUREMENT,
        ),
    ],
}

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry, async_add_devices):
    """Set up the sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    device_sensors = []

    for device in DEVICE_LIST:
        device_id = device["id"]
        if device_id not in SENSORS:
            continue

        if device_id == DEVICE_HEATPUMP2_ID and not coordinator.heatpump2Active():
            continue

        for entity_description in SENSORS[device_id]:
            if entity_description.quatt_opentherm and not coordinator.boilerOpenTherm():
                continue

            device_sensors.append(
                QuattSensor(
                    coordinator=coordinator,
                    device_name=device["name"],
                    device_id=device_id,
                    sensor_key=entity_description.key,
                    entity_description=entity_description,
                )
            )

    async_add_devices(device_sensors)


class QuattSensor(QuattEntity, SensorEntity):
    """quatt Sensor class."""

    def __init__(
        self,
        device_name: str,
        device_id: str,
        sensor_key: str,
        coordinator: QuattDataUpdateCoordinator,
        entity_description: QuattSensorEntityDescription,
    ) -> None:
        """Initialize the sensor class."""
        super().__init__(coordinator, sensor_key)
        self.entity_description = entity_description
        self._device_name = device_name
        self._device_id = device_id
        #        self._sensor_type = sensor_type
        #self._attr_name = f"{device_name} {sensor_key}"
        self._attr_unique_id = f"{device_id}_{sensor_key}"

    @property
    def entity_registry_enabled_default(self):
        """Return whether the sensor should be enabled by default."""
        return self.entity_description.entity_registry_enabled_default

    @property
    def native_value(self) -> str:
        """Return the native value of the sensor."""
        value = self.coordinator.getValue(self.entity_description.key)

        if not value:
            return value

        if self.entity_description.device_class == SensorDeviceClass.TIMESTAMP:
            value = dt_util.parse_datetime(value)

        return value
