import aiohttp
import orjson
from aiohttp.client import ClientResponse
from typing import Optional, Mapping, Any, Coroutine

class Requsts:
    def __init__(self, session: Optional[aiohttp.ClientSession] = None) -> None:
        self.headers = {}
        self.session = session
        self.base_url = "https://api.music.yandex.net"
    
    async def request(
        self,
        method: str,
        url: str,
        *,
        params: Optional[Mapping[str, str]] = None,
        data: Any = None,
        json: Any = None,
        cookies: Optional[Mapping[str, str]] = None,
        headers: Optional[Mapping[str, str]] = None,
    ) -> Coroutine[Any, Any, ClientResponse]:
        headers = self.get_headers(headers)
        if self.session is None:
            async with aiohttp.ClientSession() as session:
                responce = await session.request(
                    method=method, 
                    url=url, 
                    params=params, 
                    data=data, 
                    json=json, 
                    cookies=cookies, 
                    headers=headers
                )
        else:
            responce = await self.session.request(
                method=method, 
                url=url, 
                params=params, 
                data=data, 
                json=json, 
                cookies=cookies, 
                headers=headers
            )
        return responce

    def get(
        self, 
        url: str, 
        **kwargs
    ) -> Coroutine[Any, Any, ClientResponse]:
        method = "GET"
        return self.request(method, url, **kwargs)
    
    def post(
        self, 
        url: str, 
        **kwargs
    ) -> Coroutine[Any, Any, ClientResponse]:
        method = "POST"
        return self.request(method, url, **kwargs)
    
    def de_json(self, responce: ClientResponse):
        return responce.json(loads=orjson.loads)
    
    def set_authorization(self, token: str) -> None:
        self.headers.update({'Authorization': f'OAuth {token}'})

    def get_headers(
        self, 
        headers: Optional[Mapping[str, str]] = None
    ) -> Mapping[str, str]:
        if headers is None:
            return self.headers
        return headers.update(self.headers)