"""Support for media browsing."""
import logging, os
from urllib.parse import urlparse, parse_qs, parse_qsl, quote
from homeassistant.helpers.network import get_url
from homeassistant.components import media_source
from homeassistant.components.media_player import BrowseError, BrowseMedia
from homeassistant.components.media_player.const import (
    MediaClass,
    MediaType,
)

PLAYABLE_MEDIA_TYPES = [
    MediaType.ALBUM,
    MediaType.ARTIST,
    MediaType.TRACK,
]

CONTAINER_TYPES_SPECIFIC_MEDIA_CLASS = {
    MediaType.ALBUM: MediaClass.ALBUM,
    MediaType.ARTIST: MediaClass.ARTIST,
    MediaType.PLAYLIST: MediaClass.PLAYLIST,
    MediaType.SEASON: MediaClass.SEASON,
    MediaType.TVSHOW: MediaClass.TV_SHOW,
}

CHILD_TYPE_MEDIA_CLASS = {
    MediaType.SEASON: MediaClass.SEASON,
    MediaType.ALBUM: MediaClass.ALBUM,
    MediaType.ARTIST: MediaClass.ARTIST,
    MediaType.MOVIE: MediaClass.MOVIE,
    MediaType.PLAYLIST: MediaClass.PLAYLIST,
    MediaType.TRACK: MediaClass.TRACK,
    MediaType.TVSHOW: MediaClass.TV_SHOW,
    MediaType.CHANNEL: MediaClass.CHANNEL,
    MediaType.EPISODE: MediaClass.EPISODE,
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
        media_class=MediaClass.DIRECTORY,
        media_content_id="home",
        media_content_type="home",
        title="小米电台",
        can_play=False,
        can_expand=True,
        children=[
            BrowseMedia(
                media_class=MediaClass.DIRECTORY,
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
                media_class=MediaClass.DIRECTORY,
                media_content_type='id',
                media_content_id=str(item['id']),
                can_play=True,
                can_expand=False,
                thumbnail=item['image']
            )
        )

    return library_info