# Google Play Billing — Android In-App Purchases

## Setup

```kotlin
// build.gradle
implementation("com.android.billingclient:billing-ktx:7.0.0")
```

```kotlin
class BillingManager(private val context: Context) {
    private val purchasesUpdatedListener = PurchasesUpdatedListener { result, purchases ->
        when (result.responseCode) {
            BillingClient.BillingResponseCode.OK -> purchases?.forEach { handlePurchase(it) }
            BillingClient.BillingResponseCode.USER_CANCELED -> { /* Handle cancel */ }
            else -> { /* Handle error */ }
        }
    }
    
    private val billingClient = BillingClient.newBuilder(context)
        .setListener(purchasesUpdatedListener)
        .enablePendingPurchases()
        .build()
}
```

## Connection

```kotlin
suspend fun connect(): Boolean = suspendCoroutine { continuation ->
    billingClient.startConnection(object : BillingClientStateListener {
        override fun onBillingSetupFinished(result: BillingResult) {
            continuation.resume(result.responseCode == BillingClient.BillingResponseCode.OK)
        }
        override fun onBillingServiceDisconnected() {
            // Retry connection
        }
    })
}
```

## Query Products

```kotlin
suspend fun queryProducts(productIds: List<String>, type: ProductType): List<ProductDetails> {
    val params = QueryProductDetailsParams.newBuilder()
        .setProductList(productIds.map { id ->
            QueryProductDetailsParams.Product.newBuilder()
                .setProductId(id)
                .setProductType(type.value)
                .build()
        })
        .build()
    
    val result = billingClient.queryProductDetails(params)
    return result.productDetailsList ?: emptyList()
}

enum class ProductType(val value: String) {
    INAPP(BillingClient.ProductType.INAPP),
    SUBS(BillingClient.ProductType.SUBS)
}
```

## Purchase Flow

```kotlin
fun launchPurchase(activity: Activity, productDetails: ProductDetails, offerToken: String? = null) {
    val productDetailsParams = BillingFlowParams.ProductDetailsParams.newBuilder()
        .setProductDetails(productDetails)
        .apply { offerToken?.let { setOfferToken(it) } }
        .build()
    
    val flowParams = BillingFlowParams.newBuilder()
        .setProductDetailsParamsList(listOf(productDetailsParams))
        .build()
    
    billingClient.launchBillingFlow(activity, flowParams)
}
```

## Handle Purchase

```kotlin
private fun handlePurchase(purchase: Purchase) {
    when (purchase.purchaseState) {
        Purchase.PurchaseState.PURCHASED -> {
            // Verify on server first
            verifyOnServer(purchase.purchaseToken) { verified ->
                if (verified) {
                    grantEntitlement(purchase.products)
                    acknowledgePurchase(purchase)
                }
            }
        }
        Purchase.PurchaseState.PENDING -> {
            // Don't grant access yet - payment pending (3D Secure, etc.)
        }
    }
}

private suspend fun acknowledgePurchase(purchase: Purchase) {
    if (!purchase.isAcknowledged) {
        val params = AcknowledgePurchaseParams.newBuilder()
            .setPurchaseToken(purchase.purchaseToken)
            .build()
        billingClient.acknowledgePurchase(params)
    }
}
```

## Consume Purchase (Consumables)

```kotlin
private suspend fun consumePurchase(purchase: Purchase) {
    val params = ConsumeParams.newBuilder()
        .setPurchaseToken(purchase.purchaseToken)
        .build()
    billingClient.consumePurchase(params)
}
```

## Restore Purchases

```kotlin
suspend fun restorePurchases() {
    // Query INAPP
    val inappResult = billingClient.queryPurchasesAsync(
        QueryPurchasesParams.newBuilder()
            .setProductType(BillingClient.ProductType.INAPP)
            .build()
    )
    
    // Query SUBS
    val subsResult = billingClient.queryPurchasesAsync(
        QueryPurchasesParams.newBuilder()
            .setProductType(BillingClient.ProductType.SUBS)
            .build()
    )
    
    inappResult.purchasesList.forEach { handlePurchase(it) }
    subsResult.purchasesList.forEach { handlePurchase(it) }
}
```

## Server Verification

```kotlin
// Send purchaseToken to your server
// Server verifies with Google Play Developer API:
// GET https://androidpublisher.googleapis.com/androidpublisher/v3/applications/{package}/purchases/products/{productId}/tokens/{token}

data class ServerVerificationRequest(
    val purchaseToken: String,
    val productId: String,
    val packageName: String
)
```

## Subscription Pricing

```kotlin
fun getSubscriptionPrice(productDetails: ProductDetails): String? {
    return productDetails.subscriptionOfferDetails?.firstOrNull()
        ?.pricingPhases?.pricingPhaseList?.firstOrNull()
        ?.formattedPrice
}
```

## Common Issues

| Issue | Cause | Fix |
|-------|-------|-----|
| Auto-refund after 3 days | Purchase not acknowledged | Call acknowledgePurchase() |
| Products not found | Wrong product type | Use INAPP for one-time, SUBS for subscriptions |
| "Item already owned" | Consumable not consumed | Call consumePurchase() |
| Pending purchase stuck | 3D Secure incomplete | Handle PENDING state, wait for completion |
