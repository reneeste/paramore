# Removes an entire song from local scrape

# Example use from CLI:
# python -m lyrics.helpers.remove-scraped-song --artist paramore --song "Misery Business (Live from London)" --url "https://genius.com/Paramore-misery-business-live-from-london-lyrics"

from __future__ import annotations
import argparse, json, pandas as pd
from pathlib import Path

def parse_cli():
    p = argparse.ArgumentParser(description="Delete a single song from local data.")
    p.add_argument("--artist", required=True, help ="Artist folder, e.g. 'paramore' or 'hayley'")
    p.add_argument("--song",  required=True, help="Exact Title column value")
    p.add_argument("--url",    help="Original Genius URL (removes from scraped_urls)")
    return p.parse_args()

def artist_paths(artist: str) -> dict[str, Path]:
    base = Path(__file__).resolve().parents[1] / artist.lower()
    return {
        "songs":  base / "songs.csv",
        "lyrics": base / "lyrics.csv",
        "lyrics_json":  base / "lyrics.json",
        "titles": base / "song_titles.txt",
        "scraped": base / "scraped_urls.json",
    }

def remove_song(artist: str, song: str, url: str | None) -> dict[str, int]:
    p = artist_paths(artist)
    removed = {k: 0 for k in ["songs.csv", "lyrics.csv",
                              "song_titles.txt", "scraped_urls.json",
                              "lyrics.json"]}

    if p["songs"].exists():
        df = pd.read_csv(p["songs"])
        orig = len(df)
        df = df[df["Title"] != song]
        removed["songs.csv"] = orig - len(df)
        df.to_csv(p["songs"], index=False)

    if p["lyrics"].exists():
        df = pd.read_csv(p["lyrics"])
        orig = len(df)
        df = df[df["Song"] != song]
        removed["lyrics.csv"] = orig - len(df)
        df.to_csv(p["lyrics"], index=False)

    if p["titles"].exists():
        lines = p["titles"].read_text().splitlines()
        if song in lines:
            removed["song_titles.txt"] = 1
            p["titles"].write_text("\n".join(l for l in lines if l != song))

    if url and p["scraped"].exists():
        data = json.loads(p["scraped"].read_text() or "{}")
        if url in data:
            del data[url]
            removed["scraped_urls.json"] = 1
            p["scraped"].write_text(json.dumps(data, indent=2))

    if p["lyrics_json"].exists():
        data = json.loads(p["lyrics_json"].read_text() or "{}")
        for album in list(data.keys()):
            if song in data[album]:
                del data[album][song]
                removed["lyrics.json"] += 1
                if not data[album]:
                    del data[album]
        p["lyrics_json"].write_text(json.dumps(data, indent=4))

    return removed

if __name__ == "__main__":
    cli = parse_cli()
    print(remove_song(cli.artist, cli.song, cli.url))