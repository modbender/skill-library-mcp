#!/usr/bin/env python3
"""
generate_preview.py — Build preview.html from generated clips + open in browser

Creates a dark-themed HTML page with all clips playing side by side,
comment fields under each, and a Copy Feedback button.

Usage:
  python3 scripts/generate_preview.py --storyboard my_project/storyboard.json
"""

import json
import sys
import argparse
import webbrowser
from pathlib import Path


ROLE_COLORS = {
    "hook_a":   "#f59e0b",
    "hook_b":   "#f97316",
    "core":     "#6366f1",
    "cta_a":    "#10b981",
    "cta_b":    "#14b8a6",
}

DEFAULT_COLOR = "#94a3b8"


def build_html(sb: dict, project_dir: Path, output_dir: Path) -> str:
    scenes = sb["scenes"]
    project_name = sb.get("project", "Video Preview")

    # Build scene cards
    cards_html = ""
    scene_ids_js = json.dumps([s["id"] for s in scenes])

    for scene in scenes:
        clip_path = output_dir / f"{scene['id']}.mp4"
        rel_path = clip_path.relative_to(project_dir) if clip_path.exists() else None
        color = ROLE_COLORS.get(scene.get("role", ""), DEFAULT_COLOR)
        missing = not clip_path.exists()

        video_html = f"""
            <video controls loop>
              <source src="{rel_path}" type="video/mp4">
              Your browser does not support video.
            </video>""" if not missing else """
            <div class="missing">⚠ Clip not yet generated</div>"""

        cards_html += f"""
        <div class="card" id="card-{scene['id']}">
          <div class="card-header" style="border-color: {color}">
            <span class="role-tag" style="background: {color}22; color: {color}; border: 1px solid {color}44">
              {scene['label']}
            </span>
            <span class="scene-id">{scene['id']}</span>
            <span class="duration">{scene.get('duration', 5)}s</span>
          </div>
          <div class="video-wrap">
            {video_html}
          </div>
          <div class="prompt-preview">
            <strong>Prompt:</strong> {scene['prompt'][:120]}{'…' if len(scene['prompt']) > 120 else ''}
          </div>
          <div class="feedback-row">
            <div class="status-toggle">
              <button class="btn-approve active" onclick="setStatus('{scene['id']}', 'approve', this)">✓ Approve</button>
              <button class="btn-revise" onclick="setStatus('{scene['id']}', 'revise', this)">↺ Revise</button>
            </div>
            <textarea
              id="notes-{scene['id']}"
              class="notes"
              placeholder="Notes for Muffin… (e.g. slower camera, warmer light, more motion)"
              rows="3"
            ></textarea>
          </div>
        </div>"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{project_name} — Preview</title>
  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

    body {{
      background: #0a0a0f;
      color: #e2e8f0;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
      padding: 32px 24px;
      min-height: 100vh;
    }}

    header {{
      text-align: center;
      margin-bottom: 40px;
    }}
    header h1 {{
      font-size: 1.6rem;
      font-weight: 700;
      letter-spacing: -0.02em;
      color: #f1f5f9;
    }}
    header p {{
      margin-top: 8px;
      color: #64748b;
      font-size: 0.875rem;
    }}

    .grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
      gap: 24px;
      max-width: 1800px;
      margin: 0 auto;
    }}

    .card {{
      background: #13131a;
      border: 1px solid #1e2030;
      border-radius: 12px;
      overflow: hidden;
      display: flex;
      flex-direction: column;
      transition: border-color 0.2s;
    }}
    .card:hover {{ border-color: #2d3148; }}

    .card-header {{
      display: flex;
      align-items: center;
      gap: 10px;
      padding: 14px 16px;
      border-bottom: 2px solid #1e2030;
      border-left: 3px solid;
    }}
    .role-tag {{
      font-size: 0.72rem;
      font-weight: 700;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      padding: 3px 9px;
      border-radius: 4px;
    }}
    .scene-id {{
      font-size: 0.8rem;
      color: #475569;
      font-family: monospace;
      flex: 1;
    }}
    .duration {{
      font-size: 0.75rem;
      color: #475569;
      background: #1e2030;
      padding: 2px 8px;
      border-radius: 4px;
    }}

    .video-wrap {{
      background: #000;
      aspect-ratio: 16/9;
      display: flex;
      align-items: center;
      justify-content: center;
    }}
    .video-wrap video {{
      width: 100%;
      height: 100%;
      object-fit: cover;
    }}
    .missing {{
      color: #f59e0b;
      font-size: 0.85rem;
    }}

    .prompt-preview {{
      padding: 12px 16px;
      font-size: 0.775rem;
      color: #475569;
      line-height: 1.5;
      border-bottom: 1px solid #1e2030;
    }}
    .prompt-preview strong {{ color: #64748b; }}

    .feedback-row {{
      padding: 14px 16px;
      display: flex;
      flex-direction: column;
      gap: 10px;
    }}

    .status-toggle {{
      display: flex;
      gap: 8px;
    }}
    .status-toggle button {{
      flex: 1;
      padding: 7px 0;
      border: 1px solid #1e2030;
      border-radius: 6px;
      background: #0a0a0f;
      color: #64748b;
      font-size: 0.8rem;
      cursor: pointer;
      transition: all 0.15s;
    }}
    .btn-approve.active {{
      background: #05230f;
      border-color: #10b981;
      color: #10b981;
    }}
    .btn-revise.active {{
      background: #230e05;
      border-color: #f97316;
      color: #f97316;
    }}

    .notes {{
      width: 100%;
      background: #0d0d14;
      border: 1px solid #1e2030;
      border-radius: 6px;
      color: #cbd5e1;
      font-size: 0.8rem;
      padding: 10px 12px;
      resize: vertical;
      font-family: inherit;
      line-height: 1.5;
      transition: border-color 0.15s;
    }}
    .notes:focus {{
      outline: none;
      border-color: #6366f1;
    }}
    .notes::placeholder {{ color: #334155; }}

    .actions {{
      max-width: 1800px;
      margin: 32px auto 0;
      display: flex;
      justify-content: flex-end;
      gap: 12px;
    }}
    .btn-copy {{
      background: #6366f1;
      color: #fff;
      border: none;
      padding: 12px 28px;
      border-radius: 8px;
      font-size: 0.9rem;
      font-weight: 600;
      cursor: pointer;
      transition: background 0.15s;
    }}
    .btn-copy:hover {{ background: #4f46e5; }}
    .btn-copy.copied {{
      background: #10b981;
    }}

    .toast {{
      position: fixed;
      bottom: 24px;
      right: 24px;
      background: #10b981;
      color: #fff;
      padding: 12px 20px;
      border-radius: 8px;
      font-size: 0.875rem;
      font-weight: 600;
      opacity: 0;
      transform: translateY(8px);
      transition: all 0.2s;
      pointer-events: none;
    }}
    .toast.show {{
      opacity: 1;
      transform: translateY(0);
    }}
  </style>
</head>
<body>
  <header>
    <h1>🎬 {project_name}</h1>
    <p>Review each clip · Add notes · Hit Copy Feedback · Paste to Muffin</p>
  </header>

  <div class="grid">
    {cards_html}
  </div>

  <div class="actions">
    <button class="btn-copy" onclick="copyFeedback()">📋 Copy Feedback</button>
  </div>

  <div class="toast" id="toast">Feedback copied to clipboard!</div>

  <script>
    const sceneIds = {scene_ids_js};
    const statuses = {{}};

    // Default all to approve
    sceneIds.forEach(id => statuses[id] = 'approve');

    function setStatus(id, action, btn) {{
      statuses[id] = action;
      const card = document.getElementById('card-' + id);
      card.querySelector('.btn-approve').classList.remove('active');
      card.querySelector('.btn-revise').classList.remove('active');
      btn.classList.add('active');
    }}

    function copyFeedback() {{
      const feedback = {{
        scenes: sceneIds.map(id => ({{
          id: id,
          action: statuses[id] || 'approve',
          notes: document.getElementById('notes-' + id).value.trim()
        }}))
      }};

      const json = JSON.stringify(feedback, null, 2);
      navigator.clipboard.writeText(json).then(() => {{
        const btn = document.querySelector('.btn-copy');
        btn.textContent = '✓ Copied!';
        btn.classList.add('copied');
        const toast = document.getElementById('toast');
        toast.classList.add('show');
        setTimeout(() => {{
          btn.textContent = '📋 Copy Feedback';
          btn.classList.remove('copied');
          toast.classList.remove('show');
        }}, 2500);
      }});
    }}
  </script>
</body>
</html>"""


def main():
    parser = argparse.ArgumentParser(description="Generate preview.html from storyboard clips")
    parser.add_argument("--storyboard", "-s", required=True, help="Path to storyboard.json")
    parser.add_argument("--no-open", action="store_true", help="Don't auto-open in browser")
    args = parser.parse_args()

    storyboard_path = Path(args.storyboard)
    if not storyboard_path.exists():
        print(f"✗ Storyboard not found: {storyboard_path}")
        sys.exit(1)

    with open(storyboard_path) as f:
        sb = json.load(f)

    project_dir = storyboard_path.parent
    output_dir = project_dir / sb.get("output_dir", "clips")
    preview_path = project_dir / "preview.html"

    html = build_html(sb, project_dir, output_dir)
    preview_path.write_text(html, encoding="utf-8")

    print(f"✅ Preview built: {preview_path}")

    # Count available clips
    available = sum(1 for s in sb["scenes"] if (output_dir / f"{s['id']}.mp4").exists())
    print(f"   Clips ready: {available}/{len(sb['scenes'])}")

    if not args.no_open:
        webbrowser.open(f"file://{preview_path.resolve()}")
        print("   Opened in browser.")

    print(f"\nNext: Review clips → hit 'Copy Feedback' → paste back to Muffin")


if __name__ == "__main__":
    main()
