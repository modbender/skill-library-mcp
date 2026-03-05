"""
Static HTML export for the Natural Language Planner dashboard.

Generates a single self-contained index.html file with all task/project
data inlined as JSON, plus embedded CSS and JS. The exported file can
be opened directly in a browser or deployed to any static hosting service
(GitHub Pages, Netlify, Vercel, etc.).

Note: The export is a point-in-time snapshot — it does not auto-update.
"""

import json
import logging
from pathlib import Path
from typing import Optional

from .config_manager import load_config
from .file_manager import list_projects, list_tasks
from .index_manager import rebuild_index, get_stats
from .utils import ensure_directory

logger = logging.getLogger("nlplanner.export")


def export_dashboard(output_dir: Optional[str] = None) -> Optional[str]:
    """
    Export the dashboard as a self-contained static HTML file.

    Reads all current task and project data, embeds it as JSON in the
    dashboard HTML, and writes a single file that works without a server.

    Args:
        output_dir: Directory to write the export to. Defaults to
                    <workspace>/.nlplanner/export/

    Returns:
        Path to the exported index.html, or None on failure.

    Example:
        >>> path = export_dashboard()
        >>> print(path)
        '/home/user/nlplanner/.nlplanner/export/index.html'
    """
    config = load_config()
    ws = config.get("workspace_path", "")

    if not ws:
        logger.error("Workspace not configured. Run init first.")
        return None

    # Resolve output directory
    if output_dir:
        out = Path(output_dir).expanduser().resolve()
    else:
        out = Path(ws) / ".nlplanner" / "export"

    ensure_directory(out)

    # Gather data
    rebuild_index()
    projects = list_projects()
    tasks = list_tasks()
    stats = get_stats()

    data_payload = {
        "projects": projects,
        "tasks": tasks,
        "stats": stats,
        "exported_at": __import__("datetime").datetime.now().isoformat(timespec="seconds"),
    }

    # Read the template files
    templates_dir = Path(__file__).parent.parent / "templates" / "dashboard"
    html_content = _read_file(templates_dir / "index.html")
    css_content = _read_file(templates_dir / "styles.css")
    js_content = _read_file(templates_dir / "app.js")

    if not all([html_content, css_content, js_content]):
        logger.error("Could not read dashboard template files.")
        return None

    # Build the static JS that injects data instead of fetching from API
    static_js = _build_static_js(js_content, data_payload)

    # Inline CSS and JS into the HTML
    export_html = _inline_assets(html_content, css_content, static_js)

    # Write the export
    output_path = out / "index.html"
    try:
        output_path.write_text(export_html, encoding="utf-8")
    except OSError as e:
        logger.error("Failed to write export: %s", e)
        return None

    logger.info("Dashboard exported to %s", output_path)
    return str(output_path)


def _read_file(path: Path) -> Optional[str]:
    """Read a text file, returning None on error."""
    try:
        return path.read_text(encoding="utf-8")
    except OSError as e:
        logger.error("Could not read %s: %s", path, e)
        return None


def _escape_json_for_html(json_str: str) -> str:
    """Escape a JSON string so it is safe to embed inside an HTML <script> block.

    Prevents ``</script>`` and ``<!--`` sequences in the data from breaking
    out of the surrounding ``<script>`` tag.  These replacements produce
    strings that are still valid JavaScript string literals.
    """
    return json_str.replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")


def _build_static_js(original_js: str, data: dict) -> str:
    """
    Transform the dashboard JS for static/offline use.

    Replaces the API fetch logic with a pre-loaded data blob so the
    dashboard works as a standalone file without a running server.
    """
    data_json = _escape_json_for_html(
        json.dumps(data, default=str, ensure_ascii=False)
    )

    # Prepend the inlined data and override the api() and loadAll() functions
    static_preamble = f"""
// ── STATIC EXPORT: Data is inlined, no server needed ──────────
window.__NLP_STATIC_DATA__ = {data_json};
window.__NLP_STATIC_MODE__ = true;
"""

    # Patch: replace the api() function to return inlined data
    # and replace loadAll() to use the static data directly
    static_patch = """
// ── STATIC EXPORT: Patched loader ─────────────────────────────
(function() {
  var _origInit = null;
  var _checkInterval = setInterval(function() {
    // Wait for the app IIFE to set up, then patch
    if (window.__NLP_STATIC_MODE__) {
      clearInterval(_checkInterval);
    }
  }, 50);
})();
"""

    # Instead of patching inline, we'll wrap: let the original JS load,
    # but override the fetch-based `api` function at the window level
    # so it returns static data.  The app.js uses a local `api()` inside
    # the IIFE, so we need a different approach: inject a <script> block
    # before app.js that sets window.fetch to return our data.

    fetch_override = f"""
// ── STATIC EXPORT: Override fetch for offline use ─────────────
(function() {{
  var DATA = {data_json};
  var originalFetch = window.fetch;
  window.fetch = function(url, opts) {{
    if (typeof url !== 'string') return originalFetch(url, opts);
    // Parse the pathname
    var a = document.createElement('a');
    a.href = url;
    var path = a.pathname;
    if (path === '/api/stats') return fakeResponse(DATA.stats);
    if (path === '/api/projects') return fakeResponse(DATA.projects);
    if (path === '/api/tasks') return fakeResponse(DATA.tasks);
    if (path === '/api/health') return fakeResponse({{status:'ok',static:true}});
    if (path.indexOf('/api/search') === 0) {{
      var q = (new URL(url, location.origin)).searchParams.get('q') || '';
      q = q.toLowerCase();
      var results = DATA.tasks.filter(function(t) {{
        var s = ((t.title||'')+(t.project||'')+((t.tags||[]).join(' '))).toLowerCase();
        return s.indexOf(q) !== -1;
      }});
      return fakeResponse(results);
    }}
    if (path.indexOf('/api/task/') === 0) {{
      var tid = path.split('/api/task/')[1];
      var task = null;
      for (var i=0;i<DATA.tasks.length;i++) {{
        if (DATA.tasks[i].id===tid) {{ task = DATA.tasks[i]; break; }}
      }}
      return fakeResponse(task || {{error:'Not found'}});
    }}
    if (path.indexOf('/api/project/') === 0) {{
      var pid = path.split('/api/project/')[1];
      var proj = null;
      for (var j=0;j<DATA.projects.length;j++) {{
        if (DATA.projects[j].id===pid) {{ proj = DATA.projects[j]; break; }}
      }}
      return fakeResponse(proj || {{error:'Not found'}});
    }}
    // Fallback for other requests (attachments etc)
    return originalFetch(url, opts);
  }};
  function fakeResponse(data) {{
    return Promise.resolve(new Response(JSON.stringify(data), {{
      status: 200,
      headers: {{'Content-Type':'application/json'}}
    }}));
  }}
}})();
"""
    return fetch_override + "\n" + original_js


def _inline_assets(html: str, css: str, js: str) -> str:
    """
    Replace external CSS/JS references with inline <style> and <script> blocks.
    """
    # Replace the <link rel="stylesheet" href="styles.css" /> with inline CSS
    html = html.replace(
        '<link rel="stylesheet" href="styles.css" />',
        f"<style>\n{css}\n</style>",
    )

    # Replace <script src="app.js"></script> with inline JS
    html = html.replace(
        '<script src="app.js"></script>',
        f"<script>\n{js}\n</script>",
    )

    # Add a banner comment
    html = html.replace(
        "<title>NL Planner",
        "<!-- Static export — generated by Natural Language Planner -->\n  <title>NL Planner",
    )

    return html
