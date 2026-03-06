---
description: "Implementation rules for share extension"
---
# Share Extension

SHARE EXTENSION:
SETUP: Requires separate extension target (kind: "share" in plan extensions array).
The extension receives shared content (URLs, text, images) from other apps via the share sheet.

PRINCIPAL CLASS (in extension target):
class ShareViewController: SLComposeServiceViewController {
    override func isContentValid() -> Bool {
        return contentText.count > 0    // Validate before enabling Post button
    }

    override func didSelectPost() {
        // Access shared items
        guard let item = extensionContext?.inputItems.first as? NSExtensionItem,
              let provider = item.attachments?.first else {
            extensionContext?.completeRequest(returningItems: [], completionHandler: nil)
            return
        }

        if provider.hasItemConformingToTypeIdentifier("public.url") {
            provider.loadItem(forTypeIdentifier: "public.url") { [weak self] url, _ in
                // Handle URL
                self?.extensionContext?.completeRequest(returningItems: [], completionHandler: nil)
            }
        }
    }

    override func configurationItems() -> [Any]! {
        return []    // Return SLComposeSheetConfigurationItem array for optional UI
    }
}

INFO.PLIST KEYS (in extension's Info.plist via XcodeGen):
NSExtensionPrincipalClass: $(PRODUCT_MODULE_NAME).ShareViewController
NSExtensionActivationRule:
  NSExtensionActivationSupportsWebURLWithMaxCount: 1
  NSExtensionActivationSupportsText: true

APP GROUP: Use AppGroup entitlement to share data between main app and extension.
