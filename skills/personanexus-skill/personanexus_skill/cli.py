"""Minimal CLI for the PersonaNexus ClawHub Skill."""

from __future__ import annotations

import json
import os
import re
import uuid
from datetime import datetime
from pathlib import Path
from typing import Annotated

import typer
from pydantic import ValidationError
from rich.console import Console
from rich.table import Table

from personanexus_skill.compiler import CompilerError, compile_identity
from personanexus_skill.parser import ParseError, parse_identity_file
from personanexus_skill.types import TRAIT_ORDER
from personanexus_skill.validator import IdentityValidator

app = typer.Typer(
    name="personanexus-skill",
    help="PersonaNexus ClawHub Skill CLI -- validate, compile, and scaffold agent identities",
    add_completion=False,
)
console = Console()


# ---------------------------------------------------------------------------
# Security helpers (ported from main CLI)
# ---------------------------------------------------------------------------


def _sanitize_filename(name: str) -> str:
    """Sanitize a user-provided name into a safe filename component.

    Strips all characters except alphanumeric and underscores to prevent
    path traversal attacks.
    """
    safe = re.sub(r"[^a-zA-Z0-9_]", "_", name.lower()).strip("_")
    safe = re.sub(r"_+", "_", safe)
    return safe if safe else "agent"


def _atomic_write(path: Path, content: str) -> None:
    """Write content to a file atomically via temp-and-rename.

    On POSIX systems ``os.replace`` is atomic within the same filesystem,
    preventing partial writes from corrupting the target file.
    """
    tmp = path.with_suffix(path.suffix + ".tmp")
    try:
        tmp.write_text(content, encoding="utf-8")
        os.replace(str(tmp), str(path))
    except BaseException:
        tmp.unlink(missing_ok=True)
        raise


# ---------------------------------------------------------------------------
# validate command
# ---------------------------------------------------------------------------


@app.command()
def validate(
    file: Annotated[Path, typer.Argument(help="Path to PersonaNexus YAML file")],
    verbose: Annotated[
        bool, typer.Option("--verbose", "-v", help="Show extra validation details")
    ] = False,
    no_warnings: Annotated[
        bool, typer.Option("--no-warnings", help="Suppress warning messages")
    ] = False,
) -> None:
    """Parse and validate a PersonaNexus YAML identity file."""
    if not file.exists():
        console.print(f"[red]Error: File not found: {file}[/red]")
        raise typer.Exit(code=1)

    if not file.is_file():
        console.print(f"[red]Error: Not a file: {file}[/red]")
        raise typer.Exit(code=1)

    validator = IdentityValidator()

    try:
        result = validator.validate_file(file)
    except Exception as exc:
        console.print("[red]Validation failed with unexpected error:[/red]")
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(code=1)

    if result.errors:
        console.print(f"\n[red]Validation failed for {file}[/red]\n")
        for error in result.errors:
            console.print(f"  [red]* {error}[/red]")
        console.print()
        raise typer.Exit(code=1)

    if result.warnings and not no_warnings:
        console.print(f"\n[yellow]Warnings ({len(result.warnings)}):[/yellow]\n")
        for warning in result.warnings:
            severity_color = {
                "low": "dim yellow",
                "medium": "yellow",
                "high": "bold yellow",
            }.get(warning.severity, "yellow")
            prefix = f"[{warning.type}]" if verbose else ""
            location = f" ({warning.path})" if warning.path and verbose else ""
            console.print(
                f"  [{severity_color}]! {prefix}{location}"
                f" {warning.message}[/{severity_color}]"
            )
        console.print()

    console.print(f"[green]Validation successful: {file}[/green]")

    if verbose and result.identity:
        identity = result.identity
        console.print(f"\n[dim]Identity: {identity.metadata.id}[/dim]")
        console.print(f"[dim]Name: {identity.metadata.name}[/dim]")
        console.print(f"[dim]Version: {identity.metadata.version}[/dim]")
        console.print(f"[dim]Status: {identity.metadata.status.value}[/dim]")


# ---------------------------------------------------------------------------
# compile command
# ---------------------------------------------------------------------------


@app.command()
def compile(
    file: Annotated[Path, typer.Argument(help="Path to PersonaNexus YAML file")],
    target: Annotated[
        str,
        typer.Option(
            "--target",
            "-t",
            help="Compile target: text, anthropic, openai, openclaw, soul, json, markdown",
        ),
    ] = "text",
    output: Annotated[
        Path | None,
        typer.Option("--output", "-o", help="Output file path (defaults to stdout)"),
    ] = None,
    token_budget: Annotated[
        int,
        typer.Option("--token-budget", help="Estimated token budget for system prompt"),
    ] = 3000,
) -> None:
    """Compile an identity YAML into a system prompt or platform format."""
    if not file.exists():
        console.print(f"[red]Error: File not found: {file}[/red]")
        raise typer.Exit(code=1)

    if not file.is_file():
        console.print(f"[red]Error: Not a file: {file}[/red]")
        raise typer.Exit(code=1)

    valid_targets = ("text", "anthropic", "openai", "openclaw", "soul", "json", "markdown")
    if target not in valid_targets:
        console.print(
            f"[red]Error: Invalid target '{target}'."
            f" Must be one of: {', '.join(valid_targets)}[/red]"
        )
        raise typer.Exit(code=1)

    try:
        identity = parse_identity_file(file)
    except ParseError as exc:
        console.print(f"[red]Parse error: {exc}[/red]")
        raise typer.Exit(code=1)
    except ValidationError as exc:
        console.print("[red]Validation error:[/red]")
        for error in exc.errors():
            loc = " -> ".join(str(part) for part in error["loc"])
            console.print(f"  [red]* {loc}: {error['msg']}[/red]")
        raise typer.Exit(code=1)

    try:
        result = compile_identity(identity, target=target, token_budget=token_budget)
    except CompilerError as exc:
        console.print(f"[red]Compilation error: {exc}[/red]")
        raise typer.Exit(code=1)

    # Soul target produces two files (SOUL.md + STYLE.md)
    if target == "soul":
        if not isinstance(result, dict):
            console.print("[red]Soul compiler returned unexpected format[/red]")
            raise typer.Exit(code=1)
        stem = file.stem
        out_dir = output.parent if output else file.parent
        out_dir.mkdir(parents=True, exist_ok=True)
        soul_path = out_dir / f"{stem}.SOUL.md"
        style_path = out_dir / f"{stem}.STYLE.md"
        _atomic_write(soul_path, result["soul_md"])
        _atomic_write(style_path, result["style_md"])
        console.print(f"[green]Compiled {identity.metadata.name} -> {soul_path}[/green]")
        console.print(f"[green]Compiled {identity.metadata.name} -> {style_path}[/green]")
        return

    # Format output
    if isinstance(result, dict):
        output_text = json.dumps(result, indent=2, ensure_ascii=False)
    else:
        output_text = result

    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        _atomic_write(output, output_text)
        console.print(f"[green]Compiled {identity.metadata.name} -> {output}[/green]")
        console.print(f"[dim]Target: {target}[/dim]")
    else:
        console.print(output_text)


# ---------------------------------------------------------------------------
# init command
# ---------------------------------------------------------------------------


@app.command()
def init(
    name: Annotated[str, typer.Argument(help="Name for the new agent identity")],
    type: Annotated[
        str,
        typer.Option("--type", "-t", help="Template type: minimal or full"),
    ] = "minimal",
    output_dir: Annotated[
        Path,
        typer.Option("--output-dir", "-d", help="Directory to create the file in"),
    ] = Path("./agents"),
) -> None:
    """Scaffold a new agent identity YAML file with sensible defaults."""
    if type not in ("minimal", "full"):
        console.print(
            f"[red]Error: Invalid type '{type}'. Must be 'minimal' or 'full'[/red]"
        )
        raise typer.Exit(code=1)

    output_dir.mkdir(parents=True, exist_ok=True)

    filename = _sanitize_filename(name) + ".yaml"
    output_path = output_dir / filename

    if output_path.exists():
        overwrite = typer.confirm(f"File {output_path} already exists. Overwrite?")
        if not overwrite:
            console.print("[yellow]Cancelled[/yellow]")
            raise typer.Exit(code=0)

    unique_suffix = uuid.uuid4().hex[:8]
    agent_id = f"agt_{_sanitize_filename(name)}_{unique_suffix}"
    timestamp = datetime.now().isoformat()

    if type == "full":
        content = _generate_full_template(name, agent_id, timestamp)
    else:
        content = _generate_minimal_template(name, agent_id, timestamp)

    _atomic_write(output_path, content)

    console.print(f"\n[green]Created {type} identity: {output_path}[/green]")
    console.print(f"[dim]ID: {agent_id}[/dim]")
    console.print()


def _generate_minimal_template(name: str, agent_id: str, timestamp: str) -> str:
    """Generate a minimal identity template."""
    lines = [
        "schema_version: '1.0'",
        "",
        "metadata:",
        f"  id: {agent_id}",
        f'  name: "{name}"',
        "  version: 0.1.0",
        f'  description: "Agent identity for {name}"',
        f'  created_at: "{timestamp}"',
        f'  updated_at: "{timestamp}"',
        "  status: draft",
        "",
        "role:",
        f'  title: "{name}"',
        f'  purpose: "Assist users with tasks related to {name.lower()}"',
        "  scope:",
        "    primary:",
        "      - General assistance",
        "",
        "personality:",
        "  traits:",
        "    warmth: 0.7",
        "    directness: 0.6",
        "    rigor: 0.5",
        "",
        "communication:",
        "  tone:",
        "    default: professional and helpful",
        "",
        "principles:",
        "  - id: principle_1",
        "    priority: 1",
        "    statement: Always prioritize user safety and privacy",
        "",
        "guardrails:",
        "  hard:",
        "    - id: no_harmful_content",
        "      rule: Never generate harmful, illegal, or unethical content",
        "      enforcement: output_filter",
        "      severity: critical",
    ]
    return "\n".join(lines)


def _generate_full_template(name: str, agent_id: str, timestamp: str) -> str:
    """Generate a full identity template with all major sections."""
    lines = [
        "schema_version: '1.0'",
        "",
        "metadata:",
        f"  id: {agent_id}",
        f'  name: "{name}"',
        "  version: 0.1.0",
        f'  description: "Full PersonaNexus for {name}"',
        f'  created_at: "{timestamp}"',
        f'  updated_at: "{timestamp}"',
        "  author: PersonaNexus Framework",
        "  tags:",
        "    - assistant",
        "  status: draft",
        "",
        "role:",
        f'  title: "{name}"',
        f'  purpose: "A comprehensive assistant for {name.lower()}-related tasks"',
        "  scope:",
        "    primary:",
        "      - General assistance",
        "      - Information retrieval",
        "    secondary:",
        "      - Task planning",
        "  audience:",
        "    primary: General users",
        "    assumed_knowledge: intermediate",
        "",
        "personality:",
        "  traits:",
        "    warmth: 0.7",
        "    verbosity: 0.5",
        "    directness: 0.6",
        "    rigor: 0.5",
        "    empathy: 0.7",
        "  notes: A balanced personality focused on helpfulness",
        "",
        "communication:",
        "  tone:",
        "    default: professional and approachable",
        "    register: consultative",
        "  style:",
        "    sentence_length: mixed",
        "    use_headers: true",
        "    use_lists: true",
        "    use_emoji: sparingly",
        "  language:",
        "    primary: en",
        "    reading_level: intermediate",
        "    jargon_policy: define_on_first_use",
        "",
        "expertise:",
        "  domains:",
        "    - name: General Knowledge",
        "      level: 0.7",
        "      category: primary",
        "      can_teach: true",
        "  out_of_expertise_strategy: acknowledge_and_redirect",
        "",
        "principles:",
        "  - id: safety_first",
        "    priority: 1",
        "    statement: Prioritize user safety and wellbeing above all else",
        "  - id: be_helpful",
        "    priority: 2",
        "    statement: Provide accurate, helpful, and actionable information",
        "  - id: respect_privacy",
        "    priority: 3",
        "    statement: Respect user privacy and handle data responsibly",
        "",
        "behavior:",
        "  conversation:",
        "    length_calibration:",
        "      default: adaptive",
        "    clarification_policy:",
        "      default: ask_when_ambiguous",
        "      bias: toward_action",
        "",
        "guardrails:",
        "  hard:",
        "    - id: no_harmful_content",
        "      rule: Never generate harmful, illegal, or unethical content",
        "      enforcement: output_filter",
        "      severity: critical",
        "    - id: no_personal_data_leak",
        "      rule: Never expose or request sensitive personal information",
        "      enforcement: output_filter",
        "      severity: critical",
        "  permissions:",
        "    autonomous:",
        "      - Answer questions",
        "      - Provide explanations",
        "    forbidden:",
        "      - Access external systems without permission",
        "      - Modify user data",
        "",
        "memory:",
        "  session:",
        "    strategy: sliding_window_with_summary",
        "    sliding_window:",
        "      max_turns: 50",
        "      max_tokens: 8000",
        "",
        "presentation:",
        "  platforms:",
        "    defaults:",
        "      max_response_length: 2000",
        "      format: markdown",
    ]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# personality subcommand group
# ---------------------------------------------------------------------------


personality_app = typer.Typer(
    name="personality",
    help="OCEAN/DISC/Jungian personality mapping utilities",
    add_completion=False,
)
app.add_typer(personality_app, name="personality")


def _print_traits_table(title: str, traits: dict[str, float]) -> None:
    """Print a Rich table of trait values."""
    table = Table(title=title, show_header=True, header_style="bold")
    table.add_column("Trait", style="cyan")
    table.add_column("Value", justify="right")
    table.add_column("Level", style="dim")

    for trait_name in TRAIT_ORDER:
        if trait_name in traits:
            val = traits[trait_name]
            if val >= 0.8:
                level = "Very High"
            elif val >= 0.6:
                level = "High"
            elif val >= 0.4:
                level = "Moderate"
            elif val >= 0.2:
                level = "Low"
            else:
                level = "Very Low"
            table.add_row(trait_name, f"{val:.4f}", level)

    console.print(table)
    console.print()


@personality_app.command("ocean-to-traits")
def personality_ocean_to_traits(
    openness: Annotated[float, typer.Option(help="Openness to experience (0-1)")],
    conscientiousness: Annotated[float, typer.Option(help="Conscientiousness (0-1)")],
    extraversion: Annotated[float, typer.Option(help="Extraversion (0-1)")],
    agreeableness: Annotated[float, typer.Option(help="Agreeableness (0-1)")],
    neuroticism: Annotated[float, typer.Option(help="Neuroticism (0-1)")],
) -> None:
    """Map OCEAN (Big Five) scores to personality traits."""
    from personanexus_skill.personality import ocean_to_traits
    from personanexus_skill.types import OceanProfile

    try:
        profile = OceanProfile(
            openness=openness,
            conscientiousness=conscientiousness,
            extraversion=extraversion,
            agreeableness=agreeableness,
            neuroticism=neuroticism,
        )
    except Exception as exc:
        console.print(f"[red]Invalid OCEAN values: {exc}[/red]")
        raise typer.Exit(code=1)

    traits = ocean_to_traits(profile)
    _print_traits_table("OCEAN -> Traits", traits)


@personality_app.command("disc-to-traits")
def personality_disc_to_traits(
    preset: Annotated[
        str | None,
        typer.Option(
            help="DISC preset name (e.g. the_commander) -- overrides individual values",
        ),
    ] = None,
    dominance: Annotated[float | None, typer.Option(help="Dominance (0-1)")] = None,
    influence: Annotated[float | None, typer.Option(help="Influence (0-1)")] = None,
    steadiness: Annotated[float | None, typer.Option(help="Steadiness (0-1)")] = None,
    conscientiousness: Annotated[
        float | None, typer.Option(help="Conscientiousness (0-1)")
    ] = None,
) -> None:
    """Map DISC scores to personality traits."""
    from personanexus_skill.personality import disc_to_traits, get_disc_preset
    from personanexus_skill.types import DiscProfile

    try:
        if preset:
            profile = get_disc_preset(preset)
        else:
            if (
                dominance is None
                or influence is None
                or steadiness is None
                or conscientiousness is None
            ):
                console.print(
                    "[red]Error: All DISC values required when --preset not provided[/red]"
                )
                raise typer.Exit(code=1)
            profile = DiscProfile(
                dominance=dominance,
                influence=influence,
                steadiness=steadiness,
                conscientiousness=conscientiousness,
            )
    except typer.Exit:
        raise
    except Exception as exc:
        console.print(f"[red]Invalid DISC values: {exc}[/red]")
        raise typer.Exit(code=1)

    traits = disc_to_traits(profile)
    _print_traits_table("DISC -> Traits", traits)


@personality_app.command("jungian-to-traits")
def personality_jungian_to_traits(
    preset: Annotated[
        str | None,
        typer.Option(
            help="Jungian type code (e.g. intj) -- overrides individual values",
        ),
    ] = None,
    ei: Annotated[float | None, typer.Option(help="Extraversion (0) vs Introversion (1)")] = None,
    sn: Annotated[float | None, typer.Option(help="Sensing (0) vs iNtuition (1)")] = None,
    tf: Annotated[float | None, typer.Option(help="Thinking (0) vs Feeling (1)")] = None,
    jp: Annotated[float | None, typer.Option(help="Judging (0) vs Perceiving (1)")] = None,
) -> None:
    """Map Jungian 16-type scores to personality traits."""
    from personanexus_skill.personality import get_jungian_preset, jungian_to_traits
    from personanexus_skill.types import JungianProfile

    try:
        if preset:
            profile = get_jungian_preset(preset)
        else:
            if ei is None or sn is None or tf is None or jp is None:
                console.print(
                    "[red]Error: All Jungian dimensions required when --preset not provided[/red]"
                )
                raise typer.Exit(code=1)
            profile = JungianProfile(ei=ei, sn=sn, tf=tf, jp=jp)
    except typer.Exit:
        raise
    except Exception as exc:
        console.print(f"[red]Invalid Jungian values: {exc}[/red]")
        raise typer.Exit(code=1)

    traits = jungian_to_traits(profile)
    _print_traits_table("Jungian -> Traits", traits)


@personality_app.command("list-disc-presets")
def personality_list_disc_presets() -> None:
    """List all available DISC presets."""
    from personanexus_skill.personality import list_disc_presets

    presets = list_disc_presets()
    console.print("[bold]Available DISC Presets:[/bold]\n")
    for name in presets:
        profile = presets[name]
        console.print(f"  - {name}")
        console.print(
            f"    D={profile.dominance}, I={profile.influence}, "
            f"S={profile.steadiness}, C={profile.conscientiousness}"
        )


@personality_app.command("list-jungian-presets")
def personality_list_jungian_presets() -> None:
    """List all available Jungian 16-type presets."""
    from personanexus_skill.personality import list_jungian_presets

    presets = list_jungian_presets()
    table = Table(title="Jungian 16-Type Presets", show_header=True, header_style="bold")
    table.add_column("Type", style="cyan")
    table.add_column("E/I", justify="right")
    table.add_column("S/N", justify="right")
    table.add_column("T/F", justify="right")
    table.add_column("J/P", justify="right")

    for name, profile in sorted(presets.items()):
        table.add_row(
            name.upper(),
            f"{profile.ei:.2f}",
            f"{profile.sn:.2f}",
            f"{profile.tf:.2f}",
            f"{profile.jp:.2f}",
        )

    console.print(table)
