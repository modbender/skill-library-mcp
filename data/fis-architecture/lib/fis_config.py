"""
FIS Configuration - Shared hub path configuration
共享中心路径配置 - 可自定义
"""

from pathlib import Path

# Default shared hub name - can be customized
# Users can change this to their project name
DEFAULT_SHARED_HUB_NAME = "fis-hub"

# Or use a more descriptive name for your project:
# DEFAULT_SHARED_HUB_NAME = "my-project-hub"
# DEFAULT_SHARED_HUB_NAME = "research-center"
# DEFAULT_SHARED_HUB_NAME = "team-collaboration"

def get_shared_hub_path(hub_name: str = None) -> Path:
    """
    Get the shared hub path
    
    Args:
        hub_name: Custom hub name. If None, uses DEFAULT_SHARED_HUB_NAME
    
    Returns:
        Path to shared hub directory
    """
    name = hub_name or DEFAULT_SHARED_HUB_NAME
    return Path.home() / ".openclaw" / name

def set_shared_hub_name(name: str):
    """
    Set the shared hub name for this session
    
    Args:
        name: Name of the shared hub directory
    """
    global DEFAULT_SHARED_HUB_NAME
    DEFAULT_SHARED_HUB_NAME = name

# For backward compatibility - will be deprecated
LEGACY_SHARED_HUB = Path.home() / ".openclaw" / "fis-hub"
