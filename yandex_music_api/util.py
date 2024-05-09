from .coonector import Requests
from hashlib import md5
import xmltodict

SIGN_SALT = 'XGRlBW9FXlekgbPrRHuSiA'


def decode_download_info(xmldata: str) -> str:
    data = xmltodict.parse(xmldata)['download-info']
    host = data.get('host')
    ts = data.get('ts')
    path = data.get('path')
    s = data.get('s')
    sign = md5((SIGN_SALT + path[1::] + s).encode('utf-8')).hexdigest()

    return f'https://{host}/get-mp3/{sign}/{ts}{path}'


async def get_download_info(
    track_id: int,
    requests: Requests,
    bitrateInKbps: int = 192
) -> str:
    json = await requests.read_json(f'{requests.base_url}/tracks/{track_id}/download-info')
    results = json.get('result', [])
    for res in results:
        if res['bitrateInKbps'] == bitrateInKbps:
            diu = res['downloadInfoUrl']
            return diu
    else:
        raise Exception('bitrateInKbps error')


async def download_track(
    requests: Requests,
    downloadInfoUrl: str
) -> str:
    data = await requests.read(downloadInfoUrl)
    link = decode_download_info(data)
    return link
