from __future__ import annotations
import asyncio
from typing import TYPE_CHECKING, Optional

import aiohttp


if TYPE_CHECKING:
    from .http import HTTPClient
    from .track import Track
    from .user import User
    from .client import Client
else:
    from .util import de_list


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
        self.de_list = de_list

        self._tracks = {}
        self._users = {}
        self.userid = None

    def _identify(self, account_info: dict) -> dict:
        try:
            self.userid = account_info['account']['uid']
        except KeyError:
            pass
        return account_info

    def store_user(self, user: User) -> None:
        self._users[user.id] = user

    def get_user(self, user_id: int) -> Optional[User]:
        return self._users.get(user_id)

    def store_track(self, track: Track) -> Track:
        self._tracks[track.id] = track
        return track

    def get_track(self, id: int) -> Optional[Track]:
        return self._tracks.get(id)
