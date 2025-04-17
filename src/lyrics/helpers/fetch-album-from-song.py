# Finds album information for a song from artist name and song title (in case it's needed to check what information Genius holds about songs and their main albums)

# Example use from CLI:
# python -m lyrics.helpers.fetch-album-from-song --artist "Paramore" --song "The Only Exception"

from __future__ import annotations
import argparse, requests
from lyrics.config import CLIENT_ACCESS_TOKEN, API_ROOT

headers = {"Authorization": f"Bearer {CLIENT_ACCESS_TOKEN}"}

def parse_cli():
    p = argparse.ArgumentParser(description="Find album for a given song.")
    p.add_argument("--artist", required=True)
    p.add_argument("--song",   required=True)
    return p.parse_args()

def get_song_id_and_album(song_title: str, artist_name: str) -> None:
    print(f"🔍 Searching for: {song_title} by {artist_name}")
    r = requests.get(f"{API_ROOT}/search", params={"q": song_title},
                     headers=headers)
    if r.status_code != 200:
        print(f"❌ Failed search (HTTP {r.status_code}): {r.text}")
        return

    for hit in r.json()["response"]["hits"]:
        artist = hit["result"]["primary_artist"]["name"].lower()
        if artist_name.lower() in artist:
            song_id = hit["result"]["id"]
            title   = hit["result"]["full_title"]
            print(f"✅ Found: {title} → Song ID: {song_id}")

            meta = requests.get(f"{API_ROOT}/songs/{song_id}", headers=headers)
            if meta.status_code != 200:
                print("⚠️ Couldn't get song metadata.")
                return
            album = meta.json()["response"]["song"].get("album")
            if album:
                print(f"🎵 Album: {album['name']} → ID: {album['id']} → URL: {album['url']}")
            else:
                print("ℹ️ No album info found.")
            return
    print("❌ No matching song found.")

if __name__ == "__main__":
    args = parse_cli()
    get_song_id_and_album(args.song, args.artist)
