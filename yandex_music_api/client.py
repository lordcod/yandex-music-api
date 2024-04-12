from .coonector import Requests
from .datas import Album, Artist, Track, Playlist, de_list, LikeTrack
from typing import Optional, List, Union, Literal, overload
from functools import lru_cache



class Client:
    def __init__(
        self,
        token: str,
        requests: Optional[Requests] = None
    ) -> None:
        self.token = token
        self.requests = requests or Requests()
        self.userid = None

        self.requests.set_authorization(token)
        self.base_url = self.requests.base_url

    def account_info(self):
        return self.requests.read_json(f"{self.base_url}/account/status")

    @lru_cache()
    async def get_uid(self):
        if self.userid is None:
            try:
                self.userid = (await self.account_info())['result']['account']['uid']
            except KeyError:
                return
        else:
            return self.userid


    async def search(
        self,
        text: str,
        object_type: str = 'track',
        with_only_result: bool = False
    ) -> Union[List[Union[Artist, Album, Track, Playlist]],
               Artist, Album, Track, Playlist]:
        params = {
            'text': text,
            'nocorrect': 'False',
            'type': 'all',
            'page': '0',
            'playlist-in-best': 'True'
        }
        json = await self.requests.read_json(f'{self.base_url}/search', params=params)
        ostype = object_type+'s' if object_type != 'best' else object_type
        if object_type == 'best':
            return de_list[json['result']['best']['type']](self.requests, json['result']['best']['result'])
        results = [de_list[object_type](self.requests, res)
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
        params = {'with-positions': 'True', f'{object_type}-ids': ids}

        url = f"{self.base_url}/{object_type}s{'/list' if object_type == 'playlist' else ''}"

        data = await self.requests.read_json(url, params=params)
        results = [de_list[object_type](self.requests, obj)
                   for obj in data.get('result', [])]

        if with_only_result:
            return None if not results else results[0]
        return results

    async def like_track(self, tracks: Union[Track, List[Track]]) -> None:
        userid = await self.get_uid()
        tracks = tracks if isinstance(tracks, (list, tuple, set)) else [tracks]

        url = f"{self.base_url}/users/{userid}/likes/tracks/add-multiple"
        data = {"track-ids": [track.id for track in tracks]}

        await self.requests.post(url, data=data)

    async def dislike_track(self, tracks: Union[Track, List[Track]]) -> None:
        userid = await self.get_uid()
        tracks = tracks if hasattr(tracks, '__iter__', None) is not None else [tracks]

        url = f"{self.base_url}/users/{userid}/likes/tracks/remove"
        data = {"track-ids": [track.id for track in tracks]}

        responce = await self.requests.post(url, data=data)
        await self.requests.close_res(responce)

    async def get_likes_tracks(self) -> List[LikeTrack]:
        userid = await self.get_uid()

        url = f"{self.base_url}/users/{userid}/likes/tracks"
        responce = await self.requests.read_json(url)
        tracks_data = responce["result"]["library"]["tracks"]

        return [LikeTrack(self.requests, ltrd) for ltrd in tracks_data]
