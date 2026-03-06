---
name: feishu-automation
description: |
  Advanced automation workflows for Feishu (Lark) productivity suite. Use when you need to automate document workflows, sync data across Feishu apps, generate reports, or perform batch operations across documents, wikis, bitables, and cloud storage. Triggers: "批量处理飞书文档", "自动同步飞书表格数据", "备份知识库", "生成飞书报告", "自动化飞书任务", "飞书数据迁移".
---

# Feishu Automation

## Overview

This skill enables advanced automation across the Feishu/Lark productivity suite. It provides recipes, scripts, and workflows for common automation scenarios like batch document processing, data synchronization, report generation, and knowledge management.

## Quick Start

### Prerequisites
- OpenClaw with Feishu integration configured
- Feishu app permissions enabled for: `docx`, `wiki`, `bitable`, `drive`
- Target documents/tables already exist and are accessible

### Basic Example: Batch Update Documents
```bash
# Use the batch_update.py script to update multiple documents
python scripts/batch_update.py --folder-token fldcnXXX --template "weekly_report.md"
```

## Core Automation Tasks

### 1. Document Automation
- **Batch Creation**: Create multiple documents from templates
- **Content Sync**: Sync data from Bitable to documents
- **Format Conversion**: Convert between markdown and Feishu doc format
- **Backup & Archive**: Periodically backup important documents

### 2. Wiki & Knowledge Management
- **Wiki Migration**: Move content between wiki spaces
- **Auto-tagging**: Tag wiki pages based on content analysis
- **TOC Generation**: Generate table of contents for large wikis
- **Link Checking**: Find and fix broken links in wiki

### 3. Bitable Automation
- **Data Import/Export**: Sync Bitable with external data sources
- **Report Generation**: Create documents from Bitable queries
- **Validation Rules**: Enforce data quality in Bitable
- **Notification System**: Alert on Bitable changes

### 4. Cross-App Workflows
- **Document → Bitable**: Extract structured data from documents to tables
- **Bitable → Document**: Generate reports from table data
- **Wiki → Drive**: Archive wiki pages to cloud storage
- **Drive → Wiki**: Import documents as wiki pages

## Workflow Templates

### Weekly Report Automation
1. Query Bitable for weekly metrics
2. Generate markdown report with charts
3. Create/update Feishu document
4. Post to designated wiki space
5. Notify team via Feishu chat

See `references/weekly_report_workflow.md` for detailed implementation.

### Document Migration
1. List source folder documents
2. Convert each to markdown
3. Create new documents in target folder/wiki
4. Update all internal links
5. Verify completion

See `scripts/migrate_documents.py` for ready-to-use script.

## Tool Reference

This skill builds on OpenClaw's native Feishu tools:

- `feishu_doc` - Document read/write operations
- `feishu_wiki` - Knowledge base navigation  
- `feishu_bitable_*` - Bitable operations
- `feishu_drive` - Cloud storage management

Always use the native tools directly when possible; use scripts only for complex workflows.

## Included Resources

This skill comes with ready-to-use resources for common automation tasks.

### scripts/
- `batch_update.py` - Update multiple documents from template
- `migrate_documents.py` - Migrate documents between folders/spaces
- `bitable_to_doc.py` - Generate documents from Bitable data
- `wiki_backup.py` - Backup wiki pages to markdown files

### references/
- `weekly_report_workflow.md` - Step-by-step weekly report automation
- `feishu_api_patterns.md` - Common API usage patterns and examples
- `error_handling.md` - Handling common Feishu API errors
- `best_practices.md` - Performance and reliability tips

### assets/
- `templates/weekly_report.md` - Weekly report template
- `templates/meeting_notes.md` - Meeting notes template
- `templates/project_status.md` - Project status update template
- `config/sample_config.yaml` - Configuration examples

## Getting Help

For questions or issues:
1. Check the relevant reference file first
2. Review error messages in `error_handling.md`
3. Adapt scripts to your specific use case
4. Consult OpenClaw Feishu documentation for tool specifics
