# Fetches all songs for a given artist name

# Example use from CLI:
# python -m lyrics.helpers.fetch-songs --artist "Paramore" --output "paramore_songs.json"

from __future__ import annotations
import argparse, json, requests, sys
from lyrics.config import API_ROOT, CLIENT_ACCESS_TOKEN, artist_name_to_id

HEADERS = {"Authorization": f"Bearer {CLIENT_ACCESS_TOKEN}"}

def parse_cli():
    p = argparse.ArgumentParser(description="Dump every song for an artist.")
    p.add_argument("--artist", required=True)
    p.add_argument("--output", default="all_songs.json",
                   help="File name to save (default: all_songs.json)")
    return p.parse_args()

def get_all_songs(artist_id: int) -> list[dict]:
    page, per_page, songs = 1, 50, []
    print("🔍 Fetching songs …")
    while True:
        r = requests.get(f"{API_ROOT}/artists/{artist_id}/songs",
                         params={"page": page, "per_page": per_page, "sort": "title"},
                         headers=HEADERS)
        if r.status_code != 200:
            print("❌ Error fetching songs:", r.text)
            break
        batch = r.json()["response"]["songs"]
        if not batch:
            break
        songs.extend({
            "title": s["title"],
            "id":    s["id"],
            "url":   s["url"],
            "primary_artist": s["primary_artist"]["name"]
        } for s in batch)
        print(f"📄 Page {page}: +{len(batch)} songs")
        page += 1
    print(f"✅ Total songs fetched: {len(songs)}")
    return songs

if __name__ == "__main__":
    cli = parse_cli()
    artist_id = artist_name_to_id(cli.artist)
    
    if artist_id is None:
        sys.exit(f"❌ Could not find Genius artist‑id for '{cli.artist}'")
    
    data = get_all_songs(artist_id)
    
    with open(cli.output, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        
    print(f"\n🎧 Song list saved to {cli.output}")