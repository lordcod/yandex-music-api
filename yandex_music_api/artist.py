from __future__ import annotations

from typing import TYPE_CHECKING, List

from yandex_music_api.types import ArtistPayload

if TYPE_CHECKING:
    from yandex_music_api.state import ConnectionState
    from yandex_music_api.track import Track


class Artist:
    def __init__(self, state: ConnectionState, data: ArtistPayload) -> None:
        self._state = state
        self.id: int = int(data['id'])
        self.name: str = data['name']
        self.various: bool = data['various']
        self.popular_track: List[Track] = [state.de_list['track'](
            state, trc_data) for addtionally in data.get('popularTracks', []) for trc_data in addtionally]

    async def get_rating_tracks(self) -> List[Track]:
        responce = await self._state.http.get_artist_tracks(self.id)
        self.__init__(self._state, responce['artist'])
        tracks = responce["tracks"]

        return [self._state.store_track(self._state.de_list['track'](self._state, data)) for data in tracks]

    async def get_direct_albums(self) -> List[Track]:
        responce = await self._state.http.get_artist_direct_albums(self.id)
        albums = responce['albums']

        return [self._state.store_track(self._state.de_list['album'](self._state, data)) for data in albums]
