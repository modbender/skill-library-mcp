#!/usr/bin/env python3
"""Initialize the GRC compliance SQLite database.

Creates all tables, enables WAL mode, sets schema version.
Idempotent — safe to run multiple times.

Usage:
    python3 init_db.py [--db-path /path/to/db]

Default DB path: ~/.openclaw/grc/compliance.sqlite
"""

import argparse
import json
import os
import sqlite3
import sys

SCHEMA_VERSION = "6.0.0"

DEFAULT_DB_PATH = os.path.expanduser("~/.openclaw/grc/compliance.sqlite")

SCHEMA_SQL = """
-- Schema version tracking
CREATE TABLE IF NOT EXISTS schema_version (
    version TEXT NOT NULL,
    applied_at TEXT DEFAULT (datetime('now'))
);

-- Compliance frameworks activated for the organization
CREATE TABLE IF NOT EXISTS frameworks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    slug TEXT UNIQUE NOT NULL,
    version TEXT,
    status TEXT DEFAULT 'active',
    priority INTEGER DEFAULT 1,
    activated_at TEXT DEFAULT (datetime('now')),
    notes TEXT
);

-- Controls from activated frameworks
CREATE TABLE IF NOT EXISTS controls (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    framework_id INTEGER REFERENCES frameworks(id),
    control_id TEXT NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    category TEXT,
    status TEXT DEFAULT 'not_started',
    assignee TEXT,
    due_date TEXT,
    priority INTEGER DEFAULT 3,
    review_date TEXT,
    implementation_notes TEXT,
    last_updated TEXT DEFAULT (datetime('now')),
    UNIQUE(framework_id, control_id)
);

-- Evidence linked to controls
CREATE TABLE IF NOT EXISTS evidence (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    filename TEXT,
    filepath TEXT,
    description TEXT,
    type TEXT,
    source TEXT,
    valid_from TEXT,
    valid_until TEXT,
    status TEXT DEFAULT 'active',
    uploaded_at TEXT DEFAULT (datetime('now')),
    metadata TEXT
);

-- Evidence-to-control linkage (many-to-many)
CREATE TABLE IF NOT EXISTS evidence_controls (
    evidence_id INTEGER REFERENCES evidence(id) ON DELETE CASCADE,
    control_id INTEGER REFERENCES controls(id) ON DELETE CASCADE,
    PRIMARY KEY (evidence_id, control_id)
);

-- Risks
CREATE TABLE IF NOT EXISTS risks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    category TEXT,
    likelihood INTEGER CHECK(likelihood BETWEEN 1 AND 5),
    impact INTEGER CHECK(impact BETWEEN 1 AND 5),
    score INTEGER GENERATED ALWAYS AS (likelihood * impact) STORED,
    treatment TEXT,
    treatment_plan TEXT,
    owner TEXT,
    review_date TEXT,
    status TEXT DEFAULT 'open',
    linked_controls TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    last_updated TEXT DEFAULT (datetime('now'))
);

-- Vendors
CREATE TABLE IF NOT EXISTS vendors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    category TEXT,
    criticality TEXT DEFAULT 'medium',
    data_access TEXT,
    contact_name TEXT,
    contact_email TEXT,
    contract_start TEXT,
    contract_end TEXT,
    last_assessment_date TEXT,
    next_assessment_date TEXT,
    risk_score INTEGER,
    status TEXT DEFAULT 'active',
    notes TEXT,
    documents TEXT
);

-- Assets
CREATE TABLE IF NOT EXISTS assets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    type TEXT,
    criticality TEXT DEFAULT 'medium',
    owner TEXT,
    location TEXT,
    status TEXT DEFAULT 'active',
    description TEXT,
    linked_controls TEXT,
    metadata TEXT,
    ip_address TEXT,
    hostname TEXT,
    os_type TEXT,
    software_version TEXT,
    lifecycle_stage TEXT DEFAULT 'in_use',
    deployment_date TEXT,
    encryption_status TEXT,
    backup_status TEXT,
    patch_status TEXT,
    last_patched_date TEXT,
    discovery_source TEXT DEFAULT 'manual',
    data_classification TEXT DEFAULT 'internal',
    created_at TEXT,
    updated_at TEXT
);

-- Incidents
CREATE TABLE IF NOT EXISTS incidents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    type TEXT,
    severity TEXT DEFAULT 'medium',
    status TEXT DEFAULT 'detected',
    reported_by TEXT,
    reported_at TEXT DEFAULT (datetime('now')),
    resolved_at TEXT,
    root_cause TEXT,
    corrective_actions TEXT,
    affected_systems TEXT,
    impact_assessment TEXT,
    timeline TEXT,
    lessons_learned TEXT,
    metadata TEXT
);

-- Policies
CREATE TABLE IF NOT EXISTS policies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    type TEXT,
    version TEXT DEFAULT '1.0',
    status TEXT DEFAULT 'draft',
    content_path TEXT,
    approved_by TEXT,
    approved_at TEXT,
    review_date TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    last_updated TEXT DEFAULT (datetime('now')),
    notes TEXT
);

-- Policy-to-control linkage
CREATE TABLE IF NOT EXISTS policy_controls (
    policy_id INTEGER REFERENCES policies(id) ON DELETE CASCADE,
    control_id INTEGER REFERENCES controls(id) ON DELETE CASCADE,
    PRIMARY KEY (policy_id, control_id)
);

-- Training modules
CREATE TABLE IF NOT EXISTS training_modules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    category TEXT,
    description TEXT,
    duration_minutes INTEGER,
    duration INTEGER,
    status TEXT DEFAULT 'active',
    created_at TEXT DEFAULT (datetime('now')),
    content_type TEXT,
    content_url TEXT,
    difficulty_level TEXT DEFAULT 'beginner',
    requires_recertification INTEGER DEFAULT 0,
    recertification_days INTEGER,
    updated_at TEXT
);

-- Training assignments
CREATE TABLE IF NOT EXISTS training_assignments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    module_id INTEGER REFERENCES training_modules(id),
    assignee TEXT NOT NULL,
    status TEXT DEFAULT 'pending',
    due_date TEXT,
    completed_at TEXT,
    score INTEGER,
    assigned_at TEXT,
    certificate_path TEXT,
    created_at TEXT,
    updated_at TEXT
);

-- Personnel checklists
CREATE TABLE IF NOT EXISTS checklists (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT NOT NULL,
    person_name TEXT NOT NULL,
    status TEXT DEFAULT 'in_progress',
    created_at TEXT DEFAULT (datetime('now')),
    completed_at TEXT
);

-- Checklist items
CREATE TABLE IF NOT EXISTS checklist_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    checklist_id INTEGER REFERENCES checklists(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    completed INTEGER DEFAULT 0,
    completed_at TEXT,
    notes TEXT
);

-- Compliance scores (historical)
CREATE TABLE IF NOT EXISTS compliance_scores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    framework_slug TEXT,
    score REAL NOT NULL,
    total_controls INTEGER,
    healthy_controls INTEGER,
    at_risk_controls INTEGER,
    critical_controls INTEGER,
    calculated_at TEXT DEFAULT (datetime('now')),
    metadata TEXT
);

-- Alerts
CREATE TABLE IF NOT EXISTS alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT NOT NULL,
    severity TEXT DEFAULT 'info',
    title TEXT NOT NULL,
    message TEXT,
    status TEXT DEFAULT 'active',
    triggered_at TEXT DEFAULT (datetime('now')),
    resolved_at TEXT,
    cooldown_until TEXT,
    metadata TEXT
);

-- Control mappings (cross-framework)
CREATE TABLE IF NOT EXISTS control_mappings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_framework TEXT NOT NULL,
    source_control_id TEXT NOT NULL,
    target_framework TEXT NOT NULL,
    target_control_id TEXT NOT NULL,
    confidence REAL DEFAULT 1.0,
    UNIQUE(source_framework, source_control_id, target_framework, target_control_id)
);

-- Audit log
CREATE TABLE IF NOT EXISTS audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    action TEXT NOT NULL,
    entity_type TEXT,
    entity_id INTEGER,
    details TEXT,
    performed_at TEXT DEFAULT (datetime('now'))
);

-- Create indexes for common queries
CREATE INDEX IF NOT EXISTS idx_controls_framework ON controls(framework_id);
CREATE INDEX IF NOT EXISTS idx_controls_status ON controls(status);
CREATE INDEX IF NOT EXISTS idx_evidence_status ON evidence(status);
CREATE INDEX IF NOT EXISTS idx_evidence_valid_until ON evidence(valid_until);
CREATE INDEX IF NOT EXISTS idx_risks_score ON risks(score);
CREATE INDEX IF NOT EXISTS idx_risks_status ON risks(status);
CREATE INDEX IF NOT EXISTS idx_vendors_criticality ON vendors(criticality);
CREATE INDEX IF NOT EXISTS idx_incidents_status ON incidents(status);
CREATE INDEX IF NOT EXISTS idx_incidents_severity ON incidents(severity);
CREATE INDEX IF NOT EXISTS idx_compliance_scores_framework ON compliance_scores(framework_slug);
CREATE INDEX IF NOT EXISTS idx_compliance_scores_date ON compliance_scores(calculated_at);
CREATE INDEX IF NOT EXISTS idx_control_mappings_source ON control_mappings(source_framework, source_control_id);
CREATE INDEX IF NOT EXISTS idx_control_mappings_target ON control_mappings(target_framework, target_control_id);
CREATE INDEX IF NOT EXISTS idx_alerts_status ON alerts(status);
CREATE INDEX IF NOT EXISTS idx_audit_log_entity ON audit_log(entity_type, entity_id);

-- ==========================================================================
-- Extended Tables
-- ==========================================================================

CREATE TABLE IF NOT EXISTS vulnerabilities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    cve_id TEXT,
    description TEXT,
    source TEXT,
    cvss_score REAL,
    cvss_vector TEXT,
    severity TEXT DEFAULT 'medium',
    status TEXT DEFAULT 'open',
    assignee TEXT,
    affected_assets TEXT,
    affected_packages TEXT,
    remediation_steps TEXT,
    fix_version TEXT,
    due_date TEXT,
    resolved_at TEXT,
    resolved_by TEXT,
    risk_accepted INTEGER DEFAULT 0,
    risk_acceptance_reason TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    last_updated TEXT DEFAULT (datetime('now')),
    updated_at TEXT
);

CREATE TABLE IF NOT EXISTS vulnerability_controls (
    vulnerability_id INTEGER REFERENCES vulnerabilities(id) ON DELETE CASCADE,
    control_id INTEGER REFERENCES controls(id) ON DELETE CASCADE,
    created_at TEXT,
    PRIMARY KEY (vulnerability_id, control_id)
);

CREATE TABLE IF NOT EXISTS access_review_campaigns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    scope_type TEXT,
    scope_config TEXT,
    reviewer TEXT,
    status TEXT DEFAULT 'draft',
    start_date TEXT,
    due_date TEXT,
    completed_at TEXT,
    total_items INTEGER DEFAULT 0,
    reviewed_items INTEGER DEFAULT 0,
    approved_items INTEGER DEFAULT 0,
    revoked_items INTEGER DEFAULT 0,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT
);

CREATE TABLE IF NOT EXISTS access_review_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    campaign_id INTEGER REFERENCES access_review_campaigns(id) ON DELETE CASCADE,
    user_name TEXT NOT NULL,
    resource TEXT NOT NULL,
    current_access TEXT,
    decision TEXT DEFAULT 'pending',
    reviewer TEXT,
    reviewed_at TEXT,
    notes TEXT,
    created_at TEXT
);

CREATE TABLE IF NOT EXISTS questionnaire_templates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    category TEXT,
    questions TEXT,
    total_questions INTEGER DEFAULT 0,
    status TEXT DEFAULT 'active',
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT
);

CREATE TABLE IF NOT EXISTS questionnaire_responses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    template_id INTEGER REFERENCES questionnaire_templates(id),
    respondent TEXT NOT NULL,
    vendor_id INTEGER REFERENCES vendors(id),
    status TEXT DEFAULT 'draft',
    total_questions INTEGER DEFAULT 0,
    answered_questions INTEGER DEFAULT 0,
    submitted_at TEXT,
    reviewed_at TEXT,
    reviewed_by TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT
);

CREATE TABLE IF NOT EXISTS questionnaire_answers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    response_id INTEGER REFERENCES questionnaire_responses(id) ON DELETE CASCADE,
    question_index INTEGER NOT NULL,
    answer_text TEXT,
    status TEXT DEFAULT 'pending',
    notes TEXT,
    created_at TEXT
);

CREATE TABLE IF NOT EXISTS asset_controls (
    asset_id INTEGER REFERENCES assets(id) ON DELETE CASCADE,
    control_id INTEGER REFERENCES controls(id) ON DELETE CASCADE,
    PRIMARY KEY (asset_id, control_id)
);

-- Extended Indexes
CREATE INDEX IF NOT EXISTS idx_vulnerabilities_status ON vulnerabilities(status);
CREATE INDEX IF NOT EXISTS idx_vulnerabilities_severity ON vulnerabilities(severity);
CREATE INDEX IF NOT EXISTS idx_vulnerabilities_cve ON vulnerabilities(cve_id);
CREATE INDEX IF NOT EXISTS idx_access_reviews_status ON access_review_campaigns(status);
CREATE INDEX IF NOT EXISTS idx_questionnaire_responses_status ON questionnaire_responses(status);
CREATE INDEX IF NOT EXISTS idx_assets_lifecycle ON assets(lifecycle_stage);
CREATE INDEX IF NOT EXISTS idx_assets_classification ON assets(data_classification);
CREATE INDEX IF NOT EXISTS idx_training_assignments_status ON training_assignments(status);

-- ==========================================================================
-- Integration Credentials (secure auth storage)
-- ==========================================================================

CREATE TABLE IF NOT EXISTS integration_credentials (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    provider TEXT NOT NULL,
    auth_method TEXT NOT NULL,
    config TEXT NOT NULL,
    credential_path TEXT,
    status TEXT DEFAULT 'pending',
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    last_used TEXT,
    expires_at TEXT
);

CREATE INDEX IF NOT EXISTS idx_integration_credentials_provider ON integration_credentials(provider);
CREATE INDEX IF NOT EXISTS idx_integration_credentials_status ON integration_credentials(status);

-- Integrations (cloud provider connections)
CREATE TABLE IF NOT EXISTS integrations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    provider TEXT NOT NULL,
    status TEXT DEFAULT 'pending',
    config TEXT,
    schedule TEXT,
    last_sync TEXT,
    next_sync TEXT,
    last_error TEXT,
    error_count INTEGER DEFAULT 0,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_integrations_provider ON integrations(provider);
CREATE INDEX IF NOT EXISTS idx_integrations_status ON integrations(status);

-- Incident actions (timeline entries for incidents)
CREATE TABLE IF NOT EXISTS incident_actions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    incident_id INTEGER REFERENCES incidents(id) ON DELETE CASCADE,
    action_type TEXT NOT NULL,
    description TEXT,
    performed_by TEXT,
    outcome TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_incident_actions_incident ON incident_actions(incident_id);
"""

EXPECTED_TABLES = [
    "schema_version", "frameworks", "controls", "evidence", "evidence_controls",
    "risks", "vendors", "assets", "incidents", "policies", "policy_controls",
    "training_modules", "training_assignments", "checklists", "checklist_items",
    "compliance_scores", "alerts", "control_mappings", "audit_log",
    "vulnerabilities", "vulnerability_controls",
    "access_review_campaigns", "access_review_items",
    "questionnaire_templates", "questionnaire_responses", "questionnaire_answers",
    "asset_controls",
    "integration_credentials",
    "integrations",
    "incident_actions",
]


def get_db_path(args_db_path=None):
    """Resolve DB path from args, env, or default."""
    if args_db_path:
        return args_db_path
    return os.environ.get("GRC_DB_PATH", DEFAULT_DB_PATH)


def init_database(db_path):
    """Initialize the GRC database. Returns JSON result."""
    # Ensure directory exists
    db_dir = os.path.dirname(db_path)
    if db_dir:
        os.makedirs(db_dir, mode=0o700, exist_ok=True)

    conn = sqlite3.connect(db_path)
    os.chmod(db_path, 0o600)
    cursor = conn.cursor()

    # Check if already initialized
    try:
        cursor.execute("SELECT version FROM schema_version LIMIT 1")
        row = cursor.fetchone()
        if row:
            conn.close()
            return {
                "status": "already_initialized",
                "version": row[0],
                "db_path": db_path
            }
    except sqlite3.OperationalError:
        pass  # Table doesn't exist yet

    # Enable WAL mode
    cursor.execute("PRAGMA journal_mode=WAL;")

    # Enable foreign keys
    cursor.execute("PRAGMA foreign_keys = ON;")

    # Create all tables
    cursor.executescript(SCHEMA_SQL)

    # Insert schema version
    cursor.execute("INSERT INTO schema_version (version) VALUES (?)", (SCHEMA_VERSION,))

    conn.commit()

    # Count tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
    tables = [row[0] for row in cursor.fetchall()]

    conn.close()

    return {
        "status": "initialized",
        "version": SCHEMA_VERSION,
        "db_path": db_path,
        "tables_created": len(tables),
        "tables": sorted(tables)
    }


def main():
    parser = argparse.ArgumentParser(description="Initialize GRC compliance database")
    parser.add_argument("--db-path", help="Path to SQLite database file")
    args = parser.parse_args()

    db_path = get_db_path(args.db_path)

    try:
        result = init_database(db_path)
        print(json.dumps(result, indent=2))
        sys.exit(0)
    except Exception as e:
        error = {"status": "error", "message": str(e)}
        print(json.dumps(error), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
