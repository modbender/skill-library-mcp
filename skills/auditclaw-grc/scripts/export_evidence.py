#!/usr/bin/env python3
"""Evidence package exporter for auditors.

Creates a ZIP file containing all evidence, a manifest, summary,
and control mapping for a given framework.

Usage:
    python3 export_evidence.py --framework <slug> --output-dir <path> [--db-path <path>]

Exit codes:
    0 = success
    1 = error
"""

import argparse
import json
import os
import sqlite3
import sys
import zipfile
from datetime import datetime

DEFAULT_DB = os.path.expanduser("~/.openclaw/grc/compliance.sqlite")


def export_evidence(db_path, framework_slug, output_dir):
    """Create an evidence export ZIP for a framework."""
    if not os.path.exists(db_path):
        return {"status": "error", "message": f"Database not found: {db_path}"}

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    # Get framework
    fw = conn.execute("SELECT * FROM frameworks WHERE slug = ? AND status = 'active'",
                       (framework_slug,)).fetchone()
    if not fw:
        conn.close()
        return {"status": "error", "message": f"Framework not found or inactive: {framework_slug}"}

    framework_id = fw["id"]
    framework_name = fw["name"]

    # Get controls
    controls = conn.execute(
        "SELECT * FROM controls WHERE framework_id = ? ORDER BY control_id",
        (framework_id,)
    ).fetchall()

    # Get evidence linked to this framework's controls
    evidence = conn.execute("""
        SELECT DISTINCT e.*, GROUP_CONCAT(c.control_id, ', ') as linked_controls
        FROM evidence e
        JOIN evidence_controls ec ON e.id = ec.evidence_id
        JOIN controls c ON ec.control_id = c.id
        WHERE c.framework_id = ?
        GROUP BY e.id
        ORDER BY e.title
    """, (framework_id,)).fetchall()

    # Also get unlinked evidence
    all_evidence = conn.execute("SELECT * FROM evidence ORDER BY title").fetchall()

    conn.close()

    # Prepare output
    os.makedirs(output_dir, exist_ok=True)
    zip_filename = f"{framework_slug}-evidence-{datetime.now().strftime('%Y-%m-%d')}.zip"
    zip_path = os.path.join(output_dir, zip_filename)

    files_included = 0

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        # 1. Manifest
        manifest = {
            "framework": framework_slug,
            "framework_name": framework_name,
            "exported_at": datetime.now().isoformat(),
            "total_controls": len(controls),
            "total_evidence": len(evidence),
            "evidence_items": []
        }

        for e in evidence:
            item = {
                "id": e["id"],
                "title": e["title"],
                "type": e["type"],
                "source": e["source"],
                "status": e["status"],
                "valid_from": e["valid_from"],
                "valid_until": e["valid_until"],
                "linked_controls": e["linked_controls"],
                "filepath": e["filepath"]
            }
            manifest["evidence_items"].append(item)

            # Include actual evidence files if they exist on disk
            if e["filepath"] and os.path.exists(e["filepath"]):
                # Validate filepath is within expected directory
                real_path = os.path.realpath(e["filepath"])
                allowed_base = os.path.realpath(os.path.expanduser("~/.openclaw/grc"))
                if not real_path.startswith(allowed_base):
                    continue  # skip files outside the GRC directory
                arcname = f"evidence/{os.path.basename(e['filepath'])}"
                zf.write(e["filepath"], arcname)
                files_included += 1

        zf.writestr("manifest.json", json.dumps(manifest, indent=2))

        # 2. Summary
        status_counts = {}
        for c in controls:
            s = c["status"]
            status_counts[s] = status_counts.get(s, 0) + 1

        total = len(controls)
        complete = status_counts.get("complete", 0)
        score = round((complete / total) * 100, 1) if total > 0 else 0

        summary_lines = [
            f"# Evidence Export Summary — {framework_name}",
            f"",
            f"**Exported:** {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            f"**Framework:** {framework_name} ({framework_slug})",
            f"",
            f"## Compliance Overview",
            f"",
            f"- Total Controls: {total}",
        ]
        for status, count in sorted(status_counts.items()):
            summary_lines.append(f"- {status}: {count}")
        summary_lines.extend([
            f"- Estimated Score: {score}%",
            f"",
            f"## Evidence",
            f"",
        ])

        if evidence:
            summary_lines.append(f"Total evidence items linked to this framework: {len(evidence)}")
            summary_lines.append(f"Evidence files included in package: {files_included}")
            summary_lines.append("")
            for e in evidence:
                summary_lines.append(f"- **{e['title']}** ({e['status']})")
                summary_lines.append(f"  - Type: {e['type'] or 'N/A'} | Source: {e['source'] or 'N/A'}")
                summary_lines.append(f"  - Valid: {e['valid_from'] or 'N/A'} to {e['valid_until'] or 'N/A'}")
                summary_lines.append(f"  - Controls: {e['linked_controls'] or 'none'}")
        else:
            summary_lines.append("No evidence records linked to this framework.")

        zf.writestr("summary.md", "\n".join(summary_lines))

        # 3. Control mapping CSV
        def _csv_safe(val):
            """Escape CSV value: double quotes and neutralize formula injection."""
            s = str(val) if val else ""
            s = s.replace('"', '""')
            if s and s[0] in ('=', '+', '-', '@', '\t', '\r'):
                s = "'" + s
            return s

        csv_lines = ["control_id,title,category,priority,status,assignee,evidence_linked"]
        for c in controls:
            # Find linked evidence for this control
            linked = [e["title"] for e in evidence
                      if c["control_id"] and c["control_id"] in (e["linked_controls"] or "")]
            csv_lines.append(
                f'"{_csv_safe(c["control_id"])}","{_csv_safe(c["title"])}","{_csv_safe(c["category"])}",{c["priority"]},{_csv_safe(c["status"])},"{_csv_safe(c["assignee"])}","{_csv_safe("; ".join(linked))}"'
            )
        zf.writestr("control-mapping.csv", "\n".join(csv_lines))

    total_size = os.path.getsize(zip_path)

    return {
        "status": "exported",
        "zip_path": zip_path,
        "framework": framework_slug,
        "files_included": files_included,
        "evidence_records": len(evidence),
        "controls": len(controls),
        "manifest_included": True,
        "total_size_mb": round(total_size / (1024 * 1024), 2)
    }


def main():
    parser = argparse.ArgumentParser(description="Export evidence package for auditors")
    parser.add_argument("--framework", required=True, help="Framework slug")
    parser.add_argument("--output-dir", dest="output_dir", required=True, help="Output directory for ZIP")
    parser.add_argument("--db-path", dest="db_path", default=DEFAULT_DB, help="Database path")
    args = parser.parse_args()

    result = export_evidence(args.db_path, args.framework, args.output_dir)

    print(json.dumps(result, indent=2))
    if result["status"] == "error":
        sys.exit(1)


if __name__ == "__main__":
    main()
