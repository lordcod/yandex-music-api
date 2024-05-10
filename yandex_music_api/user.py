from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from yandex_music_api.state import ConnectionState


class User:
    def __init__(self, state: ConnectionState, data: dict) -> None:
        self._state = state
        self.data = data
        self.id = data.get('uid')
        self.login = data.get('login')
        self.name = data.get('name')
        self.sex = data.get('sex')
        self.verified = data.get('verified')
