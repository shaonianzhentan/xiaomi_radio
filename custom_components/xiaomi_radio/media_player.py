import logging, asyncio, time
import voluptuous as vol

from homeassistant.components import media_source
from homeassistant.helpers import template
from homeassistant.helpers.network import get_url
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.config_entries import ConfigEntry
from homeassistant.components.media_player import (
    MediaPlayerEntity,
    async_process_play_media_url
)
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
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_TOKEN, STATE_OFF, STATE_ON, STATE_UNAVAILABLE, STATE_PLAYING, STATE_PAUSED
import homeassistant.helpers.config_validation as cv

from .const import DOMAIN
from .browse_media import async_browse_media
from .gateway_radio import GatewayRadio
from .tts import get_converter

_LOGGER = logging.getLogger(__name__)

SUPPORT_FEATURES = SUPPORT_VOLUME_STEP | SUPPORT_VOLUME_MUTE | SUPPORT_VOLUME_SET | \
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
    async_add_entities([
        XiaomiRadio(host, token, name, hass)
    ], True)

class XiaomiRadio(MediaPlayerEntity):
    """Represent the Xiaomi TV for Home Assistant."""

    def __init__(self, host, token, name, hass):
        """Receive IP address and name to construct class."""
        self.hass = hass
        self._host = host
        self.gateway = GatewayRadio(host, token)

        self._attr_name = name
        self._attr_state = STATE_PAUSED
        self._attr_volume_level = 1
        self._attr_unique_id = host
        # 图片远程访问
        self._attr_media_image_remotely_accessible = True
        self._attr_is_volume_muted = False

        self._index = 0
        self._fm_list = []
        self.updated_at = None

    @property
    def supported_features(self):
        """Flag media player features that are supported."""
        return SUPPORT_FEATURES

    async def async_browse_media(self, media_content_type=None, media_content_id=None):
        return await async_browse_media(self, media_content_type, media_content_id)

    async def async_play_media(self, media_type, media_id, **kwargs):
        hass = self.hass
        # 媒体库
        if media_source.is_media_source_id(media_id):
            play_item = await media_source.async_resolve_media(hass, media_id, self.entity_id)
            tts_url = async_process_play_media_url(hass, play_item.url)
            # 转码
            converter = get_converter(hass)
            aac_file_name = await converter.async_get_file(hass.config.path("tts"), tts_url)
            if aac_file_name is None:
                hass.components.persistent_notification.async_create(f"音频转换失败", title='小米电台', notification_id="99999")
                return
            # 上传到网关
            state = self._attr_state
            aac_url = get_url(hass, prefer_external=True).strip('/') + f'/tts-radio/{aac_file_name}'
            result = await self.gateway.async_download_music(aac_url)
            if result:
                self.gateway.play_music(99999)
                if state == STATE_PLAYING:
                    result = self.gateway.get_music_list(3)
                    delay = result[0]['time']
                    await asyncio.sleep(delay + 3)
                    self.media_play()
            else:
                hass.components.persistent_notification.async_create(f"HA与网关不在同一个网段，无法使用TTS功能", title='小米电台', notification_id="99999")
        elif media_type == 'id':
            self.gateway.play_fm({'id': int(media_id), 'type': 0})

    async def async_update(self):
        try:
            res = await self.hass.async_add_executor_job(self.gateway.get_radio_info)
            # 音量
            self._attr_volume_level = res.get('volume') / 100

            # 读取状态
            state = STATE_OFF
            status = res.get('status')
            if status == 'pause':
                state = STATE_PAUSED
            elif status == 'run':
                state = STATE_PLAYING
            self._attr_state = state

            if res.get('id') is not None:
                self._attr_app_name = res.get('artist')
                self._attr_media_image_url = res.get('image')
                self._attr_media_title = res.get('program')

            # 收藏电台
            now = time.time()
            if self.updated_at is None or self.updated_at < now:
                fm_list = await self.hass.async_add_executor_job(self.gateway.get_channels)
                _LOGGER.debug(fm_list)
                self._fm_list = fm_list
                # 5分钟更新一次
                self.updated_at =  now + 60 * 5

        except Exception as ex:
            _LOGGER.error(ex)
            self._attr_state = STATE_UNAVAILABLE

    def volume_up(self):
        self.set_volume_level(self._attr_volume_level + 0.1)

    def volume_down(self):
        self.set_volume_level(self._attr_volume_level - 0.1)

    def mute_volume(self, mute):
        if mute:
            self.set_volume_level(0)
        else:
            self.set_volume_level(0.5)
        self._attr_is_volume_muted = mute

    def set_volume_level(self, volume_level):
        self.gateway.set_volume_level(volume_level * 100)
        self._attr_volume_level = volume_level
        
    def media_play(self):
        self.gateway.play()
        self._attr_state = STATE_PLAYING
        
    def media_pause(self):
        self.gateway.pause()
        self._attr_state = STATE_PAUSED

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
        self.gateway.play_fm(fm)
        self._attr_state = STATE_PLAYING
