"""
OpenClaw Transcript Parser

Parses OpenClaw session files (.jsonl) to extract usage data.
This allows tracking even without API keys by reading local logs.

Session files are at: ~/.openclaw/agents/<agent>/sessions/*.jsonl
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Generator, Optional
import logging

logger = logging.getLogger(__name__)

DEFAULT_SESSIONS_DIR = Path.home() / ".openclaw" / "agents"


class TranscriptParser:
    """Parse OpenClaw transcript files for usage data."""
    
    def __init__(self, sessions_dir: Optional[Path] = None):
        self.sessions_dir = sessions_dir or DEFAULT_SESSIONS_DIR
    
    def find_session_files(self, agent: str = "main", since: datetime = None) -> list[Path]:
        """Find session files, optionally filtered by modification time."""
        agent_dir = self.sessions_dir / agent / "sessions"
        if not agent_dir.exists():
            return []
        
        files = []
        for f in agent_dir.glob("*.jsonl"):
            # Skip deleted/archived
            if ".deleted." in f.name or ".archived." in f.name:
                continue
            
            if since:
                mtime = datetime.fromtimestamp(f.stat().st_mtime)
                if mtime < since:
                    continue
            
            files.append(f)
        
        return sorted(files, key=lambda f: f.stat().st_mtime, reverse=True)
    
    def parse_session(self, path: Path) -> Generator[dict, None, None]:
        """Parse a session file and yield usage records."""
        try:
            with open(path, "r") as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue
                    
                    try:
                        event = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    
                    # Look for assistant messages with usage data
                    if event.get("role") == "assistant":
                        usage = self._extract_usage(event)
                        if usage:
                            usage["session_file"] = str(path)
                            usage["line_number"] = line_num
                            yield usage
                            
        except Exception as e:
            logger.error(f"Failed to parse {path}: {e}")
    
    def _extract_usage(self, event: dict) -> Optional[dict]:
        """Extract usage data from an event."""
        # Check for usage in various locations
        usage = event.get("usage") or event.get("_usage") or {}
        
        if not usage:
            # Try nested in metadata
            meta = event.get("metadata", {})
            usage = meta.get("usage", {})
        
        if not usage:
            return None
        
        # Extract tokens
        input_tokens = usage.get("input_tokens", 0) or usage.get("prompt_tokens", 0)
        output_tokens = usage.get("output_tokens", 0) or usage.get("completion_tokens", 0)
        
        if input_tokens == 0 and output_tokens == 0:
            return None
        
        # Determine provider and model
        model = event.get("model", "") or usage.get("model", "")
        provider = self._detect_provider(model)
        
        # Try to get timestamp
        timestamp = event.get("timestamp") or event.get("created_at")
        if timestamp and isinstance(timestamp, (int, float)):
            timestamp = datetime.fromtimestamp(timestamp / 1000 if timestamp > 1e12 else timestamp)
        elif timestamp and isinstance(timestamp, str):
            try:
                timestamp = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            except:
                timestamp = None
        
        return {
            "provider": provider,
            "model": model,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cache_read_tokens": usage.get("cache_read_input_tokens", 0),
            "cache_write_tokens": usage.get("cache_creation_input_tokens", 0),
            "timestamp": timestamp,
        }
    
    def _detect_provider(self, model: str) -> str:
        """Detect provider from model name."""
        model_lower = model.lower()
        
        if "claude" in model_lower or "anthropic" in model_lower:
            return "anthropic"
        elif "gemini" in model_lower or "google" in model_lower:
            return "gemini"
        elif "gpt" in model_lower or "openai" in model_lower:
            return "openai"
        elif "deepseek" in model_lower:
            return "deepseek"
        elif "qwen" in model_lower:
            return "qwen"
        else:
            return "unknown"
    
    def scan_all_sessions(
        self, 
        agents: list[str] = None, 
        since: datetime = None
    ) -> Generator[dict, None, None]:
        """Scan all session files and yield usage records."""
        agents = agents or ["main"]
        
        for agent in agents:
            for session_file in self.find_session_files(agent, since):
                for usage in self.parse_session(session_file):
                    usage["agent"] = agent
                    yield usage


# Singleton instance
_parser = None

def get_parser() -> TranscriptParser:
    global _parser
    if _parser is None:
        _parser = TranscriptParser()
    return _parser
