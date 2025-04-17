from pathlib import Path
from lyrics.scraper import Scraper

ARTIST_ID = 22531 # Paramore's artist ID on Genius

ALBUMS = {
    "/albums/28192": "All We Know Is Falling",
    "/albums/25380": "Riot!",
    "/albums/817245": "RIOT! (International Deluxe Version)",
    "/albums/989325": "The B-Sides",
    "/albums/1367045": "Decode / I Caught Myself",
    "/albums/19097": "brand new eyes",
    "/albums/296310": "Singles Club",
    "/albums/28272": "Paramore",
    "/albums/488326": "Paramore (Deluxe Edition)",
    "/albums/340733": "After Laughter",
    "/albums/948407": "This Is Why",
    "/albums/1087053": "Re: This Is Why",
}

# Songs that don't have an album
OTHER_SONGS = {}

# Songs for which there is trouble retrieving them
EXTRA_SONG_API_PATHS = {}

# Songs that are in multiple albums and aren't behaving how they need to be
FORCE_ALBUM_OVERRIDES = {
    "Decode": "Decode / I Caught Myself",
    "I Caught Myself": "Decode / I Caught Myself",
}

# Songs that are somehow duplicates / covers / etc.
IGNORE_SONGS = {
    
    # Duplicates
    "/songs/3433029": "Hallelujah (Demo)",
    "/songs/3433046": "Oh Star (Demo)",
    "/songs/1238529": "Turn It Off (Acoustic)",
    "/songs/3644046": "Brick by Boring Brick (Acoustic)",
    "/songs/1117555": "Ignorance (Acoustic)",
    "/songs/1359430": "Emergency (Crab Mix)",
    "/songs/1649163": "Decode (Acoustic Version)",
    "/songs/1246800": "When It Rains (Demo)",
    "/songs/996877": "Hate to See Your Heart Break (Remix)",
    
    # Live
    "/songs/7209979": "Emergency (Live in Anaheim)",
    "/songs/3217948": "Misery Business (Acoustic)",
    "/songs/4157142": "Pressure (Live in Anaheim)",
    "/songs/7215107": "Misery Business (Live from London)",
    "/songs/6184402": "Ain’t It Fun (Live at Red Rocks)",
    "/songs/6184398": "Brick By Boring Brick (Live at Red Rocks)",
    "/songs/6184395": "Decode (Live at Red Rocks)",
    "/songs/6184399": "Let The Flames Begin (Live at Red Rocks)",
    "/songs/6184400": "Part II (Live at Red Rocks)",
    "/songs/6184401": "Proof (Live at Red Rocks)",
    "/songs/6184394": "Still Into You (Live at Red Rocks)",
    "/songs/6184396": "The Only Exception (Live at Red Rocks)",
    
    # Covers
    "/songs/189879": "Stuck On You",
    "/songs/189827": "My Hero",

    # Not Paramore
    "/songs/9575716": "Big Man, Little Dignity (Re: DOMi & JD BECK)",
    "/songs/9563814": "C’est Comme Ça (Re: Wet Leg)",
    "/songs/9575075": "Crave (Re: Claud)",
    "/songs/9563813": "Figure 8 (Re: Bartees Strange)",
    "/songs/9560613": "Liar (Re: Romy)",
    "/songs/9575713": "Running Out of Time (Re: Panda Bear)",
    "/songs/9573312": "Running Out of Time (Re: Zane Lowe)",
    "/songs/10058250": "Sanity (Re: Jack Antonoff)",
    "/songs/9573310": "The News (Re: The Linda Lindas)",
    "/songs/9571166": "Thick Skull (Re: Julien Baker)",
    "/songs/9578644": "This Is Why (Re: Foals)",
    "/songs/9560693": "You First (Re: Remi Wolf)",
    "/songs/10130747": "David Byrne Does Hard Times",
}

if __name__ == "__main__":
    Scraper(
        artist_id=ARTIST_ID,
        albums=ALBUMS,
        force_album_overrides=FORCE_ALBUM_OVERRIDES,
        ignore_songs=IGNORE_SONGS,
        base_path=Path(__file__).parent, 
    ).run_from_cli()