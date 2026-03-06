---
description: "Implementation rules for safari extension"
---
# Safari Extension

SAFARI WEB EXTENSION:
SETUP: Requires separate extension target (kind: "safari" in plan extensions array).
Safari Web Extensions use web technologies (JS/HTML/CSS) plus a native Swift wrapper.

SWIFT EXTENSION HANDLER (optional — for native communication):
class SafariExtensionHandler: SFSafariExtensionHandler {
    // Called when toolbar button is clicked
    override func toolbarItemClicked(in window: SFSafariWindow) {
        window.getActiveTab { tab in
            tab?.getActivePage { page in
                page?.dispatchMessageToScript(withName: "buttonClicked", userInfo: [:])
            }
        }
    }

    // Receive messages from JavaScript content scripts
    override func messageReceived(withName messageName: String, from page: SFSafariPage, userInfo: [String: Any]?) {
        // Handle message from JS: page.dispatchMessageToExtension(...)
    }
}

INFO.PLIST KEYS (extension):
NSExtensionPrincipalClass: $(PRODUCT_MODULE_NAME).SafariExtensionHandler
NSExtensionAttributes:
  SFSafariWebsiteAccess: { Level: All }

WEB EXTENSION RESOURCES (in extension bundle):
- manifest.json (Web Extension manifest v3)
- background.js (service worker)
- content.js (injected into pages)
- popup.html (toolbar popup)

ENABLE IN SAFARI: User must enable in Safari → Settings → Extensions.
