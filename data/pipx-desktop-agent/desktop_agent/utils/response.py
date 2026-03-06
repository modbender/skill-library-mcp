from datetime import datetime, timezone
from typing import Any, Optional
from pydantic import BaseModel, Field

class CommandResponse(BaseModel):
    success: bool = Field(..., description="Whether the command succeeded")
    command: str = Field(..., description="Full command path (e.g., 'mouse.move')")
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="ISO 8601 timestamp in UTC"
    )
    duration_ms: Optional[int] = Field(None, description="Execution time in milliseconds")
    data: Optional[dict[str, Any]] = Field(None, description="Command-specific data")
    error: Optional[dict[str, Any]] = Field(None, description="Error details if failed")

    def to_json(self) -> str:
        return self.model_dump_json()

    def to_text(self) -> str:
        if self.success:
            if self.data:
                if "position" in self.data:
                    pos = self.data["position"]
                    return f"Position: ({pos.get('x', '?')}, {pos.get('y', '?')})"
                if "text" in self.data:
                    return self.data["text"]
                if "size" in self.data:
                    s = self.data["size"]
                    return f"Size: {s.get('width', '?')}x{s.get('height', '?')}"
                if "message" in self.data:
                    return self.data["message"]
                if "windows" in self.data:
                    count = len(self.data["windows"])
                    return f"Found {count} window(s)"
                if "result" in self.data:
                    return str(self.data["result"])
            return "OK"
        else:
            error_msg = self.error.get("message", "Unknown error") if self.error else "Unknown error"
            return f"Error: {error_msg}"

    def print(self) -> None:
        print(self.to_json())

    @classmethod
    def success_response(
        cls,
        command: str,
        data: Optional[dict[str, Any]] = None,
        duration_ms: Optional[int] = None,
    ) -> "CommandResponse":
        return cls(
            success=True,
            command=command,
            duration_ms=duration_ms,
            data=data,
            error=None,
        )

    @classmethod
    def error_response(
        cls,
        command: str,
        code: str,
        message: str,
        details: Optional[dict[str, Any]] = None,
        duration_ms: Optional[int] = None,
    ) -> "CommandResponse":
        return cls(
            success=False,
            command=command,
            duration_ms=duration_ms,
            data=None,
            error={
                "code": code,
                "message": message,
                "details": details,
            },
        )
