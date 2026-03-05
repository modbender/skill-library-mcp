# Security Audit - Intrusive Thoughts

## Network Activity Audit

### Outbound Network Calls

**Location**: `set_mood.sh` (lines 11-23)

All network calls are **read-only GET requests** with **no authentication** to public APIs:

1. **Weather API (`wttr.in`)**
   - `curl -s "wttr.in/${LOCATION}?format=%c+%t+%h+%w"`
   - `curl -s "wttr.in/${LOCATION}?format=3"`  
   - `curl -s "wttr.in/${LOCATION}?0T"`
   - Purpose: Get weather data for mood influence
   - Data: Public weather information only

2. **BBC News RSS**
   - `curl -s "https://feeds.bbci.co.uk/news/world/rss.xml"`
   - Purpose: Get news headlines for mood influence
   - Data: Public RSS feed, read-only

3. **Hacker News RSS**
   - `curl -s "https://hnrss.org/frontpage"`
   - Purpose: Get tech news headlines for mood influence  
   - Data: Public RSS feed, read-only

**No outbound POST requests** - system never sends data externally.

### Optional Integrations (Disabled by Default)

- **Telegram Bot**: Can be enabled in config.json, but requires explicit user configuration
- **OpenAI API**: Optional environment variable, not required for core functionality

## File Operations Audit

### File Access Scope

**All file operations are restricted to the skill directory**: `~/Projects/intrusive-thoughts/`

### File Read Operations

- **Configuration**: `config.json`, `config.example.json`
- **Data**: `moods.json`, `thoughts.json`, `today_mood.json`
- **Logs**: Files in `log/` subdirectory
- **Memory**: Files in `memory_store/` subdirectory
- **Trust**: Files in `trust_store/` subdirectory
- **Health**: Files in `health/` subdirectory

### File Write Operations

- **Mood tracking**: `today_mood.json`, `mood_history.json`
- **Logging**: Various `.json` files in `log/` subdirectory
- **Memory system**: Files in `memory_store/` and `buffer/`
- **Trust learning**: Files in `trust_store/` 
- **Health monitoring**: Files in `health/`
- **Configuration backups**: `.backup.timestamp` files

**Note on `data_dir`:** The `config.json` field `system.data_dir` controls where
runtime data is stored (default: the skill directory itself). If a user changes
`data_dir` to a different path, file operations will target that path instead.
The skill only reads/writes its own data files (moods, logs, memory, etc.) — it
never scans directories or accesses unrelated files. But users should be aware
that `data_dir` determines the sandbox boundary.

## Subprocess Execution Audit

### Subprocess Calls

**Location**: `dashboard.py` (line 93)

```python
result = subprocess.run(['python3', str(get_data_dir() / 'analyze.py'), '--json'],
                       capture_output=True, text=True)
```

- **Purpose**: Dashboard calls its own `analyze.py` script for data analysis
- **Safety**: `shell=False` (default) - no shell injection risk
- **Scope**: Only calls own script within skill directory
- **Arguments**: Static arguments `['python3', 'path/to/analyze.py', '--json']`

## Security Controls

### What This System DOES NOT Do

- ❌ **No `eval()`** - No dynamic code evaluation
- ❌ **No `os.system()`** - No shell command injection
- ❌ **No `shell=True`** - No shell-based subprocess execution
- ❌ **No `base64` decode** - No encoded payload execution
- ❌ **No `sudo`** - No privilege escalation
- ❌ **No external file access** - All operations within skill directory
- ❌ **No cron/at creation in scripts** - No script calls `crontab`, `at`, or any system scheduler directly. Scheduling is done by the AI agent through OpenClaw's cron API at runtime, which the user can inspect via `openclaw cron list`
- ❌ **No remote code execution** - All code is local and user-controlled

### Unicode Control Characters

- **Issue**: Zero-width joiner (U+200D) found in emoji sequences
- **Status**: ✅ **RESOLVED** - Cleaned from all source files
- **Risk**: Low (cosmetic issue, not exploitable)

## Autonomous Execution Model

### Script Execution Sources

All autonomous prompts come from **user-controlled** sources:

1. **Morning Ritual** (`set_mood.sh`)
   - Reads weather/news for mood selection
   - No external prompts - pure data aggregation

2. **Night Workshops** (`intrusive.sh night`)  
   - Prompts sourced from user's `thoughts.json`
   - User creates and controls all thought content
   - No external prompt sources

3. **Daytime Pop-ins** (`intrusive.sh day`)
   - Prompts sourced from user's `thoughts.json`  
   - Scheduled by user's configuration
   - No external prompt sources

### Cron Job Creation — Important Distinction

**No script in this skill creates cron or at entries.** You can verify:
```bash
grep -rn 'crontab\|atq\|atrm\|\bat\b' *.sh *.py  # returns nothing relevant
```

Scheduling is handled by the **AI agent** through OpenClaw's built-in cron API
(a tool available to all OpenClaw agents, not specific to this skill). The agent
creates cron jobs by calling the `cron` tool during conversation — the same way
it would call any other tool. These jobs are visible and manageable:
```bash
openclaw cron list          # see all scheduled jobs
openclaw cron remove <id>   # remove any job
```

The SKILL.md describes the *intended* cron schedule (morning ritual, night
workshop, pop-ins) as instructions for the agent to set up — not as something
the install scripts do automatically. The user/agent is in control of what
gets scheduled.

## Security Assessment

### Risk Level: **LOW**

- ✅ **Network**: Read-only access to public APIs only
- ✅ **Files**: Sandboxed to skill directory  
- ✅ **Execution**: No dangerous system calls or shell injection
- ✅ **Autonomy**: All prompts are user-controlled
- ✅ **Scheduling**: Managed by OpenClaw, not scripts

### Recommendations

1. **Review `config.json`** before first run
2. **Audit `thoughts.json`** - all autonomous prompts come from here
3. **Monitor `log/`** directory for activity logs
4. **Keep integrations disabled** unless explicitly needed

---

*Last updated: 2026-02-14*  
*Audit scope: Full codebase scan for network calls, file operations, and subprocess execution*