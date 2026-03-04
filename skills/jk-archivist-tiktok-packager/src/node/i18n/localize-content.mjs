const CTA_TRANSLATIONS = {
  es: {
    "Follow for more collector-first insights.": "Sigue para ver mas ideas primero para coleccionistas.",
    "Link in bio for the full breakdown.": "Link en bio para ver el analisis completo.",
    "What would you change first? Comment below.": "Que cambiarias primero? Comenta abajo.",
  },
  fr: {
    "Follow for more collector-first insights.": "Suivez pour plus d analyses orientees collectionneur.",
    "Link in bio for the full breakdown.": "Lien en bio pour voir l analyse complete.",
    "What would you change first? Comment below.": "Que changeriez-vous en premier ? Commentez ci-dessous.",
  },
};

export function localizeText(text, locale) {
  if (!locale || locale === "en") return text;
  const dict = CTA_TRANSLATIONS[locale];
  if (!dict) return text;
  return dict[text] || text;
}
