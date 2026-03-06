# NEAR Email Reporter Skill

Send NEAR transaction reports via email.

## Installation

The skill is installed in `~/.openclaw/skills/near-email-reporter/`

## Usage

### Setup Email Configuration

```bash
node scripts/emailer.js setup \
  --host smtp.gmail.com \
  --port 587 \
  --user myemail@gmail.com \
  --pass myapppassword \
  --from myemail@gmail.com
```

### Send a Report

```bash
node scripts/emailer.js report myaccount.near recipient@gmail.com
```

### Set Up Alerts

```bash
node scripts/emailer.js alert myaccount.near 10.0
```

### Schedule Reports

```bash
node scripts/emailer.js schedule myaccount.near "0 9 * * *"
```

## Requirements

For actual email sending, install nodemailer:
```bash
npm install nodemailer
```

## Notes

- Configuration is stored in `~/.near-email/config.json`
- For Gmail, use App Passwords: https://myaccount.google.com/apppasswords
- Configure script to use nodemailer for actual email sending

## License

MIT
