---
name: edstem
description: Fetch, sync, and organize EdStem discussion threads for any course or institution. Use when checking for new EdStem posts, syncing course discussion forums, reviewing student/staff questions and answers, or when the user asks to check EdStem, review course discussions, or stay updated on class forums.
---

# EdStem

Fetch and organize EdStem discussion threads from any course or institution with automatic staff/student differentiation.

## Quick Start

Fetch recent threads for any course:

```bash
cd /home/axel/.openclaw/workspace/skills/edstem/scripts
python3 fetch-edstem.py <course_id> [output_dir] [--course-name "Course Name"]
```

**Examples:**
```bash
# Fetch to default directory (./edstem-<course_id>)
python3 fetch-edstem.py 92041

# Fetch to specific directory
python3 fetch-edstem.py 92041 ./machine-learning

# Specify course name for clearer output
python3 fetch-edstem.py 92041 --course-name "Machine Learning"

# Combine directory and course name
python3 fetch-edstem.py 92041 ./ml-course --course-name "Machine Learning"

# Fetch more threads (default is 10)
python3 fetch-edstem.py 92041 --limit 25
```

## Finding Your Course ID

To find your EdStem course ID:

1. Log into EdStem and navigate to your course
2. Look at the URL: `https://edstem.org/us/courses/<course_id>/`
3. The number in the URL is your course ID

Alternatively, use the API to list your courses:
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" https://us.edstem.org/api/user | jq '.courses[] | {id: .course.id, name: .course.name}'
```

## What Gets Fetched

For each course:
- **threads.json** - Full thread list with metadata
- **thread-XXX.md** - Individual threads formatted as markdown
  - Thread title, category, timestamps
  - Original post content
  - All answers and comments
  - **[STAFF]** or **[STUDENT]** tags on every post

## Features

- **Institution-agnostic**: Works with any school using EdStem
- **Staff differentiation**: Clearly marks instructor/TA posts vs student posts
- **Structured output**: Markdown format for easy reading and searching
- **API-based**: Uses EdStem's official API (no scraping)
- **Flexible output**: Choose your own output directory and organization scheme

## Authentication

The skill uses a bearer token stored in the Python script. To use with your own account:

1. Log into EdStem in your browser
2. Open Developer Tools → Network tab
3. Reload any EdStem page
4. Find an API request and copy the `Authorization: Bearer ...` token
5. Update `ED_TOKEN` in `scripts/fetch-edstem.py`

**Current token location:** Line 20 in `scripts/fetch-edstem.py`

If API calls fail (401 Unauthorized), your token likely expired and needs refresh.

## Scripts

### fetch-edstem.py (recommended)
Full-featured Python script with markdown formatting and staff/student differentiation.

**Usage:**
```bash
python3 scripts/fetch-edstem.py <course_id> [output_dir] [options]
```

**Options:**
- `output_dir` - Where to save threads (default: `./edstem-<course_id>`)
- `--course-name NAME` - Display name for the course
- `--limit N` - Number of threads to fetch (default: 10)

**Features:**
- Fetches thread metadata and full details
- Full markdown formatting with answers and comments
- Automatic staff role detection
- JSON cache of thread list
- Auto-creates output directory

### fetch-edstem.sh (lightweight alternative)
Bash/curl version for raw JSON fetching without dependencies.

**Usage:**
```bash
bash scripts/fetch-edstem.sh <course_id> [output_dir]
```

**Outputs:**
- Raw JSON files for each thread
- Requires manual formatting or post-processing

## Common Workflows

### Check for new posts
```bash
python3 scripts/fetch-edstem.py 92041 ~/courses/ml-spring-2025
```

### Sync multiple courses
```bash
# Create a simple sync script
for course in "92041:machine-learning" "94832:advanced-rl"; do
    IFS=':' read -r id name <<< "$course"
    python3 scripts/fetch-edstem.py $id ~/courses/$name --course-name "$name"
done
```

### Review recent activity
After fetching, check the markdown files:
```bash
ls -lt ./edstem-92041/*.md | head
cat ./edstem-92041/thread-001.md
```

### Search across threads
```bash
grep -r "gradient descent" ./edstem-92041/*.md
```

## Output Structure

```
<output_dir>/
├── threads.json              # Thread metadata
├── thread-001.md             # Individual threads
├── thread-002.md
└── ...
```

Each markdown file contains:
- Thread metadata (number, title, category, timestamps)
- Original post with author role
- All answers (sorted, with role tags)
- All comments (with role tags)

## Integration Examples

### With LLM agents
```bash
# Fetch threads and analyze with your agent
python3 fetch-edstem.py 92041 ./course-data
# Then: "Summarize the most common questions in ./course-data/"
```

### Automated monitoring
```bash
# Add to cron for daily sync
0 9 * * * cd /path/to/skills/edstem/scripts && python3 fetch-edstem.py 92041 ~/courses/ml
```

### Custom organization
```bash
# Organize by semester and institution
python3 fetch-edstem.py 92041 ~/school/stanford/2025-spring/cs229
python3 fetch-edstem.py 94832 ~/school/mit/2025-spring/6.7920
```

## Troubleshooting

**401 Unauthorized:** Token expired. Re-authenticate and update `ED_TOKEN` in the script.

**Course not found:** Verify the course ID and that your account has access.

**Empty threads:** Check that the course has discussion posts and you're enrolled.

**Rate limiting:** EdStem may rate-limit API requests. Add delays between fetches if needed.

## Contributing

This skill is open-source and institution-agnostic by design. Improvements welcome:
- Better content parsing (EdStem uses XML-based document format)
- Support for filtering by category or date range
- Incremental sync (only fetch new threads)
- Export to other formats (JSON, HTML, etc.)

## Version History

- **1.1.0** - Made institution-agnostic with flexible parameters
- **1.0.0** - Initial release
