# whoami Profile Format Spec

## Format

Uses Markdown format, readable by both humans and AI.

## Recommended Structure

```markdown
# My Profile

## Basic Info
- Name: [name]
- Occupation: [description]
- Location: [city/region]

## Skills & Expertise
- [skill 1]
- [skill 2]

## Work Preferences
- [preference 1]
- [preference 2]

## Current Projects
- [project 1]: [brief description]

## AI Preferences
- [communication style]
- [code style]
- [language preference]
```

## Notes

- Not all fields are required; users can fill in only the parts they consider important
- Content should be concise, max 5000 characters (~2000 Chinese characters or ~2000 English words)
- AI should auto-organize content into a reasonable Markdown structure when saving
- The update command is an overwrite operation; always pass complete content
- Remote automatically retains the last 3 historical versions; mistakes can be rolled back via API

## API Authentication

All API requests require an API Key in the header:
```
Authorization: Bearer wai_xxxxxxxxxxxxxxxx
```

API Key is read from the `~/.whoamiagent` config file:
```
WHOAMI_API_KEY=wai_xxxxxxxxxxxxxxxx
```
