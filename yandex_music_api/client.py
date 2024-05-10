import asyncio
import aiohttp

from yandex_music_api.artist import Artist
from yandex_music_api.album import Album
from yandex_music_api.playlist import Playlist
from yandex_music_api.track import ShortTrack, Track
from yandex_music_api.http import HTTPClient
from yandex_music_api.state import ConnectionState

from typing import List, Union, Literal


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

    async def identify(self):
        return self._state._identify(await self._state.http.get_account_info())

    async def search(
        self,
        text: str,
        object_type: str = 'track',
        with_only_result: bool = False
    ) -> Union[List[Union[Artist, Album, Track, Playlist]],
               Artist, Album, Track, Playlist]:
        json = await self._state.http.search(text=text, object_type=object_type)
        objtype = object_type+'s' if object_type != 'best' else object_type
        if object_type == 'best':
            return self._state.de_list[json['best']['type']](self._state, json['best'])
        results = [self._state.de_list[object_type](self._state, res)
                   for res in json[objtype]['results']]

        if with_only_result:
            return None if not results else results[0]
        return results

    async def get_playlists(
        self,
        playlist_ids: Union[List[Union[str, int]], int, str],
        with_positions: bool = True,
        with_only_result: bool = False
    ) -> Union[Playlist, List[Playlist]]:
        data = await self._state.http.get_playlists(
            playlist_ids,
            with_positions
        )
        results = [Playlist(self._state, playlist_data)
                   for playlist_data in data]

        if with_only_result:
            return None if not results else results[0]
        return results

    async def get_artists(
        self,
        artists_ids: Union[List[Union[str, int]], int, str],
        with_positions: bool = True,
        with_only_result: bool = False
    ) -> Union[Artist, List[Artist]]:
        data = await self._state.http.get_artists(
            artists_ids,
            with_positions
        )
        results = [Artist(self._state, playlist_data)
                   for playlist_data in data]

        if with_only_result:
            return None if not results else results[0]
        return results

    async def get_album(
        self,
        album_ids: Union[List[Union[str, int]], int, str],
        with_positions: bool = True,
        with_only_result: bool = False
    ) -> Union[Album, List[Album]]:
        data = await self._state.http.get_albums(
            album_ids,
            with_positions
        )
        results = [Album(self._state, album_data)
                   for album_data in data]

        if with_only_result:
            return None if not results else results[0]
        return results

    async def get_track(
        self,
        track_ids: Union[List[Union[str, int]], int, str],
        with_positions: bool = True,
        with_only_result: bool = False
    ) -> Union[Track, List[Track]]:
        data = await self._state.http.get_tracks(
            track_ids,
            with_positions
        )
        results = [Track(self._state, track_data)
                   for track_data in data]

        if with_only_result:
            return None if not results else results[0]
        return results

    async def get_likes_tracks(self) -> List[ShortTrack]:
        userid = self._state.userid

        responce = await self._state.http.get_likes_tracks(userid)
        tracks_data = responce["library"]["tracks"]

        return [ShortTrack(self._state, ltrd) for ltrd in tracks_data]

    async def get_dislikes_tracks(self) -> List[ShortTrack]:
        userid = self._state.userid

        responce = await self._state.http.get_dislikes_tracks(userid)
        tracks_data = responce['library']['tracks']

        return [ShortTrack(self._state, ltrd) for ltrd in tracks_data]
