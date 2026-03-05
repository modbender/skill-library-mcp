# Testing In-App Purchases — Sandbox & Debug

## Test Environments

| Platform | Dev/Debug | Sandbox | Production |
|----------|-----------|---------|------------|
| iOS | StoreKit Config file | Sandbox accounts | Real accounts |
| Android | License testers | Internal testing | Production |
| RevenueCat | Sandbox mode | Sandbox accounts | Production API key |

## iOS Testing

### StoreKit Configuration File (Xcode)

Best for local development - no App Store Connect needed.

1. File → New → File → StoreKit Configuration File
2. Add products matching your planned App Store Connect products
3. Run in simulator or device

```swift
// Products work immediately in Xcode
let products = try await Product.products(for: ["com.app.premium"])
```

Xcode Transaction Manager:
- Approve/decline transactions
- Refund purchases
- Expire subscriptions
- Test interruptions

### Sandbox Accounts

For testing against real App Store infrastructure:

1. App Store Connect → Users and Access → Sandbox Testers
2. Create test account (use fake email you control)
3. On device: Settings → App Store → Sign out
4. In app, purchase triggers sandbox login

Sandbox subscription durations:
| Real | Sandbox |
|------|---------|
| 3 days | 2 min |
| 1 week | 3 min |
| 1 month | 5 min |
| 2 months | 10 min |
| 3 months | 15 min |
| 6 months | 30 min |
| 1 year | 1 hour |

Renewals: Max 6 renewals per subscription, then expires.

### StoreKit Testing in CI

```swift
// Enable testing mode
@available(iOS 15.0, *)
struct StoreKitTestPlan {
    static func runTests() async throws {
        let session = try SKTestSession(configurationFileNamed: "Products")
        session.disableDialogs = true
        session.clearTransactions()
        
        // Test purchase flow
        let products = try await Product.products(for: ["premium"])
        let result = try await products[0].purchase()
        
        // Verify
        guard case .success(let verification) = result,
              case .verified(let transaction) = verification else {
            throw TestError.purchaseFailed
        }
        
        await transaction.finish()
    }
}
```

## Android Testing

### License Testers

1. Play Console → Settings → License testing
2. Add Gmail accounts
3. Those accounts get free purchases in alpha/beta

### Internal Testing Track

1. Play Console → Testing → Internal testing
2. Upload APK/AAB
3. Add testers by email
4. Testers install via Play Store link

### Test Cards

Google provides test card numbers:
- 4111 1111 1111 1111 - Always succeeds
- 4000 0000 0000 0002 - Always declines

### Billing Response Codes

```kotlin
// Force specific responses in test mode
billingClient.queryProductDetailsAsync(params) { result, details ->
    when (result.responseCode) {
        BillingClient.BillingResponseCode.OK -> // Success
        BillingClient.BillingResponseCode.USER_CANCELED -> // User backed out
        BillingClient.BillingResponseCode.SERVICE_UNAVAILABLE -> // Retry
        BillingClient.BillingResponseCode.ITEM_ALREADY_OWNED -> // Already purchased
        BillingClient.BillingResponseCode.ITEM_NOT_OWNED -> // Not owned (for consume)
    }
}
```

## RevenueCat Testing

### Debug Mode

```swift
// Enable verbose logging
Purchases.logLevel = .debug

// Use sandbox environment
Purchases.configure(
    with: Configuration.Builder(withAPIKey: "appl_xxx")
        .with(usesStoreKit2IfAvailable: true)
        .build()
)
```

### Sandbox Detection

```swift
Purchases.shared.getCustomerInfo { info, error in
    if info?.entitlements.verification == .notRequested {
        print("Running in sandbox")
    }
}
```

### Dashboard Sandbox View

RevenueCat dashboard → Toggle "View sandbox data" to see test transactions.

## Common Test Scenarios

### 1. First Purchase
```
1. Fresh install
2. View paywall
3. Select product
4. Complete purchase
5. Verify entitlement granted
6. Verify receipt sent to server
```

### 2. Restore Purchase
```
1. Fresh install on new device
2. Same account signed in
3. Tap restore
4. Verify entitlements restored
5. No duplicate charges
```

### 3. Subscription Renewal
```
1. Purchase subscription (sandbox: 5 min = 1 month)
2. Wait for renewal
3. Verify access extended
4. Verify webhook received (RENEWAL event)
```

### 4. Subscription Cancellation
```
1. Active subscription
2. Cancel via device settings
3. Access continues until period end
4. After period: access revoked
5. Webhook received (EXPIRATION)
```

### 5. Payment Failure (Involuntary Churn)
```
1. Active subscription
2. Simulate payment failure
3. Grace period begins
4. Retry period
5. Eventually expires if not fixed
```

### 6. Upgrade/Downgrade
```
1. Monthly subscription active
2. Upgrade to annual
3. Verify proration correct
4. Old subscription cancelled
5. New subscription active
```

### 7. Refund
```
1. Active purchase
2. Request refund (via Apple/Google)
3. Webhook received (REFUND)
4. Access revoked immediately
```

### 8. Family Sharing (iOS)
```
1. User A purchases
2. User B on family plan
3. User B gets access via family sharing
4. Verify ownershipType is familyShared
```

## Test Checklist

### Before Launch

**Purchases:**
- [ ] Products load correctly
- [ ] Prices display in local currency
- [ ] Purchase flow completes
- [ ] Entitlements granted after purchase
- [ ] Transaction finished (not pending)

**Restoration:**
- [ ] Restore button works
- [ ] Cross-device restore works
- [ ] No duplicate entitlements
- [ ] Family sharing handled

**Subscriptions:**
- [ ] Renewal works
- [ ] Cancellation handled
- [ ] Grace period works
- [ ] Upgrade/downgrade prorates
- [ ] Expiration revokes access

**Edge Cases:**
- [ ] Network offline during purchase
- [ ] App killed during purchase
- [ ] Pending transactions on launch
- [ ] Already owned item
- [ ] Invalid product IDs

**Server:**
- [ ] Webhooks received
- [ ] Receipts validated
- [ ] Entitlements stored
- [ ] Refunds handled

## Debugging Tools

### iOS

```swift
// Print all transactions
for await result in Transaction.all {
    print(result)
}

// Check current entitlements
for await result in Transaction.currentEntitlements {
    if let transaction = try? result.payloadValue {
        print("\(transaction.productID): \(transaction.purchaseDate)")
    }
}
```

### Android

```kotlin
// Log purchase state
billingClient.queryPurchasesAsync(QueryPurchasesParams.newBuilder()
    .setProductType(BillingClient.ProductType.SUBS)
    .build()
) { result, purchases ->
    purchases.forEach { 
        Log.d("IAP", "Purchase: ${it.products} - ${it.purchaseState}")
    }
}
```

### RevenueCat

```swift
// Debug customer info
Purchases.shared.getCustomerInfo { info, error in
    print("Original app user ID: \(info?.originalAppUserId ?? "nil")")
    print("Active subscriptions: \(info?.activeSubscriptions ?? [])")
    print("Entitlements: \(info?.entitlements.active.keys ?? [])")
}
```

## Automated Testing

### Unit Tests (Mocked)

```swift
protocol PurchaseService {
    func purchase(_ productId: String) async throws -> Bool
}

class MockPurchaseService: PurchaseService {
    var shouldSucceed = true
    
    func purchase(_ productId: String) async throws -> Bool {
        if shouldSucceed {
            return true
        } else {
            throw PurchaseError.failed
        }
    }
}

// Test
func testPurchaseSuccess() async throws {
    let mock = MockPurchaseService()
    mock.shouldSucceed = true
    let result = try await mock.purchase("premium")
    XCTAssertTrue(result)
}
```

### Integration Tests (StoreKit Config)

```swift
@available(iOS 15.0, *)
class StoreKitIntegrationTests: XCTestCase {
    var session: SKTestSession!
    
    override func setUp() async throws {
        session = try SKTestSession(configurationFileNamed: "Products")
        session.disableDialogs = true
        session.clearTransactions()
    }
    
    func testPurchaseFlow() async throws {
        // Real StoreKit 2 calls against local config
        let products = try await Product.products(for: ["premium"])
        XCTAssertFalse(products.isEmpty)
        
        let result = try await products[0].purchase()
        
        guard case .success(let verification) = result else {
            XCTFail("Purchase failed")
            return
        }
        
        let transaction = try XCTUnwrap(verification.payloadValue)
        XCTAssertEqual(transaction.productID, "premium")
        
        await transaction.finish()
    }
}
```
