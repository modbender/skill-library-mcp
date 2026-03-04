export const CTA_PACKS = {
  "follow-focused": "Follow for more collector-first insights.",
  "link-focused": "Link in bio for the full breakdown.",
  "engagement-focused": "What would you change first? Comment below.",
};

export function resolveCtaPack(ctaPack) {
  if (!ctaPack) return "follow-focused";
  if (!CTA_PACKS[ctaPack]) {
    throw new Error(
      `Unknown ctaPack '${ctaPack}'. Allowed: ${Object.keys(CTA_PACKS).join(", ")}`
    );
  }
  return ctaPack;
}
