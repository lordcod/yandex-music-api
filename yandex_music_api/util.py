
from enum import StrEnum
from typing import Any, List, Optional, Self, Union

from yandex_music_api.album import Album
from yandex_music_api.artist import Artist
from yandex_music_api.playlist import Playlist
from yandex_music_api.track import ShortTrack, Track
from yandex_music_api.types import DiffPayload


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


class OperationType(StrEnum):
    INSERT = 'insert'
    DELETE = 'delete'


class Difference:
    def __init__(self, payload: dict) -> None:
        self.payload = payload

    @classmethod
    def delete(
        cls,
        __from: int,
        __to: Optional[int] = None
    ) -> 'Difference':
        if __to is None:
            __to = __from+1

        operation = {
            'diff': {
                'op': OperationType.DELETE,
                'from': __from,
                'to': __to
            }
        }
        return cls(operation)

    @classmethod
    def insert(
        cls,
        tracks: Union[Track, ShortTrack, str, dict, List[Union[Track, ShortTrack, str, dict]]],
        index: int = 0
    ) -> 'Difference':
        if not isinstance(tracks, list):
            tracks = [tracks]

        tracks_data = []
        for trc in tracks:
            if isinstance(trc, Track):
                tracks_data.append({'id': trc.id, 'albumId': trc.album.id})
            elif isinstance(trc, ShortTrack):
                tracks_data.append({'id': trc.id, 'albumId': trc.album_id})
            elif isinstance(trc, str):
                if ',' in trc:
                    trc, *ofter_tracks = trc.split(',')
                    tracks.extend(ofter_tracks)
                try:
                    track_id, album_id = trc.split(':')
                except ValueError:
                    raise ValueError(
                        'The string does not match the operations')
                else:
                    tracks_data.append({'id': track_id, 'albumId': album_id})
            elif isinstance(trc, dict):
                tracks_data.append(trc)
            else:
                raise TypeError(f'Track format {type(trc).__name__} not found')

        operation = {
            'diff': {
                'op': OperationType.INSERT,
                'at': index,
                'tracks': tracks_data
            }
        }

        return cls(operation)


class VisibilityType(StrEnum):
    PUBLIC = 'public'
    PRIVATE = 'private'
