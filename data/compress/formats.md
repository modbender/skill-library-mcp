# Format-Specific Compression

## Code

**Strategy:** Structure-aware compression

- Remove comments (store separately if needed)
- Shorten variable names with mapping table
- Collapse whitespace
- Use function signatures as anchors
- Preserve import/dependency order

```python
# Original
def calculate_monthly_payment(principal, annual_rate, years):
    monthly_rate = annual_rate / 12
    num_payments = years * 12
    return principal * (monthly_rate * (1 + monthly_rate)**num_payments) / ((1 + monthly_rate)**num_payments - 1)

# L2 Compressed
# MAP: p=principal, r=annual_rate, y=years, mr=monthly_rate, n=num_payments
def calc_mp(p,r,y): mr=r/12; n=y*12; return p*(mr*(1+mr)**n)/((1+mr)**n-1)
```

---

## Markdown/Documentation

**Strategy:** Structural preservation

- Keep headers as anchors
- Compress body text per level
- Preserve code blocks separately
- Tables → compact notation

```markdown
# Original
## Installation
To install the package, run the following command in your terminal:
```bash
npm install mypackage
```

# L2 Compressed
## Installation
Install: `npm i mypackage`
```

---

## System Prompts

**Strategy:** Instruction preservation

- Keep all imperatives intact
- Compress examples aggressively
- Use numbered rules
- Abbreviate repeated patterns

```
# Original (250 tokens)
You are a helpful assistant. When the user asks a question, you should:
1. First, understand what they're asking
2. Then, provide a clear and concise answer
3. If you're not sure, say so rather than making things up
Always be polite and professional.

# L2 Compressed (80 tokens)
Helpful assistant. On questions: 1)understand 2)answer clearly 3)if unsure→say so. Be polite+professional.
```

---

## JSON/Config

**Strategy:** Key preservation

- Shorten keys with mapping
- Remove optional/default values
- Collapse nested structures

```json
// Original
{
  "configuration": {
    "database": {
      "host": "localhost",
      "port": 5432,
      "username": "admin"
    }
  }
}

// L3 Compressed + MAP
// MAP: cfg=configuration, db=database, h=host, p=port, u=username
{"cfg":{"db":{"h":"localhost","p":5432,"u":"admin"}}}
```

---

## Conversation History

**Strategy:** Turn-based compression

- Speaker tags: `U:` (user), `A:` (assistant)
- Collapse pleasantries
- Keep decisions and facts
- Remove filler turns

```
# Original
User: Hi there! How are you doing today?
Assistant: Hello! I'm doing well, thank you for asking. How can I help you today?
User: I need help with my Python code. I'm getting an error.
Assistant: I'd be happy to help! What error are you seeing?
User: It says "IndexError: list index out of range"

# L2 Compressed
U: help w/ Python err
A: what error?
U: IndexError: list index out of range
```

---

## Format Detection

Auto-detect and apply appropriate strategy:

| Pattern | Format |
|---------|--------|
| `def `, `function `, `class ` | Code |
| `# `, `## `, `- ` | Markdown |
| `{` + `"` | JSON |
| `User:`, `Human:`, `Assistant:` | Conversation |
| Imperatives, rules | System prompt |
