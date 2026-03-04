export function passesHardConstraints(listing, query) {
  const hard = query?.constraints?.hard || {};

  if (hard.priceMax != null && listing.price != null && listing.price > hard.priceMax) return false;
  if (hard.rentMax != null && listing.rent != null && listing.rent > hard.rentMax) return false;
  if (hard.bedsMin != null && listing.beds != null && listing.beds < hard.bedsMin) return false;
  if (hard.bathsMin != null && listing.baths != null && listing.baths < hard.bathsMin) return false;
  if (Array.isArray(hard.homeTypes) && hard.homeTypes.length) {
    const ht = (listing.homeType || "").toLowerCase();
    if (!hard.homeTypes.map((x) => x.toLowerCase()).includes(ht)) return false;
  }
  if (hard.schoolScoreMin != null && listing.schoolScore != null && listing.schoolScore < hard.schoolScoreMin) return false;
  if (hard.maxDriveMinutesToGoogleplex != null && listing.driveMinutesToGoogleplex != null && listing.driveMinutesToGoogleplex > hard.maxDriveMinutesToGoogleplex) return false;
  if (Array.isArray(hard.zipCodes) && hard.zipCodes.length) {
    const z = String(listing?.address?.zip || "");
    if (!hard.zipCodes.map((x) => String(x)).includes(z)) return false;
  }

  return true;
}

export function scoreListing(listing, query) {
  let score = 0;
  const soft = query?.constraints?.soft || {};

  if (soft.preferBackyardForKids && listing.hasBackyard) score += 20;
  if (listing.schoolScore != null) score += Math.min(10, listing.schoolScore);
  if (listing.driveMinutesToGoogleplex != null) score += Math.max(0, 25 - listing.driveMinutesToGoogleplex) * 0.5;

  return score;
}

export function filterAndRank(listings, query) {
  return (listings || [])
    .filter((x) => passesHardConstraints(x, query))
    .map((x) => ({ ...x, rankScore: scoreListing(x, query) }))
    .sort((a, b) => b.rankScore - a.rankScore);
}
