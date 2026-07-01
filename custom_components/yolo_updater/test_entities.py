"""Dummy update entities for testing the Update All integration."""

from __future__ import annotations

import logging

from homeassistant.components.update import (
    UpdateDeviceClass,
    UpdateEntity,
    UpdateEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

_LOGGER = logging.getLogger(__name__)

DUMMY_UPDATES = [
    {
        "id": "dummy_widget_alpha",
        "name": "Dummy Widget Alpha",
        "installed": "1.0.0",
        "latest": "2.0.0",
        "release_url": "https://example.com/widget-alpha/releases/2.0.0",
    },
    {
        "id": "dummy_widget_beta",
        "name": "Dummy Widget Beta",
        "installed": "3.1.0",
        "latest": "3.2.0",
        "device_class": "firmware",
        # no release_url -> renders as plain text
    },
    {
        "id": "dummy_widget_gamma",
        "name": "Dummy Widget Gamma",
        "installed": "0.9.0",
        "latest": "0.9.0",  # No update pending
    },
]


def create_test_entities(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> list[DummyUpdateEntity]:
    """Create dummy update entities for testing."""
    return [DummyUpdateEntity(entry, d) for d in DUMMY_UPDATES]


class DummyUpdateEntity(UpdateEntity):
    """A fake update entity for testing Update All."""

    _attr_supported_features = UpdateEntityFeature.INSTALL
    _attr_should_poll = False

    def __init__(self, entry: ConfigEntry, info: dict) -> None:
        """Initialize the dummy entity."""
        self._attr_unique_id = f"{entry.entry_id}_{info['id']}"
        self._attr_name = info["name"]
        self._attr_installed_version = info["installed"]
        self._attr_latest_version = info["latest"]
        self._attr_release_url = info.get("release_url")
        self._attr_device_class = (
            UpdateDeviceClass.FIRMWARE
            if info.get("device_class") == "firmware"
            else None
        )

    async def async_install(
        self, version: str | None, backup: bool, **kwargs
    ) -> None:
        """Simulate installing an update."""
        _LOGGER.info("TEST: %s 'updated' from %s to %s",
                      self.name, self.installed_version, self.latest_version)
        self._attr_installed_version = self._attr_latest_version
        self.async_write_ha_state()
