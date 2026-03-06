---
name: ahc-automator
description: Custom automation workflows for Alan Harper Composites. Automates email → ClickUp → Pipedrive chains, client onboarding, and project completion sequences. Use for AHC-specific workflows, client management automation, and composites manufacturing business processes. Trigger on "AHC workflow", "automate AHC", "client onboarding", "project completion", "email automation AHC".
compatibility: Requires ClickUp API, Pipedrive API, WhatsApp integration, and email monitoring
metadata:
  author: Andre Antunes  
  version: "1.0"
  company: Alan Harper Composites
  created: "2026-02-08"
---

# AHC-Automator: Alan Harper Composites Workflow Automation

Custom automation suite specifically designed for Alan Harper Composites manufacturing workflows, integrating ClickUp project management, Pipedrive CRM, and client communication systems.

## Overview

The AHC-Automator skill provides three core automation workflows:

1. **Email → ClickUp → Pipedrive Chain**: Automated workflow from email monitoring to task creation and deal management
2. **Client Onboarding Workflow**: Structured onboarding process with templates and automated setups
3. **Project Completion Sequence**: End-to-end project closure with reporting and invoicing triggers

---

## Quick Start

### Prerequisites
- ClickUp Team ID: `90132745943`
- Pipedrive API access configured
- WhatsApp integration for notifications
- Email monitoring active (Ian/Ronaldo)

### Run Workflows

```bash
# Email → ClickUp → Pipedrive Chain
python scripts/email_to_clickup_pipedrive.py

# Client Onboarding
python scripts/client_onboarding.py --client "Cliente Novo" --email "cliente@empresa.com"

# Project Completion
python scripts/project_completion.py --project-id 123456
```

---

## Workflow 1: Email → ClickUp → Pipedrive Chain

Monitors specific emails from Ian/Ronaldo and automatically creates tasks in ClickUp and deals in Pipedrive.

### How It Works

```
📧 Email received from Ian/Ronaldo
   ↓
🔍 Parse email content for keywords
   ↓
✅ Create ClickUp task with structured data
   ↓
💼 Create/update Pipedrive deal
   ↓
📱 Send WhatsApp notification
```

### Keywords Monitored

**ClickUp Keywords:**
- "adicionar tarefa", "atualizar ClickUp", "nova tarefa"
- "lista de convidados", "clickup"

**Pipedrive Keywords:**
- "criar deal", "add deal", "nova oportunidade"
- "pipedrive", "adicionar contato", "create lead"
- "update pipeline", "add person", "nova atividade"

### Configuration

Email monitoring is handled by existing cron jobs:
- **Ian**: `ian@alanharpercomposites.com.br` (Every 5 minutes)
- **Ronaldo**: `ronaldoaibot@gmail.com` (Every 5 minutes)

### Custom Implementation

```python
# Example usage in scripts/email_to_clickup_pipedrive.py
from ahc_automator import EmailProcessor, ClickUpClient, PipedriveClient

processor = EmailProcessor()
email_data = processor.parse_latest_emails(['ian@alanharpercomposites.com.br'])

for email in email_data:
    if processor.contains_keywords(email, 'clickup'):
        clickup = ClickUpClient()
        task_result = clickup.create_task_from_email(email)
        
    if processor.contains_keywords(email, 'pipedrive'):
        pipedrive = PipedriveClient()
        deal_result = pipedrive.create_deal_from_email(email)
```

---

## Workflow 2: Client Onboarding Workflow

Automated client onboarding process that creates structured projects, folders, and templates.

### How It Works

```
👤 New client identified
   ↓
📂 Create ClickUp project with structured folders
   ↓
📋 Generate template tasks based on client type
   ↓
📧 Send welcome email sequence
   ↓
📅 Schedule follow-up activities
```

### Project Structure Created

```
📁 [CLIENT_NAME] - Composite Manufacturing Project
├── 📂 01 - Design & Engineering
│   ├── Task: Initial requirements gathering
│   ├── Task: Technical specifications review
│   └── Task: Design approval
├── 📂 02 - Material Planning
│   ├── Task: Material cost estimation
│   ├── Task: Supplier quotes
│   └── Task: Material ordering
├── 📂 03 - Manufacturing
│   ├── Task: Production planning
│   ├── Task: Quality control setup
│   └── Task: Manufacturing execution
├── 📂 04 - Quality & Testing
│   ├── Task: Quality testing protocols
│   ├── Task: Final inspection
│   └── Task: Test results documentation
└── 📂 05 - Delivery & Closure
    ├── Task: Delivery coordination
    ├── Task: Client handover
    └── Task: Project closure documentation
```

### Templates Available

- **Standard Composite Project**: Basic composite manufacturing
- **Aerospace Grade**: High-precision aerospace components
- **Custom Engineering**: Bespoke design and manufacturing
- **Repair & Maintenance**: Component repair workflows

### Usage

```bash
# Standard onboarding
python scripts/client_onboarding.py \
    --client "Aerospace Corp" \
    --email "contact@aerospace.com" \
    --template "aerospace" \
    --value "50000" \
    --currency "EUR"

# Quick onboarding
python scripts/client_onboarding.py --quick --client "Quick Client"
```

---

## Workflow 3: Project Completion Sequence

Automated project closure workflow with reporting, invoicing, and client satisfaction tracking.

### How It Works

```
✅ Task marked complete in ClickUp
   ↓
📊 Generate project delivery report
   ↓
💰 Trigger invoice generation
   ↓
📋 Send client satisfaction survey
   ↓
📱 Update stakeholders via WhatsApp
```

### Completion Triggers

- All tasks in project marked as complete
- Manual trigger via completion script
- ClickUp automation webhook (if configured)

### Generated Reports

1. **Project Delivery Report**
   - Timeline overview
   - Quality metrics
   - Material usage
   - Cost analysis

2. **Client Handover Document**
   - Deliverable specifications
   - Maintenance guidelines
   - Warranty information
   - Contact details for support

3. **Internal Project Review**
   - Lessons learned
   - Process improvements
   - Resource utilization
   - Client feedback summary

### Invoice Integration

Connects with existing accounting system to:
- Generate final invoice
- Update payment status
- Schedule payment reminders
- Track payment completion

---

## Scripts Directory

### Core Scripts

1. **`scripts/email_to_clickup_pipedrive.py`**
   - Email monitoring and parsing
   - ClickUp task creation
   - Pipedrive deal management

2. **`scripts/client_onboarding.py`**
   - New client project setup
   - Template application
   - Welcome email automation

3. **`scripts/project_completion.py`**
   - Completion sequence trigger
   - Report generation
   - Invoice processing

4. **`scripts/whatsapp_notifier.py`**
   - WhatsApp notification sender
   - Message formatting
   - Group notifications

### Utility Scripts

1. **`scripts/ahc_utils.py`**
   - Common utilities and helpers
   - API clients and wrappers
   - Configuration management

2. **`scripts/email_parser.py`**
   - Email content analysis
   - Keyword extraction
   - Structured data parsing

3. **`scripts/report_generator.py`**
   - Project report creation
   - Template rendering
   - PDF generation

---

## Configuration Files

### `configs/ahc_config.json`

```json
{
  "clickup": {
    "team_id": "90132745943",
    "default_space": "AHC Projects",
    "templates": {
      "standard": "901322408351",
      "aerospace": "901322408352",
      "custom": "901322408353"
    }
  },
  "pipedrive": {
    "api_token": "env:PIPEDRIVE_API_TOKEN",
    "default_pipeline": "AHC Manufacturing",
    "default_stage": "New Opportunity"
  },
  "email": {
    "monitor_accounts": [
      "ian@alanharpercomposites.com.br",
      "ronaldoaibot@gmail.com"
    ],
    "keywords": {
      "clickup": ["adicionar tarefa", "nova tarefa", "clickup", "lista de convidados"],
      "pipedrive": ["criar deal", "nova oportunidade", "pipedrive", "add person"]
    }
  },
  "whatsapp": {
    "notification_groups": ["AHC Team", "Management"],
    "individual_contacts": ["Ian", "Ronaldo", "Alan"]
  }
}
```

### `configs/email_templates.json`

Client communication templates for different stages of the workflow.

---

## Integration Points

### ClickUp Integration
- Uses existing ClickUp team: `90132745943`
- Connects to Aniversário Alan project: `901322408351`
- Leverages existing task template structure

### Pipedrive Integration
- Uses direct API integration via `pipedrive_client.py`
- Creates deals, persons, and activities
- Maintains sync between ClickUp projects and Pipedrive deals

### Email Monitoring
- Leverages existing cron jobs for Ian and Ronaldo
- Extends current keyword detection
- Processes Apple Mail via osascript integration

### WhatsApp Integration
- Notification system for workflow status
- Group and individual messaging
- Customizable message templates

---

## Monitoring and Maintenance

### Workflow Logs

All workflows log to `/Users/andreantunes/.openclaw/workspace/logs/ahc-automator/`:
- `email_processing.log`: Email monitoring and parsing
- `clickup_operations.log`: ClickUp API interactions
- `pipedrive_operations.log`: Pipedrive CRM operations
- `notifications.log`: WhatsApp and email notifications

### Health Checks

```bash
# Check all workflow health
python scripts/health_check.py

# Specific workflow check
python scripts/health_check.py --workflow email_to_clickup
```

### Error Recovery

Automated error recovery for common issues:
- API rate limiting: Automatic retry with exponential backoff
- Network failures: Queue operations for retry
- Invalid data: Log errors and notify admin
- Permission issues: Alert for manual intervention

---

## Troubleshooting

### Common Issues

1. **Email not processing**
   - Check cron job status: `crontab -l`
   - Verify email account access
   - Review keyword matching in logs

2. **ClickUp task creation fails**
   - Verify Team ID and space permissions
   - Check API token validity
   - Review rate limiting in logs

3. **Pipedrive sync issues**
   - Verify API token in environment
   - Check deal/person creation permissions
   - Review API response codes in logs

4. **WhatsApp notifications not sent**
   - Check WhatsApp integration status
   - Verify contact/group IDs
   - Review notification queue

### Debug Mode

Enable debug logging:

```bash
export AHC_DEBUG=true
python scripts/email_to_clickup_pipedrive.py --debug
```

### Support

For AHC-specific automation issues:
1. Check logs in `/Users/andreantunes/.openclaw/workspace/logs/ahc-automator/`
2. Run health check script
3. Contact system administrator with log details

---

## ROI and Metrics

### Time Savings Calculation

**Email → ClickUp → Pipedrive Chain:**
- Manual process: 15 minutes per email
- Automated process: 30 seconds
- Average: 20 emails per week
- **Weekly savings: 4.8 hours**

**Client Onboarding:**
- Manual setup: 2 hours per client
- Automated setup: 10 minutes
- Average: 2 new clients per month
- **Monthly savings: 3.7 hours**

**Project Completion:**
- Manual closure: 1.5 hours per project
- Automated closure: 15 minutes
- Average: 4 projects per month
- **Monthly savings: 5 hours**

### Total Monthly ROI
- **Time saved: 24+ hours per month**
- **Value: $1,200+ per month (at $50/hour)**
- **Setup cost: 8 hours initial setup**
- **Payback period: 2 weeks**

---

## Future Enhancements

### Planned Features

1. **AI-Powered Email Classification**
   - Smart categorization of client emails
   - Automatic priority assignment
   - Intelligent task description generation

2. **Advanced Reporting Dashboard**
   - Real-time workflow metrics
   - Client satisfaction tracking
   - Resource utilization analysis

3. **Mobile Notifications**
   - Push notifications for critical tasks
   - Mobile approval workflows
   - Emergency escalation paths

4. **Integration Expansions**
   - Accounting software integration
   - Inventory management sync
   - Quality control system integration

### Technical Improvements

1. **Enhanced Error Handling**
   - Intelligent retry mechanisms
   - Automatic failover systems
   - Predictive maintenance alerts

2. **Performance Optimization**
   - Batch processing capabilities
   - Caching layers for API calls
   - Asynchronous processing

3. **Security Enhancements**
   - OAuth 2.0 implementation
   - Encrypted configuration storage
   - Audit trail logging

---

This skill provides the foundation for scalable automation at Alan Harper Composites, reducing manual work while improving consistency and client satisfaction.