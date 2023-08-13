"""Support for media browsing."""
import logging, os
from urllib.parse import urlparse, parse_qs, parse_qsl, quote
from homeassistant.helpers.network import get_url
from homeassistant.components import media_source
from homeassistant.components.media_player import BrowseError, BrowseMedia
from homeassistant.components.media_player.const import (
    MEDIA_CLASS_ALBUM,
    MEDIA_CLASS_ARTIST,
    MEDIA_CLASS_CHANNEL,
    MEDIA_CLASS_DIRECTORY,
    MEDIA_CLASS_EPISODE,
    MEDIA_CLASS_MOVIE,
    MEDIA_CLASS_MUSIC,
    MEDIA_CLASS_PLAYLIST,
    MEDIA_CLASS_SEASON,
    MEDIA_CLASS_TRACK,
    MEDIA_CLASS_TV_SHOW,
    MEDIA_TYPE_ALBUM,
    MEDIA_TYPE_ARTIST,
    MEDIA_TYPE_CHANNEL,
    MEDIA_TYPE_EPISODE,
    MEDIA_TYPE_MOVIE,
    MEDIA_TYPE_PLAYLIST,
    MEDIA_TYPE_SEASON,
    MEDIA_TYPE_TRACK,
    MEDIA_TYPE_TVSHOW,
)

PLAYABLE_MEDIA_TYPES = [
    MEDIA_TYPE_ALBUM,
    MEDIA_TYPE_ARTIST,
    MEDIA_TYPE_TRACK,
]

CONTAINER_TYPES_SPECIFIC_MEDIA_CLASS = {
    MEDIA_TYPE_ALBUM: MEDIA_CLASS_ALBUM,
    MEDIA_TYPE_ARTIST: MEDIA_CLASS_ARTIST,
    MEDIA_TYPE_PLAYLIST: MEDIA_CLASS_PLAYLIST,
    MEDIA_TYPE_SEASON: MEDIA_CLASS_SEASON,
    MEDIA_TYPE_TVSHOW: MEDIA_CLASS_TV_SHOW,
}

CHILD_TYPE_MEDIA_CLASS = {
    MEDIA_TYPE_SEASON: MEDIA_CLASS_SEASON,
    MEDIA_TYPE_ALBUM: MEDIA_CLASS_ALBUM,
    MEDIA_TYPE_ARTIST: MEDIA_CLASS_ARTIST,
    MEDIA_TYPE_MOVIE: MEDIA_CLASS_MOVIE,
    MEDIA_TYPE_PLAYLIST: MEDIA_CLASS_PLAYLIST,
    MEDIA_TYPE_TRACK: MEDIA_CLASS_TRACK,
    MEDIA_TYPE_TVSHOW: MEDIA_CLASS_TV_SHOW,
    MEDIA_TYPE_CHANNEL: MEDIA_CLASS_CHANNEL,
    MEDIA_TYPE_EPISODE: MEDIA_CLASS_EPISODE,
}

_LOGGER = logging.getLogger(__name__)

tts_protocol = 'media-source://tts'

async def async_browse_media(media_player, media_content_type, media_content_id):
    hass = media_player.hass
    # 媒体库
    if media_content_id is not None and media_content_id.startswith(tts_protocol):
        return await media_source.async_browse_media(
            hass,
            media_content_id
        )

    library_info = BrowseMedia(
        media_class=MEDIA_CLASS_DIRECTORY,
        media_content_id="home",
        media_content_type="home",
        title="小米电台",
        can_play=False,
        can_expand=True,
        children=[
            BrowseMedia(
                media_class=MEDIA_CLASS_DIRECTORY,
                media_content_id=tts_protocol,
                media_content_type='app',
                title="Text-to-speech",
                can_play=False,
                can_expand=True,
                thumbnail='https://brands.home-assistant.io/_/tts/icon.png'
            )
        ],
    )

    for item in media_player._fm_list:
        library_info.children.append(
            BrowseMedia(
                title=item['artist'],
                media_class=MEDIA_CLASS_DIRECTORY,
                media_content_type='id',
                media_content_id=str(item['id']),
                can_play=True,
                can_expand=False,
                thumbnail=item['image']
            )
        )

    return library_info