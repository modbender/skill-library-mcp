# SKILL: Read Optimizer (read-optimizer)

## Description
Optimizes file reading operations by providing smarter read strategies (head/tail/grep/diff) to reduce token usage and latency. Use this when you need to inspect large files efficiently without dumping the entire content.

## Usage

### Smart Read (Head + Tail)
Reads the first N lines and the last N lines of a file. Good for logs or large docs.
```bash
node skills/read-optimizer/index.js --file <path> --mode smart --lines 100
```

### Grep Read (Focus)
Reads lines matching a pattern (regex supported).
```bash
node skills/read-optimizer/index.js --file <path> --mode grep --pattern "error|exception"
```

### Diff Read (Changes)
Reads only the lines changed since the last git commit (if in a git repo).
```bash
node skills/read-optimizer/index.js --file <path> --mode diff
```

## Options
- `--file <path>`: Path to the file.
- `--mode <smart|grep|diff>`: Operation mode (default: smart).
- `--lines <number>`: Number of lines for head/tail (default: 50).
- `--pattern <string>`: Regex pattern for grep mode.
- `--context <number>`: Context lines for grep (default: 2).
