// @flow
import "../style/InfoModal.css";
import { isMobile } from "./utils";
import { ModalText, UpdateText } from "./constants";
import React from "react";

const mobile = isMobile();

type InfoModalProps = {
  handler: () => void,
  display: boolean,
};

export default function InfoModal({
  handler,
  display,
}: InfoModalProps): React$MixedElement {
  const clickOutHandler = (event: any) => {
    if (event.target.className !== "ModalBox") {
      handler();
    }
  };

  return (
    <div
      className="InfoModal"
      onClick={clickOutHandler}
      style={{ display: display ? "block" : "none" }}
    >
      <div className={mobile ? "ModalBox ModalBox-mobile" : "ModalBox"}>
        <p dangerouslySetInnerHTML={{ __html: ModalText }} />
        <p style={{ fontSize: "14px" }}>
          Originally made by&nbsp;<a href="https://shaynak.github.io/">Shayna Kothari</a>&nbsp;for&nbsp;<a href="https://shaynak.github.io/taylor-swift/">Taylor Swift</a>.
          <br />
          Re-made by <a href="https://github.com/reneeste/">Renee</a>: re-coded and optimized lyric scraper, added multiple artist functionality, changed some design.
          <br />
        </p>
        <p style={{ fontSize: "14px" }}>Lyrics scraped from&nbsp;<a href="http://genius.com">Genius</a> using Playwright. </p>
        <p dangerouslySetInnerHTML={{ __html: UpdateText }} style={{ fontSize: "14px", color: "#aaa" }}/>
          
     
      </div>
    </div>
  );
}
