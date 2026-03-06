export class PurchaseLinks {
  static REF_PARAM = "openclaw"

  static normalizeBaseUrl(apiEndpoint) {
    const fallback = "https://www.web2labs.com"
    const raw = String(apiEndpoint || fallback).trim()
    if (!raw) {
      return fallback
    }

    try {
      const parsed = new URL(raw)
      return `${parsed.protocol}//${parsed.host}`
    } catch {
      return fallback
    }
  }

  static withTracking(baseUrl, path) {
    const normalizedPath = path.startsWith("/") ? path : `/${path}`
    return `${baseUrl}${normalizedPath}?ref=${PurchaseLinks.REF_PARAM}`
  }

  static toNumeric(value, fallback = 0) {
    const n = Number(value)
    if (!Number.isFinite(n)) {
      return fallback
    }
    return n
  }

  static buildFromPricing(pricing, apiEndpoint) {
    const baseUrl = PurchaseLinks.normalizeBaseUrl(apiEndpoint)
    const apiBundles = Array.isArray(pricing?.apiCreditBundles)
      ? pricing.apiCreditBundles
      : []
    const creatorBundles = Array.isArray(pricing?.creatorCreditBundles)
      ? pricing.creatorCreditBundles
      : []

    return {
      ref: PurchaseLinks.REF_PARAM,
      baseUrl,
      apiCredits: apiBundles.map((bundle) => ({
        id: bundle.id,
        credits: PurchaseLinks.toNumeric(bundle.credits),
        price: PurchaseLinks.toNumeric(bundle.price),
        currency: String(bundle.currency || "EUR"),
        checkoutUrl: PurchaseLinks.withTracking(
          baseUrl,
          `/checkout/api-credits/${encodeURIComponent(String(bundle.id || ""))}`
        ),
      })),
      creatorCredits: creatorBundles.map((bundle) => ({
        id: bundle.id,
        credits: PurchaseLinks.toNumeric(bundle.credits),
        price: PurchaseLinks.toNumeric(bundle.price),
        currency: String(bundle.currency || "EUR"),
        checkoutUrl: PurchaseLinks.withTracking(
          baseUrl,
          `/checkout/creator-credits/${encodeURIComponent(String(bundle.id || ""))}`
        ),
      })),
      subscriptions: {
        creator: PurchaseLinks.withTracking(baseUrl, "/checkout/subscribe/creator"),
      },
    }
  }

  static recommendBundle(bundles, neededCredits) {
    const normalizedNeeded = Math.max(
      1,
      Math.round(PurchaseLinks.toNumeric(neededCredits, 1))
    )
    const sorted = [...(bundles || [])].sort((a, b) => {
      const aCredits = PurchaseLinks.toNumeric(a.credits)
      const bCredits = PurchaseLinks.toNumeric(b.credits)
      return aCredits - bCredits
    })

    return (
      sorted.find((bundle) => PurchaseLinks.toNumeric(bundle.credits) >= normalizedNeeded) ||
      sorted[sorted.length - 1] ||
      null
    )
  }
}
