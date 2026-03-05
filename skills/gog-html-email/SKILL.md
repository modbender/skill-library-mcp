---
name: gog-html-email
description: Send beautifully formatted HTML emails via gog CLI with templates and styling
homepage: https://gogcli.sh
metadata:
  {
    "openclaw":
      {
        "emoji": "📧",
        "requires": { "bins": ["gog"] }
      }
  }
---

# gog-html-email

Enhanced HTML email formatting for gog CLI with ready-to-use templates.

## How to Send HTML Emails

**ALWAYS use this exact workflow:**

1. Read the appropriate template file from `workspace/skills/gog-html-email/templates/`
2. Replace placeholders using `sed` commands
3. Send via `gog gmail send --body-html`

**Example:**
```bash
TEMPLATE=$(cat workspace/skills/gog-html-email/templates/basic.html)
HTML=$(echo "$TEMPLATE" | sed 's/\[NAME\]/John/g' | sed 's/\[MESSAGE\]/Your message here/g' | sed 's/\[SIGNATURE\]/Your Name/g')
gog gmail send --to recipient@example.com --subject "Subject" --body-html "$HTML"
```

**For multi-paragraph messages:**
```bash
TEMPLATE=$(cat workspace/skills/gog-html-email/templates/basic.html)
# Replace [MESSAGE] with multiple <p> tags for proper spacing
MESSAGE='<p style="margin: 0 0 16px 0;">First paragraph.</p><p style="margin: 0 0 16px 0;">Second paragraph.</p><p style="margin: 0 0 16px 0;">Third paragraph.</p>'
HTML=$(echo "$TEMPLATE" | sed "s|\[MESSAGE\]|$MESSAGE|g" | sed 's/\[NAME\]/John/g' | sed 's/\[SIGNATURE\]/Your Name/g')
gog gmail send --to recipient@example.com --subject "Subject" --body-html "$HTML"
```

**DO NOT:**
- Manually construct HTML strings
- Use heredocs or multi-line strings
- Include literal `\n` characters in HTML
- Put multiple paragraphs in a single `<p>` tag

## Template Selection Guide

Choose the right template based on the email purpose:

**Business/Professional:**
- `basic.html` - Simple professional emails
- `meeting.html` - Meeting invitations (requires: NAME, TOPIC, DATE, TIME, DURATION, LOCATION, SIGNATURE)
- `follow-up.html` - Follow-up emails
- `status-update.html` - Project updates
- `invoice.html` - Invoices and payments
- `button.html` - Emails with call-to-action buttons
- `newsletter.html` - Newsletters

**Islamic/Religious:**
- `jummah.html` - Friday greetings (Jummah Mubarak)
- `eid.html` - Eid celebrations (Eid Mubarak)
- `ramadan.html` - Ramadan greetings (Ramadan Mubarak)

**Celebrations:**
- `birthday.html` - Birthday wishes
- `anniversary.html` - Anniversary wishes
- `congratulations.html` - Congratulations messages
- `new-year.html` - New Year wishes (requires: NAME, MESSAGE, YEAR, SIGNATURE)

**Other:**
- `welcome.html` - Welcome new users
- `thank-you.html` - Thank you messages
- `highlight.html` - Important announcements
- `multi-paragraph.html` - Long-form content

## HTML Template Files

All templates are available in the `templates/` directory. Each template uses placeholder variables in `[BRACKETS]` that you can replace with actual content.

### Available Templates

1. **basic.html** - Simple professional email
   - Placeholders: `[NAME]`, `[MESSAGE]`, `[SIGNATURE]`

2. **highlight.html** - Email with highlighted box
   - Placeholders: `[NAME]`, `[HIGHLIGHT_MESSAGE]`, `[MESSAGE]`, `[SIGNATURE]`

3. **button.html** - Email with call-to-action button
   - Placeholders: `[NAME]`, `[MESSAGE]`, `[BUTTON_URL]`, `[BUTTON_TEXT]`, `[SIGNATURE]`

4. **multi-paragraph.html** - Multiple paragraph email
   - Placeholders: `[NAME]`, `[PARAGRAPH_1]`, `[PARAGRAPH_2]`, `[PARAGRAPH_3]`, `[SIGNATURE]`

5. **meeting.html** - Meeting invitation
   - Placeholders: `[NAME]`, `[TOPIC]`, `[DATE]`, `[TIME]`, `[DURATION]`, `[LOCATION]`, `[SIGNATURE]`

6. **follow-up.html** - Follow-up email
   - Placeholders: `[NAME]`, `[TOPIC]`, `[MESSAGE]`, `[SIGNATURE]`

7. **newsletter.html** - Newsletter format
   - Placeholders: `[NEWSLETTER_TITLE]`, `[DATE]`, `[SECTION_1_TITLE]`, `[SECTION_1_CONTENT]`, `[SECTION_2_TITLE]`, `[SECTION_2_CONTENT]`

8. **invoice.html** - Invoice notification
   - Placeholders: `[NAME]`, `[INVOICE_NUMBER]`, `[DATE]`, `[AMOUNT]`, `[DUE_DATE]`, `[DESCRIPTION]`, `[PAYMENT_URL]`, `[SIGNATURE]`

9. **welcome.html** - Welcome email with CTA
   - Placeholders: `[NAME]`, `[MESSAGE]`, `[GET_STARTED_URL]`, `[SIGNATURE]`

10. **status-update.html** - Project status update
    - Placeholders: `[NAME]`, `[PROJECT_NAME]`, `[COMPLETED_ITEMS]`, `[IN_PROGRESS_ITEMS]`, `[BLOCKED_ITEMS]`, `[NEXT_STEPS]`, `[SIGNATURE]`

### Special Occasion Templates

11. **jummah.html** - Jummah Mubarak greeting
    - Placeholders: `[NAME]`, `[MESSAGE]`, `[SIGNATURE]`
    - Features: Islamic greeting with blue gradient background

12. **eid.html** - Eid Mubarak greeting
    - Placeholders: `[NAME]`, `[MESSAGE]`, `[SIGNATURE]`
    - Features: Green gradient background with Islamic blessings

13. **ramadan.html** - Ramadan Mubarak greeting
    - Placeholders: `[NAME]`, `[MESSAGE]`, `[SIGNATURE]`
    - Features: Purple gradient background with Ramadan wishes

14. **birthday.html** - Birthday wishes
    - Placeholders: `[NAME]`, `[MESSAGE]`, `[SIGNATURE]`
    - Features: Pink gradient background with celebration emojis

15. **anniversary.html** - Anniversary wishes
    - Placeholders: `[NAME]`, `[MESSAGE]`, `[SIGNATURE]`
    - Features: Pink-yellow gradient with romantic theme

16. **congratulations.html** - Congratulations message
    - Placeholders: `[NAME]`, `[MESSAGE]`, `[SIGNATURE]`
    - Features: Gold-blue gradient with success theme

17. **thank-you.html** - Thank you message
    - Placeholders: `[NAME]`, `[MESSAGE]`, `[SIGNATURE]`
    - Features: Soft pastel gradient with gratitude theme

18. **new-year.html** - New Year wishes
    - Placeholders: `[NAME]`, `[MESSAGE]`, `[YEAR]`, `[SIGNATURE]`
    - Features: Purple gradient with celebration theme

### Using Templates Directly

```bash
# Read template, replace placeholders, and send
TEMPLATE=$(cat workspace/skills/gog-html-email/templates/basic.html)
HTML=$(echo "$TEMPLATE" | sed 's/\[NAME\]/John/g' | sed 's/\[MESSAGE\]/Your message here/g' | sed 's/\[SIGNATURE\]/Your Name/g')
gog gmail send --to recipient@example.com --subject "Subject" --body-html "$HTML"
```

### Quick Examples

**Basic email:**
```bash
TEMPLATE=$(cat workspace/skills/gog-html-email/templates/basic.html)
HTML=$(echo "$TEMPLATE" | sed 's/\[NAME\]/John/g' | sed 's/\[MESSAGE\]/Just wanted to check in on the project status./g' | sed 's/\[SIGNATURE\]/Sarah/g')
gog gmail send --to john@example.com --subject "Project Check-in" --body-html "$HTML"
```

**Meeting invitation:**
```bash
TEMPLATE=$(cat workspace/skills/gog-html-email/templates/meeting.html)
HTML=$(echo "$TEMPLATE" | sed 's/\[NAME\]/Team/g' | sed 's/\[TOPIC\]/Q1 Planning/g' | sed 's/\[DATE\]/March 15, 2026/g' | sed 's/\[TIME\]/2:00 PM/g' | sed 's/\[DURATION\]/1 hour/g' | sed 's/\[LOCATION\]/Conference Room A/g' | sed 's/\[SIGNATURE\]/Alex/g')
gog gmail send --to team@example.com --subject "Q1 Planning Meeting" --body-html "$HTML"
```

**Email with button:**
```bash
TEMPLATE=$(cat workspace/skills/gog-html-email/templates/button.html)
HTML=$(echo "$TEMPLATE" | sed 's/\[NAME\]/Sarah/g' | sed 's/\[MESSAGE\]/Please review the latest document./g' | sed 's|\[BUTTON_URL\]|https://docs.example.com/report|g' | sed 's/\[BUTTON_TEXT\]/View Document/g' | sed 's/\[SIGNATURE\]/Mike/g')
gog gmail send --to sarah@example.com --subject "Document Review" --body-html "$HTML"
```

**Jummah Mubarak:**
```bash
TEMPLATE=$(cat workspace/skills/gog-html-email/templates/jummah.html)
HTML=$(echo "$TEMPLATE" | sed 's/\[NAME\]/Ahmed/g' | sed 's/\[MESSAGE\]/Wishing you a blessed Friday filled with peace and blessings./g' | sed 's/\[SIGNATURE\]/Your Name/g')
gog gmail send --to ahmed@example.com --subject "Jummah Mubarak" --body-html "$HTML"
```

**Eid Mubarak:**
```bash
TEMPLATE=$(cat workspace/skills/gog-html-email/templates/eid.html)
HTML=$(echo "$TEMPLATE" | sed 's/\[NAME\]/Family/g' | sed 's/\[MESSAGE\]/May this Eid bring joy, happiness, and prosperity to you and your loved ones./g' | sed 's/\[SIGNATURE\]/Your Name/g')
gog gmail send --to family@example.com --subject "Eid Mubarak" --body-html "$HTML"
```

**Birthday wishes:**
```bash
TEMPLATE=$(cat workspace/skills/gog-html-email/templates/birthday.html)
HTML=$(echo "$TEMPLATE" | sed 's/\[NAME\]/Sarah/g' | sed 's/\[MESSAGE\]/Hope your special day is filled with joy, laughter, and wonderful memories!/g' | sed 's/\[SIGNATURE\]/Your Name/g')
gog gmail send --to sarah@example.com --subject "Happy Birthday!" --body-html "$HTML"
```

## Best Practices

1. **Use template files** - All templates are pre-formatted and tested
2. **Single-line HTML** - Templates are already single-line to avoid formatting issues
3. **Inline CSS** - All templates use inline styles for email client compatibility
4. **Max Width** - Templates are set to 600px for optimal viewing
5. **System Fonts** - Templates use `-apple-system, BlinkMacSystemFont, Segoe UI, Roboto` for best rendering
6. **Test First** - Send to yourself before sending to recipients
7. **Replace all placeholders** - Make sure to replace all `[PLACEHOLDER]` values with actual content

## Customizing Templates

You can customize template colors, fonts, and styling by adding additional `sed` commands to replace CSS values.

### Common Customizations

**Change gradient colors:**
```bash
TEMPLATE=$(cat workspace/skills/gog-html-email/templates/birthday.html)
# Replace pink gradient with blue gradient
HTML=$(echo "$TEMPLATE" | sed 's/#f093fb/#4facfe/g' | sed 's/#f5576c/#00f2fe/g')
# Then replace placeholders and send
HTML=$(echo "$HTML" | sed 's/\[NAME\]/John/g' | sed 's/\[MESSAGE\]/Your message/g' | sed 's/\[SIGNATURE\]/Your Name/g')
gog gmail send --to recipient@example.com --subject "Subject" --body-html "$HTML"
```

**Change primary color:**
```bash
TEMPLATE=$(cat workspace/skills/gog-html-email/templates/basic.html)
# Change all blue (#007bff) to purple (#667eea)
HTML=$(echo "$TEMPLATE" | sed 's/#007bff/#667eea/g')
HTML=$(echo "$HTML" | sed 's/\[NAME\]/John/g' | sed 's/\[MESSAGE\]/Your message/g' | sed 's/\[SIGNATURE\]/Your Name/g')
gog gmail send --to recipient@example.com --subject "Subject" --body-html "$HTML"
```

**Change background color:**
```bash
TEMPLATE=$(cat workspace/skills/gog-html-email/templates/highlight.html)
# Change highlight box from light gray to light blue
HTML=$(echo "$TEMPLATE" | sed 's/#f8f9fa/#e3f2fd/g')
HTML=$(echo "$HTML" | sed 's/\[NAME\]/John/g' | sed 's/\[MESSAGE\]/Your message/g' | sed 's/\[SIGNATURE\]/Your Name/g')
gog gmail send --to recipient@example.com --subject "Subject" --body-html "$HTML"
```

**Change font size:**
```bash
TEMPLATE=$(cat workspace/skills/gog-html-email/templates/basic.html)
# Make heading larger (36px to 48px)
HTML=$(echo "$TEMPLATE" | sed 's/font-size: 36px/font-size: 48px/g')
HTML=$(echo "$HTML" | sed 's/\[NAME\]/John/g' | sed 's/\[MESSAGE\]/Your message/g' | sed 's/\[SIGNATURE\]/Your Name/g')
gog gmail send --to recipient@example.com --subject "Subject" --body-html "$HTML"
```

**Change layout alignment (left-align instead of center):**
```bash
TEMPLATE=$(cat workspace/skills/gog-html-email/templates/basic.html)
# Remove centering: change "margin: 0 auto" to "margin: 0"
HTML=$(echo "$TEMPLATE" | sed 's/margin: 0 auto/margin: 0/g')
HTML=$(echo "$HTML" | sed 's/\[NAME\]/John/g' | sed 's/\[MESSAGE\]/Your message/g' | sed 's/\[SIGNATURE\]/Your Name/g')
gog gmail send --to recipient@example.com --subject "Subject" --body-html "$HTML"
```

### Color Palette Reference

**Current template colors:**

**Birthday (Pink):**
- Gradient: `#f093fb` → `#f5576c`
- Heading: `#f5576c`

**Eid (Green):**
- Gradient: `#11998e` → `#38ef7d`
- Heading: `#11998e`

**Jummah (Blue):**
- Gradient: `#4facfe` → `#00f2fe`
- Heading: `#4facfe`

**Ramadan (Purple):**
- Gradient: `#667eea` → `#764ba2`
- Heading: `#667eea`

**Anniversary (Pink-Yellow):**
- Gradient: `#fa709a` → `#fee140`
- Heading: `#fa709a`

**Congratulations (Gold-Blue):**
- Gradient: `#ffd89b` → `#19547b`
- Heading: `#19547b`

**Thank You (Pastel):**
- Gradient: `#a8edea` → `#fed6e3`

**New Year (Purple):**
- Gradient: `#667eea` → `#764ba2`
- Heading: `#667eea`

**Suggested alternative palettes:**
- Ocean: `#2E3192` → `#1BFFFF`
- Sunset: `#FF512F` → `#F09819`
- Forest: `#134E5E` → `#71B280`
- Royal: `#8E2DE2` → `#4A00E0`
- Warm: `#FF6B6B` → `#FFE66D`
- Cool: `#4ECDC4` → `#556270`

### Advanced Customization

**Multiple color changes:**
```bash
TEMPLATE=$(cat workspace/skills/gog-html-email/templates/birthday.html)
# Change to ocean theme
HTML=$(echo "$TEMPLATE" | \
  sed 's/#f093fb/#2E3192/g' | \
  sed 's/#f5576c/#1BFFFF/g' | \
  sed 's/\[NAME\]/John/g' | \
  sed 's/\[MESSAGE\]/Your message/g' | \
  sed 's/\[SIGNATURE\]/Your Name/g')
gog gmail send --to recipient@example.com --subject "Subject" --body-html "$HTML"
```

**Create custom template variant:**
```bash
# Save customized version as new template
TEMPLATE=$(cat workspace/skills/gog-html-email/templates/birthday.html)
echo "$TEMPLATE" | sed 's/#f093fb/#2E3192/g' | sed 's/#f5576c/#1BFFFF/g' > workspace/skills/gog-html-email/templates/birthday-ocean.html
# Now use the custom template
TEMPLATE=$(cat workspace/skills/gog-html-email/templates/birthday-ocean.html)
HTML=$(echo "$TEMPLATE" | sed 's/\[NAME\]/John/g' | sed 's/\[MESSAGE\]/Your message/g' | sed 's/\[SIGNATURE\]/Your Name/g')
gog gmail send --to recipient@example.com --subject "Subject" --body-html "$HTML"
```

## Notes

- Templates are single-line HTML to prevent formatting issues
- For complex layouts (tables, multiple sections), create a custom template file
- Always test HTML emails in multiple clients (Gmail, Outlook, Apple Mail)
- Use plain text (`--body`) for simple messages without formatting needs
