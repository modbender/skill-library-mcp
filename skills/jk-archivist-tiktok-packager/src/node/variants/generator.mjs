export function generateVariantSpecs(baseSpec, strategy) {
  if (!strategy) return [baseSpec];

  if (strategy === "caption-cta") {
    return [
      { ...baseSpec, ctaPack: "follow-focused", variantLabel: "cta-follow" },
      { ...baseSpec, ctaPack: "link-focused", variantLabel: "cta-link" },
      { ...baseSpec, ctaPack: "engagement-focused", variantLabel: "cta-engage" },
    ];
  }

  if (strategy === "style") {
    return [
      { ...baseSpec, stylePreset: "default", variantLabel: "style-default" },
      { ...baseSpec, stylePreset: "high-contrast", variantLabel: "style-contrast" },
      { ...baseSpec, stylePreset: "clean", variantLabel: "style-clean" },
    ];
  }

  if (strategy === "template") {
    return [
      { ...baseSpec, template: "intro", variantLabel: "template-intro" },
      { ...baseSpec, template: "educational", variantLabel: "template-edu" },
      { ...baseSpec, template: "announcement", variantLabel: "template-announce" },
    ];
  }

  throw new Error("Unknown --ab-test strategy. Allowed: caption-cta|style|template");
}
