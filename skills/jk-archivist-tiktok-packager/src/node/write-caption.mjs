import { CTA_PACKS, resolveCtaPack } from "./cta/packs.mjs";
import { buildHashtags } from "./hashtags/policy.mjs";
import { localizeText } from "./i18n/localize-content.mjs";

const CAPTION_TEMPLATES = {
  intro: ({ topic }) => `${topic || "Your topic"} gets noisy fast.
This pack turns complexity into six clear slides.
Built for repeatable, collector-first communication.`,
  educational: ({ topic }) => `Learning ${topic || "your topic"} should feel simple.
Six slides, one framework, immediate clarity.
Use this to teach with structure and consistency.`,
  "product-update": ({ topic }) => `${topic || "Product update"} in one concise visual sequence.
What changed, why it matters, and what comes next.
Built for transparent weekly shipping cadence.`,
  announcement: ({ topic }) => `${topic || "Announcement"} delivered in six crisp slides.
Share the context, change, and next step clearly.
Designed for high-trust public updates.`,
  "jk-default": () => `TCG prices look certain — until you zoom in.
JK Index is building the truth layer: clean IDs, real comps, market signals.
Follow if you want collector-first market intelligence. 👑🧱`,
};

function resolveCaptionTemplate(template) {
  if (CAPTION_TEMPLATES[template]) return template;
  return "intro";
}

export function buildCaption(options = {}) {
  if (Object.keys(options).length === 0) {
    return `TCG prices look certain — until you zoom in.
JK Index is building the truth layer: clean IDs, real comps, market signals.
Follow if you want collector-first market intelligence. 👑🧱

#pokemon #tcg #cardcollecting #marketdata #startup`;
  }

  const {
    template = "jk-default",
    topic,
    slides = [],
    ctaPack,
    hashtagPolicy = "tcg-default",
    hashtagOverrides = [],
    locale = "en",
  } = options;

  const templateKey = resolveCaptionTemplate(template);
  const base = CAPTION_TEMPLATES[templateKey]({ topic, slides }).trim();
  const cta = CTA_PACKS[resolveCtaPack(ctaPack)];
  const localizedCta = localizeText(cta, locale);
  const hashtags = buildHashtags({
    policyName: hashtagPolicy,
    slides,
    topic,
    hashtagOverrides,
    locale,
  });
  return `${base}
${localizedCta}

${hashtags.join(" ")}`;
}
