# Home Assistant YOLO Updater

![YOLO Updater](https://raw.githubusercontent.com/jjsmackay/hass-yolo-updater/main/custom_components/yolo_updater/brand/icon.png)

Press the button. Update everything. No ragrets.

Tired of clicking through a dozen individual update cards? YOLO Updater adds a single `! YOLO Update All` entity to your Home Assistant updates list. When updates are pending, hit install — it takes care of the rest.

## Features

- Aggregates your pending Home Assistant update entities into one `! YOLO Update All` entity
- **Opt-in by default.** You pick which categories it may install: HACS, Firmware, Apps, Other
- Leaves Home Assistant Core, OS, and Supervisor alone. You can't opt them in
- Exclude whole integrations, or individual entities
- Sorts to the top of the updates list (`! YOLO Update All`)
- Event-driven, no polling
- One tap installs everything in scope. YOLO

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

Click the following button and **Submit**. No configuration needed to add it.

[![Add Integration to Home Assistant.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=yolo_updater)

#### Manual

Add the integration via **Settings → Devices & Services → Add Integration → YOLO Updater** and **Submit**.

## Choose what it updates

Out of the box YOLO installs **nothing**. You opt in first. On the integration, hit **Configure**:

1. **Categories.** Tick the update types YOLO may install: HACS, Firmware, Apps, Other.
2. **Exclude integrations.** Leave out whole integrations within those categories.
3. **Exclude entities.** Leave out individual updates.

You can't opt in Home Assistant Core, OS, or Supervisor. YOLO always skips them.

## Usage

The `! YOLO Update All` entity appears in your updates list whenever an in-scope update is pending. Press **Install** to update everything in scope at once.

> ⚠️ This installs your opted-in updates with no confirmation dialog. That's the point. YOLO always leaves Core, OS, and Supervisor alone.

## Credits

- [A Clever Monkey](https://buymeacoffee.com/jjsmackay)
- [✼ Claude](https://claude.ai)

[![Buy me a Coffee?](https://buymeacoffee.com/assets/img/custom_images/yellow_img.png)](https://buymeacoffee.com/jjsmackay)

## License

[MIT](LICENSE)
