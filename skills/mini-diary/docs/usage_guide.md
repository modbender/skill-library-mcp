# Mini Diary Usage Guide

## 📖 Table of Contents
1. [Quick Start](#quick-start)
2. [Basic Commands](#basic-commands)
3. [Auto-Tagging System](#auto-tagging-system)
4. [Search Features](#search-features)
5. [NextCloud Integration](#nextcloud-integration)
6. [Customization](#customization)
7. [Troubleshooting](#troubleshooting)
8. [Advanced Tips](#advanced-tips)

## 🚀 Quick Start

### Installation
```bash
# Install via ClawHub (recommended)
clawhub install mini-diary

# Or manual installation
git clone https://github.com/PrintXDreams/mini-diary.git
cd mini-diary
./scripts/install.sh
```

### Your First Note
```bash
# Add a note (auto-tagging happens automatically)
mini-diary add "Completed project documentation"

# View your diary
cat ~/diary.md

# Search your notes
mini-diary search --stats
```

## 📝 Basic Commands

### Add Notes
```bash
# Simple note
mini-diary add "Team meeting at 2 PM"

# Note with multiple aspects
mini-diary add "Ordered Bambu PLA and submitted invoice"

# Note will be auto-tagged:
# "Team meeting" → 📅
# "Ordered Bambu PLA" → 📦🎋
# "submitted invoice" → 💰
```

### Manage Todos
```bash
# Add pending todo (direct file editing)
echo "- [ ] Call supplier about PLA stock" >> ~/diary.md

# Add completed todo
echo "- [x] Submit monthly report" >> ~/diary.md

# Add multiple todos
cat >> ~/diary.md << 'EOF'
- [ ] Schedule client training
- [x] Update software licenses
- [ ] Order office supplies
EOF

# Search todos
grep "\[ \]" ~/diary.md      # Pending todos
grep "\[x\]" ~/diary.md      # Completed todos

# Todo statistics
pending=$(grep -c "\[ \]" ~/diary.md)
completed=$(grep -c "\[x\]" ~/diary.md)
total=$((pending + completed))
completion_rate=$((completed * 100 / total))
echo "Completion: $completion_rate% ($completed/$total)"
```

### Search Diary
```bash
# Search by tag
mini-diary search --tag "📦"      # Orders
mini-diary search --tag "💰"      # Finance
mini-diary search --tag "🎋"      # Bambu/3D printing

# Search by date
mini-diary search --date "2024-02-22"

# Search in content
mini-diary search "client meeting"
mini-diary search "invoice"

# View statistics
mini-diary search --stats

# List all tags
mini-diary search --list-tags
```

## 🏷️ Auto-Tagging System

### How It Works
Mini Diary analyzes your note content and automatically adds relevant tags:

| Content Example | Auto-Tags | Reason |
|----------------|-----------|--------|
| "Family dinner tonight" | 🏠 | Contains "family" |
| "Paid vendor invoice" | 💰 | Contains "invoice" |
| "Ordered printer parts" | 📦🎋 | "Ordered" + "printer" |
| "Shipped to customer" | 🚚 | Contains "shipped" |
| "Fixed software bug" | 💻 | Contains "software" |
| "Repair client machine" | 🔧🎋 | "Repair" + "machine" |
| "Filled out form" | 📋 | Contains "form" |
| "Daily standup meeting" | 📅 | Default for routine |

### Tag Reference
- 🏠 Family: home, family, household, personal
- 💰 Finance: invoice, payment, accounting, money
- 📦 Order: order, purchase, buy, stock, inventory
- 🚚 Shipping: shipping, delivery, logistics, transport
- 💻 Tech: software, system, computer, network, tech
- 🔧 Support: repair, fix, issue, problem, maintenance
- 🎋 Bambu: bambu, 3d print, printer, filament, pla
- 📋 Form: form, report, data, spreadsheet, document
- 📅 Daily: meeting, work, routine, task, project (default)

## 🔍 Search Features

### Basic Search
```bash
# Find all notes with a specific tag
mini-diary search --tag "💻"

# Output shows:
# - Date context
# - Full note content
# - Tag count statistics
```

### Date Range Search
```bash
# Using grep with date patterns
grep -A5 "## 📅 2024-02" ~/diary.md

# Or combine with tag search
mini-diary search --tag "📦" | grep "2024-02-22"
```

### Content Search
```bash
# Case-insensitive search
mini-diary search "Bambu"
mini-diary search "invoice"
mini-diary search "meeting"
```

## ☁️ NextCloud Integration

### Setup
1. **Set environment variable**:
```bash
export NEXTCLOUD_SYNC_DIR="/path/to/your/nextcloud/diary"
```

2. **Mini Diary will automatically**:
   - Copy diary file to NextCloud directory
   - Maintain sync between locations

### ⚠️ Critical Notes

#### File Permissions
NextCloud requires specific ownership:
```bash
# Check current ownership
ls -la /path/to/nextcloud/diary/diary.md

# Fix ownership (if needed)
sudo chown www-data:www-data /path/to/nextcloud/diary/diary.md

# Docker version
docker exec nextcloud_app chown www-data:www-data /var/www/html/data/.../diary.md
```

#### Scan Command Required
NextCloud **does not** auto-detect file system changes:
```bash
# You MUST run this after file changes:
docker exec nextcloud_app php occ files:scan [your_username]

# Example output:
# +---------+-------+-----+---------+---------+--------+--------------+
# | Folders | Files | New | Updated | Removed | Errors | Elapsed time |
# +---------+-------+-----+---------+---------+--------+--------------+
# | 17      | 45    | 0   | 1       | 0       | 0      | 00:00:00     |
# +---------+-------+-----+---------+---------+--------+--------------+
```

### Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| Files not showing in NextCloud | Run the scan command |
| Permission denied errors | Check file ownership (www-data) |
| Sync conflicts | Only edit via Mini Diary, not directly in NextCloud |
| Duplicate files | Check both locations match |

## ⚙️ Customization

### Environment Variables
```bash
# Diary file location
export DIARY_FILE="$HOME/my-journal.md"

# NextCloud sync
export NEXTCLOUD_SYNC_DIR="/opt/nextcloud/data/diary"

# Debug mode
export MINI_DIARY_DEBUG=1

# Custom tags configuration
export TAGS_CONFIG="$HOME/.mini-diary-tags.json"
```

### Custom Tags
Create `~/.mini-diary-tags.json`:
```json
{
  "custom_tags": {
    "project-alpha": "🚀",
    "urgent": "⚠️",
    "idea": "💡",
    "health": "❤️"
  },
  "rules": {
    "project-alpha": ["project alpha", "pa", "alpha"],
    "urgent": ["urgent", "asap", "important"],
    "idea": ["idea", "thought", "concept"],
    "health": ["health", "exercise", "doctor"]
  }
}
```

### Diary Template
Customize `templates/diary_template.md`:
- Change header style
- Add custom sections
- Modify default structure
- Add personal notes

## 🔧 Troubleshooting

### General Issues

**Problem**: `mini-diary` command not found
**Solution**: Ensure installation completed and scripts are executable

**Problem**: Tags not appearing
**Solution**: Check note content matches tag rules, enable debug mode

**Problem**: Search returns no results
**Solution**: Verify diary file exists and has content

### NextCloud Issues

**Problem**: NextCloud shows "file not found"
**Solution**: 
1. Check `NEXTCLOUD_SYNC_DIR` is set correctly
2. Verify file exists in that directory
3. Run scan command: `docker exec nextcloud_app php occ files:scan [user]`

**Problem**: Permission errors in NextCloud
**Solution**:
```bash
# Fix ownership
sudo chown -R www-data:www-data /path/to/nextcloud/diary/

# Or for Docker
docker exec nextcloud_app chown -R www-data:www-data /var/www/html/data/.../
```

### Debug Mode
Enable debug output:
```bash
export MINI_DIARY_DEBUG=1
mini-diary add "test note"
# Shows detailed processing information
```

## 🎯 Advanced Tips

### Weekly Reports
```bash
# Generate weekly summary
mini-diary search --date $(date -d "last week" +%Y-%m-%d) --stats

# Export to CSV for analysis
grep "^- " ~/diary.md | sed 's/^- //' > notes.csv
```

### Integration with Other Tools
```bash
# Add note from another script
echo "Automated backup completed" | xargs mini-diary add

# Schedule daily notes with cron
0 17 * * * mini-diary add "End of day summary"
```

### Backup Strategy
```bash
# Backup diary file
cp ~/diary.md ~/backups/diary-$(date +%Y%m%d).md

# Sync to multiple locations
rsync -av ~/diary.md /mnt/backup/
rsync -av ~/diary.md user@server:~/backups/
```

### Performance Tips
- Keep diary file under 10,000 lines for best performance
- Use specific searches rather than scanning entire file
- Regular backups prevent data loss
- Consider splitting by year if diary grows large

## 📚 Additional Resources

- [GitHub Repository](https://github.com/PrintXDreams/mini-diary)
- [Issue Tracker](https://github.com/PrintXDreams/mini-diary/issues)
- [OpenClaw Documentation](https://docs.openclaw.ai)
- [NextCloud Administration](https://docs.nextcloud.com)

## 🤝 Getting Help

1. **Check this guide** first
2. **Search existing issues** on GitHub
3. **Create new issue** with details:
   - Error messages
   - Steps to reproduce
   - Your environment details
   - What you expected vs what happened

---

*Happy journaling with Mini Diary!* 📓✨