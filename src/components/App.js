// @flow
import "../style/index.css";
import "../style/App.css";

import React, { useEffect, useState } from "react";
import { createSearchParams, useNavigate, useLocation } from "react-router-dom";

import InputBox from "./InputBox";
import QueriedLyrics from "./QueriedLyrics";
import InfoButton from "./InfoButton";
import InfoModal from "./InfoModal";

import { ArtistName } from "./constants";
import { isMobile, getURLQueryStrings, URL_QUERY_PARAM, convertQueriesToPlurals } from "./utils";

/* -----------------------------------------------------------------------
   Build helper maps from album_map.json
   -------------------------------------------------------------------- */
const catalog = require("../lyrics/lyrics.json");
const albumMapRaw = (() => {
	try {
		return require("../lyrics/album_map.json");
	} catch {
		console.error("⚠️ album_map.json missing/invalid");
		return {};
	}
})();

/* dataset keys present in catalogue */
const ARTIST_KEYS = Object.keys(catalog);

/* pretty labels for sidebar */
const LABEL_FOR_ARTIST = {
	paramore: "Paramore",
	hayley: "Hayley Williams",
};
const label = (k) => LABEL_FOR_ARTIST[k] ?? k.replace(/(^|\s)\w/g, (m) => m.toUpperCase());

/* artist → array of unique category buttons
      and categoryKey ("artist::category") → array of albums */
const ARTIST_TO_CATEGORIES = {};
const CATEGORY_TO_ALBUMS = {};

for (const artist of ARTIST_KEYS) {
	const catSet = new Set();
	const albums = albumMapRaw[artist] || {};
	for (const [album, cats] of Object.entries(albums)) {
		cats.forEach((c) => {
			catSet.add(c);
			const key = `${artist}::${c}`;
			(CATEGORY_TO_ALBUMS[key] ||= []).push(album);
		});
	}
	ARTIST_TO_CATEGORIES[artist] = Array.from(catSet);
}

/* helper to build a full category‑state object */
const makeCatState = (checked /*: boolean */) => Object.keys(CATEGORY_TO_ALBUMS).reduce((o, k) => ({ ...o, [k]: checked }), {});
/* -------------------------------------------------------------------- */

const mobile = isMobile();

export default function App(): React$MixedElement {
	/* URL search */
	const [queries, setQueries] = useState(getURLQueryStrings());

	/* filter state (all categories ON) */
	const [activeArtists, setActiveArtists] = useState(ARTIST_KEYS.reduce((o, a) => ({ ...o, [a]: true }), {}));
	const [activeCats, setActiveCats] = useState(makeCatState(true));

	/* misc UI */
	const [infoModal, setInfoModal] = useState(false);
	const [includePlurals, setIncludePlurals] = useState(true);
	const [isLoading, setIsLoading] = useState(false);

	const navigate = useNavigate();
	const location = useLocation();

	/* ------ helpers ------ */
	const checkAll = () => {
		setActiveArtists(ARTIST_KEYS.reduce((o, a) => ({ ...o, [a]: true }), {}));
		setActiveCats(makeCatState(true));
	};
	const uncheckAll = () => {
		setActiveCats(makeCatState(false));
	};

	const toggleArtist = (artist) => {
		const nextArtists = { ...activeArtists, [artist]: !activeArtists[artist] };
		if (!nextArtists[artist]) {
			const copy = { ...activeCats };
			ARTIST_TO_CATEGORIES[artist].forEach((c) => {
				copy[`${artist}::${c}`] = false;
			});
			setActiveCats(copy);
		}
		setActiveArtists(nextArtists);
	};

	const toggleCategory = (artist, category) => {
		const key = `${artist}::${category}`;
		setActiveCats({ ...activeCats, [key]: !activeCats[key] });
	};

	/* perform search */
	const performSearch = (raw /*: string */) => {
		setIsLoading(true);
		const parts = raw
			.split(",")
			.map((q) => q.trim())
			.filter(Boolean);
		navigate({
			search: createSearchParams(parts.map((q) => [URL_QUERY_PARAM, q])).toString(),
		});
	};

	/* re‑search on filter change */
	useEffect(() => {
		if (queries.length > 0) performSearch(queries.join(","));
		// eslint-disable-next-line react-hooks/exhaustive-deps
	}, [JSON.stringify(activeArtists), JSON.stringify(activeCats)]);

	useEffect(() => {
		setQueries(getURLQueryStrings());
		setIsLoading(false);
	}, [location]);

	/* ------------------- render ------------------- */
	return (
		<div className="App">
			<InfoModal handler={() => setInfoModal(false)} display={infoModal} />

			<div className="contentWrapper">
				{/* your existing layout */}
				<div style={{}}>
					{queries.length === 0 ? (
						<div className="title">
							<span className={mobile ? "title-text-mobile header" : "title-text header"}>
								{ArtistName} <br /> lyric searcher
							</span>
						</div>
					) : (
						<div className="top-title">
							<span
								className={mobile ? "top-text-mobile header" : "top-text header"}
								onClick={() => {
									setQueries([]);
									navigate("/");
								}}
							>
								{ArtistName} <br /> lyric searcher
							</span>
						</div>
					)}

					{queries.length === 0 && <div className="tips">To search for multiple words or phrases, use a comma between them. Use a * for wildcard search.</div>}

					<InputBox submitHandler={performSearch} queryString={queries.join(", ")} includePlurals={includePlurals} setIncludePlurals={setIncludePlurals} artistToCategories={ARTIST_TO_CATEGORIES} activeCats={activeCats} toggleCategory={toggleCategory} checkAll={checkAll} uncheckAll={uncheckAll} showFilters={queries.length > 0} />

					{queries.length > 0 && <QueriedLyrics queries={includePlurals ? convertQueriesToPlurals(queries) : queries} activeArtists={activeArtists} activeCats={activeCats} categoryToAlbums={CATEGORY_TO_ALBUMS} isLoading={isLoading} />}
				</div>
				<InfoButton handler={() => setInfoModal(true)} />
			</div>
		</div>
	);
}
