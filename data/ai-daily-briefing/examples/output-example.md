# Example Output: Daily Briefing

This shows what the AI generates when you ask for a briefing.

---

## Example 1: Full Briefing (Busy Day)

**User:** "briefing"

**AI Response:**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
☀️ DAILY BRIEFING — Tuesday, February 3, 2026
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️ OVERDUE (2 items)
• Send Acme proposal — was due Feb 1
• Review Week 2 training materials — was due Jan 31

📅 TODAY'S PRIORITIES
1. [ ] Anne follow-up call — 2pm today
2. [ ] Finalize Week 3 training content — EOD
3. [ ] Prep for Makati trip — flights need booking
4. [ ] Respond to Karlen re: workflow docs
5. [ ] Clear overdue Acme proposal

📆 CALENDAR
• 10:00 AM — Team standup (30 min)
• 2:00 PM — Anne follow-up call (1 hour)
• 4:30 PM — Workshop dry run (90 min)

💡 CONTEXT (from recent meetings)
• Anne partnership confirmed — ready to move forward (from anne-call)
• OpenClaw bot architecture changing to specialists (from pm-meeting)
• Makati trip deadline approaching — need flights by Friday

🎯 FOCUS FOR TODAY
Get the Acme proposal out first thing — it's 2 days overdue and blocking the deal.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Example 2: Clean Day (Nothing Overdue)

**User:** "what's today look like?"

**AI Response:**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
☀️ DAILY BRIEFING — Wednesday, February 4, 2026
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📅 TODAY'S PRIORITIES
1. [ ] Complete Week 3 training review — EOD
2. [ ] Book Makati flights — before prices go up
3. [ ] Draft Anne partnership agreement outline

📆 CALENDAR
• 9:00 AM — Deep work block (2 hours)
• 11:30 AM — Quick sync with Jacklyn (15 min)
• 3:00 PM — Client check-in call (30 min)

💡 CONTEXT (from recent meetings)
• Acme proposal sent ✓ — awaiting response
• Workshop dry run went well — minor tweaks needed
• Karlen starting Week 3 content tomorrow

🎯 FOCUS FOR TODAY
Lighter day — use the morning block for the training review while you have energy.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Example 3: Overdue Check Only

**User:** "what's overdue?"

**AI Response:**

```
⚠️ OVERDUE ITEMS

1. Send Acme proposal — was due Feb 1 (2 days ago)
2. Review Week 2 training — was due Jan 31 (3 days ago)
3. Invoice ABC Corp — was due Jan 28 (6 days ago)

3 items need attention. Want me to help you tackle these first?
```

---

## Example 4: Nothing Overdue

**User:** "what's overdue?"

**AI Response:**

```
✅ Nothing overdue! You're caught up.

Upcoming deadlines this week:
• Makati flights — Friday
• Week 3 review — Thursday
• Client proposal draft — Friday

Want a full briefing?
```

---

## Example 5: Weekly Preview

**User:** "weekly preview"

**AI Response:**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📅 WEEKLY PREVIEW — Week of February 3, 2026
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

MONDAY (Feb 3) — Today
• 2 overdue items to clear
• Anne call at 2pm
• Workshop dry run at 4:30pm

TUESDAY (Feb 4)
• Week 3 training review due
• Light meeting day — good for deep work

WEDNESDAY (Feb 5)
• Team planning session (2 hours)
• Book Makati flights deadline

THURSDAY (Feb 6)
• Karlen starts Week 3 content
• Client check-in

FRIDAY (Feb 7)
• Makati flights MUST be booked
• Week wrap-up

⚠️ WATCH OUT FOR
• Makati flights — prices going up, book by Wed
• Anne partnership agreement — she's expecting draft by Friday
• 2 overdue items dragging into the week

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Example 6: No Data Available

**User:** "briefing"

**AI Response:**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
☀️ DAILY BRIEFING — Tuesday, February 3, 2026
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

No to-do list or meeting notes found yet.

Would you like to:
• **Start a to-do list** — Tell me your tasks for today
• **Process meeting notes** — Paste notes and I'll extract action items
• **Quick priorities** — Just tell me your top 3 things

Once you have tasks or meeting notes, your briefings will be much richer!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Example 7: End of Day Request

**User:** "briefing" (at 5pm)

**AI Response:**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🌅 END OF DAY CHECK — Tuesday, February 3, 2026
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ COMPLETED TODAY
• Anne follow-up call ✓
• Workshop dry run ✓
• Team standup ✓

⚠️ STILL OPEN
• Acme proposal — still overdue
• Week 3 training review — pushed to tomorrow

📆 TOMORROW PREVIEW
• 9:00 AM — Deep work block
• 11:30 AM — Jacklyn sync
• 3:00 PM — Client call

🎯 BEFORE YOU LOG OFF
The Acme proposal is now 2 days overdue. 15 minutes tonight or first thing tomorrow?

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Key Points

1. **Format is consistent** — Same structure every time
2. **Sections are skipped if empty** — No "Overdue: None" clutter
3. **Focus statement is mandatory** — Always end with clear direction
4. **Context is relevant** — Only show what helps today
5. **Adapts to time of day** — Morning vs evening briefings differ

---

*Part of AI Daily Briefing by Jeff J Hunter — https://jeffjhunter.com*
