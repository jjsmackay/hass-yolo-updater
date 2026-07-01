"""Scope and categorisation logic for YOLO Updater (pure functions)."""

from __future__ import annotations

CATEGORY_SYSTEM = "system"
CATEGORY_HACS = "hacs"
CATEGORY_FIRMWARE = "firmware"
CATEGORY_ADDONS = "addons"
CATEGORY_OTHER = "other"

# Categories the user can opt into. System is a hard rail, never opt-in-able.
OPT_IN_CATEGORIES = (CATEGORY_HACS, CATEGORY_FIRMWARE, CATEGORY_ADDONS, CATEGORY_OTHER)

# Human-readable category labels for the pending-update list.
CATEGORY_LABELS = {
    CATEGORY_HACS: "HACS",
    CATEGORY_FIRMWARE: "Firmware",
    CATEGORY_ADDONS: "Apps",
    CATEGORY_OTHER: "Other",
    CATEGORY_SYSTEM: "System",
}

# Canonical entity ids for HA Core/OS/Supervisor updates (the hard safety rail).
SYSTEM_ENTITY_IDS = frozenset(
    {
        "update.home_assistant_core_update",
        "update.home_assistant_operating_system_update",
        "update.home_assistant_supervisor_update",
    }
)


def is_system(entity_id: str) -> bool:
    """Return True for HA Core/OS/Supervisor updates (never installable)."""
    return entity_id in SYSTEM_ENTITY_IDS


def categorise(entity_id: str, platform: str | None, device_class: str | None) -> str:
    """Map an update entity to exactly one category (first match wins)."""
    if is_system(entity_id):
        return CATEGORY_SYSTEM
    if platform == "hacs":
        return CATEGORY_HACS
    if device_class == "firmware":
        return CATEGORY_FIRMWARE
    if platform == "hassio":
        return CATEGORY_ADDONS
    return CATEGORY_OTHER


def in_scope(
    entity_id: str,
    platform: str | None,
    device_class: str | None,
    options: dict,
) -> bool:
    """Return True if YOLO may install this update, given the user's options."""
    category = categorise(entity_id, platform, device_class)
    if category == CATEGORY_SYSTEM:
        return False
    if category not in options.get("categories", []):
        return False
    if entity_id in options.get("exclude_entities", []):
        return False
    if platform is not None and platform in options.get("exclude_integrations", []):
        return False
    return True
