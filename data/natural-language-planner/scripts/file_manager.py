"""
Core file operations for the Natural Language Planner.

Handles creation, reading, updating, listing, and archiving of projects
and tasks stored as Markdown files with YAML frontmatter.
"""

import re
import shutil
import logging
from pathlib import Path
from typing import Any, Optional

from .utils import (
    generate_slug,
    generate_task_id,
    parse_frontmatter,
    serialize_frontmatter,
    today_str,
    ensure_directory,
    safe_read_file,
    safe_write_file,
    safe_child_path,
    validate_status,
    validate_priority,
)
from .config_manager import load_config, save_config, set_config_path

logger = logging.getLogger("nlplanner.files")

# ── Project colour palette ─────────────────────────────────────────
# A curated set of accent colours that work well in both light and
# dark mode.  When a new project is created, the next unused colour
# is assigned automatically.  The user can override it later.

PROJECT_COLOUR_PALETTE = [
    "#84cc16",  # lime
    "#ef4444",  # red
    "#38bdf8",  # sky
    "#a78bfa",  # purple
    "#eab308",  # yellow
    "#ec4899",  # pink
    "#14b8a6",  # teal
    "#f97316",  # orange
    "#6366f1",  # indigo
    "#06b6d4",  # cyan
    "#f43f5e",  # rose
    "#10b981",  # emerald
]


def _next_project_colour(root: Path) -> str:
    """Pick the next unused colour from the palette.

    Scans existing projects to see which colours are already taken and
    returns the first unused one.  If all colours have been used, it
    cycles back to the beginning.
    """
    used: set[str] = set()
    projects_dir = root / "projects"
    if projects_dir.exists():
        for readme in projects_dir.glob("*/README.md"):
            raw = safe_read_file(readme)
            if raw:
                meta, _ = parse_frontmatter(raw)
                c = meta.get("color", "")
                if c:
                    used.add(c.lower())

    for colour in PROJECT_COLOUR_PALETTE:
        if colour.lower() not in used:
            return colour

    # All taken — cycle based on total project count
    return PROJECT_COLOUR_PALETTE[len(used) % len(PROJECT_COLOUR_PALETTE)]


# ── Workspace initialisation ───────────────────────────────────────

def init_workspace(workspace_path: str) -> bool:
    """
    Initialise the workspace directory structure.

    Creates the full directory tree expected by the planner:
        workspace/
        ├── .nlplanner/
        │   ├── config.json
        │   └── dashboard/
        ├── projects/
        │   └── inbox/
        │       └── tasks/
        └── archive/

    Args:
        workspace_path: Root directory for the planner workspace.

    Returns:
        True if initialisation succeeded, False otherwise.

    Example:
        >>> init_workspace("~/nlplanner")
        True
    """
    root = Path(workspace_path).expanduser().resolve()

    directories = [
        root / ".nlplanner",
        root / ".nlplanner" / "dashboard",
        root / "projects",
        root / "projects" / "inbox" / "tasks",
        root / "archive",
    ]

    for d in directories:
        if not ensure_directory(d):
            return False

    # Write initial config
    set_config_path(str(root))
    config = load_config(str(root))
    config["workspace_path"] = str(root)
    if not save_config(config, str(root)):
        return False

    # Create inbox README if it doesn't exist
    inbox_readme = root / "projects" / "inbox" / "README.md"
    if not inbox_readme.exists():
        meta = {
            "id": "inbox",
            "title": "Inbox",
            "created": today_str(),
            "status": "active",
            "tags": [],
            "color": _next_project_colour(root),
        }
        body = (
            "## Description\n"
            "Default project for uncategorized tasks.\n\n"
            "## Notes\n"
            "Tasks here haven't been assigned to a specific project yet."
        )
        safe_write_file(inbox_readme, serialize_frontmatter(meta, body))

    logger.info("Workspace initialised at %s", root)
    return True


# ── Project operations ─────────────────────────────────────────────

def create_project(
    name: str,
    description: str = "",
    tags: Optional[list[str]] = None,
    goals: Optional[list[str]] = None,
    color: Optional[str] = None,
) -> Optional[str]:
    """
    Create a new project.

    Args:
        name: Human-readable project name.
        description: Optional longer description.
        tags: Optional list of tag strings.
        goals: Optional list of project goals.
        color: Optional hex colour for the project accent (e.g. ``"#84cc16"``).
               If not provided, one is picked automatically from the palette.

    Returns:
        The project ID (slug) on success, or None on failure.

    Example:
        >>> create_project("Website Redesign", description="Modernise the company website")
        'website-redesign'
    """
    root = _workspace_root()
    if root is None:
        return None

    project_id = generate_slug(name)
    project_dir = safe_child_path(root, "projects", project_id)
    if project_dir is None:
        logger.error("Generated project slug '%s' is invalid.", project_id)
        return None

    if project_dir.exists():
        logger.warning("Project directory '%s' already exists.", project_id)
        # Return existing ID so callers can still reference it
        return project_id

    ensure_directory(project_dir / "tasks")
    ensure_directory(project_dir / "attachments")

    # Auto-assign a colour from the palette if none was given
    if not color:
        color = _next_project_colour(root)

    meta: dict[str, Any] = {
        "id": project_id,
        "title": name,
        "created": today_str(),
        "status": "active",
        "tags": tags or [],
        "color": color,
    }

    body_parts = []
    body_parts.append(f"## Description\n{description or 'No description yet.'}")
    if goals:
        body_parts.append("## Goals\n" + "\n".join(f"- {g}" for g in goals))
    body_parts.append("## Notes\n")

    content = serialize_frontmatter(meta, "\n\n".join(body_parts))
    if not safe_write_file(project_dir / "README.md", content):
        return None

    logger.info("Created project '%s' (%s)", name, project_id)
    return project_id


def get_project(project_id: str) -> Optional[dict[str, Any]]:
    """
    Read a project's metadata and body.

    Args:
        project_id: The project slug / ID.

    Returns:
        Dictionary with keys 'meta' and 'body', or None if not found.
    """
    root = _workspace_root()
    if root is None:
        return None

    readme = safe_child_path(root, "projects", project_id, "README.md")
    if readme is None:
        return None
    raw = safe_read_file(readme)
    if raw is None:
        return None

    meta, body = parse_frontmatter(raw)
    return {"meta": meta, "body": body, "path": str(readme)}


def list_projects(include_archived: bool = False) -> list[dict[str, Any]]:
    """
    List all projects with their metadata.

    Args:
        include_archived: If True, also include archived projects.

    Returns:
        List of project metadata dictionaries.
    """
    root = _workspace_root()
    if root is None:
        return []

    projects = []
    projects_dir = root / "projects"

    if projects_dir.exists():
        for readme in sorted(projects_dir.glob("*/README.md")):
            raw = safe_read_file(readme)
            if raw:
                meta, _ = parse_frontmatter(raw)
                meta["_path"] = str(readme.parent)
                projects.append(meta)

    if include_archived:
        archive_dir = root / "archive"
        if archive_dir.exists():
            for readme in sorted(archive_dir.glob("*/README.md")):
                raw = safe_read_file(readme)
                if raw:
                    meta, _ = parse_frontmatter(raw)
                    meta["_path"] = str(readme.parent)
                    meta["_archived"] = True
                    projects.append(meta)

    return projects


def update_project(project_id: str, updates: dict[str, Any]) -> bool:
    """
    Update a project's metadata and/or body.

    Args:
        project_id: The project slug / ID.
        updates: Dictionary of fields to update. Supports keys in the
                 frontmatter (e.g. 'title', 'tags', 'status') as well
                 as 'body' to replace the markdown body.

    Returns:
        True if the update was saved, False otherwise.
    """
    root = _workspace_root()
    if root is None:
        return False

    readme = safe_child_path(root, "projects", project_id, "README.md")
    if readme is None:
        logger.error("Invalid project ID '%s'.", project_id)
        return False
    raw = safe_read_file(readme)
    if raw is None:
        logger.error("Project '%s' not found.", project_id)
        return False

    meta, body = parse_frontmatter(raw)
    new_body = updates.pop("body", None)
    meta.update(updates)

    content = serialize_frontmatter(meta, new_body if new_body is not None else body)
    return safe_write_file(readme, content)


def archive_project(project_id: str) -> bool:
    """
    Move a project (and its tasks) to the archive directory.

    Args:
        project_id: The project slug / ID.

    Returns:
        True if archived successfully, False otherwise.
    """
    root = _workspace_root()
    if root is None:
        return False

    src = safe_child_path(root, "projects", project_id)
    dst = safe_child_path(root, "archive", project_id)
    if src is None or dst is None:
        logger.error("Invalid project ID '%s'.", project_id)
        return False

    if not src.exists():
        logger.error("Project '%s' not found for archiving.", project_id)
        return False

    try:
        ensure_directory(root / "archive")
        shutil.move(str(src), str(dst))
        # Update status in README
        readme = dst / "README.md"
        raw = safe_read_file(readme)
        if raw:
            meta, body = parse_frontmatter(raw)
            meta["status"] = "archived"
            safe_write_file(readme, serialize_frontmatter(meta, body))
        logger.info("Archived project '%s'.", project_id)
        return True
    except OSError as e:
        logger.error("Failed to archive project '%s': %s", project_id, e)
        return False


# ── Task operations ────────────────────────────────────────────────

def create_task(
    title: str,
    project_id: str = "inbox",
    details: Optional[dict[str, Any]] = None,
) -> Optional[str]:
    """
    Create a new task within a project.

    Args:
        title: Short task title.
        project_id: The project slug to add the task to (default: inbox).
        details: Optional dict of additional fields:
            - description (str)
            - context (str)
            - priority ('low' | 'medium' | 'high')
            - status ('todo' | 'in-progress' | 'done')
            - due (str, ISO date)
            - tags (list[str])
            - dependencies (list[str], task IDs)
            - notes (list[str])

    Returns:
        The generated task ID on success, or None on failure.

    Example:
        >>> create_task("Set up CI pipeline", project_id="website-redesign",
        ...             details={"priority": "high", "due": "2026-02-15"})
        'task-001'
    """
    root = _workspace_root()
    if root is None:
        return None

    details = details or {}

    # Resolve the task directory
    task_dir = safe_child_path(root, "projects", project_id, "tasks")
    if task_dir is None:
        logger.error("Invalid project ID '%s'.", project_id)
        return None
    if not task_dir.exists():
        logger.error("Project '%s' not found.", project_id)
        return None

    # Determine next task counter
    counter = _next_task_counter(root)
    task_id = generate_task_id(counter)

    priority = details.get("priority", "medium")
    if not validate_priority(priority):
        priority = "medium"

    status = details.get("status", "todo")
    if not validate_status(status):
        status = "todo"

    meta: dict[str, Any] = {
        "id": task_id,
        "title": title,
        "project": project_id,
        "status": status,
        "priority": priority,
        "created": today_str(),
        "due": details.get("due", ""),
        "last_checkin": today_str(),
        "tags": details.get("tags", []),
        "dependencies": details.get("dependencies", []),
    }

    body_parts = []
    body_parts.append(
        f"## Description\n{details.get('description', 'No description yet.')}"
    )
    if details.get("context"):
        body_parts.append(f"## Context\n{details['context']}")
    notes = details.get("notes", [])
    if notes:
        body_parts.append("## Notes\n" + "\n".join(f"- {n}" for n in notes))
    else:
        body_parts.append("## Notes\n")
    body_parts.append("## Attachments\n")

    # Agent Tips — AI-generated suggestions, kept separate from user content
    agent_tips = details.get("agent_tips", [])
    if agent_tips:
        body_parts.append(
            "## Agent Tips\n" + "\n".join(f"- {t}" for t in agent_tips)
        )
    else:
        body_parts.append("## Agent Tips\n")

    content = serialize_frontmatter(meta, "\n\n".join(body_parts))
    task_file = task_dir / f"{task_id}.md"

    if not safe_write_file(task_file, content):
        return None

    logger.info("Created task '%s' (%s) in project '%s'.", title, task_id, project_id)
    return task_id


def get_task(task_id: str) -> Optional[dict[str, Any]]:
    """
    Find and read a task by its ID, searching across all projects.

    Args:
        task_id: The task identifier (e.g., 'task-001').

    Returns:
        Dictionary with 'meta' and 'body' keys, or None if not found.
    """
    path = _find_task_file(task_id)
    if path is None:
        return None

    raw = safe_read_file(path)
    if raw is None:
        return None

    meta, body = parse_frontmatter(raw)
    return {"meta": meta, "body": body, "path": str(path)}


def update_task(task_id: str, updates: dict[str, Any]) -> bool:
    """
    Update a task's metadata and/or body.

    Args:
        task_id: The task identifier.
        updates: Fields to update. Supports frontmatter keys and 'body'.

    Returns:
        True if the update was saved.

    Example:
        >>> update_task("task-001", {"status": "in-progress"})
        True
    """
    path = _find_task_file(task_id)
    if path is None:
        logger.error("Task '%s' not found.", task_id)
        return False

    raw = safe_read_file(path)
    if raw is None:
        return False

    meta, body = parse_frontmatter(raw)
    new_body = updates.pop("body", None)

    # Validate controlled fields
    if "status" in updates and not validate_status(updates["status"]):
        logger.warning("Invalid status '%s'; ignoring.", updates["status"])
        del updates["status"]
    if "priority" in updates and not validate_priority(updates["priority"]):
        logger.warning("Invalid priority '%s'; ignoring.", updates["priority"])
        del updates["priority"]

    meta.update(updates)
    content = serialize_frontmatter(meta, new_body if new_body is not None else body)
    return safe_write_file(path, content)


def list_tasks(
    filter_by: Optional[dict[str, Any]] = None,
    project_id: Optional[str] = None,
    include_archived: bool = False,
) -> list[dict[str, Any]]:
    """
    List tasks, optionally filtered.

    Args:
        filter_by: Optional dict of field->value filters applied to metadata.
                   Supports: status, priority, tags (matches if any tag present).
        project_id: If provided, only list tasks in this project.
        include_archived: If True, also scan the archive directory.

    Returns:
        List of task metadata dictionaries.

    Example:
        >>> list_tasks(filter_by={"status": "todo", "priority": "high"})
        [{'id': 'task-001', 'title': '...', ...}, ...]
    """
    root = _workspace_root()
    if root is None:
        return []

    filter_by = filter_by or {}
    tasks: list[dict[str, Any]] = []

    # Determine which project directories to scan
    projects_dir = root / "projects"
    if project_id:
        search_dirs = [projects_dir / project_id / "tasks"]
    else:
        search_dirs = list(projects_dir.glob("*/tasks"))

    # Also scan the archive directory when requested
    if include_archived:
        archive_dir = root / "archive"
        if archive_dir.is_dir():
            if project_id:
                archive_tasks = archive_dir / project_id / "tasks"
                if archive_tasks.is_dir():
                    search_dirs.append(archive_tasks)
            else:
                search_dirs.extend(archive_dir.glob("*/tasks"))

    for task_dir in search_dirs:
        if not task_dir.is_dir():
            continue
        for task_file in sorted(task_dir.glob("task-*.md")):
            raw = safe_read_file(task_file)
            if raw is None:
                continue
            meta, body = parse_frontmatter(raw)
            meta["_path"] = str(task_file)

            # Extract first image attachment as thumbnail
            thumb = _extract_first_image(body)
            if thumb:
                meta["thumbnail"] = thumb

            if _matches_filter(meta, filter_by):
                tasks.append(meta)

    return tasks


def archive_task(task_id: str) -> bool:
    """
    Archive a task by moving it to the archive directory and setting
    its status to 'archived'.

    Args:
        task_id: The task identifier.

    Returns:
        True if archived successfully.
    """
    root = _workspace_root()
    if root is None:
        return False

    path = _find_task_file(task_id)
    if path is None:
        logger.error("Task '%s' not found for archiving.", task_id)
        return False

    # Read and update status
    raw = safe_read_file(path)
    if raw is None:
        return False
    meta, body = parse_frontmatter(raw)
    meta["status"] = "archived"

    # Determine archive location
    project_id = meta.get("project", "inbox")
    archive_dir = safe_child_path(root, "archive", project_id, "tasks")
    if archive_dir is None:
        logger.error("Invalid project ID '%s' in task metadata.", project_id)
        return False
    ensure_directory(archive_dir)

    archive_path = archive_dir / path.name
    if not safe_write_file(archive_path, serialize_frontmatter(meta, body)):
        return False

    # Remove original
    try:
        path.unlink()
    except OSError as e:
        logger.warning("Could not remove original task file: %s", e)

    logger.info("Archived task '%s'.", task_id)
    return True


def add_attachment(project_id: str, file_path: str, new_name: Optional[str] = None) -> Optional[str]:
    """
    Copy a file into a project's attachments directory.

    Args:
        project_id: Target project slug.
        file_path: Path to the source file.
        new_name: Optional rename for the copied file.

    Returns:
        Relative path to the attachment (from the tasks dir), or None on error.
    """
    root = _workspace_root()
    if root is None:
        return None

    src = Path(file_path).expanduser().resolve()
    if not src.is_file():
        logger.error("Attachment source '%s' not found.", file_path)
        return None

    attachments_dir = safe_child_path(root, "projects", project_id, "attachments")
    if attachments_dir is None:
        logger.error("Invalid project ID '%s'.", project_id)
        return None
    ensure_directory(attachments_dir)

    dest_name = new_name or src.name
    dest = attachments_dir / dest_name

    try:
        shutil.copy2(str(src), str(dest))
    except OSError as e:
        logger.error("Failed to copy attachment: %s", e)
        return None

    relative = f"../attachments/{dest_name}"
    logger.info("Added attachment '%s' to project '%s'.", dest_name, project_id)
    return relative


def link_tasks(task_a: str, task_b: str, relationship: str = "depends-on") -> bool:
    """
    Create a dependency link between two tasks.

    Adds task_b to task_a's dependencies list.

    Args:
        task_a: The dependent task ID.
        task_b: The dependency task ID.
        relationship: Description of the relationship (currently unused
                      beyond logging, reserved for future use).

    Returns:
        True if the link was created successfully.
    """
    task_data = get_task(task_a)
    if task_data is None:
        logger.error("Task '%s' not found.", task_a)
        return False

    deps = task_data["meta"].get("dependencies", [])
    if task_b in deps:
        logger.info("Link already exists: %s -> %s", task_a, task_b)
        return True

    # Check for circular dependency (simple direct check)
    other = get_task(task_b)
    if other and task_a in other["meta"].get("dependencies", []):
        logger.warning(
            "Circular dependency detected: %s and %s depend on each other.", task_a, task_b
        )
        return False

    deps.append(task_b)
    return update_task(task_a, {"dependencies": deps})


def move_task(task_id: str, target_project_id: str) -> bool:
    """
    Move a task from its current project to another.

    Args:
        task_id: The task identifier.
        target_project_id: The destination project slug.

    Returns:
        True if moved successfully.
    """
    root = _workspace_root()
    if root is None:
        return False

    src_path = _find_task_file(task_id)
    if src_path is None:
        logger.error("Task '%s' not found.", task_id)
        return False

    target_dir = safe_child_path(root, "projects", target_project_id, "tasks")
    if target_dir is None:
        logger.error("Invalid target project ID '%s'.", target_project_id)
        return False
    if not target_dir.exists():
        logger.error("Target project '%s' not found.", target_project_id)
        return False

    # Update the project field in metadata
    raw = safe_read_file(src_path)
    if raw is None:
        return False

    meta, body = parse_frontmatter(raw)
    meta["project"] = target_project_id
    content = serialize_frontmatter(meta, body)

    dest_path = target_dir / src_path.name
    if not safe_write_file(dest_path, content):
        return False

    try:
        src_path.unlink()
    except OSError as e:
        logger.warning("Could not remove original task file after move: %s", e)

    logger.info("Moved task '%s' to project '%s'.", task_id, target_project_id)
    return True


# ── Agent Tips ─────────────────────────────────────────────────────

def update_task_agent_tips(task_id: str, tips: list[str], replace: bool = False) -> bool:
    """
    Add AI-generated tips and suggestions to a task.

    Tips are stored in the '## Agent Tips' section of the task markdown,
    clearly separated from user-authored content.

    Args:
        task_id: The task identifier.
        tips: List of tip/suggestion strings to add.
        replace: If True, replace all existing tips. If False (default),
                 append to existing tips.

    Returns:
        True if the task was updated successfully.

    Example:
        >>> update_task_agent_tips("task-001", [
        ...     "Consider using a CSS framework like Tailwind for rapid prototyping",
        ...     "Look at competitor sites for layout inspiration: Stripe, Linear, Vercel",
        ...     "Run Lighthouse audit before and after to measure improvement",
        ... ])
        True
    """
    path = _find_task_file(task_id)
    if path is None:
        logger.error("Task '%s' not found.", task_id)
        return False

    raw = safe_read_file(path)
    if raw is None:
        return False

    meta, body = parse_frontmatter(raw)

    # Parse existing agent tips from body
    existing_tips: list[str] = []
    if not replace and "## Agent Tips" in body:
        parts = body.split("## Agent Tips")
        if len(parts) > 1:
            tips_section = parts[1].split("\n## ")[0]  # Stop at next section
            for line in tips_section.strip().splitlines():
                stripped = line.strip()
                if stripped.startswith("- "):
                    existing_tips.append(stripped[2:])

    # Combine tips
    all_tips = existing_tips + tips if not replace else tips

    # Rebuild the Agent Tips section
    tips_block = "\n".join(f"- {t}" for t in all_tips) if all_tips else ""

    if "## Agent Tips" in body:
        # Replace the section content
        before_tips = body.split("## Agent Tips")[0]
        after_parts = body.split("## Agent Tips")[1].split("\n## ", 1)
        after_section = "\n## " + after_parts[1] if len(after_parts) > 1 else ""
        body = f"{before_tips}## Agent Tips\n{tips_block}{after_section}"
    else:
        # Append the section
        body = f"{body.rstrip()}\n\n## Agent Tips\n{tips_block}"

    content = serialize_frontmatter(meta, body)
    return safe_write_file(path, content)


def get_task_agent_tips(task_id: str) -> list[str]:
    """
    Read the AI-generated tips for a task.

    Args:
        task_id: The task identifier.

    Returns:
        List of tip strings, or empty list if none.
    """
    task = get_task(task_id)
    if task is None:
        return []

    body = task.get("body", "")
    if "## Agent Tips" not in body:
        return []

    tips_section = body.split("## Agent Tips")[1].split("\n## ")[0]
    tips = []
    for line in tips_section.strip().splitlines():
        stripped = line.strip()
        if stripped.startswith("- "):
            tips.append(stripped[2:])
    return tips


# ── Internal helpers ───────────────────────────────────────────────

_IMG_LINK_RE = re.compile(
    r"\[([^\]]*)\]\(([^)]+\.(?:png|jpe?g|gif|webp|svg|bmp))\)",
    re.IGNORECASE,
)


def _extract_first_image(body: str) -> Optional[str]:
    """
    Extract the filename of the first image attachment from a task body.

    Scans the markdown body for image links (``[name](path.ext)``) where
    the extension is a known image format.  Returns just the filename
    (not the full path) so the dashboard can build the API URL.

    Returns:
        The image filename, or None if no images found.
    """
    match = _IMG_LINK_RE.search(body)
    if match:
        # Return just the filename portion (security: no paths)
        return Path(match.group(2)).name
    return None


def _workspace_root() -> Optional[Path]:
    """
    Resolve and return the workspace root from config.

    The returned path is always fully resolved so that security checks
    using ``Path.is_relative_to()`` work correctly.

    Returns:
        Resolved path to workspace root, or None if not configured.
    """
    config = load_config()
    ws = config.get("workspace_path", "")
    if not ws:
        logger.error(
            "Workspace path not configured. Run init_workspace() first."
        )
        return None
    return Path(ws).resolve()


def _find_task_file(task_id: str) -> Optional[Path]:
    """
    Locate a task file by ID across all projects.

    Args:
        task_id: The task identifier.

    Returns:
        Path to the task markdown file, or None if not found.
    """
    root = _workspace_root()
    if root is None:
        return None

    # Search active projects
    for task_file in (root / "projects").glob(f"*/tasks/{task_id}.md"):
        return task_file

    # Search archive
    for task_file in (root / "archive").glob(f"*/tasks/{task_id}.md"):
        return task_file

    logger.debug("Task file for '%s' not found.", task_id)
    return None


def _next_task_counter(root: Path) -> int:
    """
    Determine the next sequential task counter by scanning existing tasks.

    Scans all projects and the archive to find the highest existing counter.
    """
    import re as _re

    max_counter = 0
    pattern = _re.compile(r"task-(\d+)\.md$")

    for md_file in root.glob("**/tasks/task-*.md"):
        m = pattern.search(md_file.name)
        if m:
            max_counter = max(max_counter, int(m.group(1)))

    return max_counter + 1


def _matches_filter(meta: dict[str, Any], filter_by: dict[str, Any]) -> bool:
    """
    Check whether a task's metadata matches all filter conditions.
    """
    for key, value in filter_by.items():
        if key == "tags":
            # Match if any requested tag is present
            task_tags = meta.get("tags", [])
            if not any(t in task_tags for t in value):
                return False
        else:
            if meta.get(key) != value:
                return False
    return True
