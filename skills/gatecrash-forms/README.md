# GateCrash Forms - OpenClaw Skill

This skill wraps the `gatecrash-forms` npm package for use in OpenClaw.

## Installation

The skill automatically installs the `gatecrash-forms` CLI via npm when you load it.

If you need to install manually:

```bash
npm install -g gatecrash-forms
```

## Usage in OpenClaw

Read the full SKILL.md for detailed instructions and examples.

### Quick Examples

**Generate a form:**
```
Generate a feedback form using the example schema in examples/feedback.json
```

**Start server:**
```
Start the GateCrash Forms server on port 3000
```

**Initialize project:**
```
Initialize GateCrash Forms in my current project directory
```

## Configuration

Set up your SMTP credentials globally:

```bash
gatecrash-forms config smtp.host smtp.example.com
gatecrash-forms config smtp.port 465
gatecrash-forms config smtp.secure true
gatecrash-forms config smtp.auth.user your-email@example.com
gatecrash-forms config smtp.auth.pass your-password
```

Or configure per-form in the JSON schema's `submit.smtp` field.

## Links

- **Main Project:** https://github.com/Phoenix2479/gatecrash-forms
- **npm Package:** https://www.npmjs.com/package/gatecrash-forms
- **Documentation:** See SKILL.md

---

*We crash gates. We don't build new ones.* 🚀
