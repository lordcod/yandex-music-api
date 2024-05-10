from yandex_music_api import Client
import os
import asyncio
from dotenv import load_dotenv


load_dotenv("C:/Users/2008d/git/lordbot/.env")

token = os.environ.get('yandex_api_token')


async def main():
    client = Client(token)
    await client.identify()

    print(await client.get_likes_tracks())
    tracks = await client.get_track([track.id for track in (await client.get_dislikes_tracks())])
    print(tracks)

    await client._state.session.close()

if __name__ == "__main__":
    asyncio.run(main())
