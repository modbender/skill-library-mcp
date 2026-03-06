#!/usr/bin/env python3
"""
邮件收发模块：IMAP 读取 + SMTP 发送

凭证来源：config/.env（EMAIL_SENDER / EMAIL_APP_PASSWORD / EMAIL_RECIPIENTS）
行为开关：config/settings.yaml → email.enabled（false 时所有邮件功能跳过）
"""

import smtplib
import imaplib
import email
import email.utils
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import decode_header
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

logger = logging.getLogger("heartbeat.mail")

# 未配置时的占位返回值
_MAIL_DISABLED = {
    "unread_count": 0, "flagged_count": 0, "flagged_from": [],
    "high_priority": [], "last_check": "--:--", "error": None, "disabled": True
}


def _load_config() -> dict:
    import yaml
    p = Path(__file__).parent.parent / "config" / "settings.yaml"
    with open(p, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def _is_email_enabled() -> bool:
    """检查 settings.yaml 中 email.enabled 开关"""
    try:
        return _load_config().get("email", {}).get("enabled", True)
    except Exception:
        return False


def _load_credentials() -> tuple[str, str, list[str]]:
    """
    从 config/.env 读取邮件凭证。

    返回: (sender, app_password, recipients_list)
    若 .env 不存在或未配置，抛出 RuntimeError 并给出引导说明。
    """
    from dotenv import dotenv_values
    env_path = Path(__file__).parent.parent / "config" / ".env"

    if not env_path.exists():
        raise RuntimeError(
            "邮件功能未配置。\n"
            "请按以下步骤配置：\n"
            "  1. cp config/.env.example config/.env\n"
            "  2. 编辑 config/.env，填入 EMAIL_SENDER / EMAIL_APP_PASSWORD / EMAIL_RECIPIENTS\n"
            "  3. 获取 Gmail App Password：https://myaccount.google.com/apppasswords"
        )

    values = dotenv_values(env_path)
    sender   = values.get("EMAIL_SENDER", "").strip()
    password = values.get("EMAIL_APP_PASSWORD", "").strip()
    raw_rcpt = values.get("EMAIL_RECIPIENTS", "").strip()

    missing = []
    if not sender:   missing.append("EMAIL_SENDER")
    if not password or password == "xxxx xxxx xxxx xxxx": missing.append("EMAIL_APP_PASSWORD")
    if not raw_rcpt: missing.append("EMAIL_RECIPIENTS")

    if missing:
        raise RuntimeError(
            f"config/.env 中以下字段未填写：{', '.join(missing)}\n"
            "请参考 config/.env.example 完成配置。"
        )

    recipients = [r.strip() for r in raw_rcpt.split(",") if r.strip()]
    return sender, password, recipients


def _decode_str(value: str) -> str:
    if not value:
        return ""
    parts = decode_header(value)
    result = []
    for part, charset in parts:
        if isinstance(part, bytes):
            result.append(part.decode(charset or "utf-8", errors="replace"))
        else:
            result.append(part)
    return "".join(result)


# ──────────────────────────────────────────────────────────────────────────────
# 公开接口
# ──────────────────────────────────────────────────────────────────────────────

def check_mail(since_hours: int = 1) -> dict:
    """
    检查邮箱未读/标记/高优先级邮件。

    若邮件功能未启用或未配置，静默返回空结果（不报错）。
    """
    if not _is_email_enabled():
        logger.debug("邮件功能已禁用（settings.yaml email.enabled=false）")
        return {**_MAIL_DISABLED, "disabled": True}

    result = {
        "unread_count": 0, "flagged_count": 0, "flagged_from": [],
        "high_priority": [], "last_check": datetime.now().strftime("%H:%M"),
        "error": None, "disabled": False
    }

    try:
        sender, password, _ = _load_credentials()
    except RuntimeError as e:
        result["error"] = str(e)
        logger.warning("邮件未配置，跳过邮件检查。\n%s", e)
        return result

    config = _load_config()
    email_cfg = config.get("email", {})
    conn = None

    try:
        conn = imaplib.IMAP4_SSL(
            email_cfg.get("imap_host", "imap.gmail.com"),
            email_cfg.get("imap_port", 993),
            timeout=30,
        )
        conn.login(sender, password)
        conn.select("INBOX", readonly=True)

        # 未读数量
        _, data = conn.search(None, "UNSEEN")
        if data[0]:
            result["unread_count"] = len(data[0].split())

        # 标记邮件
        since_date = (datetime.now() - timedelta(hours=since_hours)).strftime("%d-%b-%Y")
        _, data = conn.search(None, f"FLAGGED SINCE {since_date}")
        if data[0]:
            flagged_ids = data[0].split()
            result["flagged_count"] = len(flagged_ids)
            for mid in flagged_ids[-5:]:
                _, msg_data = conn.fetch(mid, "(RFC822.HEADER)")
                if msg_data and msg_data[0]:
                    msg = email.message_from_bytes(msg_data[0][1])
                    result["flagged_from"].append(_decode_str(msg.get("From", "")))

        # 高优先级发件人
        hp_senders = email_cfg.get("high_priority_senders", [])
        for keyword in hp_senders:
            _, data = conn.search(None, f'FROM "{keyword}" SINCE {since_date}')
            if data[0]:
                for mid in data[0].split()[-3:]:
                    _, msg_data = conn.fetch(mid, "(RFC822.HEADER)")
                    if msg_data and msg_data[0]:
                        msg = email.message_from_bytes(msg_data[0][1])
                        result["high_priority"].append({
                            "from":    _decode_str(msg.get("From", "")),
                            "subject": _decode_str(msg.get("Subject", "")),
                            "date":    msg.get("Date", ""),
                        })

        logger.info("邮件检查完成: 未读=%d, 标记=%d", result["unread_count"], result["flagged_count"])

    except (imaplib.IMAP4.error, OSError, TimeoutError) as e:
        result["error"] = f"IMAP 连接失败: {e}"
        logger.error("邮件检查异常: %s", e)
    except Exception as e:
        result["error"] = f"邮件检查未知错误: {e}"
        logger.error("邮件检查未知异常: %s", e)
    finally:
        if conn:
            try: conn.logout()
            except Exception: pass

    return result


def send_mail(
    subject: str,
    body: str,
    recipients: Optional[list] = None,
    html: bool = False,
) -> bool:
    """
    发送邮件。

    若邮件功能未启用或未配置，静默返回 False（不报错、不阻断心跳）。
    """
    if not _is_email_enabled():
        logger.debug("邮件功能已禁用，跳过发送：%s", subject)
        return False

    try:
        sender, password, default_recipients = _load_credentials()
    except RuntimeError as e:
        logger.warning("邮件未配置，跳过发送「%s」。\n%s", subject, e)
        return False

    to_list = recipients if recipients is not None else default_recipients
    config  = _load_config()
    email_cfg = config.get("email", {})

    try:
        msg = MIMEMultipart("alternative")
        msg["From"]    = sender
        msg["To"]      = ", ".join(to_list)
        msg["Subject"] = subject
        msg["Date"]    = email.utils.formatdate(localtime=True)
        msg.attach(MIMEText(body, "html" if html else "plain", "utf-8"))

        with smtplib.SMTP(
            email_cfg.get("smtp_host", "smtp.gmail.com"),
            email_cfg.get("smtp_port", 587),
            timeout=30,
        ) as server:
            server.starttls()
            server.login(sender, password)
            server.send_message(msg)

        logger.info("邮件发送成功: %s -> %s", subject, to_list)
        return True

    except (smtplib.SMTPException, OSError, TimeoutError) as e:
        logger.error("邮件发送失败: %s", e)
        return False
    except Exception as e:
        logger.error("邮件发送未知错误: %s", e)
        return False


def send_alert(title: str, details: str) -> bool:
    """发送告警邮件"""
    body = (
        f"⚠️ 心跳告警\n{'='*40}\n"
        f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"告警: {title}\n{'='*40}\n\n{details}\n"
    )
    return send_mail(f"[ALERT] EVA Heartbeat: {title}", body)
