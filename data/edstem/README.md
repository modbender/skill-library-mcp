# EdStem Integration Skill

Fetch, sync, and organize EdStem discussion threads from any course or institution with automatic staff/student differentiation.

## Overview

This skill provides tools to programmatically access EdStem discussion forums, making it easy to:
- Monitor course discussions
- Review student questions and instructor answers
- Archive forum content
- Analyze discussion patterns
- Integrate EdStem with LLM agents and automation workflows

**Institution-agnostic:** Works with any school using EdStem (not limited to any specific institution).

## Features

- ✅ **Staff differentiation**: Clearly marks instructor/TA posts vs student posts
- ✅ **Structured output**: Markdown format for easy reading and searching
- ✅ **API-based**: Uses EdStem's official API (no scraping)
- ✅ **Flexible output**: Choose your own output directory and organization scheme
- ✅ **Course auto-detection**: Automatically fetches course name from API
- ✅ **Lightweight alternative**: Bash script available for environments without Python

## Quick Start

```bash
# Clone or install the skill
cd ~/.openclaw/workspace/skills/edstem

# Fetch threads from any course
python3 scripts/fetch-edstem.py <course_id>

# Example with custom directory
python3 scripts/fetch-edstem.py 92041 ./my-course
```

## Installation

1. Install in your OpenClaw workspace:
   ```bash
   cd ~/.openclaw/workspace/skills
   git clone <repo-url> edstem
   ```

2. Configure authentication:
   - Log into EdStem in your browser
   - Open Developer Tools → Network tab
   - Copy the `Authorization: Bearer ...` token from any API request
   - Update `ED_TOKEN` in `scripts/fetch-edstem.py` (line 20)

3. Test it:
   ```bash
   cd edstem/scripts
   python3 fetch-edstem.py --help
   ```

## Usage Examples

### Basic fetch
```bash
python3 fetch-edstem.py 92041
```

### Specify output directory
```bash
python3 fetch-edstem.py 92041 ~/courses/machine-learning
```

### Add course name for clarity
```bash
python3 fetch-edstem.py 92041 --course-name "Machine Learning CS229"
```

### Fetch more threads
```bash
python3 fetch-edstem.py 92041 --limit 25
```

### Sync multiple courses
```bash
for course_id in 92041 94832 93717; do
    python3 fetch-edstem.py $course_id ~/courses/course-$course_id
done
```

## Finding Your Course ID

Your EdStem course ID is in the URL when you visit a course:
```
https://edstem.org/us/courses/12345/
                              ^^^^^
                           Course ID
```

Or use the API to list all your courses:
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  https://us.edstem.org/api/user | jq '.courses[] | {id: .course.id, name: .course.name}'
```

## Output Format

The skill saves:
- `threads.json` - Full thread list with metadata
- `thread-XXX.md` - Individual threads as readable markdown

Each markdown file includes:
- Thread title, category, and timestamps
- Original post with author role ([STAFF] or [STUDENT])
- All answers and comments with role tags
- Sorted chronologically

## Use Cases

### With LLM Agents
```bash
# Fetch and analyze
python3 fetch-edstem.py 92041 ./course-data
# Then ask your agent: "Summarize common questions in ./course-data/"
```

### Automated Monitoring
```bash
# Daily sync via cron
0 9 * * * cd ~/.openclaw/workspace/skills/edstem/scripts && \
  python3 fetch-edstem.py 92041 ~/courses/ml
```

### Multi-Institution Setup
```bash
# Organize by school and semester
python3 fetch-edstem.py 92041 ~/school/stanford/2025-spring/cs229
python3 fetch-edstem.py 94832 ~/school/mit/2025-spring/6.7920
```

### Search Across Threads
```bash
# After fetching
grep -r "gradient descent" ./edstem-92041/*.md
```

## Requirements

- Python 3.6+
- `requests` library (`pip install requests`)
- Valid EdStem authentication token

The bash script alternative only requires:
- `curl`
- `jq`

## Documentation

See [SKILL.md](SKILL.md) for complete documentation including:
- Detailed API usage
- Troubleshooting guide
- Integration examples
- Contributing guidelines

## Version History

- **1.1.0** (2025-02-17) - Made institution-agnostic with flexible parameters
- **1.0.0** - Initial release (Columbia-specific)

## License

MIT License - Free to use and modify

## Contributing

Contributions welcome! Areas for improvement:
- Better content parsing (EdStem uses XML-based document format)
- Support for filtering by category or date range
- Incremental sync (only fetch new threads)
- Export to other formats (JSON, HTML, etc.)

## Support

For issues or questions:
- Check [SKILL.md](SKILL.md) for troubleshooting
- Open an issue on the repository
- Review the EdStem API documentation

---

Built for the OpenClaw ecosystem 🐾
