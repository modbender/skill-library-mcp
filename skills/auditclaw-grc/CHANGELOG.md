# Changelog

## [6.0.0] - 2026-02-15

### Added
- Secure credential management with path traversal protection and secret masking
- CSV injection protection in evidence exports
- XSS prevention in HTML report generation

### Changed
- Skill renamed from `audeng-grc` to `auditclaw-grc`
- SKILL.md consolidated: merged 5 versioned Quick Command Reference sections into one unified reference organized by category
- All version-tagged section headings (V2, V3, V4, V5) removed in favor of flat, category-based organization
- Proactive Suggestions table merged into single comprehensive table
- Updated action count to 97, table count to 36
- Schema version bumped to 6.0.0

### Removed
- 4 dead scaffolding scripts (actions_v4_drift.py, actions_v4_evidence_cal.py, patch_db_query_drift.py, patch_db_query_evidcal.py)
- Version-prefix comments in db_query.py replaced with category-based comments

## [5.0.0] - 2026-02-13

### Added
- Companion skill detection (`list-companions` action)
- Integration setup guides for AWS, GitHub, Azure, GCP, and identity providers
- `setup-guide`, `show-policy`, and `test-connection` actions for provider onboarding
- Credential store (`store-credential`, `get-credential`, `delete-credential` actions)
- `integration_credentials` table for secure credential storage
- 3 new db_query.py actions (97 total)

### Changed
- SKILL.md updated with companion skill documentation and integration onboarding flows
- Schema version bumped to 5.0.0 (36 tables total)

## [4.0.0] - 2026-02-12

### Added
- Cloud provider integrations (AWS, GitHub, Azure, GCP, Okta, Google Workspace)
- Integration health monitoring and sync tracking
- Compliance alerts with acknowledge/resolve workflow
- Browser-based URL scanning (headers, SSL, GDPR) with scheduling
- Drift detection and drift history tracking
- Auto-evidence mapping and evidence gap analysis
- Compliance calendar and compliance digest
- Interactive HTML dashboard with Canvas integration
- 3 new frameworks: FedRAMP Moderate (282 controls), ISO 42001 (40), SOX ITGC (50)
- 2 new database tables (integrations, browser_checks)
- 27 new db_query.py actions (93 total)

### Changed
- Schema version bumped to 4.0.0 (34 tables total)

## [3.0.0] - 2026-02-11

### Added
- Incident timeline: action tracking (containment, investigation, recovery) with timestamps
- Post-incident reviews with findings, lessons learned, and root cause tracking
- Incident summary with MTTR calculation, severity distribution, and type trends
- Incident cost tracking and regulatory notification flags
- Policy versioning with version chain tracking
- Policy approval workflow: submit, approve, reject, request changes
- Policy acknowledgment tracking per user with due dates
- Control effectiveness scoring (0-100) with automated rating
- Control maturity levels: initial, developing, defined, managed, optimizing
- Test results tracking linked to controls with pass rates and trends
- 4 new frameworks: CIS Controls v8 (153 controls), CMMC 2.0 (113), HITRUST CSF v11 (152), CCPA (28)
- CRUD completeness: update-risk, update-vendor, list-policies, update-policy actions
- 3 integration reference guides: AWS, GitHub, Google Workspace evidence collection
- 5 new database tables (incident_actions, incident_reviews, policy_approvals, policy_acknowledgments, test_results)
- 23 new db_query.py actions (70 total)
- 81 new unit tests (292 total)
- 28 production scenario messages validated

### Changed
- Skill renamed from `grc-compliance` to `auditclaw-grc`
- Schema version bumped to 3.0.0 (32 tables total)

## [2.0.0] - 2026-02-11

### Added
- Asset inventory management (add, list, update, link to controls)
- Training module management with assignment tracking and completion scoring
- Vulnerability management with CVE/CVSS tracking, severity filtering, remediation workflow
- Access review campaigns with review items, approve/revoke/flag decisions
- Vendor questionnaire templates with responses, answers, and scoring
- Trust center HTML page generation
- `link-asset-controls` and `link-vulnerability-controls` junction table actions
- 8 new database tables, 19 new columns on existing tables
- 25 new db_query.py actions (47 total)
- 66 new unit tests (211 total)
- 36 new production scenarios validated (46 total)
- SKILL.md v2.0.0 with V2 commands, interactive flows, and proactive suggestions

### Fixed
- Migration script missing timestamp columns on V2 tables
- Missing score column on questionnaire_responses
- Missing assigned_at on training_assignments

## [1.0.1] - 2026-02-11

### Fixed
- Added `user-invocable: true` to SKILL.md frontmatter for skill discovery
- Removed `sqlite3` from required bins (not needed, Python handles SQLite)

## [1.0.0] - 2026-02-11

### Added
- Initial release with 6 compliance frameworks (SOC 2, ISO 27001, HIPAA, GDPR, NIST CSF, PCI DSS)
- 22 db_query.py actions for controls, evidence, risks, vendors, incidents, policies
- Compliance scoring with trend tracking and drift detection
- Security scanning (HTTP headers, SSL/TLS)
- HTML report generation and evidence export
- Gap analysis with priority scoring and effort estimates
- Cross-framework control mappings
- Cron-based compliance alerts
- 145 unit tests
- 10 production scenarios validated
