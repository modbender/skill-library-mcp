import test from "node:test";
import assert from "node:assert/strict";

import { buildCaption } from "../../src/node/write-caption.mjs";
import { EXACT_SLIDES } from "../../src/node/render-slides.mjs";
import { todayISO } from "../../src/node/utils.mjs";
import { generateSlidesFromTopic } from "../../src/node/slide-copy.mjs";
import { loadPackagerSpec } from "../../src/node/packager-spec.mjs";

test("caption contract is exact", () => {
  const expected = `TCG prices look certain — until you zoom in.
JK Index is building the truth layer: clean IDs, real comps, market signals.
Follow if you want collector-first market intelligence. 👑🧱

#pokemon #tcg #cardcollecting #marketdata #startup`;
  assert.equal(buildCaption(), expected);
});

test("slide copy count is exactly six", () => {
  assert.equal(EXACT_SLIDES.length, 6);
});

test("todayISO returns local YYYY-MM-DD", () => {
  assert.match(todayISO(), /^\d{4}-\d{2}-\d{2}$/);
});

test("topic mode generates deterministic six lines", () => {
  const slides = generateSlidesFromTopic("Collector confidence");
  assert.equal(slides.length, 6);
  assert.equal(slides[0], "Collector confidence: why this matters now.");
});

test("context-aware caption includes CTA and hashtags", () => {
  const caption = buildCaption({
    template: "educational",
    topic: "Card grading",
    slides: generateSlidesFromTopic("Card grading"),
    ctaPack: "engagement-focused",
    hashtagPolicy: "general",
    locale: "en",
  });
  assert.match(caption, /Card grading/);
  assert.match(caption, /comment/i);
  assert.match(caption, /#/);
});

test("packager spec supports audience and locale", () => {
  const spec = loadPackagerSpec({
    topic: "Price signals",
    audience: "beginner",
    locale: "es",
    stylePreset: "default",
  });
  assert.equal(spec.audience, "beginner");
  assert.equal(spec.locale, "es");
  assert.equal(spec.slides.length, 6);
});
