#!/usr/bin/env swift

/**
 * contacts-query — Apple Contacts CLI
 *
 * A lightweight Swift CLI that queries the macOS Contacts framework (CNContactStore).
 * Triggers proper macOS permission prompts on first run.
 *
 * Usage:
 *   contacts-query search "Miriam"           # Search by name (fuzzy)
 *   contacts-query lookup "+14165692140"      # Reverse lookup by phone
 *   contacts-query list [--limit N]           # List contacts with phone numbers
 *
 * Output format (pipe-friendly):
 *   FirstName|LastName|PhoneNumber|PhoneLabel
 *
 * SECURITY NOTE: This file contains NO SQL. All contact data is accessed exclusively
 * through Apple's CNContactStore framework API (Contacts.framework). String
 * interpolation is used only for formatting pipe-delimited output to stdout and
 * writing error messages to stderr — not for constructing database queries.
 */

import Contacts
import Foundation

// MARK: - Helpers

func requestAccess() -> Bool {
    let store = CNContactStore()
    let semaphore = DispatchSemaphore(value: 0)
    var granted = false

    store.requestAccess(for: .contacts) { success, error in
        granted = success
        if let error = error {
            fputs("Error requesting contacts access: \(error.localizedDescription)\n", stderr)
        }
        semaphore.signal()
    }

    semaphore.wait()
    return granted
}

func formatPhone(_ phone: String) -> String {
    // Strip formatting for display consistency
    return phone.trimmingCharacters(in: .whitespaces)
}

func labelName(_ label: String?) -> String {
    guard let label = label else { return "" }
    // CNLabeledValue labels look like "_$!<Mobile>!$_" — extract the readable part
    if let localizedLabel = CNLabeledValue<NSString>.localizedString(forLabel: label) as String? {
        return localizedLabel
    }
    return label
}

func normalizeDigits(_ phone: String) -> String {
    return phone.filter { $0.isNumber }
}

// MARK: - Commands

func searchByName(_ query: String) {
    let store = CNContactStore()
    let keysToFetch: [CNKeyDescriptor] = [
        CNContactGivenNameKey as CNKeyDescriptor,
        CNContactFamilyNameKey as CNKeyDescriptor,
        CNContactNicknameKey as CNKeyDescriptor,
        CNContactOrganizationNameKey as CNKeyDescriptor,
        CNContactPhoneNumbersKey as CNKeyDescriptor,
    ]

    let predicate = CNContact.predicateForContacts(matchingName: query)

    do {
        let contacts = try store.unifiedContacts(matching: predicate, keysToFetch: keysToFetch)

        if contacts.isEmpty {
            print("No contacts found for \"\(query)\"")
            return
        }

        for contact in contacts {
            for phone in contact.phoneNumbers {
                let label = labelName(phone.label)
                let number = formatPhone(phone.value.stringValue)
                print("\(contact.givenName)|\(contact.familyName)|\(number)|\(label)")
            }
        }
    } catch {
        fputs("Error searching contacts: \(error.localizedDescription)\n", stderr)
        exit(1)
    }
}

func lookupByPhone(_ phoneQuery: String) {
    let store = CNContactStore()
    let keysToFetch: [CNKeyDescriptor] = [
        CNContactGivenNameKey as CNKeyDescriptor,
        CNContactFamilyNameKey as CNKeyDescriptor,
        CNContactPhoneNumbersKey as CNKeyDescriptor,
    ]

    // Normalize the query to digits for comparison
    let queryDigits = normalizeDigits(phoneQuery)
    let querySuffix = String(queryDigits.suffix(10)) // Last 10 digits (strip country code)

    guard querySuffix.count >= 7 else {
        fputs("Phone number too short (need at least 7 digits)\n", stderr)
        exit(1)
    }

    // CNContact doesn't have a phone predicate, so we fetch all and filter
    do {
        // Try fetching from all containers
        let containers = try store.containers(matching: nil)
        var found = false

        for container in containers {
            let containerPredicate = CNContact.predicateForContactsInContainer(withIdentifier: container.identifier)
            let contacts = try store.unifiedContacts(matching: containerPredicate, keysToFetch: keysToFetch)

            for contact in contacts {
                for phone in contact.phoneNumbers {
                    let phoneDigits = normalizeDigits(phone.value.stringValue)
                    let phoneSuffix = String(phoneDigits.suffix(10))

                    if phoneSuffix == querySuffix {
                        let label = labelName(phone.label)
                        let number = formatPhone(phone.value.stringValue)
                        print("\(contact.givenName)|\(contact.familyName)|\(number)|\(label)")
                        found = true
                    }
                }
            }
        }

        if !found {
            print("No contacts found for phone \"\(phoneQuery)\"")
        }
    } catch {
        fputs("Error looking up phone: \(error.localizedDescription)\n", stderr)
        exit(1)
    }
}

func listContacts(_ limit: Int) {
    let store = CNContactStore()
    let keysToFetch: [CNKeyDescriptor] = [
        CNContactGivenNameKey as CNKeyDescriptor,
        CNContactFamilyNameKey as CNKeyDescriptor,
        CNContactPhoneNumbersKey as CNKeyDescriptor,
    ]

    do {
        let containers = try store.containers(matching: nil)
        var count = 0

        for container in containers {
            if count >= limit { break }
            let predicate = CNContact.predicateForContactsInContainer(withIdentifier: container.identifier)
            let contacts = try store.unifiedContacts(matching: predicate, keysToFetch: keysToFetch)

            for contact in contacts {
                if count >= limit { break }
                if contact.phoneNumbers.isEmpty { continue }

                for phone in contact.phoneNumbers {
                    let label = labelName(phone.label)
                    let number = formatPhone(phone.value.stringValue)
                    print("\(contact.givenName)|\(contact.familyName)|\(number)|\(label)")
                }
                count += 1
            }
        }

        if count == 0 {
            print("No contacts with phone numbers found.")
        }
    } catch {
        fputs("Error listing contacts: \(error.localizedDescription)\n", stderr)
        exit(1)
    }
}

// MARK: - Main

let args = CommandLine.arguments

guard args.count >= 2 else {
    fputs("""
    Usage:
      contacts-query search "name"          Search by name
      contacts-query lookup "+14165551234"  Reverse lookup by phone
      contacts-query list [--limit N]       List contacts with phones

    Output format: FirstName|LastName|PhoneNumber|PhoneLabel
    
    """, stderr)
    exit(1)
}

// Try to request access — may succeed if run interactively, may fail if child process.
// Either way, we attempt the query — some macOS versions allow inherited access.
let _ = requestAccess()

let command = args[1].lowercased()

switch command {
case "search":
    guard args.count >= 3 else {
        fputs("Usage: contacts-query search \"name\"\n", stderr)
        exit(1)
    }
    searchByName(args[2])

case "lookup":
    guard args.count >= 3 else {
        fputs("Usage: contacts-query lookup \"+14165551234\"\n", stderr)
        exit(1)
    }
    lookupByPhone(args[2])

case "list":
    var limit = 20
    if args.count >= 4 && args[2] == "--limit" {
        limit = Int(args[3]) ?? 20
    }
    listContacts(limit)

default:
    fputs("Unknown command: \(command). Use search, lookup, or list.\n", stderr)
    exit(1)
}
