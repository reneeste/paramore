// @flow
import "../style/InputBox.css";
import { isMobile } from "./utils";
import React, { useEffect, useState } from "react";
import FilterStrip from "./FilterStrip";

const mobile = isMobile();

type InputBoxProps = {
	submitHandler: (string) => void,
	setIncludePlurals: (boolean) => void,
	includePlurals: boolean,
	queryString: string,
	artistToCategories: { [string]: Array<string> },
	activeCats: { [string]: boolean },
	toggleCategory: (string, string) => void,
	checkAll: () => void,
	showFilters: boolean,
};

export default function InputBox({ submitHandler, setIncludePlurals, includePlurals, queryString, artistToCategories, activeCats, toggleCategory, checkAll, showFilters }: InputBoxProps): React$MixedElement {
	const [query, setQuery] = useState<string>(queryString);
	const [filtersVisible, setFiltersVisible] = useState(!mobile);

	useEffect(() => {
		setQuery(queryString);
	}, [queryString]);

	const handleChange = (event: any) => {
		setQuery(event.target.value);
	};

	const handleSubmit = (event: any) => {
		if (query !== "") submitHandler(query.trim());
		event.preventDefault();
	};

	const handlePlurals = (event: any) => {
		setIncludePlurals(!includePlurals);
	};

	const toggleFilters = () => {
		setFiltersVisible(!filtersVisible);
	};

	return (
		<div className="InputBox">
			<form onSubmit={handleSubmit}>
				<label>
					<input className={mobile ? "queryBox queryBox-mobile" : "queryBox"} type="text" value={query} onChange={handleChange} />
				</label>
				<input className="submitButton" type="submit" value="➔" />
			</form>

			<div className="filtersWrapper">
				<span className="filterModalButton" onClick={handlePlurals}>
					{includePlurals ? "Including plurals" : "Excluding plurals"}
				</span>
				{showFilters && (
					<>
						<span className="filterModalButton" onClick={checkAll}>
							Reset Filters
						</span>
						<span className="filterModalButton" onClick={toggleFilters}>
							{filtersVisible ? "Hide filters" : "Show filters"}
						</span>
					</>
				)}
			</div>

			{showFilters && (
				<div className={`filterStripContainer ${filtersVisible ? "visible" : "hidden"}`}>
					<FilterStrip activeCats={activeCats} artistToCategories={artistToCategories} toggleCategory={toggleCategory} checkAll={checkAll} />
				</div>
			)}
		</div>
	);
}
