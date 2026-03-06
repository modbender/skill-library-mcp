export const HASHTAG_POLICIES = {
  "tcg-default": {
    required: ["#tcg", "#cardcollecting"],
    suggested: ["#marketdata", "#startup"],
    maxCount: 6,
  },
  general: {
    required: [],
    suggested: ["#contentstrategy", "#shortformvideo"],
    maxCount: 6,
  },
};

const TOKEN_STOPLIST = new Set([
  "the",
  "and",
  "for",
  "with",
  "from",
  "that",
  "this",
  "your",
  "into",
  "what",
]);

export function resolveHashtagPolicy(policyName) {
  if (!policyName) return "tcg-default";
  if (!HASHTAG_POLICIES[policyName]) {
    throw new Error(
      `Unknown hashtagPolicy '${policyName}'. Allowed: ${Object.keys(HASHTAG_POLICIES).join(", ")}`
    );
  }
  return policyName;
}

function sanitizeWord(raw) {
  return raw.toLowerCase().replace(/[^a-z0-9]/g, "");
}

function extractKeywords(slides, topic) {
  const words = `${slides.join(" ")} ${topic || ""}`.split(/\s+/).map(sanitizeWord);
  const counts = new Map();
  for (const word of words) {
    if (!word || word.length < 4 || TOKEN_STOPLIST.has(word)) continue;
    counts.set(word, (counts.get(word) || 0) + 1);
  }
  return [...counts.entries()]
    .sort((a, b) => b[1] - a[1])
    .slice(0, 4)
    .map(([word]) => `#${word}`);
}

export function buildHashtags({
  policyName,
  slides,
  topic,
  hashtagOverrides = [],
  locale = "en",
}) {
  const policy = HASHTAG_POLICIES[resolveHashtagPolicy(policyName)];
  const dynamic = extractKeywords(slides, topic);
  const localeTag = locale !== "en" ? [`#${locale}`] : [];
  const merged = [
    ...policy.required,
    ...hashtagOverrides,
    ...dynamic,
    ...policy.suggested,
    ...localeTag,
  ];
  const deduped = [...new Set(merged)];
  return deduped.slice(0, policy.maxCount);
}
