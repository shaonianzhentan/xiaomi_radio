import aiohttp, time
import logging
import voluptuous as vol
from miio import Device, DeviceException

from homeassistant.components.media_player import PLATFORM_SCHEMA

from homeassistant.components.remote import (
    ATTR_DELAY_SECS,
    ATTR_NUM_REPEATS,
    DEFAULT_DELAY_SECS,
    RemoteEntity,
)

from homeassistant.const import CONF_HOST, CONF_NAME
import homeassistant.helpers.config_validation as cv
from .const import DOMAIN
DEFAULT_NAME = "红外遥控"

_LOGGER = logging.getLogger(__name__)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_HOST): cv.string,
        vol.Required(CONF_TOKEN): cv.string,
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    }
)

def setup_platform(hass, config, add_entities, discovery_info=None):

    host = config.get(CONF_HOST)
    name = config.get(CONF_NAME)
    token = config.get(CONF_TOKEN)
    add_entities([XiaomiRemote(host, token, name, hass)])

class XiaomiRemote(RemoteEntity):

    def __init__(self, host, token, name, hass):
        self._host = host
        self._name = name
        self.device = Device(host, token, lazy_discover=False)

    @property
    def name(self):
        return self._name

    @property
    def unique_id(self):
        return self._host.replace('.', '')

    @property
    def is_on(self):
        return True

    @property
    def should_poll(self):
        return False

    async def async_turn_on(self, activity: str = None, **kwargs):
         """Turn the remote on."""

    async def async_turn_off(self, activity: str = None, **kwargs):
         """Turn the remote off."""
         
    async def async_send_command(self, command, **kwargs):
        """Send commands to a device."""
        ir_command = command[0]
        if ir_command.startswith("01"):
            print("01xxxxxxxxxxxxxxxxxxxxxx")
        elif ir_command.startswith("FE"):
            print("FExxxxxxxxxxxxxxxxxxxxxx")
        else:
            _LOGGER.error("Invalid IR command.")
