import { SpendPolicyGuard } from "../lib/spend-policy.mjs"

export class ThumbnailsTool {
  static normalizeVariants(value) {
    if (!Number.isFinite(Number(value))) {
      return 1
    }
    return Math.min(3, Math.max(1, Math.round(Number(value))))
  }

  static getRequestedVariants(variantCount) {
    const variants = ["A", "B", "C"]
    return variants.slice(0, Math.min(3, Math.max(1, variantCount)))
  }

  static calculateEstimatedCreatorCost({
    pricing,
    existingThumbnails,
    requestedVariantCount,
    premiumQuality,
  }) {
    const requestedVariants = ThumbnailsTool.getRequestedVariants(
      requestedVariantCount
    )
    const existingVariants = new Set(
      (existingThumbnails || [])
        .map((item) => String(item?.variant || "").trim().toUpperCase())
        .filter(Boolean)
    )
    const missingCount = requestedVariants.filter(
      (variant) => !existingVariants.has(variant)
    ).length
    const perVariantCost = Number(
      premiumQuality
        ? pricing?.thumbnails?.premium?.costPerVariant
        : pricing?.thumbnails?.standard?.costPerVariant
    )

    const normalizedPerVariantCost = Number.isFinite(perVariantCost)
      ? perVariantCost
      : premiumQuality
        ? 32
        : 8

    return {
      requestedVariants,
      missingVariants: missingCount,
      creatorCredits: Math.max(
        0,
        Math.round(missingCount * normalizedPerVariantCost)
      ),
    }
  }

  static async execute(context, params) {
    const projectId = String(params?.project_id || "").trim()
    if (!projectId) {
      throw new Error("project_id is required")
    }

    const variants = ThumbnailsTool.normalizeVariants(params?.variants)
    const premiumQuality = Boolean(params?.premium_quality)
    const hasBrandColors = Object.prototype.hasOwnProperty.call(
      params || {},
      "use_brand_colors"
    )
    const hasBrandFaces = Object.prototype.hasOwnProperty.call(
      params || {},
      "use_brand_faces"
    )

    const payload = {
      variants,
      premiumQuality,
      ...(hasBrandColors
        ? { useBrandColors: Boolean(params.use_brand_colors) }
        : {}),
      ...(hasBrandFaces
        ? { useBrandFaces: Boolean(params.use_brand_faces) }
        : {}),
    }

    const [pricing, existing] = await Promise.all([
      context.apiClient.getPricing().catch(() => null),
      context.apiClient
        .listProjectThumbnails(projectId)
        .catch(() => ({ thumbnails: [] })),
    ])

    const costEstimate = ThumbnailsTool.calculateEstimatedCreatorCost({
      pricing,
      existingThumbnails: existing?.thumbnails || [],
      requestedVariantCount: variants,
      premiumQuality,
    })

    const spendAuthorization = await SpendPolicyGuard.authorizeAction(
      context,
      {
        action: "thumbnails_generate",
        actionLabel: "Generate thumbnails",
        estimatedCost: {
          apiCredits: 0,
          creatorCredits: costEstimate.creatorCredits,
        },
        confirmSpend: Boolean(params?.confirm_spend),
        pricing,
      }
    )

    const result = await context.apiClient.generateProjectThumbnails(
      projectId,
      payload
    )

    return {
      projectId,
      spendPolicy: spendAuthorization.policy?.mode || "smart",
      estimatedCost: spendAuthorization.estimatedCost,
      ...result,
    }
  }
}
