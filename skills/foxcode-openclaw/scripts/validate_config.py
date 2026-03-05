#!/usr/bin/env python3
"""
Foxcode OpenClaw Configuration Validator

Validates that your OpenClaw configuration is correct and working.

Usage:
    python3 scripts/validate_config.py                    # Validate default config
    python3 scripts/validate_config.py --config PATH    # Validate specific config
    python3 scripts/validate_config.py --json            # JSON output
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

# Default config paths to search
DEFAULT_CONFIG_PATHS = [
    Path.home() / ".openclaw" / "openclaw.json",
]

# Valid endpoint URLs
VALID_ENDPOINTS = [
    "https://code.newcli.com/claude",
    "https://code.newcli.com/claude/super",
    "https://code.newcli.com/claude/ultra",
    "https://code.newcli.com/claude/aws",
    "https://code.newcli.com/claude/droid",
]

# Valid models
VALID_MODELS = [
    "claude-opus-4-5-20251101",
    "claude-sonnet-4-5-20251101",
    "claude-haiku-4-5-20251101",
]


class ValidationResult:
    """Stores validation results."""

    def __init__(self):
        self.checks: List[Tuple[str, bool, str]] = []
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def add_check(self, name: str, passed: bool, message: str = ""):
        self.checks.append((name, passed, message))
        if not passed:
            self.errors.append(f"{name}: {message}")

    def add_warning(self, message: str):
        self.warnings.append(message)

    @property
    def all_passed(self) -> bool:
        return all(passed for _, passed, _ in self.checks)

    def print_report(self):
        """Print human-readable validation report."""
        print("=" * 60)
        print("Foxcode Configuration Validation Report")
        print("=" * 60)
        print()

        for name, passed, message in self.checks:
            symbol = "✓" if passed else "✗"
            print(f"{symbol} {name}")
            if message:
                print(f"  {message}")

        print()

        if self.warnings:
            print("Warnings:")
            for warning in self.warnings:
                print(f"  ⚠ {warning}")
            print()

        if self.all_passed:
            print("=" * 60)
            print("✓ All checks passed! Configuration is valid.")
            print("=" * 60)
        else:
            print("=" * 60)
            print("✗ Some checks failed. Please review errors above.")
            print("=" * 60)

    def to_json(self) -> Dict:
        """Convert to JSON-serializable dict."""
        return {
            "valid": self.all_passed,
            "checks": [
                {"name": name, "passed": passed, "message": message}
                for name, passed, message in self.checks
            ],
            "warnings": self.warnings,
            "errors": self.errors
        }


def find_config_file(specified_path: Optional[str] = None) -> Optional[Path]:
    """Find the configuration file."""
    if specified_path:
        path = Path(specified_path)
        if path.exists():
            return path
        return None

    for path in DEFAULT_CONFIG_PATHS:
        if path.exists():
            return path

    return None


def validate_json_syntax(config_path: Path) -> Tuple[bool, Optional[Dict], str]:
    """Validate that the file is valid JSON."""
    try:
        with open(config_path, 'r') as f:
            content = f.read()
            config = json.loads(content)
            return True, config, ""
    except json.JSONDecodeError as e:
        return False, None, f"Invalid JSON: {e}"
    except Exception as e:
        return False, None, f"Cannot read file: {e}"


def validate_required_fields(config: Dict) -> Tuple[bool, str]:
    """Validate that required fields are present in OpenClaw format."""
    # Check for OpenClaw nested structure
    if "models" not in config:
        return False, "Missing 'models' section"
    
    if "providers" not in config.get("models", {}):
        return False, "Missing 'models.providers' section"
    
    providers = config["models"]["providers"]
    
    # Check for foxcode provider
    if "foxcode" not in providers:
        return True, "No foxcode provider found (may use other providers)"
    
    foxcode = providers["foxcode"]
    
    # Check required fields in foxcode provider
    if "baseUrl" not in foxcode:
        return False, "Missing 'baseUrl' in foxcode provider"
    
    if "apiKey" not in foxcode:
        return False, "Missing 'apiKey' in foxcode provider"
    
    return True, "All required fields present in foxcode provider"


def validate_base_url(config: Dict) -> Tuple[bool, str]:
    """Validate the base URL from foxcode provider."""
    providers = config.get("models", {}).get("providers", {})
    foxcode = providers.get("foxcode", {})
    base_url = foxcode.get("baseUrl", "")

    if not base_url:
        return False, "baseUrl is empty"

    if base_url not in VALID_ENDPOINTS:
        # Check if it's a valid URL format
        if not re.match(r'^https?://[^\s/]+', base_url):
            return False, f"Invalid URL format: {base_url}"

        # It's a custom URL, just warn
        return True, f"Custom endpoint (not in known list): {base_url}"

    return True, f"Valid endpoint: {base_url}"


def validate_api_token(config: Dict) -> Tuple[bool, str]:
    """Validate API token format from foxcode provider."""
    providers = config.get("models", {}).get("providers", {})
    foxcode = providers.get("foxcode", {})
    api_key = foxcode.get("apiKey", "")

    if not api_key:
        return False, "apiKey is empty"

    # Check for environment variable reference
    if api_key.startswith("${") and api_key.endswith("}"):
        env_var = api_key[2:-1]
        if env_var in os.environ:
            return True, f"Using environment variable: {env_var}"
        else:
            return False, f"Environment variable not set: {env_var}"

    # Validate token format
    if not re.match(r'^sk-[a-zA-Z0-9_-]+$', api_key):
        return False, "Invalid token format (should start with 'sk-')"

    if len(api_key) < 20:
        return False, "Token too short"

    return True, "Token format valid"


def validate_model(config: Dict) -> Tuple[bool, str]:
    """Validate the primary model."""
    model = config.get("model", "")

    if not model:
        return True, "No model specified (will use provider default)"

    if model not in VALID_MODELS:
        return True, f"Custom model: {model}"

    return True, f"Valid model: {model}"


def validate_fallback_models(config: Dict) -> Tuple[bool, str]:
    """Validate fallback models configuration."""
    fallbacks = config.get("fallback_models", [])

    if not fallbacks:
        return True, "No fallback models configured"

    if not isinstance(fallbacks, list):
        return False, "fallback_models must be an array"

    invalid_models = [m for m in fallbacks if m not in VALID_MODELS]
    if invalid_models:
        return True, f"Configured {len(fallbacks)} fallbacks (some custom: {', '.join(invalid_models)})"

    return True, f"Valid fallback models: {', '.join(fallbacks)}"


def test_endpoint_connection(config: Dict) -> Tuple[bool, str]:
    """Test connection to the foxcode endpoint."""
    providers = config.get("models", {}).get("providers", {})
    foxcode = providers.get("foxcode", {})
    base_url = foxcode.get("baseUrl", "")
    api_key = foxcode.get("apiKey", "")

    # Resolve environment variable if needed
    if api_key.startswith("${") and api_key.endswith("}"):
        env_var = api_key[2:-1]
        api_key = os.environ.get(env_var, "")
        if not api_key:
            return False, f"Cannot test: environment variable {env_var} not set"

    try:
        req = Request(base_url, method="HEAD")
        req.add_header("Authorization", f"Bearer {api_key}")
        req.add_header("User-Agent", "Foxcode-Validator/1.0")

        with urlopen(req, timeout=15) as response:
            return True, f"Connection successful (status: {response.getcode()})"

    except HTTPError as e:
        if e.code == 401:
            return False, "Authentication failed - check your API token"
        elif e.code in [404, 405]:
            return True, f"Endpoint reachable (status: {e.code})"
        else:
            return False, f"HTTP error: {e.code}"

    except URLError as e:
        return False, f"Cannot connect: {e.reason}"

    except Exception as e:
        return False, f"Connection error: {str(e)}"


def check_file_permissions(config_path: Path) -> Tuple[bool, str]:
    """Check that config file has appropriate permissions."""
    try:
        stat = config_path.stat()
        mode = stat.st_mode

        # Check if world-readable
        if mode & 0o044:
            return False, "File is world-readable (should be 600)"

        # Check if group-readable
        if mode & 0o040:
            return True, "File is group-readable (600 recommended)"

        return True, "Permissions secure (600)"

    except Exception as e:
        return False, f"Cannot check permissions: {e}"


def validate_config(config_path: Path, result: ValidationResult):
    """Run all validation checks."""
    # 1. JSON Syntax
    valid_json, config, error_msg = validate_json_syntax(config_path)
    result.add_check("JSON Syntax", valid_json, error_msg if not valid_json else "Valid JSON")

    if not valid_json or config is None:
        return

    # 2. Required Fields
    passed, msg = validate_required_fields(config)
    result.add_check("Required Fields", passed, msg)

    # 3. Base URL
    passed, msg = validate_base_url(config)
    result.add_check("Base URL", passed, msg)

    # 4. API Token
    passed, msg = validate_api_token(config)
    result.add_check("API Token", passed, msg)

    # 5. Primary Model
    passed, msg = validate_model(config)
    result.add_check("Primary Model", passed, msg)

    # 6. Fallback Models
    passed, msg = validate_fallback_models(config)
    result.add_check("Fallback Models", passed, msg)

    # 7. File Permissions
    passed, msg = check_file_permissions(config_path)
    result.add_check("File Permissions", passed, msg)

    # 8. Connection Test (only if previous checks passed)
    if not result.errors:
        passed, msg = test_endpoint_connection(config)
        result.add_check("Endpoint Connection", passed, msg)
        if not passed:
            result.add_warning("Connection failed - OpenClaw may not work")


def main():
    parser = argparse.ArgumentParser(
        description="Validate Foxcode OpenClaw configuration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                    Validate default config location
  %(prog)s --config PATH    Validate specific config file
  %(prog)s --json           Output as JSON
        """
    )

    parser.add_argument(
        "--config",
        help="Path to specific config file to validate"
    )

    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON"
    )

    args = parser.parse_args()

    # Find config file
    config_path = find_config_file(args.config)

    if not config_path:
        print("Error: Could not find OpenClaw config file", file=sys.stderr)
        print("Searched locations:", file=sys.stderr)
        for path in DEFAULT_CONFIG_PATHS:
            print(f"  - {path}", file=sys.stderr)
        print("\nUse --config to specify a path:", file=sys.stderr)
        print(f"  {sys.argv[0]} --config /path/to/openclaw.json", file=sys.stderr)
        sys.exit(1)

    # Run validation
    result = ValidationResult()
    validate_config(config_path, result)

    # Output results
    if args.json:
        print(json.dumps(result.to_json(), indent=2))
    else:
        print(f"Config file: {config_path}")
        print()
        result.print_report()

    # Exit with appropriate code
    sys.exit(0 if result.all_passed else 1)


if __name__ == "__main__":
    main()
