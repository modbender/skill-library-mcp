# Script Templates

Ready-to-adapt patterns for common automation needs.

## Data Transformation

### JSON Prettify
```bash
#!/bin/bash
# Usage: ./prettify.sh input.json
jq '.' "$1"
```

### CSV to JSON
```bash
#!/bin/bash
# Usage: ./csv2json.sh input.csv
python3 -c "import csv,json,sys; print(json.dumps(list(csv.DictReader(open(sys.argv[1])))))" "$1"
```

### Extract Field
```bash
#!/bin/bash
# Usage: ./extract.sh file.json '.data.items[].name'
jq -r "$2" "$1"
```

## File Operations

### Batch Rename
```bash
#!/bin/bash
# Usage: ./rename.sh '*.txt' 'prefix_'
for f in $1; do mv "$f" "$2$f"; done
```

### Find and Replace
```bash
#!/bin/bash
# Usage: ./replace.sh 'old' 'new' '*.md'
find . -name "$3" -exec sed -i '' "s/$1/$2/g" {} +
```

## Validation

### JSON Schema Check
```bash
#!/bin/bash
# Usage: ./validate.sh data.json schema.json
npx ajv validate -s "$2" -d "$1"
```

### Link Checker
```bash
#!/bin/bash
# Usage: ./check-links.sh file.md
grep -oE 'https?://[^ ]+' "$1" | xargs -I {} curl -s -o /dev/null -w "%{http_code} {}\n" {}
```

## Git Workflows

### Quick Commit
```bash
#!/bin/bash
# Usage: ./commit.sh "message"
git add -A && git commit -m "$1" && git push
```

### PR from Branch
```bash
#!/bin/bash
# Usage: ./pr.sh "title"
BRANCH=$(git rev-parse --abbrev-ref HEAD)
git push -u origin "$BRANCH"
gh pr create --title "$1" --body ""
```

## API Integration

### Authenticated Request
```bash
#!/bin/bash
# Usage: ./api.sh GET /endpoint
TOKEN=$(security find-generic-password -a clawdbot -s api_token -w)
curl -s -X "$1" -H "Authorization: Bearer $TOKEN" "https://api.example.com$2"
```

### Paginated Fetch
```bash
#!/bin/bash
# Usage: ./fetch-all.sh /items
PAGE=1
while true; do
  RESULT=$(./api.sh GET "$1?page=$PAGE")
  echo "$RESULT" | jq '.items[]'
  [ $(echo "$RESULT" | jq '.has_more') = "false" ] && break
  ((PAGE++))
done
```

## Report Generation

### Markdown Table
```bash
#!/bin/bash
# Usage: echo "a,b,c" | ./table.sh
echo "| $(head -1 | tr ',' ' | ') |"
echo "|$(head -1 | sed 's/[^,]*/---/g' | tr ',' '|')|"
tail -n +2 | while read line; do echo "| $(echo $line | tr ',' ' | ') |"; done
```

## Template Usage

1. Copy template to scripts directory
2. Modify for your specific use case
3. Make executable: `chmod +x script.sh`
4. Document: add to automation tracking
5. Use instead of prompting

**Goal:** Build a library of scripts that eliminate repetitive LLM usage.
