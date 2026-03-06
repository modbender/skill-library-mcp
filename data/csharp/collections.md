# Collection Traps

- Modify during foreach — throws `InvalidOperationException`
- `Dictionary` key not found — throws, use `TryGetValue` or `GetValueOrDefault`
- `List<T>.Remove()` during iteration — use reverse for loop or `RemoveAll()`
- `HashSet` equality — uses `EqualityComparer<T>.Default`, override `GetHashCode`
- Array covariance — `string[]` assignable to `object[]`, but storing int throws
- `IReadOnlyList` — doesn't prevent cast back to mutable list
- `ConcurrentDictionary.GetOrAdd` — factory may run multiple times (race)
- Struct in collection — copied on access, modification doesn't update collection
