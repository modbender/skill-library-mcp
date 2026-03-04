const BANNED_PATTERNS = [
  /\$/,
  /\btoken\b/i,
  /\bbuy\b/i,
  /\bsell\b/i,
  /\bguaranteed\b/i,
  /\bmost accurate\b/i,
];

const MAX_SLIDE_LENGTH = 120;
const MAX_CAPTION_LENGTH = 900;

export function collectPreflightDiagnostics({ slides, caption }) {
  const totalSlideChars = slides.reduce((sum, line) => sum + line.length, 0);
  return {
    avg_slide_chars: Math.round(totalSlideChars / Math.max(1, slides.length)),
    max_slide_chars: Math.max(...slides.map((line) => line.length)),
    caption_chars: caption.length,
    line_length_pressure: slides.map((line) => Math.round((line.length / MAX_SLIDE_LENGTH) * 100)),
    readability_score: Math.max(0, 100 - Math.round(totalSlideChars / 12) - slides.length * 2),
  };
}

export function runPreflightChecks({ slides, caption }) {
  const issues = [];

  if (!Array.isArray(slides) || slides.length !== 6) {
    issues.push("Slides must contain exactly 6 entries.");
  }

  for (const [idx, line] of slides.entries()) {
    if (line.length > MAX_SLIDE_LENGTH) {
      issues.push(`Slide ${idx + 1} exceeds ${MAX_SLIDE_LENGTH} characters.`);
    }
    for (const pattern of BANNED_PATTERNS) {
      if (pattern.test(line)) {
        issues.push(`Slide ${idx + 1} contains banned content: ${pattern}`);
      }
    }
  }

  if (typeof caption !== "string" || !caption.trim()) {
    issues.push("Caption must be a non-empty string.");
  } else {
    if (caption.length > MAX_CAPTION_LENGTH) {
      issues.push(`Caption exceeds ${MAX_CAPTION_LENGTH} characters.`);
    }
    for (const pattern of BANNED_PATTERNS) {
      if (pattern.test(caption)) {
        issues.push(`Caption contains banned content: ${pattern}`);
      }
    }
  }

  if (issues.length > 0) {
    throw new Error(`Preflight check failed:\n- ${issues.join("\n- ")}`);
  }

  return collectPreflightDiagnostics({ slides, caption });
}
