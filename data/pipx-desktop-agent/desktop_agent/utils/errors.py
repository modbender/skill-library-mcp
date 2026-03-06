from enum import Enum
from typing import Optional, Any

class ErrorCode(Enum):
    SUCCESS = 0
    INVALID_ARGUMENT = 1
    COORDINATES_OUT_OF_BOUNDS = 2
    IMAGE_NOT_FOUND = 3
    WINDOW_NOT_FOUND = 4
    OCR_FAILED = 5
    APPLICATION_NOT_FOUND = 6
    PERMISSION_DENIED = 7
    PLATFORM_NOT_SUPPORTED = 8
    TIMEOUT = 9
    UNKNOWN_ERROR = 99

    def to_string(self) -> str:
        return self.name.lower()

    @classmethod
    def from_exception(cls, exc: Exception) -> "ErrorCode":
        exc_type = type(exc).__name__.lower()
        mapping = {
            "valueerror": cls.INVALID_ARGUMENT,
            "typeerror": cls.INVALID_ARGUMENT,
            "oserror": cls.PERMISSION_DENIED,
            "filenotfounderror": cls.IMAGE_NOT_FOUND,
            "timeouterror": cls.TIMEOUT,
        }
        return mapping.get(exc_type, cls.UNKNOWN_ERROR)

class DesktopAgentError(Exception):
    def __init__(
        self,
        code: ErrorCode,
        message: str,
        details: Optional[dict] = None,
        recoverable: bool = True,
    ):
        self.code = code
        self.message = message
        self.details = details or {}
        self.recoverable = recoverable
        super().__init__(f"[{code.to_string()}] {message}")

    def to_dict(self) -> dict[str, Any]:
        return {
            "code": self.code.to_string(),
            "message": self.message,
            "details": self.details,
            "recoverable": self.recoverable,
        }

    def exit_code(self) -> int:
        return self.code.value if self.code != ErrorCode.SUCCESS else 0
