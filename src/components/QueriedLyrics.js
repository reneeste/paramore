// @flow
import "../style/QueriedLyrics.css";
import React from "react";

import SongLyric from "./SongLyric";
import { containsQuery, isMobile, queriesFound } from "./utils";

const catalog   = require("../lyrics/lyrics.json");   // artist → album → song
const albumMap  = require("../lyrics/album_map.json"); // artist → album → [cats]
const albumMeta = require("../lyrics/album_meta.json"); // album → {year,img}

const mobile = isMobile();

type Props = {
  queries:          Array<string>,
  activeArtists:    { [string]: boolean },
  activeCats:       { [string]: boolean },  
  categoryToAlbums: { [string]: Array<string> },
  isLoading:        boolean,
};

export default function QueriedLyrics({
  queries,
  activeArtists,
  activeCats,
  isLoading,
}: Props): React$MixedElement {
  /* album passes if *any* of its categories is checked */
  const albumEnabled = (artistKey, album) => {
    const cats = albumMap[artistKey]?.[album] || [];
    return cats.some((c) => activeCats[`${artistKey}::${c}`]);
  };

  let totalUses = 0;
  let totalSongs = 0;
  const nodes = [];
  let key = 0;

  for (const artistKey in catalog) {
    if (!activeArtists[artistKey]) continue;

    for (const album in catalog[artistKey]) {
      if (!albumEnabled(artistKey, album)) continue;

      const meta = albumMeta[album] || {};

      for (const song in catalog[artistKey][album]) {
        const lines = catalog[artistKey][album][song];
        let hitSong = false;

        lines.forEach((line) => {
          const hitLine = queries.some(
            (q) => containsQuery(line.lyric, q).start >= 0
          );

          if (hitLine) {
            hitSong = true;
            key += 1;
            nodes.push(
              <SongLyric
                key={key}
                album={album}
                albumYear={meta.year}
                albumImg={meta.img}
                song={song}
                lyric={line.lyric}
                prev={line.prev}
                next={line.next}
                queries={queries}
              />
            );
          }

          queries.forEach((q) => {
            totalUses += line.multiplicity * queriesFound(line.lyric, q);
          });
        });

        if (hitSong) totalSongs += 1;
      }
    }
  }

  return (
    <div>
      <div className={mobile ? "QueriedLyrics-mobile" : "QueriedLyrics"}>
        {isLoading ? <div className="loading" /> : nodes}
      </div>

      <div className={mobile ? "totalResults-mobile" : "totalResults"}>
        Found <span className="highlight">{totalUses} usage{totalUses === 1 ? "" : "s"}</span> in <span className="highlight">{totalSongs} song
        {totalSongs === 1 ? "" : "s"}</span>
      </div>

    </div>
  );
}
