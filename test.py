from yandex_music_api import Client
from yandex_music_api.coonector import Requests
from aiohttp import ClientSession
import os
import asyncio
from dotenv import load_dotenv


load_dotenv("C:/Users/2008d/git/lordbot/.env")

token = os.environ.get('yandex_api_token')


async def main():
    session = ClientSession()
    requests = Requests(session)
    client = Client(token, requests)

    track = await client.search('Time', with_only_result=True)
    await client.like_track(track)
    print(await track.download_link(320))

    track = await client.get_list('104274512', 'track', True)
    print(await track.download_link(320))

    track = await client.get_list('28123136', 'track', True)
    await client.dislike_track(track)

    likes_tracks = await client.get_likes_tracks()
    print(await likes_tracks[3].download_link())

    artist = await client.get_list('999456', 'artist', True)
    rating_track_ids = await artist.get_rating_track_ids()
    rating_tracks = await client.get_list(rating_track_ids, 'track')
    print(await rating_tracks[2].download_link())
    await session.close()

if __name__ == "__main__":
    asyncio.run(main())
