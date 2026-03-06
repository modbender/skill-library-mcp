const AUDIENCE_MODES = new Set(["beginner", "operator", "expert"]);

export function resolveAudienceMode(audience) {
  if (!audience) return "operator";
  if (!AUDIENCE_MODES.has(audience)) {
    throw new Error(`Unknown audience '${audience}'. Allowed: beginner, operator, expert`);
  }
  return audience;
}

export function adaptSlidesForAudience(slides, audience) {
  const mode = resolveAudienceMode(audience);
  if (mode === "operator") return slides;
  if (mode === "beginner") {
    return slides.map((line) => line.replace(/\bnuance\b/gi, "details"));
  }
  return slides.map((line) =>
    line.includes(":") ? line : `${line} (signal-to-noise focus for advanced readers).`
  );
}
