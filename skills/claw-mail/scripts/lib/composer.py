"""Rich email composer with built-in templates."""

from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path
from string import Template
from typing import Any

from .models import EmailAddress, EmailMessage

DEFAULT_TEMPLATE = """\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>${subject}</title>
</head>
<body style="margin:0; padding:0; background-color:#f4f4f7; font-family:-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:#f4f4f7;">
<tr>
<td align="center" style="padding:24px 0;">

${header_block}

<table role="presentation" width="600" cellpadding="0" cellspacing="0" style="max-width:600px; width:100%;">
<tr>
<td style="background-color:#ffffff; padding:32px; border-radius:0 0 8px 8px;">

  ${greeting_block}

  <div style="color:#4a5568; font-size:15px; line-height:1.6;">
    ${body}
  </div>

  ${action_block}

  ${sign_off_block}

</td>
</tr>
</table>

${footer_block}

</td>
</tr>
</table>
</body>
</html>
"""

MINIMAL_TEMPLATE = """\
<!DOCTYPE html>
<html lang="en">
<head><meta charset="utf-8"><title>${subject}</title></head>
<body style="margin:0; padding:20px; font-family:-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color:#2d3748; font-size:15px; line-height:1.6;">
${body}
${sign_off_block}
</body>
</html>
"""

DIGEST_TEMPLATE = """\
<!DOCTYPE html>
<html lang="en">
<head><meta charset="utf-8"><title>${subject}</title></head>
<body style="margin:0; padding:0; background-color:#f4f4f7; font-family:-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:#f4f4f7;">
<tr><td align="center" style="padding:24px 0;">

${header_block}

<table role="presentation" width="600" cellpadding="0" cellspacing="0" style="max-width:600px; width:100%;">
<tr>
<td style="background-color:#ffffff; padding:24px 32px;">

  ${summary_block}
  ${table_block}

</td>
</tr>
</table>

${footer_block}

</td></tr>
</table>
</body>
</html>
"""

BUILTIN_TEMPLATES = {
    "default": DEFAULT_TEMPLATE,
    "minimal": MINIMAL_TEMPLATE,
    "digest": DIGEST_TEMPLATE,
}


def _build_header_block(
    header_text: str = "", header_color: str = "#2d3748", subject: str = "",
) -> str:
    text = header_text or subject
    if not text:
        return ""
    return (
        f'<table role="presentation" width="600" cellpadding="0" cellspacing="0" '
        f'style="max-width:600px; width:100%;">\n<tr>\n'
        f'<td style="background-color:{header_color}; padding:20px 32px; '
        f'border-radius:8px 8px 0 0;">\n'
        f'  <h1 style="margin:0; color:#ffffff; font-size:20px; font-weight:600;">'
        f'{text}</h1>\n</td>\n</tr>\n</table>'
    )


def _build_footer_block(footer_text: str = "") -> str:
    if not footer_text:
        return ""
    return (
        f'<table role="presentation" width="600" cellpadding="0" cellspacing="0" '
        f'style="max-width:600px; width:100%;">\n<tr>\n'
        f'<td style="background-color:#edf2f7; padding:16px 32px; '
        f'border-radius:0 0 8px 8px;">\n'
        f'  <p style="margin:0; color:#a0aec0; font-size:12px; text-align:center;">'
        f'{footer_text}</p>\n</td>\n</tr>\n</table>'
    )


def _build_action_block(
    action_url: str = "", action_text: str = "View Details",
    action_color: str = "#4299e1",
) -> str:
    if not action_url:
        return ""
    return (
        f'<table role="presentation" cellpadding="0" cellspacing="0" '
        f'style="margin:24px 0;">\n<tr>\n'
        f'<td style="background-color:{action_color}; border-radius:6px;">\n'
        f'  <a href="{action_url}" style="display:inline-block; padding:12px 24px; '
        f'color:#ffffff; text-decoration:none; font-size:15px; font-weight:600;">'
        f'{action_text}</a>\n</td>\n</tr>\n</table>'
    )


def _build_table_block(
    items: list[dict[str, str]], columns: list[str],
) -> str:
    if not items or not columns:
        return ""
    header_cells = "".join(
        f'<th style="text-align:left; padding:8px 12px; background-color:#edf2f7; '
        f'color:#4a5568; font-size:12px; font-weight:600; text-transform:uppercase; '
        f'border-bottom:2px solid #e2e8f0;">{col}</th>'
        for col in columns
    )
    rows = ""
    for item in items:
        cells = "".join(
            f'<td style="padding:10px 12px; border-bottom:1px solid #e2e8f0; '
            f'color:#2d3748; font-size:14px;">{item.get(col, "")}</td>'
            for col in columns
        )
        rows += f"<tr>{cells}</tr>\n"
    return (
        f'<table width="100%" cellpadding="0" cellspacing="0" '
        f'style="border-collapse:collapse;">\n'
        f'<thead><tr>{header_cells}</tr></thead>\n'
        f'<tbody>\n{rows}</tbody>\n</table>'
    )


class EmailComposer:
    """Compose rich HTML emails using built-in or custom templates."""

    def __init__(self, template_dir: str | None = None) -> None:
        self.template_dir = Path(template_dir) if template_dir else None

    def compose(
        self,
        to: str | list[str],
        subject: str,
        body: str,
        template: str = "default",
        sender: str | EmailAddress | None = None,
        cc: str | list[str] | None = None,
        bcc: str | list[str] | None = None,
        reply_to: str = "",
        greeting: str = "",
        sign_off: str = "",
        header_text: str = "",
        header_color: str = "#2d3748",
        footer_text: str = "",
        action_url: str = "",
        action_text: str = "View Details",
        action_color: str = "#4299e1",
        items: list[dict[str, str]] | None = None,
        columns: list[str] | None = None,
        summary: str = "",
        **extra: Any,
    ) -> EmailMessage:
        recipients = _normalize(to)
        cc_list = _normalize(cc) if cc else []
        bcc_list = _normalize(bcc) if bcc else []

        sender_addr = None
        if sender:
            sender_addr = (
                sender if isinstance(sender, EmailAddress)
                else EmailAddress.parse(sender)
            )

        # Build template blocks
        header_block = _build_header_block(header_text, header_color, subject)
        footer_block = _build_footer_block(footer_text)
        action_block = _build_action_block(action_url, action_text, action_color)
        greeting_block = (
            f'<p style="margin:0 0 16px; color:#2d3748; font-size:16px;">{greeting}</p>'
            if greeting else ""
        )
        sign_off_block = (
            f'<p style="margin:24px 0 0; color:#4a5568; font-size:15px;">{sign_off}</p>'
            if sign_off else ""
        )
        summary_block = (
            f'<p style="margin:0 0 20px; color:#4a5568; font-size:15px;">{summary}</p>'
            if summary else ""
        )
        table_block = _build_table_block(items or [], columns or [])

        # Render template
        tmpl_str = self._get_template(template)
        html_body = Template(tmpl_str).safe_substitute(
            subject=subject,
            body=body,
            header_block=header_block,
            footer_block=footer_block,
            action_block=action_block,
            greeting_block=greeting_block,
            sign_off_block=sign_off_block,
            summary_block=summary_block,
            table_block=table_block,
        )

        plain_text = _html_to_plain(html_body)

        return EmailMessage(
            subject=subject, sender=sender_addr,
            recipients=recipients, cc=cc_list, bcc=bcc_list,
            body_html=html_body, body_plain=plain_text,
            in_reply_to=reply_to,
            date=datetime.now(),
        )

    def compose_digest(
        self,
        to: str | list[str],
        subject: str,
        items: list[dict[str, str]],
        columns: list[str],
        sender: str | EmailAddress | None = None,
        **kwargs: Any,
    ) -> EmailMessage:
        return self.compose(
            to=to, subject=subject, body="",
            template="digest", sender=sender,
            items=items, columns=columns, **kwargs,
        )

    def compose_reply(
        self,
        original: EmailMessage,
        body: str,
        sender: str | EmailAddress | None = None,
        template: str = "minimal",
        quote_original: bool = True,
        **kwargs: Any,
    ) -> EmailMessage:
        subj = original.subject
        if not subj.startswith("Re:"):
            subj = f"Re: {subj}"

        full_body = body
        if quote_original:
            quoted = _build_quote_block(original)
            full_body = f"{body}\n\n{quoted}"

        reply = self.compose(
            to=[str(original.sender)] if original.sender else [],
            subject=subj,
            body=full_body,
            template=template,
            sender=sender,
            reply_to=original.message_id,
            **kwargs,
        )
        reply.in_reply_to = original.message_id
        reply.references = original.references + [original.message_id]
        return reply

    def compose_forward(
        self,
        original: EmailMessage,
        to: str | list[str],
        body: str = "",
        sender: str | EmailAddress | None = None,
        template: str = "minimal",
        attach_original: bool = False,
        **kwargs: Any,
    ) -> EmailMessage:
        """Compose a forwarded message with the original inline-quoted.

        If *attach_original* is True, the original message's attachments
        are carried over to the forward.
        """
        subj = original.subject
        if not subj.startswith("Fwd:"):
            subj = f"Fwd: {subj}"

        fwd_block = _build_forward_block(original)
        full_body = f"{body}\n\n{fwd_block}" if body else fwd_block

        fwd = self.compose(
            to=to,
            subject=subj,
            body=full_body,
            template=template,
            sender=sender,
            **kwargs,
        )

        if attach_original and original.attachments:
            fwd.attachments = list(original.attachments)

        return fwd

    def _get_template(self, name: str) -> str:
        if name in BUILTIN_TEMPLATES:
            return BUILTIN_TEMPLATES[name]
        if self.template_dir:
            path = self.template_dir / name
            if path.is_file():
                return path.read_text()
        return BUILTIN_TEMPLATES["default"]


def _build_quote_block(original: EmailMessage) -> str:
    """Build a '> On date, sender wrote:' quoted block from the original."""
    sender = str(original.sender) if original.sender else "someone"
    date_str = (
        original.date.strftime("%a, %b %d, %Y at %I:%M %p")
        if original.date else "an unknown date"
    )
    orig_text = original.body_plain or _html_to_plain(original.body_html or "")
    quoted_lines = "\n".join(f"> {line}" for line in orig_text.splitlines())

    plain_block = f"On {date_str}, {sender} wrote:\n{quoted_lines}"

    html_quoted = orig_text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    html_quoted = "<br>".join(html_quoted.splitlines())
    html_block = (
        f'<div style="margin-top:16px; padding-left:12px; '
        f'border-left:3px solid #ccc; color:#555;">'
        f'<p style="margin:0 0 8px;">On {date_str}, {sender} wrote:</p>'
        f'<div style="white-space:pre-wrap;">{html_quoted}</div>'
        f'</div>'
    )

    return html_block


def _build_forward_block(original: EmailMessage) -> str:
    """Build a '---------- Forwarded message ----------' block."""
    sender = str(original.sender) if original.sender else "(unknown)"
    date_str = (
        original.date.strftime("%a, %b %d, %Y at %I:%M %p")
        if original.date else ""
    )
    to_str = ", ".join(str(r) for r in original.recipients) if original.recipients else ""

    orig_body = original.body_html or original.body_plain or ""

    header_lines = [
        "---------- Forwarded message ----------",
        f"From: {sender}",
    ]
    if date_str:
        header_lines.append(f"Date: {date_str}")
    header_lines.append(f"Subject: {original.subject}")
    if to_str:
        header_lines.append(f"To: {to_str}")

    header_html = "<br>".join(header_lines)
    return (
        f'<div style="margin-top:16px;">'
        f'<div style="color:#777; font-size:13px;">{header_html}</div>'
        f'<br>'
        f'<div>{orig_body}</div>'
        f'</div>'
    )


def _normalize(addrs: str | list[str] | None) -> list[EmailAddress]:
    if not addrs:
        return []
    if isinstance(addrs, str):
        addrs = [addrs]
    return [EmailAddress.parse(a) for a in addrs]


def _html_to_plain(html: str) -> str:
    # Strip <head> (contains <title> which duplicates the subject) and
    # <style>/<script> blocks before removing tags.
    text = re.sub(r"<head[\s>].*?</head>", "", html, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<style[\s>].*?</style>", "", text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<script[\s>].*?</script>", "", text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\n\s*\n", "\n\n", text)
    return text.strip()
