import { AlignmentConfig, AlignmentFingerprint } from './types.js';

export function generateFingerprint(config: AlignmentConfig, username: string): AlignmentFingerprint {
  // logic to extract keywords
  const axiomaticKeywords = config.axiomatic_entries
    .map(e => e.content.split(' ').filter(w => w.length > 4)) // Naive keyword extraction
    .flat();

  return {
    synced_at: new Date().toISOString(),
    codex_version: "1.0",
    username,
    enforcement_level: "advisory",
    keywords: {
      axiomatic: [...new Set(axiomaticKeywords)],
      shadow: []
    },
    violations_count: 0
  };
}
