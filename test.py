from yandex_music_api import Client
import os
import asyncio
from dotenv import load_dotenv

load_dotenv("C:/Users/2008d/git/lordbot/.env")

token = os.environ.get('yandex_api_token')

async def main():
    client = Client(token)
    albums = await client.get_list(7637767, 'album')
    album = albums[0]
    print(album)
    result = await album.get_tracks()
    print(await result[0].download_link(320))

if __name__ == "__main__":
    asyncio.run(main())
