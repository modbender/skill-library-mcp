# Testing and DI (SwiftUI)

Lightweight seams reduce refactor risk without introducing new tools or architecture mandates.

## Refactor safety seams

Use small, targeted seams to keep behavior stable while changing code.

- **Protocol abstraction:** define a protocol for external dependencies (network, storage, time).
- **Initializer injection with defaults:** inject dependencies, but provide a production default.
- **Closure-based seams:** inject a function for small, single-use dependencies.

```swift
protocol UserServiceProtocol {
    func fetchUser(id: String) async throws -> User
}

final class UserStore {
    private let userService: UserServiceProtocol

    init(userService: UserServiceProtocol = LiveUserService()) {
        self.userService = userService
    }
}
```

## Test doubles quick guide

- **Stub:** returns canned data (queries).
- **Mock:** verifies interactions (commands).
- **Spy:** records calls for later assertions.
- **Fake:** working in-memory implementation.

Minimal example (stub):
```swift
struct StubUserService: UserServiceProtocol {
    var result: Result<User, Error>

    func fetchUser(id: String) async throws -> User {
        try result.get()
    }
}
```

If tests exist, XCTest is the default baseline. Avoid adding new frameworks unless the project already uses them.

## When to add seams

Add seams before refactors that change:

- State ownership between views or wrappers.
- Navigation structure or destinations.
- Side-effect boundaries (networking, storage, analytics).

For refactor steps and invariants, see `references/workflows-refactor.md`.

## Optional tools

Third-party view inspection libraries (for example, ViewInspector) can be useful but are optional and not required.
