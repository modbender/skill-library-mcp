# SwiftUI State Traps

- `@State` must be private — shared state should use `@StateObject` or `@ObservedObject`
- `@StateObject` owns the object, `@ObservedObject` borrows — recreating view recreates ObservedObject
- `@Binding` with local state corrupts — don't derive Binding from @State in child then mutate both
- `@EnvironmentObject` crashes at runtime if not injected — no compile-time safety
- View identity determines state lifecycle — changing ID (explicit or implicit) resets all @State
- `ForEach` without `id:` or `Identifiable` conformance causes misrendering or crashes on mutation
- `GeometryReader` inside ScrollView breaks intrinsic sizing — use preference keys or overlay instead
- `onAppear` fires on every navigation return — not just initial appearance, use `task` with cancellation

# Combine Pitfalls

- Sink without storing `AnyCancellable` — subscription immediately cancelled, no values received
- `receive(on:)` after `sink` has no effect — must be before terminal subscriber
- `assign(to:on:)` creates strong reference to target — use `assign(to: &$published)` for @Published
- Memory leaks in custom Publishers — prefer `PassthroughSubject` or `CurrentValueSubject` over raw Publisher
- `eraseToAnyPublisher()` loses specific operators — chain everything before erasing
- Debugging Combine pipelines — insert `print("label")` operator to log all events
