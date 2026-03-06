# HTML Email Templates

This directory contains pre-built HTML email templates that can be used with the gog CLI.

## Template Files

All templates are single-line HTML (no newlines) to prevent formatting issues when used with bash commands. Each template uses placeholder variables in `[BRACKETS]` that you replace with actual content.

### Template List

**Business & Professional:**
- **basic.html** - Simple professional email
- **highlight.html** - Email with highlighted information box
- **button.html** - Email with call-to-action button
- **multi-paragraph.html** - Multiple paragraph email
- **meeting.html** - Meeting invitation with details box
- **follow-up.html** - Follow-up email template
- **newsletter.html** - Newsletter format with sections
- **invoice.html** - Invoice notification with payment button
- **welcome.html** - Welcome email with CTA button
- **status-update.html** - Project status with color-coded sections

**Special Occasions:**
- **jummah.html** - Jummah Mubarak greeting (blue gradient, Islamic theme)
- **eid.html** - Eid Mubarak greeting (green gradient, Islamic blessings)
- **ramadan.html** - Ramadan Mubarak greeting (purple gradient, blessed month)
- **birthday.html** - Birthday wishes (pink gradient, celebration theme)
- **anniversary.html** - Anniversary wishes (pink-yellow gradient, romantic)
- **congratulations.html** - Congratulations message (gold-blue gradient, success)
- **thank-you.html** - Thank you message (pastel gradient, gratitude)
- **new-year.html** - New Year wishes (purple gradient, celebration)

## Usage Pattern

```bash
# 1. Read the template file
TEMPLATE=$(cat workspace/skills/gog-html-email/templates/TEMPLATE_NAME.html)

# 2. Replace placeholders using sed
HTML=$(echo "$TEMPLATE" | sed 's/\[PLACEHOLDER1\]/value1/g' | sed 's/\[PLACEHOLDER2\]/value2/g')

# 3. Send via gog
gog gmail send --to recipient@example.com --subject "Subject" --body-html "$HTML"
```

## Important Notes

- All templates use inline CSS for maximum email client compatibility
- Templates are single-line to avoid bash heredoc issues
- Always use `<p>` tags or `<br>` for line breaks, never literal `\n` characters
- Max width is 600px for optimal viewing across devices
- System fonts are used for best cross-platform rendering

## Customization

You can create your own templates by:
1. Copying an existing template
2. Modifying the HTML structure and styling
3. Using `[PLACEHOLDER]` syntax for dynamic content
4. Keeping everything on a single line (no newlines in the HTML)

## Testing

Always test your emails before sending to recipients:

```bash
# Send test to yourself
gog gmail send --to your-email@example.com --subject "Test" --body-html "$HTML"
```
