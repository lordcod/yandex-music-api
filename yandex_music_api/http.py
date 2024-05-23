import asyncio
import time
from types import TracebackType
from typing import Any, ClassVar, Coroutine, Dict, List, Literal, Optional, Self, Type, Union

from urllib.parse import quote

import aiohttp

from yandex_music_api.exceptions import (
    Forbidden, HTTPException, HTTPNotFound, YandexMusicServerError)
from yandex_music_api.types import (AlbumPayload, ArtistBriefInfoPayload, ArtistPayload, ArtistWithAlbumsPayload, ArtistWithTrackPayload, LibraryPlaylistPayload, PlaylistPayload,
                                    PlaylistRecommendationsPayload, SearchPayload, SimilarTracksPayload, SupplementPayload, TrackDownloadinfoPayload, TrackListPayload, TrackPayload)
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
        if isinstance(v, list):
            new_params[k] = ','.join(v)
        if isinstance(v, (str, int, bool)):
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
        self.music_agent = 'YandexMusicAndroid/1011570100'

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
            "X-Yandex-Music-Client": self.music_agent
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
                if isinstance(data, str):
                    return data
                return data['result']

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

    # ? Playlist

    def get_user_playlists(self, user_id: int) -> Coroutine[Any, Any, List[PlaylistPayload]]:
        route = Route(
            "GET", "/users/{user_id}/playlists/list", user_id=user_id)
        return self.request(route)

    def get_playlist(self, user_id: int, kind: int) -> Coroutine[Any, Any, PlaylistPayload]:
        route = Route(
            "GET", "/users/{user_id}/playlists/{kind}", user_id=user_id, kind=kind)
        return self.request(route)

    def get_playlists_from_user(self, user_id: int, kinds: List[int], mixed: bool = False, rich_tracks: bool = False) -> Coroutine[Any, Any, List[PlaylistPayload]]:
        route = Route(
            "GET", "/users/{user_id}/playlists", user_id=user_id)
        params = {
            "kinds": kinds,
            "mixed": mixed,
            "rich-tracks": rich_tracks
        }
        return self.request(route, params=params)

    def create_playlist(self, user_id: int, title: str, visibility: Literal["public", "private"]) -> Coroutine[Any, Any, PlaylistPayload]:
        route = Route(
            'POST', '/users/{user_id}/playlists/create', user_id=user_id)
        data = {
            "title": title,
            "visibility": visibility
        }
        return self.request(route, data=data)

    def delete_playlist(self, user_id: int, kind: int) -> Coroutine[Any, Any, str]:
        route = Route(
            'POST', '/users/{user_id}/playlists/{kind}/delete', user_id=user_id, kind=kind)
        return self.request(route)

    def edit_playlist_name(self, user_id: int, kind: int, title: str) -> Coroutine[Any, Any, PlaylistPayload]:
        route = Route(
            'POST', '/users/{user_id}/playlists/{kind}/name', user_id=user_id, kind=kind)
        data = {"value": title}
        return self.request(route, data=data)

    def edit_playlist_tracks(self, user_id: int, kind: int, diff: dict, revision: int) -> Coroutine[Any, Any, PlaylistPayload]:
        route = Route(
            'POST', '/users/{user_id}/playlists/{kind}/change-relative', user_id=user_id, kind=kind)
        data = {
            "revision": revision,
            "diff": util.to_json(diff)
        }
        print(data)
        return self.request(route, data=data)

    def edit_playlist_visibility(self, user_id: int, kind: int, visibility: Literal["public", "private"]) -> Coroutine[Any, Any, PlaylistPayload]:
        route = Route(
            'POST', '/users/{user_id}/playlists/{kind}/visibility', user_id=user_id, kind=kind)
        data = {"value": visibility}
        return self.request(route, data=data)

    def get_playlist_recommendations(self, user_id: int, kind: int) -> Coroutine[Any, Any, PlaylistRecommendationsPayload]:
        route = Route(
            'GET', '/users/{user_id}/playlists/{kind}/recommendations', user_id=user_id, kind=kind)
        return self.request(route)

    def get_playlists(
        self,
        ids: Union[List[Union[str, int]], int, str],
        with_positions: bool = True
    ) -> Coroutine[Any, Any, List[PlaylistPayload]]:
        params = {'with-positions': with_positions, 'playlist-ids': ids}
        route = Route("GET", "/playlists/list")
        return self.request(route, params=params)

    # ? Like/Dislike

    def get_likes_tracks(self, userid: int) -> Coroutine[Any, Any, LibraryPlaylistPayload]:
        route = Route(
            "GET", "/users/{userid}/likes/tracks", userid=userid)

        return self.request(route)

    def get_dislikes_tracks(self, userid: int) -> Coroutine[Any, Any, LibraryPlaylistPayload]:
        route = Route(
            "GET", "/users/{userid}/dislikes/tracks", userid=userid)

        return self.request(route)

    def like_track(
        self,
        userid: int,
        tracks_ids: List[Union[str, int]]
    ) -> Coroutine[Any, Any, None]:
        route = Route(
            "POST", "/users/{userid}/likes/tracks/add-multiple", userid=userid)
        data = {"track-ids": tracks_ids}
        return self.request(route, data=data)

    def dislike_track(
        self,
        userid: int,
        tracks_ids: List[Union[str, int]]
    ) -> Coroutine[Any, Any, None]:
        route = Route(
            "POST", "/users/{userid}/likes/tracks/remove", userid=userid)
        data = {"track-ids": tracks_ids}
        return self.request(route, data=data)

    # ? Tracks
    def get_tracks(
        self,
        ids: Union[List[Union[str, int]], int, str],
        with_positions: bool = True
    ) -> Coroutine[Any, Any, List[TrackPayload]]:
        params = {'with-positions': with_positions, 'track-ids': ids}
        route = Route("GET", "/tracks")
        return self.request(route, params=params)

    def get_download_info(self, track_id: int) -> Coroutine[Any, Any, List[TrackDownloadinfoPayload]]:
        route = Route(
            'GET', f'/tracks/{track_id}/download-info', track_id=track_id)
        return self.request(route)

    def get_track_additionally_info(self, track_id: int) -> Coroutine[Any, Any, SupplementPayload]:
        route = Route(
            'GET', f'/tracks/{track_id}/supplement', track_id=track_id)
        return self.request(route)

    def get_similar_track(self, track_id: int) -> Coroutine[Any, Any, SimilarTracksPayload]:
        route = Route(
            'GET', f'/tracks/{track_id}/similar', track_id=track_id)
        return self.request(route)

    def get_track_lyrics(self, track_id: int, timestamp: int, sign: str):
        route = Route(
            'GET', f'/tracks/{track_id}/lyrics', track_id=track_id)
        params = {
            'timeStamp': timestamp,
            'sign': sign
        }
        return self.request(route, params=params)

    # ? Albums

    def get_album(self, album_id: int) -> Coroutine[Any, Any, AlbumPayload]:
        route = Route(
            'GET', '/albums/{album_id}', album_id=album_id)
        return self.request(route)

    def get_album_with_tracks(self, album_id: int) -> Coroutine[Any, Any, AlbumPayload]:
        route = Route(
            'GET', '/albums/{album_id}/with-tracks', album_id=album_id)
        return self.request(route)

    def get_albums(
        self,
        ids: Union[List[Union[str, int]], int, str],
        with_positions: bool = True
    ) -> Coroutine[Any, Any, List[AlbumPayload]]:
        params = {'with-positions': with_positions, 'album-ids': ids}
        route = Route("GET", "/albums")
        return self.request(route, params=params)

    # ? Artists

    def get_artists(
        self,
        ids: Union[List[Union[str, int]], int, str],
        with_positions: bool = True
    ) -> Coroutine[Any, Any, List[ArtistPayload]]:
        params = {'with-positions': with_positions, 'artist-ids': ids}
        route = Route("GET", "/artists")
        return self.request(route, params=params)

    def get_artist_track_ids(self, artist_id: int) -> Coroutine[Any, Any, ArtistPayload]:
        route = Route(
            "GET", "/artists/{artist_id}/track-ids-by-rating", artist_id=artist_id)
        return self.request(route)

    def get_artist_brief_info(self, artist_id: int) -> Coroutine[Any, Any, ArtistBriefInfoPayload]:
        route = Route(
            "GET", "/artists/{artist_id}/brief-info", artist_id=artist_id)
        return self.request(route)

    def get_artist_tracks(self, artist_id: int, page: int = 0, page_size: int = 20) -> Coroutine[Any, Any, ArtistWithTrackPayload]:
        route = Route(
            "GET", "/artists/{artist_id}/tracks", artist_id=artist_id)
        params = {
            'page': page,
            'page-size': page_size
        }
        return self.request(route, params=params)

    def get_artist_direct_albums(self, artist_id: int, page: int = 0, page_size: int = 20, sort_by: Literal['year', 'rating'] = 'rating') -> Coroutine[Any, Any, ArtistWithAlbumsPayload]:
        route = Route(
            "GET", "/artists/{artist_id}/direct-albums", artist_id=artist_id)
        params = {
            'page': page,
            'page-size': page_size,
            'sort-by': sort_by
        }
        return self.request(route, params=params)

    # ? Ofter

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
    ) -> Coroutine[Any, Any, SearchPayload]:
        route = Route("GET", "/search")
        params = {
            'text': text,
            'nocorrect': nocorrect,
            'type': object_type,
            'page': page
        }
        return self.request(route, params=params)

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
