# Apple Notes Integration with Workflows

## Overview

This document outlines how to integrate the Apple Notes extraction system with your existing workflows and tools.

## Integration Patterns

### 1. File-Based Integration

The simplest integration is through file outputs:

```bash
# Extract to JSON for programmatic processing
python3 scripts/extract-notes.py --method auto
python3 scripts/workflow-integrator.py --workflow search

# Use the resulting files in your scripts
cat output/json/notes_*.json | jq '.[] | select(.folder == "Work")'
```

### 2. Obsidian Vault Integration

```bash
# Configure Obsidian integration
cat > configs/workflows.json << 'EOF'
{
  "workflows": {
    "obsidian": {
      "enabled": true,
      "vault_path": "/Users/yourusername/Documents/ObsidianVault",
      "subfolder": "Imported/Apple Notes",
      "include_metadata": true
    }
  }
}
EOF

# Run the integration
python3 scripts/workflow-integrator.py --workflow obsidian
```

### 3. Search Engine Integration

```python
import json
import requests

# Load extracted notes
with open('output/json/notes_auto_20240212.json') as f:
    notes = json.load(f)

# Index in Elasticsearch
for note in notes:
    doc = {
        'title': note['title'],
        'content': note['body'],
        'created': note['created'],
        'folder': note['folder']
    }
    
    requests.put(
        f"http://localhost:9200/notes/_doc/{note['id']}",
        json=doc
    )
```

### 4. AI Processing Pipeline

```python
import openai
import json

# Load notes
with open('output/json/notes_auto_latest.json') as f:
    notes = json.load(f)

# Summarize with AI
summaries = []
for note in notes:
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{
            "role": "user", 
            "content": f"Summarize this note in one sentence: {note['body'][:500]}"
        }]
    )
    
    summaries.append({
        'id': note['id'],
        'title': note['title'],
        'summary': response.choices[0].message.content
    })
```

### 5. Automated Backup Integration

```bash
#!/bin/bash
# automated-backup.sh

# Extract notes
cd /path/to/apple-notes-extractor
python3 scripts/extract-notes.py --method auto

# Commit to git for version control
cd output
git add .
git commit -m "Notes backup $(date '+%Y-%m-%d %H:%M:%S')"
git push origin main

# Upload to cloud storage
rsync -av . user@backup-server:/backups/apple-notes/
```

## Workflow Examples

### Daily Note Processing

```bash
#!/bin/bash
# daily-notes.sh - Run via cron daily at 6 AM

cd /path/to/apple-notes-extractor

# Extract latest notes
python3 scripts/extract-notes.py --method auto

# Process with workflows
python3 scripts/workflow-integrator.py

# Generate daily summary
python3 -c "
import json
from datetime import datetime, timedelta

# Load latest extraction
with open('output/index.json') as f:
    index = json.load(f)

# Count notes modified in last 24h
recent_notes = []
yesterday = datetime.now() - timedelta(days=1)

for note_id, extractions in index['notes'].items():
    latest = extractions[-1]
    if latest.get('modified'):
        # Parse date and compare
        pass  # Implementation depends on date format

print(f'Daily summary: {len(recent_notes)} notes updated')
"
```

### Content Migration

```python
# migrate-to-notion.py
import requests
import json
from datetime import datetime

NOTION_TOKEN = "your-notion-token"
DATABASE_ID = "your-database-id"

def create_notion_page(note):
    url = "https://api.notion.com/v1/pages"
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    
    data = {
        "parent": {"database_id": DATABASE_ID},
        "properties": {
            "Name": {
                "title": [{"text": {"content": note['title']}}]
            },
            "Created": {
                "date": {"start": note['created']}
            },
            "Folder": {
                "select": {"name": note['folder']}
            }
        },
        "children": [
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text", "text": {"content": note['body'][:2000]}}]
                }
            }
        ]
    }
    
    return requests.post(url, headers=headers, json=data)

# Load and migrate notes
with open('output/json/notes_auto_latest.json') as f:
    notes = json.load(f)

for note in notes:
    response = create_notion_page(note)
    print(f"Migrated: {note['title']} - Status: {response.status_code}")
```

### Real-time Monitoring

```python
# notes-watcher.py
import time
import subprocess
import json
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class NotesHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.is_directory:
            return
            
        print(f"Detected change: {event.src_path}")
        
        # Trigger extraction
        subprocess.run([
            "python3", "scripts/extract-notes.py", 
            "--method", "simple"
        ])
        
        # Send notification
        subprocess.run([
            "osascript", "-e",
            'display notification "Apple Notes updated and extracted" with title "Notes Monitor"'
        ])

# Monitor Notes app data directory (requires permissions)
observer = Observer()
observer.schedule(NotesHandler(), path="~/Library/Group Containers/group.com.apple.notes", recursive=True)
observer.start()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    observer.stop()
observer.join()
```

## API Integration

### REST API Wrapper

```python
# api-server.py
from flask import Flask, jsonify, request
import json
import subprocess
from pathlib import Path

app = Flask(__name__)

@app.route('/api/notes')
def get_notes():
    # Load latest extraction
    output_dir = Path('output/json')
    latest_file = max(output_dir.glob('notes_*.json'), key=lambda x: x.stat().st_mtime)
    
    with open(latest_file) as f:
        notes = json.load(f)
    
    # Filter by query parameters
    folder = request.args.get('folder')
    if folder:
        notes = [n for n in notes if n.get('folder') == folder]
    
    return jsonify(notes)

@app.route('/api/extract', methods=['POST'])
def trigger_extraction():
    method = request.json.get('method', 'auto')
    
    result = subprocess.run([
        'python3', 'scripts/extract-notes.py', 
        '--method', method
    ], capture_output=True, text=True)
    
    return jsonify({
        'success': result.returncode == 0,
        'message': result.stdout if result.returncode == 0 else result.stderr
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
```

### Webhook Integration

```python
# webhook-handler.py
from flask import Flask, request, jsonify
import subprocess
import hmac
import hashlib

app = Flask(__name__)
WEBHOOK_SECRET = "your-webhook-secret"

@app.route('/webhook/extract', methods=['POST'])
def handle_webhook():
    # Verify signature
    signature = request.headers.get('X-Hub-Signature-256')
    if signature:
        body = request.get_data()
        expected = hmac.new(
            WEBHOOK_SECRET.encode(),
            body,
            hashlib.sha256
        ).hexdigest()
        
        if not hmac.compare_digest(f"sha256={expected}", signature):
            return jsonify({'error': 'Invalid signature'}), 401
    
    # Trigger extraction
    subprocess.Popen([
        'python3', 'scripts/extract-notes.py',
        '--method', 'auto'
    ])
    
    return jsonify({'message': 'Extraction triggered'})
```

## Performance Optimization

### Batch Processing

```bash
# For large note collections (>1000 notes)
# Use incremental extraction

# 1. Extract metadata only first
python3 scripts/extract-notes.py --method simple --config configs/metadata-only.json

# 2. Process in batches
python3 scripts/batch-processor.py --batch-size 100
```

### Caching Strategy

```python
import hashlib
import json
from pathlib import Path

def get_note_hash(note):
    """Generate hash for change detection"""
    content = f"{note['title']}{note['modified']}{note['body']}"
    return hashlib.md5(content.encode()).hexdigest()

def incremental_extraction():
    """Only extract changed notes"""
    cache_file = Path('output/cache.json')
    
    if cache_file.exists():
        with open(cache_file) as f:
            cache = json.load(f)
    else:
        cache = {}
    
    # Get current notes
    current_notes = get_all_notes()  # Your extraction function
    
    new_or_changed = []
    for note in current_notes:
        note_hash = get_note_hash(note)
        if note['id'] not in cache or cache[note['id']] != note_hash:
            new_or_changed.append(note)
            cache[note['id']] = note_hash
    
    # Save updated cache
    with open(cache_file, 'w') as f:
        json.dump(cache, f)
    
    return new_or_changed
```

## Security Considerations

### Data Encryption

```python
from cryptography.fernet import Fernet
import json

def encrypt_sensitive_notes(notes, key=None):
    """Encrypt notes containing sensitive content"""
    if not key:
        key = Fernet.generate_key()
    
    fernet = Fernet(key)
    
    sensitive_patterns = ["password", "secret", "private"]
    
    for note in notes:
        content = note.get('body', '').lower()
        if any(pattern in content for pattern in sensitive_patterns):
            note['body'] = fernet.encrypt(note['body'].encode()).decode()
            note['encrypted'] = True
    
    return notes, key
```

### Access Control

```python
import os
from pathlib import Path

def secure_extraction():
    """Run extraction with restricted permissions"""
    # Create temporary secure directory
    secure_dir = Path('/tmp/secure_notes')
    secure_dir.mkdir(mode=0o700, exist_ok=True)
    
    # Extract to secure location
    subprocess.run([
        'python3', 'scripts/extract-notes.py',
        '--output-dir', str(secure_dir)
    ])
    
    # Process and clean up
    # ... your processing code ...
    
    # Secure cleanup
    subprocess.run(['rm', '-rf', str(secure_dir)])
```

This integration guide provides practical examples for connecting the Apple Notes extraction system with common workflows and tools. Adapt these patterns to fit your specific use cases and security requirements.