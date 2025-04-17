# Central place for tokens, API roots and a shortcut that turns 'Paramore' into its Genius artist‑id so you don't repeat numbers everywhere.

from __future__ import annotations
import os, json, functools, requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv() 

CLIENT_ACCESS_TOKEN = os.getenv("CLIENT_ACCESS_TOKEN")
API_ROOT = os.getenv("API_ROOT", "https://api.genius.com")

# Simple cache so we only hit Genius once per unique artist name
@functools.lru_cache(maxsize=None)
def artist_name_to_id(name: str) -> int | None:
    # Return Genius artist‑id for a given display name (case‑insensitive)
    headers = {"Authorization": f"Bearer {CLIENT_ACCESS_TOKEN}"}
    r = requests.get(f"{API_ROOT}/search", params={"q": name}, headers=headers)
    if r.status_code != 200:
        return None
    hits = r.json()["response"]["hits"]
    for hit in hits:
        artist = hit["result"]["primary_artist"]
        if artist["name"].lower() == name.lower():
            return artist["id"]
    return None
