# Codable Pitfalls

- Missing key throws by default — use `decodeIfPresent` or custom init
- Type mismatch throws — `"123"` won't decode to `Int` automatically
- Enum raw value must match exactly — `"status": "ACTIVE"` fails for `.active` case
- Nested containers need manual `CodingKeys` at each level
- Custom `init(from:)` must decode ALL properties or provide defaults
