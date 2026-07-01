"""Config flow for YOLO Updater."""

import voluptuous as vol
from homeassistant.config_entries import ConfigEntry, ConfigFlow, OptionsFlow
from homeassistant.core import callback
from homeassistant.helpers import entity_registry as er, selector
from homeassistant.loader import async_get_integrations

from . import DOMAIN
from .scope import OPT_IN_CATEGORIES, categorise


class UpdateAllConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for YOLO Updater."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        if user_input is not None:
            return self.async_create_entry(title="YOLO Updater", data={})

        return self.async_show_form(step_id="user")

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> "UpdateAllOptionsFlow":
        """Return the options flow handler."""
        return UpdateAllOptionsFlow()


class UpdateAllOptionsFlow(OptionsFlow):
    """Three-step options flow: categories, integration excludes, entity excludes."""

    async def async_step_init(self, user_input=None):
        """Step 1 - choose which update categories YOLO may install."""
        if user_input is not None:
            self._categories = user_input.get("categories", [])
            return await self.async_step_exclude_integrations()

        current = self.config_entry.options.get("categories", [])
        schema = vol.Schema(
            {
                vol.Optional("categories", default=current): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=list(OPT_IN_CATEGORIES),
                        multiple=True,
                        mode=selector.SelectSelectorMode.LIST,
                        translation_key="categories",
                    )
                )
            }
        )
        return self.async_show_form(step_id="init", data_schema=schema)

    def _categorised_update_entities(self):
        """Return (entity_id, platform, category) for every update entity except YOLO's own."""
        registry = er.async_get(self.hass)
        rows = []
        for entry in registry.entities.values():
            if (
                not entry.entity_id.startswith("update.")
                or entry.entity_id == "update.yolo_all"
            ):
                continue
            state = self.hass.states.get(entry.entity_id)
            device_class = (
                state.attributes.get("device_class")
                if state
                else entry.original_device_class
            )
            rows.append(
                (
                    entry.entity_id,
                    entry.platform,
                    categorise(entry.entity_id, entry.platform, device_class),
                )
            )
        return rows

    async def async_step_exclude_integrations(self, user_input=None):
        """Step 2 - exclude whole integrations (within the chosen categories)."""
        if user_input is not None:
            self._exclude_integrations = user_input.get("exclude_integrations", [])
            return await self.async_step_exclude_entities()

        categories = getattr(self, "_categories", [])
        platforms = sorted(
            {
                platform
                for (_eid, platform, category) in self._categorised_update_entities()
                if platform and category in categories
            }
        )
        integrations = await async_get_integrations(self.hass, platforms)
        options = [
            selector.SelectOptionDict(
                value=domain,
                label=(
                    integration.name
                    if (integration := integrations.get(domain)) is not None
                    and not isinstance(integration, BaseException)
                    else domain
                ),
            )
            for domain in platforms
        ]
        schema = vol.Schema(
            {
                vol.Optional(
                    "exclude_integrations",
                    default=self.config_entry.options.get("exclude_integrations", []),
                ): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=options,
                        multiple=True,
                        custom_value=True,
                        mode=selector.SelectSelectorMode.DROPDOWN,
                    )
                )
            }
        )
        return self.async_show_form(
            step_id="exclude_integrations", data_schema=schema
        )

    async def async_step_exclude_entities(self, user_input=None):
        """Step 3 - exclude specific entities, scoped to chosen categories and remaining integrations."""
        categories = getattr(self, "_categories", [])
        excluded_integrations = getattr(self, "_exclude_integrations", [])
        if user_input is not None:
            return self.async_create_entry(
                title="",
                data={
                    "categories": categories,
                    "exclude_integrations": excluded_integrations,
                    "exclude_entities": user_input.get("exclude_entities", []),
                },
            )

        shown = sorted(
            eid
            for (eid, platform, category) in self._categorised_update_entities()
            if category in categories and platform not in excluded_integrations
        )
        # Only pre-fill saved excludes that are still shown.
        saved_entities = self.config_entry.options.get("exclude_entities", [])
        default_entities = [e for e in saved_entities if e in shown]
        schema = vol.Schema(
            {
                vol.Optional(
                    "exclude_entities",
                    default=default_entities,
                ): selector.EntitySelector(
                    selector.EntitySelectorConfig(
                        multiple=True,
                        include_entities=shown,
                    )
                )
            }
        )
        return self.async_show_form(step_id="exclude_entities", data_schema=schema)
