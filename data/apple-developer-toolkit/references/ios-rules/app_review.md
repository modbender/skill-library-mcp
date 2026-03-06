---
description: "Implementation rules for app review"
---
# App Review

APP REVIEW (StoreKit):
- import StoreKit; @Environment(\.requestReview) var requestReview
- Call requestReview() — Apple handles the dialog
- Trigger after meaningful engagement (launchCount >= 5, key task completed)
- Track with @AppStorage("launchCount"), increment in .onAppear of root view
- Apple limits to 3 prompts/year — never on first launch
- Check: never request immediately after error, crash, or purchase
