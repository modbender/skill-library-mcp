"""
_retry.py - Exponential backoff for transient network errors.
Shared retry logic for OpenClaw skills. Stdlib only.

Usage:
    from _retry import with_retry
    data = with_retry(lambda: imap.login(user, key))
"""

import imaplib
import smtplib
import time

# Default settings
MAX_RETRIES = 3
BASE_DELAY  = 1.0      # seconds
BACKOFF     = 2.0      # multiplier


def with_retry(fn, max_retries: int = MAX_RETRIES, base_delay: float = BASE_DELAY,
               backoff: float = BACKOFF):
    """
    Call fn() up to max_retries+1 times with exponential backoff.
    Retries on:
      - OSError / ConnectionError (socket-level: refused, timeout, DNS)
      - imaplib.IMAP4.abort (connection dropped)
      - smtplib.SMTPServerDisconnected (connection dropped)
    All other exceptions (auth errors, protocol errors) propagate immediately.
    """
    delay = base_delay
    last_exc = None
    for attempt in range(max_retries + 1):
        try:
            return fn()
        except (OSError, ConnectionError,
                imaplib.IMAP4.abort,
                smtplib.SMTPServerDisconnected) as exc:
            last_exc = exc
        # Don't sleep after last attempt
        if attempt < max_retries:
            time.sleep(delay)
            delay *= backoff
    raise last_exc
