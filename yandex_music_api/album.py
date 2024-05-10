from __future__ import annotations
from datetime import datetime

from typing import TYPE_CHECKING, List

from yandex_music_api.types import AlbumPayload

if TYPE_CHECKING:
    from yandex_music_api.state import ConnectionState
    from yandex_music_api.artist import Artist
    from yandex_music_api.track import Track


class Album:
    def __init__(self, state: ConnectionState, data: AlbumPayload) -> None:
        self._state = state
        self.id: int = int(data['id'])
        self.title: str = data['title']
        self.type: str = data['metaType']
        self.year: int = data.get('year')
        self.image: str = data['ogImage']
        self.track_count: int = int(data['trackCount'])
        self.artists: List[Artist] = [
            state.de_list['artist'](state, artist) for artist in data['artists']]
        self.best_track_ids = list(map(int, data['bests']))
        if release_date := data.get('releaseDate'):
            self.release_date: datetime = datetime.fromisoformat(release_date)

    async def get_tracks(self) -> List[Track]:
        json = await self._state.http.get_tracks_with_album(self.id)
        tracks = json["volumes"]
        return [self._state.de_list['track'](self._state, track_data) for datas in tracks for track_data in datas]
