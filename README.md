# Home Assistant YOLO Updater

![YOLO Updater](https://raw.githubusercontent.com/jjsmackay/hass-yolo-updater/main/custom_components/yolo_updater/brand/icon.png)

Press the button. Update everything. No ragrets.

Tired of clicking through a dozen individual update cards? YOLO Updater adds a single `! YOLO Update All` entity to your Home Assistant updates list. When updates are pending, hit install — it takes care of the rest.

## Features

- Aggregates **all** pending Home Assistant update entities into one
- Sorts to the top of the updates list (`! YOLO Update All`)
- Reactively updates — no polling, event-driven
- One tap to install everything. YOLO

## Installation

#### HACS (recommended)

[![My Home Assistant](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?repository=hass-yolo-updater&owner=jjsmackay&category=Integration)

1. Navigate to HACS and search for **YOLO Updater**
2. Install with the big blue **Download** button
3. Restart Home Assistant

#### Manual

Copy `custom_components/yolo_updater/` into your Home Assistant `custom_components/` directory and restart.

## Setup

#### Easy Mode

After installation, just click the following button and **Submit**. No configuration needed.

[![Add Integration to Home Assistant.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=yolo_updater)

#### Manual

Add the integration via **Settings → Devices & Services → Add Integration → YOLO Updater** and **Submit**.

## Usage

The `! YOLO Update All` entity will appear in your updates list whenever any updates are pending. Press **Install** to update everything at once.

> ⚠️ This installs all pending updates without confirmation. That's the point.

## Credits

- [A Clever Monkey](https://buymeacoffee.com/jjsmackay)
- [✼ Claude](https://claude.ai)

[![Buy me a Coffee?](https://buymeacoffee.com/assets/img/custom_images/yellow_img.png)](https://buymeacoffee.com/jjsmackay)

## License

[GLWT (Good Luck With That) Public License](LICENSE) — Good luck and Godspeed.
