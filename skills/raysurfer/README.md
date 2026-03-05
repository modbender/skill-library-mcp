# Raysurfer Code Caching Skill

Claude Code skill that provides code caching integration via the `/raysurfer` command.

## Installation

Copy the skill directory to your Claude Code skills folder:

```bash
cp -r raysurfer-code-caching-skill ~/.claude/skills/raysurfer
```

## Setup

```bash
export RAYSURFER_API_KEY=your_api_key_here
```

Get your key from the [dashboard](https://raysurfer.com/dashboard/api-keys).

## Usage

```
/raysurfer parse CSV and generate chart
```

Searches the cache for relevant code before generating new code.

```
/raysurfer upload
```

Uploads recently generated code to the cache for future reuse.

## Workflow

1. **Search**: Before writing code, searches for cached solutions
2. **Use or Generate**: Uses cached code if found, generates if not
3. **Vote**: Reports whether cached code worked
4. **Upload**: Stores new successful code for future reuse

## Runnable Scripts

The skill includes standalone scripts for each operation:

```bash
# Search
python search.py "Parse a CSV and plot a chart"
bun search.ts "Parse a CSV and plot a chart"
bash search.sh "Parse a CSV and plot a chart"

# Upload
python upload.py "Generate a bar chart" chart.py
bun upload.ts "Generate a bar chart" chart.py
bash upload.sh "Generate a bar chart" chart.py
```

## License

MIT
