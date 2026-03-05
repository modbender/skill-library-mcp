"""
Module for syncing posts with Notion.

This module provides functionality to:
- Create pages in a Notion database
- Update status of pages
- Fetch pending posts for review
"""

import logging
import os
from datetime import datetime
from typing import Optional, List

try:
    from notion_client import Client as NotionClient
except ImportError:  # pragma: no cover - handled during initialization
    NotionClient = None

from .content_generator import GeneratedPost

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NotionSync:
    """
    Sync SociClaw posts with Notion.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        database_id: Optional[str] = None,
        client: Optional[NotionClient] = None,
    ) -> None:
        """
        Initialize NotionSync.

        Args:
            api_key: Notion API key
            database_id: Notion database ID
            client: Optional NotionClient instance for testing/mocking
        """
        self.api_key = api_key or os.getenv("NOTION_API_KEY")
        self.database_id = database_id or os.getenv("NOTION_DATABASE_ID")

        if not client and (not self.api_key or not self.database_id):
            raise ValueError("NOTION_API_KEY and NOTION_DATABASE_ID must be provided")

        if client is not None:
            self.client = client
        else:
            if NotionClient is None:
                raise ImportError("notion-client is required for Notion sync")
            self.client = NotionClient(auth=self.api_key)

    def create_page(self, post: GeneratedPost, status: str = "Draft", image_url: Optional[str] = None):
        """
        Create a Notion page for a generated post.

        Args:
            post: GeneratedPost instance
            status: Initial status (Draft/Review/Scheduled/Published)
            image_url: Optional image URL to attach

        Returns:
            Created page object
        """
        content_text = post.details or post.text
        properties = {
            "Title": {
                "title": [{"text": {"content": self._summarize_title(post.text)}}]
            },
            "Content": {
                "rich_text": [{"text": {"content": content_text[:1900]}}]
            },
            "Date": {
                "date": {"start": self._format_datetime(post)}
            },
            "Status": {
                "select": {"name": status}
            },
            "Category": {
                "multi_select": [{"name": post.category}]
            },
            "Engagement": {
                "number": 0
            },
        }

        if image_url:
            properties["Image"] = {
                "files": [
                    {"name": "image", "type": "external", "external": {"url": image_url}}
                ]
            }

        page = self.client.pages.create(parent={"database_id": self.database_id}, properties=properties)
        logger.info("Created Notion page")
        return page

    def update_status(self, page_id: str, status: str):
        """
        Update the status of a Notion page.
        """
        return self.client.pages.update(
            page_id=page_id,
            properties={"Status": {"select": {"name": status}}}
        )

    def get_pending_posts(self) -> List[dict]:
        """
        Fetch posts in Draft or Review status.
        """
        result = self.client.databases.query(
            database_id=self.database_id,
            filter={
                "or": [
                    {"property": "Status", "select": {"equals": "Draft"}},
                    {"property": "Status", "select": {"equals": "Review"}},
                ]
            },
        )
        return result.get("results", [])

    def _summarize_title(self, text: str) -> str:
        """
        Build a short title for the page.
        """
        if not text or not text.strip():
            return "Untitled Post"
        first_line = text.strip().splitlines()[0]
        return (first_line[:80] + "...") if len(first_line) > 80 else first_line

    def _format_datetime(self, post: GeneratedPost) -> Optional[str]:
        """
        Format a datetime string for Notion.
        """
        if not post.date or post.time is None:
            return None
        try:
            date_obj = datetime.fromisoformat(post.date)
            date_obj = date_obj.replace(hour=int(post.time), minute=0, second=0, microsecond=0)
            return date_obj.isoformat()
        except Exception:
            return None
