from yandex_music_api import Client
import os
import asyncio
from dotenv import load_dotenv


load_dotenv()

token = os.environ.get('yandex_api_token')


async def main():
    client = Client(token)
    await client.identify()

    pls = await client.get_likes_tracks()
    print(pls[0]._state.http.user_agent)

    # pl = await client._state.http.get_playlist('misheninkolya', 1000)
    # await client.get_track([track.id for track in (await client.get_likes_tracks())])

    await client._state.session.close()

if __name__ == "__main__":
    asyncio.run(main())
