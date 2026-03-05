# RevenueCat — Cross-Platform Subscriptions

## Why RevenueCat

- Single SDK for iOS, Android, Flutter, React Native, web
- Server-side receipt validation handled
- Cross-platform entitlement sync
- Built-in analytics dashboard
- Webhooks for server events
- Free up to $2.5k MTR, then 1%

## Setup

### iOS

```swift
import RevenueCat

func application(_ application: UIApplication,
                 didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?) -> Bool {
    Purchases.logLevel = .debug
    Purchases.configure(withAPIKey: "appl_your_api_key")
    return true
}
```

### Android

```kotlin
// Application class
class App : Application() {
    override fun onCreate() {
        super.onCreate()
        Purchases.logLevel = LogLevel.DEBUG
        Purchases.configure(PurchasesConfiguration.Builder(this, "goog_your_api_key").build())
    }
}
```

### Flutter

```dart
import 'package:purchases_flutter/purchases_flutter.dart';

Future<void> initRevenueCat() async {
  await Purchases.setLogLevel(LogLevel.debug);
  
  final config = PurchasesConfiguration(
    Platform.isIOS ? 'appl_xxx' : 'goog_xxx'
  );
  await Purchases.configure(config);
}
```

## User Identification

```swift
// Anonymous by default - RevenueCat generates ID
// Link to your user system:
Purchases.shared.logIn("your_user_id") { customerInfo, created, error in
    // created = true if new RevenueCat user was created
    // false if existing user was found
}

// On logout
Purchases.shared.logOut { customerInfo, error in }
```

## Fetch Offerings

Offerings = groups of products configured in RevenueCat dashboard.

```swift
Purchases.shared.getOfferings { offerings, error in
    guard let offerings = offerings else { return }
    
    // Current offering (the one you want to show)
    if let current = offerings.current {
        // Packages within the offering
        let monthly = current.monthly  // StandardPackage
        let annual = current.annual
        let lifetime = current.lifetime
        
        // Or get all packages
        let packages = current.availablePackages
    }
}
```

```dart
// Flutter
final offerings = await Purchases.getOfferings();
final current = offerings.current;
final packages = current?.availablePackages ?? [];

// Display
for (final package in packages) {
  print('${package.identifier}: ${package.storeProduct.priceString}');
}
```

## Purchase

```swift
Purchases.shared.purchase(package: package) { transaction, customerInfo, error, userCancelled in
    if let error = error {
        // Handle error
        return
    }
    if userCancelled {
        return
    }
    
    // Check entitlements
    if customerInfo?.entitlements["premium"]?.isActive == true {
        // Unlock premium
    }
}
```

```dart
// Flutter
try {
  final customerInfo = await Purchases.purchasePackage(package);
  if (customerInfo.entitlements.all['premium']?.isActive ?? false) {
    // Unlock premium
  }
} on PlatformException catch (e) {
  final errorCode = PurchasesErrorHelper.getErrorCode(e);
  if (errorCode != PurchasesErrorCode.purchaseCancelledError) {
    // Handle error
  }
}
```

## Check Entitlements

```swift
Purchases.shared.getCustomerInfo { customerInfo, error in
    if customerInfo?.entitlements["premium"]?.isActive == true {
        // User has premium
    }
}

// Or listen for changes
Purchases.shared.delegate = self

func purchases(_ purchases: Purchases, receivedUpdated customerInfo: CustomerInfo) {
    // Update UI based on customerInfo.entitlements
}
```

```dart
// Flutter - one-time check
final customerInfo = await Purchases.getCustomerInfo();
final isPremium = customerInfo.entitlements.all['premium']?.isActive ?? false;

// Listen for changes
Purchases.addCustomerInfoUpdateListener((customerInfo) {
  // Update state
});
```

## Restore Purchases

```swift
Purchases.shared.restorePurchases { customerInfo, error in
    // customerInfo contains restored entitlements
}
```

## Offerings Configuration (Dashboard)

1. **Products** → Create products matching App Store Connect / Play Console
2. **Entitlements** → Group products that unlock same features
3. **Offerings** → Create packages (monthly, annual, lifetime)
4. **Current Offering** → Which offering to show by default

Structure:
```
Offering: "default"
├── Package: "monthly" → Product: $4.99/month → Entitlement: "premium"
├── Package: "annual" → Product: $29.99/year → Entitlement: "premium"
└── Package: "lifetime" → Product: $79.99 → Entitlement: "premium"
```

## Webhooks

Configure in RevenueCat dashboard → Integrations → Webhooks.

```javascript
// Express endpoint
app.post('/revenuecat/webhook', (req, res) => {
  const event = req.body;
  
  switch (event.type) {
    case 'INITIAL_PURCHASE':
      grantAccess(event.app_user_id, event.product_id);
      break;
    case 'RENEWAL':
      extendAccess(event.app_user_id);
      break;
    case 'CANCELLATION':
      // User cancelled - will expire at period end
      markWillExpire(event.app_user_id);
      break;
    case 'EXPIRATION':
      revokeAccess(event.app_user_id);
      break;
    case 'BILLING_ISSUE':
      sendPaymentFailedEmail(event.app_user_id);
      break;
    case 'SUBSCRIBER_ALIAS':
      // User IDs merged
      break;
  }
  
  res.sendStatus(200);
});
```

Event types:
- INITIAL_PURCHASE
- RENEWAL
- CANCELLATION
- UNCANCELLATION
- EXPIRATION
- BILLING_ISSUE
- PRODUCT_CHANGE (upgrade/downgrade)
- TRANSFER (cross-platform)

## REST API

```bash
# Get subscriber info
curl -X GET \
  "https://api.revenuecat.com/v1/subscribers/$USER_ID" \
  -H "Authorization: Bearer $SECRET_API_KEY"

# Grant entitlement (promo)
curl -X POST \
  "https://api.revenuecat.com/v1/subscribers/$USER_ID/entitlements/$ENTITLEMENT_ID/promotional" \
  -H "Authorization: Bearer $SECRET_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"duration": "monthly"}'

# Revoke entitlement
curl -X POST \
  "https://api.revenuecat.com/v1/subscribers/$USER_ID/entitlements/$ENTITLEMENT_ID/revoke_promotionals" \
  -H "Authorization: Bearer $SECRET_API_KEY"
```

## Paywalls (RevenueCat Paywalls)

RevenueCat has native paywall templates:

```swift
import RevenueCatUI

// Present paywall
let paywallView = PaywallView()

// Or with options
PaywallView(
    offering: offerings.current,
    displayCloseButton: true
)

// Full-screen controller
let controller = PaywallViewController()
present(controller, animated: true)
```

```dart
// Flutter
import 'package:purchases_ui_flutter/purchases_ui_flutter.dart';

await RevenueCatUI.presentPaywall();

// Or with options
await RevenueCatUI.presentPaywallIfNeeded(
  requiredEntitlementIdentifier: 'premium',
);
```

## Debugging

```swift
// Enable debug logs
Purchases.logLevel = .debug

// Check configuration
Purchases.shared.getOfferings { offerings, error in
    print("Offerings: \(offerings?.all.keys ?? [])")
    print("Current: \(offerings?.current?.identifier ?? "none")")
}
```

Common issues:
- Products not loading → check API key, product IDs
- Entitlements not updating → check dashboard configuration
- Webhooks not firing → verify endpoint URL, check logs

## Testing

1. **Sandbox accounts** for iOS
2. **License testers** for Android (add in Play Console)
3. RevenueCat dashboard shows real-time events
4. Use `Purchases.logLevel = .debug` during development
