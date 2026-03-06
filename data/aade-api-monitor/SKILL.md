---
name: aade-api-monitor
description: Real-time monitoring of Greek AADE tax authority systems — tracks deadlines, rate changes, and compliance updates. File-based, OpenClaw-native.
version: 1.0.0
author: openclaw-greek-accounting
homepage: https://github.com/satoshistackalotto/openclaw-greek-accounting
tags: ["greek", "accounting", "aade", "government-monitoring", "api"]
metadata: {"openclaw": {"requires": {"bins": ["jq", "curl"], "env": ["OPENCLAW_DATA_DIR", "AADE_USERNAME", "AADE_PASSWORD"]}, "optional_env": {"SLACK_WEBHOOK_URL": "Webhook URL for urgent AADE change alerts", "SMS_GATEWAY_URL": "SMS gateway for critical compliance alerts", "GOOGLE_CALENDAR_ID": "Google Calendar ID for compliance deadline sync (optional)", "OUTLOOK_CALENDAR_ID": "Outlook Calendar ID for compliance deadline sync (optional)"}, "notes": "AADE credentials required for monitoring government portal. Slack and SMS alert channels are optional — if not configured, alerts are written to local files only."}}
---

# AADE API Monitor

This skill provides comprehensive monitoring of AADE systems and announcements through OpenClaw's file processing capabilities, delivering real-time alerts for Greek tax compliance changes.


## Setup

```bash
export OPENCLAW_DATA_DIR="/data"
export AADE_USERNAME="your-aade-username"
export AADE_PASSWORD="your-aade-password"
which jq curl || sudo apt install jq curl
```

AADE credentials are used for authenticated read-only checks of announcements, rate changes, and system status. This skill never submits filings.


## Core Philosophy

- **File-First Processing**: Monitor and process government documents, not complex APIs
- **Reliable Operation**: Work offline with cached data when government sites unavailable
- **OpenClaw Native**: Built specifically for OpenClaw's strengths and limitations
- **Production Ready**: Error handling, logging, and recovery built-in from start
- **Greek Business Focus**: Professional alerts and reporting in Greek

## OpenClaw Commands

### Core AADE Monitoring Commands
```bash
# Primary monitoring operations
openclaw aade monitor --enable --government-sites --cache-updates
openclaw aade check-updates --since "24 hours" --urgent-only
openclaw aade download-announcements --date today --all-categories
openclaw aade scan-deadlines --compare-previous --alert-changes

# System status monitoring  
openclaw aade status-check --taxis --mydata --efka --report-outages
openclaw aade system-health --uptime-tracking --performance-metrics
openclaw aade maintenance-schedule --upcoming --impact-assessment

# Document processing
openclaw aade process-documents --input /data/incoming/government/ --extract-deadlines
openclaw aade classify-updates --tax-changes --deadline-changes --system-updates
openclaw aade generate-alerts --priority high --recipients accounting-team
```

### Deadline & Rate Change Monitoring
```bash
# Deadline monitoring
openclaw aade monitor-deadlines --vat --income-tax --enfia --social-security
openclaw aade deadline-changes --since yesterday --client-impact-analysis
openclaw aade calendar-update --sync-changes --notify-affected-clients

# Rate and regulation changes
openclaw aade monitor-rates --vat-rates --tax-brackets --social-security
openclaw aade regulation-tracker --new-circulars --law-changes --implementation-dates
openclaw aade impact-analysis --rate-changes --client-calculations --cost-impact
```

### Integration & Reporting Commands
```bash
# Integration with other skills
openclaw aade integrate --cli-deadline-monitor --email-processor --meta-skill
openclaw aade export-data --format json --destination /data/dashboard/state/
openclaw aade sync-calendar --include-holidays

# Professional reporting
openclaw aade report-generate --daily --weekly --monthly --client-ready-greek
openclaw aade client-notifications --deadline-changes --rate-updates --professional-tone
openclaw aade compliance-dashboard --current-status --upcoming-deadlines --action-items
```

## OpenClaw File Processing Architecture

### File System Organization
```yaml
AADE_File_Structure:
  input_monitoring:                              # Raw government documents arrive here
    - /data/incoming/government/                 # All AADE/government downloads
    
  processing_workspace:                          # Ephemeral — cleared after pipeline
    - /data/processing/compliance/               # Classification and extraction workspace
    
  output_delivery:
    - /data/dashboard/state/current-alerts.json  # Active alerts for dashboard
    - /data/dashboard/state/deadline-tracker.json # Updated deadline tracker
    - /data/reports/compliance/                   # Professional compliance reports
    - /data/exports/compliance-deadlines.json       # Calendar integration export
```

### Document Processing Pipeline
```yaml
Processing_Workflow:
  step_1_download:
    command: "openclaw aade download-batch --sources all --format pdf,html,xml"
    input: "Government website monitoring"
    output: "/data/incoming/government/{YYYYMMDD}/"
    
  step_2_extract:
    command: "openclaw aade extract-content --use-deepread --greek-language"
    input: "/data/incoming/government/"
    output: "/data/processing/compliance/"
    
  step_3_classify:
    command: "openclaw aade classify-importance --deadline-changes high --rate-changes high"
    input: "/data/processing/compliance/"
    output: "/data/processing/compliance/"
    
  step_4_compare:
    command: "openclaw aade detect-changes --compare-with-cache --highlight-differences"
    input: "/data/processing/compliance/"
    output: "/data/processing/compliance/"
    
  step_5_validate:
    command: "openclaw aade validate-data --cross-reference --accuracy-check"
    input: "/data/processing/compliance/"
    output: "/data/processing/compliance/"
    
  step_6_generate:
    command: "openclaw aade generate-outputs --alerts --reports --notifications"
    input: "/data/processing/compliance/"
    output: "/data/dashboard/state/ and /data/reports/compliance/"
```

## Intelligent Document Monitoring

### AADE Website Monitoring Strategy
```yaml
Government_Site_Monitoring:
  primary_sources:
    aade_main:
      url: "https://www.aade.gr"
      sections: ["announcements", "circulars", "deadlines", "rates"]
      frequency: "every_2_hours"
      
    taxis_updates:
      url: "https://www1.aade.gr/taxisnet"
      sections: ["system-announcements", "maintenance-schedules"]  
      frequency: "every_4_hours"
      
    mydata_status:
      url: "https://mydatapi.aade.gr"
      sections: ["api-status", "system-updates", "technical-announcements"]
      frequency: "hourly"
      
  backup_sources:
    press_releases:
      url: "https://www.aade.gr/deltia-typou"
      fallback: true
      
    legal_database:
      url: "https://www.aade.gr/nomothesia"
      frequency: "daily"
```

### Intelligent Change Detection
```yaml
Change_Detection_Logic:
  deadline_changes:
    triggers:
      - "Date changes in deadline tables"
      - "New deadline announcements"  
      - "Extension or acceleration notices"
    confidence_threshold: 0.95
    validation: "Cross-reference multiple sources"
    
  rate_changes:
    triggers:
      - "VAT rate modifications"
      - "Tax bracket adjustments"
      - "Social security rate updates"
    effective_date_tracking: "Extract implementation dates"
    impact_calculation: "Estimate client effects"
    
  system_updates:
    triggers:
      - "Maintenance announcements"
      - "New feature releases"
      - "System outage notifications"
    criticality_assessment: "Business impact analysis"
    workaround_suggestions: "Alternative procedures"
```

## OpenClaw-Native Processing Features

### Robust Error Handling
```bash
# Error recovery commands
openclaw aade retry-failed --batch-id {id} --fix-network-issues
openclaw aade fallback-mode --use-cached-data --offline-operation
openclaw aade manual-review --flagged-updates --require-human-verification

# Monitoring and diagnostics
openclaw aade health-check --test-all-sources --report-failures
openclaw aade diagnostics --connection-test --parsing-test --alert-test
openclaw aade logs --filter errors --last 48h --include-context
```

### Caching & Offline Operation
```yaml
Caching_Strategy:
  announcement_cache:
    retention: "90 days"
    update_frequency: "every_2_hours"
    fallback_behavior: "Use cached data if source unavailable"
    
  deadline_cache:
    retention: "1 year"
    critical_updates: "Force immediate refresh"
    validation: "Compare multiple sources for accuracy"
    
  system_status_cache:
    retention: "7 days" 
    real_time_updates: "When possible"
    offline_mode: "Report last known status with timestamp"
```

### Greek Language Processing
```yaml
Greek_Document_Processing:
  text_extraction:
    encoding: "UTF-8, Windows-1253, ISO-8859-7"
    ocr_support: "Greek character recognition via deepread"
    
  keyword_detection:
    deadline_terms: ["προθεσμία", "λήξη", "υποβολή", "deadline"]
    rate_terms: ["συνπžελεσπžήπš", "ποσοσπžς", "π ςροπš", "rate", "tax"]  
    system_terms: ["συνπžήρηση", "διακοπή", "maintenance", "outage"]
    
  date_recognition:
    greek_formats: ["dd/MM/yyyy", "dd-MM-yyyy", "dd Μμμ yyyy"]
    month_names: ["Ιανουάριοπš", "Φεβρουάριοπš", ..., "Δεκέμβριοπš"]
    business_day_calculation: "Exclude Greek holidays and weekends"
```

## Professional Alert System

### Alert Generation & Classification
```yaml
Alert_System:
  critical_alerts:
    deadline_changes:
      trigger: "Any tax deadline moved forward"
      delivery: "Immediate notification to assigned accountant"
      template: "ΡΡΙΣΙΜθ: Προθεσμία {tax_type} μεπžακινήθηκε σπžιπš {new_date}"
      
    system_outages:
      trigger: "TAXIS or myDATA unavailable >30 minutes"
      delivery: "Immediate notification to accounting teams"
      template: "ΔΙΑΡθΠΗ: Σύσπžημα {system_name} μη διαθέσιμο απς {outage_start}"
      
  important_alerts:
    rate_changes:
      trigger: "VAT or tax rate modifications"
      delivery: "Email + dashboard update"
      template: "Αλλαγή συνπžελεσπžή: {rate_type} απς {old_rate} σε {new_rate}"
      
    new_regulations:
      trigger: "New tax circulars or law changes"
      delivery: "Daily digest email"
      template: "Νέα εγκύκλιοπš: {circular_number} - {summary}"
      
  routine_alerts:
    system_maintenance:
      trigger: "Scheduled maintenance announcements" 
      delivery: "Weekly summary"
      template: "Προγραμμαπžισμένη συνπžήρηση: {system} πžην {date} {time}"
```

### Greek Professional Communication
```yaml
Professional_Templates:
  client_deadline_alert:
    subject: "Σημανπžική ενημέρπ°ση: Αλλαγή προθεσμίαπš {tax_type}"
    body: |
      Αξιςπžιμοι πελάπžεπš,
      
      Σαπš ενημερϽνουμε ςπžι η ΑΑΔΕ ανακοίνπ°σε αλλαγή σπžην προθεσμία 
      υποβολήπš {tax_description}.
      
      Νέα προθεσμία: {new_deadline}
      Προηγούμενη προθεσμία: {old_deadline}
      
      Παρακαλούμε επικοινπ°νήσπžε μαζί μαπš για οποιαδήποπžε διευκρίνιση.
      
      Με εκπžίμηση,
      {accounting_firm_name}
      
  rate_change_notification:
    subject: "Ενημέρπ°ση: Αλλαγή π ορολογικού συνπžελεσπžή"
    body: |
      Αγαπηπžοί συνεργάπžεπš,
      
      Απς {effective_date} ισπ¡ύει νέοπš συνπžελεσπžήπš {tax_type}:
      - Νέοπš συνπžελεσπžήπš: {new_rate}%
      - Προηγούμενοπš: {old_rate}%
      
      Η αλλαγή επηρεάζει: {affected_transactions}
      
      Το λογισπžικς μαπš γραπ είο θα ενημερϽσει ςλουπš πžουπš υπολογισμούπš.
      
      {firm_contact_info}
```

## Integration Workflows

### Meta-Skill Integration
```bash
# Integration with OpenClaw Greek Accounting Meta-Skill
openclaw aade register-with-meta --enable-orchestration
openclaw aade meta-commands --list-available --business-focused

# Meta-skill can now call:
# openclaw greek government-check  (calls aade-api-monitor internally)
# openclaw greek emergency-compliance  (uses aade alerts)
# openclaw greek status-dashboard  (includes aade system status)
```

### Other Skill Integration 
```yaml
Skill_Integration_Points:
  cli_deadline_monitor:
    data_exchange: "Share deadline change data"
    coordination: "Avoid duplicate monitoring"
    backup_relationship: "CLI monitor provides fallback data"
    
  greek_email_processor:
    alert_delivery: "Use email processor for client notifications"
    template_sharing: "Share Greek language templates"
    document_processing: "Process AADE emails received by clients"
    
  greek_compliance_aade:
    rate_updates: "Notify compliance skill of rate changes"
    calculation_updates: "Trigger recalculation when rates change"
    submission_timing: "Coordinate deadline changes with submissions"
```

## Production Monitoring & Maintenance

### Automated Health Monitoring
```bash
# Health check commands for production deployment
openclaw aade health-check --comprehensive --test-all-endpoints
openclaw aade performance-monitor --response-times --error-rates --uptime
openclaw aade data-validation --accuracy-check --cross-reference --anomaly-detection

# Maintenance and optimization
openclaw aade cache-optimize --cleanup-old --defragment --performance-tune
openclaw aade update-patterns --learn-new-formats --improve-accuracy
openclaw aade backup-data --critical-cache --configuration --logs
```

### Logging & Audit Trail
```yaml
Production_Logging:
  access_logs:
    file: "/logs/aade-monitor/access.log"
    retention: "6 months"
    includes: ["URLs accessed", "Response codes", "Response times"]
    
  change_detection_logs:
    file: "/logs/aade-monitor/changes.log" 
    retention: "2 years"
    includes: ["Detected changes", "Confidence scores", "Validation results"]
    
  alert_logs:
    file: "/logs/aade-monitor/alerts.log"
    retention: "1 year"
    includes: ["Alert generation", "Delivery methods", "User responses"]
    
  error_logs:
    file: "/logs/aade-monitor/errors.log"
    retention: "1 year"
    includes: ["Processing errors", "Network failures", "Recovery actions"]
```

## Advanced Features

### Machine Learning Enhancement
```yaml
ML_Capabilities:
  document_classification:
    training_data: "Historical AADE announcements with manual classifications"
    accuracy_target: ">95% for critical document identification"
    continuous_learning: "Update model based on manual corrections"
    
  change_impact_prediction:
    analysis: "Predict client impact based on historical patterns"
    risk_assessment: "Identify high-risk clients for proactive communication"
    resource_planning: "Estimate workload from detected changes"
    
  anomaly_detection:
    baseline_patterns: "Learn normal AADE announcement patterns"
    unusual_activity: "Flag potential system issues or major changes"
    false_positive_reduction: "Reduce unnecessary alerts through pattern learning"
```

### Compliance Dashboard Integration
```yaml
Dashboard_Features:
  real_time_status:
    aade_systems: "Live status of TAXIS, myDATA, EFKA systems"
    recent_changes: "Timeline of recent deadline and rate changes"
    alert_summary: "Critical, important, and routine alerts overview"
    
  client_impact_view:
    affected_clients: "Which clients affected by recent changes"
    action_required: "Immediate actions needed per client"
    communication_status: "Which clients have been notified"
    
  performance_metrics:
    monitoring_uptime: "AADE monitor system availability"
    detection_accuracy: "Change detection success rate"
    alert_effectiveness: "User response to generated alerts"
```

## Usage Examples

### Daily Operations
```bash
# Morning AADE check (part of daily routine)
$ openclaw aade morning-check --since yesterday

📊 AADE Morning Summary - February 18, 2026:

ðŸÂ€ºï¸ System Status:
✅ TAXIS Online (98.2% uptime last 24h)
✅ myDATA Online (99.1% uptime last 24h)  
✅ EFKA Portal Online (97.5% uptime last 24h)

📢 New Announcements (2):
📀¹ Circular POL.1157/2026 - VAT exemption clarification
⚠ï¸ System maintenance scheduled: February 20, 02:00-06:00 EET

🔀ž Changes Detected: None
📅 Upcoming Deadlines: 3 VAT returns due in 7 days

Next check in 2 hours. Manual refresh: openclaw aade check-updates
```

### Change Detection Example
```bash
$ openclaw aade detect-changes --urgent --notify-immediately

🚨 CRITICAL CHANGE DETECTED:

📅 Deadline Change Alert:
Tax Type: Monthly VAT Return (March 2026)
Old Deadline: April 25, 2026
New Deadline: April 20, 2026
Change: 5 days earlier
Impact: 47 clients affected

📀¹ Source Document:
AADE Announcement: Πθ΀º.1158/2026
Published: 2026-02-18 14:30 EET
Confidence: 98.5%

✅ Actions Taken:
- Updated compliance deadline tracker
- Generated client notifications (47 emails prepared)
- Integrated with meta-skill workflow
- Logged change in audit trail

📧 Client notifications ready for review:
openclaw aade review-notifications --batch-id 2026021801
```

### Professional Client Communication
```bash
$ openclaw aade generate-client-alert --deadline-change --professional-tone

📧 Generated Greek Client Communication:

Subject: ΕΠΕΙΓθΝ: Αλλαγή προθεσμίαπš δήλπ°σηπš ΦΠΑ Μαρπžίου 2026

Αξιςπžιμοι πελάπžεπš,

Σαπš ενημερϽνουμε με απ ορμή πžην ανακοίνπ°ση πžηπš ΑΑΔΕ (Πθ΀º.1158/2026) 
ςπžι η προθεσμία υποβολήπš πžηπš μηνιαίαπš δήλπ°σηπš ΦΠΑ για πžον Μάρπžιο 2026 
μεπžακινείπžαι απς πžιπš 25 Απριλίου σπžιπš 20 Απριλίου 2026.

Η αλλαγή επηρεάζει ςλεπš πžιπš επιπ¡ειρήσειπš με υποπ¡ρέπ°ση υποβολήπš 
μηνιαίαπš δήλπ°σηπš ΦΠΑ.

Το λογισπžικς μαπš γραπ είο έπ¡ει ήδη ενημερϽσει πžο σύσπžημα παρακολούθησηπš 
προθεσμιϽν και θα π ρονπžίσουμε για πžην έγκαιρη προεπžοιμασία και υποβολή.

Για οποιαδήποπžε διευκρίνιση, παρακαλούμε επικοινπ°νήσπžε μαζί μαπš.

Με εκπžίμηση,
[Accounting Firm Name]
📧 Ready for sending to 47 affected clients
```

## Success Metrics

A successful AADE API Monitor should achieve:
- ✅ 99%+ uptime monitoring of critical AADE systems
- ✅ <5 minute detection time for critical deadline changes
- ✅ 95%+ accuracy in document classification and change detection
- ✅ Zero false positives for critical alerts
- ✅ Complete integration with meta-skill orchestration
- ✅ Professional Greek communication standards
- ✅ Comprehensive audit trail for compliance purposes
- ✅ Robust offline operation with cached data fallback

Remember: This skill is built OpenClaw-first, using file processing and practical automation rather than complex API integrations, making it reliable and maintainable for production Greek accounting environments.