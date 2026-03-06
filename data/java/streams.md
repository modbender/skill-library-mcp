# Streams & CompletableFuture

## Streams Advanced
- Streams are single-use — can't reuse after terminal operation, create new stream
- `findFirst()` vs `findAny()` — findAny may return different element in parallel
- `flatMap()` flattens and maps — `Optional.flatMap()` unwraps nested Optionals
- `peek()` for debugging only — may not execute with short-circuit ops like `findFirst()`
- `toList()` (Java 16+) returns unmodifiable — `Collectors.toList()` is modifiable
- `groupingBy` with downstream — `groupingBy(key, counting())` for aggregation
- Infinite streams need limit — `Stream.iterate()` or `Stream.generate()` runs forever
- `reduce()` identity must be true identity — wrong value breaks parallel streams
- `collect()` vs `reduce()` — collect for mutable containers, reduce for immutable
- Primitive streams: `IntStream`, `LongStream` — avoid boxing overhead

## CompletableFuture Pitfalls
- `thenApply` vs `thenCompose` — compose unwraps nested futures, apply doesn't
- Exception handling: `exceptionally()` recovers, `handle()` transforms both success/failure
- `join()` vs `get()` — join throws unchecked CompletionException, get throws checked
- Default executor is ForkJoinPool.commonPool() — specify custom for blocking I/O
- `allOf()` returns `CompletableFuture<Void>` — must extract results manually
- `anyOf()` returns `CompletableFuture<Object>` — loses type safety
- `orTimeout()` and `completeOnTimeout()` — Java 9+, clean timeout handling
- Async variants: `thenApplyAsync()` — runs on different thread from executor
- `supplyAsync()` for computation — use executor argument for I/O-bound tasks
- Don't block in common pool — starves other parallel operations
