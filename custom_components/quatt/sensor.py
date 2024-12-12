"""Sensor platform for quatt."""

from __future__ import annotations

import logging

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import EntityCategory, UnitOfTemperature
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

SENSORS = [
    # Time
    QuattSensorEntityDescription(
        name="Timestamp last update",
        key="time.tsHuman",
        entity_category=EntityCategory.DIAGNOSTIC,
        device_class=SensorDeviceClass.TIMESTAMP,
        entity_registry_enabled_default=False,
        quatt_device_info=DEVICE_CIC_ID,
    ),
    # Heatpump 1
    QuattSensorEntityDescription(
        name="Workingmode",
        key="hp1.getMainWorkingMode",
        icon="mdi:auto-mode",
        quatt_device_info=DEVICE_HEATPUMP1_ID,
    ),
    QuattSensorEntityDescription(
        name="Temperature outside",
        key="hp1.temperatureOutside",
        icon="mdi:thermometer",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        suggested_display_precision=2,
        state_class=SensorStateClass.MEASUREMENT,
        quatt_device_info=DEVICE_HEATPUMP1_ID,
    ),
    QuattSensorEntityDescription(
        name="Temperature water in",
        key="hp1.temperatureWaterIn",
        icon="mdi:thermometer",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        suggested_display_precision=2,
        state_class=SensorStateClass.MEASUREMENT,
        quatt_device_info=DEVICE_HEATPUMP1_ID,
    ),
    QuattSensorEntityDescription(
        name="Temperature water out",
        key="hp1.temperatureWaterOut",
        icon="mdi:thermometer",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        suggested_display_precision=2,
        state_class=SensorStateClass.MEASUREMENT,
        quatt_device_info=DEVICE_HEATPUMP1_ID,
    ),
    QuattSensorEntityDescription(
        name="Water delta",
        key="hp1.computedWaterDelta",
        icon="mdi:thermometer-water",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        suggested_display_precision=2,
        state_class=SensorStateClass.MEASUREMENT,
        quatt_device_info=DEVICE_HEATPUMP1_ID,
    ),
    QuattSensorEntityDescription(
        name="Power input",
        key="hp1.powerInput",
        icon="mdi:lightning-bolt",
        native_unit_of_measurement="W",
        device_class=SensorDeviceClass.POWER,
        suggested_display_precision=0,
        state_class=SensorStateClass.MEASUREMENT,
        quatt_device_info=DEVICE_HEATPUMP1_ID,
    ),
    QuattSensorEntityDescription(
        name="Power",
        key="hp1.power",
        icon="mdi:heat-wave",
        native_unit_of_measurement="W",
        device_class=SensorDeviceClass.POWER,
        suggested_display_precision=0,
        state_class=SensorStateClass.MEASUREMENT,
        quatt_device_info=DEVICE_HEATPUMP1_ID,
    ),
    QuattSensorEntityDescription(
        name="Quatt COP",
        key="hp1.computedQuattCop",
        icon="mdi:heat-pump",
        native_unit_of_measurement="CoP",
        suggested_display_precision=2,
        state_class="measurement",
        quatt_device_info=DEVICE_HEATPUMP1_ID,
    ),
    # Heatpump 2
    QuattSensorEntityDescription(
        name="Workingmode",
        key="hp2.getMainWorkingMode",
        icon="mdi:auto-mode",
        quatt_duo=True,
        quatt_device_info=DEVICE_HEATPUMP2_ID,
    ),
    QuattSensorEntityDescription(
        name="Temperature outside",
        key="hp2.temperatureOutside",
        icon="mdi:thermometer",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        suggested_display_precision=2,
        state_class=SensorStateClass.MEASUREMENT,
        quatt_duo=True,
        quatt_device_info=DEVICE_HEATPUMP2_ID,
    ),
    QuattSensorEntityDescription(
        name="Temperature water in",
        key="hp2.temperatureWaterIn",
        icon="mdi:thermometer",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        suggested_display_precision=2,
        state_class=SensorStateClass.MEASUREMENT,
        quatt_duo=True,
        quatt_device_info=DEVICE_HEATPUMP2_ID,
    ),
    QuattSensorEntityDescription(
        name="Temperature water out",
        key="hp2.temperatureWaterOut",
        icon="mdi:thermometer",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        suggested_display_precision=2,
        state_class=SensorStateClass.MEASUREMENT,
        quatt_duo=True,
        quatt_device_info=DEVICE_HEATPUMP2_ID,
    ),
    QuattSensorEntityDescription(
        name="Water delta",
        key="hp2.computedWaterDelta",
        icon="mdi:thermometer-water",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        suggested_display_precision=2,
        state_class=SensorStateClass.MEASUREMENT,
        quatt_duo=True,
        quatt_device_info=DEVICE_HEATPUMP2_ID,
    ),
    QuattSensorEntityDescription(
        name="Power input",
        key="hp2.powerInput",
        icon="mdi:lightning-bolt",
        native_unit_of_measurement="W",
        device_class=SensorDeviceClass.POWER,
        suggested_display_precision=0,
        state_class=SensorStateClass.MEASUREMENT,
        quatt_duo=True,
        quatt_device_info=DEVICE_HEATPUMP2_ID,
    ),
    QuattSensorEntityDescription(
        name="Power",
        key="hp2.power",
        icon="mdi:heat-wave",
        native_unit_of_measurement="W",
        device_class=SensorDeviceClass.POWER,
        suggested_display_precision=0,
        state_class=SensorStateClass.MEASUREMENT,
        quatt_duo=True,
        quatt_device_info=DEVICE_HEATPUMP2_ID,
    ),
    QuattSensorEntityDescription(
        name="Quatt COP",
        key="hp2.computedQuattCop",
        icon="mdi:heat-pump",
        native_unit_of_measurement="CoP",
        suggested_display_precision=2,
        state_class=SensorStateClass.MEASUREMENT,
        quatt_duo=True,
        quatt_device_info=DEVICE_HEATPUMP2_ID,
    ),
    # Combined
    QuattSensorEntityDescription(
        name="Heat power",
        key="computedHeatPower",
        icon="mdi:heat-wave",
        native_unit_of_measurement="W",
        device_class=SensorDeviceClass.POWER,
        suggested_display_precision=0,
        state_class=SensorStateClass.MEASUREMENT,
        quatt_device_info=DEVICE_CIC_ID,
    ),
    QuattSensorEntityDescription(
        name="COP",
        key="computedCop",
        icon="mdi:heat-pump",
        native_unit_of_measurement="CoP",
        suggested_display_precision=2,
        state_class=SensorStateClass.MEASUREMENT,
        quatt_device_info=DEVICE_CIC_ID,
    ),
    QuattSensorEntityDescription(
        name="Total power input",
        key="computedPowerInput",
        icon="mdi:lightning-bolt",
        native_unit_of_measurement="W",
        device_class=SensorDeviceClass.POWER,
        suggested_display_precision=0,
        state_class=SensorStateClass.MEASUREMENT,
        quatt_duo=True,
        quatt_device_info=DEVICE_CIC_ID,
    ),
    QuattSensorEntityDescription(
        name="Total power",
        key="computedPower",
        icon="mdi:heat-wave",
        native_unit_of_measurement="W",
        device_class=SensorDeviceClass.POWER,
        suggested_display_precision=0,
        state_class=SensorStateClass.MEASUREMENT,
        quatt_duo=True,
        quatt_device_info=DEVICE_CIC_ID,
    ),
    QuattSensorEntityDescription(
        name="Total system power",
        key="computedSystemPower",
        icon="mdi:heat-wave",
        native_unit_of_measurement="W",
        device_class=SensorDeviceClass.POWER,
        suggested_display_precision=0,
        state_class=SensorStateClass.MEASUREMENT,
        quatt_device_info=DEVICE_CIC_ID,
    ),
    QuattSensorEntityDescription(
        name="Total water delta",
        key="computedWaterDelta",
        icon="mdi:thermometer-water",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        suggested_display_precision=2,
        state_class=SensorStateClass.MEASUREMENT,
        quatt_duo=True,
        quatt_device_info=DEVICE_CIC_ID,
    ),
    QuattSensorEntityDescription(
        name="Total Quatt COP",
        key="computedQuattCop",
        icon="mdi:heat-pump",
        native_unit_of_measurement="CoP",
        suggested_display_precision=2,
        state_class=SensorStateClass.MEASUREMENT,
        quatt_duo=True,
        quatt_device_info=DEVICE_CIC_ID,
    ),
    # Boiler
    QuattSensorEntityDescription(
        name="Temperature water inlet",
        key="boiler.otFbSupplyInletTemperature",
        icon="mdi:thermometer",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        suggested_display_precision=2,
        state_class=SensorStateClass.MEASUREMENT,
        quatt_device_info=DEVICE_BOILER_ID,
    ),
    QuattSensorEntityDescription(
        name="Temperature water outlet",
        key="boiler.otFbSupplyOutletTemperature",
        icon="mdi:thermometer",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        suggested_display_precision=2,
        state_class=SensorStateClass.MEASUREMENT,
        quatt_device_info=DEVICE_BOILER_ID,
    ),
    QuattSensorEntityDescription(
        name="Boiler heat power",
        key="boiler.computedBoilerHeatPower",
        icon="mdi:heat-wave",
        native_unit_of_measurement="W",
        device_class=SensorDeviceClass.POWER,
        suggested_display_precision=0,
        state_class=SensorStateClass.MEASUREMENT,
        quatt_device_info=DEVICE_CIC_ID,
    ),
    # Flowmeter
    QuattSensorEntityDescription(
        name="Temperature",
        key="flowMeter.waterSupplyTemperature",
        icon="mdi:thermometer",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        suggested_display_precision=2,
        state_class=SensorStateClass.MEASUREMENT,
        quatt_device_info=DEVICE_FLOWMETER_ID,
    ),
    QuattSensorEntityDescription(
        name="Flowrate",
        key="qc.flowRateFiltered",
        icon="mdi:gauge",
        native_unit_of_measurement="L/h",
        suggested_display_precision=0,
        state_class=SensorStateClass.MEASUREMENT,
        quatt_device_info=DEVICE_FLOWMETER_ID,
    ),
    # Thermostat
    QuattSensorEntityDescription(
        name="Control setpoint",
        key="thermostat.otFtControlSetpoint",
        icon="mdi:thermometer",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        suggested_display_precision=2,
        state_class=SensorStateClass.MEASUREMENT,
        quatt_device_info=DEVICE_THERMOSTAT_ID,
    ),
    QuattSensorEntityDescription(
        name="Room setpoint",
        key="thermostat.otFtRoomSetpoint",
        icon="mdi:thermometer",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        suggested_display_precision=1,
        state_class=SensorStateClass.MEASUREMENT,
        quatt_device_info=DEVICE_THERMOSTAT_ID,
    ),
    QuattSensorEntityDescription(
        name="Room temperature",
        key="thermostat.otFtRoomTemperature",
        icon="mdi:thermometer",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        suggested_display_precision=2,
        state_class=SensorStateClass.MEASUREMENT,
        quatt_device_info=DEVICE_THERMOSTAT_ID,
    ),
    # QC
    QuattSensorEntityDescription(
        name="QC supervisory control mode code",
        key="qc.supervisoryControlMode",
        quatt_device_info=DEVICE_CIC_ID,
    ),
    QuattSensorEntityDescription(
        name="QC supervisory control mode",
        key="qc.computedSupervisoryControlMode",
        quatt_device_info=DEVICE_CIC_ID,
    ),
    # System
    QuattSensorEntityDescription(
        name="System hostname",
        key="system.hostName",
        entity_category=EntityCategory.DIAGNOSTIC,
        quatt_device_info=DEVICE_CIC_ID,
    ),
]

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_devices):
    """Set up the sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    _LOGGER.debug("Heatpump 1 active: %s", coordinator.heatpump1Active())
    _LOGGER.debug("Heatpump 2 active: %s", coordinator.heatpump2Active())
    _LOGGER.debug("boiler OpenTherm: %s", coordinator.boilerOpenTherm())


    device_sensors = [
        QuattSensor(
            coordinator=coordinator,
            device_name=device["name"],
            device_id=device["id"],
            sensor_key=entity_description.key,
            entity_description=entity_description,
        )
        for device in DEVICE_LIST
        for entity_description in SENSORS
        if entity_description.quatt_device_info == device["id"]
    ]
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
        value = self.entity_description.entity_registry_enabled_default

        # Only check the duo property when set, enable when duo found
        if value and self.entity_description.quatt_duo:
            value = self.coordinator.heatpump2Active()

        # Only check the openthern when set, enable when opentherm found
        if value and self.entity_description.quatt_opentherm:
            value = self.coordinator.boilerOpenTherm()

        return value

    @property
    def native_value(self) -> str:
        """Return the native value of the sensor."""
        value = (
            self.coordinator.getValue(self.entity_description.key)
            if not self.entity_description.quatt_duo
            or self.coordinator.heatpump2Active()
            else None
        )

        if not value:
            return value

        if self.entity_description.device_class == SensorDeviceClass.TIMESTAMP:
            value = dt_util.parse_datetime(value)

        return value
