import asyncio
from types import TracebackType
from typing import Any, ClassVar, Dict, List, Literal, Optional, Self, Type, Union

from urllib.parse import quote

import aiohttp

from yandex_music_api.exceptions import (
    Forbidden, HTTPException, HTTPNotFound, YandexMusicServerError)
from . import util


async def json_or_text(response: aiohttp.ClientResponse) -> Union[Dict[str, Any], str]:
    text = await response.text(encoding="utf-8")
    try:
        if response.headers["content-type"] == "application/json;charset=utf-8":
            return util.from_json(text)
    except KeyError:
        # Thanks Cloudflare
        pass

    return text


def parse_params(params: dict):
    new_params = {}
    for k, v in params.items():
        if not isinstance(v, (str, int, bool)):
            raise TypeError
        new_params[k] = str(v).lower()
    return new_params


class Route:
    BASE: ClassVar[str] = "https://api.music.yandex.net"

    def __init__(self, method: str, path: str, **parameters: Any) -> None:
        self.path: str = path
        self.method: str = method
        url = self.BASE + self.path
        if parameters:
            url = url.format_map(
                {k: quote(v) if isinstance(v, str)
                 else v for k, v in parameters.items()}
            )
        self.url: str = url


class MaybeUnlock:
    def __init__(self, lock: asyncio.Lock) -> None:
        self.lock: asyncio.Lock = lock
        self._unlock: bool = True

    def __enter__(self) -> Self:
        return self

    def defer(self) -> None:
        self._unlock = False

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None:
        if self._unlock:
            self.lock.release()


class HTTPClient:
    token: Optional[str] = None

    def __init__(
        self,
        session: aiohttp.ClientSession,
        loop: asyncio.AbstractEventLoop
    ) -> None:
        self.__session = session
        self.loop = loop
        self._locks: Dict[str, asyncio.AbstractEventLoop] = {}
        self.user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 YaBrowser/24.4.0.0 Safari/537.36'

    async def request(
        self,
        route: Route,
        **kwargs: Any
    ):
        method = route.method
        url = route.url

        # header creation
        headers: Dict[str, str] = {
            "User-Agent": self.user_agent,
        }

        if self.token is not None:
            headers["Authorization"] = "OAuth " + self.token

        if "json" in kwargs:
            headers["Content-Type"] = "application/json"
            kwargs["data"] = util.to_json(kwargs.pop("json"))

        if "params" in kwargs:
            kwargs["params"] = parse_params(kwargs["params"])

        kwargs["headers"] = headers

        response: Optional[aiohttp.ClientResponse] = None
        data: Optional[Union[Dict[str, Any], str]] = None

        async with self.__session.request(method, url, **kwargs) as response:
            data = await json_or_text(response)

            if 300 > response.status >= 200:
                return data

            # we are being rate limited
            if response.status == 429:
                if not response.headers.get("Via") or isinstance(data, str):
                    # Banned by Cloudflare more than likely.
                    raise HTTPException(response, data)

            # the usual error cases
            if response.status == 403:
                raise Forbidden(response, data)
            elif response.status == 404:
                raise HTTPNotFound(response, data)
            elif response.status >= 500:
                raise YandexMusicServerError(response, data)
            else:
                raise HTTPException(response, data)

    def get_account_info(self):
        route = Route("GET", "/account/status")
        return self.request(route)

    def search(
        self,
        text: str,
        object_type: Literal['track', 'album',
                             'artist', 'podcast', 'all'] = 'all',
        page: int = 0,
        nocorrect: bool = False
    ):
        route = Route("GET", "/search")
        params = {
            'text': text,
            'nocorrect': nocorrect,
            'type': object_type,
            'page': page
        }
        return self.request(route, params=params)

    def get_tracks(
        self,
        ids: Union[List[Union[str, int]], int, str],
        with_positions: bool = True
    ):
        params = {'with-positions': with_positions, 'track-ids': ids}
        route = Route("GET", "/tracks")
        return self.request(route, params=params)

    def get_albums(
        self,
        ids: Union[List[Union[str, int]], int, str],
        with_positions: bool = True
    ):
        params = {'with-positions': with_positions, 'album-ids': ids}
        route = Route("GET", "/albums")
        return self.request(route, params=params)

    def get_artists(
        self,
        ids: Union[List[Union[str, int]], int, str],
        with_positions: bool = True
    ):
        params = {'with-positions': with_positions, 'artist-ids': ids}
        route = Route("GET", "/artists")
        return self.request(route, params=params)

    def get_playlists(
        self,
        ids: Union[List[Union[str, int]], int, str],
        with_positions: bool = True
    ):
        params = {'with-positions': with_positions, 'playlists-ids': ids}
        route = Route("GET", "/playlists/list")
        return self.request(route, params=params)

    def like_track(
        self,
        userid: int,
        tracks_ids: List[Union[str, int]]
    ):
        route = Route(
            "POST", "/users/{userid}/likes/tracks/add-multiple", userid=userid)
        data = {"track-ids": tracks_ids}
        return self.request(route, data=data)

    def dislike_track(
        self,
        userid: int,
        tracks_ids: List[Union[str, int]]
    ):
        route = Route(
            "POST", "/users/{userid}/likes/tracks/remove", userid=userid)
        data = {"track-ids": tracks_ids}
        return self.request(route, data=data)

    def get_likes_tracks(self, userid: int):
        route = Route(
            "GET", "/users/{userid}/likes/tracks", userid=userid)

        return self.request(route)

    def get_download_info(self, track_id: int):
        route = Route(
            'GET', f'/tracks/{track_id}/download-info', track_id=track_id)
        return self.request(route)

    def get_tracks_with_album(self, album_id: int):
        route = Route(
            'GET', '/albums/{album_id}/with-tracks', album_id=album_id)
        return self.request(route)

    async def get_from_downloadinfo(self, url: str) -> bytes:
        async with self.__session.get(url) as resp:
            if resp.status == 200:
                return await resp.read()
            elif resp.status == 404:
                raise HTTPNotFound(resp, "download info not found")
            elif resp.status == 403:
                raise Forbidden(resp, "cannot retrieve download info")
            else:
                raise HTTPException(resp, "failed to get download info")
