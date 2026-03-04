# Fastmail Email & Calendar Management Skill

OpenCode skill for managing Fastmail email and calendar via JMAP and CalDAV APIs.

## Features

🔹 **9 Email Management Tools:**

| Tool | Description |
|------|-------------|
| `list_mailboxes` | List all folders/mailboxes |
| `list_emails` | List emails in inbox or specific folder |
| `get_email` | Get full email content |
| `search_emails` | Search emails by text query |
| `send_email` | Send new email |
| `reply_email` | Reply to email (with reply-all option) |
| `move_email` | Move email to different folder |
| `set_labels` | Set labels/keywords ($seen, $flagged, etc.) |
| `delete_email` | Delete email (move to trash) |

🔹 **8 Calendar Management Tools:**

| Tool | Description |
|------|-------------|
| `list_calendars` | List all calendars |
| `list_events` | List events in date range |
| `get_event` | Get event details |
| `create_event` | Create new event |
| `update_event` | Update existing event |
| `delete_event` | Delete event |
| `search_events` | Search events by title/description |
| `create_recurring_event` | Create recurring event |

🔹 **4 Reminder/Alarm Tools:**

| Tool | Description |
|------|-------------|
| `add_event_reminder` | Add reminder to existing event |
| `remove_event_reminder` | Remove reminder(s) from event |
| `list_event_reminders` | List reminders for event |
| `create_event_with_reminder` | Create event with reminder(s) |

**Total: 21 MCP Tools**

## Setup

### 1. Generate Fastmail API Token (For Email)

1. Log in to [Fastmail](https://www.fastmail.com)
2. Go to **Settings** → **Privacy & Security** → **Integrations**
3. Click **New API token**
4. Name it: `OpenCode Nisha` (or any name you prefer)
5. Click **Generate**
6. **Copy the token** - you won't see it again!

### 2. Generate App Password (For Calendar)

1. Go to **Settings** → **Privacy & Security** → **Integrations**
2. Click **New app password**
3. Name it: `Calendar Sync`
4. **Copy the password** - this is different from your main password!

### 3. Set Environment Variables

Add to your shell profile (`~/.zshrc`, `~/.bashrc`, etc.):

```bash
# For Email (JMAP)
export FASTMAIL_API_TOKEN="your-api-token-here"

# For Calendar (CalDAV)
export FASTMAIL_USERNAME="your-email@fastmail.com"
export FASTMAIL_PASSWORD="your-app-password-here"
```

Or create a `.env` file:

```bash
echo "FASTMAIL_API_TOKEN=your-api-token-here" >> .env
echo "FASTMAIL_USERNAME=your-email@fastmail.com" >> .env
echo "FASTMAIL_PASSWORD=your-app-password-here" >> .env
```

Then reload:
```bash
source ~/.zshrc  # or source ~/.bashrc
```

### 4. Verify Installation

```bash
cd .opencode/skills/fastmail
bun install
bunx fastmail --help
```

## Usage Examples

### Email Commands

**Check your inbox:**
```
User: "Show me my latest emails"
User: "What's in my inbox?"
```

**Search emails:**
```
User: "Search for emails from john@example.com"
User: "Find emails about 'project alpha'"
```

**Send email:**
```
User: "Send email to sarah@example.com with subject 'Meeting Tomorrow' and body 'Let's meet at 2pm'"
```

**Reply to email:**
```
User: "Reply to the email from John saying 'Thanks, sounds good!'"
```

### Calendar Commands (Thai)

**ดูปฏิทิน:**
```
User: "แสดงปฏิทินทั้งหมด"
User: "มีกี่ปฏิทิน"
```

**ดูกิจกรรม:**
```
User: "ดูกิจกรรมวันนี้"
User: "มีนัดอะไรสัปดาห์นี้"
User: "แสดงกิจกรรมเดือนนี้"
```

**สร้างกิจกรรม:**
```
User: "สร้างนัดหมายชื่อ 'ประชุมทีม' วันพรุ่งนี้ 10:00-11:00"
User: "เพิ่มกิจกรรม 'พบลูกค้า' วันที่ 15 กุมภาพันธ์ 14:00-15:30"
```

**ค้นหากิจกรรม:**
```
User: "ค้นหากิจกรรมที่มีคำว่า 'ประชุม'"
User: "หานัดที่เกี่ยวกับโครงการ A"
```

**ลบกิจกรรม:**
```
User: "ลบกิจกรรม [event-id]"
```

### Reminder Commands (Thai)

**เพิ่ม reminder:**
```
User: "เพิ่ม reminder ก่อน event [id] 15 นาที"
User: "ตั้ง reminder ก่อน 1 ชั่วโมง"
```

**ดู reminders:**
```
User: "แสดง reminders ของ event [id]"
```

**ลบ reminder:**
```
User: "ลบ reminder ออกจาก event [id]"
```

**สร้าง event พร้อม reminder:**
```
User: "สร้างนัด 'ประชุมทีม' พรุ่งนี้ 10:00-11:00 เตือนก่อน 15 นาทีและ 1 ชั่วโมง"
```

## Timezone Information

**Calendar times use your local timezone by default**

You can configure the timezone with the `FASTMAIL_TIMEZONE` environment variable:

```bash
# Use local system timezone (default - no configuration needed)
# Or explicitly set a timezone:
export FASTMAIL_TIMEZONE="America/New_York"  # or "Asia/Bangkok", "Europe/London", etc.
```

- **Default:** Auto-detects your system's local timezone
- **Input:** Accept times in configured timezone format
- **Storage:** Stored as UTC internally
- **Display:** Converted to configured timezone for display
- **DST:** Handles Daylight Saving Time automatically

Example (with Asia/Bangkok timezone):
- You say: "สร้างนัด 10:00" (assumed local timezone)
- Stored as: 03:00 UTC
- Displayed as: 10:00+07:00

## Technical Details

### Architecture

```
.opencode/skills/fastmail/
├── SKILL.md                    # Skill metadata
├── README.md                   # Documentation
├── package.json                # Dependencies
├── tsconfig.json               # TypeScript config
├── scripts/                    # Executable code
│   ├── cli.ts                 # CLI entry point (21 tools)
│   ├── jmap-client.ts         # JMAP API client (email)
│   ├── caldav-client.ts       # CalDAV client (calendar)
│   └── tools/
│       ├── email.ts           # Email operations
│       └── calendar.ts        # Calendar operations
└── references/
    └── TOOLS.md               # Detailed tool reference
```

### APIs Used

**Email - JMAP:**
- Modern JSON-based protocol
- Fast batch operations
- Efficient syncing

**Calendar - CalDAV:**
- Industry standard protocol
- iCalendar (ICS) format
- Full recurring event support

### Dependencies

```json
{
  "@modelcontextprotocol/sdk": "^1.0.0",
  "tsdav": "^2.1.2",      // CalDAV client
  "uuid": "^9.0.0"         // Event ID generation
}
```

### Requirements

- [Bun](https://bun.sh/) - JavaScript runtime (install with `curl -fsSL https://bun.sh/install | bash`)

## Troubleshooting

### Email Issues

**Error: "FASTMAIL_API_TOKEN environment variable is required"**

**Solution:** Set the environment variable (see Setup above)

Verify it's set:
```bash
echo $FASTMAIL_API_TOKEN
```

**Error: "Failed to get session: 401 Unauthorized"**

**Cause:** Invalid or expired API token

**Solution:** Generate new token from Fastmail Settings

### Calendar Issues

**Error: "Calendar support disabled"**

**Cause:** FASTMAIL_USERNAME or FASTMAIL_PASSWORD not set

**Solution:** Set both environment variables

**Error: "401 Unauthorized" when using calendar**

**Cause:** Invalid app password

**Solution:** 
1. Check you're using app password (not main password)
2. Generate new app password from Fastmail Settings
3. Verify FASTMAIL_USERNAME includes full email

**Error: "Calendar not found"**

**Solution:** Use `list_calendars` to see available calendars

### TypeScript Build Errors

**Solution:** Rebuild the project:
```bash
cd .opencode/skills/fastmail
bun run build
```

## Development

### Run in Dev Mode

```bash
cd .opencode/skills/fastmail
bunx fastmail --help
```

### Build

```bash
bun run build
```

### Project Structure

- **`scripts/cli.ts`** - CLI entry point with 21 tool definitions
- **`scripts/jmap-client.ts`** - JMAP API client for email
- **`scripts/caldav-client.ts`** - CalDAV client for calendar
- **`scripts/tools/email.ts`** - Email operations (9 methods)
- **`scripts/tools/calendar.ts`** - Calendar operations (8 methods)

## Limitations

- **Fastmail only:** Uses Fastmail-specific APIs
- **No attachments:** File upload/download not yet implemented
- **No contacts:** Contact management not yet implemented
- **CalDAV only:** JMAP Calendar not yet available from Fastmail

## Security

- ✅ API token via environment variable (never hardcoded)
- ✅ App password for calendar (separate from main password)
- ✅ HTTPS for all API calls
- ✅ No sensitive data in logs
- ⚠️ Tokens have full account access - keep them secret!

**Best practices:**
- Use `.env` file (add to `.gitignore`)
- Rotate tokens if compromised
- Use unique token per application
- Use app passwords (not main password) for calendar

## Resources

- [Fastmail API Documentation](https://www.fastmail.com/dev/)
- [JMAP Specification](https://jmap.io/spec.html)
- [CalDAV RFC](https://datatracker.ietf.org/doc/html/rfc4791)
- [iCalendar Format](https://icalendar.org/)

## Support

For issues or questions:
1. Check `.sisyphus/notepads/fastmail-agent-skill/` for detailed docs
2. Review `issues.md` for common problems
3. Check Fastmail API status: https://fastmailstatus.com/

## License

Part of OpenCode project - follows project licensing.

---

Built with ❤️ using JMAP, CalDAV, and TypeScript
