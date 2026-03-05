# paste.rs API (quick reference)

- Endpoint: `POST https://paste.rs`
- Request body: raw bytes (treat as text; UTF-8 recommended)
- Response body (success): a single URL string to the paste, e.g. `https://paste.rs/abcd`

Examples:

```bash
# stdin
printf 'hello\n' | curl -fsS https://paste.rs -d @-

# file
curl -fsS https://paste.rs -d @README.md
```

Notes:
- paste.rs stores raw text; Markdown/HTML are pasted as-is.
- No auth required.
