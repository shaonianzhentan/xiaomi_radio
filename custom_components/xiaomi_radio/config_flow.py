from __future__ import annotations

from typing import Any
import voluptuous as vol

from homeassistant.config_entries import ConfigFlow
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN
from miio import AirConditioningCompanion, DeviceException

class SimpleConfigFlow(ConfigFlow, domain=DOMAIN):

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:

        errors = {}
        if user_input is not None:
            # 验证IP
            try:
                device = AirConditioningCompanion(user_input.get('host'), user_input.get('token'))
                print(device.info())
                return self.async_create_entry(title=DOMAIN, data=user_input)
            except Exception as ex:
                print(ex)
                errors['base'] = 'failed'
        else:
            user_input = {}

        DATA_SCHEMA = vol.Schema({
            vol.Required("name", default = user_input.get('name', '小米电台')): str,
            vol.Required("host", default = user_input.get('host')): str,
            vol.Required("token", default = user_input.get('token')): str
        })
        return self.async_show_form(step_id="user", data_schema=DATA_SCHEMA, errors=errors)

        