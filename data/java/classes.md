# Classes, Inheritance & Memory

## Inheritance Quirks
- `private` methods not overridden — new method with same name in child
- `static` methods hide, don't override — called based on reference type, not object
- `super()` must be first statement in constructor — no logic before
- `final` methods can't be overridden — `final` class can't be extended
- Fields don't participate in polymorphism — accessed by reference type
- Constructors not inherited — must define explicitly or get default
- `@Override` annotation catches typos — compiler error if not actually overriding

## Memory Management
- Leaked listeners/callbacks prevent GC — remove references when done
- `WeakReference` for caches — allows GC when memory needed
- `static` collections grow forever — clear or use weak/soft references
- Inner classes hold reference to outer — use static nested class if not needed
- `finalize()` deprecated — use Cleaner or try-with-resources
- `SoftReference` vs `WeakReference` — soft cleared only on memory pressure
- PhantomReference for cleanup actions — use with ReferenceQueue

## Modern Java Features
- Records (16+): immutable data carriers — auto-generates equals, hashCode, toString
- Sealed classes (17+): restrict inheritance — `permits` clause lists allowed subclasses
- Pattern matching in switch (21+): type patterns and guards — cleaner than instanceof chains
- Virtual threads (21+): lightweight concurrency — don't pool, create freely
- `var` for local variables (10+) — inferred type, still strongly typed

## Records & Sealed Gotchas
- Records are implicitly final — can't extend, can implement interfaces
- Record components are final — can't reassign after construction
- Compact constructor for validation — `public Point { if (x < 0) throw ...; }`
- Full constructor needed for transformation — compact can't reassign components
- Records can have static fields and methods — but not instance fields
- Sealed classes: `permits` in same file — or same package if not explicit
- `non-sealed` subclass breaks the seal — any class can extend it
- Pattern matching deconstructs records — `case Point(int x, int y) when x > 0`
- Sealed interfaces work too — same rules apply
- Text blocks (15+): `"""` multiline strings — trailing whitespace stripped
