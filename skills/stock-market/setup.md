# Setup — Stock Market

Read this when `~/stock-market/` is missing or empty.

## First-Run Transparency

Tell the user what can be created locally:
- Workspace path: `~/stock-market/`
- Decision memory: `~/stock-market/memory.md`
- Optional planning files for watchlists, briefings, and risk rules

Create files only after user confirmation.

## First Conversation Flow

### 1. Integration preference
Ask once how this skill should activate:
- Automatically when the user discusses stock market analysis, watchlists, or trade planning
- Only when explicitly requested

Store this decision in `Status.integration` inside `memory.md`.

### 2. Situation mapping
Collect minimum context before recommendations:
- Trading horizon (intraday, swing, long-term)
- Preferred instruments (single stocks, ETFs, sectors)
- Risk tolerance and max drawdown limits
- Tools already used (broker, screener, research workflow)

### 3. Scope the immediate objective
Clarify the single priority for this session:
- Build watchlist
- Validate a specific ticker thesis
- Prepare pre-market or post-market briefing
- Review completed trades and improve rules

Then execute only that objective with clear next steps.

## Allowed Learning

Store only explicit user information that improves future decisions:
- Confirmed horizon and risk limits
- Approved setup filters and catalyst preferences
- Past mistakes and rule updates the user agrees to keep

Do not infer hidden preferences from passive behavior.

## Boundaries

- Keep local files inside `~/stock-market/`
- Do not place real orders or connect brokers automatically
- Ask before creating or modifying any local planning file
