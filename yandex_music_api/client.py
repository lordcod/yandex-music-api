import asyncio
import aiohttp
from yandex_music_api.http import HTTPClient
from yandex_music_api.state import ConnectionState
from .datas import Album, Artist, Track, Playlist, de_list, LikeTrack
from typing import Optional, List, Union, Literal
from functools import lru_cache


class Client:
    def __init__(
        self,
        token: str
    ) -> None:
        session = aiohttp.ClientSession()
        loop = asyncio.get_event_loop()
        http = HTTPClient(session=session, loop=loop)
        http.token = token
        self._state = ConnectionState(
            session=session, httpclient=http, loop=loop, token=token, client=self)
        self.token = token
        self.userid = None

    async def account_info(self):
        return self._state.create_user(await self._state.http.get_account_info())

    async def search(
        self,
        text: str,
        object_type: str = 'track',
        with_only_result: bool = False
    ) -> Union[List[Union[Artist, Album, Track, Playlist]],
               Artist, Album, Track, Playlist]:
        json = await self._state.http.search(text=text, object_type=object_type)
        ostype = object_type+'s' if object_type != 'best' else object_type
        if object_type == 'best':
            return de_list[json['result']['best']['type']](self._state, json['result']['best']['result'])
        results = [de_list[object_type](self._state, res)
                   for res in json['result'][ostype]['results']]

        if with_only_result:
            return None if not results else results[0]
        return results

    async def get_list(
        self,
        ids: Union[List[Union[str, int]], int, str],
        object_type: Literal['track', 'album', 'playlist', 'artist'],
        with_only_result: bool = False
    ) -> Union[Artist, Album, Track, Playlist, List[Union[Artist, Album, Track, Playlist]]]:
        object_requests = {
            'track': self._state.http.get_tracks,
            'album': self._state.http.get_albums,
            'playlist': self._state.http.get_playlists,
            'artist': self._state.http.get_artists
        }

        data = await object_requests[object_type](ids)
        results = [de_list[object_type](self._state, obj)
                   for obj in data.get('result', [])]

        if with_only_result:
            return None if not results else results[0]
        return results

    async def get_likes_tracks(self) -> List[LikeTrack]:
        userid = self._state.userid

        responce = await self._state.http.get_likes_tracks(userid)
        tracks_data = responce["result"]["library"]["tracks"]

        return [LikeTrack(self._state, ltrd) for ltrd in tracks_data]
