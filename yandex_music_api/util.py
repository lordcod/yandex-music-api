
from typing import Any, Union

from yandex_music_api.album import Album
from yandex_music_api.artist import Artist
from yandex_music_api.playlist import Playlist
from yandex_music_api.track import Track


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

de_list = {
    'artist': Artist,
    'album': Album,
    'track': Track,
    'playlist': Playlist
}
