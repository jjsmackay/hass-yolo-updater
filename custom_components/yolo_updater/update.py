"""Update platform for YOLO Updater."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.update import UpdateEntity, UpdateEntityFeature
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EVENT_HOMEASSISTANT_STARTED, EVENT_STATE_CHANGED
from homeassistant.core import Event, HomeAssistant, callback
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import scope

_LOGGER = logging.getLogger(__name__)

TEST_MODE = False  # Set True to load dummy update entities for testing


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
    _attr_supported_features = (
        UpdateEntityFeature.INSTALL | UpdateEntityFeature.RELEASE_NOTES
    )
    _attr_should_poll = False

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the entity."""
        self._attr_unique_id = f"{entry.entry_id}_yolo_all"
        self.entity_id = "update.yolo_all"
        self._hass = hass
        self._entry = entry
        self._pending: dict[str, dict[str, str | None]] = {}
        self._unsub: list = []

    async def async_added_to_hass(self) -> None:
        """Register listeners when added to hass."""
        self._refresh_pending()

        self._unsub.append(
            self._hass.bus.async_listen(EVENT_STATE_CHANGED, self._on_state_change)
        )

        if not self._hass.is_running:
            self._unsub.append(
                self._hass.bus.async_listen_once(
                    EVENT_HOMEASSISTANT_STARTED, self._on_ha_started
                )
            )

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
        """Short summary. HA caps this at 255 chars, so keep it to a count."""
        if not self._pending:
            return None
        return f"{len(self._pending)} update(s) pending"

    async def async_release_notes(self) -> str | None:
        """Full pending list, grouped by category (not length-capped)."""
        if not self._pending:
            return None
        groups: dict[str, list[tuple[str, dict]]] = {}
        for entity_id, info in self._pending.items():
            category = info.get("category") or scope.CATEGORY_OTHER
            groups.setdefault(category, []).append((entity_id, info))

        lines = [f"**{len(self._pending)} update(s) pending:**"]
        for category in scope.OPT_IN_CATEGORIES:
            items = groups.get(category)
            if not items:
                continue
            lines.append(f"\n**{scope.CATEGORY_LABELS[category]}**")
            for _entity_id, info in sorted(items):
                name = info.get("friendly_name", _entity_id)
                if name and name.endswith(" Update"):
                    name = name[: -len(" Update")]
                cur = info.get("installed_version") or "?"
                new = info.get("latest_version") or "?"
                url = info.get("release_url")
                new_label = f"[{new}]({url})" if url else new
                lines.append(f"- {name}: {cur} \u2192 {new_label}")
        return "\n".join(lines)

    @property
    def entity_picture(self) -> str:
        """Use the HACS icon."""
        return "https://brands.home-assistant.io/_/hacs/icon.png"

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------

    async def async_install(
        self, version: str | None, backup: bool, **kwargs: Any
    ) -> None:
        """Install all pending updates."""
        registry = er.async_get(self._hass)
        options = self._entry.options
        targets = []
        for entity_id in self._pending:
            state = self._hass.states.get(entity_id)
            device_class = state.attributes.get("device_class") if state else None
            platform = self._platform_of(registry, entity_id)
            if scope.in_scope(entity_id, platform, device_class, options):
                targets.append(entity_id)
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

    @staticmethod
    def _platform_of(registry: er.EntityRegistry, entity_id: str) -> str | None:
        """Return the integration platform that provides an entity, if known."""
        entry = registry.async_get(entity_id)
        return entry.platform if entry else None

    @callback
    def _on_ha_started(self, _event: Event) -> None:
        """Re-scan once HA is fully started."""
        self._refresh_pending()
        self.async_write_ha_state()

    @callback
    def _refresh_pending(self) -> None:
        """Scan all current update entities and build the in-scope pending dict."""
        self._pending.clear()
        registry = er.async_get(self._hass)
        options = self._entry.options
        for state in self._hass.states.async_all("update"):
            if self._is_self(state.entity_id) or state.state != "on":
                continue
            platform = self._platform_of(registry, state.entity_id)
            device_class = state.attributes.get("device_class")
            if not scope.in_scope(state.entity_id, platform, device_class, options):
                continue
            self._pending[state.entity_id] = {
                "friendly_name": state.attributes.get("friendly_name"),
                "installed_version": state.attributes.get("installed_version"),
                "latest_version": state.attributes.get("latest_version"),
                "release_url": state.attributes.get("release_url"),
                "category": scope.categorise(
                    state.entity_id, platform, device_class
                ),
            }

    @callback
    def _on_state_change(self, event: Event) -> None:
        """Handle state change events for update entities."""
        entity_id = event.data.get("entity_id", "")
        if not entity_id.startswith("update.") or self._is_self(entity_id):
            return

        new_state = event.data.get("new_state")
        in_scope = False
        if new_state is not None and new_state.state == "on":
            registry = er.async_get(self._hass)
            platform = self._platform_of(registry, entity_id)
            device_class = new_state.attributes.get("device_class")
            in_scope = scope.in_scope(
                entity_id, platform, device_class, self._entry.options
            )

        if in_scope:
            self._pending[entity_id] = {
                "friendly_name": new_state.attributes.get("friendly_name"),
                "installed_version": new_state.attributes.get("installed_version"),
                "latest_version": new_state.attributes.get("latest_version"),
                "release_url": new_state.attributes.get("release_url"),
                "category": scope.categorise(entity_id, platform, device_class),
            }
        else:
            self._pending.pop(entity_id, None)

        self.async_write_ha_state()
