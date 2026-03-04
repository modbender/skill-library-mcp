# Mobile Encryption Patterns

## iOS Keychain Wrapper

```swift
import Security

class KeychainHelper {
    static func save(key: String, data: Data) -> Bool {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrAccount as String: key,
            kSecValueData as String: data,
            kSecAttrAccessible as String: kSecAttrAccessibleWhenUnlockedThisDeviceOnly
        ]
        SecItemDelete(query as CFDictionary)
        return SecItemAdd(query as CFDictionary, nil) == errSecSuccess
    }
    
    static func load(key: String) -> Data? {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrAccount as String: key,
            kSecReturnData as String: true,
            kSecMatchLimit as String: kSecMatchLimitOne
        ]
        var result: AnyObject?
        SecItemCopyMatching(query as CFDictionary, &result)
        return result as? Data
    }
}
```

## Android EncryptedSharedPreferences

```kotlin
import androidx.security.crypto.EncryptedSharedPreferences
import androidx.security.crypto.MasterKey

val masterKey = MasterKey.Builder(context)
    .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
    .build()

val prefs = EncryptedSharedPreferences.create(
    context,
    "secure_prefs",
    masterKey,
    EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
    EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
)

// Use like regular SharedPreferences
prefs.edit().putString("token", secretToken).apply()
```

## SQLCipher Setup

### iOS (GRDB + SQLCipher)
```swift
var config = Configuration()
config.prepareDatabase { db in
    try db.usePassphrase(getKeyFromKeychain())
}
let dbQueue = try DatabaseQueue(path: dbPath, configuration: config)
```

### Android (SQLCipher + Room)
```kotlin
val passphrase = SQLiteDatabase.getBytes(getKeyFromKeystore())
val factory = SupportFactory(passphrase)
Room.databaseBuilder(context, AppDatabase::class.java, "app.db")
    .openHelperFactory(factory)
    .build()
```

## Biometric Authentication

### iOS Face ID / Touch ID
```swift
import LocalAuthentication

let context = LAContext()
var error: NSError?

if context.canEvaluatePolicy(.deviceOwnerAuthenticationWithBiometrics, error: &error) {
    context.evaluatePolicy(.deviceOwnerAuthenticationWithBiometrics,
                          localizedReason: "Unlock secure data") { success, error in
        if success {
            // Release key from Keychain
        } else {
            // Fall back to PIN
        }
    }
}
```

### Android BiometricPrompt
```kotlin
val promptInfo = BiometricPrompt.PromptInfo.Builder()
    .setTitle("Unlock")
    .setNegativeButtonText("Use PIN")
    .setAllowedAuthenticators(BIOMETRIC_STRONG)
    .build()

val biometricPrompt = BiometricPrompt(this, executor,
    object : BiometricPrompt.AuthenticationCallback() {
        override fun onAuthenticationSucceeded(result: AuthenticationResult) {
            val cipher = result.cryptoObject?.cipher
            // Use cipher to decrypt key
        }
    })
biometricPrompt.authenticate(promptInfo, CryptoObject(cipher))
```

## Certificate Pinning

### iOS (URLSession)
```swift
class PinningDelegate: NSObject, URLSessionDelegate {
    let pinnedHash = "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA="
    
    func urlSession(_ session: URLSession, didReceive challenge: URLAuthenticationChallenge,
                   completionHandler: @escaping (URLSession.AuthChallengeDisposition, URLCredential?) -> Void) {
        guard let trust = challenge.protectionSpace.serverTrust,
              let cert = SecTrustGetCertificateAtIndex(trust, 0) else {
            completionHandler(.cancelAuthenticationChallenge, nil)
            return
        }
        let pubKey = SecCertificateCopyKey(cert)!
        let pubKeyData = SecKeyCopyExternalRepresentation(pubKey, nil)! as Data
        let hash = SHA256.hash(data: pubKeyData).base64EncodedString()
        
        if hash == pinnedHash {
            completionHandler(.useCredential, URLCredential(trust: trust))
        } else {
            completionHandler(.cancelAuthenticationChallenge, nil)
        }
    }
}
```

### Android (network_security_config.xml)
```xml
<?xml version="1.0" encoding="utf-8"?>
<network-security-config>
    <domain-config>
        <domain includeSubdomains="true">api.example.com</domain>
        <pin-set expiration="2025-01-01">
            <pin digest="SHA-256">AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=</pin>
            <!-- Backup pin -->
            <pin digest="SHA-256">BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB=</pin>
        </pin-set>
    </domain-config>
</network-security-config>
```
