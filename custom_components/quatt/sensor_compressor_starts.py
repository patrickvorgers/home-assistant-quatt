"""Sensors exposing the coordinator's persisted compressor start counts."""

from __future__ import annotations

from datetime import datetime

import homeassistant.util.dt as dt_util

from .compressor_starts import CompressorStartState
from .const import DEVICE_HEATPUMP_1_ID, DEVICE_HEATPUMP_2_ID
from .coordinator_remote_cic import QuattCicRemoteDataUpdateCoordinator
from .entity import QuattSensor


class QuattCompressorTrackingSensor(QuattSensor):
    """Read the stored tracking state for a heat pump."""

    coordinator: QuattCicRemoteDataUpdateCoordinator

    @property
    def _counter(self) -> CompressorStartState:
        """Return the stored counter belonging to this heat pump device."""
        index = (DEVICE_HEATPUMP_1_ID, DEVICE_HEATPUMP_2_ID).index(self._device_id)
        return self.coordinator.compressor_starts.states[index]


class QuattObservedCompressorStartsSensor(QuattCompressorTrackingSensor):
    """Report observed starts without changing the counter when read."""

    @property
    def native_value(self) -> int | None:
        """Return unknown until this compressor has a valid first measurement."""
        state = self._counter
        return state.count if state.tracking_since is not None else None

    @property
    def extra_state_attributes(self) -> dict[str, str | None]:
        """Expose the original start of tracking across reloads and restores."""
        return {"tracking_since": self._counter.tracking_since}


class QuattCompressorTrackingSinceSensor(QuattCompressorTrackingSensor):
    """Show when observation of this compressor began."""

    @property
    def native_value(self) -> datetime | None:
        """Return the persisted start of tracking as a timezone-aware timestamp."""
        since = self._counter.tracking_since
        return dt_util.parse_datetime(since) if since is not None else None
