import { sanitizeOfferId } from "./api";
import type { OfferResult } from "./api";

export interface DisplayDeal {
  id: string;
  productName: string;
  description: string;
  store: string;
  price: number | null;
  pricePerLitre: number | null;
  validFrom: string;
  validTo: string;
  sourceQuery: string;
  size: string;
  url: string | null;
}

function formatPrice(value: number | null): string {
  if (value === null || Number.isNaN(value)) {
    return "-";
  }
  return `${value.toFixed(2)} EUR`;
}

function formatPricePerLitre(value: number | null): string {
  if (value === null || Number.isNaN(value)) {
    return "-";
  }
  return `${value.toFixed(2)} EUR/L`;
}

function normalizeDate(value: string): string {
  if (!value) {
    return "-";
  }
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }
  const year = date.getUTCFullYear();
  const month = String(date.getUTCMonth() + 1).padStart(2, "0");
  const day = String(date.getUTCDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

function truncate(input: string, maxLength: number): string {
  if (input.length <= maxLength) {
    return input;
  }
  if (maxLength <= 1) {
    return input.slice(0, maxLength);
  }
  return `${input.slice(0, maxLength - 1)}...`;
}

function pad(input: string, maxLength: number): string {
  const value = truncate(input, maxLength);
  return value.padEnd(maxLength, " ");
}

export function computePricePerLitre(offer: OfferResult): number | null {
  const unit = offer.unit?.shortName?.toLowerCase();
  if (unit === "l" && typeof offer.referencePrice === "number") {
    return offer.referencePrice;
  }

  const price = typeof offer.price === "number" ? offer.price : null;
  const volume = typeof offer.volume === "number" ? offer.volume : null;
  const quantity = typeof offer.quantity === "number" ? offer.quantity : 1;

  if (price === null || volume === null || quantity === null) {
    return null;
  }

  const totalLitres = volume * quantity;
  if (!Number.isFinite(totalLitres) || totalLitres <= 0) {
    return null;
  }

  const perLitre = price / totalLitres;
  return Number.isFinite(perLitre) ? perLitre : null;
}

export function formatSize(offer: OfferResult): string {
  const volume = typeof offer.volume === "number" ? offer.volume : null;
  const quantity = typeof offer.quantity === "number" ? offer.quantity : null;
  const unit = offer.unit?.shortName || "L";

  if (volume === null) return "-";

  const volStr = volume % 1 === 0 ? `${volume}${unit}` : `${volume}${unit}`;
  if (quantity && quantity > 1) return `${quantity}×${volStr}`;
  return volStr;
}

export function mapOfferToDeal(offer: OfferResult, sourceQuery: string): DisplayDeal {
  const validity = Array.isArray(offer.validityDates) && offer.validityDates.length > 0
    ? offer.validityDates[0]
    : undefined;

  const rawId = offer.id !== undefined && offer.id !== null
    ? String(offer.id)
    : `${offer.product?.name ?? "unknown"}|${offer.advertisers?.[0]?.name ?? "unknown"}|${offer.price ?? "na"}|${offer.description ?? ""}`;

  return {
    id: rawId,
    productName: offer.product?.name?.trim() || "Unknown product",
    description: offer.description?.trim() || "",
    store: offer.advertisers?.[0]?.name?.trim() || "Unknown store",
    price: typeof offer.price === "number" ? offer.price : null,
    pricePerLitre: computePricePerLitre(offer),
    validFrom: normalizeDate(validity?.from ?? ""),
    validTo: normalizeDate(validity?.to ?? ""),
    sourceQuery,
    size: formatSize(offer),
    url: (() => { const safeId = sanitizeOfferId(offer.id); return safeId ? `https://www.marktguru.de/offers/${safeId}` : null; })(),
  };
}

export function formatDealsTable(deals: DisplayDeal[]): string {
  if (deals.length === 0) {
    return "No matching deals found.";
  }

  const headers = {
    description: 55,
    store: 14,
    size: 10,
    price: 10,
    litre: 11,
    validity: 21,
  };

  const headerLine = [
    pad("Description", headers.description),
    pad("Store", headers.store),
    pad("Size", headers.size),
    pad("Price", headers.price),
    pad("EUR/L", headers.litre),
    pad("Valid", headers.validity),
    "URL",
  ].join(" | ");

  const separator = "-".repeat(headerLine.length);

  const rows = deals.map((deal) => {
    const desc = deal.description || deal.productName;
    const url = deal.url ?? "-";
    return [
      pad(desc, headers.description),
      pad(deal.store, headers.store),
      pad(deal.size, headers.size),
      pad(formatPrice(deal.price), headers.price),
      pad(formatPricePerLitre(deal.pricePerLitre), headers.litre),
      pad(`${deal.validFrom} – ${deal.validTo}`, headers.validity),
      url,
    ].join(" | ");
  });

  return [headerLine, separator, ...rows].join("\n");
}

export function formatDealsJson(deals: DisplayDeal[], meta: Record<string, unknown>): string {
  return JSON.stringify({
    meta,
    results: deals
  }, null, 2);
}
