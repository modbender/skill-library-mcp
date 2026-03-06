---
description: "Implementation rules for website links"
---
# Website Links

WEBSITE LINKS:
- Link("Visit Website", destination: URL(string: "https://...")!) for simple links
- Or @Environment(\.openURL) var openURL; Button { openURL(url) } for custom styling
- No permissions needed for external URLs
- Safari opens by default; use SFSafariViewController via UIViewControllerRepresentable for in-app browser
- Validate URL before force-unwrapping: guard let url = URL(string:) else { return }
