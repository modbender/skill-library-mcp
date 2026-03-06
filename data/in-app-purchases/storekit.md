# StoreKit 2 — iOS In-App Purchases

## Setup

```swift
import StoreKit

// Define product IDs
enum ProductID: String, CaseIterable {
    case premium = "com.app.premium"
    case credits100 = "com.app.credits.100"
}
```

## Fetching Products

```swift
func fetchProducts() async throws -> [Product] {
    let productIDs = ProductID.allCases.map { $0.rawValue }
    return try await Product.products(for: Set(productIDs))
}
```

## Purchase Flow

```swift
func purchase(_ product: Product) async throws -> Transaction? {
    let result = try await product.purchase()
    
    switch result {
    case .success(let verification):
        let transaction = try checkVerified(verification)
        await transaction.finish()
        return transaction
        
    case .pending:
        // Ask-to-Buy or requires action
        return nil
        
    case .userCancelled:
        return nil
        
    @unknown default:
        return nil
    }
}

func checkVerified<T>(_ result: VerificationResult<T>) throws -> T {
    switch result {
    case .verified(let safe):
        return safe
    case .unverified(_, let error):
        throw error
    }
}
```

## Transaction Observer

```swift
// Start on app launch
func observeTransactionUpdates() -> Task<Void, Never> {
    Task.detached {
        for await result in Transaction.updates {
            guard let transaction = try? result.payloadValue else { continue }
            // Grant entitlement
            await self.updateEntitlements(transaction)
            await transaction.finish()
        }
    }
}
```

## Current Entitlements

```swift
func checkEntitlements() async -> Set<String> {
    var entitlements: Set<String> = []
    
    for await result in Transaction.currentEntitlements {
        guard let transaction = try? result.payloadValue else { continue }
        
        if transaction.revocationDate == nil {
            entitlements.insert(transaction.productID)
        }
    }
    return entitlements
}
```

## Subscriptions

```swift
func checkSubscriptionStatus(_ productID: String) async -> Product.SubscriptionInfo.Status? {
    guard let product = try? await Product.products(for: [productID]).first,
          let subscription = product.subscription else { return nil }
    
    let statuses = try? await subscription.status
    return statuses?.first { $0.state == .subscribed || $0.state == .inGracePeriod }
}

// Subscription states
switch status.state {
case .subscribed:
    // Active subscription
case .inGracePeriod:
    // Payment failed, still has access (prompt to update payment)
case .inBillingRetryPeriod:
    // Payment failing, Apple retrying
case .expired:
    // No longer active
case .revoked:
    // Refunded or family sharing revoked
}
```

## App Store Server API (Server-Side)

Verify transactions server-side using JWS:

```swift
// Transaction contains signedPayload (JWS)
// Send to your server for verification

// Server verifies:
// 1. JWS signature with Apple's public key
// 2. Bundle ID matches
// 3. Transaction hasn't been revoked
```

## Testing

Use StoreKit Testing in Xcode:
1. Create StoreKit Configuration File
2. Define products matching App Store Connect
3. Run in simulator or device
4. Use Xcode's Transaction Manager to simulate states

Sandbox testing:
- Create sandbox tester in App Store Connect
- Sign out of App Store on device
- Purchase triggers sandbox login
- Subscriptions renew quickly (monthly = 5 min)

## Common Issues

| Issue | Cause | Fix |
|-------|-------|-----|
| Products empty | Wrong product IDs | Match App Store Connect exactly |
| Purchase stuck | Transaction not finished | Always call `transaction.finish()` |
| Family sharing not working | Not checking ownershipType | Check `transaction.ownershipType` |
| Renewals not detected | No observer running | Start observer on app launch |
