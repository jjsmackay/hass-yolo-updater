"""Tests for scope.py. Run with: python3 tests/test_scope.py (no pytest needed)."""
import os
import sys

sys.path.insert(
    0, os.path.join(os.path.dirname(__file__), "..", "custom_components", "yolo_updater")
)
import scope  # noqa: E402


def test_categorise_system():
    for eid in (
        "update.home_assistant_core_update",
        "update.home_assistant_operating_system_update",
        "update.home_assistant_supervisor_update",
    ):
        assert scope.categorise(eid, "hassio", None) == scope.CATEGORY_SYSTEM


def test_categorise_hacs():
    assert scope.categorise("update.some_card_update", "hacs", None) == scope.CATEGORY_HACS


def test_categorise_firmware():
    assert (
        scope.categorise("update.hallway_firmware", "zwave_js", "firmware")
        == scope.CATEGORY_FIRMWARE
    )


def test_categorise_addons():
    assert scope.categorise("update.mosquitto_update", "hassio", None) == scope.CATEGORY_ADDONS


def test_categorise_other():
    assert scope.categorise("update.frigate_server", "frigate", None) == scope.CATEGORY_OTHER


def test_firmware_precedes_addons():
    assert (
        scope.categorise("update.some_addon", "hassio", "firmware") == scope.CATEGORY_FIRMWARE
    )


def test_in_scope_requires_category_opt_in():
    empty = {"categories": [], "exclude_entities": [], "exclude_integrations": []}
    assert scope.in_scope("update.some_card_update", "hacs", None, empty) is False
    opted = {"categories": ["hacs"], "exclude_entities": [], "exclude_integrations": []}
    assert scope.in_scope("update.some_card_update", "hacs", None, opted) is True


def test_in_scope_system_never():
    allcats = {
        "categories": ["hacs", "firmware", "addons", "other"],
        "exclude_entities": [],
        "exclude_integrations": [],
    }
    assert scope.in_scope("update.home_assistant_core_update", "hassio", None, allcats) is False


def test_in_scope_entity_exclude():
    opts = {
        "categories": ["hacs"],
        "exclude_entities": ["update.flaky_card_update"],
        "exclude_integrations": [],
    }
    assert scope.in_scope("update.flaky_card_update", "hacs", None, opts) is False
    assert scope.in_scope("update.good_card_update", "hacs", None, opts) is True


def test_in_scope_integration_exclude():
    opts = {
        "categories": ["firmware"],
        "exclude_entities": [],
        "exclude_integrations": ["zwave_js"],
    }
    assert scope.in_scope("update.hallway_firmware", "zwave_js", "firmware", opts) is False
    assert scope.in_scope("update.plug_firmware", "mqtt", "firmware", opts) is True


def test_in_scope_missing_keys_default_safe():
    assert scope.in_scope("update.x", "hacs", None, {}) is False


def _run_all():
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    for fn in fns:
        fn()
    print(f"all {len(fns)} scope tests passed")


if __name__ == "__main__":
    _run_all()
