import time, asyncio
import logging
import voluptuous as vol
from datetime import timedelta
from homeassistant.util.dt import utcnow
from .shaonianzhentan import save_yaml, load_yaml

from miio import AirConditioningCompanion, DeviceException

from homeassistant.components.remote import (
    ATTR_DELAY_SECS,
    ATTR_NUM_REPEATS,
    DEFAULT_DELAY_SECS,
    RemoteEntity,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_TOKEN
import homeassistant.helpers.config_validation as cv
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    config = entry.data
    host = config.get(CONF_HOST)
    name = config.get(CONF_NAME) + '遥控器'
    token = config.get(CONF_TOKEN)
    async_add_entities([XiaomiRemote(host, token, name, hass)], True)

class XiaomiRemote(RemoteEntity):

    def __init__(self, host, token, name, hass):
        self.hass = hass
        self._host = host
        self._name = name
        self.config_file = hass.config.path(".storage/xiaomi_radio.yaml")
        self.device = AirConditioningCompanion(host, token)

    @property
    def name(self):
        return self._name

    @property
    def unique_id(self):
        return self._host

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
            _LOGGER.debug(dev)
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
        # 格式转换
        if isinstance(command, list):
            if len(command) > 0:
                command = command[0]
            else:
                command = ''

        if command == '' or device == '':
            return
        # 开始录码
        await self.hass.services.async_call('persistent_notification', 'create', {
                    'notification_id': 'xiaomi_radio-learn_command',
                    'title': '小米遥控器',
                    'message': "请将红外遥控器对准空调伴侣，然后按一下要录制的按键，成功后将在这里显示相关信息"
                })
        # 读取配置文件
        command_list = load_yaml(self.config_file)
        if device not in command_list:
            command_list[device] = {}
        slot = 30
        timeout = 30
        self.device.learn(slot)
        start_time = utcnow()
        while (utcnow() - start_time) < timedelta(seconds=timeout):
            learn_result = self.device.learn_result()
            message = learn_result[0]
            _LOGGER.debug("从设备接收到的消息: '%s'", message)
            if message.startswith("FE"):
                command_list[device][command] = message
                await self.hass.services.async_call('persistent_notification', 'create', {
                    'notification_id': 'xiaomi_radio-learn_command',
                    'title': '小米遥控器',
                    'message': "设备：{} \n命令: {} \n红外码：{}".format(device, command, message)
                })
                self.device.learn_stop(slot)
                # 保存配置文件
                save_yaml(self.config_file, command_list)
                return
            await asyncio.sleep(1)

        self.device.learn_stop(slot)
        await self.hass.services.async_call('persistent_notification', 'create', {
                    'notification_id': 'xiaomi_radio-learn_command',
                    'title': '小米遥控器',
                    'message': "录制超时，没有捕获到红外命令"
                })