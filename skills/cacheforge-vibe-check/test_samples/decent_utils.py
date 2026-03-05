"""Utility functions for data processing."""
from typing import List, Optional, Dict, Any
import logging
import hashlib

logger = logging.getLogger(__name__)

MAX_RETRIES = 3
DEFAULT_TIMEOUT = 30
HASH_ALGORITHM = "sha256"


class ValidationError(Exception):
    """Raised when input validation fails."""
    pass


def validate_email(email: str) -> bool:
    """Validate an email address format.
    
    Args:
        email: The email address to validate.
        
    Returns:
        True if the email is valid, False otherwise.
    """
    if not isinstance(email, str):
        raise ValidationError(f"Expected string, got {type(email).__name__}")
    
    if not email or len(email) > 254:
        return False
    
    parts = email.split("@")
    if len(parts) != 2:
        return False
    
    local_part, domain = parts
    if not local_part or not domain:
        return False
    
    if "." not in domain:
        return False
    
    return True


def hash_password(password: str, salt: Optional[str] = None) -> Dict[str, str]:
    """Hash a password with a salt using SHA-256.
    
    Args:
        password: The plaintext password to hash.
        salt: Optional salt. Generated if not provided.
        
    Returns:
        Dict with 'hash' and 'salt' keys.
        
    Raises:
        ValidationError: If password is empty or too short.
    """
    if not password:
        raise ValidationError("Password cannot be empty")
    
    if len(password) < 8:
        raise ValidationError("Password must be at least 8 characters")
    
    if salt is None:
        salt = hashlib.sha256(str(id(password)).encode()).hexdigest()[:16]
    
    salted = f"{salt}{password}".encode("utf-8")
    hashed = hashlib.sha256(salted).hexdigest()
    
    return {"hash": hashed, "salt": salt}


def retry_operation(
    func,
    max_retries: int = MAX_RETRIES,
    timeout: int = DEFAULT_TIMEOUT,
) -> Any:
    """Retry an operation with exponential backoff.
    
    Args:
        func: Callable to retry.
        max_retries: Maximum number of retry attempts.
        timeout: Timeout per attempt in seconds.
        
    Returns:
        The result of the function call.
        
    Raises:
        Exception: The last exception if all retries fail.
    """
    last_error = None
    
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as exc:
            last_error = exc
            logger.warning(
                "Attempt %d/%d failed: %s",
                attempt + 1,
                max_retries,
                str(exc),
            )
            if attempt < max_retries - 1:
                import time
                wait_time = 2 ** attempt
                time.sleep(wait_time)
    
    raise last_error


def safe_parse_json(raw: str) -> Optional[Dict]:
    """Safely parse a JSON string.
    
    Args:
        raw: The raw JSON string to parse.
        
    Returns:
        Parsed dict or None if parsing fails.
    """
    if not isinstance(raw, str):
        logger.error("Expected string input, got %s", type(raw).__name__)
        return None
    
    try:
        import json
        return json.loads(raw)
    except (json.JSONDecodeError, ValueError) as exc:
        logger.warning("Failed to parse JSON: %s", str(exc))
        return None
