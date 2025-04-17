// @flow
import "../style/SongLyric.css";
import { boldQueries } from "./utils.js";
import React from "react";

import { isMobile } from "./utils";

const mobile = isMobile();

type Props = {
	album: string,
	albumYear?: number,
	albumImg?: string,
	song: string,
	prev: string,
	lyric: string,
	next: string,
	queries: Array<string>,
};

export default function SongLyric({ album, albumYear, albumImg, song, prev, lyric, next, queries }: Props): React$MixedElement {
	return (
		<div className="SongLyric">
			<div className="lyricBlock">
				{prev && <span className="prevLyric">{prev}<br /></span>}
				<span className="lyric" dangerouslySetInnerHTML={{ __html: boldQueries(lyric, queries) }} />
				{next && <><br /><span className="nextLyric">{next}</span></>}
			</div>

			<div className="songMeta">
				{albumImg && (
					<img
						className="albumThumb"
						src={`${process.env.PUBLIC_URL}/images/${albumImg}`}
						alt={album}
					/>
				)}
				<p>
					<strong>{song}</strong> &mdash; <i>{album}{albumYear && ` (${albumYear})`}</i>
					
				</p>
			</div>

			<hr className={mobile ? "hr-mobile" : "hr"}/>
		</div>
	);
}
