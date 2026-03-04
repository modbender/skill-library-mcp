"""Thin wrapper around gog CLI for Gmail access."""

import json
import os
import re
import subprocess
from typing import Optional

from kaimail.models import Email, EmailBatch, Thread, ThreadMessage


class GogGmailClient:
    """Gmail client using gog CLI tool."""

    keyring_password: str

    def __init__(
        self,
        account: str = os.environ.get("GCLAW_GMAIL_ACCOUNT", "your@gmail.com"),
        keyring_password: Optional[str] = None,
    ):
        self.account = account
        resolved_password = keyring_password or os.environ.get("GOG_KEYRING_PASSWORD")
        if not resolved_password:
            raise ValueError(
                "GOG_KEYRING_PASSWORD must be set as environment variable or passed explicitly"
            )
        self.keyring_password = resolved_password

    def _run_gog(self, args: list[str], timeout: int = 30) -> str:
        """Run gog command with keyring password set."""
        env = os.environ.copy()
        env["GOG_KEYRING_PASSWORD"] = self.keyring_password

        cmd = ["gog"] + args + ["--account", self.account]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            env=env,
            timeout=timeout,
        )

        if result.returncode != 0:
            raise RuntimeError(f"gog command failed: {result.stderr}")

        return result.stdout

    def search_messages(
        self,
        query: str,
        max_results: int = 50,
    ) -> EmailBatch:
        """Search for messages matching query."""
        output = self._run_gog(
            ["gmail", "messages", "search", query, "--max", str(max_results), "--json"]
        )

        data = json.loads(output)
        messages = data.get("messages", [])

        emails = []
        for msg in messages:
            emails.append(
                Email(
                    id=msg["id"],
                    threadId=msg["threadId"],
                    date=msg["date"],
                    **{"from": msg["from"]},
                    subject=msg["subject"],
                    labels=msg.get("labels", []),
                )
            )

        return EmailBatch(
            emails=emails,
            query=query,
            next_page_token=data.get("nextPageToken"),
        )

    def get_thread(self, thread_id: str) -> Thread:
        """Get full thread with message bodies."""
        output = self._run_gog(["gmail", "thread", "show", thread_id])
        return self._parse_thread_output(thread_id, output)

    def _parse_thread_output(self, thread_id: str, output: str) -> Thread:
        """Parse gog thread show output into Thread model."""
        messages: list[ThreadMessage] = []

        # First line: "Thread contains N message(s)"
        lines = output.strip().split("\n")
        message_count = 1
        if lines and lines[0].startswith("Thread contains"):
            match = re.search(r"(\d+)", lines[0])
            if match:
                message_count = int(match.group(1))

        # Split by message headers
        message_blocks = re.split(r"=== Message \d+/\d+: (\w+) ===", output)

        # message_blocks: ['header...', 'msg_id_1', 'content_1', 'msg_id_2', 'content_2', ...]
        i = 1
        while i < len(message_blocks) - 1:
            msg_id = message_blocks[i]
            content = message_blocks[i + 1]
            i += 2

            msg = self._parse_message_block(msg_id, content)
            if msg:
                messages.append(msg)

        return Thread(
            thread_id=thread_id,
            messages=messages,
            message_count=message_count,
        )

    def _parse_message_block(self, msg_id: str, content: str) -> Optional[ThreadMessage]:
        """Parse a single message block."""
        lines = content.strip().split("\n")

        headers: dict[str, str] = {}
        body_lines: list[str] = []
        attachments: list[str] = []
        in_body = False
        in_attachments = False

        for line in lines:
            if not in_body:
                if line.startswith("From: "):
                    headers["from"] = line[6:].strip()
                elif line.startswith("To: "):
                    headers["to"] = line[4:].strip()
                elif line.startswith("Subject: "):
                    headers["subject"] = line[9:].strip()
                elif line.startswith("Date: "):
                    headers["date"] = line[6:].strip()
                elif line == "" and "from" in headers:
                    in_body = True
            elif in_attachments:
                if line.startswith("attachment"):
                    parts = line.split("\t")
                    if len(parts) >= 2:
                        attachments.append(parts[1])
            else:
                if line == "Attachments:":
                    in_attachments = True
                else:
                    body_lines.append(line)

        if not headers.get("from"):
            return None

        return ThreadMessage(
            id=msg_id,
            **{"from": headers.get("from", "")},
            to=headers.get("to", ""),
            subject=headers.get("subject", ""),
            date=headers.get("date", ""),
            body="\n".join(body_lines).strip(),
            attachments=attachments,
        )
