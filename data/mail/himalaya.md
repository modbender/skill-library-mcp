# himalaya CLI Patterns

## Installation

```bash
brew install himalaya
# or
cargo install himalaya
```

## Configuration

File: `~/.config/himalaya/config.toml`

```toml
[accounts.default]
default = true
email = "user@gmail.com"
display-name = "Your Name"

backend.type = "imap"
backend.host = "imap.gmail.com"
backend.port = 993
backend.encryption = "tls"
backend.login = "user@gmail.com"
backend.passwd.cmd = "security find-internet-password -s imap.gmail.com -a user@gmail.com -w"

sender.type = "smtp"
sender.host = "smtp.gmail.com"
sender.port = 587
sender.encryption = "starttls"
sender.login = "user@gmail.com"
sender.passwd.cmd = "security find-internet-password -s smtp.gmail.com -a user@gmail.com -w"
```

## Essential Commands

| Command | Purpose |
|---------|---------|
| `himalaya envelope list -o json` | List emails (NOT `message list`) |
| `himalaya message read <id>` | Read email body |
| `himalaya message send` | Send from stdin (RFC 2822) |
| `himalaya folder list` | List all folders |
| `himalaya message move <id> <folder>` | Move to folder (case-sensitive) |

## Traps

- **Always use `-o json`**: Plain text output is hard to parse
- **Folder names case-sensitive**: "INBOX" ≠ "inbox"
- **Cache refresh needed**: After server-side folder changes, run `himalaya folder list`
- **Send reads stdin**: Pipe RFC 2822 formatted message, don't pass as argument
- **OAuth setup**: Use `token_cmd` in config for XOAUTH2 flows
