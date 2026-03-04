---
name: agent-analytics
description: "Web analytics platform that AI agents can query via CLI. Track page views, custom events, run A/B experiments, analyze funnels, retention cohorts, and traffic heatmaps. Use when the user needs web analytics, visitor tracking, event tracking, conversion optimization, growth insights, A/B testing, or wants to add analytics to their website or app. Also available as an MCP server at mcp.agentanalytics.sh."
version: 3.7.0
author: dannyshmueli
license: MIT
repository: https://github.com/Agent-Analytics/agent-analytics-mcp
homepage: https://agentanalytics.sh
compatibility: Requires npx and an Agent Analytics API key (AGENT_ANALYTICS_API_KEY). Sign up at agentanalytics.sh.
tags:
  - analytics
  - tracking
  - web
  - events
  - experiments
  - live
metadata:
  openclaw:
    requires:
      env:
        - AGENT_ANALYTICS_API_KEY
      anyBins:
        - npx
    primaryEnv: AGENT_ANALYTICS_API_KEY
---

# Agent Analytics — Stop juggling dashboards. Let your agent do it.

You are adding analytics tracking using Agent Analytics — the analytics platform your AI agent can actually use. Built for developers who ship lots of projects and want their AI agent to track, analyze, experiment, and optimize across all of them.

## Philosophy

You are NOT Mixpanel. Don't track everything. Track only what answers: **"Is this project alive and growing?"**

For a typical site, that's 3-5 custom events max on top of automatic page views.

## First-time setup

**Get an API key:** Sign up at [agentanalytics.sh](https://agentanalytics.sh) and generate a key from the dashboard. Alternatively, self-host the open-source version from [GitHub](https://github.com/Agent-Analytics/agent-analytics).

If the project doesn't have tracking yet:

```bash
# 1. Login (one time — uses your API key)
npx @agent-analytics/cli login --token aak_YOUR_API_KEY

# 2. Create the project (returns a project write token)
npx @agent-analytics/cli create my-site --domain https://mysite.com

# 3. Add the snippet (Step 1 below) using the returned token
# 4. Deploy, click around, verify:
npx @agent-analytics/cli events my-site
```

The `create` command returns a **project write token** — use it as `data-token` in the snippet below. This is separate from your API key (which is for reading/querying).

## Step 1: Add the tracking snippet

The `create` command returns a tracking snippet with your project token — add it before `</body>`. It auto-tracks `page_view` events with path, referrer, browser, OS, device, screen size, and UTM params. You do NOT need to add custom page_view events.

## Step 1b: Discover existing events (existing projects)

If tracking is already set up, check what events and property keys are already in use so you match the naming:

```bash
npx @agent-analytics/cli properties-received PROJECT_NAME
```

This shows which property keys each event type uses (e.g. `cta_click → id`, `signup → method`). Match existing naming before adding new events.

## Step 2: Add custom events to important actions

Use `onclick` handlers on the elements that matter:

```html
<a href="..." onclick="window.aa?.track('EVENT_NAME', {id: 'ELEMENT_ID'})">
```

The `?.` operator ensures no error if the tracker hasn't loaded yet.

### Standard events for 80% of SaaS sites

Pick the ones that apply. Most sites need 2-4:

| Event | When to fire | Properties |
|-------|-------------|------------|
| `cta_click` | User clicks a call-to-action button | `id` (which button) |
| `signup` | User creates an account | `method` (github/google/email) |
| `login` | User returns and logs in | `method` |
| `feature_used` | User engages with a core feature | `feature` (which one) |
| `checkout` | User starts a payment flow | `plan` (free/pro/etc) |
| `error` | Something went wrong visibly | `message`, `page` |

### What to track as `cta_click`

Only buttons that indicate conversion intent:
- "Get Started" / "Sign Up" / "Try Free" buttons
- "Upgrade" / "Buy" / pricing CTAs
- Primary navigation to signup/dashboard
- "View on GitHub" / "Star" (for open source projects)

### What NOT to track
- Every link or button (too noisy)
- Scroll depth (not actionable)
- Form field interactions (too granular)
- Footer links (low signal)

### Property naming rules

- Use `snake_case`: `hero_get_started` not `heroGetStarted`
- The `id` property identifies WHICH element: short, descriptive
- Name IDs as `section_action`: `hero_signup`, `pricing_pro`, `nav_dashboard`
- Don't encode data the page_view already captures (path, referrer, browser)

## Step 2a: Measure time-on-page

Add `data-heartbeat="15"` to the tracking snippet to get accurate time-on-page:

```html
<script defer src="https://api.agentanalytics.sh/tracker.js"
  data-project="my-site" data-token="aat_..."
  data-heartbeat="15"></script>
```

**Why it matters:** Without this, time-on-page is just the gap between two page views. If someone reads a 10-minute article and closes the tab, the recorded time is 0 seconds. This fixes it by measuring actual engaged time.

**How it works:**
- The tracker silently counts seconds while the tab is visible (no events sent during)
- When the user leaves the page (tab hidden, closes tab, or SPA navigation), the `time_on_page` property is added to the original `page_view` event — zero extra events
- The timer pauses when the tab is hidden and resumes when visible
- Minimum interval is 15 seconds (values below 15 are clamped)
- Works with SPA navigation — each page gets its own time_on_page

**Querying time-on-page data:**

```bash
# Pages with time_on_page data
npx @agent-analytics/cli query my-site \
  --filter '[{"field":"event","op":"eq","value":"page_view"},{"field":"properties.time_on_page","op":"gt","value":"0"}]' \
  --group-by properties.path --metrics event_count,unique_users
```

## Step 2b: Run A/B experiments (Pro)

Experiments let you test which variant of a page element converts better. The full lifecycle is API-driven — no dashboard UI needed.

### Creating an experiment

```bash
npx @agent-analytics/cli experiments create my-site \
  --name signup_cta --variants control,new_cta --goal signup
```

### Implementing variants

**Declarative (recommended):** Use `data-aa-experiment` and `data-aa-variant-{key}` HTML attributes. Original content is the control. The tracker swaps text for assigned variants automatically.

```html
<h1 data-aa-experiment="signup_cta" data-aa-variant-new_cta="Start Free Trial">Sign Up</h1>
```

**Programmatic (complex cases):** Use `window.aa?.experiment(name, variants)` — deterministic, same user always gets same variant.

Exposure events (`$experiment_exposure`) are tracked automatically once per session. Track the goal event normally: `window.aa?.track('signup', {method: 'github'})`.

### Checking results

```bash
npx @agent-analytics/cli experiments get exp_abc123
```

Returns Bayesian `probability_best`, `lift`, and a `recommendation`. The system needs ~100 exposures per variant before results are significant.

### Managing experiments

```bash
# Pause (stops assigning new users)
npx @agent-analytics/cli experiments pause exp_abc123

# Resume
npx @agent-analytics/cli experiments resume exp_abc123

# Complete with a winner
npx @agent-analytics/cli experiments complete exp_abc123 --winner new_cta

# Delete
npx @agent-analytics/cli experiments delete exp_abc123
```

### Forcing variants via URL param

Force a specific variant with `?aa_variant_<experiment_name>=<variant_key>`. Useful for ad landing pages that should always show the matching headline, QA testing, or sharing a specific variant.

```
https://yoursite.com/pricing/?aa_variant_signup_cta=new_cta&utm_campaign=new-cta-ad
```

- The variant must exist in the experiment config — invalid values fall through to normal hash assignment
- Works with both declarative and programmatic experiments
- Exposure events include `forced: true` so you can filter them in analytics

### Best practices
- Name experiments with snake_case: `signup_cta`, `pricing_layout`, `hero_copy`
- Use 2 variants (A/B) unless you have high traffic — more variants need more data
- Set a clear `goal_event` that maps to a business outcome (`signup`, `purchase`, not `page_view`)
- Let experiments run until `sufficient_data: true` before picking a winner
- Complete the experiment when done: `experiments complete <id> --winner new_cta`

## Step 2c: Track JS errors

Add `data-track-errors="true"` to the tracking snippet to automatically capture JavaScript errors:

```html
<script defer src="https://api.agentanalytics.sh/tracker.js"
  data-project="my-site" data-token="aat_..."
  data-track-errors="true"></script>
```

**What it tracks:**
- Uncaught exceptions (`window.addEventListener('error')`)
- Unhandled promise rejections (`window.addEventListener('unhandledrejection')`)
- Each error becomes a `$error` event with `{ message, source, line, col }`

**Safety features:**
- Max 5 errors per page view (prevents runaway logging)
- Deduplicates by message+source+line (same error on same line only tracked once)
- Resets on SPA navigation
- Does not interfere with other error handlers (additive, not overwriting)
- No stack traces (keeps payloads small)

**Querying error data:**

```bash
# Recent errors
npx @agent-analytics/cli events my-site --event '$error' --days 7

# Error breakdown by message
npx @agent-analytics/cli breakdown my-site --property message --event '$error'

# Errors per source file
npx @agent-analytics/cli query my-site \
  --filter '[{"field":"event","op":"eq","value":"$error"}]' \
  --group-by properties.source --metrics event_count
```

## Step 2d: Set global properties

Use `aa.set()` to attach properties to ALL subsequent events without repeating them in every `track()` call:

```js
// After login, tag all future events with the user's plan
window.aa?.set({ plan: 'pro', team: 'acme' });

// These events now include plan='pro' and team='acme' automatically
window.aa?.track('feature_used', { feature: 'export' });
window.aa?.track('cta_click', { id: 'upgrade' });
```

**How it works:**
- Merge order: auto-collected < UTM < global (set) < event-specific. Event-specific properties always win.
- Multiple `set()` calls merge — `set({a:1}); set({b:2})` results in `{a:1, b:2}`
- Remove a key: `aa.set({ plan: null })`
- In-memory only — does not persist across page reloads (use `identify()` for cross-session user identity)
- Zero overhead when not used

**When to use:**
- After login/signup: `aa.set({ plan: user.plan, role: user.role })`
- Feature flags: `aa.set({ feature_flag_x: 'variant_b' })`
- Any context that applies to all events for the rest of the session

## Step 2e: Consent management (GDPR/CCPA)

For sites that require user consent before tracking, use the consent management API:

```html
<!-- Add data-require-consent to the script tag -->
<script defer data-project="mysite" data-token="aat_..." data-require-consent="true"
  src="https://api.agentanalytics.sh/tracker.js"></script>
```

```js
// Events buffer in-memory until consent is granted — nothing is sent
// When the user accepts cookies/tracking:
window.aa?.grantConsent();   // flushes buffer + persists to localStorage

// If the user declines or revokes:
window.aa?.revokeConsent();  // discards buffer + blocks future sends
```

**How it works:**
- `data-require-consent="true"` or `aa.requireConsent()` → events queue in-memory but never send
- `aa.grantConsent()` → flushes buffered events, saves `aa_consent=granted` in localStorage, normal tracking resumes
- `aa.revokeConsent()` → clears buffer, removes localStorage consent, blocks sends
- On next page load, prior consent auto-detected from localStorage — no re-consent needed
- Pre-consent events are preserved (not discarded) so nothing is lost

**Programmatic alternative** (no script attribute needed):
```js
// Call before any events are tracked
window.aa?.requireConsent();

// Later, when user consents
window.aa?.grantConsent();
```

## Step 2f: Performance timing

Collect page load performance metrics automatically:

```html
<script defer data-project="mysite" data-token="aat_..."
  data-track-performance="true"
  src="https://api.agentanalytics.sh/tracker.js"></script>
```

After `window.load`, the tracker reads the Navigation Timing API and merges these properties into the `page_view` event (no extra events stored):

| Property | What it measures |
|----------|------------------|
| `perf_dns` | DNS lookup (ms) |
| `perf_tcp` | TCP handshake (ms) |
| `perf_ttfb` | Time to first byte (ms) |
| `perf_dom_interactive` | DOM ready for interaction (ms) |
| `perf_dom_complete` | DOM fully loaded (ms) |
| `perf_load` | Full page load (ms) |

Query performance data:
```bash
npx @agent-analytics/cli events mysite --event page_view --days 7
# Look for perf_dns, perf_ttfb, perf_load in event properties

npx @agent-analytics/cli breakdown mysite --property perf_ttfb --event page_view
# See TTFB distribution across page views
```

Only fires once per page load — SPA navigations via pushState don't create new Navigation Timing entries.

## Step 3: Test immediately

After adding tracking, verify it works:

```bash
# Option A: Browser console on your site:
window.aa.track('test_event', {source: 'manual_test'})

# Option B: Click around, then check:
npx @agent-analytics/cli events PROJECT_NAME

# Events appear within seconds.
```

## Querying the data

All commands use `npx @agent-analytics/cli`. Your agent uses the CLI directly — no curl needed.

### Ad-hoc queries — talk to your analytics

The `query` command is the most powerful tool. It answers any analytics question by combining metrics, filters, grouping, and date ranges. **Use this when pre-built commands don't answer the question.**

```bash
# "How many signups from Germany this week?"
npx @agent-analytics/cli query my-site \
  --filter '[{"field":"event","op":"eq","value":"signup"},{"field":"country","op":"eq","value":"DE"}]' \
  --metrics event_count,unique_users --days 7

# "Which events contain 'click' in the name?"
npx @agent-analytics/cli query my-site \
  --filter '[{"field":"event","op":"contains","value":"click"}]' \
  --group-by event

# "Traffic breakdown by country, top 10"
npx @agent-analytics/cli query my-site \
  --group-by country --metrics event_count,unique_users --limit 10

# "Daily unique users for the last 30 days"
npx @agent-analytics/cli query my-site \
  --metrics unique_users --group-by date --days 30
```

**Filter operators:** `eq`, `neq`, `gt`, `lt`, `gte`, `lte`, `contains`
**Filterable fields:** `event`, `user_id`, `date`, `country`, `session_id`, `timestamp`, and any `properties.*` field
**Group by:** `event`, `date`, `user_id`, `session_id`, `country`
**Metrics:** `event_count`, `unique_users`, `session_count`, `bounce_rate`, `avg_duration`

### CLI reference

```bash
# Setup
npx @agent-analytics/cli login --token aak_YOUR_KEY    # Save API key (one time)
npx @agent-analytics/cli projects                       # List all projects
npx @agent-analytics/cli create my-site --domain https://mysite.com  # Create project

# Real-time
npx @agent-analytics/cli live                           # Live terminal dashboard across ALL projects
npx @agent-analytics/cli live my-site                   # Live view for one project

# Analytics
npx @agent-analytics/cli stats my-site --days 7         # Overview: events, users, daily trends
npx @agent-analytics/cli insights my-site --period 7d   # Period-over-period comparison
npx @agent-analytics/cli breakdown my-site --property path --event page_view --limit 10  # Top pages/referrers/UTM
npx @agent-analytics/cli pages my-site --type entry     # Landing page performance & bounce rates
npx @agent-analytics/cli sessions-dist my-site          # Session engagement histogram
npx @agent-analytics/cli heatmap my-site                # Peak hours & busiest days
npx @agent-analytics/cli events my-site --days 30       # Raw event log
npx @agent-analytics/cli sessions my-site               # Individual session records
npx @agent-analytics/cli properties my-site             # Discover event names & property keys
npx @agent-analytics/cli properties-received my-site    # Property keys per event type (sampled)
npx @agent-analytics/cli query my-site --metrics event_count,unique_users --group-by date  # Flexible query
npx @agent-analytics/cli query my-site --group-by country --metrics event_count,unique_users  # Events per country
npx @agent-analytics/cli query my-site --filter '[{"field":"country","op":"eq","value":"US"}]'  # Filter by country
npx @agent-analytics/cli query my-site --filter '[{"field":"event","op":"contains","value":"click"}]' --group-by event  # Substring match
npx @agent-analytics/cli funnel my-site --steps "page_view,signup,purchase"  # Funnel drop-off analysis
npx @agent-analytics/cli funnel my-site --steps "page_view,signup" --breakdown country  # Funnel segmented by country
npx @agent-analytics/cli retention my-site --period week --cohorts 8        # Cohort retention analysis

# A/B experiments (pro)
npx @agent-analytics/cli experiments list my-site
npx @agent-analytics/cli experiments create my-site --name signup_cta --variants control,new_cta --goal signup
npx @agent-analytics/cli experiments get exp_abc123
npx @agent-analytics/cli experiments complete exp_abc123 --winner new_cta

# Account
npx @agent-analytics/cli whoami                         # Show account & tier
npx @agent-analytics/cli revoke-key                     # Rotate API key
```

**Key flags**:
- `--days <N>` — lookback window (default: 7; for `stats`, `events`)
- `--limit <N>` — max rows returned (default: 100)
- `--since <date>` — ISO date cutoff (`properties-received` only)
- `--period <P>` — comparison period: `1d`, `7d`, `14d`, `30d`, `90d` (`insights`) or cohort grouping: `day`, `week`, `month` (`retention`)
- `--property <key>` — property key to group by (`breakdown`, required)
- `--event <name>` — filter by event name (`breakdown`) or first-seen event filter (`retention`)
- `--returning-event <name>` — what counts as "returned" (`retention`, defaults to same as `--event`)
- `--cohorts <N>` — number of cohort periods, 1-30 (`retention`, default: 8)
- `--filter <json>` — JSON array of filters for `query` (e.g. `'[{"field":"country","op":"eq","value":"US"}]'`). Operators: `eq`, `neq`, `gt`, `lt`, `gte`, `lte`, `contains`
- `--group-by <fields>` — comma-separated group_by fields: `event`, `date`, `user_id`, `session_id`, `country` (`query`)
- `--type <T>` — page type: `entry`, `exit`, `both` (`pages` only, default: entry)
- `--steps <csv>` — comma-separated event names, 2-8 steps max (`funnel`, required)
- `--window <N>` — conversion window in hours (`funnel`, default: 168) or live time window in seconds (`live`, default: 60)
- `--count-by <field>` — `user_id` or `session_id` (`funnel` only)
- `--breakdown <key>` — segment funnel by a property (e.g. `country`, `variant`) — extracted from step 1 events (`funnel` only)
- `--breakdown-limit <N>` — max breakdown groups, 1-50 (`funnel`, default: 10)
- `--interval <N>` — live refresh in seconds (default: 5)

### The `live` command

`npx @agent-analytics/cli live` opens a real-time TUI dashboard that refreshes every 5 seconds. It shows active visitors, sessions, and events/min across all your projects, plus top pages and recent events. Note: this is an interactive terminal UI — it clears the screen on each refresh, so it works best when run directly in a terminal rather than captured as output.

## Which endpoint for which question

Match the user's question to the right call(s):

| User asks | Call | Why |
|-----------|------|-----|
| "How's my site doing?" | `insights` + `breakdown` + `pages` (parallel) | Full weekly picture in one turn |
| "Is anyone visiting right now?" | `live` | Real-time visitors, sessions, events across all projects |
| "Is anyone visiting?" | `insights --period 7d` | Quick alive-or-dead check |
| "What are my top pages?" | `breakdown --property path --event page_view` | Ranked page list with unique users |
| "Where's my traffic coming from?" | `breakdown --property referrer --event page_view` | Referrer sources |
| "Which landing page is best?" | `pages --type entry` | Bounce rate + session depth per page |
| "Are people actually engaging?" | `sessions-dist` | Bounce vs engaged split |
| "When should I deploy/post?" | `heatmap` | Find low-traffic windows or peak hours |
| "Give me a summary of all projects" | `live` or loop: `projects` then `insights` per project | Multi-project overview |
| "Which CTA converts better?" | `experiments create` + implement + `experiments get <id>` | Full A/B test lifecycle |
| "Where do users drop off?" | `funnel --steps "page_view,signup,purchase"` | Step-by-step conversion with drop-off rates |
| "Which variant converts better through the funnel?" | `funnel --steps "page_view,signup" --breakdown variant` | Funnel segmented by experiment variant |
| "Are users coming back?" | `retention --period week --cohorts 8` | Cohort retention: % returning per period |
| "How many signups from Germany?" | `query --filter '[{"field":"event","op":"eq","value":"signup"},{"field":"country","op":"eq","value":"DE"}]'` | Ad-hoc filter by event + country |
| "Events per country" | `query --group-by country --metrics event_count,unique_users` | Country breakdown |
| "Pages with pricing in the URL?" | `query --filter '[{"field":"properties.path","op":"contains","value":"pricing"}]' --group-by event` | Substring match on properties |
| "How many sessions this week?" | `query --metrics session_count --days 7` | Count distinct sessions |

For any "how is X doing" question, **always call `insights` first** — it's the single most useful endpoint. For real-time "who's on the site right now", use `live`. For any specific question that the pre-built commands don't directly answer (filtering by country, substring matching, combining multiple filters), use `query`.

## Analyze, don't just query

Don't return raw numbers. Interpret them. Here's how to turn each endpoint's response into something useful.

### `/insights` → The headline

API returns metrics with `current`, `previous`, `change`, `change_pct`, and a `trend` field.

**How to interpret:**
- `change_pct > 10` → "Growing" — call it out positively
- `change_pct` between -10 and 10 → "Stable" — mention it's steady
- `change_pct < -10` → "Declining" — flag it, suggest investigating
- `bounce_rate` current vs previous → say "improved" (went down) or "worsened" (went up)
- `avg_duration` → convert ms to seconds: `Math.round(value / 1000)`
- Previous period is all zeros → say "new project, no prior data to compare"

**Example output:**
```
This week vs last: 173 events (+22%), 98 users (+18%).
Bounce rate: 87% (up from 82% — getting worse).
Average session: 24s. Trend: growing.
```

### `/breakdown` → The ranking

API returns `values: [{ value, count, unique_users }]` sorted by count DESC.

**How to interpret:**
- Top 3-5 values is enough — don't dump the full list
- Show the `unique_users` too — 100 events from 2 users is very different from 100 events from 80 users
- Use `total_with_property / total_events` to note coverage: "155 of 155 page views have a path"
- For referrers: group "(direct)" / empty as direct traffic

**Example output:**
```
Top pages: / (98 views, 75 users), /pricing (33 views, 25 users), /docs (19 views, 4 users).
The /docs page has high repeat visits (19 views, 4 users) — power users.
```

### `/pages` → Landing page quality

API returns `entry_pages: [{ page, sessions, bounces, bounce_rate, avg_duration, avg_events }]`.

**How to interpret:**
- `bounce_rate` > 0.7 → "high bounce, needs work above the fold"
- `bounce_rate` < 0.3 → "strong landing page"
- `avg_duration` → convert ms to seconds; < 10s is concerning, > 60s is great
- `avg_events` → pages/session; 1.0 means everyone bounces, 3+ means good engagement
- Compare pages: "Your /pricing page converts 3× better than your homepage"

**Example output:**
```
Best landing page: /pricing — 14% bounce, 62s avg session, 4.1 pages/visit.
Worst: /blog/launch — 52% bounce, 18s avg. Consider a stronger CTA above the fold.
```

### `/sessions/distribution` → Engagement shape

API returns `distribution: [{ bucket, sessions, pct }]`, `engaged_pct`, `median_bucket`.

**How to interpret:**
- `engaged_pct` is the key number — sessions ≥30s as a percentage of total
- `engaged_pct` < 10% → "Most visitors leave immediately — focus on first impressions"
- `engaged_pct` 10-30% → "Moderate engagement, room to improve"
- `engaged_pct` > 30% → "Good engagement"
- If 80%+ is in the "0s" bucket, the site has a bounce problem
- If there's a healthy spread across buckets, engagement is genuine

**Example output:**
```
88% of sessions bounce instantly (0s). Only 6% stay longer than 30s.
The few who do engage stay 3-10 minutes — the content works, but first impressions don't.
```

### `/heatmap` → Timing

API returns `heatmap: [{ day, day_name, hour, events, users }]`, `peak`, `busiest_day`, `busiest_hour`.

**How to interpret:**
- `peak` is the single busiest slot — mention day + hour + timezone caveat (times are UTC)
- `busiest_day` → "Schedule blog posts/launches on this day"
- `busiest_hour` → "This is when your audience is online"
- Low-traffic windows → "Deploy during Sunday 3 AM UTC to minimize user impact"
- Weekend vs weekday split → tells you if audience is B2B (weekdays) or B2C (weekends)

**Example output:**
```
Peak: Friday at 11 PM UTC (35 events, 33 users). Busiest day overall: Sunday.
Traffic is heaviest on weekends — your audience browses on personal time.
Deploy on weekday mornings for minimal disruption.
```

### `/funnel` → Where users drop off

CLI: `funnel my-site --steps "page_view,signup,purchase"`. API: `POST /funnel` with JSON body.

API returns `steps: [{ step, event, users, conversion_rate, drop_off_rate, avg_time_to_next_ms }]` and `overall_conversion_rate`.

**How to interpret:**
- Each step shows how many users progressed from the previous step
- `conversion_rate` is step-to-step (step 2 users / step 1 users)
- `drop_off_rate` is 1 - conversion_rate at each step
- The biggest `drop_off_rate` is the bottleneck — focus optimization there
- `avg_time_to_next_ms` shows how long users take between steps (convert to hours/minutes)
- `overall_conversion_rate` is end-to-end (last step users / first step users)

**Options:**
- `--steps "event1,event2,event3"` — 2-8 step events (required)
- `--window <hours>` — max time from step 1 to last step (default: 168 = 7 days)
- `--since <days>` — lookback period, e.g. `30d` (default: 30d)
- `--count-by <field>` — `user_id` (default) or `session_id`
- `--breakdown <property>` — segment funnel by a property (e.g. `country`, `variant`). Property is extracted from step 1 events. Returns overall + per-group results.
- `--breakdown-limit <N>` — max groups returned (default: 10, max: 50). Groups ordered by step 1 users descending.

**Breakdown use case — A/B experiments:** `funnel my-site --steps "page_view,signup" --breakdown variant` shows which experiment variant converts better through the funnel.

**API-only: per-step filters** — each step can have a `filters` array with `{ property, op, value }` (ops: `eq`, `neq`, `contains`). Example: filter step 1 to `path=/pricing` to see conversions from the pricing page specifically.

**Example output:**
```
page_view → signup → purchase
  500 users → 80 (16%) → 12 (15%) — 2.4% overall
  Biggest drop-off: page_view → signup (84%). Focus on signup CTA visibility.
  Avg time to signup: 4.2 hours. Avg time to purchase: 2.1 days.
```

### `/retention` → Are users coming back?

CLI: `retention my-site --period week --cohorts 8`. API: `GET /retention?project=X&period=week&cohorts=8`.

By default uses session-based retention — a user is "retained" if they have any return visit (session) in a subsequent period. Pass `--event` to switch to event-based retention.

API returns `cohorts: [{ date, users, retained: [...], rates: [...] }]`, `average_rates: [...]`, and `users_analyzed`.

**How to interpret:**
- Each cohort row = users who first appeared in that period
- `rates[0]` is always 1.0 (100% — the cohort itself)
- `rates[1]` = % who came back the next period — this is the critical number
- Declining rates across offsets is normal; the slope matters more than absolutes
- `average_rates` is weighted by cohort size — larger cohorts count more
- Compare recent cohorts vs older ones: improving rates = product is getting stickier

**Options:**
- `--period <P>` — `day`, `week`, `month` (default: week)
- `--cohorts <N>` — number of cohort periods, 1-30 (default: 8)
- `--event <name>` — first-seen event filter (e.g. `signup`). Switches to event-based retention
- `--returning-event <name>` — what counts as "returned" (defaults to same as `--event`)

**Event-based retention:** Set `--event signup --returning-event purchase` to answer "of users who signed up, what % made a purchase in subsequent weeks?"

**Example output:**
```
Cohort W0 (2026-01-27): 142 users → W1: 45% → W2: 39% → W3: 32%
Cohort W0 (2026-02-03): 128 users → W1: 42% → W2: 36%
Weighted avg: W1 = 44%, W2 = 37%, W3 = 32%
Week-1 retention of 44% is strong — nearly half of new users return.
Slight decline in recent cohorts — investigate onboarding changes.
```

### Weekly summary recipe (3 parallel calls)

Call `insights`, `breakdown --property path --event page_view`, and `pages --type entry` in parallel, then synthesize into one response:

```
Weekly Report — my-site (Feb 8–15 vs Feb 1–8)
Events: 1,200 (+22% ↑)  Users: 450 (+18% ↑)  Bounce: 42% (improved from 48%)
Top pages: /home (523), /pricing (187), /docs (94)
Best landing: /pricing — 14% bounce, 62s avg. Worst: /blog — 52% bounce.
Trend: Growing.
```

### Multi-project overview

For a quick real-time check, use `live` — it shows all projects in one view with active visitors, sessions, and events/min.

For a historical summary, call `projects` to list all projects, then call `insights --period 7d` for each. Present one line per project:

```
my-site         142 views (+23% ↑)  12 signups   healthy
side-project     38 views (-8% ↓)    0 signups   quiet
api-docs          0 views (—)        —            ⚠ inactive since Feb 1
```

Use arrows: `↑` up, `↓` down, `—` flat. Flag anything that needs attention.

### Anomaly detection

Proactively flag — don't wait to be asked:
- **Spike**: any metric >2× its previous period → "unusual surge, check referrers"
- **Drop**: any metric <50% of previous → "significant decline, worth investigating"
- **Dead project**: zero `page_view` events → "⚠ no traffic detected"
- **Errors**: any `error` events in the window → surface the `message` property

### Visualizing results

When reporting to messaging platforms (Slack, Discord, Telegram), raw text tables break. Use companion skills:

- **`table-image-generator`** — render stats as clean table images
- **`chart-image`** — generate line, bar, area, or pie charts from analytics data

## Growth Playbook — How to grow, not just track

Tracking is step one. Growth comes from a **repeatable system**: clear messaging → focused distribution → obsessive tracking → rapid experimentation → learning. Here's how to apply each principle using Agent Analytics.

### Principle 1: Promise clarity

The #1 conversion lever is messaging. If someone lands and has to think hard to understand the value, they're gone.

**What your agent should do:**
- Set up an A/B experiment on the hero headline immediately: `experiments create PROJECT --name hero_headline --variants control,b,c --goal cta_click`
- Test 2-3 headline variations that frame the same value differently
- Use declarative HTML: `data-aa-experiment="hero_headline" data-aa-variant-b="New headline"`
- Check results after ~500 visitors per variant: `experiments get EXP_ID`
- Ship the winner, start testing the subtitle or CTA next

**Rule:** Spend more time testing messaging than adding features. Even the best product won't convert if the value isn't obvious in seconds.

### Principle 2: Track what drives decisions, not everything

Don't be Mixpanel. Track only what answers: **"Is this project alive and growing, and what should I do next?"**

**The essential events (pick 3-5):**

| Event | What it tells you |
|-------|-------------------|
| `cta_click` (with `id`) | Which buttons drive action — your conversion signal |
| `signup` | Are people converting? At what rate? |
| `feature_used` (with `feature`) | Are they finding value after signup? |
| `checkout` | Revenue signal |

**Agent workflow for tracking setup:**
1. Look at the site — identify the 2-3 most important user actions
2. Add tracking on those specific actions (not everything)
3. Verify with `events PROJECT` that data flows
4. Set up a weekly check: `insights PROJECT --period 7d`

**Anti-pattern:** Don't track scroll depth, mouse hovers, every link click, or form field interactions. Noise kills signal.

### Principle 3: Find the activation moment

Conversion doesn't happen at checkout. It happens when the user realizes the product solves their problem — the "aha moment."

**How to find it:**
1. Track key feature interactions: `feature_used` with specific feature names
2. Use `breakdown --property feature --event feature_used` to see which features correlate with retention
3. Check `sessions-dist` — if most sessions are 0s bounces, the landing page is the problem. If sessions are long but signups are low, the activation path is the problem
4. Use `pages --type entry` — compare bounce rates across landing pages to find which first impression works

**What to optimize:**
- Time to first value — how fast does the user get a result?
- Onboarding friction — where do users drop off?
- Feature discovery — are users finding the thing that makes them stay?

### Principle 4: One channel, iterate relentlessly

Don't try to be everywhere. Pick one acquisition channel and go deep.

**How Agent Analytics supports this:**
- `breakdown --property referrer --event page_view` → see where traffic actually comes from
- `breakdown --property utm_source` → track campaign sources
- `insights --period 7d` → week-over-week: is the channel growing?
- Create landing page variants per channel (e.g., `/reddit/`, `/hn/`) and compare with `pages --type entry`

**Agent workflow for channel optimization:**
1. Check referrer breakdown weekly
2. Identify the top-performing channel (highest traffic + lowest bounce)
3. Double down: create content, run experiments on that channel's landing page
4. Ignore channels that aren't working — focus beats breadth

### Principle 5: The autonomous growth loop

This is what makes Agent Analytics different from traditional analytics. Your agent can run the full cycle:

```
Track → Analyze → Experiment → Ship winner → Repeat
```

**The loop in practice:**

1. **Track**: Agent sets up tracking on CTAs and key actions
2. **Analyze**: Weekly `insights` + `breakdown` + `pages` calls → synthesize into a report
3. **Hypothesize**: "Hero headline has 87% bounce — test a clearer value prop"
4. **Experiment**: `experiments create PROJECT --name hero_v2 --variants control,b --goal cta_click`
5. **Monitor**: Check `experiments get EXP_ID` after sufficient traffic
6. **Ship**: `experiments complete EXP_ID --winner b` → deploy the winner
7. **Repeat**: Start the next experiment on the next weakest element

**What to test (in order of impact):**
1. Hero headline — biggest impact on bounce rate
2. CTA button text — directly affects conversion
3. Social proof / trust signals — affects signup confidence
4. Pricing presentation — affects revenue
5. Onboarding flow — affects activation

**Cadence:** One experiment at a time. ~1-2 weeks per test depending on traffic. Don't stack experiments unless traffic is very high (>1000 visitors/day).

### Proactive growth monitoring

Don't wait for the user to ask. If your agent has scheduled checks, proactively flag:

- **Dead project**: 0 events in 7 days → "⚠ PROJECT has no traffic — is it still deployed?"
- **Conversion drop**: `cta_click` rate dropped >20% week-over-week → "Conversion declined — worth investigating"
- **Experiment ready**: An experiment has >100 exposures per variant → "Experiment X has enough data — check results"
- **Experiment winner**: Significance >95% → "Experiment X: Variant B wins with 3.8% vs 2.1%. Ship it?"
- **Traffic spike**: >2× normal → "Unusual traffic surge on PROJECT — check referrers for the source"

## What this skill does NOT do

- No GUI dashboards — your agent IS the dashboard (or use `live` for a real-time TUI)
- No user management or billing
- Funnels and retention are ad-hoc queries (no saved/scheduled reports)
- No PII stored — IP addresses are not logged or retained. Privacy-first by design

## Examples

Track custom events via `window.aa?.track()` (the `?.` ensures no error if tracker hasn't loaded):

```js
window.aa?.track('cta_click', {id: 'hero_get_started'});
window.aa?.track('signup', {method: 'github'});
window.aa?.track('feature_used', {feature: 'create_project'});
window.aa?.track('checkout', {plan: 'pro'});
```
