import test from "node:test";
import assert from "node:assert/strict";

import { normalizeQuery, defaultBuyQuery } from "../core/query_normalizer.mjs";
import { dedupeListings } from "../core/dedupe.mjs";
import { filterAndRank } from "../core/scoring.mjs";
import { snapshotDiff } from "../core/notifier.mjs";
import { parseProvidersFlag } from "../providers/index.mjs";

test("normalizeQuery keeps South Bay buy defaults", () => {
  const q = normalizeQuery(defaultBuyQuery());
  assert.equal(q.intent, "buy");
  assert.equal(q.constraints.hard.priceMax, 3200000);
  assert.equal(q.constraints.hard.bedsMin, 4);
  assert.equal(q.constraints.hard.schoolScoreMin, 8);
  assert.equal(q.notify.to, "YOUR_CHAT_ID");
});

test("dedupeListings removes duplicates by provider id", () => {
  const list = [
    { provider: "redfin", providerId: "1", address: { street: "a" } },
    { provider: "redfin", providerId: "1", address: { street: "a" } },
  ];
  const out = dedupeListings(list);
  assert.equal(out.length, 1);
});

test("dedupeListings merges cross-provider duplicates and preserves provenance", () => {
  const list = [
    { provider: "redfin", providerId: "r1", address: { street: "123 Main", city: "Sunnyvale", state: "CA", zip: "94086" }, status: "for_sale", price: 100, beds: 3, baths: 2, sqft: 1500, schools: {} },
    { provider: "zillow", providerId: "z1", address: { street: "123 Main", city: "Sunnyvale", state: "CA", zip: "94086" }, status: "for_sale", price: 100, beds: 3, baths: 2, sqft: 1500, schools: { elementary: { rating: 8 } } },
  ];
  const out = dedupeListings(list);
  assert.equal(out.length, 1);
  assert.equal(out[0].provider, "multi");
  assert.deepEqual(out[0].sourceProviders.sort(), ["redfin", "zillow"]);
});

test("filterAndRank applies hard constraints and backyard preference", () => {
  const q = normalizeQuery(defaultBuyQuery());
  const listings = [
    { listingKey: "a", price: 3000000, beds: 4, homeType: "single_family", schoolScore: 9, driveMinutesToGoogleplex: 20, hasBackyard: true },
    { listingKey: "b", price: 3500000, beds: 4, homeType: "single_family", schoolScore: 9, driveMinutesToGoogleplex: 20, hasBackyard: true },
    { listingKey: "c", price: 3000000, beds: 4, homeType: "single_family", schoolScore: 9, driveMinutesToGoogleplex: 20, hasBackyard: false }
  ];

  const out = filterAndRank(listings, q);
  assert.equal(out.length, 2);
  assert.equal(out[0].listingKey, "a");
});

test("parseProvidersFlag supports csv list and defaults", () => {
  assert.deepEqual(parseProvidersFlag("redfin,zillow,realtor"), ["redfin", "zillow", "realtor"]);
  assert.deepEqual(parseProvidersFlag(""), ["redfin"]);
});

test("snapshotDiff detects new sale/rent and sold status transition", () => {
  const prev = [
    { listingKey: "x", status: "for_sale" },
  ];
  const next = [
    { listingKey: "x", status: "sold" },
    { listingKey: "y", status: "for_sale" },
    { listingKey: "z", status: "for_rent" },
  ];
  const d = snapshotDiff(prev, next);
  const types = d.map((x) => x.type).sort();
  assert.deepEqual(types, ["new_for_rent", "new_for_sale", "status_changed_to_sold"]);
});
