from .coonector import Requsts
from hashlib import md5
import xmltodict
from typing import List

SIGN_SALT = 'XGRlBW9FXlekgbPrRHuSiA'


class Artist:
    def __init__(self, requests: Requsts, data: dict) -> None:
        self.requests = requests
        self.data = data
        self.id: int = data.get('id')
        self.name: str = data.get('name')
        self.cover: dict = data.get('cover')
        self.avatar: str = self.cover and self.cover.get('uri')


class Playlist:
    def __init__(self, requests: Requsts, data: dict) -> None:
        self.requests = requests
        self.data = data
        self.owner: dict = data.get('owner')
        self.id: int = data.get('uid')
        self.kind = data.get('kind')
        self.title = data.get('title')
        self.description = data.get('description')
        self.tags = data.get('tags')


class Album:
    def __init__(self, requests: Requsts, data: dict) -> None:
        self.requests = requests
        self.data = data
        self.id: int = data.get('id')
        self.title: str = data.get('title')
        self.type: str = data.get('metaType')
        self.year: int = data.get('year')
        self.release_date: str = data.get('releaseDate')
        self.image: str = data.get('ogImage')
        self.artists: List[Artist] = [
            Artist(requests, artist) for artist in data.get('artists', [])]
        self.labels: dict = data.get('labels')
    
    
    async def get_tracks(self) -> List['Track']:
        json = await self.requests.read_json(f"{self.requests.base_url}/albums/{self.id}/with-tracks")
        tracks = json["result"]["volumes"]
        return [Track(self.requests, track_data) for datas in tracks for track_data in datas]


class Track:
    def __init__(self, requests: Requsts, data: dict) -> None:
        self.requests = requests
        self.data = data
        self.id: int = data.get('id')
        self.title: str = data.get('title')
        self.major: dict = data.get('major')
        self.image: str = data.get('ogImage')
        self.diration: float = data.get('durationMs', 0)/1000
        self.artists: List[Artist] = [
            Artist(requests, artist) for artist in data.get('artists', [])]
        self.artist_names: List[str] = [art.name for art in self.artists]
        self.albums: List[Album] = [Album(requests, album)
                                    for album in data.get('albums', [])]

    def get_image(self, size="1080x1080"):
        return f'https://{self.image.replace("%%", size)}'

    def get_url(self):
        album = self.albums[0]
        return f"https://music.yandex.ru/album/{album.id}/track/{self.id}"

    def __str__(self) -> str:
        return f"{self.title} - {' ,'.join(self.artist_names)}"

    def decode_download_info(self, xmldata: str) -> None:
        data = xmltodict.parse(xmldata)['download-info']
        host = data.get('host')
        ts = data.get('ts')
        path = data.get('path')
        s = data.get('s')
        sign = md5((SIGN_SALT + path[1::] + s).encode('utf-8')).hexdigest()

        return f'https://{host}/get-mp3/{sign}/{ts}{path}'

    async def download_info(
        self,
        bitrateInKbps: int = 192
    ) -> str:
        json = await self.requests.read_json(f'{self.requests.base_url}/tracks/{self.id}/download-info')
        results = json.get('result', [])
        for res in results:
            if res['bitrateInKbps'] == bitrateInKbps:
                diu = res['downloadInfoUrl']
                return diu
        else:
            raise Exception('bitrateInKbps error')

    async def download_track(
        self, 
        downloadInfoUrl: str
    ) -> str:
        data = await self.requests.read(downloadInfoUrl)
        link = self.decode_download_info(data)
        return link
    
    async def download_link(
        self,
        bitrateInKbps: int = 192
    ) -> str:
        url = await self.download_info(bitrateInKbps)
        link = await self.download_track(url)
        return link


de_list = {
    'artist': Artist,
    'album': Album,
    'track': Track,
    'playlist': Playlist
}