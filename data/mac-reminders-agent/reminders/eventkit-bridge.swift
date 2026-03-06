#!/usr/bin/env swift

// EventKit bridge for macOS Reminders with native recurrence, edit, delete, complete support
// Usage:
//   swift eventkit-bridge.swift add --title "Meeting" --due "2026-02-10T09:00:00+09:00" --repeat weekly
//   swift eventkit-bridge.swift list --scope today
//   swift eventkit-bridge.swift edit --id "ABC123" --title "New title" --due "2026-03-01T10:00:00+09:00"
//   swift eventkit-bridge.swift delete --id "ABC123"
//   swift eventkit-bridge.swift complete --id "ABC123"

import Foundation
import EventKit

// MARK: - Argument Parsing

func parseArgs(_ args: [String]) -> [String: String] {
    var result: [String: String] = [:]
    var currentKey: String? = nil

    for arg in args {
        if arg.hasPrefix("--") {
            currentKey = String(arg.dropFirst(2))
            result[currentKey!] = ""
        } else if let key = currentKey {
            result[key] = arg
            currentKey = nil
        }
    }

    return result
}

// MARK: - Date Parsing

func parseISO8601(_ dateStr: String) -> DateComponents? {
    let pattern = #"^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})"#
    guard let regex = try? NSRegularExpression(pattern: pattern),
          let match = regex.firstMatch(in: dateStr, range: NSRange(dateStr.startIndex..., in: dateStr)) else {
        return nil
    }

    func group(_ n: Int) -> Int? {
        guard let range = Range(match.range(at: n), in: dateStr) else { return nil }
        return Int(dateStr[range])
    }

    var components = DateComponents()
    components.year = group(1)
    components.month = group(2)
    components.day = group(3)
    components.hour = group(4)
    components.minute = group(5)
    components.second = group(6)

    return components
}

func parseEndDate(_ dateStr: String) -> EKRecurrenceEnd? {
    let pattern = #"^(\d{4})-(\d{2})-(\d{2})$"#
    guard let regex = try? NSRegularExpression(pattern: pattern),
          let match = regex.firstMatch(in: dateStr, range: NSRange(dateStr.startIndex..., in: dateStr)) else {
        return nil
    }

    func group(_ n: Int) -> Int? {
        guard let range = Range(match.range(at: n), in: dateStr) else { return nil }
        return Int(dateStr[range])
    }

    guard let year = group(1), let month = group(2), let day = group(3) else {
        return nil
    }

    var components = DateComponents()
    components.year = year
    components.month = month
    components.day = day

    guard let date = Calendar.current.date(from: components) else {
        return nil
    }

    return EKRecurrenceEnd(end: date)
}

// MARK: - Recurrence Frequency

func parseFrequency(_ freq: String) -> EKRecurrenceFrequency? {
    switch freq.lowercased() {
    case "daily": return .daily
    case "weekly": return .weekly
    case "monthly": return .monthly
    case "yearly": return .yearly
    default: return nil
    }
}

// MARK: - JSON Helpers

func printJSON(_ dict: [String: Any]) {
    if let data = try? JSONSerialization.data(withJSONObject: dict),
       let str = String(data: data, encoding: .utf8) {
        print(str)
    }
}

func printError(_ message: String) {
    printJSON(["ok": false, "error": message])
}

// MARK: - Store Access Helper

func withReminderAccess(_ callback: @escaping (EKEventStore) -> Void) {
    let store = EKEventStore()
    let semaphore = DispatchSemaphore(value: 0)

    store.requestFullAccessToReminders { granted, error in
        defer { semaphore.signal() }

        guard granted else {
            printError("Reminders access denied")
            return
        }

        callback(store)
    }

    semaphore.wait()
}

// MARK: - Fetch Reminder by ID

func fetchReminder(store: EKEventStore, id: String) -> EKReminder? {
    guard let item = store.calendarItem(withIdentifier: id) as? EKReminder else {
        return nil
    }
    return item
}

// MARK: - Format reminder to JSON dict

func reminderToDict(_ r: EKReminder) -> [String: Any] {
    var item: [String: Any] = [
        "id": r.calendarItemIdentifier,
        "title": r.title ?? "",
        "completed": r.isCompleted
    ]

    if let components = r.dueDateComponents,
       let date = Calendar.current.date(from: components) {
        let formatter = ISO8601DateFormatter()
        formatter.formatOptions = [.withInternetDateTime]
        item["due"] = formatter.string(from: date)
    }

    if let notes = r.notes, !notes.isEmpty {
        item["note"] = notes
    }

    if let rules = r.recurrenceRules, !rules.isEmpty {
        let rule = rules[0]
        let freqMap: [EKRecurrenceFrequency: String] = [
            .daily: "daily", .weekly: "weekly", .monthly: "monthly", .yearly: "yearly"
        ]
        item["repeat"] = freqMap[rule.frequency] ?? ""
        item["interval"] = rule.interval
    }

    return item
}

// MARK: - List Command

func listReminders(args: [String: String]) {
    let scope = args["scope"] ?? "week"

    withReminderAccess { store in
        guard let calendar = store.defaultCalendarForNewReminders() else {
            printError("No default calendar")
            return
        }

        let predicate = store.predicateForIncompleteReminders(
            withDueDateStarting: nil,
            ending: nil,
            calendars: [calendar]
        )

        let fetchSemaphore = DispatchSemaphore(value: 0)
        var fetched: [EKReminder] = []

        store.fetchReminders(matching: predicate) { reminders in
            fetched = reminders ?? []
            fetchSemaphore.signal()
        }

        fetchSemaphore.wait()

        // Filter by scope
        let now = Date()
        let cal = Calendar.current

        let filtered: [EKReminder]
        switch scope {
        case "today":
            let startOfDay = cal.startOfDay(for: now)
            let endOfDay = cal.date(byAdding: .day, value: 1, to: startOfDay)!
            filtered = fetched.filter { r in
                guard let dc = r.dueDateComponents, let d = cal.date(from: dc) else { return false }
                return d >= startOfDay && d < endOfDay
            }
        case "week":
            let startDate = cal.date(byAdding: .day, value: -1, to: now)!
            let endDate = cal.date(byAdding: .day, value: 7, to: now)!
            filtered = fetched.filter { r in
                guard let dc = r.dueDateComponents, let d = cal.date(from: dc) else { return false }
                return d >= startDate && d <= endDate
            }
        case "all":
            filtered = fetched
        default:
            filtered = fetched
        }

        let items = filtered.map { reminderToDict($0) }
        printJSON(["ok": true, "items": items])
    }
}

// MARK: - Add Command

func addReminder(args: [String: String]) {
    guard let title = args["title"], !title.isEmpty else {
        printError("--title is required")
        return
    }

    withReminderAccess { store in
        guard let calendar = store.defaultCalendarForNewReminders() else {
            printError("No default calendar")
            return
        }

        let reminder = EKReminder(eventStore: store)
        reminder.title = title
        reminder.calendar = calendar

        if let note = args["note"], !note.isEmpty {
            reminder.notes = note
        }

        if let dueStr = args["due"], !dueStr.isEmpty,
           let components = parseISO8601(dueStr) {
            reminder.dueDateComponents = components

            if let dueDate = Calendar.current.date(from: components) {
                reminder.addAlarm(EKAlarm(absoluteDate: dueDate))
            }
        }

        if let repeatStr = args["repeat"], !repeatStr.isEmpty,
           let frequency = parseFrequency(repeatStr) {

            let interval = Int(args["interval"] ?? "1") ?? 1
            var recurrenceEnd: EKRecurrenceEnd? = nil

            if let endStr = args["repeat-end"], !endStr.isEmpty {
                recurrenceEnd = parseEndDate(endStr)
            }

            let rule = EKRecurrenceRule(
                recurrenceWith: frequency,
                interval: interval,
                end: recurrenceEnd
            )
            reminder.recurrenceRules = [rule]
        }

        do {
            try store.save(reminder, commit: true)

            var result: [String: Any] = [
                "ok": true,
                "id": reminder.calendarItemIdentifier,
                "title": title
            ]

            if let due = args["due"] { result["due"] = due }
            if let note = args["note"] { result["note"] = note }
            if let repeatVal = args["repeat"], !repeatVal.isEmpty {
                result["repeat"] = repeatVal
                let freqMap = ["daily": 0, "weekly": 1, "monthly": 2, "yearly": 3]
                result["frequency"] = freqMap[repeatVal.lowercased()] ?? -1
            }
            if let interval = args["interval"] { result["interval"] = Int(interval) ?? 1 }
            if let repeatEnd = args["repeat-end"] { result["repeatEnd"] = repeatEnd }

            printJSON(result)
        } catch {
            printError(error.localizedDescription)
        }
    }
}

// MARK: - Edit Command

func editReminder(args: [String: String]) {
    guard let id = args["id"], !id.isEmpty else {
        printError("--id is required")
        return
    }

    withReminderAccess { store in
        guard let reminder = fetchReminder(store: store, id: id) else {
            printError("Reminder not found")
            return
        }

        let oldTitle = reminder.title ?? ""

        if let title = args["title"], !title.isEmpty {
            reminder.title = title
        }

        if let note = args["note"] {
            reminder.notes = note.isEmpty ? nil : note
        }

        if let dueStr = args["due"], !dueStr.isEmpty,
           let components = parseISO8601(dueStr) {
            reminder.dueDateComponents = components

            // Update alarm
            if let existingAlarms = reminder.alarms {
                for alarm in existingAlarms {
                    reminder.removeAlarm(alarm)
                }
            }
            if let dueDate = Calendar.current.date(from: components) {
                reminder.addAlarm(EKAlarm(absoluteDate: dueDate))
            }
        }

        // Update recurrence if provided
        if let repeatStr = args["repeat"], !repeatStr.isEmpty {
            if let frequency = parseFrequency(repeatStr) {
                let interval = Int(args["interval"] ?? "1") ?? 1
                var recurrenceEnd: EKRecurrenceEnd? = nil
                if let endStr = args["repeat-end"], !endStr.isEmpty {
                    recurrenceEnd = parseEndDate(endStr)
                }
                let rule = EKRecurrenceRule(
                    recurrenceWith: frequency,
                    interval: interval,
                    end: recurrenceEnd
                )
                reminder.recurrenceRules = [rule]
            }
        }

        do {
            try store.save(reminder, commit: true)
            var result: [String: Any] = [
                "ok": true,
                "id": id,
                "title": reminder.title ?? "",
                "oldTitle": oldTitle
            ]
            if let dc = reminder.dueDateComponents,
               let d = Calendar.current.date(from: dc) {
                let formatter = ISO8601DateFormatter()
                formatter.formatOptions = [.withInternetDateTime]
                result["due"] = formatter.string(from: d)
            }
            printJSON(result)
        } catch {
            printError(error.localizedDescription)
        }
    }
}

// MARK: - Delete Command

func deleteReminder(args: [String: String]) {
    guard let id = args["id"], !id.isEmpty else {
        printError("--id is required")
        return
    }

    withReminderAccess { store in
        guard let reminder = fetchReminder(store: store, id: id) else {
            printError("Reminder not found")
            return
        }

        let title = reminder.title ?? ""

        do {
            try store.remove(reminder, commit: true)
            printJSON(["ok": true, "id": id, "title": title])
        } catch {
            printError(error.localizedDescription)
        }
    }
}

// MARK: - Complete Command

func completeReminder(args: [String: String]) {
    guard let id = args["id"], !id.isEmpty else {
        printError("--id is required")
        return
    }

    withReminderAccess { store in
        guard let reminder = fetchReminder(store: store, id: id) else {
            printError("Reminder not found")
            return
        }

        let title = reminder.title ?? ""
        reminder.isCompleted = true
        reminder.completionDate = Date()

        do {
            try store.save(reminder, commit: true)
            printJSON(["ok": true, "id": id, "title": title, "completed": true])
        } catch {
            printError(error.localizedDescription)
        }
    }
}

// MARK: - Help

func showHelp() {
    print("""
    Usage:
      swift eventkit-bridge.swift list [--scope today|week|all]
      swift eventkit-bridge.swift add --title "TITLE" [--due ISO_DATE] [--note "NOTE"] [--repeat daily|weekly|monthly|yearly] [--interval N] [--repeat-end YYYY-MM-DD]
      swift eventkit-bridge.swift edit --id "ID" [--title "NEW"] [--due ISO_DATE] [--note "NEW"] [--repeat daily|weekly|monthly|yearly]
      swift eventkit-bridge.swift delete --id "ID"
      swift eventkit-bridge.swift complete --id "ID"
    """)
}

// MARK: - Entry Point

let args = CommandLine.arguments
let parsed = parseArgs(Array(args.dropFirst()))
let command = args.count > 1 ? args[1] : ""

switch command {
case "list":
    listReminders(args: parsed)
case "add":
    addReminder(args: parsed)
case "edit":
    editReminder(args: parsed)
case "delete":
    deleteReminder(args: parsed)
case "complete":
    completeReminder(args: parsed)
case "help", "--help", "-h":
    showHelp()
default:
    showHelp()
}
