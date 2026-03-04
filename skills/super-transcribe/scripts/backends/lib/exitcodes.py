"""
Standardized exit codes for super-transcribe backends.
Enables agents to distinguish error types and give appropriate user-facing messages.

EXIT_OK (0)          — Success
EXIT_GENERAL (1)     — General/unknown error
EXIT_MISSING_DEP (2) — Missing dependency (backend, pyannote, yt-dlp, etc.)
EXIT_BAD_INPUT (3)   — Bad audio, unsupported format, file not found, invalid args
EXIT_GPU_ERROR (4)   — GPU/VRAM error (OOM, CUDA not available when required)
"""

from __future__ import annotations

EXIT_OK = 0
EXIT_GENERAL = 1
EXIT_MISSING_DEP = 2
EXIT_BAD_INPUT = 3
EXIT_GPU_ERROR = 4
