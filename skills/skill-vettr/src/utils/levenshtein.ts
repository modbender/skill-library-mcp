/**
 * Compute Levenshtein edit distance between two strings.
 * Standard Wagner-Fischer dynamic programming algorithm.
 */
export function levenshtein(a: string, b: string): number {
  const la = a.length;
  const lb = b.length;

  if (la === 0) return lb;
  if (lb === 0) return la;

  // Use single-row optimisation to avoid allocating a full matrix.
  const row = new Uint16Array(lb + 1);
  for (let j = 0; j <= lb; j++) row[j] = j;

  for (let i = 1; i <= la; i++) {
    let prev = i - 1;
    row[0] = i;

    for (let j = 1; j <= lb; j++) {
      const cost = a[i - 1] === b[j - 1] ? 0 : 1;
      const current = Math.min(
        (row[j] ?? 0) + 1,           // deletion
        (row[j - 1] ?? 0) + 1,       // insertion
        prev + cost,                   // substitution
      );
      prev = row[j] ?? 0;
      row[j] = current;
    }
  }

  return row[lb] ?? 0;
}
