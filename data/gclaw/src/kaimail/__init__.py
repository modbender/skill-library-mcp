"""KaiMail - Email infrastructure library for Kai AI assistant."""

from kaimail.bot_context import BotContext
from kaimail.classifier import EmailCategory, EmailClassifier
from kaimail.client import GogGmailClient
from kaimail.fetcher import EmailFetcher
from kaimail.models import Email, EmailBatch, ParsedEmail, Thread
from kaimail.parser import EmailParser
from kaimail.store import EmailStore

__all__ = [
    "BotContext",
    "Email",
    "EmailBatch",
    "EmailCategory",
    "EmailClassifier",
    "EmailFetcher",
    "EmailParser",
    "EmailStore",
    "GogGmailClient",
    "ParsedEmail",
    "Thread",
]

__version__ = "0.1.0"
