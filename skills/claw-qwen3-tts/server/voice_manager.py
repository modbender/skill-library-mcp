"""
voice_manager.py — Persistent named voice profile management.

Each voice is stored as:
  - <name>.json  — metadata (name, description, source, timestamps, tags)
  - <name>.pt    — PyTorch speaker embedding tensor
  - <name>_sample.wav — optional sample audio

Voices are case-insensitive for lookup but preserve user casing on disk.
"""

import json
import os
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import torch


class VoiceProfile:
    """Represents a single saved voice profile."""

    def __init__(
        self,
        name: str,
        description: str = "",
        source: str = "unknown",
        source_description: str = "",
        language: str = "en",
        tags: Optional[list[str]] = None,
        embedding_file: str = "",
        sample_audio: str = "",
        usage_count: int = 0,
        created_at: Optional[str] = None,
        updated_at: Optional[str] = None,
    ):
        now = datetime.now(timezone.utc).isoformat()
        self.name = name
        self.description = description
        self.source = source
        self.source_description = source_description
        self.language = language
        self.tags = tags or []
        self.embedding_file = embedding_file or f"{name}.pt"
        self.sample_audio = sample_audio
        self.usage_count = usage_count
        self.created_at = created_at or now
        self.updated_at = updated_at or now

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "source": self.source,
            "source_description": self.source_description,
            "language": self.language,
            "tags": self.tags,
            "embedding_file": self.embedding_file,
            "sample_audio": self.sample_audio,
            "usage_count": self.usage_count,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "VoiceProfile":
        return cls(**data)

    def touch(self):
        """Update the updated_at timestamp and increment usage count."""
        self.updated_at = datetime.now(timezone.utc).isoformat()
        self.usage_count += 1


class VoiceManager:
    """
    Manages persistent named voice profiles on disk.

    Voice directory structure:
        voices/
        ├── Angie.json
        ├── Angie.pt
        ├── Angie_sample.wav  (optional)
        ├── CaptainHook.json
        ├── CaptainHook.pt
        └── ...
    """

    def __init__(self, voices_dir: str):
        self.voices_dir = Path(voices_dir)
        self.voices_dir.mkdir(parents=True, exist_ok=True)
        self._cache: dict[str, VoiceProfile] = {}
        self._load_all()

    def _load_all(self):
        """Load all voice profiles from disk into cache."""
        self._cache.clear()
        for json_file in self.voices_dir.glob("*.json"):
            try:
                with open(json_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                profile = VoiceProfile.from_dict(data)
                self._cache[profile.name.lower()] = profile
            except (json.JSONDecodeError, KeyError, TypeError) as e:
                print(f"[WARN] Failed to load voice profile {json_file}: {e}")

    def _sanitize_filename(self, name: str) -> str:
        """Sanitize a voice name for use as a filename."""
        # Replace problematic chars but keep the name readable
        safe = "".join(c if c.isalnum() or c in "-_ " else "_" for c in name)
        return safe.strip().replace(" ", "_")

    def list_voices(self) -> list[dict]:
        """List all saved voice profiles."""
        return [profile.to_dict() for profile in sorted(
            self._cache.values(), key=lambda p: p.usage_count, reverse=True
        )]

    def get_voice(self, name: str) -> Optional[VoiceProfile]:
        """Get a voice profile by name (case-insensitive)."""
        return self._cache.get(name.lower())

    def voice_exists(self, name: str) -> bool:
        """Check if a voice name already exists."""
        return name.lower() in self._cache

    def save_voice(
        self,
        name: str,
        embedding: torch.Tensor,
        description: str = "",
        source: str = "unknown",
        source_description: str = "",
        language: str = "en",
        tags: Optional[list[str]] = None,
        sample_audio_path: Optional[str] = None,
    ) -> VoiceProfile:
        """
        Save a new voice profile with the given name.

        Args:
            name: User-chosen name for the voice
            embedding: Speaker embedding tensor
            description: Human-readable description
            source: "voice-design" or "voice-clone"
            source_description: The original voice description or reference info
            language: Primary language
            tags: Optional tags for categorization
            sample_audio_path: Optional path to a sample audio file

        Returns:
            The saved VoiceProfile

        Raises:
            ValueError: If name is empty or contains invalid characters
        """
        if not name or not name.strip():
            raise ValueError("Voice name cannot be empty")

        safe_name = self._sanitize_filename(name)
        embedding_filename = f"{safe_name}.pt"
        sample_filename = ""

        # Save embedding tensor
        embedding_path = self.voices_dir / embedding_filename
        torch.save(embedding, embedding_path)

        # Copy sample audio if provided
        if sample_audio_path and os.path.exists(sample_audio_path):
            sample_filename = f"{safe_name}_sample.wav"
            shutil.copy2(sample_audio_path, self.voices_dir / sample_filename)

        # Create profile
        profile = VoiceProfile(
            name=name,
            description=description,
            source=source,
            source_description=source_description,
            language=language,
            tags=tags,
            embedding_file=embedding_filename,
            sample_audio=sample_filename,
        )

        # Save metadata JSON
        json_path = self.voices_dir / f"{safe_name}.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(profile.to_dict(), f, indent=2, ensure_ascii=False)

        # Update cache
        self._cache[name.lower()] = profile
        return profile

    def load_embedding(self, name: str) -> Optional[torch.Tensor]:
        """
        Load the speaker embedding tensor for a named voice.

        Also increments usage_count and updates timestamps.
        """
        profile = self.get_voice(name)
        if profile is None:
            return None

        embedding_path = self.voices_dir / profile.embedding_file
        if not embedding_path.exists():
            return None

        # Increment usage
        profile.touch()
        self._save_profile(profile)

        return torch.load(embedding_path, weights_only=True)

    def rename_voice(self, old_name: str, new_name: str) -> Optional[VoiceProfile]:
        """
        Rename a voice profile.

        Returns the updated profile, or None if the old name doesn't exist.
        Raises ValueError if the new name already exists.
        """
        profile = self.get_voice(old_name)
        if profile is None:
            return None

        if self.voice_exists(new_name) and new_name.lower() != old_name.lower():
            raise ValueError(f"Voice name '{new_name}' already exists")

        old_safe = self._sanitize_filename(profile.name)
        new_safe = self._sanitize_filename(new_name)

        # Rename files on disk
        for ext in [".json", ".pt", "_sample.wav"]:
            old_path = self.voices_dir / f"{old_safe}{ext}"
            new_path = self.voices_dir / f"{new_safe}{ext}"
            if old_path.exists():
                old_path.rename(new_path)

        # Update profile
        del self._cache[old_name.lower()]
        profile.name = new_name
        profile.embedding_file = f"{new_safe}.pt"
        if profile.sample_audio:
            profile.sample_audio = f"{new_safe}_sample.wav"
        profile.updated_at = datetime.now(timezone.utc).isoformat()

        # Save updated metadata
        self._cache[new_name.lower()] = profile
        self._save_profile(profile)

        return profile

    def delete_voice(self, name: str) -> bool:
        """
        Delete a voice profile and all associated files.

        Returns True if deleted, False if not found.
        """
        profile = self.get_voice(name)
        if profile is None:
            return False

        safe_name = self._sanitize_filename(profile.name)

        # Remove files
        for ext in [".json", ".pt", "_sample.wav"]:
            path = self.voices_dir / f"{safe_name}{ext}"
            if path.exists():
                path.unlink()

        # Remove from cache
        del self._cache[name.lower()]
        return True

    def update_voice(
        self,
        name: str,
        description: Optional[str] = None,
        tags: Optional[list[str]] = None,
        language: Optional[str] = None,
    ) -> Optional[VoiceProfile]:
        """Update metadata fields of an existing voice profile."""
        profile = self.get_voice(name)
        if profile is None:
            return None

        if description is not None:
            profile.description = description
        if tags is not None:
            profile.tags = tags
        if language is not None:
            profile.language = language

        profile.updated_at = datetime.now(timezone.utc).isoformat()
        self._save_profile(profile)
        return profile

    def _save_profile(self, profile: VoiceProfile):
        """Save a profile's metadata to disk."""
        safe_name = self._sanitize_filename(profile.name)
        json_path = self.voices_dir / f"{safe_name}.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(profile.to_dict(), f, indent=2, ensure_ascii=False)
