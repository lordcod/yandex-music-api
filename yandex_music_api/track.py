from __future__ import annotations
from datetime import datetime

from typing import TYPE_CHECKING, List
from hashlib import md5
import xmltodict

from yandex_music_api.types import TrackMajorPayload, TrackPayload, TrackShortPayload

if TYPE_CHECKING:
    from yandex_music_api.state import ConnectionState
    from yandex_music_api.album import Album
    from yandex_music_api.artist import Artist


SIGN_SALT = 'XGRlBW9FXlekgbPrRHuSiA'


def get_track_sign(data: dict) -> str:
    path = data['path']
    s = data['s']
    sign = md5((SIGN_SALT + path[1::] + s).encode('utf-8')).hexdigest()
    return sign


def decode_download_info(xmldata: str) -> str:
    data = xmltodict.parse(xmldata)['download-info']
    host = data['host']
    ts = data['ts']
    path = data['path']
    sign = get_track_sign(data)

    return f'https://{host}/get-mp3/{sign}/{ts}{path}'


class Track:
    def __init__(self, state: ConnectionState, data: TrackPayload) -> None:
        self._state = state
        self.albums: List[Album] = [state.de_list['album'](state, album)
                                    for album in data['albums']]
        self.artists: List[Artist] = [
            state.de_list['artist'](state, artist) for artist in data['artists']]
        self.available: bool = data['available']
        self.cover_uri = data.get('coverUri')
        self.diration: float = data['durationMs']/1000
        self.file_size: int = data['fileSize']
        self.lyrics_available: bool = data['lyricsAvailable']
        self.major: TrackMajorPayload = data['major']
        self.image: str = data.get('ogImage')
        self.id: int = int(data['id'])
        self.title: str = data['title']
        self.major: dict = data['major']
        self.artist_names: List[str] = [art.name for art in self.artists]

    def get_image(self, size="1080x1080"):
        return f'https://{self.image.replace("%%", size)}'

    def get_url(self):
        album = self.albums[0]
        return f"https://music.yandex.ru/album/{album.id}/track/{self.id}"

    def __repr__(self) -> str:
        return f"<Track title='{self.title}' id={self.id}>"

    def __str__(self) -> str:
        return f"{self.title} - {', '.join(self.artist_names)}"

    async def download_link(
        self,
        bitrateInKbps: int = 192
    ) -> str:
        results = await self._state.http.get_download_info(self.id)
        for res in results:
            if res['bitrateInKbps'] == bitrateInKbps:
                url = res['downloadInfoUrl']
                break
        else:
            raise Exception('bitrateInKbps error')
        data = await self._state.http.get_from_downloadinfo(url)
        link = decode_download_info(data)
        return link

    async def like(self) -> None:
        userid = self._state.userid
        await self._state.http.like_track(userid, [self.id])

    async def dislike(self) -> None:
        userid = self._state.userid
        await self._state.http.dislike_track(userid, [self.id])


class ShortTrack:
    def __init__(self, state: ConnectionState, data: TrackShortPayload) -> None:
        self._state = state
        self.id: int = data['id']
        self.album_id: int = data['albumId']
        self.added_at: datetime = datetime.fromisoformat(data['timestamp'])

    def __repr__(self) -> str:
        return f"<ShortTrack id={self.id} album_id={self.album_id}>"

    def get_url(self) -> str:
        return f"https://music.yandex.ru/album/{self.album_id}/track/{self.id}"

    download_link = Track.download_link
    like = Track.like
    dislike = Track.dislike
