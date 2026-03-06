# Form Validation Patterns

## Built-in Browser Validation

| Attribute | Purpose | Example |
|-----------|---------|---------|
| `required` | Field must have value | `<input required>` |
| `type="email"` | Email format | `<input type="email">` |
| `type="url"` | URL format | `<input type="url">` |
| `type="tel"` | Phone (no format) | `<input type="tel">` |
| `minlength` / `maxlength` | Text length | `<input minlength="2" maxlength="50">` |
| `min` / `max` | Number range | `<input type="number" min="1" max="100">` |
| `pattern` | Regex pattern | `<input pattern="[A-Za-z]{3}">` |
| `accept` | File types | `<input type="file" accept=".pdf,image/*">` |

## Common Validation Rules

### Email
- Basic: `/.+@.+\..+/`
- Strict: `/^[\w-\.]+@([\w-]+\.)+[\w-]{2,}$/`
- Consider: `+` aliases (user+tag@gmail.com)

### Phone (International)
- Allow: digits, spaces, dashes, parentheses, plus
- Pattern: `/^\+?[\d\s\-()]{7,20}$/`
- Best: Use library (libphonenumber)

### Password Strength
```regex
// At least 8 chars, 1 upper, 1 lower, 1 number
/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$/

// Add special char
/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&]).{8,}$/
```

### URL
- Pattern: `/^https?:\/\/.+\..+/`
- Or use URL constructor with try/catch

### Credit Card
- Luhn algorithm for checksum
- Pattern for format: `/^\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}$/`

## Country-Specific Patterns

### Spain
| Document | Pattern | Notes |
|----------|---------|-------|
| DNI | `\d{8}[A-Z]` | 8 digits + letter |
| NIE | `[XYZ]\d{7}[A-Z]` | X/Y/Z + 7 digits + letter |
| CIF | `[A-Z]\d{7}[A-Z0-9]` | Company ID |
| IBAN (ES) | `ES\d{22}` | ES + 22 digits |

### US
| Document | Pattern | Notes |
|----------|---------|-------|
| SSN | `\d{3}-\d{2}-\d{4}` | xxx-xx-xxxx |
| ZIP | `\d{5}(-\d{4})?` | 5 or 9 digits |
| Phone | `\(\d{3}\) \d{3}-\d{4}` | (xxx) xxx-xxxx |

## Validation UX Best Practices

### When to Validate
| Event | Use For |
|-------|---------|
| `onBlur` | Most fields — validate when user leaves |
| `onChange` | Real-time (password strength meter) |
| `onSubmit` | Final validation, catch-all |

### Error Display
- Show errors near the field, not just top of form
- Use red color + icon for accessibility
- Clear error when user starts fixing

### Inline Feedback
```tsx
// Good: Progressive feedback
const [strength, setStrength] = useState('weak');

<input onChange={e => setStrength(calcStrength(e.target.value))} />
<meter value={strengthScore} max="4" />
<span>{strength}</span>
```

## Server-Side Validation (Critical)

**Never trust client-side validation alone.**

### Common Server Checks
- All required fields present
- Types match expected (number is number)
- Lengths within limits
- Foreign keys exist (country code valid)
- Permissions (can this user submit this?)
- Rate limiting (prevent spam)
- File validation (actual type, not just extension)

### Sanitization
- Trim whitespace
- Normalize unicode
- Escape HTML if storing raw
- Strip/reject script tags

## Async Validation Examples

### Email Availability
```ts
// Debounce to avoid spam
const checkEmail = debounce(async (email) => {
  const res = await fetch(`/api/check-email?email=${email}`);
  return res.ok ? null : 'Email already taken';
}, 500);
```

### Address Autocomplete Validation
```ts
// Verify selected address exists in Places API
const validateAddress = async (placeId) => {
  const details = await getPlaceDetails(placeId);
  return details ? null : 'Select a valid address';
};
```
