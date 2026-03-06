import { searchListings as searchRedfin } from "./redfin.mjs";
import { searchListings as searchZillow } from "./zillow.mjs";
import { searchListings as searchRealtor } from "./realtor.mjs";

const REGISTRY = {
  redfin: searchRedfin,
  zillow: searchZillow,
  realtor: searchRealtor,
};

export function parseProvidersFlag(v = "") {
  const list = String(v || "")
    .split(",")
    .map((x) => x.trim().toLowerCase())
    .filter(Boolean);
  return list.length ? [...new Set(list)] : ["redfin"];
}

export async function searchListings(query, providers = ["redfin"]) {
  const selected = providers.filter((p) => REGISTRY[p]);
  const out = [];

  for (const p of selected) {
    const fn = REGISTRY[p];
    try {
      const rows = await fn(query);
      for (const r of rows || []) {
        out.push({ ...r, provider: r.provider || p, sourceProviders: [r.provider || p] });
      }
    } catch {
      // keep best-effort multi-provider behavior
    }
  }

  return out;
}
