# Role Input/Output Map

This document maps how data moves between roles in `social-ops`.

Use it to:
- understand role handoffs
- see which artifacts are read/written by each role
- audit logging coverage

## Canonical workflow

```text
Scout ──┬─> Content Specialist ──> Writer ──> Poster
        └─> Responder

Researcher ──> Guidance ──> Content Specialist + Writer + Poster (+ Analyst for review context)

Poster + Scout + Responder + Researcher + Writer outputs ──> Analyst
Analyst recommendations ──> Content Specialist + Researcher
```

## Role-by-role I/O

## Scout
- Reads:
  - Moltbook feed/submolts/accounts (platform data)
  - `$SOCIAL_OPS_DATA_DIR/Guidance/README.md`
  - `$SOCIAL_OPS_DATA_DIR/Guidance/GOALS.md`
  - `$SOCIAL_OPS_DATA_DIR/Content/Lanes/`
  - `$SOCIAL_OPS_DATA_DIR/Submolts/Primary.md`
  - `$SOCIAL_OPS_DATA_DIR/Submolts/Candidates.md`
- Writes:
  - `$SOCIAL_OPS_DATA_DIR/Content/Logs/Scout-YYYY-MM-DD.md`
  - `$SOCIAL_OPS_DATA_DIR/Submolts/Candidates.md` (new candidate entries)
- Primary consumers:
  - Responder (thread insertion opportunities)
  - Content Specialist (topic opportunities)
  - Researcher (trend follow-up)

## Researcher
- Reads:
  - Moltbook high-performing posts/accounts
  - `$SOCIAL_OPS_DATA_DIR/Guidance/GOALS.md` (human direction)
  - `$SOCIAL_OPS_DATA_DIR/Guidance/Research-Tasks.md` (task queue)
  - prior research logs
  - `$SOCIAL_OPS_DATA_DIR/Submolts/Candidates.md`
  - `$SOCIAL_OPS_DATA_DIR/Submolts/Primary.md`
- Writes:
  - `$SOCIAL_OPS_DATA_DIR/Guidance/README.md` (durable guidance)
  - `$SOCIAL_OPS_DATA_DIR/Guidance/Research-Tasks.md` (task queue updates)
  - `$SOCIAL_OPS_DATA_DIR/Content/Logs/Research-YYYY-MM-DD.md`
  - `$SOCIAL_OPS_DATA_DIR/Submolts/Candidates.md` (analysis notes, additional candidates)
- Primary consumers:
  - Content Specialist (content planning)
  - Poster (tone/check alignment)
  - Analyst (pattern validation over time)

## Content Specialist
- Reads:
  - `$SOCIAL_OPS_DATA_DIR/Guidance/README.md`
  - `$SOCIAL_OPS_DATA_DIR/Guidance/GOALS.md`
  - `$SOCIAL_OPS_DATA_DIR/Guidance/Local-File-References.md` (optional, human-curated)
  - `$SOCIAL_OPS_DATA_DIR/Content/Lanes/`
  - recent `$SOCIAL_OPS_DATA_DIR/Content/Logs/Research-YYYY-MM-DD.md`
  - `$SOCIAL_OPS_DATA_DIR/Submolts/Candidates.md`
  - `$SOCIAL_OPS_DATA_DIR/Submolts/Primary.md`
  - local files/directories referenced by `Local-File-References.md` (only if present/accessible)
- Writes:
  - `$SOCIAL_OPS_DATA_DIR/Content/Lanes/*.md` (create/refine/retire lane definitions)
  - `$SOCIAL_OPS_DATA_DIR/Content/Logs/Content-YYYY-MM-DD.md`
  - `$SOCIAL_OPS_DATA_DIR/Submolts/Primary.md` (promotions from Candidates)
  - `$SOCIAL_OPS_DATA_DIR/Submolts/Candidates.md` (removals after promotion)
  - `$SOCIAL_OPS_DATA_DIR/Submolts/Retired.md` (retired submolts)
- Primary consumers:
  - Writer (writes final posts based on lanes)
  - Analyst (evaluates lane/post pipeline performance)

## Writer
- Reads:
  - `$SOCIAL_OPS_DATA_DIR/Guidance/README.md`
  - `$SOCIAL_OPS_DATA_DIR/Guidance/GOALS.md`
  - `$SOCIAL_OPS_DATA_DIR/Content/Memory/writer.md` (long-term memory)
  - `$SOCIAL_OPS_DATA_DIR/Content/Memory/writer-YYYY-MM-DD.md` (last 3 days)
  - `$SOCIAL_OPS_DATA_DIR/Content/Lanes/` (selects one lane per run)
  - `$SOCIAL_OPS_DATA_DIR/Content/Todo/` (queue depth check)
  - `$SOCIAL_OPS_DATA_DIR/Submolts/Primary.md`
  - `$SOCIAL_OPS_DATA_DIR/Guidance/Local-File-References.md` (optional, human-curated)
  - local files/directories referenced by `Local-File-References.md` (only if present/accessible)
  - recent `$SOCIAL_OPS_DATA_DIR/Content/Logs/Research-YYYY-MM-DD.md`
- Writes:
  - `$SOCIAL_OPS_DATA_DIR/Content/Todo/YYYY-MM-DD-XX-LaneName.md`
  - `$SOCIAL_OPS_DATA_DIR/Content/Memory/writer.md` (long-term memory updates)
  - `$SOCIAL_OPS_DATA_DIR/Content/Memory/writer-YYYY-MM-DD.md` (daily memory log)
  - `$SOCIAL_OPS_DATA_DIR/Content/Logs/Writer-YYYY-MM-DD.md`
- Primary consumers:
  - Poster (publishes TODO items)
  - Analyst (evaluates post quality and queue balance)

## Poster
- Reads:
  - `$SOCIAL_OPS_DATA_DIR/Guidance/README.md`
  - `$SOCIAL_OPS_DATA_DIR/Content/Todo/`
  - `$SOCIAL_OPS_DATA_DIR/Content/Lanes/`
- Writes:
  - `$SOCIAL_OPS_DATA_DIR/Content/Done/` (moves posted file from Todo)
  - `$SOCIAL_OPS_DATA_DIR/Content/Logs/Poster-YYYY-MM-DD.md`
  - published post URL attached to moved post artifact
- Primary consumers:
  - Analyst (performance review)
  - Responder (reply surface from posted content)

## Responder
- Reads:
  - Moltbook replies/DMs/mentions
  - `{baseDir}/../state/comment-state.json`
  - latest Scout log: `$SOCIAL_OPS_DATA_DIR/Content/Logs/Scout-YYYY-MM-DD.md`
- Writes:
  - `{baseDir}/../state/comment-state.json` (watermarks + seen ids)
  - `$SOCIAL_OPS_DATA_DIR/Content/Logs/Responder-YYYY-MM-DD.md`
- Primary consumers:
  - Analyst (relational signal quality)

## Analyst
- Reads:
  - `$SOCIAL_OPS_DATA_DIR/Content/Done/`
  - `$SOCIAL_OPS_DATA_DIR/Content/Logs/Poster-YYYY-MM-DD.md`
  - `$SOCIAL_OPS_DATA_DIR/Content/Logs/Writer-YYYY-MM-DD.md`
  - `$SOCIAL_OPS_DATA_DIR/Content/Logs/Responder-YYYY-MM-DD.md`
  - `$SOCIAL_OPS_DATA_DIR/Content/Logs/Scout-YYYY-MM-DD.md`
  - `$SOCIAL_OPS_DATA_DIR/Content/Logs/Research-YYYY-MM-DD.md`
  - `$SOCIAL_OPS_DATA_DIR/Submolts/Primary.md`
  - Moltbook engagement metrics
- Writes:
  - `$SOCIAL_OPS_DATA_DIR/Content/Logs/Analysis-YYYY-WW.md` (includes submolt retirement recommendations)
  - recommendations (consumed by Content Specialist + Researcher)
- Primary consumers:
  - Content Specialist (lane/cadence changes)
  - Researcher (new research focus)

## Shared artifact map

- Guidance artifacts:
  - `$SOCIAL_OPS_DATA_DIR/Guidance/README.md` (producer: Researcher; consumers: Scout, Content Specialist, Writer, Poster, Analyst)
  - `$SOCIAL_OPS_DATA_DIR/Guidance/GOALS.md` (producer: human operator; consumers: Scout, Researcher, Content Specialist, Writer)
  - `$SOCIAL_OPS_DATA_DIR/Guidance/Research-Tasks.md` (producer/consumer: Researcher)
  - `$SOCIAL_OPS_DATA_DIR/Guidance/Local-File-References.md` (producer: human operator and/or Researcher; consumers: Content Specialist, Writer)

- Pipeline artifacts:
  - `$SOCIAL_OPS_DATA_DIR/Content/Todo/` (producer: Writer; consumer: Poster)
  - `$SOCIAL_OPS_DATA_DIR/Content/Done/` (producer: Poster; consumer: Analyst)
  - `$SOCIAL_OPS_DATA_DIR/Content/Lanes/` (producer: Content Specialist; consumers: Poster, Analyst)

- Log artifacts:
  - `$SOCIAL_OPS_DATA_DIR/Content/Logs/Scout-YYYY-MM-DD.md` (producer: Scout; consumers: Responder, Analyst)
  - `$SOCIAL_OPS_DATA_DIR/Content/Logs/Research-YYYY-MM-DD.md` (producer: Researcher; consumers: Content Specialist, Analyst)
  - `$SOCIAL_OPS_DATA_DIR/Content/Logs/Content-YYYY-MM-DD.md` (producer: Content Specialist; consumer: Analyst)
  - `$SOCIAL_OPS_DATA_DIR/Content/Logs/Writer-YYYY-MM-DD.md` (producer: Writer; consumer: Analyst)
  - `$SOCIAL_OPS_DATA_DIR/Content/Logs/Poster-YYYY-MM-DD.md` (producer: Poster; consumer: Analyst)
  - `$SOCIAL_OPS_DATA_DIR/Content/Logs/Responder-YYYY-MM-DD.md` (producer: Responder; consumer: Analyst)
  - `$SOCIAL_OPS_DATA_DIR/Content/Logs/Analysis-YYYY-WW.md` (producer: Analyst; consumers: Content Specialist, Researcher)

- Submolt lifecycle artifacts:
  - `$SOCIAL_OPS_DATA_DIR/Submolts/Primary.md` (producers: Content Specialist; consumers: Scout, Researcher, Analyst)
  - `$SOCIAL_OPS_DATA_DIR/Submolts/Candidates.md` (producers: Scout, Researcher; consumer: Content Specialist)
  - `$SOCIAL_OPS_DATA_DIR/Submolts/Retired.md` (producer: Content Specialist; consumer: Analyst)

- Memory artifacts:
  - `$SOCIAL_OPS_DATA_DIR/Content/Memory/writer.md` (producer/consumer: Writer; long-term creative memory)
  - `$SOCIAL_OPS_DATA_DIR/Content/Memory/writer-YYYY-MM-DD.md` (producer: Writer; consumer: Writer on subsequent runs)

- Runtime state artifacts:
  - `{baseDir}/../state/comment-state.json` (producer/consumer: Responder)

## Notes

- Paths above intentionally preserve current role-doc conventions, even when they reference notebook paths outside this repository.
- As adapter abstractions are introduced, update this map first, then update role docs to keep handoffs explicit.
