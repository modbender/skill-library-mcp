# LinkedIn Connect — Browser Automation Workflow

## Setup

```
# For Chrome Relay (Option A — recommended for flagged accounts):
browser action=tabs profile=chrome
→ note the targetId of the LinkedIn tab — reuse it throughout, never open new tabs

# For OpenClaw isolated browser (Option B):
browser action=tabs profile=openclaw
→ note the targetId of the LinkedIn tab — reuse it throughout
```

Use `profile=<PROFILE>` throughout — substitute with `chrome` or `openclaw` based on what the user confirmed in the pre-flight checklist.

---

## ⚠️ Mandatory Between Every Profile — No Exceptions

Always navigate to the feed before loading a new profile. **Never skip this step.** Jumping directly between profile URLs is the primary trigger for LinkedIn's automation detection. This step must happen even if the previous profile loaded fine.

```
browser action=navigate profile=<PROFILE> targetId=<TAB> targetUrl=https://www.linkedin.com/feed/
```

After the feed loads, wait 2–4 seconds (use `browser action=act request={"kind":"wait","timeMs":3000}`) before navigating to the next profile.

---

## Tier 1 — Direct URL

```
browser action=navigate profile=<PROFILE> targetId=<TAB> targetUrl=<PROFILE_URL>
```

- Result URL matches profile path → profile loaded, go to **Connect Step**
- Result URL is `/404/` → go to **Tier 2** (Google Search)

---

## Tier 2 — Google Search

Navigate directly to Google search (do NOT use address bar — stay in the LinkedIn tab via navigate):

```
browser action=navigate profile=<PROFILE> targetId=<TAB> targetUrl=https://www.google.com/search?q=<FirstName>+<LastName>+<Brand>+linkedin
```

Take a compact snapshot. Find the LinkedIn profile URL in results (usually the first organic result).

```
browser action=act request={"kind":"click","ref":"<linkedin-result-ref>"}
```

This lands on their LinkedIn profile — go to **Connect Step**.

**If no trustworthy LinkedIn result found** → go to **Tier 3**

---

## Tier 3 — LinkedIn People Search (last resort)

Navigate to LinkedIn people search:

```
browser action=navigate profile=<PROFILE> targetId=<TAB> targetUrl=https://www.linkedin.com/search/results/people/?keywords=<FirstName>+<LastName>+<Brand>
```

Take a compact snapshot and scan results for the person. Check name + company headline match.

**Option A — Connect inline from search results:**

Some search result cards show a `Connect` button directly. If visible and the person matches:
```
browser action=act request={"kind":"click","ref":"<connect-ref>"}
```
→ go to **Confirm Dialog**

**Option B — No inline Connect, open profile:**

Click the person's name link to navigate to their profile, then go to **Connect Step**.

**If no trustworthy match** → mark `Profile Not Found`, move to next person.

---

## Connect Step — Detecting Status

Take a compact interactive snapshot on the loaded profile:

```
browser action=snapshot compact=true depth=2 interactive=true targetId=<TAB>
```

| What you see | Status | Action |
|---|---|---|
| `Connect` button on profile | Not connected | → Pattern A |
| `Follow` + `Message` + `More actions` (no Connect) | Follow mode | → Pattern B |
| `Message` only, no Follow, no Connect | Already 1st degree | Mark `Already Connected` |
| `Pending` button | Request already sent | Mark `Pending` |
| `Following` button (post-action) | Just sent | Mark `Request Sent` |

---

## Pattern A — Direct Connect Button

```
browser action=act request={"kind":"click","ref":"<connect-button-ref>"}
```
→ go to **Confirm Dialog**

---

## Pattern B — Connect via More Actions

**1. Click More actions:**
```
browser action=act request={"kind":"click","ref":"<more-actions-ref>"}
```

**2. Get dropdown items using selector (most reliable):**
```
browser action=snapshot compact=false depth=3 selector=".artdeco-dropdown__content--is-open" targetId=<TAB>
```

This exposes the dropdown buttons directly. Look for `"Invite [Name] to connect"`.

**3. Click it:**
```
browser action=act request={"kind":"click","ref":"<invite-ref>"}
```
→ go to **Confirm Dialog**

**If dropdown has no Invite/Connect option** → mark `Follow Only`

---

## Confirm Dialog

After clicking Connect or Invite, LinkedIn shows a modal. Take snapshot:

```
browser action=snapshot compact=true depth=2 interactive=true
```

Buttons: `Dismiss` | `Add a note` | `Send without a note`

```
browser action=act request={"kind":"click","ref":"<send-without-note-ref>"}
```

**Confirm success:** Take one more snapshot. Button should now say `Following [Name]` and "Notify me about all of [Name]'s posts" should appear. Mark `Request Sent`.

---

## Common Issues

**Consecutive 404s on valid-looking URLs**
→ LinkedIn rate-limiting. Navigate to `/feed/`, wait 10 seconds, retry once. If still 404, go to Tier 2 (Google Search).

**More actions dropdown items not visible in compact snapshot**
→ Use `selector=".artdeco-dropdown__content--is-open"` with `compact=false depth=3`. Do not rely on compact snapshots for dropdown contents.

**Relay disconnects**
→ Never use `browser action=open` — this creates a new tab and breaks the relay. Always use `navigate` on the existing tab. If relay disconnects, ask user to re-click the OpenClaw Browser Relay icon on the LinkedIn tab.

**Old-format LinkedIn slugs (e.g. `-21b1804`, `-05bb7611`)**
→ Legacy URL format. Will always 404. Skip Tier 1, go directly to Tier 2 (Google Search).

**Name collision in Google results (common names)**
→ Hover/click the LinkedIn result carefully — check the URL slug matches the person's name/company before clicking through.

**Name collision in LinkedIn people search (common names)**
→ Check the company/headline in the result card before connecting. If ambiguous, open the profile and verify before sending.

**LinkedIn search shows no Connect button inline**
→ Normal for many profiles. Click through to the profile and use Pattern A or B.
