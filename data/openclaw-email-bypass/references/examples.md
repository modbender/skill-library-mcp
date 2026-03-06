# OpenClaw Email Bypass Usage Examples

## Command Line Usage

### Simple Text Email
```bash
python3 scripts/send_email.py "recipient@example.com" "Hello" "Plain text message."
```

### HTML Email
```bash
python3 scripts/send_email.py "recipient@example.com" "Report" "Fallback" "<h1>HTML Content</h1>"
```

---

## Python Integration

```python
from scripts.send_email import send_email

send_email(
    to="dev@example.com",
    subject="Alert",
    body="System check passed."
)
```

---

## Troubleshooting

### Environment Errors
Ensure `GOOGLE_SCRIPT_URL` and `GOOGLE_SCRIPT_TOKEN` are exported in your current shell.

### Authorization Errors
Verify that `GOOGLE_SCRIPT_TOKEN` matches the `AUTH_TOKEN` in your Google Script Properties.
