"""CLI entry point for crabukit."""

import subprocess
import tempfile
import shutil
import sys
from pathlib import Path
from typing import Optional

import click

from crabukit.scanner import SkillScanner
from crabukit.formatters.cli_table import CLIFormatter


@click.group()
@click.version_option(version="0.1.0", prog_name="crabukit")
def cli():
    """🔒 Crabukit - Security scanner for OpenClaw skills.
    
    Analyze skills for security vulnerabilities, dangerous permissions,
    and malicious code patterns before installation.
    
    Examples:
        crabukit scan ./my-skill/
        crabukit scan /opt/homebrew/lib/node_modules/clawdbot/skills/unknown-skill
        crabukit scan ./skill --fail-on=high
        crabukit install youtube-summarize
    """
    pass


@cli.command()
@click.argument('skill_path', type=click.Path(exists=True))
@click.option('--fail-on', 
              type=click.Choice(['critical', 'high', 'medium', 'low', 'info'], case_sensitive=False),
              default=None,
              help='Exit with error code if findings at this severity or higher are found')
@click.option('--format', 
              type=click.Choice(['table', 'json', 'sarif'], case_sensitive=False),
              default='table',
              help='Output format')
def scan(skill_path: str, fail_on: Optional[str], format: str):
    """Scan a skill for security issues.
    
    SKILL_PATH is the path to the skill directory to analyze.
    """
    scanner = SkillScanner(skill_path)
    result = scanner.scan()
    
    # Output results
    if format == 'table':
        formatter = CLIFormatter()
        formatter.print_report(result)
    elif format == 'json':
        import json
        # Use the scanner's to_dict method for complete output
        click.echo(json.dumps(result.to_dict(), indent=2))
    
    # Determine exit code
    if fail_on:
        severity_order = {
            'critical': 4,
            'high': 3,
            'medium': 2,
            'low': 1,
            'info': 0,
        }
        threshold = severity_order.get(fail_on.lower(), 0)
        
        for finding in result.findings:
            finding_level = severity_order.get(finding.severity.value, -1)
            if finding_level >= threshold:
                sys.exit(1)
    
    sys.exit(0)


@cli.command()
@click.argument('skill_name')
@click.option('--fail-on', 
              type=click.Choice(['critical', 'high', 'medium', 'low'], case_sensitive=False),
              default='high',
              help='Severity level to fail on (default: high)')
@click.option('--yes', '-y', is_flag=True, help='Skip confirmation prompt')
def install(skill_name: str, fail_on: str, yes: bool):
    """Safely install a skill from ClawHub with security scanning.
    
    Downloads the skill, scans it with Clawdex + Crabukit, and only installs
    if security checks pass.
    
    SKILL_NAME is the name of the skill to install from ClawHub.
    
    Examples:
        crabukit install youtube-summarize
        crabukit install youtube-summarize --fail-on=critical
        crabukit install some-skill -y
    """
    import os
    
    click.echo(f"🔒 Crabukit Safe Install: {skill_name}")
    click.echo()
    
    # Create temp directory
    temp_dir = tempfile.mkdtemp(prefix="crabukit-install-")
    workdir = Path(temp_dir)
    skills_dir = workdir / "skills"
    skills_dir.mkdir(exist_ok=True)
    
    try:
        # Step 1: Download
        click.echo("⬇️  Step 1: Downloading skill from ClawHub...")
        env = os.environ.copy()
        env["CLAWDHUB_WORKDIR"] = str(workdir)
        
        result = subprocess.run(
            ["clawdhub", "install", skill_name],
            capture_output=True,
            text=True,
            env=env
        )
        
        if result.returncode != 0 and "already exists" not in result.stderr.lower():
            click.echo(f"❌ Failed to download skill: {skill_name}")
            click.echo(f"Error: {result.stderr}")
            return 1
        
        skill_path = skills_dir / skill_name
        if not skill_path.exists():
            # Try alternate location
            skill_path = workdir / skill_name
        
        if not skill_path.exists():
            click.echo("❌ Skill not found in temp directory after download")
            return 1
        
        click.echo(f"✓ Downloaded to: {skill_path}")
        click.echo()
        
        # Step 2: Security scan
        click.echo("🔍 Step 2: Running security scan...")
        click.echo()
        click.echo("   Layer 1: Checking Clawdex database (known malicious skills)...")
        click.echo("   Layer 2: Running Crabukit behavior analysis (zero-day detection)...")
        click.echo()
        
        scanner = SkillScanner(str(skill_path))
        scan_result = scanner.scan()
        
        # Show results
        formatter = CLIFormatter()
        formatter.print_report(scan_result)
        
        # Check if passed
        severity_order = {'critical': 4, 'high': 3, 'medium': 2, 'low': 1}
        threshold = severity_order.get(fail_on.lower(), 3)
        
        failed = any(
            severity_order.get(f.severity.value, 0) >= threshold 
            for f in scan_result.findings 
            if f.severity.value != 'info'
        )
        
        if failed:
            click.echo()
            click.echo("❌ Security check FAILED")
            click.echo(f"⚠️  Installation blocked (fail-on={fail_on})")
            click.echo()
            click.echo("To install anyway (not recommended):")
            click.echo(f"  clawdhub install {skill_name}")
            return 1
        
        click.echo()
        click.echo("✅ Security check passed!")
        click.echo()
        
        # Step 3: Confirm and install
        if not yes:
            click.confirm("📦 Install this skill?", abort=True)
        
        click.echo("📦 Installing skill to workspace...")
        result = subprocess.run(
            ["clawdhub", "install", skill_name],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            click.echo()
            click.echo(f"🎉 Successfully installed {skill_name}!")
            return 0
        else:
            click.echo()
            click.echo("❌ Installation failed")
            if result.stderr:
                click.echo(f"Error: {result.stderr}")
            return 1
            
    finally:
        # Cleanup
        shutil.rmtree(temp_dir, ignore_errors=True)


@cli.command()
def list_rules():
    """List all detection rules."""
    from crabukit.rules.patterns import (
        PYTHON_DANGEROUS_CALLS,
        PYTHON_SUBPROCESS_PATTERNS,
        BASH_PATTERNS,
        SECRET_PATTERNS,
    )
    
    click.echo("🔒 Crabukit Detection Rules")
    click.echo()
    
    click.echo("[Python Rules]")
    for name in PYTHON_DANGEROUS_CALLS:
        click.echo(f"  - {name}()")
    
    click.echo()
    click.echo("[Subprocess Rules]")
    for name in PYTHON_SUBPROCESS_PATTERNS:
        click.echo(f"  - {name}()")
    
    click.echo()
    click.echo("[Secret Detection]")
    for name in SECRET_PATTERNS:
        click.echo(f"  - {name}")
    
    click.echo()
    click.echo("[Bash Patterns]")
    for name in BASH_PATTERNS:
        click.echo(f"  - {name}")


def main():
    """Entry point."""
    cli()


if __name__ == '__main__':
    main()
