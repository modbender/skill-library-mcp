# Testing & Serialization

## JUnit 5 Traps
- `@Test` has no expected attribute — use `assertThrows(Exception.class, () -> code)`
- `@BeforeEach` runs per test — `@BeforeAll` once per class (must be static)
- `assertEquals(expected, actual)` — order matters for failure messages
- `assertAll()` for grouped assertions — reports all failures, not just first
- `@Disabled` skips test — not `@Ignore` (that's JUnit 4)
- `@Nested` for test organization — inner class inherits `@BeforeEach`
- `@ParameterizedTest` needs source — `@ValueSource`, `@CsvSource`, `@MethodSource`
- `@TempDir` for temporary files — cleaned up automatically after test

## Mockito Pitfalls
- `when().thenReturn()` for stubbing — must call on mock, not real method
- `verify()` checks interaction — call after the action, not before
- `@Mock` creates fake object — all methods return defaults (null, 0, false)
- `@Spy` wraps real object — real methods called unless stubbed
- `@InjectMocks` does constructor injection — or setter, or field injection
- `ArgumentCaptor` for complex assertions — capture arguments, verify later
- `doReturn().when()` for spies — regular `when()` calls real method first
- `reset()` is code smell — usually means test does too much

## Serialization Gotchas
- `serialVersionUID` must match — mismatch throws InvalidClassException
- `transient` fields not serialized — will be null/default on deserialization
- Custom `writeObject`/`readObject` — must be private, exact signature matters
- Static fields not serialized — belong to class, not instance
- Prefer JSON/Protobuf over Java serialization — security vulnerabilities (CVEs)
- `readResolve()` for singletons — return canonical instance to preserve identity
- Inheritance: parent must be Serializable or have no-arg constructor
- `Externalizable` for full control — must implement `writeExternal`/`readExternal`
