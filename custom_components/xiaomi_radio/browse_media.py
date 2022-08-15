"""Support for media browsing."""
import logging, os
import requests
from urllib.parse import urlparse, parse_qs, parse_qsl, quote
from homeassistant.helpers.network import get_url
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

async def async_browse_media(media_player, media_content_type, media_content_id):

    library_info = BrowseMedia(
        media_class=MEDIA_CLASS_DIRECTORY,
        media_content_id="home",
        media_content_type="home",
        title="小米电台",
        can_play=False,
        can_expand=True,
        children=[],
    )
    for item in media_player._fm_list:
        id = str(item['id'])
        res = await media_player.hass.async_add_executor_job(requests.get, f'https://live.ximalaya.com/live-web/v1/radio?radioId={id}')
        
        res_data = res.json()
        data = res_data['data']
        title = data.get('programName', '')
        if title != '':
            title = data.get('name', '小米电台')

        library_info.children.append(
            BrowseMedia(
                title=title,
                media_class=MEDIA_CLASS_DIRECTORY,
                media_content_type='id',
                media_content_id=id,
                can_play=True,
                can_expand=False,
                thumbnail=data.get('coverLarge', 'https://www.home-assistant.io/images/favicon-192x192-full.png')
            )
        )
    return library_info