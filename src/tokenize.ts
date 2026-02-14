export function tokenize(text: string): string[] {
  const words = text.toLowerCase().replace(/[^a-z0-9\-]/g, " ").split(/\s+/).filter(Boolean);
  const tokens: string[] = [];
  for (const word of words) {
    tokens.push(word);
    // Split hyphenated tokens into sub-tokens
    if (word.includes("-")) {
      for (const part of word.split("-")) {
        if (part) tokens.push(part);
      }
    }
  }
  return tokens;
}
