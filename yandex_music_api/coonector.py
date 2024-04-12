import aiohttp
import orjson
from aiohttp.client import ClientResponse
from typing import Optional, Mapping, Any, Coroutine


class Requests:
    def __init__(self, session: Optional[aiohttp.ClientSession] = None) -> None:
        self.headers = {}
        self.base_url = "https://api.music.yandex.net"
        self.session = session

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
    ) -> ClientResponse:
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
        responce.raise_for_status()
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

    def de_json(self, responce: ClientResponse) -> Optional[dict]:
        return responce.json(loads=orjson.loads)

    async def read(
        self,
        url: str,
        *,
        method: str = "GET",
        **kwargs
    ) -> str:
        response = await self.request(method, url, **kwargs)
        data_bytes = await response.read()
        text = data_bytes.decode()
        await self.close_res(response)
        return text

    async def read_json(
        self,
        url: str,
        *,
        method: str = "GET",
        **kwargs
    ) -> dict:
        response = await self.request(method, url, **kwargs)
        data = await self.de_json(response)
        await self.close_res(response)
        return data

    def close_res(self, responce: ClientResponse) -> Coroutine[Any, Any, None]:
        responce.release()
        return responce.wait_for_close()

    def set_authorization(self, token: str) -> None:
        self.headers.update({'Authorization': f'OAuth {token}'})

    def get_headers(
        self,
        headers: Optional[Mapping[str, str]] = None
    ) -> Mapping[str, str]:
        if headers is None:
            return self.headers
        return headers.update(self.headers)
