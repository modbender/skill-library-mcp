import crypto from "crypto";

function normalizeAddress(addr = {}) {
  return [addr.street, addr.city, addr.state, addr.zip]
    .map((x) => (x || "").toString().trim().toLowerCase())
    .join("|");
}

function dedupeFingerprint(listing = {}) {
  const addr = normalizeAddress(listing.address);
  const beds = listing.beds ?? "?";
  const baths = listing.baths ?? "?";
  const sqft = listing.sqft ?? "?";
  const status = listing.status || "?";
  const amount = listing.status === "for_rent" ? (listing.rent ?? "?") : (listing.price ?? "?");
  return `${addr}|${beds}|${baths}|${sqft}|${status}|${amount}`;
}

export function listingKey(listing) {
  if (listing.listingKey) return listing.listingKey;
  if (listing.provider && listing.providerId) return `${listing.provider}:${listing.providerId}`;
  const digest = crypto.createHash("sha1").update(normalizeAddress(listing.address)).digest("hex").slice(0, 12);
  return `addr:${digest}`;
}

export function dedupeListings(listings = []) {
  const byFingerprint = new Map();

  for (const x of listings) {
    const k = dedupeFingerprint(x);
    const item = { ...x, listingKey: listingKey(x) };

    if (!byFingerprint.has(k)) {
      byFingerprint.set(k, item);
      continue;
    }

    const prev = byFingerprint.get(k);
    const mergedSources = [...new Set([...(prev.sourceProviders || [prev.provider].filter(Boolean)), ...(item.sourceProviders || [item.provider].filter(Boolean))])];

    // Prefer item with richer school details or non-null geo fields.
    const prevSchoolRich = JSON.stringify(prev.schools || {}).length;
    const itemSchoolRich = JSON.stringify(item.schools || {}).length;
    const pick = (itemSchoolRich > prevSchoolRich || (!prev.lat && item.lat) || (!prev.lng && item.lng)) ? item : prev;

    byFingerprint.set(k, {
      ...pick,
      sourceProviders: mergedSources,
      provider: mergedSources.length > 1 ? "multi" : (pick.provider || mergedSources[0] || "unknown"),
    });
  }

  return [...byFingerprint.values()];
}
