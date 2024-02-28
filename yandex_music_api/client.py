from .coonector import Requsts
from .datas import Album, Artist, Track, Playlist, de_list
from typing import Optional, List, Union, Literal




class Client:
    def __init__(
        self, 
        token: str,
        requests: Optional[Requsts] = None
    ) -> None:
        self.token = token
        self.requests = requests or Requsts()
        
        self.requests.set_authorization(token)
        self.base_url = "https://api.music.yandex.net"
    
    
    
    async def account_info(self):
        return await self.requests.read_json(f"{self.base_url}/account/status")
    
    
    async def search(
        self,
        text: str,
        object_type: str = 'track',
    ) -> Union[List[Union[Artist, Album, Track, Playlist]],
               Artist, Album, Track, Playlist]:
        params = {
            'text': text,
            'nocorrect': 'False',
            'type': 'all',
            'page': '0',
            'playlist-in-best': 'True'
        }
        json = self.requests.read_json(f'{self.base_url}/search', params=params)
        ostype = object_type+'s' if object_type != 'best' else object_type
        if object_type == 'best':
            return de_list[json['result']['best']['type']](self.requests, json['result']['best']['result'])
        return [de_list[object_type](self.requests, res)
                for res in json['result'][ostype]['results']]

    async def get_list(
        self,
        ids: Union[List[Union[str, int]], int, str],
        object_type: Literal['track', 'album', 'playlist', 'artist']
    ) -> List[Union[Artist, Album, Track, Playlist]]:
        params = {'with-positions': 'True', f'{object_type}-ids': ids}

        url = f"{self.base_url}/{object_type}s{'/list' if object_type == 'playlist' else ''}"

        data = await self.requests.read_json(url, params=params)
        res = [de_list[object_type](self.requests, obj) for obj in data.get('result', [])]
        return res