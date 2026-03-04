# Brief Templates

_Standard templates for dispatching tasks to agents. Leader reads this before composing briefs._

---

## Universal Structure (All Agents)

### Required Fields (every brief must have)

```markdown
**Task ID:** T-{YYYYMMDD}-{HHMM}
**Callback to:** {Leader's current session key — agent MUST callback to this session when done}

**Task:** [one-line description]

**Acceptance Criteria:**
- [ ] [verifiable condition 1]
- [ ] [verifiable condition 2]
- [ ] ...

**Execution Boundary:**
- Deliver: [what to report back]
- DO NOT: [specific actions that require Leader confirmation]
```

### Optional Fields (include when relevant)

```markdown
**Context:**
- Spec: [file path or link]
- Prior output: [file path from previous agent]
- Related files: [shared/ paths, brand profile, etc.]

**Brand Scope:** {brand_id} — read `shared/brands/{brand_id}/profile.md`

**Dependencies:**
- Requires output from: [agent name] — [what output]
- Input files: [paths]

**Priority:** normal | urgent | low
- urgent: owner is actively waiting, prioritize speed
- normal: standard turnaround
- low: no rush, quality over speed

**Deadline:** [expected completion time or "no deadline"]

**Reference:**
- Spec doc: [path]
- Reference images: [paths]
- Prior conversation context: [summary]
```

---

## Agent-Specific Templates

### Engineer

```markdown
**Task:** [description]

**Context:**
- Spec: [path]
- Existing code: [paths]
- Dependencies/framework: [e.g., Node.js, Python, Vue]

**Requirements:**
1. [specific requirement]
2. [specific requirement]

**Acceptance Criteria:**
- [ ] [functional criterion]
- [ ] [performance criterion if applicable]
- [ ] [error handling: what happens when X fails]

**Testing:**
- [ ] [test case 1]
- [ ] [edge case: empty input, malformed data, etc.]
- [ ] [integration: works with existing system]

**Output:**
- Code location: [directory path]
- README with setup/run instructions
- List of modified/created files in report

**Execution Boundary:**
- Deliver: code + test results + file list
- DO NOT: push to git, deploy, install global packages, modify files outside specified directory
- Wait for Leader review before any external action
```

### Designer

```markdown
**Task:** [description]

**Context:**
- Brand: {brand_id} — read `shared/brands/{brand_id}/profile.md` for visual identity
- Reference images: [local paths or URLs]

**Visual Spec:**
- Dimensions: [WxH px]
- Format: [PNG/JPG/sprite sheet]
- Style: [pixel art / photo-realistic / flat design / etc.]
- Color palette: [specific colors or "follow brand profile"]
- Resolution: [1x / 2x / specific DPI]

**Acceptance Criteria:**
- [ ] Matches specified dimensions and format
- [ ] Consistent with brand visual identity
- [ ] [specific visual requirement]

**Output:**
- Save to: ~/.openclaw/media/generated/[path]
- Report back with exact file path(s)

**Execution Boundary:**
- Deliver: image files + file paths
- If generation fails or quality is low, report [BLOCKED] or [LOW_CONFIDENCE] with explanation
```

### Researcher

```markdown
**Task:** [research question]

**Scope:**
- Depth: overview | standard | deep-dive
- Timeframe: [e.g., last 6 months, current state]
- Geography: [e.g., Thailand market, global]
- Sources: [academic / industry / social / all]

**Context:**
- Brand: {brand_id} (if brand-related)
- Shared knowledge: [relevant shared/ paths]
- Prior research: [paths to previous findings]

**Acceptance Criteria:**
- [ ] Answers the core research question
- [ ] Sources cited
- [ ] Actionable insights highlighted
- [ ] [specific data points needed]

**Output Format:**
- Markdown report with structured sections
- Key findings summary at top
- Source citations throughout

**Execution Boundary:**
- Deliver: research report
- Use [KB_PROPOSE] for any domain knowledge worth persisting
```

### Content

```markdown
**Task:** [description]

**Brand Scope:** {brand_id} — read profile.md + content-guidelines.md

**Content Spec:**
- Platform: [Facebook / Instagram / TikTok / blog]
- Format: [post / caption / article / ad copy]
- Language: [from brand profile, e.g., Thai]
- Length: [word/character limit or range]
- Variants: [A/B versions needed? how many?]

**Context:**
- Research input: [path to researcher output, if available]
- Product/topic focus: [specific product or theme]
- Campaign context: [if part of larger campaign]

**Acceptance Criteria:**
- [ ] Matches brand voice and tone
- [ ] Correct language and platform conventions
- [ ] Within specified length
- [ ] [specific messaging requirement]

**Output:**
- Final copy in markdown, clearly formatted
- Hashtag recommendations if applicable

**Execution Boundary:**
- Deliver: copy text
- DO NOT: publish to any platform
- Signal [NEEDS_INFO] if research input is insufficient
```

### Operator

```markdown
**Task:** [description]

**Execution Plan:**
1. [Step 1 — specific action]
2. [Step 2 — specific action]
3. ...

**Context:**
- Target platform/URL: [URL]
- Login: [credential reference or "already logged in"]
- Brand: {brand_id} (if applicable)

**Expected Outcome:**
- [What the screen should show when done]
- [What data to extract, if applicable]

**Acceptance Criteria:**
- [ ] [specific verifiable outcome]
- [ ] Screenshot captured as evidence (if applicable)

**Output:**
- Report: what was done, step by step
- Screenshots if applicable
- Extracted data in specified format

**Execution Boundary:**
- DO NOT: publish content, submit forms, delete data, make purchases — unless explicitly instructed per step
- If unexpected screen/error appears, stop and report immediately
```

### Reviewer

```markdown
**Review Task:** [what to review]

**Deliverable:**
- [Path to content/code being reviewed]
- [Original brief — attached or path]

**Review Standards:**
- Brand alignment (read `shared/brands/{brand_id}/profile.md`)
- Brief compliance — does output meet acceptance criteria?
- [Technical correctness / audience fit / factual accuracy — as applicable]

**Prior Context:**
- Revision round: [1st / 2nd / rework after feedback]
- Previous feedback: [summary if applicable]

**Output:**
- [APPROVE] or [REVISE]
- Specific, actionable feedback (shorter than the deliverable)
- Max 2 review rounds
```

---

## Rework Brief (Revision Request)

_Use this template when sending rework/revision requests to agents after quality review._

```markdown
**Task ID:** T-{YYYYMMDD}-{HHMM}
**Callback to:** {Leader's current session key}
**Round:** {1/2 or 2/2}

**[REVISION REQUEST]**

**What was delivered:** {one-line summary of agent's output}

**Issues found:**
1. {specific issue with concrete example}
2. {specific issue with concrete example}

**Expected fix:**
- [ ] {verifiable correction 1}
- [ ] {verifiable correction 2}

**Context:** {any additional info agent needs — original brief reference, updated requirements, reviewer feedback if Path B}
```

---

## Execution Boundary — Common Examples

| Agent | Common boundaries |
|-------|------------------|
| Engineer | No git push, no deploy, no global installs, no file changes outside scope |
| Designer | Deliver files only, report [BLOCKED] if generation fails |
| Researcher | Report only, use [KB_PROPOSE] for knowledge updates |
| Content | Text delivery only, no publishing |
| Operator | No publishing, no form submission, no deletion without explicit per-step instruction |
| Reviewer | Read-only, no modifications to deliverable |

These are defaults. Each brief may override based on task context (e.g., owner pre-approved a push → brief can say "push allowed after tests pass").

---

_Version: 2.1 | Updated: 2026-03-04 — Added Rework Brief template_
