#!/usr/bin/env python3
"""
Input Validation

Validates Discord snowflake IDs and agent identifiers.
"""

import re


SNOWFLAKE_RE = re.compile(r'^\d{17,20}$')
AGENT_ID_RE = re.compile(r'^[a-z0-9_-]{1,32}$')


def validate_snowflake(value: str, label: str = "ID") -> str:
    """Validate a Discord snowflake ID.
    
    Args:
        value: ID string to validate
        label: Human-readable label for error messages
        
    Returns:
        The validated ID string
        
    Raises:
        ValueError: If the ID is invalid
    """
    if not SNOWFLAKE_RE.match(value):
        raise ValueError(f"Invalid {label}: '{value}' (expected 17-20 digit snowflake)")
    return value


def validate_agent_id(value: str) -> str:
    """Validate an agent identifier.
    
    Args:
        value: Agent ID to validate
        
    Returns:
        The validated agent ID
        
    Raises:
        ValueError: If the agent ID is invalid
    """
    if not AGENT_ID_RE.match(value):
        raise ValueError(
            f"Invalid agent ID: '{value}' (expected lowercase alphanumeric, hyphens, underscores, max 32 chars)"
        )
    return value
