from datetime import datetime

from yandex_music_api.state import ConnectionState
from typing import List
from .util import get_download_info, download_track


class Artist:
    def __init__(self, state: ConnectionState, data: dict) -> None:
        self._state = state
        self.data = data
        self.id: int = data.get('id')
        self.name: str = data.get('name')
        self.cover: dict = data.get('cover')
        self.avatar: str = self.cover and self.cover.get('uri')

    async def get_rating_track_ids(self) -> List[int]:
        url = f"{self.requests.base_url}/artists/{self.id}/track-ids-by-rating"
        responce = await self.requests.read_json(url)
        track_ids = responce["result"]["tracks"]

        return track_ids


class Playlist:
    def __init__(self, state: ConnectionState, data: dict) -> None:
        self._state = state
        self.data = data
        self.owner: dict = data.get('owner')
        self.id: int = data.get('uid')
        self.kind = data.get('kind')
        self.title = data.get('title')
        self.description = data.get('description')
        self.tags = data.get('tags')


class Album:
    def __init__(self, state: ConnectionState, data: dict) -> None:
        self._state = state
        self.data = data
        self.id: int = data.get('id')
        self.title: str = data.get('title')
        self.type: str = data.get('metaType')
        self.year: int = data.get('year')
        self.release_date: str = data.get('releaseDate')
        self.image: str = data.get('ogImage')
        self.artists: List[Artist] = [
            Artist(state, artist) for artist in data.get('artists', [])]
        self.labels: dict = data.get('labels')

    async def get_tracks(self) -> List['Track']:
        json = await self._state.http.get_tracks_with_album(self.id)
        tracks = json["result"]["volumes"]
        return [Track(self._state, track_data) for datas in tracks for track_data in datas]


class Track:
    def __init__(self, state: ConnectionState, data: dict) -> None:
        self._state = state
        self.data = data
        self.id: int = data.get('id')
        self.title: str = data.get('title')
        self.major: dict = data.get('major')
        self.image: str = data.get('ogImage')
        self.diration: float = data.get('durationMs', 0)/1000
        self.artists: List[Artist] = [
            Artist(state, artist) for artist in data.get('artists', [])]
        self.artist_names: List[str] = [art.name for art in self.artists]
        self.albums: List[Album] = [Album(state, album)
                                    for album in data.get('albums', [])]

    def get_image(self, size="1080x1080"):
        return f'https://{self.image.replace("%%", size)}'

    def get_url(self):
        album = self.albums[0]
        return f"https://music.yandex.ru/album/{album.id}/track/{self.id}"

    def __repr__(self) -> str:
        return f"<Track title='{self.title}' id={self.id}>"

    def __str__(self) -> str:
        return f"{self.title} - {' ,'.join(self.artist_names)}"

    async def download_link(
        self,
        bitrateInKbps: int = 192
    ) -> str:
        url = await get_download_info(self.id, self._state, bitrateInKbps)
        link = await download_track(self._state, url)
        return link

    async def like(
        self
    ) -> None:
        userid = self._state.userid
        await self._state.http.like_track(userid, [self.id])

    async def dislike(
        self
    ) -> None:
        userid = self._state.userid
        await self._state.http.dislike_track(userid, [self.id])


class LikeTrack:
    def __init__(self, state: ConnectionState, data: dict) -> None:
        self._state = state
        self.data = data
        self.id = data.get('id')
        self.album_id = data.get('albumId')
        self.added_at = datetime.fromisoformat(data.get("timestamp"))

    def __repr__(self) -> str:
        return f"<LikeTrack album_id={self.album_id} id={self.id}>"

    def get_url(self):
        return f"https://music.yandex.ru/album/{self.album_id}/track/{self.id}"

    def download_link(
        self,
        bitrateInKbps: int = 192
    ) -> str:
        return Track.download_link(self, bitrateInKbps)


de_list = {
    'artist': Artist,
    'album': Album,
    'track': Track,
    'playlist': Playlist
}
