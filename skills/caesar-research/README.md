# caesar-cli

A command-line interface for the [Caesar](https://www.caesar.org/) research API.

## Install

Requires [Go](https://go.dev/dl/) 1.21 or later.

```bash
go install github.com/alexrudloff/caesar-cli@latest
```

Or build from source:

```bash
git clone https://github.com/alexrudloff/caesar-cli.git
cd caesar-cli
go build -o caesar .
```

This produces a `caesar` binary in the current directory. Move it somewhere on your `$PATH` to use it globally:

```bash
mv caesar /usr/local/bin/
```

## Configuration

Get an API key from [caesar.org](https://www.caesar.org/) and set it as an environment variable:

```bash
export CAESAR_API_KEY=your_key_here
```

To persist it across shell sessions, add the export line to your shell profile (`~/.zshrc`, `~/.bashrc`, etc.), or create a local `.env` file:

```bash
echo 'export CAESAR_API_KEY=your_key_here' > .env
source .env
```

The `.env` file is git-ignored and will not be committed.

## Usage

### Research

```bash
# Run a research query (waits for completion by default)
caesar research create "What is quantum computing?"

# Return immediately with job ID
caesar research create "query" --no-wait

# Check on a job
caesar research get <job-id>

# Watch a job until it completes, printing events
caesar research watch <job-id>

# View reasoning events for a job
caesar research events <job-id>
```

Research options:

| Flag | Description |
|------|-------------|
| `--no-wait` | Return immediately with job ID |
| `--model` | Model to use (`gpt-5.2`, `gemini-3-pro`, `gemini-3-flash`, `claude-opus-4.5`) |
| `--loops N` | Max reasoning loops (default 1) |
| `--reasoning` | Enable reasoning mode |
| `--auto` | Auto-configure based on query |
| `--exclude-social` | Exclude social media sources |
| `--exclude-domain` | Domains to exclude (repeatable) |
| `--system-prompt` | Custom system prompt |
| `--brainstorm` | Brainstorm session ID to use |

### Chat

Ask follow-up questions about a completed research job:

```bash
# Send a follow-up (waits for response by default)
caesar chat send <job-id> "Tell me more about X"

# Return immediately
caesar chat send <job-id> "question" --wait=false

# View chat history
caesar chat history <job-id>
```

### Brainstorm

Get clarifying questions before starting research:

```bash
caesar brainstorm "How does CRISPR work?"
```

Then use the returned session ID:

```bash
caesar research create --brainstorm <session-id> "How does CRISPR work?"
```

### Collections

```bash
caesar collections create "My Dataset" --description "Optional description"
```
