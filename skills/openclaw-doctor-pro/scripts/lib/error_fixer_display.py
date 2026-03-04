"""Display helpers for error-fixer CLI output."""
from __future__ import annotations

from rich.console import Console
from rich.panel import Panel


def display_suggestions(
    console: Console,
    suggestions: list,
    title: str,
    header: str,
    border_color: str
) -> None:
    """Display skill suggestions panel.

    Args:
        console: Rich console
        suggestions: List of suggestion objects with priority/reason/benefit/install_command
        title: Panel title
        header: Header text
        border_color: Panel border color
    """
    console.print("\n")
    content = []
    content.append(f"[bold {border_color}]{header}[/bold {border_color}]\n")

    for sug in suggestions:
        priority_color = "red" if sug.priority == "HIGH" else "yellow"
        content.append(
            f"[{priority_color} bold]🔧 {sug.skill_name}[/{priority_color} bold] "
            f"[{priority_color}]{sug.priority} PRIORITY[/{priority_color}]"
        )
        content.append(f"   Reason: {sug.reason}")
        content.append(f"   Benefit: {sug.benefit}")
        content.append(f"   [dim]Install: {sug.install_command}[/dim]\n")

    panel = Panel(
        "\n".join(content),
        title=f"[bold]{title}[/bold]",
        border_style=border_color
    )
    console.print(panel)


def display_integration_suggestions(
    console: Console,
    suggestions: list,
    title: str,
    header: str,
    border_color: str
) -> None:
    """Display integration suggestions panel.

    Args:
        console: Rich console
        suggestions: List of integration suggestion objects
        title: Panel title
        header: Header text
        border_color: Panel border color
    """
    console.print("\n")
    content = []
    content.append(f"[bold {border_color}]{header}[/bold {border_color}]\n")

    for sug in suggestions:
        priority_color = "red" if sug.priority == "HIGH" else "yellow"
        content.append(
            f"[{priority_color} bold]🐙 {sug.skill_name}[/{priority_color} bold] "
            f"[{priority_color}]{sug.priority} PRIORITY[/{priority_color}]"
        )
        content.append(f"   Reason: {sug.reason}")
        content.append(f"   Benefit: {sug.benefit}")
        content.append(f"   [dim]Install: {sug.install_command}[/dim]")
        if hasattr(sug, 'config_example') and sug.config_example:
            content.append(f"   [dim]Config: {sug.config_example}[/dim]")
        content.append("")

    panel = Panel(
        "\n".join(content),
        title=f"[bold]{title}[/bold]",
        border_style=border_color
    )
    console.print(panel)
