# FOSMVVM ServerRequest Generator - Reference Templates

Complete file templates for generating ServerRequest flows.

> **Architecture context:** See [FOSMVVMArchitecture.md](../../docs/FOSMVVMArchitecture.md) - especially "Core Principle: ServerRequest Is THE Way"

---

## REMEMBER: MVVMEnvironment + processRequest()

Before using these templates, remember:

```swift
// ✅ Import your shared module (contains ServerRequests AND SystemVersion)
import ViewModels  // ← See "The Shared Module Pattern" in FOSMVVMArchitecture.md

// ✅ Configure MVVMEnvironment ONCE at app/tool startup
let mvvmEnv = await MVVMEnvironment(
    currentVersion: .currentApplicationVersion,  // From shared module's SystemVersion extension
    appBundle: Bundle.module,
    deploymentURLs: [.debug: URL(string: "http://localhost:8080")!]
)
// Version headers (X-FOS-Version) are AUTOMATIC via SystemVersion.current

// ✅ Client invocation - ALWAYS use mvvmEnv
let request = {Action}Request(requestBody: .init(...))
try await request.processRequest(mvvmEnv: mvvmEnv)
let result = request.responseBody

// ❌ NEVER do this - violates DRY
try await request.processRequest(baseURL: someURL, headers: someHeaders)

// ❌ NEVER do this - hand-written HTTP
let url = URL(string: "http://server/api/something")!
```

The templates below define the **types**. The URL path is derived from the type name automatically. Configuration lives in MVVMEnvironment.

---

## Placeholders

| Placeholder | Replace With | Example |
|-------------|--------------|---------|
| `{Action}` | Operation name (PascalCase) | `MoveIdea`, `CreateUser`, `DeleteDocument` |
| `{action}` | Same, camelCase | `moveIdea`, `createUser` |
| `{Entity}` | Entity being operated on | `Idea`, `User`, `Document` |
| `{entity}` | Same, camelCase | `idea`, `user`, `document` |
| `{ViewModelsTarget}` | Shared ViewModels SPM target | `ViewModels` |
| `{WebServerTarget}` | Server-side target | `WebServer`, `AppServer` |
| `{Protocol}` | Request protocol | `UpdateRequest`, `CreateRequest` |

---

## Template 1: ServerRequest Type

**Location:** `Sources/{ViewModelsTarget}/Requests/{Action}Request.swift`

```swift
import FOSFoundation
import FOSMVVM
import Foundation

public final class {Action}Request: {Protocol}, @unchecked Sendable {
    public typealias Query = EmptyQuery
    public typealias Fragment = EmptyFragment
    public typealias ResponseError = EmptyError

    public let requestBody: RequestBody?
    public var responseBody: ResponseBody?

    // What the client sends
    public struct RequestBody: ServerRequestBody, ValidatableModel {
        public let {entity}Id: ModelIdType
        // Add other fields as needed

        public init({entity}Id: ModelIdType) {
            self.{entity}Id = {entity}Id
        }

        public func validate(
            fields: [any FOSMVVM.FormFieldBase]?,
            validations: FOSMVVM.Validations
        ) -> FOSMVVM.ValidationResult.Status? {
            nil  // Add validation if needed
        }
    }

    // What the server returns
    public struct ResponseBody: {Protocol}ResponseBody {
        public let viewModel: {Entity}ViewModel  // Or appropriate ViewModel

        public init(viewModel: {Entity}ViewModel) {
            self.viewModel = viewModel
        }
    }

    public init(
        query: Query? = nil,
        fragment: Fragment? = nil,
        requestBody: RequestBody? = nil,
        responseBody: ResponseBody? = nil
    ) {
        self.requestBody = requestBody
        self.responseBody = responseBody
    }
}

// MARK: - Stubbable

public extension {Action}Request {
    static func stub() -> Self {
        .stub(requestBody: .stub())
    }

    static func stub(
        requestBody: RequestBody? = .stub(),
        responseBody: ResponseBody? = nil
    ) -> Self {
        .init(requestBody: requestBody, responseBody: responseBody)
    }
}

extension {Action}Request.RequestBody: Stubbable {
    public static func stub() -> Self {
        .init({entity}Id: .init())
    }
}

extension {Action}Request.ResponseBody: Stubbable {
    public static func stub() -> Self {
        .init(viewModel: .stub())
    }
}
```

---

## Template 2: Controller (Server-Side Handler)

**Location:** `Sources/{WebServerTarget}/Controllers/{Action}Controller.swift`

```swift
import Fluent
import FOSMVVM
import FOSMVVMVapor
import Vapor
import {ViewModelsTarget}

final class {Action}Controller: ServerRequestController {
    typealias TRequest = {Action}Request

    let actions: [ServerRequestAction: ActionProcessor] = [
        .{action}: {Action}Request.perform{Action}
    ]
}

private extension {Action}Request {
    static func perform{Action}(
        _ request: Vapor.Request,
        _ serverRequest: {Action}Request,
        _ requestBody: RequestBody
    ) async throws -> ResponseBody {
        let db = request.db

        // 1. Fetch entity (with relationships if needed)
        guard let {entity} = try await {Entity}.query(on: db)
            .filter(\.$id == requestBody.{entity}Id)
            .with(\.$createdBy)  // Add relationships as needed
            .first()
        else {
            throw Abort(.notFound, reason: "{Entity} not found: \(requestBody.{entity}Id)")
        }

        // 2. Perform the operation
        // {entity}.someField = requestBody.newValue
        // try await {entity}.save(on: db)

        // 3. Build and return ViewModel
        let viewModel = {Entity}ViewModel(
            id: try {entity}.requireID()
            // ... map fields
        )

        return .init(viewModel: viewModel)
    }
}
```

---

## Template 3: Controller Registration

**Location:** `Sources/{WebServerTarget}/routes.swift`

```swift
// Add to existing routes.swift
try versionedGroup.register(collection: {Action}Controller())
```

---

## Template 4: Client Invocation

### All Swift Clients (iOS, macOS, CLI, background jobs, etc.)

```swift
// MVVMEnvironment configured ONCE at app/tool startup (see "REMEMBER" section above)

// Make requests using mvvmEnv
let request = {Action}Request(requestBody: .init(
    {entity}Id: entityId
    // ... other fields
))

do {
    try await request.processRequest(mvvmEnv: mvvmEnv)
    let viewModel = request.responseBody?.viewModel
    // Use viewModel...
} catch {
    // Handle error
}
```

### WebApp Bridge (for browser clients)

**WebApp Route:** `Sources/{WebAppTarget}/routes.swift`

```swift
app.post("{action-kebab-case}") { req async throws -> Response in
    // 1. Decode what JS sent
    let body = try req.content.decode({Action}Request.RequestBody.self)

    // 2. Call server via ServerRequest (NOT hardcoded URL!)
    // mvvmEnv is configured at WebApp startup
    let serverRequest = {Action}Request(requestBody: body)
    try await serverRequest.processRequest(mvvmEnv: req.application.mvvmEnv)

    guard let response = serverRequest.responseBody else {
        throw Abort(.internalServerError, reason: "No response from server")
    }

    // 3. Return response (HTML fragment or JSON)
    return try await req.view.render(
        "{Feature}/{Entity}View",
        ["viewModel": response.viewModel]
    )
}
```

**JavaScript Handler:**

```javascript
async function handle{Action}(data) {
    // CRITICAL: Capture DOM references BEFORE any await
    const element = data.element;
    const entityId = element.dataset.entityId;

    const request = {
        {entity}Id: entityId
        // ... other fields from data attributes
    };

    try {
        // POST to WebApp (NOT WebServer!)
        const response = await fetch('/{action-kebab-case}', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(request)
        });

        if (!response.ok) {
            throw new Error(await response.text() || 'Operation failed');
        }

        // Handle response (HTML or JSON depending on your pattern)
        const html = await response.text();
        // Swap into DOM...

    } catch (error) {
        console.error('Error:', error);
        // Handle error...
    }
}
```

---

## Protocol-Specific Templates

### ShowRequest (Read)

```swift
public final class Get{Entity}Request: ShowRequest, @unchecked Sendable {
    public typealias Fragment = EmptyFragment
    public typealias RequestBody = EmptyBody  // No body for GET

    public let query: Query?
    public var responseBody: ResponseBody?

    public struct Query: ServerRequestQuery {
        public let {entity}Id: ModelIdType
    }

    public struct ResponseBody: ServerRequestBody {
        public let viewModel: {Entity}ViewModel
    }
    // ...
}
```

### CreateRequest (Create)

```swift
public final class Create{Entity}Request: CreateRequest, @unchecked Sendable {
    // RequestBody: ValidatableModel required
    public struct RequestBody: ServerRequestBody, ValidatableModel {
        public let content: String
        // ... fields for new entity
    }

    public struct ResponseBody: CreateResponseBody {
        public let id: ModelIdType  // Or full ViewModel
    }
    // ...
}
```

### UpdateRequest (Update)

```swift
public final class Update{Entity}Request: UpdateRequest, @unchecked Sendable {
    public struct RequestBody: ServerRequestBody, ValidatableModel {
        public let {entity}Id: ModelIdType
        public let newValue: SomeType
    }

    public struct ResponseBody: UpdateResponseBody {
        public let viewModel: {Entity}ViewModel
    }
    // ...
}
```

### DeleteRequest (Soft Delete)

```swift
public final class Delete{Entity}Request: DeleteRequest, @unchecked Sendable {
    public struct RequestBody: ServerRequestBody {
        public let {entity}Id: ModelIdType
    }

    public typealias ResponseBody = EmptyBody  // Often no response needed
    // ...
}
```

### Large Upload RequestBody

For file uploads or large payloads, specify `maxBodySize` to override the server's default limit:

```swift
public final class Upload{Entity}Request: CreateRequest, @unchecked Sendable {
    // ...

    public struct RequestBody: ServerRequestBody, ValidatableModel {
        // Override default body size limit (e.g., 50MB for file uploads)
        public static var maxBodySize: ServerRequestBodySize? { .mb(50) }

        public let fileName: String
        public let fileData: Data
        // ... other fields

        public func validate(
            fields: [any FOSMVVM.FormFieldBase]?,
            validations: FOSMVVM.Validations
        ) -> FOSMVVM.ValidationResult.Status? {
            nil
        }
    }
    // ...
}
```

Available size units:
- `.bytes(_ count: UInt)` - Raw bytes
- `.kb(_ count: UInt)` - Kilobytes (× 1,024)
- `.mb(_ count: UInt)` - Megabytes (× 1,048,576)
- `.gb(_ count: UInt)` - Gigabytes (× 1,073,741,824)

### Custom ResponseError - Pattern 1: Associated Values

For errors with dynamic data in messages, use `LocalizableSubstitutions`:

```swift
public final class Create{Entity}Request: CreateRequest, @unchecked Sendable {
    public typealias ResponseError = Create{Entity}Error
    // ...
}

public struct Create{Entity}Error: ServerRequestError {
    public let code: ErrorCode
    public let message: LocalizableSubstitutions

    public enum ErrorCode: Codable {
        case duplicateContent
        case quotaExceeded(requestedSize: Int, maximumSize: Int)
        case invalidCategory(category: String)

        var message: LocalizableSubstitutions {
            switch self {
            case .duplicateContent:
                .init(
                    baseString: .localized(for: Self.self, parentType: Create{Entity}Error.self, propertyName: "duplicateContent"),
                    substitutions: [:]
                )
            case .quotaExceeded(let requestedSize, let maximumSize):
                .init(
                    baseString: .localized(for: Self.self, parentType: Create{Entity}Error.self, propertyName: "quotaExceeded"),
                    substitutions: [
                        "requestedSize": LocalizableInt(value: requestedSize),
                        "maximumSize": LocalizableInt(value: maximumSize)
                    ]
                )
            case .invalidCategory(let category):
                .init(
                    baseString: .localized(for: Self.self, parentType: Create{Entity}Error.self, propertyName: "invalidCategory"),
                    substitutions: [
                        "category": LocalizableString.constant(category)
                    ]
                )
            }
        }
    }

    public init(code: ErrorCode) {
        self.code = code
        self.message = code.message  // Required to localize properly via Codable
    }
}
```

```yaml
en:
  Create{Entity}Error:
    ErrorCode:
      duplicateContent: "The requested content is a duplicate."
      quotaExceeded: "Size %{requestedSize} exceeds maximum %{maximumSize}."
      invalidCategory: "The category %{category} is not valid."
```

### Custom ResponseError - Pattern 2: Simple String Codes

For simpler errors without associated values:

```swift
public struct Simple{Entity}Error: ServerRequestError {
    public let code: ErrorCode
    public let message: LocalizableString

    public enum ErrorCode: String, Codable, Sendable {
        case notFound
        case permissionDenied

        var message: LocalizableString {
            .localized(for: Self.self, parentType: Simple{Entity}Error.self, propertyName: rawValue)
        }
    }

    public init(code: ErrorCode) {
        self.code = code
        self.message = code.message
    }
}
```

```yaml
en:
  Simple{Entity}Error:
    ErrorCode:
      notFound: "The requested item was not found."
      permissionDenied: "You don't have permission to perform this action."
```

**Controller throwing custom error:**

```swift
private extension Create{Entity}Request {
    static func performCreate(
        _ request: Vapor.Request,
        _ serverRequest: Create{Entity}Request,
        _ requestBody: RequestBody
    ) async throws -> ResponseBody {
        // Check for duplicate
        if try await {Entity}.query(on: request.db)
            .filter(\.$content == requestBody.content)
            .first() != nil {
            throw Create{Entity}Error(code: .duplicateContent)
        }

        // Check quota
        let count = try await {Entity}.query(on: request.db).count()
        if count >= quotaLimit {
            throw Create{Entity}Error(code: .quotaExceeded(
                requestedSize: requestBody.size,
                maximumSize: quotaLimit
            ))
        }

        // ... proceed with creation
    }
}
```

**Client handling custom error:**

```swift
do {
    try await request.processRequest(mvvmEnv: mvvmEnv)
} catch let error as Create{Entity}Error {
    switch error.code {
    case .duplicateContent:
        showDuplicateWarning(message: error.message)
    case .quotaExceeded(let requestedSize, let maximumSize):
        showQuotaError(requested: requestedSize, maximum: maximumSize, message: error.message)
    case .invalidCategory(let category):
        highlightInvalidCategory(category, message: error.message)
    }
} catch {
    showGenericError(error)
}
```

---

## Checklist

### ServerRequest Type
- [ ] Extends correct protocol (ShowRequest, CreateRequest, UpdateRequest, DeleteRequest)
- [ ] RequestBody has all fields client needs to send
- [ ] ResponseBody contains what client needs back (often a ViewModel)
- [ ] ResponseError defined if operation has known failure modes (use EmptyError otherwise)
- [ ] Stubbable conformance for testing
- [ ] ValidatableModel on RequestBody (for write operations)
- [ ] `maxBodySize` set on RequestBody if handling large uploads (files, images, etc.)

### Controller
- [ ] Correct action mapping (.show, .create, .update, .delete)
- [ ] Fetches entity with relationships (`with(\.$relation)`)
- [ ] Uses `try entity.requireID()` not `id!`
- [ ] Returns fully populated response

### Registration
- [ ] Controller registered in routes.swift

### Client Invocation
- [ ] MVVMEnvironment configured once at app/tool startup
- [ ] Uses `request.processRequest(mvvmEnv:)` - NO baseURL/headers per-call
- [ ] Handles response via `request.responseBody`
- [ ] Catches custom `ResponseError` type if defined
- [ ] Generic error fallback for unexpected errors

### WebApp Bridge (if needed)
- [ ] MVVMEnvironment configured at WebApp startup
- [ ] Route decodes RequestBody
- [ ] Route uses `processRequest(mvvmEnv:)` (not hardcoded URL to WebServer)
- [ ] JS captures DOM references before await
- [ ] JS POSTs to WebApp, not WebServer

---

## Common Patterns

### ViewModel Response
```swift
public struct ResponseBody: UpdateResponseBody {
    public let viewModel: {Entity}CardViewModel
}
```

### ID-Only Response
```swift
public struct ResponseBody: CreateResponseBody {
    public let id: ModelIdType
}
```

### Empty Response
```swift
public typealias ResponseBody = EmptyBody
```

### Multiple ViewModels Response
```swift
public struct ResponseBody: ShowResponseBody {
    public let items: [{Entity}ViewModel]
    public let totalCount: Int
}
```

---

## Built-in ValidationError

FOSMVVM provides `ValidationError` for field-level validation. Use instead of custom error types for form validation:

```swift
// In controller
let validations = Validations()

if requestBody.email.isEmpty {
    validations.validations.append(.init(
        status: .error,
        fieldId: "email",
        message: .localized(for: Create{Entity}Request.self, propertyName: "emailRequired")
    ))
}

if let error = validations.validationError {
    throw error
}
```

```swift
// Client handling
catch let error as ValidationError {
    for validation in error.validations {
        for message in validation.messages {
            for fieldId in message.fieldIds {
                formFields[fieldId]?.showError(message.message)
            }
        }
    }
}
```

## Other Common Error Patterns

### Rate Limit Error
```swift
public struct RateLimitError: ServerRequestError {
    public let retryAfterSeconds: Int
    public let limit: Int
    public let resetAt: LocalizableDate
}
```

### Permission Error
```swift
public struct PermissionError: ServerRequestError {
    public let code: ErrorCode
    public let message: LocalizableString

    public enum ErrorCode: String, Codable, Sendable {
        case insufficientRole
        case accountSuspended

        var message: LocalizableString {
            .localized(for: Self.self, parentType: PermissionError.self, propertyName: rawValue)
        }
    }

    public init(code: ErrorCode) {
        self.code = code
        self.message = code.message
    }
}
```
