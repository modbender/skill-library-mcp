# Testing Traps (XCTest)

- `XCTAssertEqual` with floating point — use `accuracy:` parameter for doubles
- Async test without expectation — test passes before async work completes
- `setUp()` vs `setUpWithError()` — latter throws, former swallows failures silently
- `@testable import` required for internal access — without it only public symbols visible
- Mock protocols need manual conformance — no automatic mocking, consider sourcery/swift-macro
- Test parallelization shares state — use `setUp` to reset, avoid static mutable state
- `XCTUnwrap` vs manual unwrap — prefer XCTUnwrap for clearer failure messages

# SPM Gotchas

- Version resolution conflicts — pin exact versions or use branch-based dependencies carefully
- Local package changes need `swift package resolve` — Xcode doesn't always auto-detect
- Platform-conditional dependencies use `#if` in targets — not in Package.swift directly
- Resources must be in `Package.swift` resources: — files in Sources/ not auto-bundled
- Plugins (build tools, commands) have sandboxed filesystem access — can't write anywhere
- Binary targets must specify exact checksums — updates require manifest changes
