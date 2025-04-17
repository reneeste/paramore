# Merges the lyrics.json files of multiple artists (Paramore & Hayley Williams) into one file, tagging every album with its artist. Run whenever any of the artists are re-scraped.

# Example use from CLI:
# python -m lyrics.helpers.combine --artists paramore hayley

from __future__ import annotations
import argparse, json
from pathlib import Path

def parse_cli():
    ap = argparse.ArgumentParser()
    ap.add_argument("--artists", nargs="+", required=True, help="Folder names under src/lyrics/ (paramore hayley)")
    return ap.parse_args()

def load_lyrics(path: Path) -> dict:
    try:
        return json.loads(path.read_text())
    except Exception:
        print(f"⚠️  Cannot load {path}")
        return {}

def merge(artists: list[str]) -> dict:
    combo: dict[str, dict] = {}
    for art in artists:
        path = Path(__file__).resolve().parents[1] / art / "lyrics.json"
        data = load_lyrics(path)
        for album, songs in data.items():
            combo.setdefault(art, {}).setdefault(album, {}).update(songs)
    return combo

if __name__ == "__main__":
    args = parse_cli()
    merged = merge(args.artists)
    
    out_path = Path(__file__).resolve().parents[2] / "lyrics" / "lyrics.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(merged, indent=2), encoding="utf-8")
    
    print(f"✅ Wrote combined file with {len(merged)} artist blocks → {out_path}")
