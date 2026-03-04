#!/usr/bin/env python3
"""Format Discord messages into digest format."""

import json
import re
import sys
from datetime import datetime, timezone, timedelta


def extract_links(content: str) -> list:
    """Extract all URLs from message content."""
    url_pattern = r'https?://[^\s<>\[\]()\"\']+(?:\([^\s()]*\))*[^\s<>\[\]()\"\'.,;:!?]'
    return re.findall(url_pattern, content)


def clean_content(content: str) -> str:
    """Clean Discord markdown and mentions."""
    # Remove user mentions <@123456>
    content = re.sub(r'<@!?\d+>', '', content)
    # Remove role mentions <@&123456>
    content = re.sub(r'<@&\d+>', '', content)
    # Remove channel mentions <#123456>
    content = re.sub(r'<#\d+>', '', content)
    # Remove custom emojis <:name:123456>
    content = re.sub(r'<a?:\w+:\d+>', '', content)
    # Remove Discord markdown headers ###, ##, #
    content = re.sub(r'^#{1,3}\s*', '', content, flags=re.MULTILINE)
    # Remove bold/italic markers for clean text
    content = re.sub(r'__([^_]+)__', r'\1', content)
    # Clean extra whitespace
    content = re.sub(r'\s+', ' ', content).strip()
    return content


def make_message_url(guild_id: str, channel_id: str, message_id: str) -> str:
    """Create Discord message URL."""
    return f"https://discord.com/channels/{guild_id}/{channel_id}/{message_id}"


def summarize_content(content: str, max_len: int = 200) -> str:
    """Create a brief summary of the message content."""
    cleaned = clean_content(content)
    # Clean markdown links: [text](url) → text
    cleaned = re.sub(r'\[([^\]]+)\]\([^)]*\)', r'\1', cleaned)
    # Remove standalone URLs
    cleaned = re.sub(r'https?://\S+', '', cleaned)
    # Clean broken parens and extra spaces
    cleaned = re.sub(r'\(\s*\)', '', cleaned)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    if len(cleaned) <= max_len:
        return cleaned
    return cleaned[:max_len].rsplit(' ', 1)[0] + "..."


def extract_title(content: str) -> str:
    """Extract or generate a title from message content."""
    # First try to get Discord header (### Title)
    header_match = re.search(r'^#{1,3}\s*(.+?)$', content, re.MULTILINE)
    if header_match:
        title = header_match.group(1).strip()
        # Remove markdown links from title, keep text
        title = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', title)
        return title[:80]

    cleaned = clean_content(content)
    # Remove URLs
    cleaned = re.sub(r'https?://\S+', '', cleaned).strip()
    # Take first line or first sentence
    first_line = cleaned.split('\n')[0].strip()
    # If first line has bold markers, use that as title
    bold_match = re.search(r'\*\*(.*?)\*\*', first_line)
    if bold_match:
        return bold_match.group(1)[:80]
    # Otherwise use first ~60 chars
    if len(first_line) > 80:
        return first_line[:77].rsplit(' ', 1)[0] + "..."
    return first_line if first_line else "No title"


def format_digest(guild_name: str, guild_id: str, channels_data: list, date: str = None) -> str:
    """
    Format messages into digest.

    channels_data: list of {
        "channel_name": str,
        "channel_id": str,
        "messages": list of Discord message objects
    }
    """
    if not date:
        date = datetime.now(timezone(timedelta(hours=2))).strftime("%d.%m.%y")

    # Header
    lines = [f"**#{guild_name} {date}**\n"]

    msg_count = 0
    for ch_data in channels_data:
        channel_name = ch_data["channel_name"]
        channel_id = ch_data["channel_id"]
        messages = ch_data.get("messages", [])

        if not messages:
            continue

        # Sort by timestamp (oldest first)
        messages.sort(key=lambda m: m.get("id", "0"))

        for msg in messages:
            content = msg.get("content", "")
            embeds = msg.get("embeds", [])
            attachments = msg.get("attachments", [])

            # Skip empty messages (unless they have embeds)
            if not content and not embeds:
                continue

            # Skip very short messages (likely reactions/replies)
            if len(content) < 20 and not embeds:
                continue

            msg_id = msg["id"]
            msg_url = make_message_url(guild_id, channel_id, msg_id)

            # Extract title and summary
            title = extract_title(content)

            # Build summary from content + embeds
            summary_parts = []
            if content:
                summary_parts.append(summarize_content(content))
            for embed in embeds:
                if embed.get("description"):
                    summary_parts.append(summarize_content(embed["description"], 150))
                elif embed.get("title"):
                    summary_parts.append(embed["title"])

            summary = " ".join(summary_parts)[:300] if summary_parts else "No description"

            # Collect all links
            links = extract_links(content)
            for embed in embeds:
                if embed.get("url"):
                    links.append(embed["url"])
            for att in attachments:
                if att.get("url"):
                    links.append(att["url"])

            # Remove duplicates while preserving order
            seen = set()
            unique_links = []
            for l in links:
                if l not in seen:
                    seen.add(l)
                    unique_links.append(l)

            # Format entry matching Nikolay's format exactly
            icon = "📸" if attachments else "📝"

            # Summary: skip the title line, take the meat of the message
            # Remove the first header line to avoid repeating the title
            content_no_header = re.sub(r'^#{1,3}\s*.+?\n', '', content, count=1).strip()
            short_summary = summarize_content(content_no_header if content_no_header else content, 180)
            # Remove markdown artifacts from summary
            short_summary = re.sub(r'\*\*([^*]+)\*\*', r'\1', short_summary)
            short_summary = re.sub(r'#{1,3}\s*', '', short_summary)
            # Clean markdown links: [text](url) → text
            short_summary = re.sub(r'\[([^\]]+)\]\([^)]*\)', r'\1', short_summary)
            # Clean broken link refs
            short_summary = re.sub(r'\(\s*\)', '', short_summary).strip()

            entry = f"**[→post]({msg_url}) | {icon} {channel_name}**\n"
            entry += f"**{title}**\n"
            entry += f"**Details:** {short_summary}\n"

            if unique_links:
                link_parts = []
                for i, link in enumerate(unique_links[:5]):  # max 5 links
                    link_parts.append(f"[source {i+1}]({link})")
                entry += f"**Links:** {' | '.join(link_parts)}\n"

            lines.append(entry)
            msg_count += 1

    if msg_count == 0:
        lines.append("_No new messages for the specified period._")

    return "\n".join(lines)


def format_digest_from_file(input_file: str, guild_name: str, guild_id: str) -> str:
    """Format digest from a JSON file with channel data."""
    with open(input_file, 'r') as f:
        channels_data = json.load(f)
    return format_digest(guild_name, guild_id, channels_data)


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: digest_formatter.py <input.json> <guild_name> <guild_id>")
        print("Input JSON: [{channel_name, channel_id, messages: [...]}]")
        sys.exit(1)

    result = format_digest_from_file(sys.argv[1], sys.argv[2], sys.argv[3])
    print(result)
