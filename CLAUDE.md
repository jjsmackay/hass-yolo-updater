# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A Home Assistant custom integration that exposes a single `update.yolo_all` entity (`! YOLO Update All`) which aggregates all pending HA update entities. Pressing "Update" calls `update.install` on each pending entity sequentially.

## Architecture

- `__init__.py` — entry setup/unload, declares `DOMAIN = "yolo_updater"`
- `config_flow.py` — single-instance config flow, no options
- `update.py` — core logic: `UpdateAllEntity` subscribes to `EVENT_STATE_CHANGED` on the HA event bus, filters to `update.*` entities (excluding itself), and rescans on `EVENT_HOMEASSISTANT_STARTED` to catch integrations that load late
- `scripts/dev_entities.py` — dev-only tool (not shipped) that injects dummy `update.*` entities into a running HA via the REST API, so `update.yolo_all` aggregates them like real updates

The shipped integration under `custom_components/yolo_updater/` contains no test or dev code — dummy entities are spawned externally (see Testing locally).

## Key design decisions

- Uses `hass.bus.async_listen(EVENT_STATE_CHANGED, ...)` rather than `async_track_state_change_event` — the latter doesn't accept `None` for all-entity tracking
- `entity_id` is hardcoded to `update.yolo_all` via `self.entity_id` in `__init__`
- `installed_version` returns `"pending"` when updates exist and `"latest"` when none — this drives the `on`/`off` state

## Testing locally

Against a running HA, spawn three dummy update entities (two pending, one current):

```
export HA_TOKEN="<long-lived token>"   # HA Profile > Long-lived access tokens
python scripts/dev_entities.py         # spawn; --clear to reset them
```

They land as `update.dummy_widget_*`. Because they aren't in the entity registry, YOLO categorises them as "Other"/"Firmware" — opt those categories in via the YOLO Updater options to see them aggregated. The states persist until HA restarts or you `--clear`.

After any code change, restart Home Assistant and check the logs. Add the integration via Settings > Devices & Services > Add Integration > YOLO Updater.
