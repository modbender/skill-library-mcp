"""CLI output formatters."""

from typing import List
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich import box

from crabukit.rules.patterns import Severity
from crabukit.scanner import ScanResult


class CLIFormatter:
    """Format scan results for CLI output."""
    
    SEVERITY_COLORS = {
        Severity.CRITICAL: "red",
        Severity.HIGH: "bright_red",
        Severity.MEDIUM: "yellow",
        Severity.LOW: "blue",
        Severity.INFO: "dim",
    }
    
    SEVERITY_ICONS = {
        Severity.CRITICAL: "🔴",
        Severity.HIGH: "🟠",
        Severity.MEDIUM: "🟡",
        Severity.LOW: "🔵",
        Severity.INFO: "⚪",
    }
    
    def __init__(self):
        self.console = Console()
    
    def print_report(self, result: ScanResult):
        """Print a full scan report."""
        self._print_header(result)
        self._print_summary(result)
        self._print_findings(result)
        self._print_recommendation(result)
    
    def _print_header(self, result: ScanResult):
        """Print report header."""
        self.console.print()
        self.console.print(Panel.fit(
            f"[bold cyan]🔒 Crabukit Security Report[/bold cyan]\n"
            f"[dim]v0.1.0 - OpenClaw Skill Scanner[/dim]",
            border_style="cyan"
        ))
        self.console.print()
        
        # Basic info
        self.console.print(f"[bold]Skill:[/bold] {result.skill_name}")
        self.console.print(f"[bold]Path:[/bold] {result.skill_path}")
        self.console.print(f"[bold]Files scanned:[/bold] {result.files_scanned}")
        
        # Show external scanner info
        external_findings = [f for f in result.findings if f.file_path == "external_scan"]
        if external_findings:
            scanners = set()
            for f in external_findings:
                if "CLAWDEX" in f.rule_id:
                    scanners.add("Clawdex")
                elif "EXTERNAL_" in f.rule_id:
                    scanners.add("External")
            if scanners:
                self.console.print(f"[bold green]✓ External scanners:[/bold green] {', '.join(scanners)}")
        
        self.console.print()
    
    def _print_summary(self, result: ScanResult):
        """Print severity summary."""
        if result.errors:
            for error in result.errors:
                self.console.print(f"[red]Error: {error}[/red]")
            self.console.print()
        
        # Count by severity
        counts = {
            Severity.CRITICAL: len(result.findings_by_severity(Severity.CRITICAL)),
            Severity.HIGH: len(result.findings_by_severity(Severity.HIGH)),
            Severity.MEDIUM: len(result.findings_by_severity(Severity.MEDIUM)),
            Severity.LOW: len(result.findings_by_severity(Severity.LOW)),
            Severity.INFO: len(result.findings_by_severity(Severity.INFO)),
        }
        
        total = sum(counts.values())
        
        if total == 0:
            self.console.print(Panel(
                "[bold green]✓ No security issues found![/bold green]",
                border_style="green"
            ))
            return
        
        # Create summary table
        table = Table(box=box.SIMPLE, show_header=False)
        table.add_column("Severity", style="bold")
        table.add_column("Count", justify="right")
        
        for severity in [Severity.CRITICAL, Severity.HIGH, Severity.MEDIUM, Severity.LOW, Severity.INFO]:
            count = counts[severity]
            if count > 0:
                color = self.SEVERITY_COLORS[severity]
                icon = self.SEVERITY_ICONS[severity]
                table.add_row(
                    f"[{color}]{icon} {severity.value.upper()}[/{color}]",
                    f"[{color}]{count}[/{color}]"
                )
        
        # Risk score panel
        risk_color = self._risk_color(result.risk_level)
        score_panel = Panel(
            f"[bold {risk_color}]{result.risk_level}[/bold {risk_color}]\n"
            f"[dim]Score: {result.score}/100[/dim]",
            title="Risk Level",
            border_style=risk_color,
            width=20
        )
        
        self.console.print(table)
        self.console.print()
        self.console.print(score_panel)
        self.console.print()
    
    def _print_findings(self, result: ScanResult):
        """Print detailed findings."""
        if not result.findings:
            return
        
        self.console.print("[bold]Detailed Findings:[/bold]")
        self.console.print()
        
        current_severity = None
        
        for finding in result.findings:
            # Print severity header when it changes
            if finding.severity != current_severity:
                current_severity = finding.severity
                color = self.SEVERITY_COLORS[current_severity]
                icon = self.SEVERITY_ICONS[current_severity]
                self.console.print(f"\n[{color}]{icon} {current_severity.value.upper()}[/{color}]")
            
            # Print finding
            color = self.SEVERITY_COLORS[finding.severity]
            self.console.print(f"  [{color}]→ {finding.title}[/{color}]")
            self.console.print(f"    [dim]File: {finding.file_path}:{finding.line_number}[/dim]")
            self.console.print(f"    {finding.description}")
            
            if finding.code_snippet:
                snippet = finding.code_snippet[:80] + "..." if len(finding.code_snippet) > 80 else finding.code_snippet
                self.console.print(f"    [dim]Code: {snippet}[/dim]")
            
            if finding.remediation:
                self.console.print(f"    [green]Fix: {finding.remediation}[/green]")
            
            self.console.print()
    
    def _print_recommendation(self, result: ScanResult):
        """Print final recommendation."""
        if result.risk_level == "CRITICAL":
            msg = "[bold red]Do not install this skill. Critical security issues found.[/bold red]"
        elif result.risk_level == "HIGH":
            msg = "[bold yellow]High risk - review carefully before installing.[/bold yellow]"
        elif result.risk_level == "MEDIUM":
            msg = "[bold yellow]Medium risk - review findings before installing.[/bold yellow]"
        elif result.risk_level == "LOW":
            msg = "[bold blue]Low risk - minor issues found.[/bold blue]"
        else:
            msg = "[bold green]✓ Safe to install - no issues found.[/bold green]"
        
        self.console.print(Panel(msg, border_style="default"))
        self.console.print()
    
    def _risk_color(self, level: str) -> str:
        """Get color for risk level."""
        colors = {
            "CRITICAL": "red",
            "HIGH": "bright_red",
            "MEDIUM": "yellow",
            "LOW": "blue",
            "CLEAN": "green",
        }
        return colors.get(level, "white")
