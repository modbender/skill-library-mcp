# OpenClaw Email Skill

## Description
Send emails (with optional file attachments) from OpenClaw using SMTP. This skill uses a Gmail account with an App Password.

## Usage
- **When to use**: User asks to email a report, log, or any file.
- **Parameters**:
  - `to` (string, required): Recipient email address.
  - `subject` (string, required): Email subject.
  - `body` (string, required): Plain‑text body.
  - `attachment_path` (string, optional): Absolute path to a file to attach.

## Tools
The skill provides a function `send_email` that can be called via the OpenClaw function tool.
