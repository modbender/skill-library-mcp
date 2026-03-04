---
name: password-gen
description: "Secure password generator with multiple character sets and strength analysis. Use when: (1) generating strong passwords, (2) creating memorable passphrases, (3) analyzing password strength, or (4) any password-related security needs. Supports random passwords, passphrases, and detailed strength analysis."
---

# Password Generator

Generate secure passwords and passphrases locally. No network calls - everything is generated on your machine using cryptographically secure random functions.

## When to Use

- Generate strong passwords for accounts
- Create memorable passphrases
- Analyze existing password strength
- Build secure password policies

## Quick Start

### Generate Strong Password
```bash
python3 scripts/password-gen.py generate
# Output: 🔐 Password Generated
#         Password: K:kx]h--Xo<RKwKp
#         Length: 16
#         Strength: Strong
```

### Generate Passphrase
```bash
python3 scripts/password-gen.py passphrase 6
# Output: Password: lambda-window-yellow-nu-mu
```

### Analyze Password
```bash
python3 scripts/password-gen.py analyze "MyPassword123!"
```

## Commands

### `generate [length] [options]`
Generate a random password with specified options.

**Options:**
- `--no-upper` - Exclude uppercase letters
- `--no-lower` - Exclude lowercase letters
- `--no-digits` - Exclude digits
- `--no-symbols` - Exclude symbols
- `--exclude-ambiguous` - Exclude ambiguous characters (0,O,l,I)
- `--exclude-similar` - Exclude similar characters

**Examples:**
```bash
# Default 16-character password
python3 scripts/password-gen.py generate

# 20-character password
python3 scripts/password-gen.py generate 20

# Letters only (no symbols)
python3 scripts/password-gen.py generate 12 --no-symbols

# Numbers and letters only
python3 scripts/password-gen.py generate 16 --no-symbols

# Exclude ambiguous characters
python3 scripts/password-gen.py generate 16 --exclude-ambiguous

# Custom combination
python3 scripts/password-gen.py generate 12 --no-upper --no-symbols
```

### `passphrase [word_count] [options]`
Generate a memorable passphrase (series of words).

**Options:**
- `--separator=char` - Word separator (default: "-")

**Examples:**
```bash
# Default 4-word passphrase
python3 scripts/password-gen.py passphrase

# 6-word passphrase
python3 scripts/password-gen.py passphrase 6

# Custom separator
python3 scripts/password-gen.py passphrase 5 --separator="_"
```

### `analyze <password>`
Analyze the strength and composition of a password.

**Examples:**
```bash
python3 scripts/password-gen.py analyze "MyPassword123!"

python3 scripts/password-gen.py analyze "weakpass"
```

### `list`
List available character sets and excluded characters.

```bash
python3 scripts/password-gen.py list
```

## Password Strength Levels

- **Weak** - Short or missing character types
- **Medium** - Decent length with multiple character types
- **Strong** - Long with all character types
- **Very Strong** - Very long with diverse character set

## Security Features

- Uses `secrets` module for cryptographically secure randomness
- No network requests - all generation is local
- Configurable character sets
- Excludes ambiguous characters option
- Strength analysis and recommendations

## Character Sets

- **Lowercase letters**: a-z (or a-z without l,o if excluding ambiguous)
- **Uppercase letters**: A-Z (or A-Z without I,O if excluding ambiguous)
- **Digits**: 0-9 (or 2-9 if excluding ambiguous)
- **Symbols**: !@#$%^&*()_+-=[]{}|;:,.<>?~`

## Examples

### Basic Usage
```bash
# Generate strong password
python3 scripts/password-gen.py generate

# Generate 24-character password
python3 scripts/password-gen.py generate 24
```

### For Different Use Cases
```bash
# Database password (no ambiguous chars)
python3 scripts/password-gen.py generate 20 --exclude-ambiguous

# PIN code (numbers only)
python3 scripts/password-gen.py generate 6 --no-upper --no-lower --no-symbols

# Website password (letters and numbers)
python3 scripts/password-gen.py generate 16 --no-symbols

# Memorable password (passphrase)
python3 scripts/password-gen.py passphrase 5
```

### Analysis Examples
```bash
# Analyze existing password
python3 scripts/password-gen.py analyze "MyPassword123!"

# Check if password is weak
python3 scripts/password-gen.py analyze "password123"
```

## Tips

- Use at least 12-16 characters for good security
- Include all character types when possible
- Consider passphrases for better memorability
- Avoid using personal information
- Use different passwords for different accounts
- Consider using a password manager

## Troubleshooting

**"Password too weak" warnings:**
- Increase length
- Add more character types
- Use the `--exclude-ambiguous` option for clarity

**"Command not found":**
- Ensure Python 3 is installed
- Check script permissions: `chmod +x scripts/password-gen.py`

## Security Notes

- Generated passwords are shown in plain text
- Copy passwords immediately after generation
- Don't save passwords in command history
- Use secure methods to store generated passwords
- Consider using a password manager for storage
