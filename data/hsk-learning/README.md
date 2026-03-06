# HSK Learning Skill for OpenClaw

A comprehensive HSK Chinese learning system with spaced repetition mastery tracking, vocabulary analysis, and adaptive quiz generation.

## Features

- **Spaced Repetition Mastery System**: Tracks mastery state (unknown/learning/mastered) for all 2,211 HSK 3.0 words
- **Vocabulary Exposure Analysis**: Scans conversation logs, categorizes CJK tokens by HSK level
- **Quiz Log Parsing**: Automatically extracts vocabulary and correctness from quiz-performance logs
- **Adaptive Quiz Generation**: Creates quizzes prioritizing words due for review
- **Progress Tracking**: Detailed statistics and progress reports

## Quick Start

### Installation
```bash
clawhub install hsk-learning
```

### Initialization (First-Time Setup)
```bash
cd skills/hsk-learning
node scripts/init-mastery-db.js
```

### Restart OpenClaw
```bash
openclaw gateway restart
```

## Usage Examples

### Check Mastery Stats
```javascript
hsk_get_mastery_stats({ format: 'text' });
```

### Update Mastery from Quiz Logs
```javascript
hsk_update_mastery_from_quiz({ date: 'all' });
```

### Get Words Due for Review
```javascript
hsk_get_due_words({ limit: 10, level: 1 });
```

### Generate Adaptive Quiz
```javascript
hsk_generate_quiz({ difficulty: 'mixed', format: 'simple' });
```

## Data Management

### User-Specific Files (Git Ignored)
- `data/hsk-mastery-db.json` - Your personal mastery tracking
- `data/user-config.json` - Your preferences (optional)

### Shared Files (Included in Repository)
- `data/hsk-database.json` - HSK word database
- `data/hsk-word-to-level.json` - Word-to-level mapping
- `data/user-config.template.json` - Configuration template

## Integration with OpenClaw

### Cron Jobs for Automation
Set up cron jobs for:
- Daily vocabulary scanning
- Weekly progress reports
- Daily quiz reminders

### Memory Integration
The skill automatically scans `memory/*.md` files for CJK tokens and updates vocabulary exposure reports.

## Development

### Project Structure
```
hsk-learning/
├── index.js              # Main skill entry point
├── lib/                  # Core libraries
│   ├── mastery.js       # Spaced repetition logic
│   ├── parser.js        # Quiz log parsing
│   └── vocab-tracker.js # Vocabulary analysis
├── data/                 # Data files
├── scripts/             # Utility scripts
│   └── init-mastery-db.js # First-time setup
└── README.md            # This file
```

### Testing
```bash
# Test mastery initialization
node scripts/init-mastery-db.js

# Test skill functions
node -e "const skill = require('./index.js'); skill.hsk_get_mastery_stats({ format: 'text' }).then(console.log);"
```

## Publishing

### Prepare for Publication
1. Ensure `.gitignore` excludes user-specific files
2. Update version in `manifest.json`
3. Test initialization script works for new users
4. Update documentation

### Publish to ClawHub
```bash
clawhub publish ./hsk-learning --slug hsk-learning --name "HSK Learning" --version 1.1.0 --changelog "User-agnostic improvements"
```

## License

MIT

## Acknowledgments

- HSK 3.0 word lists from [mandarinbean.com](https://mandarinbean.com)
- Spaced repetition algorithm inspired by SM-2 (SuperMemo)
- Built for [OpenClaw](https://openclaw.ai) community