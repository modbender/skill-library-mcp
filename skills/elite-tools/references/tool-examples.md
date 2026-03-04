# Tool Examples

This file contains practical examples for each of the modern CLI tools.

## fdfind Examples

Find all Python files:
```bash
fdfind "\.py$"
```

Find files by name:
```bash
fdfind "config.yaml"
```

## batcat Examples

View file with line numbers:
```bash
batcat -n file.txt
```

View specific line range:
```bash
batcat --line-range 10:20 -n file.txt
```

## sd Examples

Replace text in a file:
```bash
sd "old_text" "new_text" file.txt
```

## sg Examples

Find variable declarations:
```bash
sg -p "let $VAR = $VALUE" src/
```

## jc Examples

Parse process list:
```bash
jc ps aux
```

Parse disk usage:
```bash
jc df -h
```

## gron Examples

Flatten JSON:
```bash
curl -s https://api.github.com/users/octocat | gron
```

Filter flattened JSON:
```bash
curl -s https://api.github.com/users/octocat | gron | grep "name"
```

## yq Examples

Read YAML value:
```bash
yq e '.database.host' config.yaml
```

Update YAML value:
```bash
yq e '.database.port = 5432' -i config.yaml
```

## difft Examples

Compare files:
```bash
difft file1.txt file2.txt
```

## tealdeer Examples

Get help for a command:
```bash
tealdeer ls
```

## html2text Examples

Convert HTML to Markdown:
```bash
curl -s https://example.com | html2text
```