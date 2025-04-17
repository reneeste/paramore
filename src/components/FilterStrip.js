// @flow
import "../style/FilterStrip.css";
import React from "react";

import { isMobile } from "./utils";
const mobile = isMobile();

type Props = {
	artistToCategories: { [string]: Array<string> }, // as before
	activeCats: { [string]: boolean },
	toggleCategory: (string, string) => void,
	checkAll: () => void,
	uncheckAll: () => void,
};

export default function FilterStrip({ artistToCategories, activeCats, toggleCategory }: Props): React$MixedElement {
	/* flatten all pills */
	const pills = [];
	Object.entries(artistToCategories).forEach(([artist, cats]) => {
		cats.forEach((cat) => {
			const key = `${artist}::${cat}`;
			const state = activeCats[key] ? "on" : "off";
			pills.push(
				<span key={key} className={`catPill--${state} ` + (mobile ? " catPill-mobile" : "catPill")} onClick={() => toggleCategory(artist, cat)}>
					{cat}
				</span>
			);
		});
	});

	return (
		<div className={mobile ? " FilterStrip-mobile" : "FilterStrip"}>
			<div className="pillWrap">{pills}</div>
		</div>
	);
}
