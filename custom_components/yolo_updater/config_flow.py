"""Config flow for YOLO Updater."""

from homeassistant.config_entries import ConfigFlow

from . import DOMAIN


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
