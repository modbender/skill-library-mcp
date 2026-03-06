"""Email service for sending magic links and other transactional emails via Resend."""
import logging
from datetime import datetime

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending emails via Resend HTTP API."""

    RESEND_API_URL = "https://api.resend.com/emails"

    def is_configured(self) -> bool:
        """Check if Resend API key is configured."""
        return bool(settings.resend_api_key)

    async def send_magic_link(
        self,
        to_email: str,
        token: str,
        frontend_url: str,
    ) -> None:
        """
        Send a magic link email for authentication.
        Does not raise on failure; logs errors instead.
        """
        if not self.is_configured():
            logger.warning("Resend API key not configured; skipping magic link email")
            return

        magic_link_url = f"{frontend_url.rstrip('/')}/auth/verify?token={token}"
        expires = settings.magic_link_expire_minutes

        plain_text = (
            "Sign in to MoltFundMe\n"
            "=====================\n\n"
            "Click the link below to sign in:\n\n"
            f"{magic_link_url}\n\n"
            f"This link expires in {expires} minutes.\n"
            "If you didn't request this, you can safely ignore this email.\n\n"
            "---\n"
            "MoltFundMe — Where AI agents help humans help humans\n"
        )

        html_text = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Sign in to MoltFundMe</title>
</head>
<body style="margin:0;padding:0;background-color:#f3f4f6;font-family:'Inter',system-ui,-apple-system,'Segoe UI',Roboto,sans-serif;">
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:#f3f4f6;padding:40px 0;">
    <tr>
      <td align="center">
        <table role="presentation" width="480" cellpadding="0" cellspacing="0" style="max-width:480px;width:100%;background-color:#ffffff;border-radius:12px;box-shadow:0 1px 3px rgba(0,0,0,0.1);overflow:hidden;">
          <!-- Header -->
          <tr>
            <td style="background-color:#ffffff;padding:32px 40px;text-align:center;border-bottom:1px solid #e5e7eb;">
              <span style="font-size:28px;font-weight:700;letter-spacing:-0.5px;">
                <span style="color:#ff6b35;">Molt</span><span style="color:#00b964;">Fund</span><span style="color:#111827;">Me</span>
              </span>
            </td>
          </tr>
          <!-- Body -->
          <tr>
            <td style="padding:40px;">
              <h1 style="margin:0 0 8px;font-size:22px;font-weight:700;color:#111827;">Sign in to your account</h1>
              <p style="margin:0 0 28px;font-size:15px;color:#6b7280;line-height:1.6;">
                Click the button below to securely sign in. No password needed.
              </p>
              <!-- CTA Button -->
              <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
                <tr>
                  <td align="center" style="padding:0 0 28px;">
                    <a href="{magic_link_url}" target="_blank" style="display:inline-block;background-color:#00b964;color:#ffffff;font-size:16px;font-weight:600;text-decoration:none;padding:14px 36px;border-radius:8px;letter-spacing:0.2px;">
                      Sign In to MoltFundMe
                    </a>
                  </td>
                </tr>
              </table>
              <!-- Divider -->
              <hr style="border:none;border-top:1px solid #e5e7eb;margin:0 0 20px;">
              <p style="margin:0 0 12px;font-size:13px;color:#9ca3af;line-height:1.5;">
                Or copy and paste this link into your browser:
              </p>
              <p style="margin:0 0 20px;font-size:13px;word-break:break-all;">
                <a href="{magic_link_url}" style="color:#00b964;text-decoration:underline;">{magic_link_url}</a>
              </p>
              <p style="margin:0;font-size:13px;color:#9ca3af;line-height:1.5;">
                This link expires in <strong style="color:#6b7280;">{expires} minutes</strong>.
                If you didn&rsquo;t request this, you can safely ignore this email.
              </p>
            </td>
          </tr>
          <!-- Footer -->
          <tr>
            <td style="background-color:#f9fafb;padding:24px 40px;border-top:1px solid #e5e7eb;text-align:center;">
              <p style="margin:0 0 4px;font-size:12px;color:#9ca3af;">
                Where AI agents help humans help humans
              </p>
              <p style="margin:0;font-size:12px;color:#d1d5db;">
                &copy; {datetime.now().year} MoltFundMe &middot; Direct wallet-to-wallet crypto donations
              </p>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>"""

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.RESEND_API_URL,
                    headers={
                        "Authorization": f"Bearer {settings.resend_api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "from": f"MoltFundMe <{settings.from_email}>",
                        "to": [to_email],
                        "subject": "Sign in to MoltFundMe \U0001f512",
                        "html": html_text,
                        "text": plain_text,
                    },
                )
                if response.status_code not in (200, 201):
                    logger.error(
                        f"Resend API error ({response.status_code}): {response.text}"
                    )
                else:
                    logger.info(f"Magic link email sent to {to_email}")
        except Exception as e:
            logger.error(
                f"Failed to send magic link email to {to_email}: {e}",
                exc_info=True,
            )

    async def send_campaign_milestone(
        self,
        to_email: str,
        campaign_title: str,
        milestone_percent: int,
    ) -> None:
        """Send email when campaign reaches funding milestone (25/50/75/100%)."""
        if not self.is_configured():
            logger.warning("Resend API key not configured; skipping milestone email")
            return
        subject = f"Your campaign reached {milestone_percent}% of its goal!"
        text = f"Congratulations! {campaign_title} has reached {milestone_percent}% of its funding goal."
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.RESEND_API_URL,
                    headers={
                        "Authorization": f"Bearer {settings.resend_api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "from": f"MoltFundMe <{settings.from_email}>",
                        "to": [to_email],
                        "subject": subject,
                        "text": text,
                        "html": f"<p>{text}</p>",
                    },
                )
                if response.status_code not in (200, 201):
                    logger.error(f"Resend API error ({response.status_code}): {response.text}")
                else:
                    logger.info(f"Milestone email sent to {to_email}")
        except Exception as e:
            logger.error(f"Failed to send milestone email: {e}", exc_info=True)

    async def send_new_advocate_notification(
        self,
        to_email: str,
        campaign_title: str,
        agent_name: str,
    ) -> None:
        """Send email when a new agent advocates for a campaign."""
        if not self.is_configured():
            logger.warning("Resend API key not configured; skipping advocate notification")
            return
        subject = f"A new advocate supports {campaign_title}"
        text = f"{agent_name} is now advocating for your campaign: {campaign_title}."
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.RESEND_API_URL,
                    headers={
                        "Authorization": f"Bearer {settings.resend_api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "from": f"MoltFundMe <{settings.from_email}>",
                        "to": [to_email],
                        "subject": subject,
                        "text": text,
                        "html": f"<p>{text}</p>",
                    },
                )
                if response.status_code not in (200, 201):
                    logger.error(f"Resend API error ({response.status_code}): {response.text}")
                else:
                    logger.info(f"Advocate notification sent to {to_email}")
        except Exception as e:
            logger.error(f"Failed to send advocate notification: {e}", exc_info=True)


email_service = EmailService()
