#!/usr/bin/env python3
"""
Telnyx RAG Memory - Sync Script

Syncs workspace files to Telnyx Storage for semantic search.
Files are auto-embedded by Telnyx AI when embeddings are enabled on the bucket.

Supports smart chunking for large files (markdown, JSON/Slack exports).

Usage:
  ./sync.py                 # Sync all configured files
  ./sync.py --watch         # Watch for changes and sync in real-time
  ./sync.py --list          # List files in bucket
  ./sync.py --create-bucket # Create the memory bucket
  ./sync.py --status        # Check bucket and embedding status
  ./sync.py --prune         # Remove orphaned files from bucket
  ./sync.py --quiet         # Only show errors (good for cron)
  ./sync.py --embed         # Trigger embedding after sync
  ./sync.py --embed-status <task_id>  # Check embedding task status
  ./sync.py --chunk-size 600          # Override chunk size (tokens)
"""

import os
import sys
import json
import hashlib
import hmac
import datetime
import urllib.request
import urllib.error
import urllib.parse
import time
import re
import argparse
from pathlib import Path

# Default configuration
DEFAULT_CONFIG = {
    "bucket": "chief-memory",
    "region": "us-central-1",
    "workspace": "/home/node/clawd",
    "patterns": [
        "MEMORY.md",
        "USER.md",
        "SOUL.md",
        "AGENTS.md",
        "TOOLS.md",
        "GUARDRAILS.md",
        "memory/*.md",
        "knowledge/*.json",
        "knowledge/*.md",
        "skills/*/SKILL.md",
        "docs/*.md",
    ],
    "exclude": [
        "*.tmp",
        "*~",
        ".git/*",
        "__pycache__/*",
        "node_modules/*",
    ],
    "priority_prefixes": ["memory/", "MEMORY.md"],
    "chunk_size": 800,
}

# ---------------------------------------------------------------------------
# Chunking helpers
# ---------------------------------------------------------------------------

def _estimate_tokens(text):
    """Estimate token count from character count (approx 1 token per 4 chars)

    Args:
        text (str): Input text

    Returns:
        int: Estimated token count
    """
    return max(1, len(text) // 4)


def _make_metadata_header(source, chunk_index, total_chunks, title=""):
    """Build a YAML-style metadata header for a chunk

    Args:
        source (str): Original file path
        chunk_index (int): 1-based chunk index
        total_chunks (int): Total chunks for this file
        title (str): Section title

    Returns:
        str: Metadata header block
    """
    lines = ["---"]
    lines.append("source: %s" % source)
    lines.append("chunk: %d/%d" % (chunk_index, total_chunks))
    if title:
        lines.append("title: %s" % title)
    lines.append("---")
    return "\n".join(lines)


def _chunk_key(original_key, index, ext=".md"):
    """Generate deterministic chunk filename

    Args:
        original_key (str): Original S3 key / relative path
        index (int): 1-based chunk index
        ext (str): File extension for chunks

    Returns:
        str: Chunk key like  'path/file__chunk-001.md'
    """
    base, _ = os.path.splitext(original_key)
    return "%s__chunk-%03d%s" % (base, index, ext)


def _extract_heading(text):
    """Extract first markdown heading from text

    Args:
        text (str): Markdown text

    Returns:
        str: Heading text or empty string
    """
    for line in text.split("\n"):
        line = line.strip()
        if line.startswith("#"):
            return line.lstrip("#").strip()
    return ""


def _split_by_paragraphs(text, max_tokens):
    """Split text into chunks by paragraph boundaries respecting token limit

    Args:
        text (str): Input text
        max_tokens (int): Max tokens per chunk

    Returns:
        list[str]: List of text chunks
    """
    paragraphs = re.split(r"\n\s*\n", text)
    chunks = []
    current = []
    current_tokens = 0

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        pt = _estimate_tokens(para)
        if current and (current_tokens + pt) > max_tokens:
            chunks.append("\n\n".join(current))
            current = [para]
            current_tokens = pt
        else:
            current.append(para)
            current_tokens += pt

    if current:
        chunks.append("\n\n".join(current))

    return chunks if chunks else [text]


def chunk_markdown(text, source, max_tokens=800):
    """Split markdown into semantic chunks by headers then paragraphs

    Args:
        text (str): Markdown content
        source (str): Original file path for metadata
        max_tokens (int): Target max tokens per chunk

    Returns:
        list[tuple[str, str]]: List of (chunk_content_with_metadata, title)
    """
    if _estimate_tokens(text) <= max_tokens:
        title = _extract_heading(text) or os.path.basename(source)
        header = _make_metadata_header(source, 1, 1, title)
        return [(header + "\n\n" + text, title)]

    # Split on level-2 and level-3 headers
    sections = re.split(r"(?m)^(#{2,3}\s+.+)$", text)

    # Reassemble into (heading, body) pairs
    parts = []
    current_heading = ""
    current_body_parts = []

    i = 0
    while i < len(sections):
        section = sections[i]
        if re.match(r"^#{2,3}\s+", section.strip()):
            # Save previous
            if current_body_parts:
                body = "\n".join(current_body_parts).strip()
                if body:
                    parts.append((current_heading, body))
            current_heading = section.strip().lstrip("#").strip()
            current_body_parts = []
        else:
            current_body_parts.append(section)
        i += 1

    # Save last section
    if current_body_parts:
        body = "\n".join(current_body_parts).strip()
        if body:
            parts.append((current_heading, body))

    if not parts:
        parts = [("", text)]

    # Sub-split large sections by paragraph
    final_parts = []
    for heading, body in parts:
        if _estimate_tokens(body) > max_tokens:
            sub_chunks = _split_by_paragraphs(body, max_tokens)
            for j, sc in enumerate(sub_chunks):
                sub_title = heading
                if len(sub_chunks) > 1:
                    sub_title = "%s (part %d)" % (heading, j + 1) if heading else ""
                final_parts.append((sub_title, sc))
        else:
            final_parts.append((heading, body))

    total = len(final_parts)
    results = []
    for idx, (title, body) in enumerate(final_parts, 1):
        display_title = title or _extract_heading(body) or os.path.basename(source)
        header = _make_metadata_header(source, idx, total, display_title)
        results.append((header + "\n\n" + body, display_title))

    return results


def chunk_slack_json(text, source, max_tokens=800):
    """Split Slack-style JSON exports into chunks by time window / thread

    Args:
        text (str): JSON content (array of message objects)
        source (str): Original file path
        max_tokens (int): Target max tokens per chunk

    Returns:
        list[tuple[str, str]]: List of (chunk_content_with_metadata, title)
    """
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        # Fall back to markdown chunking for invalid JSON
        return chunk_markdown(text, source, max_tokens)

    # Handle both array of messages and object with messages key
    messages = []
    channel_name = ""
    if isinstance(data, list):
        messages = data
        # Try to extract channel from filename
        channel_name = os.path.basename(source).replace(".json", "")
    elif isinstance(data, dict):
        messages = data.get("messages", data.get("data", []))
        channel_name = data.get("channel", data.get("name", ""))
        if not isinstance(messages, list):
            return chunk_markdown(text, source, max_tokens)

    if not messages:
        return chunk_markdown(text, source, max_tokens)

    # Group messages into chunks by token budget
    chunks_raw = []
    current_msgs = []
    current_tokens = 0
    current_authors = set()
    current_dates = []

    for msg in messages:
        if not isinstance(msg, dict):
            continue
        # Extract text content
        msg_text = msg.get("text", msg.get("content", ""))
        user = msg.get("user", msg.get("username", msg.get("author", "unknown")))
        ts = msg.get("ts", msg.get("timestamp", msg.get("date", "")))

        formatted = "[%s] %s: %s" % (str(ts)[:10] if ts else "?", user, msg_text)
        mt = _estimate_tokens(formatted)

        if current_msgs and (current_tokens + mt) > max_tokens:
            chunks_raw.append((current_msgs[:], current_authors.copy(), current_dates[:]))
            current_msgs = [formatted]
            current_tokens = mt
            current_authors = {user}
            current_dates = [str(ts)[:10] if ts else ""]
        else:
            current_msgs.append(formatted)
            current_tokens += mt
            current_authors.add(user)
            if ts:
                current_dates.append(str(ts)[:10])

    if current_msgs:
        chunks_raw.append((current_msgs[:], current_authors.copy(), current_dates[:]))

    total = len(chunks_raw)
    results = []
    for idx, (msgs, authors, dates) in enumerate(chunks_raw, 1):
        date_range = ""
        clean_dates = sorted(set(d for d in dates if d))
        if clean_dates:
            if len(clean_dates) == 1:
                date_range = clean_dates[0]
            else:
                date_range = "%s to %s" % (clean_dates[0], clean_dates[-1])

        title = channel_name or os.path.basename(source)
        meta_lines = ["---"]
        meta_lines.append("source: %s" % source)
        meta_lines.append("chunk: %d/%d" % (idx, total))
        meta_lines.append("title: %s" % title)
        if channel_name:
            meta_lines.append("channel: %s" % channel_name)
        if date_range:
            meta_lines.append("date_range: %s" % date_range)
        if authors:
            meta_lines.append("authors: %s" % ", ".join(sorted(authors)))
        meta_lines.append("---")
        header = "\n".join(meta_lines)

        body = "\n".join(msgs)
        results.append((header + "\n\n" + body, title))

    return results if results else chunk_markdown(text, source, max_tokens)


def chunk_file(filepath, s3_key, max_tokens=800):
    """Chunk a file based on its type

    Args:
        filepath (Path): Local file path
        s3_key (str): Relative path / S3 key
        max_tokens (int): Target max tokens per chunk

    Returns:
        list[tuple[str, str, str]]: List of (chunk_key, content, title)
    """
    try:
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            text = f.read()
    except IOError:
        return []

    if not text.strip():
        return []

    # Small files don't need chunking - return as-is without metadata wrapping
    if _estimate_tokens(text) <= max_tokens:
        return [(s3_key, text, "")]

    # Route by file type
    ext = os.path.splitext(str(filepath))[1].lower()
    if ext == ".json":
        chunks = chunk_slack_json(text, s3_key, max_tokens)
    else:
        chunks = chunk_markdown(text, s3_key, max_tokens)

    # Generate chunk keys
    result = []
    for idx, (content, title) in enumerate(chunks, 1):
        ck = _chunk_key(s3_key, idx)
        result.append((ck, content, title))

    return result


# ---------------------------------------------------------------------------
# Sync state
# ---------------------------------------------------------------------------

class SyncState:
    """Manages sync state tracking with file hashes and chunk mappings"""

    def __init__(self, state_file=".sync-state.json"):
        self.state_file = state_file
        self.state = self._load_state()

    def _load_state(self):
        """Load sync state from disk"""
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, "r") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        return {"file_hashes": {}, "chunk_map": {}, "last_sync": None}

    def save_state(self):
        """Save sync state to disk"""
        self.state["last_sync"] = datetime.datetime.utcnow().isoformat()
        try:
            with open(self.state_file, "w") as f:
                json.dump(self.state, f, indent=2)
        except IOError as e:
            print("Warning: Could not save sync state: %s" % e, file=sys.stderr)

    def get_file_hash(self, filepath):
        """Get stored hash for a file"""
        return self.state["file_hashes"].get(str(filepath))

    def set_file_hash(self, filepath, file_hash):
        """Store hash for a file"""
        self.state["file_hashes"][str(filepath)] = file_hash

    def remove_file(self, filepath):
        """Remove file from sync state"""
        self.state["file_hashes"].pop(str(filepath), None)

    def get_tracked_files(self):
        """Get set of all tracked files (including chunk keys)"""
        tracked = set(self.state["file_hashes"].keys())
        for chunks in self.state.get("chunk_map", {}).values():
            tracked.update(chunks)
        return tracked

    def get_chunk_keys(self, source_key):
        """Get list of chunk keys for a source file

        Args:
            source_key (str): Original file S3 key

        Returns:
            list[str]: List of chunk keys
        """
        return self.state.get("chunk_map", {}).get(source_key, [])

    def set_chunk_keys(self, source_key, chunk_keys):
        """Store chunk key mapping for a source file

        Args:
            source_key (str): Original file S3 key
            chunk_keys (list[str]): Chunk keys produced
        """
        if "chunk_map" not in self.state:
            self.state["chunk_map"] = {}
        self.state["chunk_map"][source_key] = chunk_keys

    def remove_chunks(self, source_key):
        """Remove chunk mapping for a source file

        Args:
            source_key (str): Original file S3 key

        Returns:
            list[str]: Old chunk keys that were tracked
        """
        return self.state.get("chunk_map", {}).pop(source_key, [])

    def get_all_chunk_keys(self):
        """Get all chunk keys across all source files

        Returns:
            set[str]: All chunk keys
        """
        result = set()
        for chunks in self.state.get("chunk_map", {}).values():
            result.update(chunks)
        return result


# ---------------------------------------------------------------------------
# S3 Client
# ---------------------------------------------------------------------------

class TelnyxS3Client:
    """Clean S3 client for Telnyx Cloud Storage using AWS SigV4"""

    def __init__(self, api_key, region):
        self.api_key = api_key
        self.region = region
        self.secret_key = "placeholder"  # Telnyx uses API key as access key

    def _sign(self, key, msg):
        """AWS SigV4 signing helper"""
        return hmac.new(key, msg.encode("utf-8"), hashlib.sha256).digest()

    def _get_signature_key(self, date_stamp):
        """Generate AWS SigV4 signing key"""
        k_date = self._sign(("AWS4" + self.secret_key).encode("utf-8"), date_stamp)
        k_region = self._sign(k_date, self.region)
        k_service = self._sign(k_region, "s3")
        k_signing = self._sign(k_service, "aws4_request")
        return k_signing

    def _make_request(self, method, bucket, key, payload=b"", content_type=None, extra_headers=None):
        """Make authenticated S3 request"""
        host = (
            "%s.%s.telnyxcloudstorage.com" % (bucket, self.region)
            if bucket
            else "%s.telnyxcloudstorage.com" % self.region
        )
        path = "/%s" % key if key else "/"

        t = datetime.datetime.utcnow()
        amz_date = t.strftime("%Y%m%dT%H%M%SZ")
        date_stamp = t.strftime("%Y%m%d")

        payload_hash = hashlib.sha256(payload).hexdigest()

        headers = {
            "host": host,
            "x-amz-content-sha256": payload_hash,
            "x-amz-date": amz_date,
        }

        if content_type:
            headers["content-type"] = content_type
        if payload:
            headers["content-length"] = str(len(payload))
        if extra_headers:
            headers.update(extra_headers)

        canonical_headers = "".join("%s:%s\n" % (k, v) for k, v in sorted(headers.items()))
        signed_headers = ";".join(sorted(headers.keys()))

        canonical_request = "%s\n%s\n\n%s\n%s\n%s" % (
            method, path, canonical_headers, signed_headers, payload_hash
        )

        algorithm = "AWS4-HMAC-SHA256"
        credential_scope = "%s/%s/s3/aws4_request" % (date_stamp, self.region)
        string_to_sign = "%s\n%s\n%s\n%s" % (
            algorithm,
            amz_date,
            credential_scope,
            hashlib.sha256(canonical_request.encode()).hexdigest(),
        )

        signing_key = self._get_signature_key(date_stamp)
        signature = hmac.new(signing_key, string_to_sign.encode(), hashlib.sha256).hexdigest()

        auth = "%s Credential=%s/%s, SignedHeaders=%s, Signature=%s" % (
            algorithm, self.api_key, credential_scope, signed_headers, signature
        )

        request_headers = {
            "x-amz-date": amz_date,
            "x-amz-content-sha256": payload_hash,
            "Authorization": auth,
        }
        if content_type:
            request_headers["Content-Type"] = content_type
        if payload:
            request_headers["Content-Length"] = str(len(payload))
        if extra_headers:
            request_headers.update(extra_headers)

        url = "https://%s%s" % (host, path)
        req = urllib.request.Request(
            url, data=payload if payload else None, headers=request_headers, method=method
        )

        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                return response.status, response.read().decode("utf-8", errors="ignore")
        except urllib.error.HTTPError as e:
            return e.code, e.read().decode("utf-8", errors="ignore")
        except Exception as e:
            return 0, str(e)

    def put_object(self, bucket, key, data, content_type=None):
        """Upload object to bucket"""
        if isinstance(data, str):
            data = data.encode("utf-8")

        if not content_type:
            if key.endswith(".md"):
                content_type = "text/markdown"
            elif key.endswith(".json"):
                content_type = "application/json"
            else:
                content_type = "text/plain"

        status, _ = self._make_request("PUT", bucket, key, data, content_type)
        return status in [200, 204]

    def head_object(self, bucket, key):
        """Check if object exists and get metadata"""
        status, _ = self._make_request("HEAD", bucket, key)
        return status == 200

    def list_objects(self, bucket, prefix=""):
        """List objects in bucket"""
        query = "?prefix=%s" % urllib.parse.quote(prefix) if prefix else ""
        status, body = self._make_request("GET", bucket, "" + query)

        if status == 200:
            files = []
            for match in re.finditer(r"<Key>([^<]+)</Key>", body):
                files.append(match.group(1))
            return files
        return []

    def delete_object(self, bucket, key):
        """Delete object from bucket"""
        status, _ = self._make_request("DELETE", bucket, key)
        return status in [200, 204]

    def create_bucket(self, bucket):
        """Create bucket in region"""
        bucket_config = (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<CreateBucketConfiguration xmlns="http://s3.amazonaws.com/doc/2006-03-01/">\n'
            "  <LocationConstraint>%s</LocationConstraint>\n"
            "</CreateBucketConfiguration>" % self.region
        )

        host = "%s.telnyxcloudstorage.com" % self.region
        path = "/%s" % bucket

        t = datetime.datetime.utcnow()
        amz_date = t.strftime("%Y%m%dT%H%M%SZ")
        date_stamp = t.strftime("%Y%m%d")

        payload = bucket_config.encode()
        payload_hash = hashlib.sha256(payload).hexdigest()

        headers = {
            "host": host,
            "x-amz-content-sha256": payload_hash,
            "x-amz-date": amz_date,
            "content-type": "application/xml",
            "content-length": str(len(payload)),
        }

        canonical_headers = "".join("%s:%s\n" % (k, v) for k, v in sorted(headers.items()))
        signed_headers = ";".join(sorted(headers.keys()))

        canonical_request = "PUT\n%s\n\n%s\n%s\n%s" % (
            path, canonical_headers, signed_headers, payload_hash
        )

        algorithm = "AWS4-HMAC-SHA256"
        credential_scope = "%s/%s/s3/aws4_request" % (date_stamp, self.region)
        string_to_sign = "%s\n%s\n%s\n%s" % (
            algorithm,
            amz_date,
            credential_scope,
            hashlib.sha256(canonical_request.encode()).hexdigest(),
        )

        signing_key = self._get_signature_key(date_stamp)
        signature = hmac.new(signing_key, string_to_sign.encode(), hashlib.sha256).hexdigest()

        auth = "%s Credential=%s/%s, SignedHeaders=%s, Signature=%s" % (
            algorithm, self.api_key, credential_scope, signed_headers, signature
        )

        request_headers = {
            "x-amz-date": amz_date,
            "x-amz-content-sha256": payload_hash,
            "Authorization": auth,
            "Content-Type": "application/xml",
            "Content-Length": str(len(payload)),
        }

        url = "https://%s%s" % (host, path)
        req = urllib.request.Request(url, data=payload, headers=request_headers, method="PUT")

        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                status = response.status
        except urllib.error.HTTPError as e:
            status = e.code
        except Exception:
            status = 0

        return status in [200, 204] or status == 409  # 409 = already exists


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_config():
    """Load configuration from file or defaults"""
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
    if os.path.exists(config_path):
        try:
            with open(config_path) as f:
                user_config = json.load(f)
                return {**DEFAULT_CONFIG, **user_config}
        except (json.JSONDecodeError, IOError):
            pass
    return DEFAULT_CONFIG


def load_credentials():
    """Load Telnyx API key from environment or .env file"""
    api_key = os.environ.get("TELNYX_API_KEY")
    if api_key:
        return api_key

    env_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    if os.path.exists(env_file):
        try:
            with open(env_file) as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("TELNYX_API_KEY="):
                        return line.split("=", 1)[1].strip('"').strip("'")
        except IOError:
            pass
    return None


def calculate_file_hash(filepath):
    """Calculate SHA-256 hash of file contents"""
    hash_sha256 = hashlib.sha256()
    try:
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    except IOError:
        return None


def get_files_to_sync(config):
    """Get list of files to sync based on patterns"""
    workspace = Path(config["workspace"])
    files = []

    for pattern in config["patterns"]:
        for path in workspace.glob(pattern):
            if path.is_file():
                rel_path = path.relative_to(workspace)

                excluded = False
                for excl in config.get("exclude", []):
                    if path.match(excl):
                        excluded = True
                        break

                if not excluded:
                    files.append((path, str(rel_path)))

    return files


def make_api_request(method, endpoint, payload=None):
    """Make Telnyx API request (for embeddings)"""
    api_key = load_credentials()
    if not api_key:
        raise ValueError("No API key available")

    url = "https://api.telnyx.com/v2/%s" % endpoint
    data = json.dumps(payload).encode() if payload else None

    headers = {
        "Authorization": "Bearer %s" % api_key,
        "Content-Type": "application/json",
    }

    req = urllib.request.Request(url, data=data, headers=headers, method=method)

    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            return response.status, json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", errors="ignore")
    except Exception as e:
        return 0, str(e)


def show_progress(current, total, prefix="Progress"):
    """Display a simple progress bar"""
    if total == 0:
        return

    percent = int((current / total) * 100)
    filled = int((current / total) * 40)
    bar = "\u2588" * filled + "\u2591" * (40 - filled)
    print("\r%s: [%s] %d%% (%d/%d)" % (prefix, bar, percent, current, total), end="", flush=True)


# ---------------------------------------------------------------------------
# Sync logic
# ---------------------------------------------------------------------------

def _delete_old_chunks(client, bucket, state, s3_key, quiet=False):
    """Delete previously uploaded chunks for a source file

    Args:
        client (TelnyxS3Client): S3 client
        bucket (str): Bucket name
        state (SyncState): Sync state
        s3_key (str): Source file key
        quiet (bool): Suppress output

    Returns:
        int: Number of chunks deleted
    """
    old_chunks = state.get_chunk_keys(s3_key)
    deleted = 0
    for ck in old_chunks:
        if client.delete_object(bucket, ck):
            deleted += 1
            if not quiet:
                print("  🗑️  %s" % ck)
    return deleted


def sync_files(config, quiet=False, show_progress_bar=True, chunk_size_override=None):
    """Sync all configured files to the bucket with incremental updates and chunking

    Args:
        config (dict): Configuration
        quiet (bool): Suppress output
        show_progress_bar (bool): Show progress
        chunk_size_override (int or None): Override chunk size in tokens

    Returns:
        tuple[int, int]: (success_count, failed_count)
    """
    api_key = load_credentials()
    if not api_key:
        if not quiet:
            print("ERROR: No Telnyx API key found.")
            print("Set TELNYX_API_KEY environment variable or create .env file")
        return 0, 0

    client = TelnyxS3Client(api_key, config["region"])
    state = SyncState()
    files = get_files_to_sync(config)
    max_tokens = chunk_size_override or config.get("chunk_size", 800)

    if not quiet:
        print("\n\U0001f504 Syncing %d files to %s (chunk size: %d tokens)" % (
            len(files), config["bucket"], max_tokens))
        if not files:
            print("No files match the configured patterns.")
            return 0, 0
        print()

    success = 0
    failed = 0
    skipped = 0

    for i, (local_path, s3_key) in enumerate(files, 1):
        if show_progress_bar and not quiet:
            show_progress(i - 1, len(files), "Checking")

        current_hash = calculate_file_hash(local_path)
        if not current_hash:
            failed += 1
            if not quiet:
                print("\n  \u2717 %s (could not read)" % s3_key)
            continue

        stored_hash = state.get_file_hash(s3_key)
        if stored_hash == current_hash:
            skipped += 1
            continue

        # File changed or new — chunk and upload
        chunks = chunk_file(local_path, s3_key, max_tokens)
        if not chunks:
            failed += 1
            if not quiet:
                print("\n  \u2717 %s (empty or unreadable)" % s3_key)
            continue

        # Delete old chunks first
        _delete_old_chunks(client, config["bucket"], state, s3_key, quiet)

        # Upload chunks (or the single file if no chunking needed)
        chunk_keys = []
        all_ok = True
        for ck, content, title in chunks:
            if client.put_object(config["bucket"], ck, content):
                chunk_keys.append(ck)
            else:
                all_ok = False
                if not quiet:
                    print("\n  \u2717 %s" % ck)

        if all_ok:
            success += 1
            state.set_file_hash(s3_key, current_hash)
            if len(chunks) > 1:
                state.set_chunk_keys(s3_key, chunk_keys)
                if not quiet:
                    print("\n  \u2713 %s (%d chunks)" % (s3_key, len(chunks)))
            else:
                # Single file, no chunk mapping needed — clear any old mapping
                state.remove_chunks(s3_key)
                if not quiet:
                    print("\n  \u2713 %s" % s3_key)
        else:
            failed += 1

    if show_progress_bar and not quiet:
        print()  # Final newline

    state.save_state()

    if not quiet:
        print("\n\u2705 Synced: %d | Skipped: %d | Failed: %d" % (success, skipped, failed))

    return success, failed


def prune_orphaned_files(config, quiet=False):
    """Remove files from bucket that no longer exist locally"""
    api_key = load_credentials()
    if not api_key:
        if not quiet:
            print("ERROR: No API key available for pruning")
        return 0

    client = TelnyxS3Client(api_key, config["region"])
    state = SyncState()

    local_files = set(s3_key for _, s3_key in get_files_to_sync(config))

    bucket_files = set(client.list_objects(config["bucket"]))
    tracked_files = state.get_tracked_files()

    orphaned = (bucket_files & tracked_files) - local_files
    # Also include chunk keys whose source no longer exists
    all_chunk_keys = state.get_all_chunk_keys()
    orphaned = orphaned | (all_chunk_keys - set().union(
        *(set(state.get_chunk_keys(k)) for k in local_files if state.get_chunk_keys(k))
    ) if all_chunk_keys else set())

    if not orphaned:
        if not quiet:
            print("No orphaned files to remove.")
        return 0

    if not quiet:
        print("\n\U0001f5d1\ufe0f  Removing %d orphaned files:" % len(orphaned))

    removed = 0
    for file_key in orphaned:
        if client.delete_object(config["bucket"], file_key):
            removed += 1
            state.remove_file(file_key)
            if not quiet:
                print("  \u2713 Removed %s" % file_key)
        else:
            if not quiet:
                print("  \u2717 Failed to remove %s" % file_key)

    state.save_state()

    if not quiet:
        print("\n\u2705 Removed %d orphaned files" % removed)

    return removed


def trigger_embedding(config, quiet=False):
    """Trigger embedding process on the bucket"""
    if not quiet:
        print("\n\U0001f9e0 Triggering embedding on bucket: %s" % config["bucket"])

    status, response = make_api_request("POST", "ai/embeddings", {
        "bucket_name": config["bucket"],
    })

    if status in [200, 201, 202]:
        if not quiet:
            print("\u2705 Embedding triggered successfully")
            if isinstance(response, dict) and "data" in response:
                task_id = response["data"].get("task_id")
                if task_id:
                    print("   Task ID: %s" % task_id)
                    print("   Check status with: ./sync.py --embed-status %s" % task_id)
        return True
    else:
        if not quiet:
            print("\u274c Failed to trigger embedding: %s" % status)
            print("   Response: %s" % response)
        return False


def check_embed_status(task_id, quiet=False):
    """Check embedding task status"""
    if not quiet:
        print("\n\U0001f50d Checking embedding task: %s" % task_id)

    status, response = make_api_request("GET", "ai/embeddings/%s" % task_id)

    if status == 200 and isinstance(response, dict):
        data = response.get("data", {})
        task_status = data.get("status", "unknown")
        progress = data.get("progress", 0)

        if not quiet:
            print("   Status: %s" % task_status)
            print("   Progress: %s%%" % progress)

            if task_status == "completed":
                print("\u2705 Embedding complete! You can now search.")
            elif task_status == "failed":
                error = data.get("error", "Unknown error")
                print("\u274c Error: %s" % error)
        return task_status
    else:
        if not quiet:
            print("\u274c Failed to check status: %s" % status)
        return "unknown"


def list_bucket_files(config, quiet=False):
    """List files in the bucket"""
    api_key = load_credentials()
    if not api_key:
        if not quiet:
            print("ERROR: No API key available")
        return []

    client = TelnyxS3Client(api_key, config["region"])
    files = client.list_objects(config["bucket"])

    if not quiet:
        print("\n\U0001f4c1 Files in %s (%d):" % (config["bucket"], len(files)))
        for f in sorted(files):
            print("  %s" % f)

    return files


def create_bucket(config, quiet=False):
    """Create the memory bucket"""
    api_key = load_credentials()
    if not api_key:
        if not quiet:
            print("ERROR: No API key available")
        return False

    client = TelnyxS3Client(api_key, config["region"])
    bucket = config["bucket"]

    if not quiet:
        print("Creating bucket: %s" % bucket)

    if client.create_bucket(bucket):
        if not quiet:
            print("\u2705 Bucket '%s' ready" % bucket)
        return True
    else:
        if not quiet:
            print("\u274c Failed to create bucket '%s'" % bucket)
        return False


def check_status(config, quiet=False):
    """Check bucket and embedding status"""
    api_key = load_credentials()
    if not api_key:
        if not quiet:
            print("ERROR: No API key available")
        return

    client = TelnyxS3Client(api_key, config["region"])

    if not quiet:
        print("\n\U0001f4ca Status for bucket: %s" % config["bucket"])

    if client.head_object(config["bucket"], ""):
        if not quiet:
            print("  \u2713 Bucket exists")
    else:
        if not quiet:
            print("  \u2717 Bucket not found")
        return

    files = client.list_objects(config["bucket"])
    if not quiet:
        print("  \U0001f4c1 Files indexed: %d" % len(files))

    if not quiet:
        print("  \U0001f9e0 Testing embeddings...")

    test_status, test_response = make_api_request("POST", "ai/embeddings/similarity-search", {
        "bucket_name": config["bucket"],
        "query": "test",
        "num_docs": 1,
    })

    if not quiet:
        if test_status == 200:
            print("  \u2705 Embeddings active and searchable")
        elif test_status == 404:
            print("  \u26a0\ufe0f Embeddings not enabled. Use --embed to trigger.")
        else:
            print("  \u2753 Embedding status unclear: %s" % test_status)


def watch_files(config, quiet=False):
    """Watch for file changes and sync in real-time"""
    if not quiet:
        print("\n\U0001f441\ufe0f Watching for changes in %s" % config["workspace"])
        print("   Press Ctrl+C to stop\n")

    state = SyncState()
    last_check = {}
    max_tokens = config.get("chunk_size", 800)

    try:
        while True:
            files = get_files_to_sync(config)
            changed = []

            for local_path, s3_key in files:
                try:
                    mtime = local_path.stat().st_mtime
                    if s3_key not in last_check or last_check[s3_key] != mtime:
                        if s3_key in last_check:
                            changed.append((local_path, s3_key))
                        last_check[s3_key] = mtime
                except OSError:
                    continue

            if changed:
                api_key = load_credentials()
                if api_key:
                    client = TelnyxS3Client(api_key, config["region"])
                    for local_path, s3_key in changed:
                        try:
                            chunks = chunk_file(local_path, s3_key, max_tokens)
                            if not chunks:
                                continue

                            # Delete old chunks
                            _delete_old_chunks(client, config["bucket"], state, s3_key, quiet)

                            chunk_keys = []
                            for ck, content, title in chunks:
                                if client.put_object(config["bucket"], ck, content):
                                    chunk_keys.append(ck)
                                    if not quiet:
                                        print("  \u2191 %s" % ck)
                                else:
                                    if not quiet:
                                        print("  \u2717 %s" % ck)

                            current_hash = calculate_file_hash(local_path)
                            if current_hash:
                                state.set_file_hash(s3_key, current_hash)
                            if len(chunks) > 1:
                                state.set_chunk_keys(s3_key, chunk_keys)
                            else:
                                state.remove_chunks(s3_key)
                        except Exception as e:
                            if not quiet:
                                print("  \u2717 %s (%s)" % (s3_key, e))

                    if changed:
                        state.save_state()

            time.sleep(2)
    except KeyboardInterrupt:
        if not quiet:
            print("\n\n\U0001f44b Stopped watching")


def main():
    parser = argparse.ArgumentParser(description="Telnyx RAG Memory Sync")
    parser.add_argument("--watch", "-w", action="store_true", help="Watch for changes")
    parser.add_argument("--list", "-l", action="store_true", help="List bucket files")
    parser.add_argument("--create-bucket", action="store_true", help="Create the bucket")
    parser.add_argument("--status", "-s", action="store_true", help="Check status")
    parser.add_argument("--prune", action="store_true", help="Remove orphaned files from bucket")
    parser.add_argument("--quiet", "-q", action="store_true", help="Only show errors")
    parser.add_argument("--embed", action="store_true", help="Trigger embedding after sync")
    parser.add_argument("--embed-status", metavar="TASK_ID", help="Check embedding task status")
    parser.add_argument(
        "--chunk-size", type=int, default=None,
        help="Override chunk size in tokens (default: from config, approx 800)"
    )

    args = parser.parse_args()
    config = load_config()

    if not args.quiet:
        print("\n\U0001f9e0 Telnyx RAG Memory Sync\n" + "=" * 40)

    try:
        if args.create_bucket:
            create_bucket(config, args.quiet)
        elif args.list:
            list_bucket_files(config, args.quiet)
        elif args.status:
            check_status(config, args.quiet)
        elif args.prune:
            prune_orphaned_files(config, args.quiet)
        elif args.embed and not args.watch:
            trigger_embedding(config, args.quiet)
        elif args.embed_status:
            check_embed_status(args.embed_status, args.quiet)
        elif args.watch:
            sync_files(config, args.quiet, chunk_size_override=args.chunk_size)
            watch_files(config, args.quiet)
        else:
            success, failed = sync_files(
                config, args.quiet, chunk_size_override=args.chunk_size
            )
            if args.embed and success > 0:
                trigger_embedding(config, args.quiet)
    except KeyboardInterrupt:
        if not args.quiet:
            print("\n\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print("ERROR: %s" % e, file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
