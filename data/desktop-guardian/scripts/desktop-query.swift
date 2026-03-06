import Foundation
import CoreGraphics
import AppKit

// Desktop Guardian v2 — Swift CLI fallback for degraded mode (no Hammerspoon)
// Zero permissions needed: CGWindowList + NSWorkspace
// Compile: swiftc -O desktop-query.swift -o desktop-query

func main() -> Never {
    let dialogOwners: Set<String> = [
        "UserNotificationCenter", "CoreServicesUIAgent", "SecurityAgent",
        "SystemUIServer", "universalAccessAuthWarn", "AXVisualSupportAgent",
        "coreauthd"
    ]

    var windowsByApp: [String: [[String: Any]]] = [:]
    var dialogList: [[String: Any]] = []

    // CGWindowList: on-screen windows
    if let windowList = CGWindowListCopyWindowInfo([.optionOnScreenOnly], kCGNullWindowID) as? [[String: Any]] {
        for win in windowList {
            guard let ownerName = win[kCGWindowOwnerName as String] as? String else { continue }
            let layer = win[kCGWindowLayer as String] as? Int ?? 0
            let title = win[kCGWindowName as String] as? String ?? ""
            let wid = win[kCGWindowNumber as String] as? Int ?? 0

            if layer == 0 {
                let winInfo: [String: Any] = ["id": wid, "title": title, "minimized": false, "fullscreen": false]
                windowsByApp[ownerName, default: []].append(winInfo)
            } else if dialogOwners.contains(ownerName) {
                dialogList.append([
                    "app": ownerName,
                    "bundleId": "",
                    "title": title,
                    "buttons": [] as [String],  // Can't detect buttons without Accessibility
                    "defaultButton": NSNull(),
                    "windowId": wid
                ])
            }
        }
    }

    // NSWorkspace: running GUI apps
    var apps: [[String: Any]] = []
    var summary: [String: Any] = ["totalWindows": 0, "windowsByApp": [:] as [String: Int], "dialogCount": dialogList.count]
    var totalWindows = 0
    var windowCounts: [String: Int] = [:]

    for app in NSWorkspace.shared.runningApplications {
        guard app.activationPolicy == .regular else { continue }
        let name = app.localizedName ?? "Unknown"
        let wins = windowsByApp[name] ?? []
        apps.append([
            "name": name,
            "bundleId": app.bundleIdentifier ?? "",
            "pid": app.processIdentifier,
            "windowCount": wins.count,
            "windows": wins,
            "hidden": app.isHidden
        ])
        totalWindows += wins.count
        windowCounts[name] = wins.count
    }

    summary["totalWindows"] = totalWindows
    summary["windowsByApp"] = windowCounts

    let formatter = ISO8601DateFormatter()
    formatter.formatOptions = [.withInternetDateTime]
    formatter.timeZone = TimeZone.current

    let front = NSWorkspace.shared.frontmostApplication?.localizedName ?? ""

    let output: [String: Any] = [
        "timestamp": formatter.string(from: Date()),
        "frontmostApp": front,
        "apps": apps,
        "dialogs": dialogList,
        "chromeTabs": ["count": -1, "tabs": [] as [Any], "cdpAvailable": false] as [String: Any],
        "summary": summary
    ]

    do {
        let data = try JSONSerialization.data(withJSONObject: output, options: [.prettyPrinted, .sortedKeys])
        if let json = String(data: data, encoding: .utf8) {
            print(json)
        }
    } catch {
        print("{\"error\":\"json serialization failed\"}")
    }

    exit(0)
}

main()
