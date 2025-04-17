from __future__ import annotations
import time
import re
import os, json, socket, argparse, math, re, requests, pandas as pd
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional
import lyricsgenius
from lyricsgenius.types import Song
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
from lyrics.config import API_ROOT, CLIENT_ACCESS_TOKEN

# Fetches raw lyrics text from a Genius song URL using Playwright
def get_lyrics_from_url(url, timeout=60000) -> Optional[str]:
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            print(f"🌐 Scraping: {url}")
            page.goto(url, timeout=timeout)

            # Accept cookie banners or GDPR popups
            try:
                consent = page.query_selector("button:has-text('Accept')")
                if consent:
                    consent.click()
            except:
                pass

            time.sleep(2)  # let scripts/rendering finish

            try:
                page.wait_for_selector("div[data-lyrics-container]", timeout=10000)
            except:
                print("⚠️ Lyrics container not found.")
                return ""

            # Extract and clean
            lyrics_elements = page.locator("div[data-lyrics-container]").all()
            raw_lyrics = "\n".join([el.inner_text().strip() for el in lyrics_elements])
            lines = raw_lyrics.split("\n")

            # Remove any Genius description-like intro (not part of real lyrics)
            cleaned_lines = []
            for line in lines:
                if (
                    "Read More" in line
                    or "You might also like" in line
                    or line.strip().startswith("“") and line.strip().endswith("”")
                    or re.search(r'\b(song|track|lyrics)\b.*(is|was).*', line.lower())
                ):
                    continue
                cleaned_lines.append(line.strip())

            browser.close()
            return "\n".join(cleaned_lines).strip()

    except PlaywrightTimeout:
        print(f"❌ TimeoutError on: {url}")
        return None
    except Exception as e:
        print(f"❌ Error while scraping {url}: {e}")
        return None

# Scrapes every song for one artist and writes CSV / JSON artefacts
class Scraper:
    # ───────────────────────────── CONSTRUCTION ──────────────────────────── #
    def __init__(
        self,
        artist_id: int,
        albums: Dict[str, str],
        other_songs: Dict[str, str] | None = None,
        extra_song_api_paths: Dict[str, str] | None = None,
        force_album_overrides: Dict[str, str] | None = None,
        ignore_songs: Dict[str, str] | None = None,
        base_path: str | Path = ".",
    ) -> None:
        self.artist_id = artist_id
        self.albums = albums
        self.other_songs = other_songs or {}
        self.extra_song_api_paths = extra_song_api_paths or {}
        self.force_album_overrides = force_album_overrides or {}
        self.ignore_songs = ignore_songs or {}

        # Each artist gets its own little workspace (in this case paramore/..., hayley/...)
        base = Path(base_path)
        self.csv_path = base / "songs.csv"
        self.lyric_path = base / "lyrics.csv"
        self.lyric_json_path = base / "lyrics.json"
        self.song_list_path = base / "song_titles.txt"
        self.scraped_urls_path = base / "scraped_urls.json"

        base.mkdir(parents=True, exist_ok=True)

        self.api_root = API_ROOT
        self.artist_url = f"{self.api_root}/artists/{self.artist_id}"
        self.genius = lyricsgenius.Genius(CLIENT_ACCESS_TOKEN, retries=3, timeout=20)

    # ───────────────────────────── PUBLIC ENTRY POINTS ───────────────────── #
    def run_from_cli(self) -> None:
        parser = argparse.ArgumentParser()
        parser.add_argument("--append", action="store_true")
        parser.add_argument("--appendpaths", action="store_true")
        args = parser.parse_args()
        self.run(append=args.append, appendpaths=args.appendpaths)

    def run(self, *, append: bool = False, appendpaths: bool = False) -> None:
        scraped_urls = self._load_scraped_urls()
        original_url_count = len(scraped_urls)

        existing_df, existing_titles = self._load_existing_songs()

        songs_by_album, has_failed, last_album = {}, True, None
        retries = 0
        while has_failed and retries < 4:
            songs_by_album, has_failed, last_album = self._get_songs_by_album(
                songs_by_album,
                last_album,
                existing_titles,
                appendpaths,
                scraped_urls,
            )
            retries += 1

        self._albums_to_songs_csv(songs_by_album, existing_df)
        self._save_scraped_urls(scraped_urls)

        if len(scraped_urls) > original_url_count:
            self._songs_to_lyrics()
            self._lyrics_to_json()

    # ───────────────────────────── HELPERS ────────────────────────── #
    def _load_scraped_urls(self) -> Dict[str, str]:
        if self.scraped_urls_path.exists():
            try:
                return json.loads(self.scraped_urls_path.read_text())
            except json.JSONDecodeError:
                print("⚠️ scraped_urls.json exists but is invalid. Reinitializing.")
        return {}

    def _save_scraped_urls(self, scraped_urls: Dict[str, str]) -> None:
        self.scraped_urls_path.write_text(json.dumps(scraped_urls, indent=2))

    def _load_existing_songs(self) -> Tuple[Optional[pd.DataFrame], List[str]]:
        if self.csv_path.exists() and self.csv_path.stat().st_size > 0:
            df = pd.read_csv(self.csv_path)
            return df, list(df["Title"])
        return None, []

    # ─────────────────────────── SCRAPING LOGIC ────────────────────────── #
    def _get_songs_by_album(
        self,
        songs_by_album: Dict[str, List[Song]],
        last_album: Optional[str],
        songs_so_far: List[str],
        append_paths: bool,
        scraped_urls: Dict[str, str],
    ) -> Tuple[Dict[str, List[Song]], bool, Optional[str]]:

        def get_song_data(api_path: str) -> Optional[Dict]:
            request_url = self.api_root + api_path
            r = requests.get(request_url,
                             headers={"Authorization": f"Bearer {CLIENT_ACCESS_TOKEN}"})
            data = r.json()
            if "response" in data and "song" in data["response"]:
                return data["response"]["song"]
            print(f"⚠️ Failed to fetch song data from {api_path}")
            print(f"Response: {data}")
            return None

        def clean_lyrics_and_append(
            song_data: Dict,
            album_name: str,
            lyrics: str,
        ) -> str:
            song_title = self._clean_title(song_data["title"])

            # Forced album overrides
            if song_title in self.force_album_overrides:
                album_name = self.force_album_overrides[song_title]

            cleaned_lyrics = self.clean_lyrics(lyrics)
            s = Song(self.genius, song_data, cleaned_lyrics)

            if album_name not in songs_by_album:
                songs_by_album[album_name] = []

            # Avoid duplicates across albums
            for album_songs in songs_by_album.values():
                if any(self._clean_title(song.title) == song_title
                       for song in album_songs):
                    return

            songs_by_album[album_name].append(s)
            
            return album_name

        album_index = 0

        if not append_paths:
            for album_api_path in self.albums:
                if (last_album is None or
                        album_index >= list(self.albums.keys()).index(last_album)):
                    album_name = self.albums[album_api_path]
                    print(f'💿 Getting songs for album "{album_name}"')
                    next_page = 1
                    tracks: List[Dict] = []

                    while next_page is not None:
                        try:
                            request_url = (
                                self.api_root
                                + album_api_path
                                + f"/tracks?page={next_page}"
                            )
                            r = requests.get(
                                request_url,
                                headers={"Authorization": f"Bearer {CLIENT_ACCESS_TOKEN}"}
                            )
                            track_data = r.json()
                            tracks.extend(track_data["response"]["tracks"])
                            next_page = track_data["response"]["next_page"]
                        except Exception:
                            print("Failed getting album", album_name,
                                  "-- saving songs so far")
                            return songs_by_album, True, album_api_path

                    for track in tracks:
                        song = track["song"]
                        cleaned_song_title = self._clean_title(song["title"])

                        try:
                            song_url = song["url"]

                            # Skip if URL already scraped
                            if song_url in scraped_urls:
                                print(f"⏩ Skipped (already scraped): "
                                      f"'{song['title']}' {song_url}")
                                continue

                            # Ignore list
                            if song["api_path"] in self.ignore_songs:
                                print(f"⏩ Skipped (ignored manually): "
                                      f"'{song['title']}' {song_url}")
                                continue

                            if (cleaned_song_title not in songs_so_far):
                                lyrics = get_lyrics_from_url(song_url)
                                if lyrics and self._has_song_identifier(lyrics):
                                    songs_so_far.append(cleaned_song_title)
                                    album_used = clean_lyrics_and_append(song, album_name, lyrics)
                                    scraped_urls[song_url] = album_used
                        except (requests.exceptions.Timeout, socket.timeout):
                            print("Failed receiving song", cleaned_song_title,
                                  "-- saving songs so far")
                            return songs_by_album, True, album_api_path
                album_index += 1

        for api_path, album_name in self.extra_song_api_paths.items():
            song_data = get_song_data(api_path)
            if (song_data
                    and self._clean_title(song_data["title"]) not in songs_so_far):
                lyrics = get_lyrics_from_url(song_data["url"])
                clean_lyrics_and_append(song_data, album_name, lyrics)

        return songs_by_album, False, None

    # Convert to CSV ------------------------------------------------------- #
    def _albums_to_songs_csv(
        self,
        songs_by_album: Dict[str, List[Song]],
        existing_df: Optional[pd.DataFrame] = None,
    ) -> None:
        songs_records: List[Dict[str, str]] = []
        songs_titles: List[str] = []

        for album, songs in songs_by_album.items():
            for song in songs:
                song_title = self._clean_title(song.title)
                api_path = song._body.get("api_path")
                if api_path in self.ignore_songs:
                    continue
                if song_title in songs_titles:
                    continue

                songs_records.append({
                    "Title": song_title,
                    "Album": album,
                    "Lyrics": song.lyrics,
                })
                songs_titles.append(song_title)

        if not songs_records:
            print("📄 No new songs to write. Skipping CSV save.")
            return

        song_df = pd.DataFrame.from_records(songs_records)
        if existing_df is not None:
            song_df = pd.concat([existing_df, song_df])
            song_df = song_df[~song_df["Title"].isin(self.ignore_songs)]
            song_df = song_df.drop_duplicates("Title", keep="last")

        song_df.to_csv(self.csv_path, index=False)
        print(f"✅ Saved {len(songs_records)} songs to CSV")

    # ───────────────────────── LYRIC POST PROCESSING ──────────────────────── #
    class _Lyric:
        def __init__(self,
                     lyric: str,
                     prev_lyric: Optional[str] = None,
                     next_lyric: Optional[str] = None) -> None:
            self.lyric = lyric
            self.prev = prev_lyric
            self.next = next_lyric

        def __eq__(self, other: object) -> bool:  # type: ignore[override]
            if not isinstance(other, Scraper._Lyric):
                return NotImplemented
            return (self.lyric == other.lyric
                    and self.prev == other.prev
                    and self.next == other.next)

        def __hash__(self) -> int:
            return hash((self.prev or "") + self.lyric + (self.next or ""))

        def __repr__(self) -> str:  # pragma: no cover
            return self.lyric

    def _songs_to_lyrics(self) -> None:
        if not (self.csv_path.exists() and self.csv_path.stat().st_size > 0):
            print("⚠️ No song data found in CSV to process.")
            return

        try:
            song_data = pd.read_csv(self.csv_path)
        except pd.errors.EmptyDataError:
            print("⚠️ CSV exists but is empty. Skipping lyrics processing.")
            return

        lyric_records: List[Dict[str, str | int]] = []
        song_titles: List[str] = []

        for title, album, lyrics in song_data.to_records(index=False):
            if title in song_titles or len(lyrics) <= 1:
                continue

            song_titles.append(title)
            lyric_dict = self._get_lyric_list(str(lyrics))

            for lyric_obj, multiplicity in lyric_dict.items():
                lyric_records.append({
                    "Song": title,
                    "Album": album,
                    "Lyric": lyric_obj.lyric,
                    "Previous Lyric": lyric_obj.prev,
                    "Next Lyric": lyric_obj.next,
                    "Multiplicity": multiplicity,
                })

        lyric_df = pd.DataFrame.from_records(lyric_records)
        lyric_df.to_csv(self.lyric_path, index=False)

        self.song_list_path.write_text(
            "\n".join(sorted(set(song_titles))), encoding="utf-8")

        print("✅ Generated lyrics CSV")

    def _lyrics_to_json(self) -> None:
        if not (self.lyric_path.exists() and self.lyric_path.stat().st_size > 0):
            print("⚠️ No lyric data found. Skipping JSON generation.")
            return

        try:
            lyric_data = pd.read_csv(self.lyric_path)
        except pd.errors.EmptyDataError:
            print("⚠️ Lyrics CSV is empty. Skipping JSON generation.")
            return

        lyric_dict: Dict[str, Dict[str, List[Dict[str, str | int]]]] = {}

        for song in lyric_data.to_records(index=False):
            title, album, lyric, prev_lyric, next_lyric, multiplicity = song
            if album != album:  # NaN
                album = title
            lyric_dict.setdefault(album, {}).setdefault(title, []).append({
                "lyric": lyric,
                "prev": "" if prev_lyric != prev_lyric else prev_lyric,
                "next": "" if next_lyric != next_lyric else next_lyric,
                "multiplicity": int(multiplicity),
            })

        self.lyric_json_path.write_text(json.dumps(lyric_dict, indent=4),
                                        encoding="utf-8")
        print("✅ Generated lyrics JSON")

    # ─────────────────────── STRING CLEANUP HELPERS ───────────────────────── #
    @staticmethod
    def _clean_string(string: str) -> str:
        string = re.sub(r"\u2018|\u2019", "'", string)
        string = re.sub(r"\u201C|\u201D", '"', string)
        string = re.sub(r"\u200b", "", string)
        string = re.sub(
            r"[\u00A0\u1680\u180e\u2000-\u2009\u200a\u202f\u205f\u3000\u200e]",
            " ",
            string,
        )
        string = re.sub(r"\u0435", "e", string)
        string = re.sub(r"\u2013|\u2014", " - ", string)
        return string.strip(" ")

    @classmethod
    def _clean_title(cls, title: str) -> str:  # keep original name
        return cls._clean_string(title)

    @classmethod
    def clean_lyrics(cls, lyrics: str) -> str:
        lines = lyrics.split("\n")
        cleaned_lines: List[str] = []
        started = False

        for line in lines:
            line = line.strip()
            if not started:
                if re.search(r"\bLyrics\b", line):
                    started = True
                    continue
            if started:
                cleaned_lines.append(line)

        lyrics = "\n".join(cleaned_lines)
        lyrics = cls._clean_string(lyrics)

        lyrics = re.sub(r"[0-9]*URLCopyEmbedCopy", "", lyrics)
        lyrics = re.sub(r"[0-9]*Embed", "", lyrics)
        lyrics = re.sub(r"[0-9]*EmbedShare", "", lyrics)
        lyrics = re.sub(
            r"See [\w\s]* LiveGet tickets as low as \$\d*You might also like",
            "\n",
            lyrics,
        )
        return lyrics

    @staticmethod
    def _has_song_identifier(lyrics: str) -> bool:
        return any(tag in lyrics for tag in ("[Intro", "[Verse", "[Chorus"))

    # ─────────────────────── LYRIC LIST BUILDER ────────────────────────── #
    def _get_lyric_list(
        self,
        lyrics: str,
    ) -> Dict["Scraper._Lyric", int]:
        lines = lyrics.split("\n")
        lyric_dict: Dict[Scraper._Lyric, int] = {}
        prev_line: Optional[str] = None

        for i, curr in enumerate(lines):
            curr_line = curr.strip()
            if not curr_line or (curr_line.startswith("[")
                                 and curr_line.endswith("]")):
                continue

            next_line: Optional[str] = None
            for j in range(i + 1, len(lines)):
                peek = lines[j].strip()
                if peek and not peek.startswith("["):
                    next_line = peek
                    break

            lyric = Scraper._Lyric(curr_line, prev_line, next_line)
            lyric_dict[lyric] = lyric_dict.get(lyric, 0) + 1
            prev_line = curr_line

        return lyric_dict