#!/usr/bin/env python3
"""
Generate Feishu documents from Bitable data.

This script queries a Bitable and generates formatted documents
from the results. Useful for reports, summaries, or data exports.

Usage:
  python bitable_to_doc.py --app-token basXXX --table-id tblYYY --template report_template.md
  python bitable_to_doc.py --app-token basXXX --table-id tblYYY --query "Status=Active" --output-folder fldcnZZZ
"""

import argparse
import json
import sys
from datetime import datetime

def query_bitable(app_token, table_id, filter_formula=None, fields=None):
    """
    Query records from a Bitable.
    Returns sample data for demonstration.
    """
    print(f"[INFO] Querying Bitable {table_id} in app {app_token}")
    
    if filter_formula:
        print(f"  Filter: {filter_formula}")
    
    if fields:
        print(f"  Fields: {fields}")
    
    # Sample data for demonstration
    sample_records = [
        {
            "record_id": "rec001",
            "fields": {
                "Name": "Project Alpha",
                "Status": "Active",
                "Progress": 75,
                "Due Date": "2026-02-28",
                "Owner": "Alice"
            }
        },
        {
            "record_id": "rec002",
            "fields": {
                "Name": "Project Beta",
                "Status": "On Hold",
                "Progress": 30,
                "Due Date": "2026-03-15",
                "Owner": "Bob"
            }
        },
        {
            "record_id": "rec003",
            "fields": {
                "Name": "Project Gamma",
                "Status": "Completed",
                "Progress": 100,
                "Due Date": "2026-01-31",
                "Owner": "Charlie"
            }
        }
    ]
    
    # Apply simple filtering for demonstration
    if filter_formula:
        filtered = []
        for record in sample_records:
            # Simple keyword matching for demo
            if "Active" in filter_formula and record["fields"]["Status"] == "Active":
                filtered.append(record)
            elif "Completed" in filter_formula and record["fields"]["Status"] == "Completed":
                filtered.append(record)
            elif "On Hold" in filter_formula and record["fields"]["Status"] == "On Hold":
                filtered.append(record)
            else:
                # If no specific match, include all for demo
                filtered.append(record)
        return filtered[:2]  # Limit for demo
    
    return sample_records

def generate_markdown_table(records, fields=None):
    """
    Generate markdown table from records.
    """
    if not records:
        return "No records found."
    
    # Determine fields to include
    if not fields:
        # Use fields from first record
        first_record = records[0]
        fields = list(first_record["fields"].keys())
    
    # Create header
    header = "| " + " | ".join(fields) + " |"
    separator = "| " + " | ".join(["---"] * len(fields)) + " |"
    
    # Create rows
    rows = []
    for record in records:
        row_cells = []
        for field in fields:
            value = record["fields"].get(field, "")
            row_cells.append(str(value))
        rows.append("| " + " | ".join(row_cells) + " |")
    
    return "\n".join([header, separator] + rows)

def generate_document_content(records, template=None):
    """
    Generate document content from records and template.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    if template:
        # Load template from file
        try:
            with open(template, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"[WARNING] Could not load template {template}: {e}")
            content = "# Bitable Report\n\nGenerated on {{timestamp}}\n\n"
    else:
        content = "# Bitable Report\n\nGenerated on {{timestamp}}\n\n"
    
    # Replace template variables
    content = content.replace("{{timestamp}}", timestamp)
    content = content.replace("{{record_count}}", str(len(records)))
    
    # Add summary section if placeholder exists
    if "{{summary}}" in content:
        summary = f"## Summary\n\nTotal records: {len(records)}\n"
        
        # Count by status
        status_count = {}
        for record in records:
            status = record["fields"].get("Status", "Unknown")
            status_count[status] = status_count.get(status, 0) + 1
        
        if status_count:
            summary += "\n**By Status:**\n"
            for status, count in status_count.items():
                summary += f"- {status}: {count}\n"
        
        content = content.replace("{{summary}}", summary)
    
    # Add data table if placeholder exists
    if "{{data_table}}" in content:
        table = generate_markdown_table(records)
        content = content.replace("{{data_table}}", table)
    else:
        # Add table at the end if no placeholder
        content += "\n## Data\n\n"
        content += generate_markdown_table(records)
    
    return content

def create_feishu_document(content, title=None, folder_token=None):
    """
    Create a new Feishu document.
    """
    if not title:
        title = f"Bitable Report {datetime.now().strftime('%Y-%m-%d')}"
    
    print(f"[INFO] Creating document: {title}")
    print(f"  Content length: {len(content)} characters")
    
    if folder_token:
        print(f"  Target folder: {folder_token}")
    
    # In real implementation:
    # exec_result = exec('tool call', {
    #     'tool': 'feishu_doc',
    #     'action': 'create',
    #     'title': title,
    #     'content': content,
    #     'folder_token': folder_token
    # })
    
    return "doc_demo_token_123"

def main():
    parser = argparse.ArgumentParser(description="Generate documents from Bitable data")
    
    # Bitable connection
    parser.add_argument("--app-token", required=True, help="Bitable app token")
    parser.add_argument("--table-id", required=True, help="Bitable table ID")
    
    # Query options
    parser.add_argument("--query", help="Filter formula (e.g., 'Status=Active')")
    parser.add_argument("--fields", help="Comma-separated list of fields to include")
    
    # Output options
    parser.add_argument("--template", help="Path to markdown template file")
    parser.add_argument("--output-folder", help="Feishu folder token for new document")
    parser.add_argument("--title", help="Document title (default: auto-generated)")
    parser.add_argument("--output-file", help="Save to local file instead of creating document")
    parser.add_argument("--dry-run", action="store_true", help="Preview without creating document")
    
    args = parser.parse_args()
    
    # Parse fields
    field_list = args.fields.split(',') if args.fields else None
    
    # Query Bitable
    print(f"[INFO] Connecting to Bitable...")
    records = query_bitable(args.app_token, args.table_id, args.query, field_list)
    
    if not records:
        print("[WARNING] No records found matching query")
        sys.exit(0)
    
    print(f"[INFO] Retrieved {len(records)} records")
    
    # Generate document content
    content = generate_document_content(records, args.template)
    
    if args.dry_run:
        print("\n" + "="*60)
        print("DRY RUN - Document Preview")
        print("="*60)
        print(content[:2000])  # Preview first 2000 chars
        if len(content) > 2000:
            print(f"\n... (truncated, total {len(content)} characters)")
        print("="*60)
        return
    
    # Create output
    if args.output_file:
        # Save to local file
        with open(args.output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"[SUCCESS] Saved to {args.output_file}")
    
    else:
        # Create Feishu document
        doc_token = create_feishu_document(
            content, 
            args.title, 
            args.output_folder
        )
        print(f"[SUCCESS] Document created: {doc_token}")
        
        # Show document URL pattern
        print(f"[INFO] Document URL: https://your-domain.feishu.cn/docx/{doc_token}")

if __name__ == "__main__":
    main()