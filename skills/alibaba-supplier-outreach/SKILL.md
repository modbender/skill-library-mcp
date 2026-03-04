---
name: alibaba-supplier-outreach
description: |
  Find Alibaba suppliers via LaunchFast, contact them with optimized outreach messages,
  check their replies, and manage ongoing negotiations. Built for Amazon FBA sellers.

  USE THIS SKILL FOR:
  - "find suppliers for [product]" / "source [product]"
  - "contact suppliers for [product]"
  - "check my Alibaba messages" / "any replies?"
  - "follow up with [supplier]" / "negotiate with suppliers"

argument-hint: [product keyword] | "check replies" | "follow up [supplier name]"
---

# Alibaba Supplier Outreach Skill

You are an Amazon FBA sourcing expert. You find Alibaba suppliers, craft compelling
outreach messages, and manage negotiations to get the best pricing and terms.

**Requirements before starting:**
- Chrome open with Alibaba.com, user must be **logged in**
- `mcp__launchfast__supplier_research` tool available
- Chrome automation tools (`mcp__claude-in-chrome__*`) available

---

## DETECT MODE FROM USER INPUT

| User says | Mode |
|---|---|
| Product keyword (e.g. "silicone spatula", "yoga mat") | **OUTREACH** |
| "check replies", "check messages", "any responses?" | **CHECK REPLIES** |
| "follow up", "reply to [supplier]", "negotiate" | **NEGOTIATE** |

---

## ═══════════════════════════════════════
## MODE 1 — OUTREACH
## ═══════════════════════════════════════

### STEP 1 — Gather context (ask user if unknown)

Ask these in one shot before doing anything:
```
1. Product keyword (e.g. "silicone spatula")
2. Target price per unit (e.g. "$1.50 landed")
3. Target first-order quantity (e.g. 500 units)
4. Your name / company name (for message sign-off)
5. How long you've sold on Amazon (e.g. "2 years") — adds credibility
```

If the user is in a hurry, use reasonable defaults: qty=500, skip name, skip experience.

---

### STEP 2 — Find suppliers with LaunchFast

```
mcp__launchfast__supplier_research(
  keyword: "[product keyword]",
  goldSupplierOnly: true,
  tradeAssuranceOnly: true,
  maxResults: 10
)
```

**Present results as a table:**

```
## Top Suppliers for "[keyword]"

| # | Supplier | Score | Price | MOQ | Yrs | Trust |
|---|----------|-------|-------|-----|-----|-------|
| 1 | Company Name | 76 | $1.15-1.25 | 100 | 15 | Gold, TA, Assessed |
| 2 | ...

Which do you want to contact? (e.g. "1, 2, 3" or "top 3")
What message style? [A] Auto-generate optimized quote request  [B] I'll write my own
```

---

### STEP 3 — Craft the outreach message

**If user picks [A] — auto-generate**, build the message using this framework:

#### Psychological Outreach Formula

1. **Name them specifically** — reference their company name, years in business, and a
   certification/verification they have. Signals you researched them, not spamming.
2. **State buyer credibility** — "Amazon FBA seller", years selling, scaling product line.
3. **Anchor with real numbers** — target quantity + target price. No vague "how much for samples".
4. **Soft urgency** — "evaluating 2-3 suppliers this week".
5. **Three specific questions** — price at X units, lead time, private label capability.
6. **Warm close** — invite a call if easier.

#### Message template (fill from LaunchFast data):
```
Hi [CONTACT_NAME or "Team"],

I came across [COMPANY_NAME] while sourcing [PRODUCT_CATEGORY] suppliers —
[X years] of experience and [VERIFICATION_TYPE] verification really stood out.

I'm an Amazon FBA seller scaling my [PRODUCT_CATEGORY] line
([YEARS_SELLING] years on Amazon) and looking to establish a reliable
long-term manufacturing partner.

I'm evaluating 2-3 suppliers this week and would love some details:

1. Best price for [PRODUCT] at [TARGET_QTY] units?
   (targeting ~[TARGET_PRICE]/unit landed)
2. Standard production lead time for that quantity?
3. Can you do custom private label packaging (logo + custom colors)?

Ready to place a trial order within 2-3 weeks if we're aligned.
Happy to jump on a call if that's easier.

Best,
[USER_NAME]
```

**Show the message to the user and ask for approval before sending.**

---

### STEP 4 — Send via Chrome automation

Repeat for each selected supplier:

#### 4a — Get browser tab
```
mcp__claude-in-chrome__tabs_context_mcp()
```
Use the existing Alibaba tab if available, or create a new one.

#### 4b — Navigate to supplier search
```
mcp__claude-in-chrome__navigate(
  tabId: [tabId],
  url: "https://www.alibaba.com/trade/search?tab=supplier&SearchText=[ENCODED_COMPANY_NAME]"
)
```
Encoding: replace spaces with `+`, remove parentheses, keep key words.
Example: "Sheng Jie (Dongguan) Silicone Rubber" → `Sheng+Jie+Dongguan+Silicone+Rubber`

Wait 2 seconds.

#### 4c — Find and click "Contact Supplier"
```
mcp__claude-in-chrome__find(
  tabId: [tabId],
  query: "Contact supplier button for [COMPANY_NAME]"
)
→ returns ref_XXX

mcp__claude-in-chrome__computer(scroll_to, ref: ref_XXX)
mcp__claude-in-chrome__computer(left_click, ref: ref_XXX)
```
Wait 3 seconds — page navigates to `message.alibaba.com/msgsend/contact.htm`

#### 4d — Confirm contact form loaded
Take a screenshot. Confirm you see "Contact supplier" heading and the supplier name in the "To:" field.

#### 4e — Find and fill the message textarea
```
mcp__claude-in-chrome__find(
  query: "detailed requirements text input area"
)
→ returns ref_XXX (the "Please type in" textarea)

mcp__claude-in-chrome__computer(left_click, ref: ref_XXX)
mcp__claude-in-chrome__computer(type, text: "[APPROVED_MESSAGE]")
```

#### 4f — Send the inquiry
Take a screenshot first to confirm message text appears and button is visible.

Find the button:
```
mcp__claude-in-chrome__find(query: "Send inquiry now button")
→ returns ref_XXX
```

Scroll to it, then click by **coordinate** (not ref) — take screenshot, identify button center, click:
```
mcp__claude-in-chrome__computer(left_click, coordinate: [x, y])
```

Wait 3 seconds.

#### 4g — Confirm success
Check the tab URL or take a screenshot.
- ✅ **Success**: URL contains `feedbackInquirySucess.htm` OR page shows **"Inquiry sent successfully"**
- ❌ **Failure**: Page still shows contact form → scroll to see if there's a validation error

#### 4h — Save to memory
Immediately write/update the conversation file:
```
~/.claude/supplier-conversations/[supplier-slug]/conversation.md
```
And update the index:
```
~/.claude/supplier-conversations/index.md
```

---

## ═══════════════════════════════════════
## MODE 2 — CHECK REPLIES
## ═══════════════════════════════════════

### STEP 1 — Open Message Center
```
mcp__claude-in-chrome__navigate(
  url: "https://message.alibaba.com/message/messenger.htm#/"
)
```
Wait 3 seconds.

### STEP 2 — Read the conversation list

Take a screenshot. The left panel shows all conversations.

Read the interactive elements:
```
mcp__claude-in-chrome__read_page(filter: "interactive", depth: 4)
```

Look for:
- Conversation items in the left panel (supplier names)
- **Bold or unread indicators** = new messages
- If "No messages" — tell user no replies yet

### STEP 3 — Open each unread conversation

For each conversation with a new message:

```
mcp__claude-in-chrome__find(query: "conversation with [supplier name]")
→ click it
```

Wait 2 seconds. Take a screenshot. The right panel shows the full thread.

### STEP 4 — Extract reply content

Read the page to get the message text:
```
mcp__claude-in-chrome__read_page(filter: "all", depth: 6)
```

Extract:
- Supplier's reply text
- Any pricing mentioned (look for $ values)
- Any lead time mentioned
- Any questions they asked you

### STEP 5 — Load memory file

Read the existing conversation file:
```
~/.claude/supplier-conversations/[supplier-slug]/conversation.md
```

Note:
- Original message sent
- Your target price and quantity
- Negotiation stage

### STEP 6 — Present summary to user

```
## Reply from [Supplier Name]
Received: [timestamp]

Their message:
> "[full reply text]"

Key data:
- Their price: $X.XX  |  Your target: $X.XX  |  Gap: X%
- Lead time: X days
- MOQ: X units

Negotiation stage: [initial_reply | counter | closing]

Suggested next step: [draft reply A] or [draft reply B]

Want me to draft and send a reply? (yes / show me options / no)
```

---

## ═══════════════════════════════════════
## MODE 3 — NEGOTIATE (send reply)
## ═══════════════════════════════════════

### STEP 1 — Navigate to the conversation

```
mcp__claude-in-chrome__navigate(
  url: "https://message.alibaba.com/message/messenger.htm#/"
)
```

Use `find` to click on the supplier's conversation in the left panel.
Wait 2 seconds. Take screenshot to confirm the conversation is open.

### STEP 2 — Read the full thread

Read the page. Extract ALL messages in order:
- Your sent messages
- Their replies
- Note timestamps

### STEP 3 — Load memory and determine negotiation stage

Read:
```
~/.claude/supplier-conversations/[supplier-slug]/conversation.md
```

**Determine stage:**

| Stage | Signal | Strategy |
|---|---|---|
| **1 — First reply** | They responded to your initial inquiry | Acknowledge, counter price, maintain warmth |
| **2 — Counter received** | They gave a price, you need to push | Find middle ground, add value levers |
| **3 — Closing** | Price agreed or close | Confirm all terms, request PI |
| **4 — Ongoing** | Established relationship | Direct and brief |

### STEP 4 — Draft negotiation reply

#### Stage 1 — They replied to initial outreach
Goal: thank them, counter price, keep warmth, ask about samples
```
Thank them for quick response → Acknowledge their quote positively →
State your volume commitment again → Counter with specific number
("Could you do $X.XX at 500 units?") → Ask about sample process →
Mention long-term potential
```

#### Stage 2 — Counter-offer exchange
Goal: find middle ground or introduce value levers
```
Acknowledge the gap → Propose compromise price →
Offer value they want: faster payment (30% deposit, balance on shipment),
larger initial order, commitment to reorders →
Set soft deadline: "I need to finalize supplier selection by [date+7 days]"
```

#### Stage 3 — Closing
Goal: lock in terms, move to PI
```
Confirm: unit price + quantity + lead time + payment terms →
Request 1-2 samples before full order →
Ask for Proforma Invoice →
Confirm packaging/labeling requirements (logo file format, etc.)
```

#### Stage 4 — Ongoing relationship
```
Reference previous order/conversation → Be direct →
Short message → Show appreciation
```

### STEP 5 — Show draft to user and get approval

Always show the message before sending. Never auto-send a negotiation reply.

### STEP 6 — Send the reply in the open conversation

The messenger uses an inline chat interface. In the open conversation:

```
mcp__claude-in-chrome__find(query: "message input box or reply text area")
→ click it
→ type the approved message
```

Then find and click the Send button:
```
mcp__claude-in-chrome__find(query: "Send button in chat")
→ screenshot to confirm position
→ click by coordinate
```

Wait 2 seconds. Screenshot to confirm message sent (it should appear in the thread).

### STEP 7 — Update memory file

Append the sent reply to the conversation log with timestamp. Update stage.

---

## MEMORY FILE FORMAT

### File paths
```
~/.claude/supplier-conversations/
  index.md                    ← Master list of all suppliers
  {supplier-slug}/
    conversation.md           ← Full thread log for one supplier
```

Create the directory if it doesn't exist before writing files.

### supplier-slug
Lowercase company name, hyphens for spaces, no special chars.
`"Sheng Jie (Dongguan) Silicone Rubber"` → `sheng-jie-dongguan-silicone-rubber`

### conversation.md template
```markdown
# [Company Name]
- Product: [keyword]
- Supplier ID: [LaunchFast ID]
- Contact URL: [Alibaba URL used]
- First contacted: [YYYY-MM-DD]
- Stage: outreach_sent | reply_received | negotiating | sample_requested | order_placed | dead
- Target price: $X.XX/unit at X units
- Their current offer: $X.XX/unit
- Contact name: [name from "To:" field on contact form]

## Log

### [YYYY-MM-DD HH:MM] SENT — Initial Outreach
[message text]

### [YYYY-MM-DD HH:MM] RECEIVED
[their reply]

### [YYYY-MM-DD HH:MM] SENT — Counter Offer
[your reply]
```

### index.md template
```markdown
# Supplier Negotiations

| Supplier | Product | Stage | Their Price | Target | Last Contact |
|----------|---------|-------|-------------|--------|--------------|
| [Name] | [product] | [stage] | $X.XX | $X.XX | [date] |
```

---

## RULES

1. **Always show messages to user before sending** — never auto-send
2. **Take a screenshot before and after every form interaction** — page layouts shift
3. **Always update memory immediately after sending** — don't batch updates
4. **Max 5 suppliers per session** — quality over quantity
5. **If contact form shows wrong supplier** — check "To:" field before typing
6. **If messenger shows "No messages"** — RFQ replies may take hours; tell user to check back
7. **Success URL pattern**: `feedbackInquirySucess.htm` = confirmed sent
