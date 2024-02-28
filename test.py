import yandex_music_api
import os
import asyncio
from dotenv import load_dotenv

load_dotenv("C:/Users/2008d/git/lordbot/.env")

token = os.environ.get('yandex_api_token')

async def main():
    track = (await yandex_music_api.yandex_music_requests.get_list(53447834))[0]
    print(await track.download_link(320))

if __name__ == "__main__":
    asyncio.run(main())
