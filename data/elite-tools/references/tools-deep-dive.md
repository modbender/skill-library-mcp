# Elite CLI Tools - Deep Dive

## 1. Fast File Discovery with `fdfind`

### Why Replace `find`?
- 5-50x faster (parallelized, Rust-based)
- Respects `.gitignore` by default (no `node_modules` floods)
- Smart case sensitivity
- Intuitive syntax: `fdfind PATTERN` vs `find -iname '*PATTERN*'`

### Examples

```bash
# Find by extension
fdfind -e py

# Find in specific directory
fdfind passwd /etc

# Include hidden files
fdfind -H pre-commit

# Search full path
fdfind -p '.*/lesson-\d+/[a-z]+.jpg'

# Exclude patterns
fdfind -H -E .git -E '*.bak'

# Execute on results (parallel)
fdfind -e zip -x unzip

# Open all test files in editor
fdfind -g 'test_*.py' -X vim

# Delete recursively
fdfind -H '\.DS_Store$' -tf -X rm

# Show file details
fdfind -e rs -l
```

## 2. File Viewing with `batcat`

### Why Replace `cat`/`less`?
- Syntax highlighting for 100+ languages
- Git integration (shows modifications)
- Automatic paging
- Line numbers and decorations
- Non-printable character visualization

### Examples

```bash
# View with syntax highlighting
batcat README.md

# Line numbers only
batcat -n main.rs

# Specific line range
batcat --line-range 50:80 -n src/main.rs

# Plain output (no decorations)
batcat -p notes.md

# Show non-printable characters
batcat -A /etc/hosts

# Combine files
batcat header.md content.md footer.md > document.md

# Colorize man pages
export MANPAGER="batcat -plman"

# Colorize help text
cp --help | batcat -plhelp

# Continuous log monitoring
tail -f app.log | batcat --paging=never -l log

# View old git version
git show v0.6.0:src/main.rs | batcat -l rs

# Use as fzf previewer
fzf --preview "batcat --color=always --line-range=:500 {}"
```

## 3. Intuitive String Replacement with `sd`

### Why Replace `sed`?
- Familiar regex (JavaScript/Python style)
- No delimiter escaping hell
- String-literal mode (`-F`)
- Preview mode (`-p`)
- ~2-12x faster than sed

### Examples

```bash
# Simple replacement
sd 'before' 'after' file.txt

# String-literal mode (no regex)
sd -F '((([])))' '' log.txt

# Capture groups
sd '(\w+)\s+\+(\w+)\s+(\w+)' 'cmd: $1, channel: $2, subcmd: $3' file.txt

# Named capture groups
sd '(?P<dollars>\d+)\.(?P<cents>\d+)' '$dollars dollars and $cents cents' prices.txt

# Preview changes
sd -p 'window.fetch' 'fetch' http.js

# In-place file modification
sd 'window.fetch' 'fetch' http.js

# Project-wide replacement (with fd)
fdfind --type file --exec sd 'from "react"' 'from "preact"'

# Replace newlines with commas
sd '\n' ',' file.txt

# Extract paths from strings
echo "sample with /path/" | sd '.*(/.*/)'  '$1'
```

## 4. Code Structural Search with `sg` (ast-grep)

### Why Replace `grep`/`ripgrep`?
- Searches AST not text (ignores formatting)
- Pattern code looks like real code
- Wildcard matching with `$VAR` and `$$$MULTI`
- Rewrite/refactor capabilities
- 20+ languages supported

### Examples

```bash
# Find variable declarations
sg -p 'let $VAR = $VALUE' src/

# Find function calls
sg -p '$FUNC($$$ARGS)' src/

# Find try-catch blocks
sg -p 'try { $$$BODY } catch ($ERR) { $$$HANDLER }' src/

# Rewrite optional chaining
sg -p '$A && $A()' -l ts -r '$A?.()' src/

# Find imports from specific module
sg -p 'import { $$$ITEMS } from "$MODULE"' src/

# Rewrite API migration
sg -p 'new Zodios($URL, $CONF as const,)' -l ts -r 'new Zodios($URL, $CONF)' -i src/
```

## 5. CLI to JSON with `jc`

### Why Replace `awk`/`cut` chains?
- Structured JSON from 90+ CLI tools
- Schema-aware (numbers/bools preserved)
- Strict and raw modes
- Python library support
- Streaming parsers for large data

### Examples

```bash
# Process list
ps aux | jc --ps | jq '.[] | select(.cpu_percent > 1.0) | .command'

# Disk usage
df -h | jc --df | jq '.[] | select(.use_percent > 80) | .filesystem'

# Network connections
netstat -tuln | jc --netstat | jq '.[] | select(.state == "LISTEN") | .local_address'

# DNS lookup
dig example.com | jc --dig | jq '.[].answer[].data'

# System uptime
uptime | jc --uptime | jq '.uptime_days'

# Parse CSV
cat data.csv | jc --csv | jq '.[] | select(.status == "active")'

# Magic syntax (prepend jc)
jc ps aux | jq '.[].pid'

# Batch IP processing
cat ips.txt | jc --slurp --ip-address | jq '.[] | select(.is_private == false)'
```

## 6. JSON Flattening with `gron`

### Why Replace `jq` for exploration?
- Makes nested JSON greppable
- Shows absolute path to every value
- Reversible (`--ungron` rebuilds JSON)
- Valid JavaScript output
- JSON stream mode

### Examples

```bash
# Flatten JSON from file
gron data.json

# Flatten from URL
gron https://api.github.com/users/octocat

# Flatten from stdin
curl -s https://api.example.com | gron

# Find specific fields
gron data.json | grep 'email'

# Diff JSON files
diff <(gron old.json) <(gron new.json)

# Filter and rebuild JSON
gron data.json | grep 'dependencies' | gron --ungron

# Reverse (ungron)
gron data.json | grep 'likes' | gron --ungron

# JSON stream mode
curl -s https://api.example.com | gron --json
```

## 7. YAML/JSON/XML Processing with `yq`

### Why Replace `sed` on YAML?
- Syntax-aware (preserves indentation/comments)
- Multi-format (YAML/JSON/XML/CSV/TOML)
- jq-like expression language
- In-place editing
- Environment variable substitution

### Examples

```bash
# Read value
yq '.database.host' config.yaml

# Update in-place
yq -i '.database.port = 5432' config.yaml

# Environment variables
DB_HOST=localhost yq -i '.database.host = strenv(DB_HOST)' config.yaml

# Merge files
yq -n 'load("base.yaml") * load("overlay.yaml")'

# Merge with globs
yq ea '. as $item ireduce ({}; . * $item)' path/to/*.yml

# Multiple updates
yq -i '
  .a.b[0].c = "cool" |
  .x.y.z = "foobar"
' file.yaml

# Find and update array item
yq -i '(.[] | select(.name == "foo") | .address) = "12 cat st"' data.yaml

# Convert JSON to YAML
yq -Poy sample.json

# Convert YAML to JSON
yq -o json config.yaml

# Filter enabled services
yq '.services |= map(select(.enabled == true))' docker-compose.yml
```

## 8. Semantic Diffs with `difft`

### Why Replace `diff`?
- Syntax-aware (understands code structure)
- Highlights actual changes vs reformatting
- 40+ languages supported
- Not line-oriented (handles multi-line refactors)
- Merge conflict visualization

### Examples

```bash
# Compare files
difft old.py new.py

# Ignore formatting changes
difft formatted.js unformatted.js

# Check if ASTs are identical
difft --check-only --exit-code before.js after.js

# Handle merge conflicts
difft conflicted_file.py

# Use with git
git config --global diff.external difft
```

## 9. Documentation with `tldr` (tealdeer)

### Why Replace `man`?
- Concise, example-focused
- Community-driven practical examples
- Colorized output
- Offline cache
- ~13ms startup (Rust)

### Examples

```bash
# Get examples for a command
tldr tar

# Platform-specific
tldr --platform osx pbcopy

# Search commands
tldr --search archive

# Update cache
tldr --update

# List all available pages
tldr --list
```

## 10. Web to Markdown with `html2text`

### Why Replace raw HTML parsing?
- Clean Markdown output
- Strips tags/CSS/JS noise
- Configurable width and formatting
- Preserves document structure

### Examples

```bash
# Convert webpage
curl -s https://example.com | html2text

# Set output width
html2text -width 100 page.html

# UTF-8 mode
html2text -utf8 page.html

# Ignore links
html2text -nobs page.html

# Pretty style (more vertical space)
html2text -style pretty page.html
```

## Integration Workflows

### Code Refactoring Pipeline
```bash
sg -p 'oldFunc($$$ARGS)' src/ | batcat
sg -p 'oldFunc($$$ARGS)' -r 'newFunc($$$ARGS)' -i src/
```

### System Analysis
```bash
ps aux | jc --ps | jq -r '.[] | select(.cpu_percent > 5.0) | .command' | sort | uniq -c
```

### Config Management
```bash
yq '.version' config.yaml
yq -i '.version = "2.0.0"' config.yaml
```

### JSON Exploration
```bash
curl -s https://api.example.com | gron | grep 'user' | gron --ungron | jq .
```
