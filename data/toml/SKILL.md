---
name: TOML
description: Write valid TOML configuration files with correct types and structure.
metadata: {"clawdbot":{"emoji":"⚙️","os":["linux","darwin","win32"]}}
---

## Strings

- Basic strings `"..."` support escapes: `\n`, `\t`, `\\`, `\"`
- Literal strings `'...'` are raw—no escape sequences, backslash is literal
- Multiline basic `"""..."""` allows newlines; leading newline after `"""` is trimmed
- Multiline literal `'''...'''` for raw blocks; no escape processing

## Keys

- Bare keys: alphanumeric, dash, underscore only—`key-name_1` valid
- Quoted keys for special chars: `"key with spaces"` or `'key.with.dots'`
- Dotted keys `a.b.c = 1` equivalent to nested tables—defines `[a.b]` implicitly
- Keys are case-sensitive—`Key` and `key` are different

## Tables

- `[table]` defines table; all following key-values belong to it until next header
- `[a.b.c]` creates nested structure—parent tables created implicitly
- Dotted keys under `[table]` extend it: `[fruit]` then `apple.color = "red"` works
- Defining table after dotted key created it is error—order matters

## Arrays of Tables

- `[[array]]` appends new table to array each time it appears
- `[[products]]` twice creates `products[0]` and `products[1]`
- Mix `[array.nested]` after `[[array]]` to add to most recent array element
- Cannot redefine static table as array or vice versa

## Inline Tables

- `point = { x = 1, y = 2 }` for compact single-line tables
- Inline tables cannot span lines (until TOML 1.1)
- Cannot add keys to inline table after definition—immutable once closed
- Nested inline tables allowed but reduce readability

## Types

- Integers: decimal, hex `0xDEAD`, octal `0o755`, binary `0b1010`
- Underscores for readability: `1_000_000` is valid
- Floats: `3.14`, `5e-10`, `inf`, `nan` (case-sensitive)
- Booleans: `true`/`false` only—lowercase, no yes/no/on/off

## Dates & Times

- RFC 3339 format: `2024-01-15T14:30:00Z` or with offset `+05:30`
- Local datetime: `2024-01-15T14:30:00` (no timezone)
- Local date: `2024-01-15`; Local time: `14:30:00`
- Milliseconds supported: `14:30:00.123`

## Common Pitfalls

- No null type—omit key entirely for optional values
- Arrays must be homogeneous (TOML 1.0)—TOML 1.1 allows mixed types
- Trailing commas not allowed in arrays or inline tables
- Comment `#` only outside strings—no inline comment after value on same line works, but avoid ambiguity
