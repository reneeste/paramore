# Fetches all albums for a given artist name

# Example use from CLI:
# python -m lyrics.helpers.fetch-albums --artist "Paramore"

from __future__ import annotations
import argparse, requests, sys
from lyrics.config import artist_name_to_id

def parse_cli():
    p = argparse.ArgumentParser(description="List all albums by artist name.")
    p.add_argument("--artist", required=True, help="Artist name, e.g. 'Paramore'")
    return p.parse_args()

def list_albums(artist_id: int) -> None:
    page, total = 1, 0
    base_url = f"https://genius.com/api/artists/{artist_id}/albums"
    
    while True:
        r = requests.get(base_url, params={"page": page})
        if r.status_code != 200:
            print(f"❌ Failed to fetch page {page} – HTTP {r.status_code}")
            break

        albums = r.json()["response"]["albums"]
        if not albums:
            break

        for alb in albums:
            print(f"{alb['name']} → ID: {alb['id']} → URL: {alb['url']}")
        total += len(albums)
        page += 1

    print(f"✅ {total} albums total")

if __name__ == "__main__":
    cli = parse_cli()
    artist_id = artist_name_to_id(cli.artist)
    
    if artist_id is None:
        sys.exit(f"❌ Could not find Genius artist‑id for '{cli.artist}'")
        
    list_albums(artist_id)