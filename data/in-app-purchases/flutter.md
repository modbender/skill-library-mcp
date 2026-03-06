# Flutter In-App Purchases

## Package Options

| Package | Use Case |
|---------|----------|
| `in_app_purchase` | Official Flutter plugin, full control |
| `purchases_flutter` | RevenueCat SDK, managed backend |

## in_app_purchase (Official)

### Setup

```yaml
# pubspec.yaml
dependencies:
  in_app_purchase: ^3.1.0
```

iOS: No additional setup required.

Android: Add billing permission (usually auto-included).

### Initialize

```dart
import 'package:in_app_purchase/in_app_purchase.dart';

class IAPService {
  final InAppPurchase _iap = InAppPurchase.instance;
  StreamSubscription<List<PurchaseDetails>>? _subscription;
  
  Future<void> initialize() async {
    final available = await _iap.isAvailable();
    if (!available) return;
    
    _subscription = _iap.purchaseStream.listen(_onPurchaseUpdate);
  }
  
  void dispose() {
    _subscription?.cancel();
  }
}
```

### Fetch Products

```dart
Future<List<ProductDetails>> fetchProducts(Set<String> productIds) async {
  final response = await _iap.queryProductDetails(productIds);
  
  if (response.notFoundIDs.isNotEmpty) {
    debugPrint('Products not found: ${response.notFoundIDs}');
  }
  
  return response.productDetails;
}
```

### Purchase

```dart
Future<bool> purchase(ProductDetails product) async {
  final purchaseParam = PurchaseParam(productDetails: product);
  
  if (product.id.contains('subscription')) {
    return await _iap.buyNonConsumable(purchaseParam: purchaseParam);
  } else {
    return await _iap.buyConsumable(purchaseParam: purchaseParam);
  }
}
```

### Handle Updates

```dart
void _onPurchaseUpdate(List<PurchaseDetails> purchases) {
  for (final purchase in purchases) {
    switch (purchase.status) {
      case PurchaseStatus.purchased:
      case PurchaseStatus.restored:
        _verifyAndDeliver(purchase);
        break;
      case PurchaseStatus.pending:
        // Show pending UI
        break;
      case PurchaseStatus.error:
        _handleError(purchase.error!);
        break;
      case PurchaseStatus.canceled:
        // User cancelled
        break;
    }
  }
}

Future<void> _verifyAndDeliver(PurchaseDetails purchase) async {
  // Verify on your server
  final verified = await _verifyOnServer(purchase);
  
  if (verified) {
    // Grant entitlement
    await _grantEntitlement(purchase.productID);
  }
  
  // Complete the purchase
  if (purchase.pendingCompletePurchase) {
    await _iap.completePurchase(purchase);
  }
}
```

### Restore Purchases

```dart
Future<void> restorePurchases() async {
  await _iap.restorePurchases();
  // Results come through purchaseStream
}
```

## RevenueCat (purchases_flutter)

### Setup

```yaml
dependencies:
  purchases_flutter: ^6.0.0
```

### Initialize

```dart
import 'package:purchases_flutter/purchases_flutter.dart';

Future<void> initRevenueCat() async {
  await Purchases.setLogLevel(LogLevel.debug);
  
  PurchasesConfiguration config;
  if (Platform.isIOS) {
    config = PurchasesConfiguration('appl_your_ios_key');
  } else {
    config = PurchasesConfiguration('goog_your_android_key');
  }
  
  await Purchases.configure(config);
}
```

### Fetch Offerings

```dart
Future<Offerings?> fetchOfferings() async {
  try {
    return await Purchases.getOfferings();
  } catch (e) {
    debugPrint('Error fetching offerings: $e');
    return null;
  }
}

// Usage
final offerings = await fetchOfferings();
final currentOffering = offerings?.current;
final packages = currentOffering?.availablePackages;
```

### Purchase

```dart
Future<CustomerInfo?> purchase(Package package) async {
  try {
    final result = await Purchases.purchasePackage(package);
    return result;
  } on PlatformException catch (e) {
    final errorCode = PurchasesErrorHelper.getErrorCode(e);
    if (errorCode != PurchasesErrorCode.purchaseCancelledError) {
      // Handle error
    }
    return null;
  }
}
```

### Check Entitlements

```dart
Future<bool> hasAccess(String entitlementId) async {
  final customerInfo = await Purchases.getCustomerInfo();
  return customerInfo.entitlements.all[entitlementId]?.isActive ?? false;
}
```

### Restore

```dart
Future<CustomerInfo> restorePurchases() async {
  return await Purchases.restorePurchases();
}
```

## Platform-Specific Gotchas

### iOS
- Test with StoreKit Configuration file in Xcode
- Sandbox subscriptions renew every 5 minutes
- Need to handle `SKPaymentTransactionObserver` on native side if mixing

### Android
- Use `flutter clean` after modifying billing setup
- Test with license testing accounts in Play Console
- Handle pending purchases (3D Secure prompts)

## Common Issues

| Issue | Platform | Fix |
|-------|----------|-----|
| Products empty | Both | Verify product IDs match store exactly |
| Purchase hangs | Both | Ensure `completePurchase()` is called |
| Restore fails | iOS | Check sandbox account signed in |
| "Already owned" | Android | Call `completePurchase()` on consumables |
