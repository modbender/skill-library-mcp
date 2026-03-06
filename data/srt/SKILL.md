---
name: srt
description: Korean SRT (Super Rapid Train) search, reservation, and booking management
homepage: https://github.com/khj809/openclaw-srt-skill
user-invocable: true
metadata:
  {
    "openclaw":
      {
        "emoji": "🚅",
        "requires": { "bins": ["python3", "uv"], "env": ["SRT_PHONE", "SRT_PASSWORD"] },
        "install": [
          {"id": "uv", "kind": "uv", "package": "SRTrain", "label": "Install SRTrain from PyPI (uv) — source: https://pypi.org/project/SRTrain / https://github.com/ryanking13/SRT"}
        ]
      },
  }
---

# SRT Korean Train Service Skill

## Prerequisites

- Environment variables `SRT_PHONE` (format: `010-XXXX-XXXX`) and `SRT_PASSWORD` must be set before running scripts.

## Reference

**Environment variables:**
| Variable | Required | Description |
|----------|----------|-------------|
| `SRT_PHONE` | ✅ | SRT account phone number (hyphens required: `010-XXXX-XXXX`) |
| `SRT_PASSWORD` | ✅ | SRT account password |
| `SRT_DATA_DIR` | optional | Directory for logs, cache, and state files. Defaults to system temp dir (`/tmp/srt`). |

**Station names** (Korean only):
수서, 부산, 동대구, 대전, 천안아산, 오송, 광주송정, 울산, 포항, 경주, 김천구미, 익산, 전주, 목포, 신경주

**Date:** `YYYYMMDD` · **Time:** `HHMMSS` (e.g. `200000` = 20:00)

---

## Commands

### Search Trains
```bash
cd <project_dir> && uv run --with SRTrain python3 scripts/srt_cli.py train search \
  --departure "수서" --arrival "동대구" --date "20260227" --time "200000"
```
Search params and results are cached (in `SRT_DATA_DIR`) and required by `reserve`.

### Reserve (one-shot)
```bash
cd <project_dir> && uv run --with SRTrain python3 scripts/srt_cli.py reserve one-shot --train-id "1"
```
`--train-id` is the 1-based index from search results. Must run `train search` first.

### View Reservations
```bash
cd <project_dir> && uv run --with SRTrain python3 scripts/srt_cli.py reserve list --format json
```

### Cancel Reservation
```bash
cd <project_dir> && uv run --with SRTrain python3 scripts/srt_cli.py reserve cancel \
  --reservation-id "RES123456" --confirm
```

---

## Continuous Monitoring (취소표 모니터링)

For "keep trying until a seat opens" requests, **do not loop inside a cron job**.
Instead: run `srt_cli.py reserve retry` as a persistent background process, then create a separate cron job to read the log and report.

### Step 1: Search (populate cache)
```bash
cd <project_dir> && uv run --with SRTrain python3 scripts/srt_cli.py train search \
  --departure "수서" --arrival "동대구" --date "20260227" --time "200000"
```
Note the `train_id` of the target train from the results.

### Step 2: Start background retry process
```bash
LOG_FILE=<choose_any_path>.log
PID_FILE=<choose_any_path>.pid
cd <project_dir> && nohup uv run --with SRTrain python3 scripts/srt_cli.py reserve retry \
  --train-id <id> --timeout-minutes 1440 --wait-seconds 10 \
  --log-file "$LOG_FILE" > /dev/null 2>&1 &
echo $! > "$PID_FILE"
```

The script prints `LOG_FILE: <path>` on startup — capture this to know exactly where logs are written.
You may also set `SRT_DATA_DIR` to control where auto-generated logs and cache files are placed.

> **Path safety:** `SRT_DATA_DIR` and `--log-file` are validated at runtime to resolve within the user's home directory or system temp dir only. Paths that escape these boundaries (e.g. via `../`) are rejected.

**`reserve retry` options:**
| Option | Default | Description |
|--------|---------|-------------|
| `--train-id` | (all) | 1-based index from search; comma-separated for multiple |
| `--timeout-minutes` | 60 | Total duration. Use 1440 for 24h |
| `--wait-seconds` | 10 | Delay between attempts |
| `--log-file` | auto | Explicit log file path (overrides `SRT_DATA_DIR` default) |

Log markers to watch for:
- `=== 시도 #N` — attempt number
- `SUCCESS` — reservation succeeded (contains 예약번호, 좌석)
- `TIMEOUT` — timed out without success

### Step 3: Create periodic reporting cron job
Create an **isolated agentTurn** cron job (every 15 min) with **`--no-deliver`** (delivery mode: none).
The agent must use the `message` tool to post directly to the Discord channel — do **not** use `--announce` (the announce queue can fail with a gateway pairing error in isolated sessions).

CLI:
```bash
openclaw cron add \
  --agent srt \
  --name "SRT 모니터링 보고 (15분마다)" \
  --every 15m \
  --session isolated \
  --no-deliver \
  --message "..."
```

Agent message must instruct:
1. Check process status:
   ```bash
   cd <project_dir> && uv run --with SRTrain python3 scripts/srt_cli.py reserve status --pid-file <pid_file>
   ```
2. Read log tail: `tail -50 <log_file>`
3. Summarise attempt count, last attempt time, success/failure
4. **Send report via `message` tool** (`channel=discord`, `target=<channel_id>`)
5. On `SUCCESS` in log → include 예약번호/좌석 in message, then remove this cron job and termination job
6. On `NOT_RUNNING` without `SUCCESS` → report crash, remove this cron job

The message payload must include this job's own ID and the termination job ID so it can self-remove.

### Step 4: Create termination job
Create an **isolated agentTurn** `at`-schedule cron job (`--no-deliver`, `--delete-after-run`) at the deadline.

CLI:
```bash
openclaw cron add \
  --agent srt \
  --name "SRT 모니터링 종료" \
  --at "<ISO UTC time>" \
  --session isolated \
  --no-deliver \
  --delete-after-run \
  --message "..."
```

Agent message must instruct:
1. Stop the process:
   ```bash
   cd <project_dir> && uv run --with SRTrain python3 scripts/srt_cli.py reserve stop --pid-file <pid_file>
   ```
2. Remove the reporting cron job by ID
3. Read final log and **send outcome via `message` tool** to Discord channel

---

## JSON Output

**Search result item:**
```json
{
  "train_number": "369",
  "departure_time": "200000",
  "arrival_time": "213600",
  "departure_station": "수서",
  "arrival_station": "동대구",
  "seat_available": false,
  "general_seat": "매진",
  "special_seat": "매진",
  "train_id": "1"
}
```

**Reservation result:**
```json
{
  "success": true,
  "data": {
    "reservation_id": "RES123456",
    "train_number": "369",
    "seat_number": "3A",
    "payment_required": true
  }
}
```

Exit codes: `0` = success · `1` = retryable (no seats) · `2` = fatal

---

## Error Handling

| Error | Cause | Resolution |
|-------|-------|-----------|
| `AuthenticationFailed` | Wrong credentials | Check `SRT_PHONE` / `SRT_PASSWORD` |
| `NoSeatsAvailable` | Sold out | Use `--retry` or try different train |
| `StationNotFound` | Invalid name | Use Korean station names above |
| `NoTrainsFound` | No trains found | Try different date/time |
| `RateLimitExceeded` | Too many attempts | Wait a few minutes |

---

## Natural Language Handling

Extract from Korean input:
- Stations → Korean names (수서, 동대구, etc.)
- Date → relative ("내일", "다음주 금요일") to YYYYMMDD
- Time → ("20시 이후", "오후 2시") to HHMMSS
- Passenger count → default 1 if not specified

**Patterns:**
- "검색해줘" → `train search`
- "예약해줘" (one-shot) → `train search` then `reserve one-shot`
- "취소표 나오면 잡아줘 / 될 때까지 돌려줘" → Continuous Monitoring flow above
- "내 예약 확인해줘" → `reserve list`
- "취소해줘" → `list` then `cancel`

## Payment Note
Reservations must be paid via SRT app or <https://etk.srail.kr> within ~20 minutes of reservation.
