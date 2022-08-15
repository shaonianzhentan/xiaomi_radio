"""Add support for the Xiaomi TVs."""
import logging, asyncio, functools, os
import requests, time, hashlib
import voluptuous as vol
from .shaonianzhentan import download, md5
from miio import Device, DeviceException

from haffmpeg.core import HAFFmpeg
from homeassistant.helpers import template
from homeassistant.helpers.network import get_url
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.config_entries import ConfigEntry
from homeassistant.components.ffmpeg import (DATA_FFMPEG, CONF_EXTRA_ARGUMENTS)    
from homeassistant.components.media_player import MediaPlayerEntity
from homeassistant.components.media_player.const import (
    SUPPORT_BROWSE_MEDIA,
    SUPPORT_TURN_OFF,
    SUPPORT_TURN_ON,
    SUPPORT_VOLUME_STEP,
    SUPPORT_VOLUME_SET,
    SUPPORT_VOLUME_MUTE,
    SUPPORT_SELECT_SOURCE,
    SUPPORT_SELECT_SOUND_MODE,
    SUPPORT_PLAY_MEDIA,
    SUPPORT_PLAY,
    SUPPORT_PAUSE,
    SUPPORT_NEXT_TRACK,
    SUPPORT_PREVIOUS_TRACK
)

from homeassistant.components.ffmpeg import (
    DATA_FFMPEG, CONF_EXTRA_ARGUMENTS)
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_TOKEN, STATE_OFF, STATE_ON, STATE_PLAYING, STATE_PAUSED
import homeassistant.helpers.config_validation as cv

from .const import DEFAULT_NAME, DOMAIN, VERSION
from .browse_media import async_browse_media

_LOGGER = logging.getLogger(__name__)

SUPPORT_XIAOMI_RADIO = SUPPORT_VOLUME_STEP | SUPPORT_VOLUME_MUTE | SUPPORT_VOLUME_SET | \
    SUPPORT_PLAY | SUPPORT_PAUSE | SUPPORT_PREVIOUS_TRACK | SUPPORT_NEXT_TRACK | \
    SUPPORT_BROWSE_MEDIA | SUPPORT_PLAY_MEDIA

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    config = entry.data
    host = config.get(CONF_HOST)
    name = config.get(CONF_NAME)
    token = config.get(CONF_TOKEN)
    hass.http.register_static_path('/tts-radio', hass.config.path("tts"), False)
    xiaomiRadio = XiaomiRadio(host, token, name, hass)
    hass.services.async_register(DOMAIN, 'tts', xiaomiRadio.tts)
    async_add_entities([xiaomiRadio], True)

class XiaomiRadio(MediaPlayerEntity):
    """Represent the Xiaomi TV for Home Assistant."""

    def __init__(self, host, token, name, hass):
        """Receive IP address and name to construct class."""
        self.hass = hass
        self._name = name
        self._host = host
        self.device = Device(host, token, lazy_discover=False)
        self._state = STATE_PAUSED
        self._volume_level = 1
        self._is_volume_muted = False
        self._index = 0
        self._fm_list = []

    @property
    def name(self):
        """Return the display name of this TV."""
        return self._name

    @property
    def media_image_remotely_accessible(self) -> bool:
        # 图片远程访问
        return True

    @property
    def unique_id(self):
        return self._host.replace('.', '')

    @property
    def volume_level(self):
        return self._volume_level

    @property
    def is_volume_muted(self):
        return self._is_volume_muted

    @property
    def state(self):
        """Return _state variable, containing the appropriate constant."""
        return self._state

    @property
    def assumed_state(self):
        """Indicate that state is assumed."""
        return True

    @property
    def supported_features(self):
        """Flag media player features that are supported."""
        return SUPPORT_XIAOMI_RADIO

    async def async_browse_media(self, media_content_type=None, media_content_id=None):
        return await async_browse_media(self, media_content_type, media_content_id)

    async def async_play_media(self, media_type, media_id, **kwargs):
        if media_type == 'id':            
            self.device.send('play_specify_fm', {'id': int(media_id), 'type': 0})
            await self.load_media_info(media_id)
        elif media_type == 'tts':
            pass

    async def async_update(self):
        # 当前状态
        status = self.device.send("get_prop_fm", [])
        current_volume = status.get('current_volume', 100)
        self._volume_level = current_volume / 100
        current_program = status.get('current_program')
        current_status = status.get('current_status', 'pause')
        if current_status == 'pause':
            self._state = STATE_PAUSED
        elif current_status == 'run':
            self._state = STATE_PLAYING

        # 获取收藏电台
        result = self.device.send("get_channels", {"start": 0})
        self._fm_list = result['chs']
        # 读取相关信息
        if current_program is not None:
            await self.load_media_info(current_program)

    def volume_up(self):
        self.set_volume_level(self._volume_level + 0.1)

    def volume_down(self):
        self.set_volume_level(self._volume_level - 0.1)

    def mute_volume(self, mute):
        if mute:
            self.set_volume_level(0)
        else:
            self.set_volume_level(0.5)
        self._is_volume_muted = mute

    def set_volume_level(self, volume_level):
        self._volume_level = volume_level
        self.device.send('volume_ctrl_fm', [str(volume_level * 100)])
        
    def media_play(self):
        self.device.send('play_fm', ["on"])

    def media_pause(self):
        self.device.send('play_fm', ["off"])
        
    def media_next_track(self):
        _len = len(self._fm_list)
        if _len == 0:
            return None  
        index = self._index + 1
        if index >= _len:
            index = 0
        self.load_media(index)

    def media_previous_track(self):
        _len = len(self._fm_list)
        if _len == 0:
            return None
        index = self._index - 1
        if index < 0:
            index = len(self._fm_list) - 1
        self.load_media(index)

    def load_media(self, index):
        self._index = index
        fm = self._fm_list[index]
        id = fm['id']
        self.device.send('play_specify_fm', {'id': id, 'type': fm['type']})

    async def load_media_info(self, id):
        radioId = str(id)
        if self._attr_app_id != radioId:
            self._attr_app_id = radioId
            res = await self.hass.async_add_executor_job(requests.get, f'https://live.ximalaya.com/live-web/v1/radio?radioId={radioId}')
            res_data = res.json()
            data = res_data['data']            
            title = data.get('programName', '')
            if title != '':
                title = data.get('name', '小米电台')
            self._attr_media_artist = data.get('name', '小米电台')
            self._attr_media_image_url = data.get('coverLarge', 'https://www.home-assistant.io/images/favicon-192x192-full.png')
            self._attr_media_title = title

    async def tts(self, call):
        _state = self._state
        data = call.data
        message = self.template_message(data.get('text', ''))
        is_continue = data.get('continue', True)
        is_notification = data.get('notification', False)
        tts_dir = self.hass.config.path("tts")
        md5_message = md5(message)
        mp3Path = f'{tts_dir}/radio-{md5_message}.mp3'
        aacPath = f'{tts_dir}/radio-{md5_message}.aac'
        ttsUrl = get_url(self.hass).strip('/') + f'/tts-radio/radio-{md5_message}.aac'
        if os.path.exists(aacPath) == False:
            # 下载mp3文件
            await download(f'https://fanyi.baidu.com/gettts?lan=zh&text={message}&spd=5&source=web', mp3Path)
            # 转换aac文件
            ffmpeg = AacConverter(self.hass.data[DATA_FFMPEG].binary)
            result = await ffmpeg.convert(mp3Path, output=aacPath)
            if (not result) or (not os.path.exists(aacPath)) or (os.path.getsize(aacPath) < 1):
                _LOGGER.error("Convert file to aac failed.")
                return False
        # 删除文件并重新上传
        self.device.send("delete_user_music", ['99999'])
        self.device.send("download_user_music", ["99999", ttsUrl])
        index = 0
        while index < 10:
            progess = self.device.send("get_download_progress", [])
            if str(progess) == "['99999:100']":
                break
            index += 1
            await asyncio.sleep(1)
        if (index >= 10):
            _LOGGER.error("download tts file [" + ttsUrl + "] to gateway failed.")
            return False
        self.device.send('play_music', [99999])
        
        if is_notification == True:
            # log_msg = "TTS: %s" % message
            self.hass.components.persistent_notification.async_create(f"TTS: {message}", title='小米电台', notification_id="99999")
        # 如果之前是在播放电台，则恢复播放
        if is_continue and _state == STATE_PLAYING:
            result = self.device.send("get_music_info", [3])
            delay = result['list'][0]['time']
            await asyncio.sleep(delay + 3)
            self.media_play()

        # 解析模板
    def template_message(self, _message):
        tpl = template.Template(_message, self.hass)
        _message = tpl.async_render(None)
        return _message

class AacConverter(HAFFmpeg):

    @asyncio.coroutine
    def convert(self, input_source, output, extra_cmd=None, timeout=15):
        command = [
            "-vn",
            "-c:a",
            "aac",
            "-strict",
            "-2",
            "-b:a",
            "64K",
            "-ar",
            "48000",
            "-ac",
            "2",
            "-y"
        ]      
        is_open = yield from self.open(cmd=command, input_source=input_source, output=output, extra_cmd=extra_cmd)         
        if not is_open:
            _LOGGER.warning("Error starting FFmpeg.")
            return False
        try:
            proc_func = functools.partial(self._proc.communicate, timeout=timeout)
            out, error = yield from self._loop.run_in_executor(None, proc_func)
        except (asyncio.TimeoutError, ValueError):
            _LOGGER.error("Timeout convert audio file.")
            self._proc.kill()
            return False    
        return True

'''
0: alarm
1: alarm
2: chord
3: custom
print(device.send("get_music_info", [0]))
'''