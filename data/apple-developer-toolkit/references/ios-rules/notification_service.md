---
description: "Implementation rules for notification service"
---
# Notification Service

NOTIFICATION SERVICE EXTENSION:
SETUP: Requires separate extension target (kind: "notification_service" in plan extensions array).
Used to modify rich push notification content before display (add images, decrypt payload, etc.).

PRINCIPAL CLASS (in extension):
class NotificationService: UNNotificationServiceExtension {
    var contentHandler: ((UNNotificationContent) -> Void)?
    var bestAttemptContent: UNMutableNotificationContent?

    override func didReceive(_ request: UNNotificationRequest,
                             withContentHandler contentHandler: @escaping (UNNotificationContent) -> Void) {
        self.contentHandler = contentHandler
        bestAttemptContent = (request.content.mutableCopy() as? UNMutableNotificationContent)

        guard let bestAttemptContent else { contentHandler(request.content); return }

        // Modify content here — e.g., download and attach image
        if let urlString = request.content.userInfo["image_url"] as? String,
           let url = URL(string: urlString) {
            downloadAndAttach(url: url, to: bestAttemptContent) { modified in
                contentHandler(modified)
            }
        } else {
            bestAttemptContent.title = "[Modified] " + bestAttemptContent.title
            contentHandler(bestAttemptContent)
        }
    }

    override func serviceExtensionTimeWillExpire() {
        // Called just before extension is killed — deliver best attempt
        if let contentHandler, let bestAttemptContent {
            contentHandler(bestAttemptContent)
        }
    }
}

ADDING ATTACHMENT:
func downloadAndAttach(url: URL, to content: UNMutableNotificationContent, completion: @escaping (UNNotificationContent) -> Void) {
    URLSession.shared.downloadTask(with: url) { localURL, _, _ in
        if let localURL, let attachment = try? UNNotificationAttachment(identifier: "image", url: localURL) {
            content.attachments = [attachment]
        }
        completion(content)
    }.resume()
}
