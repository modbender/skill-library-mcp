# FOSMVVM ServerRequest Test Generator - Reference Templates

Complete file templates for generating ServerRequest tests.

> **Conceptual context:** See [SKILL.md](SKILL.md) for when and why to use this skill.
> **Architecture context:** See [FOSMVVMArchitecture.md](../../docs/FOSMVVMArchitecture.md)

---

## REMEMBER: TestingApplicationTester.test()

Before using these templates, remember:

```swift
// ✅ Use app.testing().test() with typed ServerRequest
let request = MyRequest(query: .init(...))
try await app.testing().test(request, locale: en) { response in
    // response is TestingServerRequestResponse<MyRequest>
    #expect(response.status == .ok)
    #expect(response.body?.someField == expected)
}

// ❌ NEVER do this - manual URL/path
try await app.test(.GET, "/my_request?id=123") { response in }

// ❌ NEVER do this - manual HTTP construction
let url = URL(string: "http://localhost/path")!
let data = try await URLSession.shared.data(from: url)
```

The templates below show proper ServerRequest testing. The path is derived from the type automatically. Headers and encoding are handled by the infrastructure.

---

## Placeholders

| Placeholder | Replace With | Example |
|-------------|--------------|---------|
| `{Feature}` | Feature or area name (PascalCase) | `Idea`, `User`, `Dashboard` |
| `{feature}` | Same, camelCase | `idea`, `user`, `dashboard` |
| `{Action}` | Operation name | `Create`, `Update`, `Show`, `Delete` |
| `{Target}` | Test target name | `WebServerTests`, `AppTests` |
| `{ViewModelsTarget}` | Shared ViewModels SPM target | `ViewModels` |
| `{WebServerTarget}` | Server-side target | `WebServer`, `AppServer` |
| `{ResourceDir}` | YAML resource directory | `TestYAML`, `Resources` |

---

# Test File Templates

---

## Template 1: Basic ServerRequest Test Suite

For testing a single ServerRequest type with success and error cases.

**Location:** `Tests/{Target}Tests/Requests/{Feature}RequestTests.swift`

```swift
// {Feature}RequestTests.swift
//
// Copyright 2025 {Your Company}
//
// Licensed under the Apache License, Version 2.0 (the  License);
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

import FOSFoundation
@testable import FOSMVVM
@testable import FOSMVVMVapor
import FOSTesting
import FOSTestingVapor
import Foundation
import Testing
import Vapor
import VaporTesting
@testable import {ViewModelsTarget}
@testable import {WebServerTarget}

@Suite("{Feature} Request Tests")
struct {Feature}RequestTests {
    // MARK: - Success Cases

    @Test func {feature}Request_success() async throws {
        try await withTestApp { app in
            let request = {Feature}Request(query: .init(id: validId))

            try await app.testing().test(request, locale: en) { response in
                #expect(response.status == .ok)
                #expect(response.body != nil)
            }
        }
    }

    // MARK: - Error Cases

    @Test func {feature}Request_notFound() async throws {
        try await withTestApp { app in
            let request = {Feature}Request(query: .init(id: invalidId))

            try await app.testing().test(request, locale: en) { response in
                #expect(response.status == .notFound)
            }
        }
    }

    // MARK: - Test Helpers

    private let validId = ModelIdType()
    private let invalidId = ModelIdType()
    private let en = Locale(identifier: "en")
}

// MARK: - Test Application Setup

private func withTestApp(_ test: (Application) async throws -> Void) async throws {
    try await withApp { app in
        // Configure localization if needed
        try app.initYamlLocalization(
            bundle: Bundle.module,
            resourceDirectoryName: "{ResourceDir}"
        )

        // Register controller
        try app.routes.register(collection: {Feature}Controller())

        try await test(app)
    }
}
```

---

## Template 2: ViewModelRequest Test Suite with Localization

For testing ViewModelRequest types with multi-locale verification.

**Location:** `Tests/{Target}Tests/Requests/{Feature}ViewModelRequestTests.swift`

```swift
// {Feature}ViewModelRequestTests.swift

import FOSFoundation
@testable import FOSMVVM
@testable import FOSMVVMVapor
import FOSTesting
import FOSTestingVapor
import Foundation
import Testing
import Vapor
import VaporTesting
@testable import {ViewModelsTarget}
@testable import {WebServerTarget}

@Suite("{Feature} ViewModel Request Tests")
struct {Feature}ViewModelRequestTests {
    // MARK: - Multi-Locale Tests

    @Test func viewModelRequest_englishLocale() async throws {
        try await withTestApp { app in
            let request = {Feature}ViewModelRequest()

            try await app.testing().test(request, locale: en) { response in
                #expect(response.status == .ok)
                let vm = try #require(response.body)
                #expect(try vm.pageTitle.localizedString == "Expected English Title")
            }
        }
    }

    @Test func viewModelRequest_spanishLocale() async throws {
        try await withTestApp { app in
            let request = {Feature}ViewModelRequest()

            try await app.testing().test(request, locale: es) { response in
                #expect(response.status == .ok)
                let vm = try #require(response.body)
                #expect(try vm.pageTitle.localizedString == "Título Esperado en Español")
            }
        }
    }

    @Test func viewModelRequest_allLocales() async throws {
        try await withTestApp { app in
            let request = {Feature}ViewModelRequest()

            for locale in [en, es] {
                try await app.testing().test(request, locale: locale) { response in
                    #expect(response.status == .ok)
                    let vm = try #require(response.body)
                    // Verify non-empty localized content
                    #expect(try !vm.pageTitle.localizedString.isEmpty)
                }
            }
        }
    }

    // MARK: - Test Helpers

    private let en = Locale(identifier: "en")
    private let es = Locale(identifier: "es")
}

private func withTestApp(_ test: (Application) async throws -> Void) async throws {
    try await withApp { app in
        try app.initYamlLocalization(
            bundle: Bundle.module,
            resourceDirectoryName: "{ResourceDir}"
        )
        try app.routes.register(collection: {Feature}ViewModelController())
        try await test(app)
    }
}
```

---

## Template 3: CreateRequest Test Suite

For testing CreateRequest types with validation.

**Location:** `Tests/{Target}Tests/Requests/Create{Feature}RequestTests.swift`

```swift
// Create{Feature}RequestTests.swift

import FOSFoundation
@testable import FOSMVVM
@testable import FOSMVVMVapor
import FOSTesting
import FOSTestingVapor
import Foundation
import Testing
import Vapor
import VaporTesting
@testable import {ViewModelsTarget}
@testable import {WebServerTarget}

@Suite("Create {Feature} Request Tests")
struct Create{Feature}RequestTests {
    // MARK: - Success Cases

    @Test func createRequest_validInput() async throws {
        try await withTestApp { app in
            let request = Create{Feature}Request(requestBody: .init(
                name: "Valid Name",
                content: "Valid content"
            ))

            try await app.testing().test(request, locale: en) { response in
                #expect(response.status == .ok)
                let body = try #require(response.body)
                #expect(body.id != nil)
            }
        }
    }

    // MARK: - Validation Error Cases

    @Test func createRequest_emptyName() async throws {
        try await withTestApp { app in
            let request = Create{Feature}Request(requestBody: .init(
                name: "",  // Invalid: empty
                content: "Valid content"
            ))

            try await app.testing().test(request, locale: en) { response in
                #expect(response.status == .badRequest)
                #expect(response.error != nil)
            }
        }
    }

    @Test func createRequest_contentTooLong() async throws {
        try await withTestApp { app in
            let request = Create{Feature}Request(requestBody: .init(
                name: "Valid Name",
                content: String(repeating: "x", count: 10001)  // Exceeds max
            ))

            try await app.testing().test(request, locale: en) { response in
                #expect(response.status == .badRequest)
            }
        }
    }

    // MARK: - Test Helpers

    private let en = Locale(identifier: "en")
}

private func withTestApp(_ test: (Application) async throws -> Void) async throws {
    try await withApp { app in
        try app.routes.register(collection: Create{Feature}Controller())
        try await test(app)
    }
}
```

---

## Template 4: UpdateRequest Test Suite

For testing UpdateRequest types with entity modification.

**Location:** `Tests/{Target}Tests/Requests/Update{Feature}RequestTests.swift`

```swift
// Update{Feature}RequestTests.swift

import FOSFoundation
@testable import FOSMVVM
@testable import FOSMVVMVapor
import FOSTesting
import FOSTestingVapor
import Foundation
import Testing
import Vapor
import VaporTesting
@testable import {ViewModelsTarget}
@testable import {WebServerTarget}

@Suite("Update {Feature} Request Tests")
struct Update{Feature}RequestTests {
    // MARK: - Success Cases

    @Test func updateRequest_success() async throws {
        try await withTestApp { app in
            // Create entity first
            let createRequest = Create{Feature}Request(requestBody: .init(
                name: "Original Name"
            ))
            var createdId: ModelIdType?
            try await app.testing().test(createRequest, locale: en) { response in
                createdId = response.body?.id
            }

            // Update the entity
            let updateRequest = Update{Feature}Request(requestBody: .init(
                {feature}Id: try #require(createdId),
                name: "Updated Name"
            ))

            try await app.testing().test(updateRequest, locale: en) { response in
                #expect(response.status == .ok)
                #expect(response.body?.viewModel.name == "Updated Name")
            }
        }
    }

    // MARK: - Error Cases

    @Test func updateRequest_notFound() async throws {
        try await withTestApp { app in
            let request = Update{Feature}Request(requestBody: .init(
                {feature}Id: ModelIdType(),  // Non-existent ID
                name: "Updated Name"
            ))

            try await app.testing().test(request, locale: en) { response in
                #expect(response.status == .notFound)
            }
        }
    }

    @Test func updateRequest_invalidInput() async throws {
        try await withTestApp { app in
            let request = Update{Feature}Request(requestBody: .init(
                {feature}Id: existingId,
                name: ""  // Invalid: empty
            ))

            try await app.testing().test(request, locale: en) { response in
                #expect(response.status == .badRequest)
            }
        }
    }

    // MARK: - Test Helpers

    private let existingId = ModelIdType()
    private let en = Locale(identifier: "en")
}

private func withTestApp(_ test: (Application) async throws -> Void) async throws {
    try await withApp { app in
        try app.routes.register(collection: Create{Feature}Controller())
        try app.routes.register(collection: Update{Feature}Controller())
        try await test(app)
    }
}
```

---

## Template 5: DeleteRequest Test Suite

For testing DeleteRequest types with entity removal.

**Location:** `Tests/{Target}Tests/Requests/Delete{Feature}RequestTests.swift`

```swift
// Delete{Feature}RequestTests.swift

import FOSFoundation
@testable import FOSMVVM
@testable import FOSMVVMVapor
import FOSTesting
import FOSTestingVapor
import Foundation
import Testing
import Vapor
import VaporTesting
@testable import {ViewModelsTarget}
@testable import {WebServerTarget}

@Suite("Delete {Feature} Request Tests")
struct Delete{Feature}RequestTests {
    // MARK: - Success Cases

    @Test func deleteRequest_success() async throws {
        try await withTestApp { app in
            // Create entity first
            let createRequest = Create{Feature}Request(requestBody: .init(
                name: "To Be Deleted"
            ))
            var createdId: ModelIdType?
            try await app.testing().test(createRequest, locale: en) { response in
                createdId = response.body?.id
            }

            // Delete the entity
            let deleteRequest = Delete{Feature}Request(requestBody: .init(
                {feature}Id: try #require(createdId)
            ))

            try await app.testing().test(deleteRequest, locale: en) { response in
                #expect(response.status == .ok)
            }

            // Verify deletion - should return not found
            let showRequest = Show{Feature}Request(query: .init(
                {feature}Id: try #require(createdId)
            ))
            try await app.testing().test(showRequest, locale: en) { response in
                #expect(response.status == .notFound)
            }
        }
    }

    // MARK: - Error Cases

    @Test func deleteRequest_notFound() async throws {
        try await withTestApp { app in
            let request = Delete{Feature}Request(requestBody: .init(
                {feature}Id: ModelIdType()  // Non-existent ID
            ))

            try await app.testing().test(request, locale: en) { response in
                #expect(response.status == .notFound)
            }
        }
    }

    // MARK: - Test Helpers

    private let en = Locale(identifier: "en")
}

private func withTestApp(_ test: (Application) async throws -> Void) async throws {
    try await withApp { app in
        try app.routes.register(collection: Create{Feature}Controller())
        try app.routes.register(collection: Show{Feature}Controller())
        try app.routes.register(collection: Delete{Feature}Controller())
        try await test(app)
    }
}
```

---

## Template 6: ShowRequest with Query Parameters

For testing ShowRequest types with complex query parameters.

**Location:** `Tests/{Target}Tests/Requests/Show{Feature}RequestTests.swift`

```swift
// Show{Feature}RequestTests.swift

import FOSFoundation
@testable import FOSMVVM
@testable import FOSMVVMVapor
import FOSTesting
import FOSTestingVapor
import Foundation
import Testing
import Vapor
import VaporTesting
@testable import {ViewModelsTarget}
@testable import {WebServerTarget}

@Suite("Show {Feature} Request Tests")
struct Show{Feature}RequestTests {
    // MARK: - Basic Query Tests

    @Test func showRequest_byId() async throws {
        try await withTestApp { app in
            let request = Show{Feature}Request(query: .init(
                {feature}Id: existingId
            ))

            try await app.testing().test(request, locale: en) { response in
                #expect(response.status == .ok)
                #expect(response.body?.viewModel.id == existingId)
            }
        }
    }

    // MARK: - Query Parameter Variations

    @Test func showRequest_withIncludeDetails() async throws {
        try await withTestApp { app in
            let request = Show{Feature}Request(query: .init(
                {feature}Id: existingId,
                includeDetails: true
            ))

            try await app.testing().test(request, locale: en) { response in
                #expect(response.status == .ok)
                #expect(response.body?.viewModel.details != nil)
            }
        }
    }

    @Test func showRequest_withoutIncludeDetails() async throws {
        try await withTestApp { app in
            let request = Show{Feature}Request(query: .init(
                {feature}Id: existingId,
                includeDetails: false
            ))

            try await app.testing().test(request, locale: en) { response in
                #expect(response.status == .ok)
                #expect(response.body?.viewModel.details == nil)
            }
        }
    }

    // MARK: - Error Cases

    @Test func showRequest_notFound() async throws {
        try await withTestApp { app in
            let request = Show{Feature}Request(query: .init(
                {feature}Id: ModelIdType()  // Non-existent
            ))

            try await app.testing().test(request, locale: en) { response in
                #expect(response.status == .notFound)
            }
        }
    }

    // MARK: - Test Helpers

    private let existingId = ModelIdType()
    private let en = Locale(identifier: "en")
}

private func withTestApp(_ test: (Application) async throws -> Void) async throws {
    try await withApp { app in
        try app.routes.register(collection: Show{Feature}Controller())
        try await test(app)
    }
}
```

---

## Template 7: Comprehensive CRUD Test Suite

For testing all CRUD operations for a feature in one suite.

**Location:** `Tests/{Target}Tests/Requests/{Feature}CRUDTests.swift`

```swift
// {Feature}CRUDTests.swift

import FOSFoundation
@testable import FOSMVVM
@testable import FOSMVVMVapor
import FOSTesting
import FOSTestingVapor
import Foundation
import Testing
import Vapor
import VaporTesting
@testable import {ViewModelsTarget}
@testable import {WebServerTarget}

@Suite("{Feature} CRUD Tests")
struct {Feature}CRUDTests {
    // MARK: - Create

    @Test func create_{feature}() async throws {
        try await withTestApp { app in
            let request = Create{Feature}Request(requestBody: .init(
                name: "New {Feature}"
            ))

            try await app.testing().test(request, locale: en) { response in
                #expect(response.status == .ok)
                #expect(response.body?.id != nil)
            }
        }
    }

    // MARK: - Read

    @Test func show_{feature}() async throws {
        try await withTestApp { app in
            // Create first
            let id = try await create{Feature}(app: app)

            // Then read
            let request = Show{Feature}Request(query: .init({feature}Id: id))

            try await app.testing().test(request, locale: en) { response in
                #expect(response.status == .ok)
                #expect(response.body?.viewModel.id == id)
            }
        }
    }

    // MARK: - Update

    @Test func update_{feature}() async throws {
        try await withTestApp { app in
            let id = try await create{Feature}(app: app)

            let request = Update{Feature}Request(requestBody: .init(
                {feature}Id: id,
                name: "Updated Name"
            ))

            try await app.testing().test(request, locale: en) { response in
                #expect(response.status == .ok)
                #expect(response.body?.viewModel.name == "Updated Name")
            }
        }
    }

    // MARK: - Delete

    @Test func delete_{feature}() async throws {
        try await withTestApp { app in
            let id = try await create{Feature}(app: app)

            let request = Delete{Feature}Request(requestBody: .init({feature}Id: id))

            try await app.testing().test(request, locale: en) { response in
                #expect(response.status == .ok)
            }

            // Verify deleted
            let showRequest = Show{Feature}Request(query: .init({feature}Id: id))
            try await app.testing().test(showRequest, locale: en) { response in
                #expect(response.status == .notFound)
            }
        }
    }

    // MARK: - Helper Methods

    private func create{Feature}(app: Application) async throws -> ModelIdType {
        let request = Create{Feature}Request(requestBody: .init(name: "Test"))
        var createdId: ModelIdType?

        try await app.testing().test(request, locale: en) { response in
            createdId = response.body?.id
        }

        return try #require(createdId)
    }

    private let en = Locale(identifier: "en")
}

private func withTestApp(_ test: (Application) async throws -> Void) async throws {
    try await withApp { app in
        try app.routes.register(collection: {Feature}CRUDController())
        try await test(app)
    }
}
```

---

# Checklists

## New ServerRequest Test Checklist

- [ ] Test file created in `Tests/{Target}Tests/Requests/`
- [ ] Imports include `FOSTestingVapor` and `VaporTesting`
- [ ] Uses `app.testing().test(request, locale:)` for ALL testing
- [ ] Success case tested
- [ ] Not found / error case tested
- [ ] Validation errors tested (for Create/Update)
- [ ] Multi-locale tested (if ResponseBody has localized fields)
- [ ] Test app setup includes route registration
- [ ] Tests pass: `swift test --filter {TestSuiteName}`

## Localized Response Test Checklist

- [ ] YAML localization loaded in test app
- [ ] Each locale tested explicitly
- [ ] Localized string values verified
- [ ] Empty string checks for required fields

## CRUD Test Checklist

- [ ] Create: Valid input returns ID
- [ ] Create: Invalid input returns error
- [ ] Read: Existing entity returns data
- [ ] Read: Non-existent returns not found
- [ ] Update: Valid update applies changes
- [ ] Update: Invalid input returns error
- [ ] Update: Non-existent returns not found
- [ ] Delete: Removes entity
- [ ] Delete: Non-existent returns not found
- [ ] Delete: Verify entity no longer accessible

---

## Quick Reference

**Minimal test:**
```swift
@Test func myRequest() async throws {
    try await withTestApp { app in
        let request = MyRequest(query: .init(id: validId))
        try await app.testing().test(request, locale: en) { response in
            #expect(response.status == .ok)
        }
    }
}
```

**With body verification:**
```swift
@Test func myRequest_withBody() async throws {
    try await withTestApp { app in
        let request = MyRequest(query: .init(id: validId))
        try await app.testing().test(request, locale: en) { response in
            #expect(response.status == .ok)
            let body = try #require(response.body)
            #expect(body.viewModel.name == "Expected")
        }
    }
}
```

**Multi-locale:**
```swift
@Test func myRequest_allLocales() async throws {
    try await withTestApp { app in
        let request = MyRequest()
        for locale in [en, es] {
            try await app.testing().test(request, locale: locale) { response in
                #expect(response.status == .ok)
            }
        }
    }
}
```

**Error verification:**
```swift
@Test func myRequest_error() async throws {
    try await withTestApp { app in
        let request = MyRequest(query: .init(id: invalidId))
        try await app.testing().test(request, locale: en) { response in
            #expect(response.status == .notFound)
            #expect(response.error != nil)
        }
    }
}
```
