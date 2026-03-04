export function normalizeCounterparty(value) {
  if (!value) return null;
  const normalized = value.toLowerCase().replace(/[^a-z0-9]+/g, " ").trim();
  return normalized.length === 0 ? null : normalized;
}
