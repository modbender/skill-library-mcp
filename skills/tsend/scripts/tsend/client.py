"""Telegram Bot API client"""

import httpx
from pathlib import Path
from typing import Any


class TelegramClient:
    """Telegram Bot API client for sending files"""

    def __init__(self, token: str, chat_id: str):
        self.token = token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{token}"
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create async client"""
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=30.0)
        return self._client

    async def close(self) -> None:
        """Close the client"""
        if self._client:
            await self._client.aclose()
            self._client = None

    async def _request(self, method: str, data: dict, files: dict | None = None) -> dict:
        """Send a request to Telegram API"""
        url = f"{self.base_url}/{method}"
        client = await self._get_client()

        try:
            if files:
                response = await client.post(url, data=data, files=files)
            else:
                response = await client.post(url, json=data)

            result = response.json()
            if not result.get("ok"):
                raise TelegramError(f"API Error: {result.get('description', 'Unknown error')}")
            return result
        except httpx.HTTPError as e:
            raise TelegramError(f"Network error: {e}")

    async def send_document(
        self,
        file_path: Path,
        caption: str | None = None,
        filename: str | None = None,
    ) -> dict:
        """Send a document file to Telegram

        Args:
            file_path: Path to the file to send
            caption: Optional caption for the file (max 1024 chars)
            filename: Optional custom filename

        Returns:
            API response data
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # Caption limit: 1024 chars
        if caption and len(caption) > 1024:
            caption = caption[:1021] + "..."

        data = {"chat_id": self.chat_id}
        if caption:
            data["caption"] = caption

        file_data = {"document": (filename or file_path.name, file_path.read_bytes())}

        return await self._request("sendDocument", data, files=file_data)

    async def send_message(
        self,
        text: str,
        parse_mode: str | None = None,
    ) -> dict:
        """Send a text message to Telegram

        Args:
            text: Message text to send
            parse_mode: Optional parse mode (HTML/Markdown)

        Returns:
            API response data
        """
        # Telegram message limit: 4096 chars
        if len(text) > 4096:
            raise ValueError(f"Message too long: {len(text)} chars (max 4096)")

        data = {"chat_id": self.chat_id, "text": text}
        if parse_mode:
            data["parse_mode"] = parse_mode

        return await self._request("sendMessage", data)

    async def send_photo(
        self,
        file_path: Path,
        caption: str | None = None,
    ) -> dict:
        """Send a photo to Telegram

        Args:
            file_path: Path to the image file
            caption: Optional caption (max 1024 chars)

        Returns:
            API response data
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # Caption limit: 1024 chars
        if caption and len(caption) > 1024:
            caption = caption[:1021] + "..."

        data = {"chat_id": self.chat_id}
        if caption:
            data["caption"] = caption

        file_data = {"photo": (file_path.name, file_path.read_bytes())}

        return await self._request("sendPhoto", data, files=file_data)

    async def get_updates(self, timeout: int = 10) -> dict:
        """Get recent updates from Telegram (for finding chat_id)

        Args:
            timeout: Long polling timeout in seconds

        Returns:
            API response data with updates list
        """
        params = {"timeout": timeout}
        client = await self._get_client()

        try:
            url = f"{self.base_url}/getUpdates"
            response = await client.get(url, params=params)
            return response.json()
        except httpx.HTTPError as e:
            raise TelegramError(f"Network error: {e}")

    async def get_me(self) -> dict:
        """Get basic information about the bot

        Returns:
            API response data with bot info
        """
        client = await self._get_client()
        try:
            url = f"{self.base_url}/getMe"
            response = await client.get(url)
            return response.json()
        except httpx.HTTPError as e:
            raise TelegramError(f"Network error: {e}")



class TelegramError(Exception):
    """Telegram API error"""
    pass
