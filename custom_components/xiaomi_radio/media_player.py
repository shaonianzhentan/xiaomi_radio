"""Add support for the Xiaomi TVs."""
import logging
import requests, time, hashlib
import voluptuous as vol

from miio import Device, DeviceException

from homeassistant.components.media_player import PLATFORM_SCHEMA, MediaPlayerEntity
from homeassistant.components.media_player.const import (
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
from homeassistant.const import CONF_HOST, CONF_NAME, STATE_OFF, STATE_ON, STATE_PLAYING, STATE_PAUSED
import homeassistant.helpers.config_validation as cv

from .const import DEFAULT_NAME

_LOGGER = logging.getLogger(__name__)
CONF_TOKEN = 'token'

SUPPORT_XIAOMI_RADIO = SUPPORT_VOLUME_STEP | SUPPORT_VOLUME_MUTE | SUPPORT_VOLUME_SET | \
    SUPPORT_PLAY | SUPPORT_PAUSE | SUPPORT_PREVIOUS_TRACK | SUPPORT_NEXT_TRACK

# No host is needed for configuration, however it can be set.
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_HOST): cv.string,
        vol.Required(CONF_TOKEN): cv.string,
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    }
)

def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the Xiaomi TV platform."""

    # If a hostname is set. Discovery is skipped.
    host = config.get(CONF_HOST)
    name = config.get(CONF_NAME)
    token = config.get(CONF_TOKEN)
    add_entities([XiaomiRadio(host, token, name, hass)])

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
        self._media_title = '小米空调伴侣电台'
        self._fm_list = []
        self._attributes = { 'ver': '1.1' }

    @property
    def name(self):
        """Return the display name of this TV."""
        return self._name

    @property
    def media_title(self):
        return self._media_title

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

    @property
    def extra_state_attributes(self):
        return self._attributes

    def update(self):
        # 当前状态
        status = self.device.send("get_prop_fm", [])
        current_volume = status.get('current_volume', 100)
        self._volume_level = current_volume / 100

        current_status = status.get('current_status', 'pause')
        if current_status == 'pause':
            self._state = STATE_PAUSED
        elif current_status == 'run':
            self._state = STATE_PLAYING
        
        # 获取收藏电台
        result = self.device.send("get_channels", {"start": 0})
        self._fm_list = result['chs']
        self._attributes.update({'fm_list': self._fm_list})
        if len(self._fm_list) > self._index:
            self._media_title = self._fm_list[self._index]['url']
            
    # 选择应用
    def select_source(self, source):
        if self.apps[source] is not None and self.state == STATE_ON:
            self.execute('startapp&type=packagename&packagename=' + self.apps[source])

    def turn_off(self):
        if self._state != STATE_OFF:
            self.keyevent('power')
            self.fire_event('off')
            self._state = STATE_OFF

    def turn_on(self):
        """Wake the TV back up from sleep."""
        if self._state != STATE_ON:
            self.fire_event('on')
            self._state = STATE_ON

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
        self._index = index
        fm = self._fm_list[index]
        self._media_title = fm['url']
        self.device.send('play_specify_fm', {'id': fm['id'], 'type': fm['type']})

    def media_previous_track(self):
        _len = len(self._fm_list)
        if _len == 0:
            return None
        index = self._index - 1
        if index < 0:
            index = len(self._fm_list) - 1
        self._index = index
        fm = self._fm_list[index]
        self._media_title = fm['url']
        self.device.send('play_specify_fm', {'id': fm['id'], 'type': fm['type']})
