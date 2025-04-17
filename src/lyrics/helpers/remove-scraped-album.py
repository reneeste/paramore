# Removes an entire album (and its songs) from local scrape

# Example use from CLI:
# python -m lyrics.helpers.remove-scraped-album --artist paramore --album "All We Know Is Falling (10th Anniversary Edition)"

from __future__ import annotations
from pathlib import Path
import argparse, json, pandas as pd

def parse_cli() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Remove an entire album (and its songs) from local scrape.")
    p.add_argument("--artist", required=True,
                   help="Display name, e.g. 'paramore' or 'hayley'")
    p.add_argument("--album", required=True,
                   help="Exact album title as it appears in CSV")
    return p.parse_args()

def album_paths(artist: str) -> dict[str, Path]:
    base = Path(__file__).resolve().parents[1] / artist.lower()
    return {
        "songs":  base / "songs.csv",
        "lyrics": base / "lyrics.csv",
        "lyrics_json":  base / "lyrics.json",
        "titles": base / "song_titles.txt",
        "scraped": base / "scraped_urls.json",
    }

def remove_scraped_album(artist: str, album: str) -> dict[str, int]:
    paths = album_paths(artist)
    
    removed = {k: 0 for k in ["songs.csv", "lyrics.csv", "song_titles.txt", "scraped_urls.json", "lyrics.json"]}

    # songs.csv
    if paths["songs"].exists():
        df = pd.read_csv(paths["songs"])
        titles = set(df[df["Album"] == album]["Title"])
        removed["songs.csv"] = len(titles)
        df = df[df["Album"] != album]
        df.to_csv(paths["songs"], index=False)
    else:
        titles = set()

    # lyrics.csv
    if paths["lyrics"].exists():
        df = pd.read_csv(paths["lyrics"])
        orig = len(df)
        df = df[df["Album"] != album]
        removed["lyrics.csv"] = orig - len(df)
        df.to_csv(paths["lyrics"], index=False)

    # song_titles.txt
    if paths["titles"].exists():
        lines = paths["titles"].read_text().splitlines()
        kept = [l for l in lines if l not in titles]
        removed["song_titles.txt"] = len(lines) - len(kept)
        paths["titles"].write_text("\n".join(kept))

    # scraped_urls.json
    if paths["scraped"].exists():
        data = json.loads(paths["scraped"].read_text() or "{}")
        orig = len(data)
        data = {u: a for u, a in data.items() if a != album}
        removed["scraped_urls.json"] = orig - len(data)
        paths["scraped"].write_text(json.dumps(data, indent=2))

    # lyrics.json
    if paths["lyrics_json"].exists():
        data = json.loads(paths["lyrics_json"].read_text() or "{}")
        if album in data:
            removed["lyrics.json"] = len(data[album])
            del data[album]
            paths["lyrics_json"].write_text(json.dumps(data, indent=4))

    return removed

if __name__ == "__main__":
    cli = parse_cli()
    print(remove_scraped_album(cli.artist, cli.album))