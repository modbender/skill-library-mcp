import test from "node:test";
import assert from "node:assert/strict";
import { findComparableListings, findRecentSimilarPrices, buildSubjectFromListing } from "../core/comps.mjs";

const listings = [
  {
    status: "for_sale",
    address: { street: "101 Alpha St", city: "Sunnyvale" },
    price: 2200000,
    beds: 4,
    baths: 3,
    sqft: 2200,
    homeType: "single_family",
    url: "https://example.com/a",
  },
  {
    status: "for_sale",
    address: { street: "102 Beta St", city: "Sunnyvale" },
    price: 2350000,
    beds: 4,
    baths: 3,
    sqft: 2300,
    homeType: "single_family",
    url: "https://example.com/b",
  },
  {
    status: "for_sale",
    address: { street: "201 Gamma St", city: "Palo Alto" },
    price: 3900000,
    beds: 5,
    baths: 4,
    sqft: 3400,
    homeType: "single_family",
    url: "https://example.com/c",
  },
];

test("findComparableListings returns ranked comps and stats", () => {
  const subject = {
    address: "101 Alpha",
    city: "Sunnyvale",
    beds: 4,
    baths: 3,
    sqft: 2200,
    homeType: "single_family",
    status: "for_sale",
  };

  const out = findComparableListings(subject, listings, { minScore: 20, limit: 5 });
  assert.equal(out.comps.length, 1);
  assert.equal(out.comps[0].listing.address.street, "102 Beta St");
  assert.equal(out.stats.count, 1);
  assert.equal(out.stats.median, 2350000);
});

test("redfin-url strict mode enforces beds/type/city-or-zip/school/sqft constraints", () => {
  const subject = buildSubjectFromListing({
    address: { street: "1 A St", city: "Sunnyvale", zip: "94087" },
    beds: 4,
    baths: 3,
    sqft: 2000,
    homeType: "single_family",
    schoolScore: 8.7,
    status: "for_sale",
  });

  const rows = [
    { status: "sold", address: { street: "ok", city: "Sunnyvale", zip: "94087" }, price: 2000000, beds: 4, baths: 3, sqft: 1900, homeType: "single_family", schoolScore: 8.6 },
    { status: "sold", address: { street: "bad-bed", city: "Sunnyvale", zip: "94087" }, price: 2100000, beds: 5, baths: 3, sqft: 1900, homeType: "single_family", schoolScore: 8.6 },
  ];

  const out = findRecentSimilarPrices(subject, rows, {
    intent: "buy",
    minScore: 1,
    strict: { homeTypeMatch: true, bedsExact: true, sameCityOrZip: true, schoolScoreDelta: 0.5, sqftPct: 0.2 },
  });

  assert.equal(out.comps.length, 1);
  assert.equal(out.comps[0].listing.address.street, "ok");
});

test("findRecentSimilarPrices prioritizes sold listings for buy intent", () => {
  const now = Date.parse("2026-02-28T20:40:00Z");
  const subject = {
    city: "Sunnyvale",
    beds: 4,
    baths: 3,
    sqft: 2200,
    homeType: "single_family",
    status: "for_sale",
  };

  const rows = [
    {
      status: "for_sale",
      address: { street: "A", city: "Sunnyvale" },
      price: 2500000,
      beds: 4,
      baths: 3,
      sqft: 2200,
      homeType: "single_family",
      sourceAsOf: "2026-02-27T00:00:00Z",
    },
    {
      status: "sold",
      address: { street: "B", city: "Sunnyvale" },
      price: 2450000,
      beds: 4,
      baths: 3,
      sqft: 2190,
      homeType: "single_family",
      soldDate: "2026-02-20T00:00:00Z",
    },
  ];

  const out = findRecentSimilarPrices(subject, rows, { intent: "buy", minScore: 10, nowMs: now });
  assert.equal(out.comps.length, 2);
  assert.equal(out.comps[0].listing.status, "sold");
});
