# FOSMVVM Fluent DataModel Generator - Reference Templates

This document contains the complete file templates for generating Fluent DataModels.
Replace `{Model}` with the actual model name (e.g., `User`, `Idea`).

> **Fields Layer:** For form-backed models, first run [fosmvvm-fields-generator](../fosmvvm-fields-generator/SKILL.md) to generate the Fields protocol, Messages struct, and YAML localization.

---

## File 1: {Model}.swift (Fluent Model)

**Location:** `Sources/{WebServerTarget}/DataModels/{Model}.swift`

```swift
import FluentKit
import FOSFoundation
import FOSMVVM
import FOSMVVMVapor
import Foundation
import {ViewModelsTarget}

final class {Model}: DataModel, {Model}Fields, Hashable, @unchecked Sendable {
    static let schema = "{models}"  // snake_case plural

    // MARK: Public Properties

    @ID(key: .id) var id: ModelIdType?

    // MARK: {Model}Fields Protocol

    // Add fields matching the protocol:
    // @Field(key: "field_name") var fieldName: FieldType

    let {model}ValidationMessages: {Model}FieldsMessages

    // MARK: Timestamps

    @Timestamp(key: "created_at", on: .create) var createdAt: Date?
    @Timestamp(key: "updated_at", on: .update) var updatedAt: Date?

    init() {
        self.{model}ValidationMessages = .init()
    }

    init(id: ModelIdType? = nil, /* add field parameters */) {
        self.{model}ValidationMessages = .init()
        self.id = id
        // Assign fields
    }
}
```

---

## File 2: {Model}+Schema.swift

**Location:** `Sources/{WebServerTarget}/Migrations/{Model}+Schema.swift`

```swift
import Fluent

extension {Model} {
    struct Initial: AsyncMigration {
        let name = "\({Model}.schema)-initial"

        func prepare(on database: any Database) async throws {
            try await database.schema({Model}.schema)

                // MARK: Properties

                .id()
                // Add fields:
                // .field("field_name", .string, .required)
                // .field("optional_field", .string)
                // .field("foreign_key", .uuid, .references("other_table", "id"))

                // MARK: Timestamps

                .field("created_at", .datetime)
                .field("updated_at", .datetime)

                // MARK: Constraints

                // Add constraints:
                // .unique(on: "field_name")

                .create()
        }

        func revert(on database: any Database) async throws {
            try await database.schema({Model}.schema).delete()
        }
    }
}
```

---

## File 3: {Model}+Seed.swift

**Location:** `Sources/{WebServerTarget}/Migrations/{Model}+Seed.swift`

```swift
import Fluent
import Vapor

extension {Model} {
    struct Seed: AsyncMigration {
        let name = "\({Model}.schema)-seed"

        func prepare(on database: any Database) async throws {
            guard try await {Model}.query(on: database).count() == 0 else { return }

            let items: [{Model}]
            switch Vapor.Environment.deployment {
            case .debug:
                items = try {Model}.defaultDebugItems
            case .test:
                items = try {Model}.defaultTestItems
            default:
                fatalError("Unknown Deployment: \(Vapor.Environment.deployment)")
            }

            for item in items {
                try await item.save(on: database)
            }
        }

        func revert(on database: any Database) async throws {}
    }
}

private extension {Model} {
    static var defaultDebugItems: [{Model}] {
        get throws { [
            // Add debug seed data:
            // .init(fieldName: "value")
        ] }
    }

    static var defaultTestItems: [{Model}] {
        get throws { [
            // Add test seed data:
            // .init(fieldName: "test_value")
        ] }
    }
}
```

---

## File 4: {Model}FieldsTests.swift

**Location:** `Tests/{ViewModelsTarget}Tests/FieldModels/{Model}FieldsTests.swift`

```swift
import FOSFoundation
import FOSMVVM
import FOSTesting
import Foundation
import Testing
import {ViewModelsTarget}

@Suite("{Model} Fields")
struct {Model}FieldsTests: LocalizableTestCase {
    @Test func {model}FormFields() throws {
        // Test all form fields:
        // try expectFullFormFieldTests({Model}.fieldNameField)
    }

    // Add validation tests with arguments:
    // @Test(arguments: [
    //     Test{Model}(fieldName: ""),
    //     Test{Model}(fieldName: String.random(length: {Model}.fieldNameRange.lowerBound - 1)),
    //     Test{Model}(fieldName: String.random(length: {Model}.fieldNameRange.upperBound + 1))
    // ]) fileprivate func `{Model} FieldName Validation`(
    //     item: Test{Model}
    // ) throws {
    //     for locale in locales {
    //         var item = item
    //         try item.localizeMessages(encoder: encoder(locale: locale))
    //
    //         let validations = Validations()
    //         let status = try #require(item.validate(validations: validations))
    //         #expect(status.hasError)
    //         let messages = validations.validations
    //             .compactMap { $0.messages(for: {Model}.fieldNameField.fieldId) }
    //             .flatMap(\.self)
    //         #expect(messages.count == 1)
    //         guard let message = messages.first else { return }
    //
    //         #expect(message.message != .empty, "\(locale)")
    //     }
    // }

    let locStore: LocalizationStore

    init() async throws {
        self.locStore = try Self.loadLocalizationStore(
            bundle: Bundle.module,
            resourceDirectoryName: ""
        )
    }
}

private struct Test{Model}: {Model}Fields {
    var id: ModelIdType?
    // Add fields matching protocol

    private(set) var {model}ValidationMessages: {Model}FieldsMessages

    mutating func localizeMessages(encoder: JSONEncoder) throws {
        {model}ValidationMessages = try {Model}FieldsMessages().toJSON(encoder: encoder).fromJSON()
    }

    init(
        id: ModelIdType? = .init()
        // Add default parameters for all fields
    ) {
        self.id = id
        // Assign fields
        self.{model}ValidationMessages = .init()
    }
}
```

---

## File 5: Update database.swift

**Location:** `Sources/{WebServerTarget}/database.swift`

Add to the existing file:

```swift
// Under MARK: Migrations
app.migrations.add({Model}.Initial())

// Under MARK: Seed (inside the if !app.environment.isRelease block)
app.migrations.add({Model}.Seed(), to: dbId)
```

---

## Relationship Patterns

### Pattern 0: Many-to-Many (Junction Tables)

Use junction tables, NEVER UUID arrays.

**Anti-pattern (don't do this):**
```swift
// BAD - loses referential integrity, bypasses type safety
@Field(key: "source_nodes") var sourceNodes: [ModelIdType]
```

**Correct pattern:**

1. Create junction table (DataModel-only, no Fields needed):
```swift
import FluentKit
import Foundation

final class {Parent}{Relationship}: Model, @unchecked Sendable {
    static let schema = "{parent}_{relationships}"  // snake_case plural

    @ID(key: .id) var id: UUID?
    @Parent(key: "{parent}_id") var {parent}: {Parent}
    @Parent(key: "{related}_id") var {related}: {Related}
    @Timestamp(key: "created_at", on: .create) var createdAt: Date?

    init() {}

    init({parent}ID: {Parent}.IDValue, {related}ID: {Related}.IDValue) {
        self.${parent}.id = {parent}ID
        self.${related}.id = {related}ID
    }
}
```

2. Wire `@Siblings` in parent model:
```swift
final class {Parent}: DataModel, {Parent}Fields, ... {
    @Siblings(through: {Parent}{Relationship}.self,
              from: \.${parent},
              to: \.${related}) var {relationships}: [{Related}]
}
```

3. Create migration for junction table:
```swift
extension {Parent}{Relationship} {
    struct Initial: AsyncMigration {
        let name = "\({Parent}{Relationship}.schema)-initial"

        func prepare(on database: any Database) async throws {
            try await database.schema({Parent}{Relationship}.schema)
                .id()
                .field("{parent}_id", .uuid, .required,
                       .references({Parent}.schema, "id", onDelete: .cascade))
                .field("{related}_id", .uuid, .required,
                       .references({Related}.schema, "id", onDelete: .cascade))
                .field("created_at", .datetime)
                .unique(on: "{parent}_id", "{related}_id")
                .create()
        }

        func revert(on database: any Database) async throws {
            try await database.schema({Parent}{Relationship}.schema).delete()
        }
    }
}
```

**Naming convention:**
- Junction table: `{Parent}{Relationship}` (e.g., `DocumentOriginatingConversation`)
- Relationship property: descriptive verb (e.g., `originatingConversations`)
- Avoid generic names like `sourceNodes` - be specific about the relationship meaning

### Pattern 1: Associated Type (Preferred for Required Relationships)

**PRINCIPLE: Existential types (`any Protocol`) are a code smell.** Use associated types for required relationships.

**In the protocol** (`{Model}Fields.swift`):
```swift
public protocol {Model}Fields: ValidatableModel, Codable, Sendable {
    associatedtype {Related}: {Related}Fields

    var id: ModelIdType? { get set }
    var {related}: {Related} { get set }  // Associated type, not existential
}
```

**In the Fluent model** (`{Model}.swift`):
```swift
final class {Model}: DataModel, {Model}Fields, Hashable, @unchecked Sendable {
    static let schema = "{models}"

    @ID(key: .id) var id: ModelIdType?
    @Parent(key: "{related}_id") var {related}: {Related}  // Directly satisfies protocol!

    // CRITICAL: Initialize validationMessages FIRST
    init(id: ModelIdType? = nil, {related}ID: {Related}.IDValue) {
        self.{model}ValidationMessages = .init()  // FIRST!
        self.id = id
        self.${related}.id = {related}ID
    }
}
```

**In the schema** (`{Model}+Schema.swift`):
```swift
.field("{related}_id", .uuid, .required, .references({Related}.schema, "id", onDelete: .cascade))
```

**In tests** (`{Model}FieldsTests.swift`):
```swift
private struct Test{Model}: {Model}Fields {
    typealias {Related} = Test{Related}  // Satisfy the associated type

    var id: ModelIdType?
    var {related}: Test{Related}  // Concrete type
}

private struct Test{Related}: {Related}Fields {
    var id: ModelIdType? = .init()
    // ... all required fields with defaults
}
```

### Pattern 2: Plain ID (For Optional FKs or External References)

Use when the relationship is optional or references an external system:

**In the protocol:**
```swift
var {related}Id: ModelIdType { get set }           // Required FK as ID
var externalSystemId: ModelIdType? { get set }     // Optional/external FK
```

**In the Fluent model:**
```swift
@Parent(key: "{related}_id") var {related}: {Related}

// Computed property to satisfy protocol
var {related}Id: ModelIdType {
    get { ${related}.id }
    set { ${related}.id = newValue }
}

// Optional external reference - plain field, not @Parent
@OptionalField(key: "external_system_id") var externalSystemId: ModelIdType?
```

---

## Raw SQL in Migrations (PostgreSQL Features)

For PostgreSQL-specific features not supported by Fluent's schema builder:

```swift
// {Model}+Schema.swift

import Fluent
import SQLKit  // Required for raw SQL

extension {Model} {
    struct Initial: AsyncMigration {
        let name = "\({Model}.schema)-initial"

        func prepare(on database: any Database) async throws {
            // Standard Fluent schema builder
            try await database.schema({Model}.schema)
                .id()
                .field("content", .string, .required)
                .field("created_at", .datetime)
                .field("updated_at", .datetime)
                .create()

            // PostgreSQL-specific features via raw SQL
            guard let sql = database as? any SQLDatabase else { return }

            let schema = {Model}.schema

            // Full-text search with tsvector (GENERATED column)
            try await sql.raw(SQLQueryString("""
                ALTER TABLE \(unsafeRaw: schema) ADD COLUMN search_vector tsvector
                GENERATED ALWAYS AS (to_tsvector('english', content)) STORED
                """)).run()

            // GIN index for full-text search
            try await sql.raw(SQLQueryString("""
                CREATE INDEX \(unsafeRaw: schema)_search_idx
                ON \(unsafeRaw: schema) USING GIN (search_vector)
                """)).run()

            // LTREE column for hierarchical data
            // try await sql.raw(SQLQueryString("""
            //     ALTER TABLE \(unsafeRaw: schema) ADD COLUMN path ltree
            //     """)).run()
        }

        func revert(on database: any Database) async throws {
            try await database.schema({Model}.schema).delete()
        }
    }
}
```

**Key points:**
- Import `SQLKit` (not just `Fluent`)
- Cast database: `database as? any SQLDatabase`
- Use `SQLQueryString` with `\(unsafeRaw:)` for table/column names
- These columns exist only in the database - not in the protocol or Fluent model
- The Fluent model can still query/filter on them using raw queries
