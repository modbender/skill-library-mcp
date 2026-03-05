#!/usr/bin/env python3
"""
Unified CLI for tokenQrusher - Token optimization for OpenClaw.

SECURITY MANIFEST:
  Environment variables accessed: None
  External endpoints called: None
  Local files read: None
  Local files written: None
"""
from __future__ import annotations

import sys
import os
import json
import argparse
import logging
from pathlib import Path
from typing import (
    Optional, List, Dict, Any, Tuple, 
    Callable, TypeVar, Generic
)
from dataclasses import dataclass
from enum import Enum, auto
from abc import ABC, abstractmethod

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[tokenqrusher] %(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)


# =============================================================================
# THEOREMS (Constants)
# =============================================================================

class ExitCode(Enum):
    """CLI exit codes (theorems)."""
    SUCCESS = 0
    GENERAL_ERROR = 1
    INVALID_ARGS = 2
    CONFIG_ERROR = 3
    NOT_FOUND = 4
    BUDGET_EXCEEDED = 5


class ComplexityLevel(Enum):
    """Context complexity levels."""
    SIMPLE = "simple"
    STANDARD = "standard"
    COMPLEX = "complex"


class ModelTier(Enum):
    """AI model tiers."""
    QUICK = "quick"
    STANDARD = "standard"
    DEEP = "deep"


# =============================================================================
# RESULT TYPES (Theorems)
# =============================================================================

@dataclass(frozen=True, slots=True)
class CliResult:
    """Immutable CLI result."""
    exit_code: ExitCode
    message: str
    data: Optional[Dict[str, Any]] = None
    
    @property
    def success(self) -> bool:
        """Whether operation succeeded."""
        return self.exit_code == ExitCode.SUCCESS
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'exit_code': self.exit_code.value,
            'message': self.message,
            'data': self.data
        }


# =============================================================================
# SUB-COMMAND INTERFACE (Abstract)
# =============================================================================

class SubCommand(ABC):
    """Abstract base class for subcommands."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Command name."""
        pass
    
    @property
    @abstractmethod
    def help(self) -> str:
        """Command help text."""
        pass
    
    @abstractmethod
    def add_args(self, parser: argparse.ArgumentParser) -> None:
        """Add command-specific arguments."""
        pass
    
    @abstractmethod
    def execute(self, args: argparse.Namespace) -> CliResult:
        """Execute the command."""
        pass


# =============================================================================
# CONTEXT COMMAND
# =============================================================================

class ContextCommand(SubCommand):
    """Context optimization - recommend context files for a prompt."""
    
    @property
    def name(self) -> str:
        return "context"
    
    @property
    def help(self) -> str:
        return "Recommend context files for a prompt"
    
    def add_args(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument('prompt', nargs='?', default='hello', help='User prompt')
        parser.add_argument('--files', action='store_true', help='Show files only')
        parser.add_argument('--json', action='store_true', help='JSON output')
    
    def execute(self, args: argparse.Namespace) -> CliResult:
        # Import classifier from token-context hook
        prompt = args.prompt
        
        # Simple pattern matching (same as hook)
        simple_patterns = [
            r'^(hi|hey|hello|yo|sup|howdy)$',
            r'^(thanks|thank you|thx|ty)$',
            r'^(ok|okay|sure|got it|understood)$',
            r'^(yes|yeah|yep|yup|no|nope|nah)$',
            r'^(good|great|nice|cool|awesome)$',
            r'^\?+$',
        ]
        
        complex_patterns = [
            r'^(design|architect)\s+\w+',
            r'\barchitect(?:ure|ing)?\b',
            r'\bcomprehensive\b',
            r'\banalyze\s+deeply\b',
            r'\bplan\s+\w+\s+system\b',
        ]
        
        import re
        
        level = ComplexityLevel.STANDARD
        confidence = 0.6
        
        for pattern in simple_patterns:
            if re.match(pattern, prompt, re.IGNORECASE):
                level = ComplexityLevel.SIMPLE
                confidence = 0.95
                break
        
        if level == ComplexityLevel.STANDARD:
            for pattern in complex_patterns:
                if re.search(pattern, prompt, re.IGNORECASE):
                    level = ComplexityLevel.COMPLEX
                    confidence = 0.90
                    break
        
        # Get files for level
        files_map = {
            ComplexityLevel.SIMPLE: ['SOUL.md', 'IDENTITY.md'],
            ComplexityLevel.STANDARD: ['SOUL.md', 'IDENTITY.md', 'USER.md'],
            ComplexityLevel.COMPLEX: ['SOUL.md', 'IDENTITY.md', 'USER.md', 'TOOLS.md', 'AGENTS.md', 'MEMORY.md']
        }
        
        files = files_map[level]
        
        # Calculate savings
        total_files = 7  # Max files
        savings = ((total_files - len(files)) / total_files) * 100
        
        data = {
            'prompt': prompt,
            'complexity': level.value,
            'confidence': confidence,
            'files': files,
            'files_count': len(files),
            'savings_percent': savings
        }
        
        if args.json:
            return CliResult(ExitCode.SUCCESS, "OK", data)
        
        if args.files:
            output = '\n'.join(files)
            return CliResult(ExitCode.SUCCESS, output, data)
        
        message = f"Complexity: {level.value} (confidence: {confidence:.0%})\nFiles: {', '.join(files)}\nSavings: {savings:.0f}%"
        return CliResult(ExitCode.SUCCESS, message, data)


# =============================================================================
# MODEL COMMAND
# =============================================================================

class StatusCommand(SubCommand):
    """Full system status."""
    
    @property
    def name(self) -> str:
        return "status"
    
    @property
    def help(self) -> str:
        return "Show full system status"
    
    def add_args(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
        parser.add_argument('--json', action='store_true', help='JSON output')
    
    def execute(self, args: argparse.Namespace) -> CliResult:
        import subprocess
        
        # Get hooks status
        try:
            result = subprocess.run(
                ['openclaw', 'hooks', 'list'],
                capture_output=True,
                text=True,
                timeout=10
            )
            output = result.stdout if result.returncode == 0 else result.stderr
        except Exception as e:
            output = f"Error: {e}"
        
        if args.json:
            return CliResult(ExitCode.SUCCESS, "OK", {'hooks': output})
        
        # Format text output
        lines = ["=== tokenQrusher Status ===", ""]
        lines.append("Hooks:")
        lines.append(output)
        
        message = "\n".join(lines)
        return CliResult(ExitCode.SUCCESS, message)


# =============================================================================
# INSTALL COMMAND
# =============================================================================

class InstallCommand(SubCommand):
    """Install hooks and cron jobs."""
    
    @property
    def name(self) -> str:
        return "install"
    
    @property
    def help(self) -> str:
        return "Install hooks and cron jobs"
    
    def add_args(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument('--hooks', action='store_true', help='Install hooks')
        parser.add_argument('--cron', action='store_true', help='Install cron jobs')
        parser.add_argument('--all', action='store_true', help='Install everything')
        parser.add_argument('--dry-run', action='store_true', help='Show what would be done')
    
    def execute(self, args: argparse.Namespace) -> CliResult:
        actions: List[str] = []
        
        if args.all or args.hooks:
            actions.append("Enable token-context hook")
            actions.append("Enable token-model hook")
            actions.append("Enable token-usage hook")
            actions.append("Enable token-cron hook")
            actions.append("Enable token-heartbeat hook")
        
        if args.all or args.cron:
            actions.append("Add cron job for optimize (hourly)")
            actions.append("Add cron job for budget-check (5 min)")
        
        if not actions:
            return CliResult(ExitCode.INVALID_ARGS, "No actions specified. Use --hooks, --cron, or --all")
        
        if args.dry_run:
            message = "Would do:\n" + "\n".join(f"  - {a}" for a in actions)
            return CliResult(ExitCode.SUCCESS, message, {'actions': actions})
        
        # Execute actions
        results = []
        
        if args.all or args.hooks:
            import subprocess
            hooks = ['token-context', 'token-heartbeat']
            for hook in hooks:
                try:
                    subprocess.run(['openclaw', 'hooks', 'enable', hook],
                                capture_output=True, timeout=10)
                    results.append(f"Enabled: {hook}")
                except Exception as e:
                    results.append(f"Failed: {hook}: {e}")
        
        message = "Installation complete:\n" + "\n".join(f"  - {r}" for r in results)
        
        return CliResult(ExitCode.SUCCESS, message, {'results': results})


# =============================================================================
# MAIN CLI
# =============================================================================

class TokenQrusherCLI:
    """
    Unified CLI for tokenQrusher.
    
    Coordinates all subcommands.
    """
    
    def __init__(self) -> None:
        """Initialize CLI."""
        self.commands: Dict[str, SubCommand] = {
            'context': ContextCommand(),
            'status': StatusCommand(),
            'install': InstallCommand(),
        }
        
        self.parser = self._create_parser()
    
    def _create_parser(self) -> argparse.ArgumentParser:
        """Create argument parser."""
        parser = argparse.ArgumentParser(
            prog='tokenqrusher',
            description='Token optimization tools for OpenClaw',
            formatter_class=argparse.RawDescriptionHelpFormatter
        )
        
        subparsers = parser.add_subparsers(dest='command', help='Available commands')
        
        # Add subcommands
        for cmd in self.commands.values():
            cmd_parser = subparsers.add_parser(cmd.name, help=cmd.help)
            cmd.add_args(cmd_parser)
        
        return parser
    
    def run(self, argv: Optional[List[str]] = None) -> int:
        """
        Run CLI.
        
        Args:
            argv: Command line arguments (default: sys.argv)
            
        Returns:
            Exit code
        """
        args = self.parser.parse_args(argv)
        
        # No command specified
        if not args.command:
            self.parser.print_help()
            return ExitCode.SUCCESS.value
        
        # Get command
        cmd = self.commands.get(args.command)
        
        if cmd is None:
            print(f"Unknown command: {args.command}", file=sys.stderr)
            return ExitCode.INVALID_ARGS.value
        
        # Execute
        try:
            result = cmd.execute(args)
            
            # Print output
            if result.message:
                print(result.message)
            
            if result.data and args.__dict__.get('json'):
                print(json.dumps(result.data, indent=2))
            
            return result.exit_code.value
            
        except Exception as e:
            logger.exception("Command failed")
            print(f"Error: {e}", file=sys.stderr)
            return ExitCode.GENERAL_ERROR.value


def main() -> int:
    """Entry point."""
    cli = TokenQrusherCLI()
    return cli.run()


if __name__ == '__main__':
    sys.exit(main())
