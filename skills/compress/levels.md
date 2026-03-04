# Compression Levels

## L1: Light (~0.8x ratio)

**Human-readable, minimal changes.**

Techniques:
- Remove filler words ("basically", "actually", "in order to")
- Normalize whitespace
- Collapse redundant phrasing
- Remove obvious context ("as mentioned above")

Example:
```
Original: "In order to successfully complete the task, you will basically need to..."
L1: "To complete the task, you need to..."
```

---

## L2: Moderate (~0.5x ratio)

**Abbreviations and shortcuts, still scannable by humans.**

Techniques:
- Common abbreviations (usr, req, resp, cfg, fn, var)
- Pronoun chains (replace repeated nouns)
- Implicit context (remove when recoverable)
- Numbered references instead of repeating

Example:
```
Original: "The user sends a request to the server. The server processes the request and returns a response to the user."
L2: "Usr→srv req. Srv processes, returns resp→usr."
```

---

## L3: Dense (~0.3x ratio)

**Structured notation, AI-preferred but humans can decode with effort.**

Techniques:
- Relationship notation: `A→B`, `X∈Y`, `P⊃Q`
- Entity codes: `[E1]=User`, `[E2]=Server`
- Compressed templates: `{action}({agent},{target},{result})`
- Remove all redundancy

Example:
```
Original: Full API documentation with examples
L3: "EP:/users POST{name,email}→201{id,created} | GET{id}→200{user} | ERR:400invalid,404notfound"
```

---

## L4: Maximum (~0.15x ratio)

**Pure semantic encoding, requires LLM to decode. Not human-readable.**

Techniques:
- Entity-relationship graphs
- Semantic triples
- Domain-specific micro-languages
- Reference tables + indices

Example:
```
Original: Multi-page technical specification
L4: "§[1:cfg,2:api,3:err] E{U,S,D,R} R{U→S:auth,S→D:qry,D→R:fmt} F{1.2.a,1.2.b,2.1.c}"
```

**Warning:** L4 requires decompression prompt. Store separately.

---

## Choosing a Level

| Scenario | Level |
|----------|-------|
| Team docs (humans will read) | L1 |
| System prompts (repeated use) | L2 |
| Context injection (fit more in) | L3 |
| Long-term storage (max savings) | L4 |
| Unknown future use | L2 (safe default) |
