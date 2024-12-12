"""DataUpdateCoordinator for quatt."""

from __future__ import annotations

from datetime import timedelta
import math

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import STATE_UNAVAILABLE, STATE_UNKNOWN
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import QuattApiClient, QuattApiClientAuthenticationError, QuattApiClientError
from .const import CONF_POWER_SENSOR, CONVERSION_FACTORS, DOMAIN, LOGGER


# https://developers.home-assistant.io/docs/integration_fetching_data#coordinated-single-api-poll-for-data-for-all-entities
class QuattDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    config_entry: ConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        update_interval: int,
        client: QuattApiClient,
    ) -> None:
        """Initialize."""
        self.client = client
        super().__init__(
            hass=hass,
            logger=LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=update_interval),
        )

        self._power_sensor_id: str = (
            self.config_entry.options.get(CONF_POWER_SENSOR, "")
            if (self.config_entry is not None)
            and (len(self.config_entry.options.get(CONF_POWER_SENSOR, "")) > 6)
            else None
        )

    async def _async_update_data(self):
        """Update data via library."""
        try:
            return await self.client.async_get_data()
        except QuattApiClientAuthenticationError as exception:
            raise ConfigEntryAuthFailed(exception) from exception
        except QuattApiClientError as exception:
            raise UpdateFailed(exception) from exception

    def heatpump1Active(self):
        """Check if heatpump 1 is active."""
        LOGGER.debug(self.getValue("hp1"))
        return self.getValue("hp1") is not None

    def heatpump2Active(self):
        """Check if heatpump 2 is active."""
        LOGGER.debug(self.getValue("hp2"))
        return self.getValue("hp2") is not None

    def boilerOpenTherm(self):
        """Check if boiler is connected to CIC ofer OpenTherm."""
        LOGGER.debug(self.getValue("boiler.otFbChModeActive"))
        return self.getValue("boiler.otFbChModeActive") is not None

    def getConversionFactor(self, temperature: float):
        """Get the conversion factor for the nearest temperature."""
        nearestTemperature = min(
            CONVERSION_FACTORS.keys(), key=lambda t: abs(t - temperature)
        )
        return CONVERSION_FACTORS[nearestTemperature]

    def electricalPower(self):
        """Get heatpump power from sensor."""
        if self._power_sensor_id is None:
            return None
        LOGGER.debug("electricalPower %s", self.hass.states.get(self._power_sensor_id))
        if self.hass.states.get(self._power_sensor_id) is None:
            return None
        if self.hass.states.get(self._power_sensor_id).state not in [
            STATE_UNAVAILABLE,
            STATE_UNKNOWN,
        ]:
            return self.hass.states.get(self._power_sensor_id).state
        return None

    def computedWaterDelta(self, parent_key: str | None = None):
        """Compute waterDelta."""
        if parent_key is None:
            parent_key = ""
            heatpump_prefix = "hp2" if self.heatpump2Active() else "hp1"
            temperature_water_out = self.getValue(f"{heatpump_prefix}.temperatureWaterOut")
            temperature_water_in = self.getValue("hp1.temperatureWaterIn")
        else:
            temperature_water_out = self.getValue(f"{parent_key}.temperatureWaterOut")
            temperature_water_in = self.getValue(f"{parent_key}.temperatureWaterIn")

        LOGGER.debug(
            "%s.computedWaterDelta.temperatureWaterOut %s",
            parent_key,
            temperature_water_out,
        )
        LOGGER.debug(
            "%s.computedWaterDelta.temperatureWaterIn %s",
            parent_key,
            temperature_water_in,
        )

        if temperature_water_out is None or temperature_water_in is None:
            return None

        return round(temperature_water_out - temperature_water_in, 2)

    def computedHeatPower(self, parent_key: str | None = None):
        """Compute heatPower."""

        # Retrieve the supervisory control mode state first
        state = self.getValue("qc.supervisoryControlMode")
        LOGGER.debug("computedBoilerHeatPower.supervisoryControlMode: %s", state)

        # If the state is not valid or the heatpump is not active, no need to proceed
        if state is None:
            return None
        if state not in [2, 3]:
            return 0.0

        computed_water_delta = self.computedWaterDelta(None)
        heatpump_prefix = "hp2" if self.heatpump2Active() else "hp1"
        temperature_water_out = self.getValue(f"{heatpump_prefix}.temperatureWaterOut")
        flowrate = self.getValue("qc.flowRateFiltered")

        LOGGER.debug("computedHeatPower.computedWaterDelta %s", computed_water_delta)
        LOGGER.debug("computedHeatPower.flowRate %s", flowrate)
        LOGGER.debug("computedHeatPower.temperatureWaterOut %s", temperature_water_out)

        if (
            computed_water_delta is None
            or flowrate is None
            or temperature_water_out is None
        ):
            return None

        value = round(
            computed_water_delta
            * flowrate
            * self.getConversionFactor(temperature_water_out),
            2,
        )

        # Prevent any negative numbers
        return max(value, 0.00)

    def computedBoilerHeatPower(self, parent_key: str | None = None) -> float | None:
        """Compute the boiler's added heat power."""

        # Retrieve the supervisory control mode state first
        state = self.getValue("qc.supervisoryControlMode")
        LOGGER.debug("computedBoilerHeatPower.supervisoryControlMode: %s", state)

        # If the state is not valid or the boiler is not active, no need to proceed
        if state is None:
            return None
        if state not in [3, 4]:
            return 0.0

        # Retrieve other required values
        heatpump_water_out = (
            self.getValue("hp2.temperatureWaterOut")
            if self.heatpump2Active()
            else self.getValue("hp1.temperatureWaterOut")
        )
        flowrate = self.getValue("qc.flowRateFiltered")
        flow_water_temperature = self.getValue("flowMeter.waterSupplyTemperature")

        # Log debug information
        LOGGER.debug(
            "computedBoilerHeatPower.temperatureWaterOut: %s", heatpump_water_out
        )
        LOGGER.debug("computedBoilerHeatPower.flowRate: %s", flowrate)
        LOGGER.debug(
            "computedBoilerHeatPower.waterSupplyTemperature: %s", flow_water_temperature
        )

        # Validate other inputs
        if heatpump_water_out is None or flowrate is None or flow_water_temperature is None:
            return None

        # Compute the heat power using the conversion factor
        conversion_factor = self.getConversionFactor(flow_water_temperature)
        value = round(
            (flow_water_temperature - heatpump_water_out) * flowrate * conversion_factor, 2
        )

        # Prevent any negative numbers
        return max(value, 0.00)

    def computedSystemPower(self, parent_key: str | None = None):
        """Compute total system power."""
        boiler_power = self.computedBoilerHeatPower(parent_key)
        heatpump_power = self.computedPower(parent_key)

        # Log debug information
        LOGGER.debug("computedSystemPower.boilerPower: %s", boiler_power)
        LOGGER.debug("computedSystemPower.heatpumpPower: %s", heatpump_power)

        # Validate inputs
        if boiler_power is None or heatpump_power is None:
            return None

        return float(boiler_power) + float(heatpump_power)

    def computedPowerInput(self, parent_key: str | None = None):
        """Compute total powerInput."""
        power_input_hp1 = float(self.getValue("hp1.powerInput", 0))
        power_input_hp2 = (
            float(self.getValue("hp2.powerInput", 0)) if self.heatpump2Active() else 0
        )
        return power_input_hp1 + power_input_hp2

    def computedPower(self, parent_key: str | None = None):
        """Compute total power."""
        power_hp1 = float(self.getValue("hp1.power", 0))
        power_hp2 = float(self.getValue("hp2.power", 0)) if self.heatpump2Active() else 0
        return power_hp1 + power_hp2

    def computedCop(self, parent_key: str | None = None):
        """Compute COP."""
        electrical_power = self.electricalPower()
        computed_heat_power = self.computedHeatPower(parent_key)

        LOGGER.debug("computedCop.electricalPower %s", electrical_power)
        LOGGER.debug("computedCop.computedHeatPower %s", computed_heat_power)

        if electrical_power is None or computed_heat_power is None:
            return None

        computed_heat_power = float(computed_heat_power)
        electrical_power = float(electrical_power)
        if electrical_power == 0:
            return None

        return round(computed_heat_power / electrical_power, 2)

    def computedQuattCop(self, parent_key: str | None = None):
        """Compute Quatt COP."""
        if parent_key is None:
            power_input = self.computedPowerInput(parent_key)
            power_output = self.computedPower(parent_key)
        else:
            power_input = self.getValue(parent_key + ".powerInput")
            power_output = self.getValue(parent_key + ".power")

        LOGGER.debug("%s.computedQuattCop.powerInput %s", parent_key, power_input)
        LOGGER.debug("%s.computedQuattCop.powerOutput %s", parent_key, power_output)

        if power_input is None or power_output is None:
            return None

        power_output = float(power_output)
        power_input = float(power_input)
        if power_input == 0:
            return None

        value = round(power_output / power_input, 2)

        # Prevent negative sign for 0 values (like: -0.0)
        return math.copysign(0.0, 1) if value == 0 else value

    def computedDefrost(self, parent_key: str | None = None):
        """Compute Quatt Defrost State."""
        if parent_key is None:
            return None

        # Get the needed information to determine the defrost case
        state = self.getValue("qc.supervisoryControlMode")
        power_output = self.getValue(f"{parent_key}.power")
        water_delta = self.computedWaterDelta(parent_key)

        LOGGER.debug("%s.computedDefrost.supervisoryControlMode %s", parent_key, state)
        LOGGER.debug("%s.computedDefrost.powerOutput %s", parent_key, power_output)
        LOGGER.debug(
            "%s.computedDefrost.computedWaterDelta %s", parent_key, water_delta
        )

        if state is None or power_output is None or water_delta is None:
            return None

        state = int(state)
        power_output = float(power_output)
        water_delta = float(water_delta)

        # State equals to "Heating - heatpump" only or "heatpump + boiler"
        return state in [2, 3] and power_output == 0 and water_delta < -1

    def computedSupervisoryControlMode(self, parent_key: str | None = None):
        """Map the numeric supervisoryControlMode to a textual status."""
        state = self.getValue("qc.supervisoryControlMode")
        mapping = {
            0: "Standby",
            1: "Standby - heating",
            2: "Heating - heatpump only",
            3: "Heating - heatpump + boiler",
            4: "Heating - boiler only",
            96: "Anti-freeze protection - boiler on",
            97: "Anti-freeze protection - boiler pre-pump",
            98: "Anti-freeze protection - water circulation",
            99: "Fault - circulation pump on",
        }

        if state in mapping:
            return mapping[state]
        if state >= 100:
            return "Commissioning modes"
        return None

    def getValue(self, value_path: str, default: float | None = None):
        """Check retrieve a value by dot notation."""
        keys = value_path.split(".")
        value = self.data
        parent_key = None
        for key in keys:
            if value is None:
                return default

            if key.isdigit():
                key = int(key)
                if not isinstance(value, list) or len(value) < key:
                    LOGGER.warning(
                        "Could not find %d of %s",
                        key,
                        value_path,
                    )
                    LOGGER.debug(" in %s %s", value, type(value))
                    return default

            elif len(key) > 8 and key[0:8] == "computed" and key in dir(self):
                method = getattr(self, key)
                return method(parent_key)
            elif key not in value:
                # Ignore any warnings about hp2 - for single quatt installations it is valid that hp2 does not exist.
                if key != "hp2":
                    LOGGER.warning("Could not find %s of %s", key, value_path)
                    LOGGER.debug("in %s", value)
                return default
            value = value[key]
            parent_key = key

        return value
