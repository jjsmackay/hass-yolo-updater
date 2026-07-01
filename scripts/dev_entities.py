#!/usr/bin/env python3
"""Spawn dummy ``update.*`` entities in a running Home Assistant, for testing.

This is a developer tool, not part of the shipped integration. It injects fake
update entities straight into a live HA via the REST API, so ``update.yolo_all``
picks them up and aggregates them exactly like real updates.

Usage:
    export HA_TOKEN="<long-lived access token>"   # Profile > Long-lived tokens
    export HA_URL="http://localhost:8123"          # optional, this is the default

    python scripts/dev_entities.py          # spawn the dummies (updates pending)
    python scripts/dev_entities.py --clear  # remove them again

Notes:
  - Injected entities are not in the entity registry, so YOLO categorises them as
    "Other" (or "Firmware" by device_class). Opt those categories in via the YOLO
    Updater options to see them in the pending list.
  - ``update.install`` won't actually do anything on these fakes (no integration
    backs them); they exist to exercise aggregation, categorisation, and the
    release-notes display. The states persist until HA restarts or you --clear.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request

# id -> attributes. state is "on" when latest_version != installed_version.
DUMMY_UPDATES = [
    {
        "entity_id": "update.dummy_widget_alpha",
        "friendly_name": "Dummy Widget Alpha Update",
        "installed_version": "1.0.0",
        "latest_version": "2.0.0",
        "release_url": "https://example.com/widget-alpha/releases/2.0.0",
    },
    {
        "entity_id": "update.dummy_widget_beta",
        "friendly_name": "Dummy Widget Beta Update",
        "installed_version": "3.1.0",
        "latest_version": "3.2.0",
        "device_class": "firmware",
        # no release_url -> renders as plain text
    },
    {
        "entity_id": "update.dummy_widget_gamma",
        "friendly_name": "Dummy Widget Gamma Update",
        "installed_version": "0.9.0",
        "latest_version": "0.9.0",  # no update pending -> state off
    },
]


def _request(url: str, token: str, payload: dict) -> None:
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(req) as resp:  # noqa: S310 (trusted local URL)
        resp.read()


def _set_state(base: str, token: str, dummy: dict, *, clear: bool) -> str:
    installed = dummy["installed_version"]
    latest = installed if clear else dummy["latest_version"]
    state = "off" if latest == installed else "on"
    attributes = {
        "friendly_name": dummy["friendly_name"],
        "installed_version": installed,
        "latest_version": latest,
        "in_progress": False,
        "release_url": dummy.get("release_url"),
        "title": dummy["friendly_name"].removesuffix(" Update"),
        "supported_features": 1,  # UpdateEntityFeature.INSTALL
    }
    if dummy.get("device_class"):
        attributes["device_class"] = dummy["device_class"]

    url = f"{base}/api/states/{dummy['entity_id']}"
    _request(url, token, {"state": state, "attributes": attributes})
    return state


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--clear",
        action="store_true",
        help="reset the dummies so no update is pending (state off)",
    )
    args = parser.parse_args()

    base = os.environ.get("HA_URL", "http://localhost:8123").rstrip("/")
    token = os.environ.get("HA_TOKEN")
    if not token:
        print("HA_TOKEN is not set (create a long-lived token in your HA profile)")
        return 1

    try:
        for dummy in DUMMY_UPDATES:
            state = _set_state(base, token, dummy, clear=args.clear)
            print(f"{dummy['entity_id']}: {state}")
    except urllib.error.URLError as err:
        print(f"Failed to reach {base}: {err}")
        return 1

    print("Done. Opt in the 'Other'/'Firmware' categories in YOLO Updater options.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
