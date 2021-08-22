import time, asyncio
import logging
import voluptuous as vol
from datetime import timedelta
from homeassistant.util.dt import utcnow
from .shaonianzhentan import save_yaml, load_yaml

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
        self.config_file = hass.config.path(".shaonianzhentan/ir_command.yaml")
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
        device = kwargs.get('device', '')
        key = command[0]
        ir_command = key
        if device != '':
            # 读取配置文件
            command_list = load_yaml(self.config_file)
            dev = command_list.get(device, {})
            # 判断配置是否存在
            if key in dev:
                ir_command = dev[key]
        # 发送红外命令
        if ir_command.startswith("FE"):
            state = self.device.status()
            air_condition_model = state.air_condition_model.hex()
            if air_condition_model is not None:
                self.device.send_ir_code(air_condition_model, ir_command)

    async def async_learn_command(self, **kwargs):
        device = kwargs.get('device', '')
        command = kwargs.get('command', '')
        if command == '' or device == '':
            return
        # 读取配置文件
        command_list = load_yaml(self.config_file)
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
                command_list[device][command] = message
                log_msg = "收到的命令是: {}, 红外码：{}".format(command, message)
                self.hass.components.persistent_notification.async_create(
                    log_msg, title="小米遥控器"
                )
                self.device.learn_stop(slot)
                # 保存配置文件
                save_yaml(self.config_file, command_list)
                return
            await asyncio.sleep(1)

        self.device.learn_stop(slot)
        self.hass.components.persistent_notification.async_create(
            "录制超时，没有捕获到红外命令", title="小米遥控器"
        )