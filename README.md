# Home Assistant YOLO Updater

![YOLO Updater](https://raw.githubusercontent.com/jjsmackay/hass-yolo-updater/main/custom_components/yolo_updater/brand/icon.png)

Press the button. Update everything. No ragrets.

Tired of clicking through a dozen individual update cards? YOLO Updater adds a single `! YOLO Update All` entity to your Home Assistant updates list. When updates are pending, hit install — it takes care of the rest.

## Features

- Aggregates **all** pending Home Assistant update entities into one
- Sorts to the top of the updates list (`! YOLO Update All`)
- Reactively updates — no polling, event-driven
- One tap to install everything

## Installation

### HACS (recommended)

1. Open HACS → Integrations → Custom repositories
2. Add `https://github.com/jjsmackay/hass-yolo-updater` as an Integration
3. Search for **YOLO Updater** and install
4. Restart Home Assistant

### Manual

Copy `custom_components/yolo_updater/` into your Home Assistant `custom_components/` directory and restart.

## Setup

After installation, add the integration via **Settings → Devices & Services → Add Integration → YOLO Updater**. No configuration needed.

## Usage

The `! YOLO Update All` entity will appear in your updates list whenever any updates are pending. Press **Install** to update everything at once.

> ⚠️ This installs all pending updates without confirmation. That's the point.

## License

[GLWT (Good Luck With That) Public License](LICENSE) — Good luck and Godspeed.
