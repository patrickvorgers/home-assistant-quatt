"""Persist observed compressor starts independently of sensor entities."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime
import math
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.storage import Store

from .const import DOMAIN

COMPRESSOR_ON_HZ = 1.0
STORAGE_VERSION = 1


@dataclass
class CompressorStartState:
    """The count and last known state of one compressor."""

    count: int = 0
    running: bool | None = None
    tracking_since: str | None = None

    def update(self, frequency: Any, now: datetime) -> bool:
        """Count an observed start, ignoring missing or invalid measurements."""
        if isinstance(frequency, bool) or not isinstance(frequency, (int, float, str)):
            return False
        try:
            value = float(frequency)
        except (ValueError, OverflowError):
            return False
        if not math.isfinite(value) or value < 0:
            return False

        running = value >= COMPRESSOR_ON_HZ
        if running == self.running:
            return False
        if self.tracking_since is None:
            self.tracking_since = now.isoformat()
        if running:
            self.count += 1
        self.running = running
        return True


class CompressorStartCounter:
    """Keep independent HP1/HP2 counts in versioned, per-entry storage."""

    def __init__(self, hass: HomeAssistant, entry_id: str) -> None:
        """Initialize storage without performing I/O."""
        self._store = Store(
            hass,
            STORAGE_VERSION,
            f"{DOMAIN}.compressor_starts.{entry_id}",
            atomic_writes=True,
        )
        self.states = [CompressorStartState(), CompressorStartState()]
        self._loaded = False

    async def async_load(self) -> None:
        """Restore both counters before processing the first API response."""
        if self._loaded:
            return
        stored = await self._store.async_load()
        if stored is not None:
            self.states = [
                CompressorStartState(**stored[key]) for key in ("hp1", "hp2")
            ]
        self._loaded = True

    async def async_update(self, data: Any, now: datetime) -> None:
        """Process existing API measurements and save only state transitions."""
        await self.async_load()
        if not isinstance(data, dict):
            return
        result = data.get("result", data)
        if not isinstance(result, dict):
            return
        heatpumps = result.get("heatPumps")
        if not isinstance(heatpumps, list):
            return

        changed = False
        for index, pump in enumerate(heatpumps[:2]):
            if isinstance(pump, dict):
                changed |= self.states[index].update(
                    pump.get("compressorFrequency"), now
                )
        if changed:
            # Persist stops too, so the next start is recognized after a reload.
            await self._store.async_save(
                {"hp1": asdict(self.states[0]), "hp2": asdict(self.states[1])}
            )

    async def async_remove(self) -> None:
        """Remove counters only when the config entry is deleted."""
        await self._store.async_remove()
