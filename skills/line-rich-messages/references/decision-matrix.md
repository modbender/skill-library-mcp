# LINE UI Decision Matrix

Use this guide to choose the best UI element for your specific scenario on LINE.

| Scenario | Recommended UI | Why? |
| :--- | :--- | :--- |
| **Simple binary choice** (Yes/No) | **Confirm Dialog** | Native system prompt, very clean. |
| **Quick next-step choices** (2-4 options) | **Quick Replies** | Floating bubbles at the bottom; doesn't clutter chat history. |
| **Main menu or feature selection** | **Button Menu** | Persistent card with title and description. Professional look. |
| **Delivering a document/file** | **Button Menu** | Directs user to a Google Drive link via a physical button. |
| **Displaying structured data** | **Markdown Table** | Automatically converts to a professional Flex card. |
| **Sharing a physical location** | **Location Card** | Native map integration. |
| **Event details / Invitations** | **Event Card** | Rich layout with date, time, and location support. |
| **Showing code or logs** | **Code Block** | Converts to a styled card for better mobile readability. |
| **Sharing Copy-Paste Data** (IDs, Keys) | **Plain Text** | **Crucial**: Flex Message text cannot be selected. Use plain text for copy-paste items. |

## Friction Levels (Lower is better)
1. **Quick Reply** (1 tap) - Immediate flow continuation.
2. **Button/Confirm** (1 tap) - Intentional decision.
3. **Table/Link** (1 tap) - Data consumption.
4. **Text Reply** (High friction) - Avoid asking for typed responses if a choice exists.
