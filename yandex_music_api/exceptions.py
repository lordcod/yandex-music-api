from typing import Optional, Union, List

class YandexMusicException(Exception):
    """Possible links in the Yandex Music Library Api for LordCord"""



class NotFound(YandexMusicException):
    def __init__(self,
                 message: str,
                 *,
                 ids: Optional[Union[List[Union[str, int]], int, str]] = None,
                 request: Optional[str] = None
                 ) -> None:
        super().__init__(message)
        self.message = message
        self.ids = ids
        self.request = request

    def __str__(self) -> str:
        return self.message

class BitrateNotFound(YandexMusicException):
    def __init__(self, bitrateInKbps: int) -> None:
        super().__init__(f"Bitrate {bitrateInKbps} not found.")