#!/usr/bin/env python3
"""Unified database interface for GRC compliance operations.

All CRUD operations go through this script. Returns JSON to stdout.

Usage:
    python3 db_query.py --action <action> [--args] [--db-path /path/to/db]

Actions (Phase 1):
    status              Overall compliance status
    activate-framework  Activate a compliance framework
    deactivate-framework Deactivate a framework
    list-controls       List controls with filters
    add-control         Create a custom control
    update-control      Update control fields
    add-evidence        Record evidence
    update-evidence     Update evidence status
    list-evidence       List evidence with filters
    add-risk            Create a risk entry
    list-risks          List risks with filters
    add-vendor          Register a vendor
    list-vendors        List vendors
    add-incident        Log an incident
    update-incident     Update incident status
    list-incidents      List incidents
    add-policy          Record a policy
    score-history       Historical score data
    list-mappings       Cross-framework control mappings

Actions (Phase 2 - Assets, Training, Vulnerabilities):
    add-asset           Register an asset
    list-assets         List assets with filters
    update-asset        Update an asset
    add-training-module       Create a training module
    list-training-modules     List training modules
    add-training-assignment   Assign training to a user
    list-training-assignments List training assignments
    update-training-assignment Update a training assignment
    add-vulnerability         Register a vulnerability
    list-vulnerabilities      List vulnerabilities
    update-vulnerability      Update a vulnerability

Actions (Phase 2 - Access Reviews, Questionnaires):
    add-access-review          Create an access review campaign
    list-access-reviews        List access review campaigns
    update-access-review       Update an access review campaign
    add-review-item            Add item to access review
    list-review-items          List access review items
    update-review-item         Record decision on review item
    add-questionnaire-template       Create a questionnaire template
    list-questionnaire-templates     List questionnaire templates
    add-questionnaire-response       Start a questionnaire response
    list-questionnaire-responses     List questionnaire responses
    add-questionnaire-answer         Record an answer
    update-questionnaire-response    Update questionnaire response status

Actions (Phase 5 - Integration Setup UX):
    setup-guide          Step-by-step setup guide for a cloud provider
    show-policy          Show exact IAM policy/permissions for a provider
    test-connection      Test connectivity to a configured provider
"""

import argparse
import json
import os
import sqlite3
import sys
from datetime import datetime, timedelta

DEFAULT_DB_PATH = os.path.expanduser("~/.openclaw/grc/compliance.sqlite")


def get_db(db_path=None):
    """Get a database connection with proper settings."""
    path = db_path or os.environ.get("GRC_DB_PATH", DEFAULT_DB_PATH)
    if not os.path.exists(path):
        print(json.dumps({"status": "error", "message": "Database not initialised. Run init_db.py first."}), file=sys.stderr)
        sys.exit(1)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def action_status(conn, args):
    """Overall compliance status or framework-specific."""
    query_parts = []
    params = []

    if args.framework:
        fw = conn.execute("SELECT id, name, slug FROM frameworks WHERE slug = ? AND status = 'active'", (args.framework,)).fetchone()
        if not fw:
            return {"status": "error", "message": f"Framework '{args.framework}' not found or inactive"}
        framework_filter = "AND c.framework_id = ?"
        params = [fw["id"]]
    else:
        framework_filter = ""

    # Count controls by status
    total = conn.execute(f"SELECT COUNT(*) FROM controls c WHERE 1=1 {framework_filter}", params).fetchone()[0]
    complete = conn.execute(f"SELECT COUNT(*) FROM controls c WHERE c.status = 'complete' {framework_filter}", params).fetchone()[0]
    in_progress = conn.execute(f"SELECT COUNT(*) FROM controls c WHERE c.status = 'in_progress' {framework_filter}", params).fetchone()[0]
    not_started = conn.execute(f"SELECT COUNT(*) FROM controls c WHERE c.status = 'not_started' {framework_filter}", params).fetchone()[0]
    awaiting = conn.execute(f"SELECT COUNT(*) FROM controls c WHERE c.status = 'awaiting_review' {framework_filter}", params).fetchone()[0]
    rejected = conn.execute(f"SELECT COUNT(*) FROM controls c WHERE c.status = 'rejected' {framework_filter}", params).fetchone()[0]

    # Count evidence
    total_evidence = conn.execute("SELECT COUNT(*) FROM evidence").fetchone()[0]
    active_evidence = conn.execute("SELECT COUNT(*) FROM evidence WHERE status = 'active'").fetchone()[0]
    expired_evidence = conn.execute("SELECT COUNT(*) FROM evidence WHERE status = 'expired'").fetchone()[0]

    # Expiring soon (within 30 days)
    cutoff = (datetime.now() + timedelta(days=30)).isoformat()
    expiring = conn.execute(
        "SELECT COUNT(*) FROM evidence WHERE status = 'active' AND valid_until IS NOT NULL AND valid_until <= ?",
        (cutoff,)
    ).fetchone()[0]

    # Active frameworks
    frameworks = [dict(r) for r in conn.execute("SELECT id, name, slug, status FROM frameworks WHERE status = 'active'").fetchall()]

    # Open risks
    total_risks = conn.execute("SELECT COUNT(*) FROM risks WHERE status = 'open'").fetchone()[0]
    high_risks = conn.execute("SELECT COUNT(*) FROM risks WHERE status = 'open' AND score >= 15").fetchone()[0]

    # Open incidents
    open_incidents = conn.execute("SELECT COUNT(*) FROM incidents WHERE status NOT IN ('resolved', 'closed')").fetchone()[0]

    result = {
        "status": "ok",
        "frameworks": frameworks,
        "controls": {
            "total": total,
            "complete": complete,
            "in_progress": in_progress,
            "not_started": not_started,
            "awaiting_review": awaiting,
            "rejected": rejected,
        },
        "evidence": {
            "total": total_evidence,
            "active": active_evidence,
            "expired": expired_evidence,
            "expiring_soon": expiring,
        },
        "risks": {
            "open": total_risks,
            "high_critical": high_risks,
        },
        "incidents": {
            "open": open_incidents,
        },
    }

    if args.framework:
        result["framework"] = args.framework

    return result


def action_activate_framework(conn, args):
    """Activate a compliance framework, loading its controls."""
    slug = args.slug
    if not slug:
        return {"status": "error", "message": "Missing --slug argument"}

    # Check if already active
    existing = conn.execute("SELECT id, status FROM frameworks WHERE slug = ?", (slug,)).fetchone()
    if existing and existing["status"] == "active":
        count = conn.execute("SELECT COUNT(*) FROM controls WHERE framework_id = ?", (existing["id"],)).fetchone()[0]
        return {"status": "already_active", "framework": slug, "controls": count}

    # Find framework JSON file
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    framework_path = args.framework_file if hasattr(args, 'framework_file') and args.framework_file else None

    if not framework_path:
        framework_path = os.path.join(base_dir, "assets", "frameworks", f"{slug}.json")

    if not os.path.exists(framework_path):
        return {"status": "error", "message": f"Unknown framework: {slug}. Check that the framework JSON file exists."}

    with open(framework_path, "r") as f:
        fw_data = json.load(f)

    # Reactivate if inactive
    if existing and existing["status"] == "inactive":
        conn.execute("UPDATE frameworks SET status = 'active', activated_at = datetime('now') WHERE id = ?", (existing["id"],))
        # Delete old controls and re-import
        conn.execute("DELETE FROM controls WHERE framework_id = ?", (existing["id"],))
        fw_id = existing["id"]
    else:
        cursor = conn.execute(
            "INSERT INTO frameworks (name, slug, version, status) VALUES (?, ?, ?, 'active')",
            (fw_data["name"], fw_data["id"], fw_data.get("version", "1.0"))
        )
        fw_id = cursor.lastrowid

    # Load controls from framework data
    control_count = 0
    for domain in fw_data.get("domains", []):
        for control in domain.get("controls", []):
            conn.execute(
                """INSERT INTO controls (framework_id, control_id, title, description, category, priority, status)
                   VALUES (?, ?, ?, ?, ?, ?, 'not_started')""",
                (fw_id, control["id"], control["title"], control.get("description", ""),
                 control.get("category", domain.get("name", "")), control.get("priority", 3))
            )
            control_count += 1

            # Load cross-framework mappings if present
            mappings = control.get("mappings", {})
            for target_fw, target_ids in mappings.items():
                for target_id in target_ids:
                    try:
                        conn.execute(
                            """INSERT OR IGNORE INTO control_mappings
                               (source_framework, source_control_id, target_framework, target_control_id)
                               VALUES (?, ?, ?, ?)""",
                            (slug, control["id"], target_fw, target_id)
                        )
                    except sqlite3.IntegrityError:
                        pass

    conn.commit()

    # Log the action
    conn.execute(
        "INSERT INTO audit_log (action, entity_type, entity_id, details) VALUES (?, ?, ?, ?)",
        ("activate_framework", "framework", fw_id, json.dumps({"slug": slug, "controls": control_count}))
    )
    conn.commit()

    domains = [d["name"] for d in fw_data.get("domains", [])]

    return {
        "status": "activated",
        "framework": slug,
        "name": fw_data["name"],
        "controls_loaded": control_count,
        "domains": domains,
    }


def action_deactivate_framework(conn, args):
    """Deactivate a framework (archives, doesn't delete)."""
    slug = args.slug
    if not slug:
        return {"status": "error", "message": "Missing --slug argument"}

    fw = conn.execute("SELECT id FROM frameworks WHERE slug = ? AND status = 'active'", (slug,)).fetchone()
    if not fw:
        return {"status": "error", "message": f"Framework '{slug}' not found or already inactive"}

    reason = getattr(args, 'reason', None) or "Deactivated by user"
    conn.execute("UPDATE frameworks SET status = 'inactive', notes = ? WHERE id = ?", (reason, fw["id"]))
    conn.commit()

    return {"status": "deactivated", "framework": slug, "reason": reason}


def action_list_controls(conn, args):
    """List controls with optional filters."""
    query = "SELECT c.*, f.slug as framework_slug FROM controls c JOIN frameworks f ON c.framework_id = f.id WHERE 1=1"
    params = []

    if args.framework:
        query += " AND f.slug = ?"
        params.append(args.framework)
    if args.status:
        query += " AND c.status = ?"
        params.append(args.status)
    if args.priority:
        query += " AND c.priority >= ?"
        params.append(int(args.priority))
    if args.overdue:
        query += " AND c.due_date < ? AND c.status NOT IN ('complete', 'rejected')"
        params.append(datetime.now().isoformat())

    # Effectiveness and maturity filters
    maturity_level = getattr(args, 'maturity_level', None)
    if maturity_level:
        query += " AND c.maturity_level = ?"
        params.append(maturity_level)

    min_effectiveness = getattr(args, 'min_effectiveness', None)
    if min_effectiveness is not None:
        query += " AND c.effectiveness_score >= ?"
        params.append(int(min_effectiveness))

    query += " ORDER BY c.priority DESC, c.control_id ASC"

    rows = conn.execute(query, params).fetchall()
    controls = [dict(r) for r in rows]

    return {"status": "ok", "count": len(controls), "controls": controls}


def action_add_control(conn, args):
    """Add a custom control."""
    title = args.title
    if not title:
        return {"status": "error", "message": "Missing --title argument"}

    # Framework is optional for custom controls
    fw_id = None
    if args.framework:
        fw = conn.execute("SELECT id FROM frameworks WHERE slug = ? AND status = 'active'", (args.framework,)).fetchone()
        if not fw:
            return {"status": "error", "message": f"Framework '{args.framework}' not found or inactive"}
        fw_id = fw["id"]

    control_code = getattr(args, 'control_id_code', None) or "CUSTOM"
    priority = int(args.priority) if args.priority else 3
    status = args.status or "not_started"

    cursor = conn.execute(
        """INSERT INTO controls (framework_id, control_id, title, description, category, priority, status, assignee, due_date)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (fw_id, control_code, title, args.description or "", args.category or "",
         priority, status, args.assignee or None, args.due_date or None)
    )
    conn.commit()

    return {"status": "created", "id": cursor.lastrowid, "control_id": control_code, "title": title}


def action_update_control(conn, args):
    """Update a control by DB id or control_id code."""
    # Resolve the control
    control = None
    ids_to_update = []

    if args.id:
        # Support batch: --id 1,2,3
        id_parts = str(args.id).split(",")
        for id_str in id_parts:
            id_str = id_str.strip()
            if id_str.isdigit():
                row = conn.execute("SELECT id FROM controls WHERE id = ?", (int(id_str),)).fetchone()
                if row:
                    ids_to_update.append(row["id"])
        if not ids_to_update:
            return {"status": "error", "message": f"Control(s) not found with id: {args.id}"}
    elif hasattr(args, 'control_id_code') and args.control_id_code:
        row = conn.execute("SELECT id FROM controls WHERE control_id = ?", (args.control_id_code,)).fetchone()
        if not row:
            return {"status": "error", "message": f"Control not found with control_id: {args.control_id_code}"}
        ids_to_update = [row["id"]]
    else:
        return {"status": "error", "message": "Provide --id or --control-id to identify the control"}

    # Build update SET clause
    updates = []
    params = []
    if args.status:
        updates.append("status = ?")
        params.append(args.status)
    if args.assignee:
        updates.append("assignee = ?")
        params.append(args.assignee)
    if args.due_date:
        updates.append("due_date = ?")
        params.append(args.due_date)
    if args.priority:
        updates.append("priority = ?")
        params.append(int(args.priority))
    if hasattr(args, 'review_date') and args.review_date:
        updates.append("review_date = ?")
        params.append(args.review_date)
    if hasattr(args, 'implementation_notes') and args.implementation_notes:
        updates.append("implementation_notes = ?")
        params.append(args.implementation_notes)

    if not updates:
        return {"status": "error", "message": "No fields to update. Provide --status, --assignee, --due-date, --priority, --review-date, or --implementation-notes"}

    updates.append("last_updated = datetime('now')")
    set_clause = ", ".join(updates)

    updated_count = 0
    for cid in ids_to_update:
        conn.execute(f"UPDATE controls SET {set_clause} WHERE id = ?", params + [cid])
        updated_count += 1

    conn.commit()

    return {"status": "updated", "updated_count": updated_count, "ids": ids_to_update}


def action_add_evidence(conn, args):
    """Add evidence record, optionally linking to controls."""
    title = args.title
    if not title:
        return {"status": "error", "message": "Missing --title argument"}

    cursor = conn.execute(
        """INSERT INTO evidence (title, filename, filepath, description, type, source, valid_from, valid_until, status)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'active')""",
        (title, getattr(args, 'filename', None), getattr(args, 'filepath', None),
         args.description or "", args.type or "manual", args.source or "manual",
         getattr(args, 'valid_from', None), getattr(args, 'valid_until', None))
    )
    evidence_id = cursor.lastrowid

    # Link to controls
    linked = []
    if hasattr(args, 'control_ids') and args.control_ids:
        for cid_str in str(args.control_ids).split(","):
            cid = cid_str.strip()
            if cid.isdigit():
                try:
                    conn.execute("INSERT INTO evidence_controls (evidence_id, control_id) VALUES (?, ?)",
                                 (evidence_id, int(cid)))
                    linked.append(int(cid))
                except sqlite3.IntegrityError:
                    pass

    conn.commit()

    return {"status": "created", "id": evidence_id, "title": title, "linked_controls": linked}


def action_update_evidence(conn, args):
    """Update evidence status."""
    if not args.id:
        return {"status": "error", "message": "Missing --id argument"}

    row = conn.execute("SELECT id FROM evidence WHERE id = ?", (int(args.id),)).fetchone()
    if not row:
        return {"status": "error", "message": f"Evidence not found with id: {args.id}"}

    updates = []
    params = []
    if args.status:
        updates.append("status = ?")
        params.append(args.status)

    if not updates:
        return {"status": "error", "message": "No fields to update. Provide --status"}

    set_clause = ", ".join(updates)
    conn.execute(f"UPDATE evidence SET {set_clause} WHERE id = ?", params + [int(args.id)])
    conn.commit()

    return {"status": "updated", "id": int(args.id)}


def action_list_evidence(conn, args):
    """List evidence with optional filters."""
    query = "SELECT * FROM evidence WHERE 1=1"
    params = []

    if args.status:
        query += " AND status = ?"
        params.append(args.status)
    if hasattr(args, 'expiring_within') and args.expiring_within:
        cutoff = (datetime.now() + timedelta(days=int(args.expiring_within))).isoformat()
        now = datetime.now().isoformat()
        query += " AND status = 'active' AND valid_until IS NOT NULL AND valid_until <= ? AND valid_until > ?"
        params.extend([cutoff, now])

    query += " ORDER BY valid_until ASC"
    rows = conn.execute(query, params).fetchall()
    evidence = [dict(r) for r in rows]

    return {"status": "ok", "count": len(evidence), "evidence": evidence}


def action_add_risk(conn, args):
    """Add a risk entry with validation."""
    title = args.title
    if not title:
        return {"status": "error", "message": "Missing --title argument"}

    likelihood = int(args.likelihood) if args.likelihood else None
    impact = int(args.impact) if args.impact else None

    if likelihood is not None and (likelihood < 1 or likelihood > 5):
        return {"status": "error", "message": "Likelihood must be between 1 and 5"}
    if impact is not None and (impact < 1 or impact > 5):
        return {"status": "error", "message": "Impact must be between 1 and 5"}

    cursor = conn.execute(
        """INSERT INTO risks (title, description, category, likelihood, impact, treatment, treatment_plan, owner, review_date, status, linked_controls)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'open', ?)""",
        (title, args.description or "", args.category or "security",
         likelihood, impact, getattr(args, 'treatment', None),
         getattr(args, 'treatment_plan', None), args.owner or None,
         getattr(args, 'review_date', None),
         getattr(args, 'linked_controls', None))
    )
    conn.commit()

    risk_id = cursor.lastrowid
    # Fetch the computed score
    score = conn.execute("SELECT score FROM risks WHERE id = ?", (risk_id,)).fetchone()["score"]

    # Determine risk level
    risk_level = get_risk_level(score)

    return {"status": "created", "id": risk_id, "title": title, "score": score, "level": risk_level}


def get_risk_level(score):
    """Map score to risk level per risk_matrix.json."""
    if score is None:
        return "unknown"
    if score <= 4:
        return "very_low"
    if score <= 9:
        return "low"
    if score <= 14:
        return "medium"
    if score <= 19:
        return "high"
    return "critical"


def action_list_risks(conn, args):
    """List risks with optional filters."""
    query = "SELECT * FROM risks WHERE 1=1"
    params = []

    if args.status:
        query += " AND status = ?"
        params.append(args.status)
    if hasattr(args, 'min_score') and args.min_score:
        query += " AND score >= ?"
        params.append(int(args.min_score))
    if args.category:
        query += " AND category = ?"
        params.append(args.category)

    query += " ORDER BY score DESC"
    rows = conn.execute(query, params).fetchall()
    risks = [dict(r) for r in rows]

    # Add risk level to each
    for r in risks:
        r["level"] = get_risk_level(r.get("score"))

    return {"status": "ok", "count": len(risks), "risks": risks}


def action_update_risk(conn, args):
    """Update a risk record. Score auto-recalculates when likelihood/impact change."""
    if not args.id:
        return {"status": "error", "message": "Missing --id argument"}
    row = conn.execute("SELECT id FROM risks WHERE id = ?", (int(args.id),)).fetchone()
    if not row:
        return {"status": "error", "message": f"Risk not found with id: {args.id}"}

    updates = []
    params = []
    if args.status:
        updates.append("status = ?")
        params.append(args.status)
    if args.likelihood:
        updates.append("likelihood = ?")
        params.append(int(args.likelihood))
    if args.impact:
        updates.append("impact = ?")
        params.append(int(args.impact))
    if args.treatment:
        updates.append("treatment = ?")
        params.append(args.treatment)
    if hasattr(args, 'treatment_plan') and args.treatment_plan:
        updates.append("treatment_plan = ?")
        params.append(args.treatment_plan)
    if args.owner:
        updates.append("owner = ?")
        params.append(args.owner)
    if hasattr(args, 'review_date') and args.review_date:
        updates.append("review_date = ?")
        params.append(args.review_date)
    if args.category:
        updates.append("category = ?")
        params.append(args.category)
    if args.description:
        updates.append("description = ?")
        params.append(args.description)

    if not updates:
        return {"status": "error", "message": "No fields to update"}

    updates.append("last_updated = datetime('now')")
    set_clause = ", ".join(updates)
    conn.execute(f"UPDATE risks SET {set_clause} WHERE id = ?", params + [int(args.id)])
    conn.commit()

    # Fetch updated record to return new score (auto-recalculated by GENERATED column)
    updated = dict(conn.execute("SELECT * FROM risks WHERE id = ?", (int(args.id),)).fetchone())
    updated["level"] = get_risk_level(updated.get("score"))
    return {"status": "updated", "id": int(args.id), "risk": updated}


def action_add_vendor(conn, args):
    """Register a vendor."""
    name = args.name
    if not name:
        return {"status": "error", "message": "Missing --name argument"}

    cursor = conn.execute(
        """INSERT INTO vendors (name, category, criticality, data_access, contact_name, contact_email, notes, status)
           VALUES (?, ?, ?, ?, ?, ?, ?, 'active')""",
        (name, args.category or None, args.criticality or "medium",
         getattr(args, 'data_access', None),
         getattr(args, 'contact_name', None), getattr(args, 'contact_email', None),
         getattr(args, 'notes', None))
    )
    conn.commit()

    return {"status": "created", "id": cursor.lastrowid, "name": name, "criticality": args.criticality or "medium"}


def action_list_vendors(conn, args):
    """List vendors with optional filters."""
    query = "SELECT * FROM vendors WHERE 1=1"
    params = []

    if args.status:
        query += " AND status = ?"
        params.append(args.status)
    if hasattr(args, 'overdue_reviews') and args.overdue_reviews:
        query += " AND next_assessment_date < ? AND status = 'active'"
        params.append(datetime.now().isoformat())

    query += " ORDER BY criticality DESC, name ASC"
    rows = conn.execute(query, params).fetchall()

    return {"status": "ok", "count": len(rows), "vendors": [dict(r) for r in rows]}


def action_update_vendor(conn, args):
    """Update a vendor record."""
    if not args.id:
        return {"status": "error", "message": "Missing --id argument"}
    row = conn.execute("SELECT id FROM vendors WHERE id = ?", (int(args.id),)).fetchone()
    if not row:
        return {"status": "error", "message": f"Vendor not found with id: {args.id}"}

    updates = []
    params = []
    if args.status:
        updates.append("status = ?")
        params.append(args.status)
    if args.criticality:
        updates.append("criticality = ?")
        params.append(args.criticality)
    if hasattr(args, 'risk_score') and args.risk_score is not None:
        updates.append("risk_score = ?")
        params.append(int(args.risk_score))
    if hasattr(args, 'next_assessment_date') and args.next_assessment_date:
        updates.append("next_assessment_date = ?")
        params.append(args.next_assessment_date)
    if hasattr(args, 'notes') and args.notes:
        updates.append("notes = ?")
        params.append(args.notes)
    if args.name:
        updates.append("name = ?")
        params.append(args.name)
    if args.category:
        updates.append("category = ?")
        params.append(args.category)
    if hasattr(args, 'contact_name') and args.contact_name:
        updates.append("contact_name = ?")
        params.append(args.contact_name)
    if hasattr(args, 'contact_email') and args.contact_email:
        updates.append("contact_email = ?")
        params.append(args.contact_email)

    if not updates:
        return {"status": "error", "message": "No fields to update"}

    set_clause = ", ".join(updates)
    conn.execute(f"UPDATE vendors SET {set_clause} WHERE id = ?", params + [int(args.id)])
    conn.commit()
    return {"status": "updated", "id": int(args.id)}


def action_add_incident(conn, args):
    """Log an incident."""
    title = args.title
    if not title:
        return {"status": "error", "message": "Missing --title argument"}

    cursor = conn.execute(
        """INSERT INTO incidents (title, description, type, severity, status)
           VALUES (?, ?, ?, ?, 'detected')""",
        (title, args.description or "", args.type or "security_breach",
         args.severity or "medium")
    )
    conn.commit()

    return {"status": "created", "id": cursor.lastrowid, "title": title, "severity": args.severity or "medium"}


def action_update_incident(conn, args):
    """Update incident fields including V3 costs, regulatory, and preventive actions."""
    if not args.id:
        return {"status": "error", "message": "Missing --id argument"}

    row = conn.execute("SELECT * FROM incidents WHERE id = ?", (int(args.id),)).fetchone()
    if not row:
        return {"status": "error", "message": f"Incident not found with id: {args.id}"}

    updates = []
    params = []
    if args.status:
        updates.append("status = ?")
        params.append(args.status)
    if args.severity:
        updates.append("severity = ?")
        params.append(args.severity)
    if hasattr(args, 'root_cause') and args.root_cause:
        updates.append("root_cause = ?")
        params.append(args.root_cause)
    if hasattr(args, 'preventive_actions') and args.preventive_actions:
        updates.append("preventive_actions = ?")
        params.append(args.preventive_actions)
    if hasattr(args, 'impact_assessment') and args.impact_assessment:
        updates.append("impact_assessment = ?")
        params.append(args.impact_assessment)
    if hasattr(args, 'estimated_cost') and args.estimated_cost is not None:
        updates.append("estimated_cost = ?")
        params.append(float(args.estimated_cost))
    if hasattr(args, 'actual_cost') and args.actual_cost is not None:
        updates.append("actual_cost = ?")
        params.append(float(args.actual_cost))
    if hasattr(args, 'regulatory_required') and args.regulatory_required is not None:
        updates.append("regulatory_notification_required = ?")
        params.append(int(args.regulatory_required))
    if hasattr(args, 'regulatory_body') and args.regulatory_body:
        # Append to JSON array of notified bodies
        import json as _json
        existing = row["regulatory_bodies_notified"] if dict(row).get("regulatory_bodies_notified") else "[]"
        try:
            bodies = _json.loads(existing)
        except (ValueError, TypeError):
            bodies = []
        bodies.append({"body": args.regulatory_body, "notified_at": datetime.now().isoformat()})
        updates.append("regulatory_bodies_notified = ?")
        params.append(_json.dumps(bodies))
        updates.append("regulatory_notification_sent_at = datetime('now')")

    if args.status == "resolved":
        updates.append("resolved_at = datetime('now')")

    if not updates:
        return {"status": "error", "message": "No fields to update"}

    set_clause = ", ".join(updates)
    conn.execute(f"UPDATE incidents SET {set_clause} WHERE id = ?", params + [int(args.id)])
    conn.commit()

    return {"status": "updated", "id": int(args.id)}


def action_list_incidents(conn, args):
    """List incidents with optional filters."""
    query = "SELECT * FROM incidents WHERE 1=1"
    params = []

    if args.status:
        query += " AND status = ?"
        params.append(args.status)
    if args.severity:
        query += " AND severity = ?"
        params.append(args.severity)

    query += " ORDER BY reported_at DESC"
    rows = conn.execute(query, params).fetchall()

    return {"status": "ok", "count": len(rows), "incidents": [dict(r) for r in rows]}


# ---------------------------------------------------------------------------
# INCIDENT TIMELINE & REVIEWS
# ---------------------------------------------------------------------------

def action_add_incident_action(conn, args):
    """Add a timeline action to an incident."""
    incident_id = getattr(args, 'incident_id', None)
    if not incident_id:
        return {"status": "error", "message": "Missing --incident-id argument"}

    row = conn.execute("SELECT id FROM incidents WHERE id = ?", (int(incident_id),)).fetchone()
    if not row:
        return {"status": "error", "message": f"Incident not found with id: {incident_id}"}

    action_type = getattr(args, 'action_type', None)
    if not action_type:
        return {"status": "error", "message": "Missing --action-type argument"}

    title = args.title
    if not title:
        return {"status": "error", "message": "Missing --title argument"}

    cursor = conn.execute(
        """INSERT INTO incident_actions (incident_id, action_type, title, description, outcome)
           VALUES (?, ?, ?, ?, ?)""",
        (int(incident_id), action_type, title,
         args.description or None, getattr(args, 'outcome', None))
    )
    conn.commit()
    return {"status": "created", "id": cursor.lastrowid, "incident_id": int(incident_id), "action_type": action_type}


def action_list_incident_actions(conn, args):
    """List timeline actions for an incident."""
    incident_id = getattr(args, 'incident_id', None)
    if not incident_id:
        return {"status": "error", "message": "Missing --incident-id argument"}

    query = "SELECT * FROM incident_actions WHERE incident_id = ?"
    params = [int(incident_id)]

    action_type = getattr(args, 'action_type', None)
    if action_type:
        query += " AND action_type = ?"
        params.append(action_type)

    query += " ORDER BY action_taken_at ASC"
    rows = conn.execute(query, params).fetchall()
    return {"status": "ok", "count": len(rows), "actions": [dict(r) for r in rows]}


def action_add_incident_review(conn, args):
    """Add a post-incident review."""
    incident_id = getattr(args, 'incident_id', None)
    if not incident_id:
        return {"status": "error", "message": "Missing --incident-id argument"}

    row = conn.execute("SELECT id FROM incidents WHERE id = ?", (int(incident_id),)).fetchone()
    if not row:
        return {"status": "error", "message": f"Incident not found with id: {incident_id}"}

    conducted_by = getattr(args, 'conducted_by', None)
    if not conducted_by:
        return {"status": "error", "message": "Missing --conducted-by argument"}

    cursor = conn.execute(
        """INSERT INTO incident_reviews
           (incident_id, conducted_by, what_happened, what_went_well,
            what_went_wrong, lessons_learned, action_items, recommendations)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (int(incident_id), conducted_by,
         getattr(args, 'what_happened', None),
         getattr(args, 'what_went_well', None),
         getattr(args, 'what_went_wrong', None),
         getattr(args, 'lessons_learned', None),
         getattr(args, 'action_items', None),
         getattr(args, 'recommendations', None))
    )
    conn.commit()
    return {"status": "created", "id": cursor.lastrowid, "incident_id": int(incident_id), "conducted_by": conducted_by}


def action_update_incident_review(conn, args):
    """Update an incident review (e.g., mark as completed)."""
    if not args.id:
        return {"status": "error", "message": "Missing --id argument"}

    row = conn.execute("SELECT id FROM incident_reviews WHERE id = ?", (int(args.id),)).fetchone()
    if not row:
        return {"status": "error", "message": f"Incident review not found with id: {args.id}"}

    updates = []
    params = []
    if hasattr(args, 'is_completed') and args.is_completed is not None:
        updates.append("is_completed = ?")
        params.append(int(args.is_completed))
    if hasattr(args, 'what_happened') and args.what_happened:
        updates.append("what_happened = ?")
        params.append(args.what_happened)
    if hasattr(args, 'what_went_well') and args.what_went_well:
        updates.append("what_went_well = ?")
        params.append(args.what_went_well)
    if hasattr(args, 'what_went_wrong') and args.what_went_wrong:
        updates.append("what_went_wrong = ?")
        params.append(args.what_went_wrong)
    if hasattr(args, 'lessons_learned') and args.lessons_learned:
        updates.append("lessons_learned = ?")
        params.append(args.lessons_learned)
    if hasattr(args, 'recommendations') and args.recommendations:
        updates.append("recommendations = ?")
        params.append(args.recommendations)
    if hasattr(args, 'action_items') and args.action_items:
        updates.append("action_items = ?")
        params.append(args.action_items)

    if not updates:
        return {"status": "error", "message": "No fields to update"}

    set_clause = ", ".join(updates)
    conn.execute(f"UPDATE incident_reviews SET {set_clause} WHERE id = ?", params + [int(args.id)])
    conn.commit()
    return {"status": "updated", "id": int(args.id)}


def action_list_incident_reviews(conn, args):
    """List post-incident reviews for an incident."""
    incident_id = getattr(args, 'incident_id', None)
    if not incident_id:
        return {"status": "error", "message": "Missing --incident-id argument"}

    query = "SELECT * FROM incident_reviews WHERE incident_id = ?"
    params = [int(incident_id)]

    query += " ORDER BY review_date DESC"
    rows = conn.execute(query, params).fetchall()
    return {"status": "ok", "count": len(rows), "reviews": [dict(r) for r in rows]}


def action_incident_summary(conn, args):
    """Aggregate incident statistics: counts, MTTR, breakdowns."""
    rows = conn.execute("SELECT * FROM incidents").fetchall()
    incidents = [dict(r) for r in rows]

    total = len(incidents)
    if total == 0:
        return {
            "status": "ok",
            "total": 0,
            "mttr_hours": None,
            "by_severity": {},
            "by_type": {},
            "by_status": {},
            "open_count": 0,
            "resolved_count": 0,
        }

    by_severity = {}
    by_type = {}
    by_status = {}
    resolved_count = 0
    open_count = 0
    total_resolution_hours = 0
    resolved_with_times = 0

    for inc in incidents:
        sev = inc.get("severity") or "unknown"
        by_severity[sev] = by_severity.get(sev, 0) + 1

        itype = inc.get("type") or "unknown"
        by_type[itype] = by_type.get(itype, 0) + 1

        st = inc.get("status") or "unknown"
        by_status[st] = by_status.get(st, 0) + 1

        if st == "resolved":
            resolved_count += 1
            reported_at = inc.get("reported_at")
            resolved_at = inc.get("resolved_at")
            if reported_at and resolved_at:
                try:
                    start = datetime.fromisoformat(reported_at)
                    end = datetime.fromisoformat(resolved_at)
                    hours = (end - start).total_seconds() / 3600
                    total_resolution_hours += hours
                    resolved_with_times += 1
                except (ValueError, TypeError):
                    pass
        else:
            open_count += 1

    mttr_hours = round(total_resolution_hours / resolved_with_times, 2) if resolved_with_times > 0 else None

    return {
        "status": "ok",
        "total": total,
        "mttr_hours": mttr_hours,
        "by_severity": by_severity,
        "by_type": by_type,
        "by_status": by_status,
        "open_count": open_count,
        "resolved_count": resolved_count,
    }


def action_add_policy(conn, args):
    """Record a policy."""
    title = args.title
    if not title:
        return {"status": "error", "message": "Missing --title argument"}

    cursor = conn.execute(
        """INSERT INTO policies (title, type, status, content_path)
           VALUES (?, ?, ?, ?)""",
        (title, args.type or "information_security", args.status or "draft",
         getattr(args, 'content_path', None))
    )
    conn.commit()

    return {"status": "created", "id": cursor.lastrowid, "title": title, "policy_status": args.status or "draft"}


def action_list_policies(conn, args):
    """List policies with optional filters."""
    query = "SELECT * FROM policies WHERE 1=1"
    params = []

    if args.type:
        query += " AND type = ?"
        params.append(args.type)
    if args.status:
        query += " AND status = ?"
        params.append(args.status)
    if hasattr(args, 'review_due') and args.review_due:
        query += " AND review_date < ? AND status NOT IN ('archived', 'draft')"
        params.append(datetime.now().isoformat())

    query += " ORDER BY created_at DESC"
    rows = conn.execute(query, params).fetchall()
    return {"status": "ok", "count": len(rows), "policies": [dict(r) for r in rows]}


def action_update_policy(conn, args):
    """Update a policy record."""
    if not args.id:
        return {"status": "error", "message": "Missing --id argument"}
    row = conn.execute("SELECT id FROM policies WHERE id = ?", (int(args.id),)).fetchone()
    if not row:
        return {"status": "error", "message": f"Policy not found with id: {args.id}"}

    updates = []
    params = []
    if args.status:
        updates.append("status = ?")
        params.append(args.status)
    if args.title:
        updates.append("title = ?")
        params.append(args.title)
    if args.type:
        updates.append("type = ?")
        params.append(args.type)
    if hasattr(args, 'version') and args.version:
        updates.append("version = ?")
        params.append(args.version)
    if hasattr(args, 'content_path') and args.content_path:
        updates.append("content_path = ?")
        params.append(args.content_path)
    if hasattr(args, 'approved_by') and args.approved_by:
        updates.append("approved_by = ?")
        params.append(args.approved_by)
        updates.append("approved_at = datetime('now')")
    if hasattr(args, 'review_date') and args.review_date:
        updates.append("review_date = ?")
        params.append(args.review_date)
    if hasattr(args, 'notes') and args.notes:
        updates.append("notes = ?")
        params.append(args.notes)

    if not updates:
        return {"status": "error", "message": "No fields to update"}

    updates.append("last_updated = datetime('now')")
    set_clause = ", ".join(updates)
    conn.execute(f"UPDATE policies SET {set_clause} WHERE id = ?", params + [int(args.id)])
    conn.commit()
    return {"status": "updated", "id": int(args.id)}


# ===========================================================================
# POLICY WORKFLOWS
# ===========================================================================


def action_create_policy_version(conn, args):
    """Create a new version of an existing policy."""
    policy_id = getattr(args, 'policy_id', None)
    if not policy_id:
        return {"status": "error", "message": "Missing --policy-id argument"}

    parent = conn.execute("SELECT * FROM policies WHERE id = ?", (int(policy_id),)).fetchone()
    if not parent:
        return {"status": "error", "message": f"Policy not found with id: {policy_id}"}

    parent = dict(parent)

    # Parse version and increment major number
    try:
        major = int(parent["version"].split(".")[0])
    except (ValueError, AttributeError, IndexError):
        major = 1
    new_version = f"{major + 1}.0"

    change_summary = getattr(args, 'change_summary', None)

    cursor = conn.execute(
        """INSERT INTO policies (title, type, version, status, content_path, parent_version_id,
           owner, change_summary)
           VALUES (?, ?, ?, 'draft', ?, ?, ?, ?)""",
        (parent["title"], parent["type"], new_version, parent.get("content_path"),
         int(policy_id), parent.get("owner"), change_summary)
    )
    conn.commit()

    return {
        "status": "created",
        "id": cursor.lastrowid,
        "title": parent["title"],
        "version": new_version,
        "parent_version_id": int(policy_id),
        "policy_status": "draft"
    }


def action_list_policy_versions(conn, args):
    """List all versions in a policy chain."""
    policy_id = getattr(args, 'policy_id', None)
    if not policy_id:
        return {"status": "error", "message": "Missing --policy-id argument"}

    # Walk up to find root
    current_id = int(policy_id)
    visited = set()
    while current_id and current_id not in visited:
        visited.add(current_id)
        row = conn.execute(
            "SELECT id, parent_version_id FROM policies WHERE id = ?", (current_id,)
        ).fetchone()
        if not row:
            break
        if row["parent_version_id"] is None:
            break
        current_id = row["parent_version_id"]

    root_id = current_id

    # BFS from root collecting all descendants in version chain
    versions = []
    queue = [root_id]
    while queue:
        cid = queue.pop(0)
        row = conn.execute("SELECT * FROM policies WHERE id = ?", (cid,)).fetchone()
        if row:
            versions.append(dict(row))
            children = conn.execute(
                "SELECT id FROM policies WHERE parent_version_id = ? ORDER BY id", (cid,)
            ).fetchall()
            for child in children:
                queue.append(child["id"])

    return {"status": "ok", "count": len(versions), "versions": versions}


def action_submit_policy_approval(conn, args):
    """Submit a policy for approval."""
    policy_id = getattr(args, 'policy_id', None)
    if not policy_id:
        return {"status": "error", "message": "Missing --policy-id argument"}

    requested_by = getattr(args, 'requested_by', None)
    if not requested_by:
        return {"status": "error", "message": "Missing --requested-by argument"}

    # Verify policy exists
    policy = conn.execute("SELECT id FROM policies WHERE id = ?", (int(policy_id),)).fetchone()
    if not policy:
        return {"status": "error", "message": f"Policy not found with id: {policy_id}"}

    request_notes = getattr(args, 'request_notes', None)

    cursor = conn.execute(
        """INSERT INTO policy_approvals (policy_id, requested_by, request_notes)
           VALUES (?, ?, ?)""",
        (int(policy_id), requested_by, request_notes)
    )

    # Update policy status to pending_approval
    conn.execute(
        "UPDATE policies SET status = 'pending_approval', last_updated = datetime('now') WHERE id = ?",
        (int(policy_id),)
    )
    conn.commit()

    return {
        "status": "created",
        "id": cursor.lastrowid,
        "policy_id": int(policy_id),
        "requested_by": requested_by,
        "decision": "pending"
    }


def action_review_policy_approval(conn, args):
    """Review a policy approval request (approve/reject/changes_requested)."""
    if not args.id:
        return {"status": "error", "message": "Missing --id argument"}

    decision = getattr(args, 'decision', None)
    if not decision:
        return {"status": "error", "message": "Missing --decision argument"}

    if decision not in ('approved', 'rejected', 'changes_requested'):
        return {"status": "error", "message": f"Invalid decision: {decision}. Must be approved, rejected, or changes_requested"}

    reviewed_by = getattr(args, 'reviewed_by', None)
    if not reviewed_by:
        return {"status": "error", "message": "Missing --reviewed-by argument"}

    # Get approval record
    approval = conn.execute(
        "SELECT * FROM policy_approvals WHERE id = ?", (int(args.id),)
    ).fetchone()
    if not approval:
        return {"status": "error", "message": f"Approval not found with id: {args.id}"}

    decision_notes = getattr(args, 'notes', None)

    conn.execute(
        """UPDATE policy_approvals SET decision = ?, reviewed_by = ?, reviewed_at = datetime('now'),
           decision_notes = ? WHERE id = ?""",
        (decision, reviewed_by, decision_notes, int(args.id))
    )

    policy_id = approval["policy_id"]

    if decision == "approved":
        conn.execute(
            """UPDATE policies SET status = 'approved', approved_by = ?, approved_at = datetime('now'),
               last_updated = datetime('now') WHERE id = ?""",
            (reviewed_by, policy_id)
        )
    else:
        # rejected or changes_requested: revert to draft
        conn.execute(
            "UPDATE policies SET status = 'draft', last_updated = datetime('now') WHERE id = ?",
            (policy_id,)
        )

    conn.commit()

    return {
        "status": "updated",
        "id": int(args.id),
        "policy_id": policy_id,
        "decision": decision,
        "reviewed_by": reviewed_by
    }


def action_list_policy_approvals(conn, args):
    """List policy approval records (audit trail)."""
    query = "SELECT * FROM policy_approvals WHERE 1=1"
    params = []

    policy_id = getattr(args, 'policy_id', None)
    if policy_id:
        query += " AND policy_id = ?"
        params.append(int(policy_id))

    decision = getattr(args, 'decision', None)
    if decision:
        query += " AND decision = ?"
        params.append(decision)

    query += " ORDER BY created_at DESC"
    rows = conn.execute(query, params).fetchall()

    return {"status": "ok", "count": len(rows), "approvals": [dict(r) for r in rows]}


def action_require_policy_acknowledgment(conn, args):
    """Create acknowledgment requirements for multiple users."""
    policy_id = getattr(args, 'policy_id', None)
    if not policy_id:
        return {"status": "error", "message": "Missing --policy-id argument"}

    users = getattr(args, 'users', None)
    if not users:
        return {"status": "error", "message": "Missing --users argument (comma-separated names)"}

    # Verify policy exists
    policy = conn.execute("SELECT id FROM policies WHERE id = ?", (int(policy_id),)).fetchone()
    if not policy:
        return {"status": "error", "message": f"Policy not found with id: {policy_id}"}

    due_date = getattr(args, 'due_date', None)
    user_list = [u.strip() for u in users.split(",") if u.strip()]

    created = []
    skipped = []
    for user in user_list:
        try:
            conn.execute(
                """INSERT INTO policy_acknowledgments (policy_id, user_name, due_date, status)
                   VALUES (?, ?, ?, 'pending')""",
                (int(policy_id), user, due_date)
            )
            created.append(user)
        except sqlite3.IntegrityError:
            skipped.append(user)

    conn.commit()

    return {
        "status": "created",
        "policy_id": int(policy_id),
        "created_count": len(created),
        "created_for": created,
        "skipped": skipped
    }


def action_acknowledge_policy(conn, args):
    """Record a user's acknowledgment of a policy."""
    policy_id = getattr(args, 'policy_id', None)
    if not policy_id:
        return {"status": "error", "message": "Missing --policy-id argument"}

    user_name = getattr(args, 'user_name', None)
    if not user_name:
        return {"status": "error", "message": "Missing --user-name argument"}

    # Find the acknowledgment record
    row = conn.execute(
        "SELECT * FROM policy_acknowledgments WHERE policy_id = ? AND user_name = ?",
        (int(policy_id), user_name)
    ).fetchone()

    if not row:
        return {"status": "error", "message": f"No acknowledgment requirement found for user '{user_name}' on policy {policy_id}"}

    if row["status"] == "acknowledged":
        return {
            "status": "already_acknowledged",
            "id": row["id"],
            "user_name": user_name,
            "acknowledged_at": row["acknowledged_at"]
        }

    conn.execute(
        """UPDATE policy_acknowledgments SET status = 'acknowledged', acknowledged_at = datetime('now')
           WHERE id = ?""",
        (row["id"],)
    )
    conn.commit()

    return {
        "status": "acknowledged",
        "id": row["id"],
        "user_name": user_name,
        "policy_id": int(policy_id)
    }


def action_list_policy_acknowledgments(conn, args):
    """List policy acknowledgments with rate calculation."""
    query = "SELECT * FROM policy_acknowledgments WHERE 1=1"
    params = []

    policy_id = getattr(args, 'policy_id', None)
    if policy_id:
        query += " AND policy_id = ?"
        params.append(int(policy_id))

    pending = getattr(args, 'pending', False)
    if pending:
        query += " AND status = 'pending'"

    overdue = getattr(args, 'overdue', False)
    if overdue:
        query += " AND status = 'pending' AND due_date < ?"
        params.append(datetime.now().strftime("%Y-%m-%d"))

    query += " ORDER BY created_at DESC"
    rows = conn.execute(query, params).fetchall()
    acks = [dict(r) for r in rows]

    # Calculate acknowledgment rate
    total = len(acks)
    acknowledged = sum(1 for a in acks if a["status"] == "acknowledged")
    rate = round(acknowledged / total * 100, 1) if total > 0 else None

    return {
        "status": "ok",
        "count": total,
        "acknowledgment_rate": rate,
        "acknowledged_count": acknowledged,
        "pending_count": total - acknowledged,
        "acknowledgments": acks
    }


# ===========================================================================
# CONTROL EFFECTIVENESS & TEST RESULTS
# ===========================================================================


def action_update_control_effectiveness(conn, args):
    """Update control effectiveness score and maturity level."""
    if not args.id:
        return {"status": "error", "message": "Missing --id argument"}

    row = conn.execute("SELECT id FROM controls WHERE id = ?", (int(args.id),)).fetchone()
    if not row:
        return {"status": "error", "message": f"Control not found with id: {args.id}"}

    updates = []
    params = []

    effectiveness_score = getattr(args, 'effectiveness_score', None)
    if effectiveness_score is not None:
        score = int(effectiveness_score)
        updates.append("effectiveness_score = ?")
        params.append(score)

        # Auto-compute effectiveness_rating
        if score >= 80:
            rating = "effective"
        elif score >= 50:
            rating = "partially_effective"
        else:
            rating = "ineffective"
        updates.append("effectiveness_rating = ?")
        params.append(rating)

    maturity_level = getattr(args, 'maturity_level', None)
    if maturity_level:
        valid = ("initial", "developing", "defined", "managed", "optimizing")
        if maturity_level not in valid:
            return {"status": "error", "message": f"Invalid maturity_level: {maturity_level}. Must be one of: {', '.join(valid)}"}
        updates.append("maturity_level = ?")
        params.append(maturity_level)

    if not updates:
        return {"status": "error", "message": "No fields to update. Provide --effectiveness-score or --maturity-level"}

    updates.append("last_updated = datetime('now')")
    set_clause = ", ".join(updates)
    conn.execute(f"UPDATE controls SET {set_clause} WHERE id = ?", params + [int(args.id)])
    conn.commit()

    return {"status": "updated", "id": int(args.id)}


def action_list_controls_by_maturity(conn, args):
    """List controls grouped by maturity level with distribution."""
    query = "SELECT * FROM controls WHERE maturity_level IS NOT NULL"
    params = []

    maturity_level = getattr(args, 'maturity_level', None)
    if maturity_level:
        query += " AND maturity_level = ?"
        params.append(maturity_level)

    query += " ORDER BY maturity_level, control_id"
    rows = conn.execute(query, params).fetchall()
    controls = [dict(r) for r in rows]

    # Maturity distribution
    distribution = {}
    for c in controls:
        lvl = c["maturity_level"]
        distribution[lvl] = distribution.get(lvl, 0) + 1

    return {
        "status": "ok",
        "count": len(controls),
        "maturity_distribution": distribution,
        "controls": controls
    }


def action_add_test_result(conn, args):
    """Record a test result, optionally linked to a control."""
    test_name = getattr(args, 'test_name', None)
    if not test_name:
        return {"status": "error", "message": "Missing --test-name argument"}

    status = args.status
    if not status:
        return {"status": "error", "message": "Missing --status argument"}

    control_id = getattr(args, 'control_id_ref', None)
    items_checked = getattr(args, 'items_checked', None) or 0
    items_passed = getattr(args, 'items_passed', None) or 0
    items_failed = getattr(args, 'items_failed', None) or 0
    findings = getattr(args, 'findings', None)
    duration_ms = getattr(args, 'duration_ms', None)

    # Verify control exists if provided
    if control_id:
        ctrl = conn.execute("SELECT id FROM controls WHERE id = ?", (int(control_id),)).fetchone()
        if not ctrl:
            return {"status": "error", "message": f"Control not found with id: {control_id}"}

    cursor = conn.execute(
        """INSERT INTO test_results (test_name, control_id, status, items_checked, items_passed,
           items_failed, findings, duration_ms)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (test_name, int(control_id) if control_id else None, status,
         int(items_checked), int(items_passed), int(items_failed),
         findings, int(duration_ms) if duration_ms else None)
    )

    # Update control's last_tested_at if linked
    if control_id:
        conn.execute(
            "UPDATE controls SET last_tested_at = datetime('now'), last_updated = datetime('now') WHERE id = ?",
            (int(control_id),)
        )

    conn.commit()

    return {"status": "created", "id": cursor.lastrowid, "test_name": test_name, "result_status": status}


def action_list_test_results(conn, args):
    """List test results with optional filters and pass_rate calculation."""
    query = "SELECT * FROM test_results WHERE 1=1"
    params = []

    control_id = getattr(args, 'control_id_ref', None)
    if control_id:
        query += " AND control_id = ?"
        params.append(int(control_id))

    if args.status:
        query += " AND status = ?"
        params.append(args.status)

    test_name = getattr(args, 'test_name', None)
    if test_name:
        query += " AND test_name = ?"
        params.append(test_name)

    query += " ORDER BY tested_at DESC"
    rows = conn.execute(query, params).fetchall()
    results = [dict(r) for r in rows]

    # Calculate pass_rate
    total = len(results)
    passed = sum(1 for r in results if r["status"] == "passed")
    pass_rate = round(passed / total * 100, 1) if total > 0 else None

    return {
        "status": "ok",
        "count": total,
        "pass_rate": pass_rate,
        "results": results
    }


def action_test_summary(conn, args):
    """Aggregate test result statistics."""
    rows = conn.execute("SELECT * FROM test_results ORDER BY tested_at ASC").fetchall()
    results = [dict(r) for r in rows]

    total = len(results)
    if total == 0:
        return {
            "status": "ok",
            "total_runs": 0,
            "pass_rate": None,
            "by_status": {},
            "by_test": {},
        }

    # Counts by status
    by_status = {}
    for r in results:
        s = r["status"]
        by_status[s] = by_status.get(s, 0) + 1

    # Counts by test name
    by_test = {}
    for r in results:
        name = r["test_name"]
        if name not in by_test:
            by_test[name] = {"runs": 0, "passed": 0, "failed": 0}
        by_test[name]["runs"] += 1
        if r["status"] == "passed":
            by_test[name]["passed"] += 1
        elif r["status"] == "failed":
            by_test[name]["failed"] += 1

    # Overall pass_rate
    passed = by_status.get("passed", 0)
    pass_rate = round(passed / total * 100, 1) if total > 0 else None

    # Trend: compare first half to second half
    trend = "unknown"
    if total >= 4:
        mid = total // 2
        first_half = results[:mid]
        second_half = results[mid:]
        first_pass = sum(1 for r in first_half if r["status"] == "passed") / len(first_half)
        second_pass = sum(1 for r in second_half if r["status"] == "passed") / len(second_half)
        delta = second_pass - first_pass
        if delta > 0.1:
            trend = "improving"
        elif delta < -0.1:
            trend = "declining"
        else:
            trend = "stable"

    return {
        "status": "ok",
        "total_runs": total,
        "pass_rate": pass_rate,
        "by_status": by_status,
        "by_test": by_test,
        "trend": trend,
    }


def action_score_history(conn, args):
    """Historical compliance scores."""
    query = "SELECT * FROM compliance_scores WHERE 1=1"
    params = []

    if args.framework:
        query += " AND framework_slug = ?"
        params.append(args.framework)

    days = int(getattr(args, 'days', None) or 30)
    cutoff = (datetime.now() - timedelta(days=days)).isoformat()
    query += " AND calculated_at >= ?"
    params.append(cutoff)

    query += " ORDER BY calculated_at ASC"
    rows = conn.execute(query, params).fetchall()
    scores = [dict(r) for r in rows]

    # Calculate trend
    trend = "unknown"
    if len(scores) >= 2:
        first = scores[0]["score"]
        last = scores[-1]["score"]
        delta = last - first
        if delta > 2:
            trend = "improving"
        elif delta < -2:
            trend = "declining"
        else:
            trend = "stable"

    # Stats
    score_values = [s["score"] for s in scores]
    stats = {}
    if score_values:
        stats = {
            "min": round(min(score_values), 2),
            "max": round(max(score_values), 2),
            "avg": round(sum(score_values) / len(score_values), 2),
            "current": round(score_values[-1], 2),
        }

    return {
        "status": "ok",
        "period_days": days,
        "data_points": len(scores),
        "trend": trend,
        "stats": stats,
        "scores": scores,
    }


def action_list_mappings(conn, args):
    """Cross-framework control mappings."""
    if not hasattr(args, 'source_framework') or not args.source_framework:
        return {"status": "error", "message": "Missing --source-framework argument"}
    if not hasattr(args, 'target_framework') or not args.target_framework:
        return {"status": "error", "message": "Missing --target-framework argument"}

    rows = conn.execute(
        """SELECT * FROM control_mappings
           WHERE source_framework = ? AND target_framework = ?
           ORDER BY source_control_id""",
        (args.source_framework, args.target_framework)
    ).fetchall()

    return {"status": "ok", "count": len(rows), "mappings": [dict(r) for r in rows]}


def action_gap_analysis(conn, args):
    """Identify compliance gaps for a framework."""
    if not args.framework:
        return {"status": "error", "message": "Missing --framework argument"}

    fw = conn.execute("SELECT id, name FROM frameworks WHERE slug = ? AND status = 'active'", (args.framework,)).fetchone()
    if not fw:
        return {"status": "error", "message": f"Framework '{args.framework}' not found or inactive"}

    # Find gaps: not_started controls, controls without evidence, expired evidence
    not_started = conn.execute(
        "SELECT * FROM controls WHERE framework_id = ? AND status = 'not_started' ORDER BY priority DESC",
        (fw["id"],)
    ).fetchall()

    # Controls without any evidence linked
    no_evidence = conn.execute(
        """SELECT c.* FROM controls c
           WHERE c.framework_id = ? AND c.status = 'complete'
           AND c.id NOT IN (SELECT control_id FROM evidence_controls)
           ORDER BY c.priority DESC""",
        (fw["id"],)
    ).fetchall()

    # Controls with expired evidence
    expired_evidence_controls = conn.execute(
        """SELECT DISTINCT c.* FROM controls c
           JOIN evidence_controls ec ON c.id = ec.control_id
           JOIN evidence e ON ec.evidence_id = e.id
           WHERE c.framework_id = ? AND e.status = 'expired'
           ORDER BY c.priority DESC""",
        (fw["id"],)
    ).fetchall()

    # Overdue controls
    overdue = conn.execute(
        """SELECT * FROM controls WHERE framework_id = ? AND due_date < ?
           AND status NOT IN ('complete', 'rejected')
           ORDER BY priority DESC""",
        (fw["id"], datetime.now().isoformat())
    ).fetchall()

    total = conn.execute("SELECT COUNT(*) FROM controls WHERE framework_id = ?", (fw["id"],)).fetchone()[0]

    gaps = []
    for c in not_started:
        d = dict(c)
        priority_score = d.get("priority", 3) * 3  # not_started is worst
        d["gap_type"] = "not_started"
        d["priority_score"] = priority_score
        d["effort_days"] = max(1, d.get("priority", 3))
        d["remediation_phase"] = "immediate" if d.get("priority", 3) >= 4 else "short_term"
        gaps.append(d)

    for c in no_evidence:
        d = dict(c)
        d["gap_type"] = "missing_evidence"
        d["priority_score"] = d.get("priority", 3) * 2
        d["effort_days"] = 1
        d["remediation_phase"] = "short_term"
        gaps.append(d)

    for c in expired_evidence_controls:
        d = dict(c)
        d["gap_type"] = "expired_evidence"
        d["priority_score"] = d.get("priority", 3) * 2
        d["effort_days"] = 1
        d["remediation_phase"] = "immediate"
        gaps.append(d)

    for c in overdue:
        d = dict(c)
        d["gap_type"] = "overdue"
        d["priority_score"] = d.get("priority", 3) * 2.5
        d["effort_days"] = max(1, d.get("priority", 3) - 1)
        d["remediation_phase"] = "immediate"
        gaps.append(d)

    # Sort by priority score descending
    gaps.sort(key=lambda g: g.get("priority_score", 0), reverse=True)

    complete = conn.execute("SELECT COUNT(*) FROM controls WHERE framework_id = ? AND status = 'complete'", (fw["id"],)).fetchone()[0]
    readiness = round((complete / total * 100) if total > 0 else 0, 2)

    return {
        "status": "ok",
        "framework": args.framework,
        "total_controls": total,
        "readiness_percent": readiness,
        "gap_count": len(gaps),
        "gaps": gaps,
        "summary": {
            "not_started": len(not_started),
            "missing_evidence": len(no_evidence),
            "expired_evidence": len(expired_evidence_controls),
            "overdue": len(overdue),
        },
    }



def action_export_evidence(conn, args):
    """Export evidence package as ZIP for auditors."""
    if not args.framework:
        return {"status": "error", "message": "Missing --framework argument"}
    if not args.output_dir:
        return {"status": "error", "message": "Missing --output-dir argument"}

    # Import the export module
    scripts_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, scripts_dir)
    from export_evidence import export_evidence
    sys.path.pop(0)

    conn.close()  # Close our connection; export_evidence opens its own
    return export_evidence(args.db_path, args.framework, args.output_dir)


def action_generate_report(conn, args):
    """Generate HTML compliance report."""
    if not args.framework:
        return {"status": "error", "message": "Missing --framework argument"}

    output_dir = args.output_dir or os.path.expanduser("~/.openclaw/grc/reports")

    # Import the report module
    scripts_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, scripts_dir)
    from generate_report import generate_report
    sys.path.pop(0)

    conn.close()  # Close our connection; generate_report opens its own
    return generate_report(args.db_path, args.framework, output_dir)


# ---------------------------------------------------------------------------
# ASSET OPERATIONS
# ---------------------------------------------------------------------------

def action_add_asset(conn, args):
    """Register an asset."""
    name = args.name
    if not name:
        return {"status": "error", "message": "Missing --name argument"}
    criticality = getattr(args, 'criticality', None) or "medium"
    status = getattr(args, 'status', None) or "active"
    lifecycle_stage = getattr(args, 'lifecycle_stage', None) or "in_use"
    data_classification = getattr(args, 'data_classification', None) or "internal"
    discovery_source = getattr(args, 'discovery_source', None) or "manual"
    cursor = conn.execute(
        """INSERT INTO assets (name, type, criticality, owner, description, status,
                               ip_address, hostname, os_type, software_version,
                               lifecycle_stage, data_classification, discovery_source,
                               encryption_status, backup_status, patch_status,
                               created_at, updated_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            name,
            getattr(args, 'type', None),
            criticality,
            getattr(args, 'owner', None),
            getattr(args, 'description', None),
            status,
            getattr(args, 'ip_address', None),
            getattr(args, 'hostname', None),
            getattr(args, 'os_type', None),
            getattr(args, 'software_version', None),
            lifecycle_stage,
            data_classification,
            discovery_source,
            getattr(args, 'encryption_status', None),
            getattr(args, 'backup_status', None),
            getattr(args, 'patch_status', None),
            datetime.now().isoformat(),
            datetime.now().isoformat(),
        ),
    )
    conn.commit()
    return {
        "status": "created",
        "id": cursor.lastrowid,
        "name": name,
        "criticality": criticality,
    }


def action_list_assets(conn, args):
    """List assets with optional filters."""
    query = "SELECT * FROM assets WHERE 1=1"
    params = []
    if getattr(args, 'type', None):
        query += " AND type = ?"
        params.append(args.type)
    if getattr(args, 'criticality', None):
        query += " AND criticality = ?"
        params.append(args.criticality)
    if getattr(args, 'status', None):
        query += " AND status = ?"
        params.append(args.status)
    if getattr(args, 'lifecycle_stage', None):
        query += " AND lifecycle_stage = ?"
        params.append(args.lifecycle_stage)
    if getattr(args, 'data_classification', None):
        query += " AND data_classification = ?"
        params.append(args.data_classification)
    if getattr(args, 'discovery_source', None):
        query += " AND discovery_source = ?"
        params.append(args.discovery_source)
    query += " ORDER BY criticality DESC, name ASC"
    rows = conn.execute(query, params).fetchall()
    return {"status": "ok", "count": len(rows), "assets": [dict(r) for r in rows]}


def action_update_asset(conn, args):
    """Update an existing asset."""
    asset_id = getattr(args, 'id', None)
    if not asset_id:
        return {"status": "error", "message": "Missing --id argument"}

    updatable_fields = {
        "name": getattr(args, 'name', None),
        "type": getattr(args, 'type', None),
        "criticality": getattr(args, 'criticality', None),
        "owner": getattr(args, 'owner', None),
        "description": getattr(args, 'description', None),
        "status": getattr(args, 'status', None),
        "ip_address": getattr(args, 'ip_address', None),
        "hostname": getattr(args, 'hostname', None),
        "os_type": getattr(args, 'os_type', None),
        "software_version": getattr(args, 'software_version', None),
        "lifecycle_stage": getattr(args, 'lifecycle_stage', None),
        "data_classification": getattr(args, 'data_classification', None),
        "discovery_source": getattr(args, 'discovery_source', None),
        "encryption_status": getattr(args, 'encryption_status', None),
        "backup_status": getattr(args, 'backup_status', None),
        "patch_status": getattr(args, 'patch_status', None),
    }

    # Build dynamic SET clause for provided fields only
    set_clauses = []
    params = []
    for col, val in updatable_fields.items():
        if val is not None:
            set_clauses.append(f"{col} = ?")
            params.append(val)

    if not set_clauses:
        return {"status": "error", "message": "No fields to update"}

    set_clauses.append("updated_at = ?")
    params.append(datetime.now().isoformat())
    params.append(asset_id)

    conn.execute(
        f"UPDATE assets SET {', '.join(set_clauses)} WHERE id = ?",
        params,
    )
    conn.commit()
    return {"status": "updated", "id": asset_id}




def action_link_asset_controls(conn, args):
    """Link an asset to one or more controls via the asset_controls junction table."""
    asset_id = getattr(args, 'id', None)
    if not asset_id:
        return {"status": "error", "message": "Missing --id argument"}
    control_ids = getattr(args, 'control_ids', None)
    if not control_ids:
        return {"status": "error", "message": "Missing --control-ids argument"}
    
    ids = [int(x.strip()) for x in str(control_ids).split(",")]
    linked = 0
    for cid in ids:
        try:
            conn.execute(
                "INSERT OR IGNORE INTO asset_controls (asset_id, control_id) VALUES (?, ?)",
                (int(asset_id), cid)
            )
            linked += 1
        except sqlite3.IntegrityError:
            pass  # duplicate link already exists
    conn.commit()
    return {"status": "ok", "asset_id": int(asset_id), "linked_controls": ids, "linked_count": linked}

# ---------------------------------------------------------------------------
# TRAINING OPERATIONS
# ---------------------------------------------------------------------------

def action_add_training_module(conn, args):
    """Create a training module."""
    title = getattr(args, 'title', None)
    if not title:
        return {"status": "error", "message": "Missing --title argument"}
    difficulty_level = getattr(args, 'difficulty_level', None) or "beginner"
    cursor = conn.execute(
        """INSERT INTO training_modules (title, category, description, duration,
                                          content_type, content_url, difficulty_level,
                                          requires_recertification, recertification_days,
                                          status, created_at, updated_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'active', ?, ?)""",
        (
            title,
            getattr(args, 'category', None),
            getattr(args, 'description', None),
            getattr(args, 'duration', None),
            getattr(args, 'content_type', None),
            getattr(args, 'content_url', None),
            difficulty_level,
            getattr(args, 'requires_recertification', None) or 0,
            getattr(args, 'recertification_days', None),
            datetime.now().isoformat(),
            datetime.now().isoformat(),
        ),
    )
    conn.commit()
    return {"status": "created", "id": cursor.lastrowid, "title": title}


def action_list_training_modules(conn, args):
    """List training modules with optional filters."""
    query = "SELECT * FROM training_modules WHERE 1=1"
    params = []
    if getattr(args, 'category', None):
        query += " AND category = ?"
        params.append(args.category)
    if getattr(args, 'status', None):
        query += " AND status = ?"
        params.append(args.status)
    if getattr(args, 'difficulty_level', None):
        query += " AND difficulty_level = ?"
        params.append(args.difficulty_level)
    query += " ORDER BY title ASC"
    rows = conn.execute(query, params).fetchall()
    return {"status": "ok", "count": len(rows), "modules": [dict(r) for r in rows]}


def action_add_training_assignment(conn, args):
    """Assign a training module to a user."""
    module_id = getattr(args, 'module_id', None)
    assignee = getattr(args, 'assignee', None)
    if not module_id:
        return {"status": "error", "message": "Missing --module-id argument"}
    if not assignee:
        return {"status": "error", "message": "Missing --assignee argument"}
    status = getattr(args, 'status', None) or "pending"
    cursor = conn.execute(
        """INSERT INTO training_assignments (module_id, assignee, due_date, status,
                                              assigned_at, created_at, updated_at)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (
            module_id,
            assignee,
            getattr(args, 'due_date', None),
            status,
            datetime.now().isoformat(),
            datetime.now().isoformat(),
            datetime.now().isoformat(),
        ),
    )
    conn.commit()
    return {
        "status": "created",
        "id": cursor.lastrowid,
        "module_id": module_id,
        "assignee": assignee,
    }


def action_list_training_assignments(conn, args):
    """List training assignments with optional filters."""
    query = "SELECT * FROM training_assignments WHERE 1=1"
    params = []
    if getattr(args, 'assignee', None):
        query += " AND assignee = ?"
        params.append(args.assignee)
    if getattr(args, 'status', None):
        query += " AND status = ?"
        params.append(args.status)
    if getattr(args, 'module_id', None):
        query += " AND module_id = ?"
        params.append(args.module_id)
    if getattr(args, 'overdue', None):
        query += " AND due_date < ? AND status != 'completed'"
        params.append(datetime.now().isoformat())
    query += " ORDER BY due_date ASC"
    rows = conn.execute(query, params).fetchall()
    return {"status": "ok", "count": len(rows), "assignments": [dict(r) for r in rows]}


def action_update_training_assignment(conn, args):
    """Update a training assignment (mark complete, set score, etc.)."""
    assignment_id = getattr(args, 'id', None)
    if not assignment_id:
        return {"status": "error", "message": "Missing --id argument"}

    updatable_fields = {
        "status": getattr(args, 'status', None),
        "score": getattr(args, 'score', None),
        "completed_at": getattr(args, 'completed_at', None),
        "certificate_path": getattr(args, 'certificate_path', None),
    }

    # Auto-set completed_at when status is 'completed' and no explicit value given
    if updatable_fields["status"] == "completed" and not updatable_fields["completed_at"]:
        updatable_fields["completed_at"] = datetime.now().isoformat()

    set_clauses = []
    params = []
    for col, val in updatable_fields.items():
        if val is not None:
            set_clauses.append(f"{col} = ?")
            params.append(val)

    if not set_clauses:
        return {"status": "error", "message": "No fields to update"}

    set_clauses.append("updated_at = ?")
    params.append(datetime.now().isoformat())
    params.append(assignment_id)

    conn.execute(
        f"UPDATE training_assignments SET {', '.join(set_clauses)} WHERE id = ?",
        params,
    )
    conn.commit()
    return {"status": "updated", "id": assignment_id}


# ---------------------------------------------------------------------------
# VULNERABILITY OPERATIONS
# ---------------------------------------------------------------------------

def action_add_vulnerability(conn, args):
    """Register a vulnerability finding."""
    title = getattr(args, 'title', None)
    if not title:
        return {"status": "error", "message": "Missing --title argument"}
    severity = getattr(args, 'severity', None) or "medium"
    cvss_score = getattr(args, 'cvss_score', None)
    cursor = conn.execute(
        """INSERT INTO vulnerabilities (title, cve_id, description, source,
                                         cvss_score, cvss_vector, severity,
                                         assignee, affected_assets, affected_packages,
                                         remediation_steps, due_date, status,
                                         created_at, updated_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'open', ?, ?)""",
        (
            title,
            getattr(args, 'cve_id', None),
            getattr(args, 'description', None),
            getattr(args, 'source', None),
            cvss_score,
            getattr(args, 'cvss_vector', None),
            severity,
            getattr(args, 'assignee', None),
            getattr(args, 'affected_assets', None),
            getattr(args, 'affected_packages', None),
            getattr(args, 'remediation_steps', None),
            getattr(args, 'due_date', None),
            datetime.now().isoformat(),
            datetime.now().isoformat(),
        ),
    )
    vuln_id = cursor.lastrowid

    # Optionally link to controls via vulnerability_controls junction table
    control_ids_raw = getattr(args, 'control_ids', None)
    if control_ids_raw:
        for cid in control_ids_raw.split(","):
            cid = cid.strip()
            if cid:
                conn.execute(
                    """INSERT INTO vulnerability_controls (vulnerability_id, control_id, created_at)
                       VALUES (?, ?, ?)""",
                    (vuln_id, cid, datetime.now().isoformat()),
                )

    conn.commit()
    return {
        "status": "created",
        "id": vuln_id,
        "title": title,
        "severity": severity,
        "cvss_score": cvss_score,
    }


def action_list_vulnerabilities(conn, args):
    """List vulnerabilities with optional filters."""
    query = "SELECT * FROM vulnerabilities WHERE 1=1"
    params = []
    if getattr(args, 'status', None):
        query += " AND status = ?"
        params.append(args.status)
    if getattr(args, 'severity', None):
        query += " AND severity = ?"
        params.append(args.severity)
    if getattr(args, 'source', None):
        query += " AND source = ?"
        params.append(args.source)
    if getattr(args, 'assignee', None):
        query += " AND assignee = ?"
        params.append(args.assignee)
    if getattr(args, 'min_cvss', None) is not None:
        query += " AND cvss_score >= ?"
        params.append(float(args.min_cvss))
    query += " ORDER BY cvss_score DESC NULLS LAST, severity DESC"
    rows = conn.execute(query, params).fetchall()
    return {
        "status": "ok",
        "count": len(rows),
        "vulnerabilities": [dict(r) for r in rows],
    }


def action_update_vulnerability(conn, args):
    """Update a vulnerability record."""
    vuln_id = getattr(args, 'id', None)
    if not vuln_id:
        return {"status": "error", "message": "Missing --id argument"}

    updatable_fields = {
        "status": getattr(args, 'status', None),
        "assignee": getattr(args, 'assignee', None),
        "remediation_steps": getattr(args, 'remediation_steps', None),
        "fix_version": getattr(args, 'fix_version', None),
        "resolved_at": getattr(args, 'resolved_at', None),
        "resolved_by": getattr(args, 'resolved_by', None),
        "risk_accepted": getattr(args, 'risk_accepted', None),
        "risk_acceptance_reason": getattr(args, 'risk_acceptance_reason', None),
    }

    # Auto-set resolved_at when status is 'resolved' and no explicit value given
    if updatable_fields["status"] == "resolved" and not updatable_fields["resolved_at"]:
        updatable_fields["resolved_at"] = datetime.now().isoformat()

    set_clauses = []
    params = []
    for col, val in updatable_fields.items():
        if val is not None:
            set_clauses.append(f"{col} = ?")
            params.append(val)

    if not set_clauses:
        return {"status": "error", "message": "No fields to update"}

    set_clauses.append("updated_at = ?")
    params.append(datetime.now().isoformat())
    params.append(vuln_id)

    conn.execute(
        f"UPDATE vulnerabilities SET {', '.join(set_clauses)} WHERE id = ?",
        params,
    )
    conn.commit()
    return {"status": "updated", "id": vuln_id}


# ---------------------------------------------------------------------------

def action_link_vulnerability_controls(conn, args):
    """Link a vulnerability to one or more controls via the vulnerability_controls junction table."""
    vuln_id = getattr(args, 'id', None)
    if not vuln_id:
        return {"status": "error", "message": "Missing --id argument"}
    control_ids = getattr(args, 'control_ids', None)
    if not control_ids:
        return {"status": "error", "message": "Missing --control-ids argument"}
    
    from datetime import datetime as dt
    ids = [int(x.strip()) for x in str(control_ids).split(",")]
    linked = 0
    for cid in ids:
        try:
            conn.execute(
                "INSERT OR IGNORE INTO vulnerability_controls (vulnerability_id, control_id, created_at) VALUES (?, ?, ?)",
                (int(vuln_id), cid, dt.now().isoformat())
            )
            linked += 1
        except sqlite3.IntegrityError:
            pass  # duplicate link already exists
    conn.commit()
    return {"status": "ok", "vulnerability_id": int(vuln_id), "linked_controls": ids, "linked_count": linked}


# ACCESS REVIEW OPERATIONS
# ---------------------------------------------------------------------------

def action_add_access_review(conn, args):
    """Create an access review campaign."""
    title = getattr(args, 'title', None)
    if not title:
        return {"status": "error", "message": "Missing --title argument"}
    description = getattr(args, 'description', None)
    scope_type = getattr(args, 'scope_type', None) or 'all_users'
    scope_config = getattr(args, 'scope_config', None)
    reviewer = getattr(args, 'reviewer', None)
    start_date = getattr(args, 'start_date', None)
    due_date = getattr(args, 'due_date', None)
    now = datetime.utcnow().isoformat()
    cursor = conn.execute(
        """INSERT INTO access_review_campaigns
           (title, description, scope_type, scope_config, reviewer, status,
            start_date, due_date, total_items, reviewed_items, approved_items,
            revoked_items, created_at, updated_at)
           VALUES (?, ?, ?, ?, ?, 'draft', ?, ?, 0, 0, 0, 0, ?, ?)""",
        (title, description, scope_type, scope_config, reviewer,
         start_date, due_date, now, now)
    )
    conn.commit()
    return {"status": "created", "id": cursor.lastrowid, "title": title}


def action_list_access_reviews(conn, args):
    """List access review campaigns with optional filters."""
    query = "SELECT * FROM access_review_campaigns WHERE 1=1"
    params = []
    status = getattr(args, 'status', None)
    if status:
        query += " AND status = ?"
        params.append(status)
    reviewer = getattr(args, 'reviewer', None)
    if reviewer:
        query += " AND reviewer = ?"
        params.append(reviewer)
    query += " ORDER BY created_at DESC"
    rows = conn.execute(query, params).fetchall()
    campaigns = [dict(r) for r in rows]
    return {"status": "ok", "count": len(campaigns), "campaigns": campaigns}


def action_update_access_review(conn, args):
    """Update an access review campaign."""
    review_id = getattr(args, 'id', None)
    if not review_id:
        return {"status": "error", "message": "Missing --id argument"}
    now = datetime.utcnow().isoformat()
    updates = []
    params = []
    new_status = getattr(args, 'status', None)
    if new_status:
        updates.append("status = ?")
        params.append(new_status)
        if new_status == 'completed':
            updates.append("completed_at = ?")
            params.append(now)
        if new_status == 'active':
            # Auto-set start_date if it is currently null
            row = conn.execute(
                "SELECT start_date FROM access_review_campaigns WHERE id = ?",
                (review_id,)
            ).fetchone()
            if row and not row['start_date']:
                updates.append("start_date = ?")
                params.append(now)
    reviewer = getattr(args, 'reviewer', None)
    if reviewer:
        updates.append("reviewer = ?")
        params.append(reviewer)
    due_date = getattr(args, 'due_date', None)
    if due_date:
        updates.append("due_date = ?")
        params.append(due_date)
    description = getattr(args, 'description', None)
    if description:
        updates.append("description = ?")
        params.append(description)
    if not updates:
        return {"status": "error", "message": "No fields to update"}
    updates.append("updated_at = ?")
    params.append(now)
    params.append(review_id)
    conn.execute(
        f"UPDATE access_review_campaigns SET {', '.join(updates)} WHERE id = ?",
        params
    )
    conn.commit()
    return {"status": "updated", "id": int(review_id)}


def action_add_review_item(conn, args):
    """Add an item to an access review campaign."""
    campaign_id = getattr(args, 'campaign_id', None)
    if not campaign_id:
        return {"status": "error", "message": "Missing --campaign-id argument"}
    user_name = getattr(args, 'user_name', None)
    if not user_name:
        return {"status": "error", "message": "Missing --user-name argument"}
    resource = getattr(args, 'resource', None)
    if not resource:
        return {"status": "error", "message": "Missing --resource argument"}
    current_access = getattr(args, 'current_access', None)
    now = datetime.utcnow().isoformat()
    cursor = conn.execute(
        """INSERT INTO access_review_items
           (campaign_id, user_name, resource, current_access, decision, created_at)
           VALUES (?, ?, ?, ?, 'pending', ?)""",
        (campaign_id, user_name, resource, current_access, now)
    )
    conn.execute(
        "UPDATE access_review_campaigns SET total_items = total_items + 1, updated_at = ? WHERE id = ?",
        (now, campaign_id)
    )
    conn.commit()
    return {"status": "created", "id": cursor.lastrowid, "campaign_id": int(campaign_id)}


def action_list_review_items(conn, args):
    """List items in an access review campaign."""
    campaign_id = getattr(args, 'campaign_id', None)
    if not campaign_id:
        return {"status": "error", "message": "Missing --campaign-id argument"}
    query = "SELECT * FROM access_review_items WHERE campaign_id = ?"
    params = [campaign_id]
    decision = getattr(args, 'decision', None)
    if decision:
        query += " AND decision = ?"
        params.append(decision)
    query += " ORDER BY user_name ASC"
    rows = conn.execute(query, params).fetchall()
    items = [dict(r) for r in rows]
    return {"status": "ok", "count": len(items), "items": items}


def action_update_review_item(conn, args):
    """Record a decision on an access review item."""
    item_id = getattr(args, 'id', None)
    if not item_id:
        return {"status": "error", "message": "Missing --id argument"}
    decision = getattr(args, 'decision', None)
    if not decision:
        return {"status": "error", "message": "Missing --decision argument"}
    if decision not in ('approved', 'revoked', 'modified'):
        return {"status": "error", "message": "Decision must be approved, revoked, or modified"}
    reviewer = getattr(args, 'reviewer', None)
    notes = getattr(args, 'notes', None)
    now = datetime.utcnow().isoformat()
    # Fetch the item to get its campaign_id and current decision
    row = conn.execute(
        "SELECT campaign_id, decision AS old_decision FROM access_review_items WHERE id = ?",
        (item_id,)
    ).fetchone()
    if not row:
        return {"status": "error", "message": f"Review item {item_id} not found"}
    campaign_id = row['campaign_id']
    old_decision = row['old_decision']
    # Update the item
    conn.execute(
        """UPDATE access_review_items
           SET decision = ?, reviewer = ?, notes = ?, reviewed_at = ?
           WHERE id = ?""",
        (decision, reviewer, notes, now, item_id)
    )
    # Update campaign counters
    # Increment reviewed_items only if the old decision was 'pending'
    if old_decision == 'pending':
        conn.execute(
            "UPDATE access_review_campaigns SET reviewed_items = reviewed_items + 1, updated_at = ? WHERE id = ?",
            (now, campaign_id)
        )
    # Decrement old counter if it was not pending (i.e. changing a previous decision)
    if old_decision == 'approved':
        conn.execute(
            "UPDATE access_review_campaigns SET approved_items = approved_items - 1 WHERE id = ?",
            (campaign_id,)
        )
    elif old_decision == 'revoked':
        conn.execute(
            "UPDATE access_review_campaigns SET revoked_items = revoked_items - 1 WHERE id = ?",
            (campaign_id,)
        )
    # Increment new counter
    if decision == 'approved':
        conn.execute(
            "UPDATE access_review_campaigns SET approved_items = approved_items + 1, updated_at = ? WHERE id = ?",
            (now, campaign_id)
        )
    elif decision == 'revoked':
        conn.execute(
            "UPDATE access_review_campaigns SET revoked_items = revoked_items + 1, updated_at = ? WHERE id = ?",
            (now, campaign_id)
        )
    conn.commit()
    return {"status": "updated", "id": int(item_id), "decision": decision}


# ---------------------------------------------------------------------------
# QUESTIONNAIRE OPERATIONS
# ---------------------------------------------------------------------------

def action_add_questionnaire_template(conn, args):
    """Create a questionnaire template."""
    title = getattr(args, 'title', None)
    if not title:
        return {"status": "error", "message": "Missing --title argument"}
    description = getattr(args, 'description', None)
    category = getattr(args, 'category', None) or 'security_review'
    questions_json = getattr(args, 'questions', None)
    question_count = 0
    if questions_json:
        try:
            questions_list = json.loads(questions_json)
            question_count = len(questions_list)
        except (json.JSONDecodeError, TypeError):
            return {"status": "error", "message": "Invalid --questions JSON"}
    now = datetime.utcnow().isoformat()
    cursor = conn.execute(
        """INSERT INTO questionnaire_templates
           (title, description, category, questions, total_questions, status, created_at, updated_at)
           VALUES (?, ?, ?, ?, ?, 'active', ?, ?)""",
        (title, description, category, questions_json, question_count, now, now)
    )
    conn.commit()
    return {"status": "created", "id": cursor.lastrowid, "title": title, "question_count": question_count}


def action_list_questionnaire_templates(conn, args):
    """List questionnaire templates with optional filters."""
    query = "SELECT * FROM questionnaire_templates WHERE 1=1"
    params = []
    category = getattr(args, 'category', None)
    if category:
        query += " AND category = ?"
        params.append(category)
    status = getattr(args, 'status', None)
    if status:
        query += " AND status = ?"
        params.append(status)
    query += " ORDER BY title ASC"
    rows = conn.execute(query, params).fetchall()
    templates = [dict(r) for r in rows]
    return {"status": "ok", "count": len(templates), "templates": templates}


def action_add_questionnaire_response(conn, args):
    """Create a new questionnaire response for a template."""
    template_id = getattr(args, 'template_id', None)
    if not template_id:
        return {"status": "error", "message": "Missing --template-id argument"}
    respondent = getattr(args, 'respondent', None)
    if not respondent:
        return {"status": "error", "message": "Missing --respondent argument"}
    vendor_id = getattr(args, 'vendor_id', None)
    # Look up the template to get total_questions
    tmpl = conn.execute(
        "SELECT questions, total_questions FROM questionnaire_templates WHERE id = ?",
        (template_id,)
    ).fetchone()
    if not tmpl:
        return {"status": "error", "message": f"Template {template_id} not found"}
    total_questions = tmpl['total_questions'] or 0
    now = datetime.utcnow().isoformat()
    cursor = conn.execute(
        """INSERT INTO questionnaire_responses
           (template_id, respondent, vendor_id, status, total_questions, answered_questions,
            created_at, updated_at)
           VALUES (?, ?, ?, 'draft', ?, 0, ?, ?)""",
        (template_id, respondent, vendor_id, total_questions, now, now)
    )
    conn.commit()
    return {
        "status": "created",
        "id": cursor.lastrowid,
        "template_id": int(template_id),
        "respondent": respondent,
        "total_questions": total_questions,
    }


def action_list_questionnaire_responses(conn, args):
    """List questionnaire responses with optional filters."""
    query = "SELECT * FROM questionnaire_responses WHERE 1=1"
    params = []
    status = getattr(args, 'status', None)
    if status:
        query += " AND status = ?"
        params.append(status)
    template_id = getattr(args, 'template_id', None)
    if template_id:
        query += " AND template_id = ?"
        params.append(template_id)
    vendor_id = getattr(args, 'vendor_id', None)
    if vendor_id:
        query += " AND vendor_id = ?"
        params.append(vendor_id)
    respondent = getattr(args, 'respondent', None)
    if respondent:
        query += " AND respondent = ?"
        params.append(respondent)
    query += " ORDER BY created_at DESC"
    rows = conn.execute(query, params).fetchall()
    responses = [dict(r) for r in rows]
    return {"status": "ok", "count": len(responses), "responses": responses}


def action_add_questionnaire_answer(conn, args):
    """Record an answer to a questionnaire question."""
    response_id = getattr(args, 'response_id', None)
    if not response_id:
        return {"status": "error", "message": "Missing --response-id argument"}
    question_index = getattr(args, 'question_index', None)
    if question_index is None:
        return {"status": "error", "message": "Missing --question-index argument"}
    answer_text = getattr(args, 'answer_text', None)
    if not answer_text:
        return {"status": "error", "message": "Missing --answer-text argument"}
    now = datetime.utcnow().isoformat()
    cursor = conn.execute(
        """INSERT INTO questionnaire_answers
           (response_id, question_index, answer_text, created_at)
           VALUES (?, ?, ?, ?)""",
        (response_id, question_index, answer_text, now)
    )
    # Increment answered_questions on the parent response
    conn.execute(
        "UPDATE questionnaire_responses SET answered_questions = answered_questions + 1, updated_at = ? WHERE id = ?",
        (now, response_id)
    )
    # Check if all questions are now answered
    resp = conn.execute(
        "SELECT answered_questions, total_questions FROM questionnaire_responses WHERE id = ?",
        (response_id,)
    ).fetchone()
    if resp and resp['total_questions'] and resp['answered_questions'] >= resp['total_questions']:
        conn.execute(
            "UPDATE questionnaire_responses SET status = 'completed', submitted_at = ?, updated_at = ? WHERE id = ?",
            (now, now, response_id)
        )
    conn.commit()
    return {
        "status": "created",
        "id": cursor.lastrowid,
        "response_id": int(response_id),
        "question_index": int(question_index),
    }


def action_update_questionnaire_response(conn, args):
    """Update a questionnaire response status."""
    response_id = getattr(args, 'id', None)
    if not response_id:
        return {"status": "error", "message": "Missing --id argument"}
    now = datetime.utcnow().isoformat()
    updates = []
    params = []
    new_status = getattr(args, 'status', None)
    if new_status:
        updates.append("status = ?")
        params.append(new_status)
    reviewed_by = getattr(args, 'reviewed_by', None)
    if reviewed_by:
        updates.append("reviewed_by = ?")
        params.append(reviewed_by)
    score = getattr(args, 'score', None)
    if score is not None:
        updates.append("score = ?")
        params.append(float(score))
    if new_status == 'reviewed':
        updates.append("reviewed_at = ?")
        params.append(now)
    if not updates:
        return {"status": "error", "message": "No fields to update"}
    updates.append("updated_at = ?")
    params.append(now)
    params.append(response_id)
    conn.execute(
        f"UPDATE questionnaire_responses SET {', '.join(updates)} WHERE id = ?",
        params
    )
    conn.commit()
    return {"status": "updated", "id": int(response_id)}



# ===========================================================================
# INTEGRATION ACTIONS
# ===========================================================================

def action_add_integration(conn, args):
    """Register a new integration provider."""
    provider = getattr(args, 'provider', None)
    if not provider:
        return {"status": "error", "message": "Missing --provider argument"}
    name = args.name
    if not name:
        return {"status": "error", "message": "Missing --name argument"}

    schedule = getattr(args, 'schedule', None)
    config = getattr(args, 'config', None)

    cursor = conn.execute(
        """INSERT INTO integrations (provider, name, status, schedule, config)
           VALUES (?, ?, 'configured', ?, ?)""",
        (provider, name, schedule, config)
    )
    conn.commit()

    return {
        "status": "created",
        "id": cursor.lastrowid,
        "provider": provider,
        "name": name,
    }


def action_list_integrations(conn, args):
    """List integrations with optional filters."""
    query = "SELECT * FROM integrations WHERE 1=1"
    params = []

    provider = getattr(args, 'provider', None)
    if provider:
        query += " AND provider = ?"
        params.append(provider)
    if args.status:
        query += " AND status = ?"
        params.append(args.status)

    query += " ORDER BY provider, name"
    rows = conn.execute(query, params).fetchall()

    return {"status": "ok", "count": len(rows), "integrations": [dict(r) for r in rows]}


def action_update_integration(conn, args):
    """Update an integration record."""
    if not args.id:
        return {"status": "error", "message": "Missing --id argument"}
    row = conn.execute("SELECT id FROM integrations WHERE id = ?", (int(args.id),)).fetchone()
    if not row:
        return {"status": "error", "message": f"Integration not found with id: {args.id}"}

    updates = []
    params = []
    if args.status:
        updates.append("status = ?")
        params.append(args.status)
    if getattr(args, 'last_sync', None):
        updates.append("last_sync = ?")
        params.append(args.last_sync)
    if getattr(args, 'next_sync', None):
        updates.append("next_sync = ?")
        params.append(args.next_sync)
    if getattr(args, 'error_message', None):
        updates.append("last_error = ?")
        params.append(args.error_message)
        updates.append("error_count = error_count + 1")
    if getattr(args, 'schedule', None):
        updates.append("schedule = ?")
        params.append(args.schedule)
    if args.name:
        updates.append("name = ?")
        params.append(args.name)

    if not updates:
        return {"status": "error", "message": "No fields to update"}

    updates.append("updated_at = datetime('now')")
    set_clause = ", ".join(updates)
    conn.execute(f"UPDATE integrations SET {set_clause} WHERE id = ?", params + [int(args.id)])
    conn.commit()
    return {"status": "updated", "id": int(args.id)}


def action_sync_integration(conn, args):
    """Trigger sync for an integration (marks as syncing, returns provider info)."""
    if not args.id:
        return {"status": "error", "message": "Missing --id argument"}
    row = conn.execute("SELECT id, provider, name, status FROM integrations WHERE id = ?",
                       (int(args.id),)).fetchone()
    if not row:
        return {"status": "error", "message": f"Integration not found with id: {args.id}"}

    now = datetime.now().isoformat(timespec="seconds")
    conn.execute(
        "UPDATE integrations SET status = 'syncing', last_sync = ?, updated_at = ? WHERE id = ?",
        (now, now, int(args.id))
    )
    conn.commit()

    return {
        "status": "syncing",
        "id": dict(row)["id"],
        "provider": dict(row)["provider"],
        "name": dict(row)["name"],
    }


def action_integration_health(conn, args):
    """Show health dashboard for all integrations, including companion skill status."""
    rows = conn.execute(
        "SELECT * FROM integrations ORDER BY provider, name"
    ).fetchall()

    integrations = []
    healthy = errored = stale = disabled = 0

    for row in rows:
        r = dict(row)
        sync_age_hours = None
        is_stale = False
        if r["last_sync"]:
            try:
                last = datetime.fromisoformat(r["last_sync"])
                sync_age_hours = round((datetime.now() - last).total_seconds() / 3600, 1)
                is_stale = sync_age_hours > 48
            except (ValueError, TypeError):
                pass

        evidence_count = conn.execute(
            "SELECT COUNT(*) FROM evidence WHERE source = ?", (r["provider"],)
        ).fetchone()[0]

        last_evidence = conn.execute(
            "SELECT MAX(uploaded_at) FROM evidence WHERE source = ?", (r["provider"],)
        ).fetchone()[0]

        health = "disabled" if r["status"] == "disabled" else \
                 "errored" if r["error_count"] and r["error_count"] > 0 else \
                 "stale" if is_stale else "healthy"

        if health == "healthy":
            healthy += 1
        elif health == "errored":
            errored += 1
        elif health == "stale":
            stale += 1
        else:
            disabled += 1

        integrations.append({
            **r,
            "sync_age_hours": sync_age_hours,
            "is_stale": is_stale,
            "evidence_count": evidence_count,
            "last_evidence_date": last_evidence,
            "health": health,
        })

    # Add companion skill install status
    companion_status = []
    for name, meta in COMPANION_SKILLS.items():
        companion_status.append({
            "name": name,
            "installed": _detect_companion_installed(name),
            "provider": meta["provider"],
            "install_command": meta["install"],
        })

    return {
        "status": "ok",
        "total": len(integrations),
        "healthy": healthy,
        "errored": errored,
        "stale": stale,
        "disabled": disabled,
        "integrations": integrations,
        "companions": companion_status,
    }


# ===========================================================================
# COMPANION SKILL DETECTION
# ===========================================================================

# Known companion skills with metadata for detection and user guidance
COMPANION_SKILLS = {
    "auditclaw-aws": {
        "description": "AWS compliance evidence collection",
        "checks": "15 checks (S3, IAM, CloudTrail, VPC, KMS, EC2, RDS, Lambda, EBS, SQS, SNS, Secrets Manager, Config, GuardDuty, Security Hub)",
        "install": "clawhub install auditclaw-aws",
        "setup": "Configure AWS credentials: aws configure (needs read-only IAM access)",
        "env_var": "AWS_ACCESS_KEY_ID",
        "provider": "aws",
    },
    "auditclaw-github": {
        "description": "GitHub compliance evidence collection",
        "checks": "9 checks (branch protection, secret scanning, 2FA, vulnerability alerts, code scanning, license, CODEOWNERS, signed commits, audit logs)",
        "install": "clawhub install auditclaw-github",
        "setup": "Set GITHUB_TOKEN env var with repo and org read access",
        "env_var": "GITHUB_TOKEN",
        "provider": "github",
    },
    "auditclaw-azure": {
        "description": "Azure compliance evidence collection",
        "checks": "12 checks (storage, NSG, Key Vault, SQL, compute, App Service, Defender)",
        "install": "clawhub install auditclaw-azure",
        "setup": "Configure Azure credentials: az login or set AZURE_CLIENT_ID + AZURE_TENANT_ID + AZURE_CLIENT_SECRET. Needs Reader + Security Reader roles.",
        "env_var": "AZURE_SUBSCRIPTION_ID",
        "provider": "azure",
    },
    "auditclaw-gcp": {
        "description": "GCP compliance evidence collection",
        "checks": "12 checks (storage, firewall, IAM, logging, KMS, DNS, BigQuery, compute, Cloud SQL)",
        "install": "clawhub install auditclaw-gcp",
        "setup": "Set GOOGLE_APPLICATION_CREDENTIALS to service account JSON. Needs roles/viewer + iam.securityReviewer.",
        "env_var": "GCP_PROJECT_ID",
        "provider": "gcp",
    },
    "auditclaw-idp": {
        "description": "Identity provider compliance checks (Google Workspace + Okta)",
        "checks": "8 checks (MFA enforcement, admin audit, inactive users, password policy — for both Google Workspace and Okta)",
        "install": "clawhub install auditclaw-idp",
        "setup": "For Google Workspace: set GOOGLE_WORKSPACE_SA_KEY + GOOGLE_WORKSPACE_ADMIN_EMAIL. For Okta: set OKTA_ORG_URL + OKTA_API_TOKEN.",
        "env_var": None,
        "provider": "idp",
    },
}


def _detect_companion_installed(skill_name):
    """Check if a companion skill is installed by looking for its SKILL.md."""
    candidates = [
        os.path.expanduser(f"~/.openclaw/skills/{skill_name}/SKILL.md"),
        os.path.expanduser(f"~/clawd/skills/{skill_name}/SKILL.md"),
        os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(
            os.path.abspath(__file__)))), skill_name, "SKILL.md"),
    ]
    for path in candidates:
        if os.path.exists(path):
            return True
    return False


def action_list_companions(conn, args):
    """List all known companion skills with their install status."""
    companions = []
    installed_count = 0
    available_count = 0

    for name, meta in COMPANION_SKILLS.items():
        is_installed = _detect_companion_installed(name)
        if is_installed:
            installed_count += 1
        else:
            available_count += 1

        # Check if the provider has evidence in the DB
        evidence_count = conn.execute(
            "SELECT COUNT(*) FROM evidence WHERE source = ?",
            (meta["provider"],)
        ).fetchone()[0]

        companions.append({
            "name": name,
            "description": meta["description"],
            "checks": meta["checks"],
            "installed": is_installed,
            "install_command": meta["install"],
            "setup_instructions": meta["setup"],
            "evidence_count": evidence_count,
        })

    return {
        "status": "ok",
        "total": len(companions),
        "installed": installed_count,
        "available": available_count,
        "companions": companions,
    }


# ===========================================================================
# INTEGRATION SETUP UX ACTIONS
# ===========================================================================

def action_setup_guide(conn, args):
    """Return step-by-step setup guide for a cloud integration."""
    provider = args.provider
    if not provider:
        return {"status": "error", "message": "Missing --provider argument (aws, github, azure, gcp, idp)"}

    guides = {
        "aws": {
            "provider": "aws",
            "title": "AWS Integration Setup",
            "auth_method": "IAM Role + AssumeRole (recommended) or Access Keys (legacy)",
            "checks_unlocked": "15 security checks across S3, IAM, CloudTrail, VPC, KMS, EC2, RDS, Lambda, CloudWatch, Config, GuardDuty, Security Hub, EKS, ECS, ELB",
            "steps": [
                {
                    "step": 1,
                    "title": "Create IAM Role (recommended)",
                    "instructions": "Go to AWS Console \u2192 IAM \u2192 Roles \u2192 Create Role \u2192 'Another AWS account'. Enter AuditClaw's account ID and the External ID shown below. Attach the ReadOnlyAccess managed policy (or our custom policy from 'show aws policy').",
                    "cli_alternative": "aws iam create-role --role-name AuditClawReadOnly --assume-role-policy-document file://trust-policy.json && aws iam attach-role-policy --role-name AuditClawReadOnly --policy-arn arn:aws:iam::aws:policy/ReadOnlyAccess"
                },
                {
                    "step": 2,
                    "title": "Share Role ARN",
                    "instructions": "Tell me the Role ARN (e.g., arn:aws:iam::123456789012:role/AuditClawReadOnly). No access keys or secrets needed \u2014 AuditClaw will use temporary credentials via STS AssumeRole.",
                },
                {
                    "step": 3,
                    "title": "Verify Connection",
                    "instructions": "I'll test the IAM Role and show which checks are accessible. Run 'test aws connection' to verify anytime."
                }
            ],
            "estimated_time": "5 minutes",
            "permissions_summary": "Read-only access via IAM Role with temporary credentials (1-hour TTL, auto-refreshed). No static access keys stored.",
            "policy_command": "Run 'show aws policy' to see the exact IAM policy JSON",
            "security_note": "IAM Role + AssumeRole is the recommended approach. No long-lived credentials are stored. Temporary tokens expire after 1 hour.",
        },
        "github": {
            "provider": "github",
            "title": "GitHub Integration Setup",
            "auth_method": "GitHub App (recommended) or Personal Access Token (legacy)",
            "checks_unlocked": "9 compliance checks: branch protection, secret scanning, 2FA enforcement, Dependabot alerts, code scanning, license, CODEOWNERS, signed commits, audit logs",
            "steps": [
                {
                    "step": 1,
                    "title": "Option A: Install GitHub App (recommended)",
                    "instructions": "Install the AuditClaw GitHub App on your organization. Select which repositories to grant access to. The app uses short-lived installation tokens \u2014 no static tokens to manage or rotate.",
                },
                {
                    "step": 2,
                    "title": "Option B: Personal Access Token (alternative)",
                    "instructions": "Go to GitHub \u2192 Settings \u2192 Developer Settings \u2192 Fine-grained tokens. Name: auditclaw-grc. Expiration: 90 days. Grant READ-ONLY permissions:\n\u2022 Repository: Contents, Branch protection rules, Secret scanning alerts, Dependabot alerts\n\u2022 Organization: Members, Administration (read)",
                },
                {
                    "step": 3,
                    "title": "Specify Organization",
                    "instructions": "Tell me your GitHub organization name (e.g., 'my-company'). I'll scan all repos in that org."
                },
                {
                    "step": 4,
                    "title": "Verify Connection",
                    "instructions": "I'll test the connection and show which checks are accessible. Run 'test github connection' to verify anytime."
                }
            ],
            "estimated_time": "3 minutes",
            "permissions_summary": "Read-only access to repository metadata, branch protection rules, security alerts, and organization settings. No write permissions.",
            "policy_command": "Run 'show github policy' to see exact permissions needed"
        },
        "azure": {
            "provider": "azure",
            "title": "Azure Integration Setup",
            "checks_unlocked": "12 security checks across storage accounts, NSGs, Key Vault, SQL Server, VMs, App Service, and Defender for Cloud",
            "steps": [
                {
                    "step": 1,
                    "title": "Create Service Principal",
                    "instructions": "Run in Azure CLI or Cloud Shell:\n\naz ad sp create-for-rbac --name auditclaw-scanner --role Reader --scopes /subscriptions/YOUR_SUBSCRIPTION_ID",
                    "cli_alternative": "az ad sp create-for-rbac --name auditclaw-scanner --role Reader --scopes /subscriptions/<SUB_ID>"
                },
                {
                    "step": 2,
                    "title": "Add Security Reader Role",
                    "instructions": "az role assignment create --assignee APP_ID_FROM_STEP_1 --role 'Security Reader' --scope /subscriptions/YOUR_SUBSCRIPTION_ID",
                },
                {
                    "step": 3,
                    "title": "Provide Credentials",
                    "instructions": "Send me these values from the output of step 1:\n\u2022 appId \u2192 AZURE_CLIENT_ID\n\u2022 password \u2192 AZURE_CLIENT_SECRET\n\u2022 tenant \u2192 AZURE_TENANT_ID\n\u2022 Your subscription ID \u2192 AZURE_SUBSCRIPTION_ID"
                },
                {
                    "step": 4,
                    "title": "Verify Connection",
                    "instructions": "I'll test the service principal and show which checks are accessible. Run 'test azure connection' to verify anytime."
                }
            ],
            "estimated_time": "5 minutes",
            "permissions_summary": "Reader + Security Reader roles (subscription-level). Read-only access to resource configurations and security settings.",
            "policy_command": "Run 'show azure policy' to see exact roles and permissions needed"
        },
        "gcp": {
            "provider": "gcp",
            "title": "GCP Integration Setup",
            "checks_unlocked": "12 security checks across Cloud Storage, firewall rules, IAM, audit logging, KMS, DNS, BigQuery, Compute Engine, and Cloud SQL",
            "steps": [
                {
                    "step": 1,
                    "title": "Create Service Account",
                    "instructions": "Go to GCP Console \u2192 IAM & Admin \u2192 Service Accounts \u2192 Create Service Account.\nName: auditclaw-scanner\nDescription: Read-only compliance scanning",
                    "cli_alternative": "gcloud iam service-accounts create auditclaw-scanner --display-name='AuditClaw Scanner'"
                },
                {
                    "step": 2,
                    "title": "Assign Roles",
                    "instructions": "Grant these roles to the service account:\n\u2022 roles/viewer (project-level)\n\u2022 roles/iam.securityReviewer\n\u2022 roles/cloudsql.viewer\n\u2022 roles/logging.viewer\n\u2022 roles/dns.reader\n\u2022 roles/cloudkms.viewer",
                    "cli_alternative": "for role in roles/viewer roles/iam.securityReviewer roles/cloudsql.viewer roles/logging.viewer roles/dns.reader roles/cloudkms.viewer; do gcloud projects add-iam-policy-binding PROJECT_ID --member=serviceAccount:auditclaw-scanner@PROJECT_ID.iam.gserviceaccount.com --role=$role; done"
                },
                {
                    "step": 3,
                    "title": "Generate Key",
                    "instructions": "Go to the service account \u2192 Keys \u2192 Add Key \u2192 Create new key \u2192 JSON.\nThis downloads a JSON key file.",
                    "cli_alternative": "gcloud iam service-accounts keys create key.json --iam-account=auditclaw-scanner@PROJECT_ID.iam.gserviceaccount.com"
                },
                {
                    "step": 4,
                    "title": "Provide Credentials",
                    "instructions": "Send me the JSON key file content and your GCP project ID. I'll configure GOOGLE_APPLICATION_CREDENTIALS and GCP_PROJECT_ID."
                },
                {
                    "step": 5,
                    "title": "Verify Connection",
                    "instructions": "I'll test the service account and show which checks are accessible. Run 'test gcp connection' to verify anytime."
                }
            ],
            "estimated_time": "5 minutes",
            "permissions_summary": "6 read-only IAM roles. No write, modify, or delete permissions. All checks use read-only API calls.",
            "policy_command": "Run 'show gcp policy' to see exact IAM roles needed"
        },
        "idp": {
            "provider": "idp",
            "title": "Identity Provider Integration Setup",
            "checks_unlocked": "8 identity checks: MFA enforcement, admin audit, inactive users, password policy \u2014 for both Google Workspace and Okta",
            "steps": [
                {
                    "step": 1,
                    "title": "Choose Provider(s)",
                    "instructions": "AuditClaw supports Google Workspace and Okta. You can configure one or both. Which do you use?"
                },
                {
                    "step": 2,
                    "title": "Google Workspace Setup (if applicable)",
                    "instructions": "1. Go to Google Cloud Console \u2192 APIs & Services \u2192 Enable Admin SDK API\n2. Create a service account with domain-wide delegation\n3. In Google Admin \u2192 Security \u2192 API controls \u2192 Domain-wide delegation, add the service account with scopes:\n   \u2022 https://www.googleapis.com/auth/admin.directory.user.readonly\n   \u2022 https://www.googleapis.com/auth/admin.reports.audit.readonly\n4. Send me: the JSON key file path and your super admin email address"
                },
                {
                    "step": 3,
                    "title": "Okta Setup (if applicable)",
                    "instructions": "1. Go to Okta Admin \u2192 Security \u2192 API \u2192 Tokens \u2192 Create Token\n2. Name: auditclaw-scanner\n3. The token needs read access to: users, factors, policies, sessions\n4. Send me: your Okta org URL (e.g., https://mycompany.okta.com) and the API token"
                },
                {
                    "step": 4,
                    "title": "Verify Connection",
                    "instructions": "I'll test the credentials and show which checks are accessible. Run 'test idp connection' to verify anytime."
                }
            ],
            "estimated_time": "5-10 minutes",
            "permissions_summary": "Google: Admin SDK read-only (user directory + audit reports). Okta: read-only API token (users, factors, policies).",
            "policy_command": "Run 'show idp policy' to see exact permissions needed"
        }
    }

    if provider not in guides:
        return {"status": "error", "message": f"Unknown provider: {provider}. Available: aws, github, azure, gcp, idp"}

    guide = guides[provider]
    # Check if companion is installed
    skill_name = f"auditclaw-{provider}"
    guide["companion_installed"] = _detect_companion_installed(skill_name)

    # Check current evidence count
    provider_name = COMPANION_SKILLS.get(skill_name, {}).get("provider", provider)
    evidence_count = conn.execute(
        "SELECT COUNT(*) FROM evidence WHERE source = ?", (provider_name,)
    ).fetchone()[0]
    guide["current_evidence_count"] = evidence_count
    guide["status"] = "ok"

    return guide


def action_show_policy(conn, args):
    """Return the exact permissions/policy needed for a cloud provider."""
    provider = args.provider
    if not provider:
        return {"status": "error", "message": "Missing --provider argument (aws, github, azure, gcp, idp)"}

    skill_name = f"auditclaw-{provider}"

    # Find the companion skill directory
    candidates = [
        os.path.expanduser(f"~/.openclaw/skills/{skill_name}/scripts"),
        os.path.expanduser(f"~/clawd/skills/{skill_name}/scripts"),
        os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(
            os.path.abspath(__file__)))), skill_name, "scripts"),
    ]

    skill_dir = None
    for path in candidates:
        if os.path.isdir(path):
            skill_dir = path
            break

    if not skill_dir:
        return {"status": "error", "message": f"Companion skill {skill_name} not found. Install with: clawhub install {skill_name}"}

    # Policy file names per provider
    policy_files = {
        "aws": "iam-policy.json",
        "github": "github-permissions.json",
        "azure": "azure-roles.json",
        "gcp": "gcp-roles.json",
        "idp": "idp-permissions.json",
    }

    policy_file = policy_files.get(provider)
    if not policy_file:
        return {"status": "error", "message": f"Unknown provider: {provider}"}

    policy_path = os.path.join(skill_dir, policy_file)
    if not os.path.exists(policy_path):
        return {"status": "error", "message": f"Policy file not found at {policy_path}"}

    with open(policy_path, "r") as f:
        content = f.read()

    # Try to parse as JSON, otherwise return as text
    try:
        policy_data = json.loads(content)
    except json.JSONDecodeError:
        policy_data = content

    return {
        "status": "ok",
        "provider": provider,
        "policy_file": policy_path,
        "format": "json" if isinstance(policy_data, (dict, list)) else "text",
        "policy": policy_data,
        "instructions": f"Copy this policy and apply it in your {provider.upper()} console. See 'setup {provider}' for step-by-step instructions."
    }


def action_test_connection(conn, args):
    """Test connectivity to a cloud provider and report per-service status."""
    provider = args.provider
    if not provider:
        return {"status": "error", "message": "Missing --provider argument (aws, github, azure, gcp, idp)"}

    skill_name = f"auditclaw-{provider}"
    if not _detect_companion_installed(skill_name):
        return {"status": "error", "message": f"Companion {skill_name} not installed. Run: clawhub install {skill_name}"}

    # Find the companion's test script
    candidates = [
        os.path.expanduser(f"~/.openclaw/skills/{skill_name}/scripts"),
        os.path.expanduser(f"~/clawd/skills/{skill_name}/scripts"),
        os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(
            os.path.abspath(__file__)))), skill_name, "scripts"),
    ]

    skill_dir = None
    for path in candidates:
        if os.path.isdir(path):
            skill_dir = path
            break

    if not skill_dir:
        return {"status": "error", "message": f"Could not find {skill_name} scripts directory"}

    # Run the evidence script with --test-connection flag
    import subprocess
    script_map = {
        "aws": "aws_evidence.py",
        "github": "github_evidence.py",
        "azure": "azure_evidence.py",
        "gcp": "gcp_evidence.py",
        "idp": "idp_evidence.py",
    }

    script = script_map.get(provider)
    if not script:
        return {"status": "error", "message": f"Unknown provider: {provider}"}

    script_path = os.path.join(skill_dir, script)
    if not os.path.exists(script_path):
        return {"status": "error", "message": f"Evidence script not found: {script_path}"}

    try:
        result = subprocess.run(
            ["python3", script_path, "--test-connection"],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0:
            try:
                test_result = json.loads(result.stdout)
            except json.JSONDecodeError:
                test_result = {"raw_output": result.stdout}
            return {
                "status": "ok",
                "provider": provider,
                "connection_test": test_result,
            }
        else:
            error_msg = result.stderr.strip() or result.stdout.strip()
            return {
                "status": "error",
                "provider": provider,
                "message": f"Connection test failed: {error_msg}",
                "hint": f"Run 'setup {provider}' for setup instructions"
            }
    except subprocess.TimeoutExpired:
        return {"status": "error", "provider": provider, "message": "Connection test timed out (30s). Check network and credentials."}
    except Exception as e:
        return {"status": "error", "provider": provider, "message": str(e)}


# ===========================================================================
# CREDENTIAL MANAGEMENT ACTIONS
# ===========================================================================

VALID_CREDENTIAL_PROVIDERS = {"aws", "github", "azure", "gcp", "idp"}


def action_store_credential(conn, args):
    """Store or update a credential for a cloud provider."""
    provider = args.provider
    if not provider:
        return {"status": "error", "message": "Missing --provider argument (aws, github, azure, gcp, idp)"}
    if provider not in VALID_CREDENTIAL_PROVIDERS:
        return {"status": "error", "message": f"Invalid provider '{provider}'. Must be one of: aws, github, azure, gcp, idp"}

    auth_method = getattr(args, "auth_method", None) or getattr(args, "type", None)
    if not auth_method:
        return {"status": "error", "message": "Missing --type argument (iam_role, github_app, service_principal, service_account, access_key, personal_token, client_secret, api_token)"}

    config_str = args.config
    if not config_str:
        return {"status": "error", "message": "Missing --config argument (JSON config, e.g. '{\"role_arn\": \"...\"}')"}

    try:
        config = json.loads(config_str) if isinstance(config_str, str) else config_str
    except json.JSONDecodeError:
        return {"status": "error", "message": "Invalid --config JSON"}

    # Secret data comes from --description (reuse existing arg, since secrets shouldn't be a new CLI arg name)
    secret_data = args.description
    expires_at = getattr(args, "valid_until", None)

    from credential_store import save_credential
    result = save_credential(
        args.db_path or os.path.expanduser("~/.openclaw/grc/compliance.sqlite"),
        provider, auth_method, config,
        secret_data=secret_data, expires_at=expires_at
    )
    return result


def action_get_credential(conn, args):
    """Retrieve credential info for a provider (secrets masked)."""
    provider = args.provider
    if not provider:
        return {"status": "error", "message": "Missing --provider argument (aws, github, azure, gcp, idp)"}
    if provider not in VALID_CREDENTIAL_PROVIDERS:
        return {"status": "error", "message": f"Invalid provider '{provider}'. Must be one of: aws, github, azure, gcp, idp"}

    from credential_store import get_credential
    cred = get_credential(
        args.db_path or os.path.expanduser("~/.openclaw/grc/compliance.sqlite"),
        provider
    )

    if not cred:
        return {"status": "not_found", "provider": provider, "message": f"No credential stored for {provider}"}

    # Mask secret data for safety
    result = {
        "status": "ok",
        "id": cred["id"],
        "provider": cred["provider"],
        "auth_method": cred["auth_method"],
        "config": cred["config"],
        "has_secret": cred.get("secret_available", False),
        "credential_path": cred.get("credential_path"),
        "cred_status": cred["status"],
        "created_at": cred["created_at"],
        "updated_at": cred["updated_at"],
        "last_used": cred.get("last_used"),
        "expires_at": cred.get("expires_at"),
    }
    return result


def action_delete_credential(conn, args):
    """Delete stored credential for a provider."""
    provider = args.provider
    if not provider:
        return {"status": "error", "message": "Missing --provider argument (aws, github, azure, gcp, idp)"}
    if provider not in VALID_CREDENTIAL_PROVIDERS:
        return {"status": "error", "message": f"Invalid provider '{provider}'. Must be one of: aws, github, azure, gcp, idp"}

    from credential_store import delete_credential
    result = delete_credential(
        args.db_path or os.path.expanduser("~/.openclaw/grc/compliance.sqlite"),
        provider
    )
    return result


# ===========================================================================
# ALERT ACTIONS
# ===========================================================================

def action_add_alert(conn, args):
    """Create a new alert."""
    alert_type = args.type
    if not alert_type:
        return {"status": "error", "message": "Missing --type argument"}
    title = args.title
    if not title:
        return {"status": "error", "message": "Missing --title argument"}

    severity = args.severity or "info"
    description = args.description or None
    resource_type = getattr(args, 'resource_type', None)
    resource_id_val = getattr(args, 'resource_id', None)
    drift_details = getattr(args, 'drift_details', None)

    # Pack extra fields into metadata JSON
    import json as _json
    meta = {}
    if resource_type:
        meta["resource_type"] = resource_type
    if resource_id_val:
        meta["resource_id"] = resource_id_val
    if drift_details:
        meta["drift_details"] = drift_details
    metadata_str = _json.dumps(meta) if meta else None

    cursor = conn.execute(
        """INSERT INTO alerts (type, title, severity, message, metadata)
           VALUES (?, ?, ?, ?, ?)""",
        (alert_type, title, severity, description, metadata_str)
    )
    conn.commit()

    return {
        "status": "created",
        "id": cursor.lastrowid,
        "type": alert_type,
        "severity": severity,
        "title": title,
    }


def action_list_alerts(conn, args):
    """List alerts with optional filters."""
    query = "SELECT * FROM alerts WHERE 1=1"
    params = []

    if args.type:
        query += " AND type = ?"
        params.append(args.type)
    if args.severity:
        query += " AND severity = ?"
        params.append(args.severity)
    if args.status:
        query += " AND status = ?"
        params.append(args.status)
    acknowledged = getattr(args, 'acknowledged', None)
    if acknowledged is not None and acknowledged != "":
        if str(acknowledged) in ("0", "false", "no"):
            query += " AND acknowledged_at IS NULL"
        elif str(acknowledged) in ("1", "true", "yes"):
            query += " AND acknowledged_at IS NOT NULL"
    resolved = getattr(args, 'resolved', None)
    if resolved is not None and resolved != "":
        if str(resolved) in ("0", "false", "no"):
            query += " AND resolved_at IS NULL"
        elif str(resolved) in ("1", "true", "yes"):
            query += " AND resolved_at IS NOT NULL"

    query += " ORDER BY triggered_at DESC"
    rows = conn.execute(query, params).fetchall()

    unacknowledged = sum(1 for r in rows if not dict(r).get("acknowledged_at"))
    unresolved = sum(1 for r in rows if not dict(r).get("resolved_at"))

    return {
        "status": "ok",
        "count": len(rows),
        "unacknowledged": unacknowledged,
        "unresolved": unresolved,
        "alerts": [dict(r) for r in rows],
    }


def action_acknowledge_alert(conn, args):
    """Acknowledge an alert."""
    if not args.id:
        return {"status": "error", "message": "Missing --id argument"}
    row = conn.execute("SELECT id, status FROM alerts WHERE id = ?", (int(args.id),)).fetchone()
    if not row:
        return {"status": "error", "message": f"Alert not found with id: {args.id}"}

    now = datetime.now().isoformat(timespec="seconds")
    acknowledged_by = getattr(args, 'acknowledged_by', None) or "user"

    conn.execute(
        "UPDATE alerts SET acknowledged_at = ?, acknowledged_by = ? WHERE id = ?",
        (now, acknowledged_by, int(args.id))
    )
    conn.commit()

    return {"status": "acknowledged", "id": int(args.id)}


def action_resolve_alert(conn, args):
    """Resolve an alert."""
    if not args.id:
        return {"status": "error", "message": "Missing --id argument"}
    row = conn.execute("SELECT id, status FROM alerts WHERE id = ?", (int(args.id),)).fetchone()
    if not row:
        return {"status": "error", "message": f"Alert not found with id: {args.id}"}

    now = datetime.now().isoformat(timespec="seconds")
    conn.execute(
        "UPDATE alerts SET status = 'resolved', resolved_at = ? WHERE id = ?",
        (now, int(args.id))
    )
    conn.commit()

    return {"status": "resolved", "id": int(args.id)}


# ===========================================================================
# BROWSER CHECK ACTIONS
# ===========================================================================

def action_add_browser_check(conn, args):
    """Register a URL for scheduled scanning."""
    name = args.name
    if not name:
        return {"status": "error", "message": "Missing --name argument"}
    url = getattr(args, 'url', None)
    if not url:
        return {"status": "error", "message": "Missing --url argument"}
    check_type = getattr(args, 'check_type', None)
    if not check_type:
        return {"status": "error", "message": "Missing --check-type argument"}

    schedule = getattr(args, 'schedule', None)

    cursor = conn.execute(
        """INSERT INTO browser_checks (name, url, check_type, schedule)
           VALUES (?, ?, ?, ?)""",
        (name, url, check_type, schedule)
    )
    conn.commit()

    return {
        "status": "created",
        "id": cursor.lastrowid,
        "name": name,
        "url": url,
        "check_type": check_type,
    }


def action_list_browser_checks(conn, args):
    """List browser checks with optional filters."""
    query = "SELECT * FROM browser_checks WHERE 1=1"
    params = []

    check_type = getattr(args, 'check_type', None)
    if check_type:
        query += " AND check_type = ?"
        params.append(check_type)
    if args.status:
        query += " AND status = ?"
        params.append(args.status)

    query += " ORDER BY name"
    rows = conn.execute(query, params).fetchall()

    return {"status": "ok", "count": len(rows), "checks": [dict(r) for r in rows]}


def action_update_browser_check(conn, args):
    """Update a browser check record."""
    if not args.id:
        return {"status": "error", "message": "Missing --id argument"}
    row = conn.execute("SELECT id FROM browser_checks WHERE id = ?", (int(args.id),)).fetchone()
    if not row:
        return {"status": "error", "message": f"Browser check not found with id: {args.id}"}

    updates = []
    params = []
    if args.status:
        updates.append("status = ?")
        params.append(args.status)
    if getattr(args, 'last_run', None):
        updates.append("last_run = ?")
        params.append(args.last_run)
    if getattr(args, 'last_result', None):
        updates.append("last_result = ?")
        params.append(args.last_result)
    if getattr(args, 'last_status', None):
        updates.append("last_status = ?")
        params.append(args.last_status)
    if getattr(args, 'schedule', None):
        updates.append("schedule = ?")
        params.append(args.schedule)
    if args.name:
        updates.append("name = ?")
        params.append(args.name)
    if getattr(args, 'url', None):
        updates.append("url = ?")
        params.append(args.url)

    if not updates:
        return {"status": "error", "message": "No fields to update"}

    updates.append("updated_at = datetime('now')")
    if getattr(args, 'last_run', None):
        updates.append("run_count = run_count + 1")

    set_clause = ", ".join(updates)
    conn.execute(f"UPDATE browser_checks SET {set_clause} WHERE id = ?", params + [int(args.id)])
    conn.commit()
    return {"status": "updated", "id": int(args.id)}


def action_run_browser_check(conn, args):
    """Trigger a browser check run (marks as running, returns check info)."""
    if not args.id:
        return {"status": "error", "message": "Missing --id argument"}
    row = conn.execute(
        "SELECT id, name, url, check_type, status FROM browser_checks WHERE id = ?",
        (int(args.id),)
    ).fetchone()
    if not row:
        return {"status": "error", "message": f"Browser check not found with id: {args.id}"}

    r = dict(row)
    now = datetime.now().isoformat(timespec="seconds")
    conn.execute(
        "UPDATE browser_checks SET last_run = ?, run_count = run_count + 1, updated_at = ? WHERE id = ?",
        (now, now, int(args.id))
    )
    conn.commit()

    return {
        "status": "running",
        "id": r["id"],
        "name": r["name"],
        "url": r["url"],
        "check_type": r["check_type"],
    }


def action_check_drift(conn, args):
    """Check for configuration drift across providers."""
    provider = getattr(args, 'provider', None) or 'all'
    check = getattr(args, 'check_type', None)  # reuse check_type arg

    return _check_drift_inline(conn, provider, check)


def _check_drift_inline(conn, provider, check=None):
    """Inline drift check comparing evidence snapshots."""
    providers = [provider] if provider != "all" else ["aws", "github"]
    drifts = []
    total_checks = 0
    regressions = 0
    improvements = 0
    unchanged = 0

    for prov in providers:
        query = """
            SELECT id, description, metadata, uploaded_at
            FROM evidence WHERE source = ? AND type = 'automated'
            ORDER BY uploaded_at DESC LIMIT 50
        """
        rows = conn.execute(query, (prov,)).fetchall()
        if not rows:
            continue

        # Group by check name (extract from description like "AWS iam check: 7/7 passed")
        checks_seen = {}
        for row in rows:
            r = dict(row)
            desc = r.get("description", "")
            parts = desc.split(" check:")
            check_name = parts[0].split()[-1] if len(parts) >= 2 else "unknown"
            if check and check_name != check:
                continue
            if check_name in checks_seen:
                continue
            checks_seen[check_name] = r

        for check_name, current in checks_seen.items():
            total_checks += 1
            # Find previous snapshot for same check
            prev_row = conn.execute(
                """SELECT id, description, metadata, uploaded_at
                   FROM evidence WHERE source = ? AND type = 'automated'
                   AND id < ? AND description LIKE ?
                   ORDER BY uploaded_at DESC LIMIT 1""",
                (prov, current["id"], f"%{check_name} check:%")
            ).fetchone()

            if not prev_row:
                drifts.append({
                    "provider": prov, "check": check_name, "type": "initial",
                    "detail": "First snapshot — no previous data to compare",
                    "evidence_id": current["id"],
                })
                unchanged += 1
                continue

            try:
                curr_data = json.loads(current.get("metadata", "{}") or "{}")
                prev_data = json.loads(dict(prev_row).get("metadata", "{}") or "{}")
            except (json.JSONDecodeError, TypeError):
                unchanged += 1
                continue

            curr_failed = curr_data.get("failed", 0)
            prev_failed = prev_data.get("failed", 0)
            curr_passed = curr_data.get("passed", 0)
            prev_passed = prev_data.get("passed", 0)

            if curr_failed > prev_failed:
                drift_type = "regression"
                severity = "critical" if curr_failed - prev_failed >= 3 else "warning"
                regressions += 1
            elif curr_failed < prev_failed:
                drift_type = "improvement"
                severity = "info"
                improvements += 1
            else:
                drift_type = "unchanged"
                severity = "info"
                unchanged += 1

            drifts.append({
                "provider": prov, "check": check_name, "type": drift_type,
                "severity": severity,
                "current_failed": curr_failed, "previous_failed": prev_failed,
                "current_passed": curr_passed, "previous_passed": prev_passed,
                "evidence_id": current["id"],
            })

    return {
        "status": "ok",
        "total_checks": total_checks,
        "drifted": regressions + improvements,
        "regressions": regressions,
        "improvements": improvements,
        "unchanged": unchanged,
        "drifts": drifts,
    }


def action_drift_history(conn, args):
    """Get drift detection history from alerts."""
    provider = getattr(args, 'provider', None)
    days = int(getattr(args, 'days', None) or 30)
    severity_filter = getattr(args, 'severity', None)

    query = "SELECT * FROM alerts WHERE type = 'drift_detected'"
    params = []

    if provider:
        query += " AND json_extract(metadata, '$.resource_type') = ?"
        params.append(provider)
    if days:
        query += " AND triggered_at >= datetime('now', ?)"
        params.append(f"-{days} days")
    if severity_filter == "regression":
        query += " AND severity IN ('critical', 'warning')"
    elif severity_filter == "improvement":
        query += " AND severity = 'info'"

    query += " ORDER BY triggered_at DESC"
    rows = conn.execute(query, params).fetchall()

    alerts = [dict(r) for r in rows]
    reg_count = sum(1 for a in alerts if a["severity"] in ("critical", "warning"))
    imp_count = sum(1 for a in alerts if a["severity"] == "info")

    return {
        "status": "ok",
        "total": len(alerts),
        "regressions": reg_count,
        "improvements": imp_count,
        "drifts": alerts,
    }


def action_auto_map_evidence(conn, args):
    """Auto-map evidence to controls across frameworks using control_mappings."""
    if not args.id:
        return {"status": "error", "message": "Missing --id argument (evidence ID)"}

    evidence_id = int(args.id)
    ev = conn.execute("SELECT * FROM evidence WHERE id = ?", (evidence_id,)).fetchone()
    if not ev:
        return {"status": "error", "message": f"Evidence not found with id: {evidence_id}"}

    # Get currently linked controls
    linked = conn.execute(
        "SELECT control_id FROM evidence_controls WHERE evidence_id = ?", (evidence_id,)
    ).fetchall()
    original_controls = [dict(r)["control_id"] for r in linked]

    if not original_controls:
        return {
            "status": "ok",
            "evidence_id": evidence_id,
            "original_controls": [],
            "suggested_controls": [],
            "mapped_count": 0,
            "message": "No controls currently linked to this evidence. Link controls first.",
        }

    # Look up cross-framework mappings
    suggested = []
    seen = set(original_controls)

    for ctrl_id in original_controls:
        mappings = conn.execute(
            """SELECT target_framework, target_control_id, confidence
               FROM control_mappings
               WHERE source_control_id = ? AND confidence >= 0.7
               UNION
               SELECT source_framework, source_control_id, confidence
               FROM control_mappings
               WHERE target_control_id = ? AND confidence >= 0.7""",
            (str(ctrl_id), str(ctrl_id))
        ).fetchall()

        for mapping in mappings:
            m = dict(mapping)
            target_ctrl = m.get("target_control_id") or m.get("source_control_id")
            if target_ctrl and target_ctrl not in seen:
                seen.add(target_ctrl)
                framework = m.get("target_framework") or m.get("source_framework", "unknown")
                suggested.append({
                    "control_id": target_ctrl,
                    "framework": framework,
                    "confidence": m.get("confidence", 0.7),
                    "source_control": ctrl_id,
                })

    return {
        "status": "ok",
        "evidence_id": evidence_id,
        "original_controls": original_controls,
        "suggested_controls": suggested,
        "mapped_count": len(suggested),
    }


def action_list_evidence_gaps(conn, args):
    """List controls that have no evidence linked."""
    framework = args.framework if hasattr(args, 'framework') and args.framework else None

    # Get all controls with framework info
    query = """SELECT c.id, f.slug as framework_slug, c.title
               FROM controls c
               JOIN frameworks f ON c.framework_id = f.id
               WHERE 1=1"""
    params = []
    if framework:
        query += " AND f.slug = ?"
        params.append(framework)
    query += " ORDER BY f.slug, c.id"
    all_controls = conn.execute(query, params).fetchall()

    # Get controls that have evidence
    covered = set()
    ev_rows = conn.execute(
        """SELECT DISTINCT ec.control_id
           FROM evidence_controls ec
           JOIN evidence e ON e.id = ec.evidence_id
           WHERE e.status = 'active'"""
    ).fetchall()
    for r in ev_rows:
        covered.add(dict(r)["control_id"])

    # Calculate gaps
    gaps = []
    for ctrl in all_controls:
        c = dict(ctrl)
        if c["id"] not in covered:
            gaps.append({
                "control_id": c["id"],
                "framework": c["framework_slug"],
                "title": c["title"],
            })

    total_controls = len(all_controls)
    covered_count = total_controls - len(gaps)
    coverage_pct = round((covered_count / total_controls * 100), 1) if total_controls > 0 else 0

    return {
        "status": "ok",
        "total_controls": total_controls,
        "controls_with_evidence": covered_count,
        "controls_without_evidence": len(gaps),
        "framework_coverage_pct": coverage_pct,
        "gaps": gaps[:50],
    }


# ---------------------------------------------------------------------------
# Step 9.7: Compliance Calendar + Digest
# ---------------------------------------------------------------------------

def action_compliance_calendar(conn, args):
    """Show upcoming compliance deadlines from all sources."""
    days = int(getattr(args, 'days', None) or 30)
    cal_type = args.type if hasattr(args, 'type') and args.type else "all"
    now = datetime.now()
    cutoff = (now + timedelta(days=days)).isoformat(timespec="seconds")
    now_str = now.isoformat(timespec="seconds")

    upcoming = []
    overdue = 0
    due_this_week = 0
    due_this_month = 0
    week_cutoff = (now + timedelta(days=7)).isoformat(timespec="seconds")

    # Evidence expiry
    if cal_type in ("all", "evidence"):
        rows = conn.execute(
            """SELECT id, title, valid_until, type, source
               FROM evidence WHERE valid_until IS NOT NULL AND valid_until <= ?
               ORDER BY valid_until""",
            (cutoff,)
        ).fetchall()
        for r in rows:
            d = dict(r)
            is_overdue = d["valid_until"] and d["valid_until"] < now_str
            upcoming.append({
                "type": "evidence_expiry",
                "date": d["valid_until"],
                "title": f"Evidence expires: {d['title']}",
                "resource_id": d["id"],
                "resource_type": "evidence",
                "overdue": is_overdue,
            })
            if is_overdue:
                overdue += 1
            elif d["valid_until"] <= week_cutoff:
                due_this_week += 1
            else:
                due_this_month += 1

    # Policy reviews (column is review_date)
    if cal_type in ("all", "policy"):
        rows = conn.execute(
            """SELECT id, title, review_date
               FROM policies WHERE review_date IS NOT NULL AND review_date <= ?
               ORDER BY review_date""",
            (cutoff,)
        ).fetchall()
        for r in rows:
            d = dict(r)
            is_overdue = d["review_date"] and d["review_date"] < now_str
            upcoming.append({
                "type": "policy_review",
                "date": d["review_date"],
                "title": f"Policy review due: {d['title']}",
                "resource_id": d["id"],
                "resource_type": "policy",
                "overdue": is_overdue,
            })
            if is_overdue:
                overdue += 1
            elif d["review_date"] <= week_cutoff:
                due_this_week += 1
            else:
                due_this_month += 1

    # Vendor assessments
    if cal_type in ("all", "vendor"):
        rows = conn.execute(
            """SELECT id, name, next_assessment_date
               FROM vendors WHERE next_assessment_date IS NOT NULL AND next_assessment_date <= ?
               ORDER BY next_assessment_date""",
            (cutoff,)
        ).fetchall()
        for r in rows:
            d = dict(r)
            is_overdue = d["next_assessment_date"] and d["next_assessment_date"] < now_str
            upcoming.append({
                "type": "vendor_assessment",
                "date": d["next_assessment_date"],
                "title": f"Vendor assessment due: {d['name']}",
                "resource_id": d["id"],
                "resource_type": "vendor",
                "overdue": is_overdue,
            })
            if is_overdue:
                overdue += 1
            elif d["next_assessment_date"] <= week_cutoff:
                due_this_week += 1
            else:
                due_this_month += 1

    # Training due dates (module_id FK to training_modules)
    if cal_type in ("all", "training"):
        rows = conn.execute(
            """SELECT ta.id, tm.title, ta.due_date, ta.assignee
               FROM training_assignments ta
               JOIN training_modules tm ON tm.id = ta.module_id
               WHERE ta.due_date IS NOT NULL AND ta.due_date <= ?
               AND ta.status != 'completed'
               ORDER BY ta.due_date""",
            (cutoff,)
        ).fetchall()
        for r in rows:
            d = dict(r)
            is_overdue = d["due_date"] and d["due_date"] < now_str
            upcoming.append({
                "type": "training_due",
                "date": d["due_date"],
                "title": f"Training due: {d['title']} ({d.get('assignee', 'unassigned')})",
                "resource_id": d["id"],
                "resource_type": "training_assignment",
                "overdue": is_overdue,
            })
            if is_overdue:
                overdue += 1
            elif d["due_date"] <= week_cutoff:
                due_this_week += 1
            else:
                due_this_month += 1

    # Sort by date
    upcoming.sort(key=lambda x: x.get("date") or "9999")

    return {
        "status": "ok",
        "total": len(upcoming),
        "overdue": overdue,
        "due_this_week": due_this_week,
        "due_this_month": due_this_month,
        "upcoming": upcoming,
    }


def action_compliance_digest(conn, args):
    """Generate compliance digest summary."""
    period = getattr(args, 'period', None) or "daily"

    if period == "daily":
        days_back = 1
    elif period == "weekly":
        days_back = 7
    else:  # monthly
        days_back = 30

    cutoff = f"-{days_back} days"

    # Score change
    scores = conn.execute(
        """SELECT framework_slug, score, calculated_at
           FROM compliance_scores
           ORDER BY calculated_at DESC LIMIT 20"""
    ).fetchall()

    latest_scores = {}
    for s in scores:
        d = dict(s)
        if d["framework_slug"] not in latest_scores:
            latest_scores[d["framework_slug"]] = d["score"]

    avg_score = round(sum(latest_scores.values()) / len(latest_scores), 1) if latest_scores else 0

    # New alerts
    new_alerts = conn.execute(
        "SELECT COUNT(*) FROM alerts WHERE triggered_at >= datetime('now', ?)", (cutoff,)
    ).fetchone()[0]

    # Unresolved alerts
    unresolved_alerts = conn.execute(
        "SELECT COUNT(*) FROM alerts WHERE resolved_at IS NULL"
    ).fetchone()[0]

    # Expiring evidence (within 30 days)
    expiring_evidence = conn.execute(
        """SELECT COUNT(*) FROM evidence
           WHERE valid_until IS NOT NULL
           AND valid_until <= datetime('now', '+30 days')
           AND valid_until >= datetime('now')
           AND status = 'active'"""
    ).fetchone()[0]

    # Overdue items
    overdue_training = conn.execute(
        """SELECT COUNT(*) FROM training_assignments
           WHERE due_date < datetime('now') AND status != 'completed'"""
    ).fetchone()[0]

    overdue_policies = conn.execute(
        """SELECT COUNT(*) FROM policies
           WHERE review_date IS NOT NULL AND review_date < datetime('now')"""
    ).fetchone()[0]

    # Recent incidents
    active_incidents = conn.execute(
        "SELECT COUNT(*) FROM incidents WHERE status IN ('open', 'investigating')"
    ).fetchone()[0]

    # Integration health
    total_integrations = conn.execute(
        "SELECT COUNT(*) FROM integrations"
    ).fetchone()[0]

    healthy_integrations = conn.execute(
        "SELECT COUNT(*) FROM integrations WHERE status IN ('active', 'configured') AND (error_count IS NULL OR error_count = 0)"
    ).fetchone()[0]

    return {
        "status": "ok",
        "period": period,
        "digest": {
            "average_score": avg_score,
            "frameworks_tracked": len(latest_scores),
            "new_alerts": new_alerts,
            "unresolved_alerts": unresolved_alerts,
            "expiring_evidence": expiring_evidence,
            "overdue_training": overdue_training,
            "overdue_policies": overdue_policies,
            "active_incidents": active_incidents,
            "total_integrations": total_integrations,
            "healthy_integrations": healthy_integrations,
        },
    }




def action_generate_dashboard(conn, args):
    """Generate GRC dashboard summary for chat display and optional HTML.

    Returns structured data with a text_summary field suitable for
    sending via Telegram or other chat interfaces, plus a dashboard_url
    if the web dashboard is accessible.
    """
    from datetime import datetime, timedelta

    # Overall scores
    scores = conn.execute(
        "SELECT framework_slug, score, calculated_at FROM compliance_scores ORDER BY calculated_at DESC"
    ).fetchall()
    latest_scores = {}
    for s in scores:
        d = dict(s)
        slug = d["framework_slug"]
        if slug and slug not in latest_scores:
            latest_scores[slug] = d

    all_scores = [v["score"] for v in latest_scores.values()]
    overall_score = round(sum(all_scores) / len(all_scores), 1) if all_scores else 0
    frameworks_count = len(latest_scores)

    # Risk summary
    total_risks = conn.execute("SELECT COUNT(*) FROM risks").fetchone()[0]
    high_risks = conn.execute(
        "SELECT COUNT(*) FROM risks WHERE likelihood >= 4 AND impact >= 4"
    ).fetchone()[0]
    open_risks = conn.execute(
        "SELECT COUNT(*) FROM risks WHERE status = 'open'"
    ).fetchone()[0]

    # Evidence freshness
    now_str = datetime.now().isoformat(timespec="seconds")
    expiring_cutoff = (datetime.now() + timedelta(days=30)).isoformat(timespec="seconds")
    fresh = conn.execute(
        "SELECT COUNT(*) FROM evidence WHERE status = 'active' AND (valid_until IS NULL OR valid_until > ?)",
        (expiring_cutoff,)
    ).fetchone()[0]
    expiring = conn.execute(
        "SELECT COUNT(*) FROM evidence WHERE status = 'active' AND valid_until IS NOT NULL AND valid_until <= ? AND valid_until > ?",
        (expiring_cutoff, now_str)
    ).fetchone()[0]
    expired = conn.execute(
        "SELECT COUNT(*) FROM evidence WHERE status = 'active' AND valid_until IS NOT NULL AND valid_until <= ?",
        (now_str,)
    ).fetchone()[0]
    evidence_total = fresh + expiring + expired

    # Alerts
    unresolved_alerts = conn.execute(
        "SELECT COUNT(*) FROM alerts WHERE resolved_at IS NULL"
    ).fetchone()[0]
    critical_alerts = conn.execute(
        "SELECT COUNT(*) FROM alerts WHERE resolved_at IS NULL AND severity = 'critical'"
    ).fetchone()[0]

    # Active incidents
    active_incidents = conn.execute(
        "SELECT COUNT(*) FROM incidents WHERE status IN ('open', 'investigating')"
    ).fetchone()[0]

    # Control maturity
    maturity = conn.execute(
        "SELECT maturity_level, COUNT(*) as count FROM controls WHERE maturity_level IS NOT NULL GROUP BY maturity_level"
    ).fetchall()
    maturity_dist = {dict(m)["maturity_level"]: dict(m)["count"] for m in maturity}
    total_controls = sum(maturity_dist.values()) if maturity_dist else 0

    # Integration health
    total_integrations = conn.execute("SELECT COUNT(*) FROM integrations").fetchone()[0]
    healthy_integrations = conn.execute(
        "SELECT COUNT(*) FROM integrations WHERE status IN ('active', 'configured') AND (error_count IS NULL OR error_count = 0)"
    ).fetchone()[0]

    # Build score indicator
    if overall_score >= 80:
        score_indicator = "GREEN"
    elif overall_score >= 60:
        score_indicator = "YELLOW"
    else:
        score_indicator = "RED"

    # Build framework breakdown lines
    fw_lines = []
    for slug, score_data in sorted(latest_scores.items(), key=lambda x: x[0] or ""):
        sc = score_data["score"]
        indicator = "+" if sc >= 80 else "~" if sc >= 60 else "-"
        calc_date = (score_data.get("calculated_at") or "")[:10]
        fw_lines.append(f"  [{indicator}] {slug.upper()}: {sc}% (scored {calc_date})")

    # Build maturity breakdown
    mat_order = ["initial", "developing", "defined", "managed", "optimizing"]
    mat_lines = []
    for level in mat_order:
        count = maturity_dist.get(level, 0)
        if count > 0:
            mat_lines.append(f"  {level.title()}: {count}")

    # Build text summary
    lines = []
    lines.append(f"=== GRC COMPLIANCE DASHBOARD ===")
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append("")
    lines.append(f"OVERALL SCORE: {overall_score}% [{score_indicator}]")
    lines.append(f"Frameworks tracked: {frameworks_count}")
    lines.append("")

    if fw_lines:
        lines.append("FRAMEWORK SCORES:")
        lines.extend(fw_lines)
        lines.append("")

    lines.append("RISK OVERVIEW:")
    lines.append(f"  Total risks: {total_risks}")
    lines.append(f"  High/Critical: {high_risks}")
    lines.append(f"  Open: {open_risks}")
    lines.append("")

    lines.append(f"EVIDENCE ({evidence_total} items):")
    lines.append(f"  Fresh: {fresh}")
    lines.append(f"  Expiring (30d): {expiring}")
    lines.append(f"  Expired: {expired}")
    lines.append("")

    lines.append("ALERTS & INCIDENTS:")
    lines.append(f"  Unresolved alerts: {unresolved_alerts}")
    lines.append(f"  Critical alerts: {critical_alerts}")
    lines.append(f"  Active incidents: {active_incidents}")
    lines.append("")

    if mat_lines:
        lines.append(f"CONTROL MATURITY ({total_controls} controls):")
        lines.extend(mat_lines)
        lines.append("")

    if total_integrations > 0:
        lines.append(f"INTEGRATIONS: {healthy_integrations}/{total_integrations} healthy")
        lines.append("")

    # Dashboard URL
    dashboard_url = os.environ.get("DASHBOARD_URL", "http://localhost:8080/grc/")
    lines.append(f"Full dashboard: {dashboard_url}")

    text_summary = "\n".join(lines)

    # Also regenerate the HTML dashboard
    import subprocess
    db_path = getattr(args, 'db_path', None)
    if db_path:
        scripts_dir = os.path.dirname(os.path.abspath(__file__))
        dashboard_script = os.path.join(scripts_dir, "generate_dashboard.py")
        if os.path.exists(dashboard_script):
            try:
                subprocess.run(
                    ["python3", dashboard_script, "--db-path", db_path],
                    capture_output=True, timeout=30
                )
            except Exception:
                pass  # Non-fatal: text summary is the primary output

    return {
        "status": "ok",
        "overall_score": overall_score,
        "score_indicator": score_indicator,
        "frameworks_count": frameworks_count,
        "framework_scores": {slug: {"score": d["score"], "calculated_at": d.get("calculated_at")} for slug, d in latest_scores.items()},
        "risks": {"total": total_risks, "high_critical": high_risks, "open": open_risks},
        "evidence": {"total": evidence_total, "fresh": fresh, "expiring": expiring, "expired": expired},
        "alerts": {"unresolved": unresolved_alerts, "critical": critical_alerts},
        "active_incidents": active_incidents,
        "maturity": maturity_dist,
        "integrations": {"total": total_integrations, "healthy": healthy_integrations},
        "dashboard_url": dashboard_url,
        "text_summary": text_summary,
        "generated_at": datetime.now().isoformat(timespec="seconds"),
    }



def build_parser():
    """Build argument parser with all actions."""
    parser = argparse.ArgumentParser(description="GRC Database Query Interface")
    parser.add_argument("--action", required=True, help="The action to perform")
    parser.add_argument("--db-path", help="Path to SQLite database")

    # Common filters
    parser.add_argument("--framework", help="Framework slug filter")
    parser.add_argument("--status", help="Status filter")
    parser.add_argument("--id", help="Record ID (supports comma-separated for batch)")
    parser.add_argument("--slug", help="Framework slug for activate/deactivate")

    # Control fields
    parser.add_argument("--title", help="Title for new records")
    parser.add_argument("--description", help="Description")
    parser.add_argument("--category", help="Category")
    parser.add_argument("--priority", help="Priority (1-5)")
    parser.add_argument("--assignee", help="Assignee name")
    parser.add_argument("--due-date", dest="due_date", help="Due date (ISO format)")
    parser.add_argument("--control-id", dest="control_id_code", help="Control ID code (e.g., CC1.1)")
    parser.add_argument("--review-date", dest="review_date", help="Review date")
    parser.add_argument("--implementation-notes", dest="implementation_notes", help="Implementation notes")

    # Evidence fields
    parser.add_argument("--filename", help="Evidence filename")
    parser.add_argument("--filepath", help="Evidence file path")
    parser.add_argument("--type", help="Type (manual, automated, integration)")
    parser.add_argument("--source", help="Source (aws, github, manual, etc.)")
    parser.add_argument("--valid-from", dest="valid_from", help="Valid from date")
    parser.add_argument("--valid-until", dest="valid_until", help="Valid until date")
    parser.add_argument("--control-ids", dest="control_ids", help="Comma-separated control IDs to link")
    parser.add_argument("--expiring-within", dest="expiring_within", help="Days until expiry filter")

    # Risk fields
    parser.add_argument("--likelihood", help="Risk likelihood (1-5)")
    parser.add_argument("--impact", help="Risk impact (1-5)")
    parser.add_argument("--treatment", help="Risk treatment strategy")
    parser.add_argument("--treatment-plan", dest="treatment_plan", help="Treatment plan details")
    parser.add_argument("--owner", help="Owner/responsible person")
    parser.add_argument("--min-score", dest="min_score", help="Minimum risk score filter")
    parser.add_argument("--linked-controls", dest="linked_controls", help="JSON array of control IDs")

    # Vendor fields
    parser.add_argument("--name", help="Vendor/entity name")
    parser.add_argument("--criticality", help="Criticality level")
    parser.add_argument("--data-access", dest="data_access", help="Vendor data access description")
    parser.add_argument("--contact-name", dest="contact_name", help="Contact name")
    parser.add_argument("--contact-email", dest="contact_email", help="Contact email")
    parser.add_argument("--overdue", action="store_true", help="Filter overdue controls")
    parser.add_argument("--overdue-reviews", dest="overdue_reviews", action="store_true", help="Filter overdue reviews")

    # Incident fields
    parser.add_argument("--severity", help="Incident severity")
    parser.add_argument("--root-cause", dest="root_cause", help="Root cause")
    parser.add_argument("--incident-id", dest="incident_id", help="Incident ID for actions/reviews")
    parser.add_argument("--action-type", dest="action_type", help="Incident action type (investigation, containment, etc.)")
    parser.add_argument("--outcome", help="Incident action outcome")
    parser.add_argument("--conducted-by", dest="conducted_by", help="Review conductor name")
    parser.add_argument("--what-happened", dest="what_happened", help="What happened description")
    parser.add_argument("--what-went-well", dest="what_went_well", help="What went well")
    parser.add_argument("--what-went-wrong", dest="what_went_wrong", help="What went wrong")
    parser.add_argument("--lessons-learned", dest="lessons_learned", help="Lessons learned")
    parser.add_argument("--action-items", dest="action_items", help="Action items (JSON array)")
    parser.add_argument("--recommendations", help="Recommendations")
    parser.add_argument("--is-completed", dest="is_completed", type=int, help="Review completed (0 or 1)")
    parser.add_argument("--estimated-cost", dest="estimated_cost", type=float, help="Estimated incident cost")
    parser.add_argument("--actual-cost", dest="actual_cost", type=float, help="Actual incident cost")
    parser.add_argument("--regulatory-required", dest="regulatory_required", type=int, help="Regulatory notification required (0 or 1)")
    parser.add_argument("--regulatory-body", dest="regulatory_body", help="Regulatory body name")
    parser.add_argument("--preventive-actions", dest="preventive_actions", help="Preventive actions taken")
    parser.add_argument("--impact-assessment", dest="impact_assessment", help="Impact assessment")

    # Policy fields
    parser.add_argument("--content-path", dest="content_path", help="Policy content file path")
    parser.add_argument("--approved-by", dest="approved_by", help="Policy approver name")
    parser.add_argument("--version", help="Policy version string")
    parser.add_argument("--review-due", dest="review_due", action="store_true", help="Filter policies with overdue reviews")

    # Policy workflow fields
    parser.add_argument("--policy-id", dest="policy_id", help="Policy ID for versions/approvals/acknowledgments")
    parser.add_argument("--change-summary", dest="change_summary", help="Summary of changes for new policy version")
    parser.add_argument("--requested-by", dest="requested_by", help="Person requesting policy approval")
    parser.add_argument("--request-notes", dest="request_notes", help="Notes for approval request")
    parser.add_argument("--users", help="Comma-separated list of user names")
    parser.add_argument("--pending", action="store_true", help="Filter for pending acknowledgments")

    # Control effectiveness fields
    parser.add_argument("--effectiveness-score", dest="effectiveness_score", type=int, help="Control effectiveness score (0-100)")
    parser.add_argument("--maturity-level", dest="maturity_level", help="Control maturity level (initial/developing/defined/managed/optimizing)")
    parser.add_argument("--min-effectiveness", dest="min_effectiveness", type=int, help="Minimum effectiveness score filter")

    # Test result fields
    parser.add_argument("--test-name", dest="test_name", help="Test name")
    parser.add_argument("--control-id-ref", dest="control_id_ref", help="Control ID reference for test results")
    parser.add_argument("--items-checked", dest="items_checked", type=int, help="Number of items checked")
    parser.add_argument("--items-passed", dest="items_passed", type=int, help="Number of items passed")
    parser.add_argument("--items-failed", dest="items_failed", type=int, help="Number of items failed")
    parser.add_argument("--findings", help="Test findings (JSON array)")
    parser.add_argument("--duration-ms", dest="duration_ms", type=int, help="Test duration in milliseconds")

    # Vendor update fields
    parser.add_argument("--risk-score", dest="risk_score", type=int, help="Vendor risk score")
    parser.add_argument("--next-assessment-date", dest="next_assessment_date", help="Next vendor assessment date")

    # Score history
    parser.add_argument("--days", help="Number of days for history")

    # Mappings
    parser.add_argument("--source-framework", dest="source_framework", help="Source framework for mappings")
    parser.add_argument("--target-framework", dest="target_framework", help="Target framework for mappings")

    # Framework activation
    parser.add_argument("--framework-file", dest="framework_file", help="Path to framework JSON file")
    parser.add_argument("--reason", help="Reason for deactivation")
    
    # Export/report
    parser.add_argument("--output-dir", dest="output_dir", help="Output directory for exports/reports")

    # Asset fields
    parser.add_argument("--ip-address", dest="ip_address", help="Asset IP address")
    parser.add_argument("--hostname", help="Asset hostname")
    parser.add_argument("--os-type", dest="os_type", help="Operating system type")
    parser.add_argument("--software-version", dest="software_version", help="Software version")
    parser.add_argument("--lifecycle-stage", dest="lifecycle_stage", help="Asset lifecycle stage")
    parser.add_argument("--data-classification", dest="data_classification", help="Data classification level")
    parser.add_argument("--discovery-source", dest="discovery_source", help="How the asset was discovered")
    parser.add_argument("--encryption-status", dest="encryption_status", help="Encryption status")
    parser.add_argument("--backup-status", dest="backup_status", help="Backup status")
    parser.add_argument("--patch-status", dest="patch_status", help="Patch status")

    # Training module fields
    parser.add_argument("--duration", type=int, help="Duration in minutes")
    parser.add_argument("--content-type", dest="content_type", help="Training content type")
    parser.add_argument("--content-url", dest="content_url", help="Training content URL")
    parser.add_argument("--difficulty-level", dest="difficulty_level", help="Difficulty level")
    parser.add_argument("--requires-recertification", dest="requires_recertification", type=int, help="Requires recertification (0 or 1)")
    parser.add_argument("--recertification-days", dest="recertification_days", type=int, help="Days between recertifications")

    # Training assignment fields
    parser.add_argument("--module-id", dest="module_id", type=int, help="Training module ID")
    parser.add_argument("--score", type=float, help="Training score")
    parser.add_argument("--completed-at", dest="completed_at", help="Completion timestamp")
    parser.add_argument("--certificate-path", dest="certificate_path", help="Path to certificate file")

    # Vulnerability fields
    parser.add_argument("--cve-id", dest="cve_id", help="CVE identifier")
    parser.add_argument("--cvss-score", dest="cvss_score", type=float, help="CVSS score")
    parser.add_argument("--cvss-vector", dest="cvss_vector", help="CVSS vector string")
    parser.add_argument("--affected-assets", dest="affected_assets", help="Affected assets (JSON string)")
    parser.add_argument("--affected-packages", dest="affected_packages", help="Affected packages (JSON string)")
    parser.add_argument("--remediation-steps", dest="remediation_steps", help="Remediation steps")
    parser.add_argument("--min-cvss", dest="min_cvss", type=float, help="Minimum CVSS score filter")
    parser.add_argument("--fix-version", dest="fix_version", help="Version containing fix")
    parser.add_argument("--resolved-at", dest="resolved_at", help="Resolution timestamp")
    parser.add_argument("--resolved-by", dest="resolved_by", help="Person who resolved")
    parser.add_argument("--risk-accepted", dest="risk_accepted", type=int, help="Risk accepted (0 or 1)")
    parser.add_argument("--risk-acceptance-reason", dest="risk_acceptance_reason", help="Reason for risk acceptance")

    # Access review fields
    parser.add_argument("--scope-type", dest="scope_type", help="Access review scope type")
    parser.add_argument("--scope-config", dest="scope_config", help="Access review scope config")
    parser.add_argument("--reviewer", help="Reviewer name")
    parser.add_argument("--campaign-id", dest="campaign_id", help="Access review campaign ID")
    parser.add_argument("--user-name", dest="user_name", help="User name for access review")
    parser.add_argument("--resource", help="Resource for access review")
    parser.add_argument("--current-access", dest="current_access", help="Current access level")
    parser.add_argument("--decision", help="Access review decision")
    parser.add_argument("--notes", help="Notes for review item")
    parser.add_argument("--start-date", dest="start_date", help="Start date (ISO format)")

    # Questionnaire fields
    parser.add_argument("--template-id", dest="template_id", help="Questionnaire template ID")
    parser.add_argument("--respondent", help="Questionnaire respondent")
    parser.add_argument("--vendor-id", dest="vendor_id", help="Vendor ID for questionnaire")
    parser.add_argument("--questions", help="Questions JSON array")
    parser.add_argument("--response-id", dest="response_id", help="Questionnaire response ID")
    parser.add_argument("--question-index", dest="question_index", type=int, help="Question index")
    parser.add_argument("--answer-text", dest="answer_text", help="Answer text")
    parser.add_argument("--reviewed-by", dest="reviewed_by", help="Reviewed by person")

    # Integration arguments
    parser.add_argument("--provider", help="Integration provider (aws, github, google-workspace, okta)")
    parser.add_argument("--schedule", help="Cron schedule expression")
    parser.add_argument("--config", help="Integration configuration JSON")
    parser.add_argument("--last-sync", dest="last_sync", help="Last sync timestamp")
    parser.add_argument("--next-sync", dest="next_sync", help="Next sync timestamp")
    parser.add_argument("--error-message", dest="error_message", help="Error message text")
    # Alert arguments
    parser.add_argument("--acknowledged", help="Filter by acknowledged status (0/1)")
    parser.add_argument("--resolved", help="Filter by resolved status (0/1)")
    parser.add_argument("--resource-type", dest="resource_type", help="Resource type for alert")
    parser.add_argument("--resource-id", dest="resource_id", help="Resource identifier for alert")
    parser.add_argument("--drift-details", dest="drift_details", help="Drift details JSON")
    parser.add_argument("--acknowledged-by", dest="acknowledged_by", help="Who acknowledged the alert")
    # Browser check arguments
    parser.add_argument("--url", help="URL for browser check")
    parser.add_argument("--check-type", dest="check_type", help="Check type (gdpr/ssl/security_headers/uptime)")
    parser.add_argument("--last-run", dest="last_run", help="Last run timestamp")
    parser.add_argument("--last-result", dest="last_result", help="Last result JSON")
    parser.add_argument("--last-status", dest="last_status", help="Last check status")
    parser.add_argument("--period", help="Digest period: daily/weekly/monthly")
    parser.add_argument("--output", help="Output file path for dashboard HTML")
    # Credential management arguments
    parser.add_argument("--auth-method", dest="auth_method", help="Auth method (iam_role, github_app, service_principal, etc.)")
    parser.add_argument("--file-content", dest="file_content", help="File content for evidence storage")

    return parser


# Action dispatch table
ACTIONS = {
    "status": action_status,
    "activate-framework": action_activate_framework,
    "deactivate-framework": action_deactivate_framework,
    "list-controls": action_list_controls,
    "add-control": action_add_control,
    "update-control": action_update_control,
    "add-evidence": action_add_evidence,
    "update-evidence": action_update_evidence,
    "list-evidence": action_list_evidence,
    "add-risk": action_add_risk,
    "list-risks": action_list_risks,
    "update-risk": action_update_risk,
    "add-vendor": action_add_vendor,
    "list-vendors": action_list_vendors,
    "update-vendor": action_update_vendor,
    "add-incident": action_add_incident,
    "update-incident": action_update_incident,
    "list-incidents": action_list_incidents,
    # Incident Timeline & Reviews
    "add-incident-action": action_add_incident_action,
    "list-incident-actions": action_list_incident_actions,
    "add-incident-review": action_add_incident_review,
    "update-incident-review": action_update_incident_review,
    "list-incident-reviews": action_list_incident_reviews,
    "incident-summary": action_incident_summary,
    "add-policy": action_add_policy,
    "list-policies": action_list_policies,
    "update-policy": action_update_policy,
    # Policy Workflows
    "create-policy-version": action_create_policy_version,
    "list-policy-versions": action_list_policy_versions,
    "submit-policy-approval": action_submit_policy_approval,
    "review-policy-approval": action_review_policy_approval,
    "list-policy-approvals": action_list_policy_approvals,
    "require-policy-acknowledgment": action_require_policy_acknowledgment,
    "acknowledge-policy": action_acknowledge_policy,
    "list-policy-acknowledgments": action_list_policy_acknowledgments,
    # Control Effectiveness & Test Results
    "update-control-effectiveness": action_update_control_effectiveness,
    "list-controls-by-maturity": action_list_controls_by_maturity,
    "add-test-result": action_add_test_result,
    "list-test-results": action_list_test_results,
    "test-summary": action_test_summary,
    "score-history": action_score_history,
    "list-mappings": action_list_mappings,
    "gap-analysis": action_gap_analysis,
    "export-evidence": action_export_evidence,
    "generate-report": action_generate_report,
    # Assets
    "add-asset": action_add_asset,
    "list-assets": action_list_assets,
    "link-asset-controls": action_link_asset_controls,
    "update-asset": action_update_asset,
    # Training
    "add-training-module": action_add_training_module,
    "list-training-modules": action_list_training_modules,
    "add-training-assignment": action_add_training_assignment,
    "list-training-assignments": action_list_training_assignments,
    "update-training-assignment": action_update_training_assignment,
    # Vulnerabilities
    "add-vulnerability": action_add_vulnerability,
    "list-vulnerabilities": action_list_vulnerabilities,
    "link-vulnerability-controls": action_link_vulnerability_controls,
    "update-vulnerability": action_update_vulnerability,
    # Access Reviews
    "add-access-review": action_add_access_review,
    "list-access-reviews": action_list_access_reviews,
    "update-access-review": action_update_access_review,
    "add-review-item": action_add_review_item,
    "list-review-items": action_list_review_items,
    "update-review-item": action_update_review_item,
    # Questionnaires
    "add-questionnaire-template": action_add_questionnaire_template,
    "list-questionnaire-templates": action_list_questionnaire_templates,
    "add-questionnaire-response": action_add_questionnaire_response,
    "list-questionnaire-responses": action_list_questionnaire_responses,
    "add-questionnaire-answer": action_add_questionnaire_answer,
    "update-questionnaire-response": action_update_questionnaire_response,
    # Integrations
    "add-integration": action_add_integration,
    "list-integrations": action_list_integrations,
    "update-integration": action_update_integration,
    "sync-integration": action_sync_integration,
    "integration-health": action_integration_health,
    # Alerts
    "add-alert": action_add_alert,
    "list-alerts": action_list_alerts,
    "acknowledge-alert": action_acknowledge_alert,
    "resolve-alert": action_resolve_alert,
    # Browser Checks
    "add-browser-check": action_add_browser_check,
    "list-browser-checks": action_list_browser_checks,
    "update-browser-check": action_update_browser_check,
    "run-browser-check": action_run_browser_check,
    "check-drift": action_check_drift,
    "drift-history": action_drift_history,
    "auto-map-evidence": action_auto_map_evidence,
    "list-evidence-gaps": action_list_evidence_gaps,
    "compliance-calendar": action_compliance_calendar,
    "compliance-digest": action_compliance_digest,
    "generate-dashboard": action_generate_dashboard,
    # Companion Detection
    "list-companions": action_list_companions,
    # Integration Setup
    "setup-guide": action_setup_guide,
    "show-policy": action_show_policy,
    "test-connection": action_test_connection,
    # Credential Management
    "store-credential": action_store_credential,
    "get-credential": action_get_credential,
    "delete-credential": action_delete_credential,
}


def main():
    parser = build_parser()
    args, _unknown = parser.parse_known_args()

    action_name = args.action
    if action_name not in ACTIONS:
        result = {"status": "error", "message": f"Unknown action: {action_name}", "available": sorted(ACTIONS.keys())}
        print(json.dumps(result), file=sys.stderr)
        sys.exit(1)

    try:
        conn = get_db(args.db_path)
        result = ACTIONS[action_name](conn, args)
        conn.close()

        if result.get("status") == "error":
            print(json.dumps(result, indent=2, default=str), file=sys.stderr)
            sys.exit(1)

        print(json.dumps(result, indent=2, default=str))
        sys.exit(0)
    except Exception as e:
        error = {"status": "error", "message": f"Action '{action_name}' failed. Check logs for details.", "action": action_name}
        print(f"ERROR: {action_name}: {e}", file=sys.stderr)
        print(json.dumps(error), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
