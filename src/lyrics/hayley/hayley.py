from pathlib import Path
from lyrics.scraper import Scraper

ARTIST_ID = 298 # Hayley's artist ID on Genius

ALBUMS = {
    "/albums/595868": "Petals for Armor",
    "/albums/730452": "FLOWERS for VASES / descansos",
}

# Songs that don't have an album
OTHER_SONGS = {}

# Songs for which there is trouble retrieving them
EXTRA_SONG_API_PATHS = {}

# Songs that are in multiple albums and aren't behaving how they need to be
FORCE_ALBUM_OVERRIDES = {}

# Songs that are somehow duplicates / covers / etc.
IGNORE_SONGS = {}

if __name__ == "__main__":
    Scraper(
        artist_id=ARTIST_ID,
        albums=ALBUMS,
        force_album_overrides=FORCE_ALBUM_OVERRIDES,
        ignore_songs=IGNORE_SONGS,
        base_path=Path(__file__).parent, 
    ).run_from_cli()