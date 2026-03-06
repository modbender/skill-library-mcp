# JVM, GC & Module System

## JVM/GC Pitfalls
- String concatenation uses `invokedynamic` — Java 9+, no StringBuilder needed in simple cases
- Escape analysis may stack-allocate — JIT optimization, don't rely on it for correctness
- G1GC is default since Java 9 — ZGC or Shenandoah for sub-millisecond pauses
- Set `-Xmx` equals `-Xms` in production — avoids heap resize pauses
- GC logs: `-Xlog:gc*` (Java 9+) — essential for troubleshooting
- Metaspace replaces PermGen (Java 8+) — can still OOM with classloader leaks
- `-XX:+UseStringDeduplication` — G1GC only, saves memory on duplicate strings
- Class Data Sharing (CDS) — `-Xshare:dump` and `-Xshare:on` for faster startup
- `jcmd` for runtime diagnostics — thread dumps, heap dumps, GC info
- Native memory: DirectByteBuffer — not in heap, can cause OOM outside -Xmx

## Module System (Java 9+)
- `module-info.java` at root — declares `requires`, `exports`, `opens`
- Split packages forbidden — same package can't exist in two modules
- Reflection needs `opens` — `opens pkg to framework;` for frameworks like Spring
- `requires transitive` exposes — readers of your module get the dependency too
- Automatic modules for classpath JARs — module name from JAR manifest or filename
- `--add-opens` at runtime — escape hatch when you can't modify module-info
- `exports` controls compile-time access — `opens` controls runtime reflection
- Service provider: `provides X with Y` — cleaner than ServiceLoader classpath scanning
- Unnamed module for classpath code — can read all named modules
- `jdeps` analyzes dependencies — use `--jdk-internals` to find illegal access
