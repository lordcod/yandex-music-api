from __future__ import annotations
import contextlib
from typing import TYPE_CHECKING, List

from yandex_music_api.types import PlaylistPayload

if TYPE_CHECKING:
    from yandex_music_api.state import ConnectionState
    from yandex_music_api.track import Track
    from yandex_music_api.util import Difference, VisibilityType


class Playlist:
    def __init__(self, state: ConnectionState, data: PlaylistPayload) -> None:
        self._state = state
        self.data = data
        self.revision = data.get('revision', 0)
        self.owner = data.get('owner')
        self.id = data.get('uid')
        self.kind = data.get('kind')
        self.title = data.get('title')
        self.description = data.get('description')
        self.tags = data.get('tags')
        self.track_count = data['trackCount']

    @property
    def tracks(self) -> List[Track]:
        ret = []
        for track_item in self.data.get('tracks'):
            with contextlib.suppress(KeyError):
                track = self._state.de_list['track'](
                    self._state, track_item.get('track'))
                ret.append(track)
        return ret

    async def delete(self) -> None:
        await self._state.http.delete_playlist(self.id, self.kind)

    async def edit_tracks(self, diff: Difference) -> None:
        await self._state.http.edit_playlist_tracks(self.id, self.kind, diff.payload, self.revision)

    async def edit_name(self, title: str) -> None:
        await self._state.http.edit_playlist_name(self.id, self.kind, title)

    async def edit_visibility(self, visibility: VisibilityType):
        await self._state.http.edit_playlist_visibility(self.id, self.kind, visibility)

    async def get_recomendation(self) -> Track:
        recmd = await self._state.http.get_playlist_recommendations(self.id, self.kind)
        return [self._state.de_list['track'](self._state, data) for data in recmd['tracks']]

    def __repr__(self) -> str:
        return f"<Playlist title='{self.title}' kind={self.kind} trackCount={self.track_count}>"

    def __str__(self) -> str:
        return repr(self)
