"""Update platform for YOLO Updater."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.update import UpdateEntity, UpdateEntityFeature
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EVENT_HOMEASSISTANT_STARTED, EVENT_STATE_CHANGED
from homeassistant.core import Event, HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

_LOGGER = logging.getLogger(__name__)

TEST_MODE = True  # Set True to load dummy update entities for testing


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Update All entity."""
    entities: list[UpdateEntity] = [UpdateAllEntity(hass, entry)]
    if TEST_MODE:
        from .test_entities import create_test_entities

        entities.extend(create_test_entities(hass, entry))
    async_add_entities(entities)


class UpdateAllEntity(UpdateEntity):
    """Aggregate update entity that tracks all pending updates."""

    _attr_has_entity_name = False
    _attr_name = "! YOLO Update All"
    _attr_supported_features = UpdateEntityFeature.INSTALL
    _attr_should_poll = False

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the entity."""
        self._attr_unique_id = f"{entry.entry_id}_yolo_all"
        self.entity_id = "update.yolo_all"
        self._hass = hass
        self._pending: dict[str, dict[str, str | None]] = {}
        self._unsub: list = []

    async def async_added_to_hass(self) -> None:
        """Register listeners when added to hass."""
        self._refresh_pending()

        self._unsub.append(self._hass.bus.async_listen(EVENT_STATE_CHANGED, self._on_state_change))

        if not self._hass.is_running:
            self._unsub.append(self._hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STARTED, self._on_ha_started))

    async def async_will_remove_from_hass(self) -> None:
        """Clean up listeners."""
        for unsub in self._unsub:
            unsub()
        self._unsub.clear()

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def installed_version(self) -> str | None:
        """Return a synthetic installed version."""
        if self._pending:
            return "pending"
        return "latest"

    @property
    def latest_version(self) -> str | None:
        """Return a synthetic latest version."""
        return "latest"

    @property
    def release_summary(self) -> str | None:
        """List pending updates."""
        if not self._pending:
            return None
        lines = [f"**{len(self._pending)} update(s) pending:**\n"]
        for entity_id, info in sorted(self._pending.items()):
            name = info.get("friendly_name", entity_id)
            cur = info.get("installed_version") or "?"
            new = info.get("latest_version") or "?"
            lines.append(f"- {name}: {cur} \u2192 {new}")
        return "\n".join(lines)

    @property
    def entity_picture(self) -> str:
        """Use the HACS icon."""
        return "https://brands.home-assistant.io/_/hacs/icon.png"

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------

    async def async_install(self, version: str | None, backup: bool, **kwargs: Any) -> None:
        """Install all pending updates."""
        targets = list(self._pending.keys())
        if not targets:
            _LOGGER.info("No pending updates to install")
            return

        _LOGGER.info("Installing %d pending update(s): %s", len(targets), targets)
        for entity_id in targets:
            await self._hass.services.async_call(
                "update",
                "install",
                {"entity_id": entity_id},
                blocking=True,
            )

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _is_self(self, entity_id: str) -> bool:
        """Check if an entity is this entity (avoid self-tracking)."""
        return entity_id == self.entity_id

    @callback
    def _on_ha_started(self, _event: Event) -> None:
        """Re-scan once HA is fully started."""
        self._refresh_pending()
        self.async_write_ha_state()

    @callback
    def _refresh_pending(self) -> None:
        """Scan all current update entities and build pending dict."""
        self._pending.clear()
        for state in self._hass.states.async_all("update"):
            if self._is_self(state.entity_id):
                continue
            if state.state == "on":
                self._pending[state.entity_id] = {
                    "friendly_name": state.attributes.get("friendly_name"),
                    "installed_version": state.attributes.get("installed_version"),
                    "latest_version": state.attributes.get("latest_version"),
                }

    @callback
    def _on_state_change(self, event: Event) -> None:
        """Handle state change events for update entities."""
        entity_id = event.data.get("entity_id", "")
        if not entity_id.startswith("update.") or self._is_self(entity_id):
            return

        new_state = event.data.get("new_state")
        if new_state is None:
            self._pending.pop(entity_id, None)
        elif new_state.state == "on":
            self._pending[entity_id] = {
                "friendly_name": new_state.attributes.get("friendly_name"),
                "installed_version": new_state.attributes.get("installed_version"),
                "latest_version": new_state.attributes.get("latest_version"),
            }
        else:
            self._pending.pop(entity_id, None)

        self.async_write_ha_state()
