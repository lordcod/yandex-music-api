from __future__ import annotations
from typing import TYPE_CHECKING

from yandex_music_api.types import PlaylistPayload

if TYPE_CHECKING:
    from yandex_music_api.state import ConnectionState


class Playlist:
    def __init__(self, state: ConnectionState, data: PlaylistPayload) -> None:
        self._state = state
        self.data = data
        self.owner: dict = data.get('owner')
        self.id: int = data.get('uid')
        self.kind = data.get('kind')
        self.title = data.get('title')
        self.description = data.get('description')
        self.tags = data.get('tags')
