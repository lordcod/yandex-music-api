
from yandex_music_api import Client
import os
import asyncio
from dotenv import load_dotenv

from yandex_music_api.http import Route
from yandex_music_api.types import PlaylistShortPayload
from yandex_music_api.util import Difference


load_dotenv()

token = os.environ.get('yandex_api_token')


async def main():
    client = Client(token)
    await client.identify()

    pls = await client.get_playlist_from_userid('ramilded', 3)
    print(pls.tracks)

    # await client._state.http.edit_playlist_tracks(playlist.owner['uid'], playlist.id, diff, playlist.revision)
    # await client._state.http.edit_playlist_tracks(client._state.userid, 1018, diff, playlist.revision)

    # r = Route('GET', '/landing3/chart/{charttype}', charttype='world')
    # res = await client._state.http.request(r)

    # pl = await client._state.http.get_playlist('misheninkolya', 1000)
    # await client.get_track([track.id for track in (await client.get_likes_tracks())])

    await client._state.session.close()

if __name__ == "__main__":
    asyncio.run(main())
