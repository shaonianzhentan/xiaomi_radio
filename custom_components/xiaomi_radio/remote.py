import aiohttp, time, asyncio
import logging
import voluptuous as vol
from datetime import timedelta
from homeassistant.util.dt import utcnow

from miio import AirConditioningCompanion, DeviceException

from homeassistant.components.media_player import PLATFORM_SCHEMA

from homeassistant.components.remote import (
    ATTR_DELAY_SECS,
    ATTR_NUM_REPEATS,
    DEFAULT_DELAY_SECS,
    RemoteEntity,
)

from homeassistant.const import CONF_HOST, CONF_NAME, CONF_TOKEN
import homeassistant.helpers.config_validation as cv
from .const import DOMAIN
DEFAULT_NAME = "空调伴侣"

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
        self.hass = hass
        self._host = host
        self._name = name
        self.device = AirConditioningCompanion(host, token)

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
        key = command[0]
        actionKeys = {
            # 创建电视
            'cwds_power': ['FE000000000000000000000000050025224A0036003E00AC01C312F43301020202000000000002020200000000000002020000000002020000020202020433020477'],
            # 天猫魔盒
            'tmmh_power': ['FE000000000000000000000000070024224B0032003F00B000E901CD0384121154010101010101010102020202020101020202020102010201010101020102010206530663'],
            'tmmh_up': ['FE000000000000000000000000060024224A003700AF00E901CF038E121F430000000000000000010101010100000101010000000001000000010101010001054205FE'],
            'tmmh_down': ['FE000000000000000000000000060024224A003700AE00E801CC038D121C430000000000000000010101010100000100010001000000000100010001010101054205F5'],
            'tmmh_right': ['FE000000000000000000000000070026224D003800AF00E901CD039B1220265E4300000000000000000101010101000001000101010000000001000000010101010542064205D7'],
            'tmmh_left': ['FE000000000000000000000000060024224A003800AE00E701CF039E12214300000000000000000101010101000001000101000000000001000001010101010542050E'],
            'tmmh_home': ['FE000000000000000000000000060024224A003700AF00E901CF038E121E430000000000000000010101010100000101010100000001000000000101010001054205FD'],
            'tmmh_enter': ['FE000000000000000000000000060024224A003700AF00E901CE038B121A430000000000000000010101010100000100010000000000000100010101010101054205F5'],
            'tmmh_back': ['FE000000000000000000000000060024224A003700AE00E901CF038F121C430000000000000000010101010100000101010101000001000000000001010001054205FB'],
            'tmmh_menu': ['FE000000000000000000000000060024224A003700AE00E601CE038F121A430000000000000000010101010100000100010100010000000100000100010101054205F5'],
            'tmmh_volumedown': ['FE000000000000000000000000060024224A003700AE00E601CB0392121D430000000000000000010101010100000101000101010001000001000000010001054205F8'],
            'tmmh_volumeup': ['FE000000000000000000000000060024224A003700AE00E801CE0390121D430000000000000000010101010100000101010101010101010000000000000000054205FB']
        }

        if key in actionKeys:
            ir_command = actionKeys[key][0]
        else:
            ir_command = key

        if ir_command.startswith("FE"):
            # 发送红外命令
            state = await self.device.status()
            air_condition_model = state.air_condition_model.hex()
            if air_condition_model is not None:
                self.device.send_ir_code(air_condition_model, ir_command)

    async def async_learn_command(self, **kwargs):        
        # 开始录码
        slot = 30
        timeout = 30
        self.device.learn(slot)
        start_time = utcnow()
        while (utcnow() - start_time) < timedelta(seconds=timeout):
            message = self.device.learn_result()
            message = message[0]
            _LOGGER.debug("从设备接收到的消息: '%s'", message)
            if message.startswith("FE"):
                log_msg = "收到的命令是: {}".format(message)
                _LOGGER.info(log_msg)
                self.hass.components.persistent_notification.async_create(
                    log_msg, title="小米遥控器"
                )
                self.device.learn_stop(slot)
                return
            await asyncio.sleep(1)

        self.device.learn_stop(slot)
        _LOGGER.error("录制超时，没有捕获到红外命令")
        self.hass.components.persistent_notification.async_create(
            "录制超时，没有捕获到红外命令", title="小米遥控器"
        )