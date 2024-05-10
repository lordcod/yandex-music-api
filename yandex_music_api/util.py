
from typing import Any, Union
from hashlib import md5
import xmltodict

from yandex_music_api.state import ConnectionState

SIGN_SALT = 'XGRlBW9FXlekgbPrRHuSiA'

try:
    import orjson
except ImportError:
    import json

    def to_json(data: Any):
        return json.dumps(data)

    def from_json(data: Union[str, bytes, bytearray]):
        return json.loads(data)
else:
    def to_json(data: Any):
        return orjson.dumps(data).decode()

    def from_json(data: Union[str, bytes, bytearray, memoryview]):
        return orjson.loads(data)


def decode_download_info(xmldata: str) -> str:
    data = xmltodict.parse(xmldata)['download-info']
    host = data['host']
    ts = data['ts']
    path = data['path']
    s = data['s']
    sign = md5((SIGN_SALT + path[1::] + s).encode('utf-8')).hexdigest()

    return f'https://{host}/get-mp3/{sign}/{ts}{path}'


async def get_download_info(
    track_id: int,
    state: ConnectionState,
    bitrateInKbps: int = 192
) -> str:
    json = state.http.get_download_info(track_id)
    results = json.get('result', [])
    for res in results:
        if res['bitrateInKbps'] == bitrateInKbps:
            diu = res['downloadInfoUrl']
            return diu
    else:
        raise Exception('bitrateInKbps error')


async def download_track(
    state: ConnectionState,
    downloadInfoUrl: str
) -> str:
    data = await state.http.get_from_downloadinfo(downloadInfoUrl)
    link = decode_download_info(data)
    return link
