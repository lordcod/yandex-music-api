from __future__ import annotations
import asyncio
from typing import TYPE_CHECKING, Optional

import aiohttp


if TYPE_CHECKING:
    from .http import HTTPClient
    from yandex_music_api.datas import Track
    from yandex_music_api.client import Client


class ConnectionState:
    def __init__(
        self,
        session: aiohttp.ClientSession,
        httpclient: HTTPClient,
        loop: asyncio.AbstractEventLoop,
        token: Optional[str],
        client: Client
    ) -> None:
        self.http = httpclient
        self.session = session
        self.loop = loop
        self.token = token
        self.client = client

        self._tracks = {}
        self.userid = None

    def _create_user(self, account_info: dict) -> dict:
        try:
            self.userid = account_info['result']['account']['uid']
        except KeyError:
            pass
        return account_info

    def store_track(self, track: Track) -> None:
        self._tracks[track.id] = track

    def get_track(self, id: int) -> Optional[Track]:
        return self._tracks.get(id)
