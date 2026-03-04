"""
NIMA Core Exceptions

Custom exception hierarchy for NIMA error handling.

Created: 2026-02-13
"""

from typing import Optional, List


class NimaError(Exception):
    """Base exception for all nima-core errors."""
    pass


class AffectVectorError(NimaError):
    """Raised when an affect vector is invalid."""
    pass


class InvalidAffectNameError(AffectVectorError):
    """Raised when an unknown affect name is used."""
    
    def __init__(self, name: str, valid_names: Optional[List[str]] = None):
        self.name = name
        self.valid_names = valid_names
        msg = f"Unknown affect: '{name}'"
        if valid_names:
            msg += f". Valid affects: {', '.join(valid_names)}"
        super().__init__(msg)


class AffectValueError(AffectVectorError):
    """Raised when an affect value is out of range."""
    
    def __init__(self, affect: str, value: float):
        self.affect = affect
        self.value = value
        super().__init__(
            f"Affect '{affect}' value must be in [0, 1], got {value}"
        )


class BaselineValidationError(AffectVectorError):
    """Raised when a baseline vector is invalid."""
    
    def __init__(self, reason: str):
        super().__init__(f"Invalid baseline: {reason}")


class StatePersistenceError(NimaError):
    """Raised when state cannot be saved or loaded."""
    
    def __init__(self, path: str, operation: str, reason: str):
        self.path = path
        self.operation = operation
        self.reason = reason
        super().__init__(
            f"Failed to {operation} state at '{path}': {reason}"
        )


class ProfileNotFoundError(NimaError):
    """Raised when a requested personality profile doesn't exist."""
    
    def __init__(self, profile_name: str, available: Optional[List[str]] = None):
        self.profile_name = profile_name
        self.available = available
        msg = f"Profile not found: '{profile_name}'"
        if available:
            msg += f". Available: {', '.join(available)}"
        super().__init__(msg)


class EmotionDetectionError(NimaError):
    """Raised when emotion detection fails."""
    pass


class ArchetypeError(NimaError):
    """Raised for archetype-related errors."""
    pass


class UnknownArchetypeError(ArchetypeError):
    """Raised when an unknown archetype is requested."""
    
    def __init__(self, name: str, available: Optional[List[str]] = None):
        self.name = name
        self.available = available
        msg = f"Unknown archetype: '{name}'"
        if available:
            msg += f". Available: {', '.join(available)}"
        super().__init__(msg)