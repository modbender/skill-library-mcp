# Curriculum Generator Skill

An intelligent educational curriculum generation system for OpenClaw that creates customized curricula for educational PODs (Points of Delivery).

## Features

- ✅ Guided requirement gathering through structured questionnaires
- ✅ Research-based curriculum design and assessment
- ✅ Automatic resource link population via web search
- ✅ Excel/CSV output generation
- ✅ Local memory storage for continuous improvement
- ✅ Strict step enforcement with human escalation policies
- ✅ Background task execution support

## What It Does

This skill helps generate complete educational curricula by:

1. **Gathering Requirements**: Collects detailed information about:
   - Target audience (age, grade, background)
   - POD infrastructure (computers, internet, lab hours)
   - Teacher capability and availability
   - Learning objectives and constraints

2. **Designing Curriculum**: Creates structured courses with:
   - Weekly lesson breakdowns
   - Learning objectives per lesson
   - Module and sub-topic organization
   - Assessment strategies

3. **Finding Resources**: Automatically searches and populates free educational resources from:
   - YouTube tutorials
   - FreeCodeCamp courses
   - W3Schools documentation
   - Khan Academy content
   - Other quality educational platforms

4. **Generating Outputs**: Creates Excel/CSV files with complete curriculum details

## Requirements

### Dependencies

- **neo-ddg-search skill**: For web searching educational resources
  - Install: `clawhub install neobotjan2026/neo-ddg-search`

### System Requirements

- Node.js (installed with OpenClaw)
- Python 3 with pandas and openpyxl:
```bash
  pip3 install pandas openpyxl
```

## Installation

### Via ClawHub
```bash
clawhub install tarasinghrajput/curriculum-generator
```

### Manual Installation
```bash
cd ~/.openclaw/skills/
git clone https://github.com/tarasinghrajput/curriculum-generator curriculum-generator
cd curriculum-generator
```

## Usage

### Basic Usage

In your chat with ClawdBot:
```
Create a new curriculum for our POD
```

### With Debug Mode
```
Create curriculum debug mode:
- Topic: Web Development
- Duration: 12 weeks
- Show all searches
```

### Quick Test
```
Create tiny curriculum:
- Topic: Python basics
- 1 week, 2 lessons only
```

## Example Output

The skill generates CSV/Excel files with columns:
- Curriculum ID
- File Name
- Target POD Type
- Clusters
- Content Type
- Covered Topics
- Owner
- **Resource Link** (automatically populated with URLs)
- Document Creation Date
- Last Updated On

## How It Works

### Two Scenarios

**Scenario A**: Assessment of existing curriculum
- Evaluates current curriculum effectiveness
- Identifies gaps and improvement areas
- Provides actionable recommendations

**Scenario B**: Design of new curriculum
- Defines learning foundation and outcomes
- Develops course structure and timeline
- Plans teacher preparation
- Designs assessment strategy

### Resource Search Process

For each topic in the curriculum:
1. Executes DuckDuckGo search via neo-ddg-search
2. Extracts educational URLs from results
3. Prioritizes quality platforms (YouTube, FreeCodeCamp, W3Schools)
4. Populates resource links automatically

### Escalation Policy

The skill escalates to humans when:
- Missing critical inputs (age/grade, lab hours, teacher capability)
- Teacher capability risks detected
- Operational infeasibility identified
- High-risk curriculum changes proposed
- No resources found after searches

## Configuration

### Storage Locations

- **Memory**: `~/.openclaw/skills/curriculum-generator/memory/`
- **Outputs**: `~/.openclaw/skills/curriculum-generator/outputs/`
- **Templates**: `~/.openclaw/skills/curriculum-generator/templates/`

### Activation Triggers

The skill activates when you say:
- "create curriculum"
- "design curriculum"
- "assess curriculum"
- "curriculum help"

## Troubleshooting

### Resource Links Show "TBD"

Make sure neo-ddg-search is installed:
```bash
clawhub install neobotjan2026/neo-ddg-search
```

### Pandas Not Found

Install Python dependencies:
```bash
pip3 install pandas openpyxl
```

### Skill Not Activating?


Restart OpenClaw Gateway:
```bash
openclaw gateway restart
```

## Contributing

Contributions are welcome! Please:
1. Test your changes thoroughly
2. Update documentation
3. Follow the existing code style
4. Submit clear pull requests

## Credits

Created for educational POD curriculum generation with focus on digital literacy and skill development.

## Support

For issues or questions:
- Open an issue on GitHub
- Join the OpenClaw Discord community
- Check the [OpenClaw documentation](https://docs.openclaw.ai)

## Version History

### v1.0.0
- Initial release
- Structured questionnaire system
- Automatic resource link population
- Excel/CSV output generation
- Human escalation policies
- Memory and learning system
