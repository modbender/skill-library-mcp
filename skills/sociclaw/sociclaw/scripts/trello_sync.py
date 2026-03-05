"""
Module for syncing posts with Trello.

This module provides functionality to:
- Create and configure the SociClaw Trello board
- Create cards for generated posts
- Update card status
- Attach images to cards
"""

import hashlib
import logging
import os
import re
import time
from datetime import datetime, timedelta
from typing import List, Optional

try:
    from trello import TrelloClient
except ImportError:  # pragma: no cover - handled during initialization
    TrelloClient = None

from .content_generator import GeneratedPost

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TrelloSync:
    """
    Sync SociClaw posts with Trello.
    """

    BOARD_NAME = "SociClaw Content Calendar"
    BASE_WORKFLOW_LISTS = ["Backlog", "Review", "Scheduled", "Published"]
    DEFAULT_BOOTSTRAP_LISTS = {
        "To Do",
        "Doing",
        "Done",
        "A Fazer",
        "Fazendo",
        "Concluido",
        "Concluido (PT)",
        "Concluido PT",
    }
    QUARTER_LIST_PATTERN = re.compile(r"^Q[1-4]\s+\d{4}\s+-\s+[A-Za-z]+\s*$")
    MONTH_YEAR_LIST_PATTERN = re.compile(
        r"^(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}\s*$"
    )

    def __init__(
        self,
        api_key: Optional[str] = None,
        token: Optional[str] = None,
        board_id: Optional[str] = None,
        client: Optional[TrelloClient] = None,
        request_delay_seconds: Optional[float] = None,
    ) -> None:
        """
        Initialize TrelloSync.

        Args:
            api_key: Trello API key
            token: Trello API token
            board_id: Existing board ID (optional)
            client: Optional TrelloClient instance for testing/mocking
        """
        self.api_key = api_key or os.getenv("TRELLO_API_KEY")
        self.token = token or os.getenv("TRELLO_TOKEN")
        self.board_id = board_id or os.getenv("TRELLO_BOARD_ID")
        if request_delay_seconds is None:
            request_delay_seconds = float(os.getenv("SOCICLAW_TRELLO_DELAY_SECONDS", "0.2"))
        self.request_delay_seconds = max(0.0, float(request_delay_seconds))
        self.plan_window_days = max(1, int(os.getenv("SOCICLAW_TRELLO_PLAN_WINDOW_DAYS", "14")))
        self.allow_past_month_routing = (
            os.getenv("SOCICLAW_TRELLO_ALLOW_PAST_MONTH_ROUTING", "").strip().lower()
            in {"1", "true", "yes", "on"}
        )

        if not client and (not self.api_key or not self.token):
            raise ValueError("TRELLO_API_KEY and TRELLO_TOKEN must be provided")

        if client is not None:
            self.client = client
        else:
            if TrelloClient is None:
                raise ImportError("py-trello is required for Trello sync")
            self.client = TrelloClient(api_key=self.api_key, token=self.token)
        self.board = None

    def setup_board(self) -> None:
        """
        Ensure the SociClaw board and required lists exist.
        """
        if self.board_id:
            self.board = self.client.get_board(self.board_id)
            logger.info("Using existing Trello board")
        else:
            self.board = self._find_or_create_board(self.BOARD_NAME)

        self._ensure_lists()

    def create_card(self, post: GeneratedPost, list_name: Optional[str] = None):
        """
        Create a Trello card for a generated post.

        Args:
            post: GeneratedPost instance
            list_name: Target list name. If omitted, SociClaw routes by post month
                      when available, otherwise falls back to Backlog.

        Returns:
            Created card object
        """
        if not self.board:
            self.setup_board()

        resolved_list_name = self._resolve_target_list_name(post, requested_list_name=list_name)
        target_list = self._get_list_by_name(resolved_list_name)
        if not target_list and resolved_list_name != "Backlog":
            self.board.add_list(resolved_list_name)
            self._throttle()
            target_list = self._get_list_by_name(resolved_list_name)
        if not target_list:
            target_list = self._get_list_by_name("Backlog")
        if not target_list:
            raise ValueError("List not found: Backlog")

        post_id = self._build_post_identity(post)
        existing = self._find_card_by_identity_anywhere(post_id)
        if existing:
            return existing

        title = self._summarize_title(post.text)

        due_date = self._build_due_date(post)
        if post.details and post.details.strip():
            full_content = post.details.strip()
        else:
            content_parts = [part.strip() for part in [post.title, post.body] if part and part.strip()]
            if post.text and post.text.strip():
                content_parts.append(f"Post:\n{post.text.strip()}")
            full_content = "\n\n".join(content_parts).strip() or "Post content unavailable."
        description = f"{full_content}\n\n[SociClaw-ID:{post_id}]"
        card = target_list.add_card(name=title, desc=description, due=due_date)
        self._throttle()

        label = self._get_or_create_label(post.category)
        if label:
            card.add_label(label)

        self._ensure_checklist(card)
        return card

    def attach_image_to_post(
        self,
        post: GeneratedPost,
        *,
        image_url: Optional[str] = None,
        image_path: Optional[str] = None,
    ):
        """
        Attach an image to the Trello card corresponding to a generated post.
        Creates the card if it does not exist yet.
        """
        post_id = self._build_post_identity(post)
        card = self._find_card_by_identity_anywhere(post_id)
        if not card:
            card = self.create_card(post)

        if image_url:
            card.attach(name="image", url=image_url)
            self._throttle()
            return card
        if image_path:
            with open(image_path, "rb") as handle:
                card.attach(name="image", file=handle)
            self._throttle()
            return card
        raise ValueError("image_url or image_path is required")

    def update_card_status(self, card_id: str, list_name: str):
        """
        Move a card to a different list (status).
        """
        if not self.board:
            self.setup_board()

        target_list = self._get_list_by_name(list_name)
        if not target_list:
            raise ValueError(f"List not found: {list_name}")

        card = self.client.get_card(card_id)
        card.change_list(target_list.id)
        self._throttle()
        return card

    def attach_image(self, card_id: str, image_url: Optional[str] = None, image_path: Optional[str] = None) -> None:
        """
        Attach an image to a card.
        """
        card = self.client.get_card(card_id)
        if image_url:
            card.attach(name="image", url=image_url)
            self._throttle()
            return
        if image_path:
            with open(image_path, "rb") as handle:
                card.attach(name="image", file=handle)
            self._throttle()
            return
        raise ValueError("image_url or image_path is required")

    def _find_or_create_board(self, name: str):
        boards = self.client.list_boards()
        for board in boards:
            if board.name == name:
                logger.info("Found existing Trello board")
                return board
        logger.info("Creating Trello board")
        return self.client.add_board(name)

    def _ensure_lists(self) -> None:
        existing_open_lists = list(self.board.list_lists("open"))
        self._archive_default_bootstrap_lists(existing_open_lists)
        active_month_names = self._active_month_list_names()
        self._archive_stale_content_lists(existing_open_lists, active_month_names)

        required_names = self._required_list_names()
        existing_lists = {lst.name: lst for lst in self.board.list_lists("open")}
        for name in required_names:
            if name not in existing_lists:
                self.board.add_list(name)
                self._throttle()
                existing_lists = {lst.name: lst for lst in self.board.list_lists("open")}
        self._reorder_required_lists_to_front(required_names)

    def _required_list_names(self, *, reference_date: Optional[datetime] = None) -> List[str]:
        """
        Build a minimal Trello column set.

        We only create month columns inside the active planning window, starting
        from the user's current date, to avoid stale columns such as January when
        the user is already in February.
        """
        month_lists = self._active_month_list_names(reference_date=reference_date)
        return [*month_lists, "Backlog", "Review", "Scheduled", "Published"]

    def _resolve_target_list_name(self, post: GeneratedPost, *, requested_list_name: Optional[str]) -> str:
        if requested_list_name and requested_list_name.strip():
            return requested_list_name.strip()

        due_date = self._build_due_date(post)
        if due_date:
            today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            if due_date < today_start and not self.allow_past_month_routing:
                return today_start.strftime("%B %Y")
            return due_date.strftime("%B %Y")

        return "Backlog"

    def _active_month_list_names(self, *, reference_date: Optional[datetime] = None) -> List[str]:
        if reference_date is None:
            reference_date = datetime.utcnow()

        month_keys = set()
        for offset in range(self.plan_window_days):
            day = reference_date + timedelta(days=offset)
            month_keys.add((day.year, day.month))

        ordered = sorted(month_keys)
        return [datetime(year=y, month=m, day=1).strftime("%B %Y") for y, m in ordered]

    def _archive_default_bootstrap_lists(self, open_lists: List) -> None:
        """
        Archive empty default Trello lists so SociClaw columns are not pushed to
        the far right behind generic starter columns.
        """
        for lst in open_lists:
            name = (getattr(lst, "name", "") or "").strip()
            if name not in self.DEFAULT_BOOTSTRAP_LISTS:
                continue
            try:
                cards = lst.list_cards()
            except Exception:
                cards = []
            if cards:
                continue
            try:
                lst.close()
                self._throttle()
            except Exception:
                logger.warning("Could not archive default Trello list: %s", name)

    def _archive_stale_content_lists(self, open_lists: List, active_month_names: List[str]) -> None:
        """
        Archive legacy/stale content columns that are outside the active planning
        window. This removes old quarter-based lists and outdated month lists.
        """
        active_set = set(active_month_names)
        for lst in open_lists:
            name = (getattr(lst, "name", "") or "").strip()
            if not name:
                continue
            if name in active_set:
                continue
            if not (self.QUARTER_LIST_PATTERN.match(name) or self.MONTH_YEAR_LIST_PATTERN.match(name)):
                continue
            try:
                lst.close()
                self._throttle()
            except Exception:
                logger.warning("Could not archive stale Trello content list: %s", name)

    def _reorder_required_lists_to_front(self, required_names: List[str]) -> None:
        """
        Keep SociClaw columns at the beginning of the board, in predictable order.
        """
        open_lists = {lst.name: lst for lst in self.board.list_lists("open")}
        for name in reversed(required_names):
            lst = open_lists.get(name)
            if not lst:
                continue
            try:
                lst.move("top")
                self._throttle()
            except Exception:
                logger.warning("Could not reorder Trello list: %s", name)

    def _get_list_by_name(self, name: str):
        lists = self.board.list_lists("open")
        for lst in lists:
            if lst.name == name:
                return lst
        return None

    def _get_or_create_label(self, name: str):
        labels = self.board.get_labels()
        for label in labels:
            if label.name == name:
                return label
        return self.board.add_label(name, "blue")

    def _summarize_title(self, text: str) -> str:
        if not text or not text.strip():
            return "Untitled Post"
        first_line = text.strip().splitlines()[0]
        return (first_line[:80] + "...") if len(first_line) > 80 else first_line

    def _build_due_date(self, post: GeneratedPost) -> Optional[datetime]:
        if not post.date or post.time is None:
            return None
        try:
            date_obj = datetime.fromisoformat(post.date)
            return date_obj.replace(hour=int(post.time), minute=0, second=0, microsecond=0)
        except Exception:
            return None

    def _ensure_checklist(self, card) -> None:
        checklist_name = "Approval"

        checklists = []
        try:
            if hasattr(card, "get_checklists") and callable(card.get_checklists):
                checklists = card.get_checklists() or []
            elif hasattr(card, "checklists"):
                checklists = getattr(card, "checklists") or []
        except Exception:
            checklists = []

        for checklist in checklists:
            if getattr(checklist, "name", None) == checklist_name:
                return

        if not hasattr(card, "add_checklist"):
            logger.warning("Card object does not support add_checklist; skipping checklist creation.")
            return

        checklist = card.add_checklist(checklist_name)
        for item in ["Review copy", "Approve image", "Schedule"]:
            checklist.add_checklist_item(item, checked=False)
            self._throttle()

    def _throttle(self) -> None:
        if self.request_delay_seconds > 0:
            time.sleep(self.request_delay_seconds)

    def _build_post_identity(self, post: GeneratedPost) -> str:
        base = "|".join(
            [
                str(post.date or ""),
                str(post.time or ""),
                str(post.category or ""),
                str(post.text or ""),
            ]
        )
        return hashlib.sha1(base.encode("utf-8")).hexdigest()[:16]

    def _find_card_by_identity(self, target_list, post_id: str):
        marker = f"[SociClaw-ID:{post_id}]"
        try:
            cards = target_list.list_cards()
        except Exception:
            return None
        for card in cards:
            desc = getattr(card, "description", "") or ""
            if marker in desc:
                return card
        return None

    def _find_card_by_identity_anywhere(self, post_id: str):
        marker = f"[SociClaw-ID:{post_id}]"
        try:
            lists = self.board.list_lists("open")
        except Exception:
            return None
        for lst in lists:
            try:
                cards = lst.list_cards()
            except Exception:
                continue
            for card in cards:
                desc = getattr(card, "description", "") or ""
                if marker in desc:
                    return card
        return None
