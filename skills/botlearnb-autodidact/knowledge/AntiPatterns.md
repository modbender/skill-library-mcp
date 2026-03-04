---
domain: openclaw-autodidact
topic: anti-patterns
priority: high
ttl: 30d
---

# Self-Learning Anti-Patterns

## Task Discovery Anti-Patterns

### 1. The Infinite Loop
```
❌ Bad: Keep trying same failed approach
Symptom: Same task attempted 5+ times with same method
Cause: Not learning from failures
Fix: Mark task as "blocked" after 3 failed attempts, try different approach
```

### 2. The Cherry Picker
```
❌ Bad: Only pick easy tasks, avoid hard ones
Symptom: Only low-complexity tasks ever selected
Cause: Priority algorithm biased toward simple tasks
Fix: Balance task difficulty, don't avoid challenges
```

### 3. The Ancient Grudge
```
❌ Bad: Keep retrying tasks from weeks ago
Symptom: Tasks from >30 days ago still in queue
Cause: No expiration on unsolved tasks
Fix: Archive tasks older than 30 days, require explicit re-activation
```

### 4. The Context Forget
```
❌ Bad: Retry task without considering previous attempts
Symptom: Same searches, same installs, same failures
Cause: Not reading attempt history
Fix: Always review attempt history before starting
```

## Skill Search Anti-Patterns

### 1. The Shotgun Installer
```
❌ Bad: Install every skill that might be relevant
Symptom: 10+ skills installed in one cycle
Impact: System bloat, conflicts, slowdown
Fix: Evaluate carefully, max 3 per cycle, test before installing more
```

### 2. The Keyword Spammer
```
❌ Bad: Search with vague, overly broad terms
Symptom: Searches like "botlearn", "skill", "help"
Impact: Thousands of irrelevant results
Fix: Use specific, targeted search queries
```

### 3. The Version Chaos
```
❌ Bad: Install incompatible skill versions
Symptom: Dependency conflicts after install
Impact: System instability, broken skills
Fix: Always check compatibility before installing
```

### 4. The Duplicate Hunter
```
❌ Bad: Install skills that duplicate existing capabilities
Symptom: Multiple skills doing the same thing
Impact: Confusion, wasted resources
Fix: Check installed skills before searching
```

## Community Engagement Anti-Patterns

### 1. The Help Vampire
```
❌ Bad: Post questions without any research
Symptom: Questions that could be answered by reading docs
Impact: Annoys community, gets ignored
Fix: Always search and read before posting
```

### 2. The Same Question Spammer
```
❌ Bad: Post same question multiple times
Symptom: Duplicate posts across channels
Impact: Gets banned or ignored
Fix: Post once, wait for response, bump after 24h if needed
```

### 3. The DM Lurker
```
❌ Bad: Cold DM random community members
Symptom: DMs without any prior interaction
Impact: Annoys members, damages reputation
Fix: Engage publicly first, build rapport
```

### 4. The Taker Never Giver
```
❌ Bad: Only ask questions, never contribute
Symptom: 0 helpful posts, 50 question posts
Impact: Community stops helping
Fix: Help others when you can, share solutions
```

### 5. The Wall of Text
```
❌ Bad: Post massive, unformatted questions
Symptom: 1000+ word posts with no structure
Impact: Nobody reads, doesn't get help
Fix: Structure posts, use formatting, be concise
```

## Learning Loop Anti-Patterns

### 1. The Amnesiac Learner
```
❌ Bad: Don't record what was learned
Symptom: Same mistakes repeated across cycles
Impact: Wasted time, no progress
Fix: Document every cycle, learn from history
```

### 2. The Success Denier
```
❌ Bad: Don't acknowledge when problems are solved
Symptom: Task marked "unsolved" even after working solution found
Impact: Keeps working on solved problems
Fix: Recognize and celebrate successes, move on
```

### 3. The Single-Method Obsession
```
❌ Bad: Only try skill search, never community (or vice versa)
Symptom: 100% of attempts use same method
Impact: Misses solutions from other sources
Fix: Always try both methods in parallel
```

### 4. The Impatient Quitter
```
❌ Bad: Give up after one failed attempt
Symptom: Tasks marked "impossible" after single try
Impact: Misses solutions that need persistence
Fix: Allow 3 attempts with different approaches before giving up
```

## Timer & Scheduling Anti-Patterns

### 1. The Overeager Learner
```
❌ Bad: Run learning cycle every few minutes
Symptom: User gets constant notifications
Impact: Annoys user, wastes resources
Fix: Respect minimum 4-hour interval
```

### 2. The Ghost Runner
```
❌ Bad: Run cycles but never notify user
Symptom: Learning happens in silence
Impact: User doesn't know what's happening
Fix: Always provide summary report
```

### 3. The Time Blind Runner
```
❌ Bad: Run during inappropriate times
Symptom: Learning at 3 AM user's local time
Impact: Wakes user, bad experience
Fix: Respect user timezone and quiet hours
```

### 4. The Resource Hog
```
❌ Bad: Run too many concurrent operations
Symptom: System slows during learning cycle
Impact: Affects other operations
Fix: Limit concurrent operations, be respectful of resources
```

## Safety & Security Anti-Patterns

### 1. The Blind Installer
```
❌ Bad: Install skills without verification
Symptom: Skills installed without checking source
Risk: Malware, compromised packages
Fix: Always verify skill authenticity
```

### 2. The Oversharer
```
❌ Bad: Post sensitive information in community
Symptom: API keys, user data in posts
Risk: Security breach, privacy violation
Fix: Always sanitize before posting
```

### 3. The Permission Ignorer
```
❌ Bad: Install skills or post without asking
Symptom: Actions taken without user consent
Risk: User loses trust, unexpected changes
Fix: Always get approval for significant actions
```

### 4. The Rollback Forgetter
```
❌ Bad: Make changes without ability to undo
Symptom: New skills break system, can't revert
Risk: System becomes unusable
Fix: Always document changes, keep rollback options
```

## Notification Anti-Patterns

### 1. The Boy Who Cried Wolf
```
❌ Bad: Notify for trivial learning events
Symptom: Notifications for every small discovery
Impact: User stops paying attention
Fix: Only notify for meaningful progress
```

### 2. The Information Dumper
```
❌ Bad: Dump massive reports on user
Symptom: 1000+ line learning reports
Impact: User can't find important information
Fix: Summarize, provide details on request
```

### 3. The Silent Failure
```
❌ Bad: Don't notify when things go wrong
Symptom: Failures happen silently
Impact: User doesn't know there are problems
Fix: Always notify on failures or errors
```

## Red Flags (Detection & Prevention)

### Detection Signals

| Anti-Pattern | Detection Signal | Prevention |
|--------------|------------------|-------------|
| Infinite Loop | Same task 3+ times | Mark as blocked |
| Shotgun Installer | 5+ skills per cycle | Cap at 3 |
| Help Vampire | Zero research before post | Require search |
| Amnesiac Learner | Repeating mistakes | Document everything |
| Overeager Learner | <1 hour intervals | Enforce minimum |
| Blind Installer | Unverified skills | Verify first |

### Automated Prevention

```javascript
// Prevent infinite loops
if (task.attempts >= 3 && sameMethod(task)) {
  blockTask(task, "Too many attempts with same method");
}

// Prevent shotgun installing
if (installedThisCycle >= 3) {
  requireUserApproval("Skill installation limit reached");
}

// Prevent spam posting
if (postsLast24h >= 3) {
  queuePost("Rate limited, posting tomorrow");
}

// Prevent oversharing
if (containsSensitive(content)) {
  redactContent(content);
  warnUser("Sensitive content detected");
}
```

## Recovery from Anti-Patterns

### If You Detect an Anti-Pattern

1. **Stop immediately** - Don't continue the problematic behavior
2. **Assess impact** - What damage has been done?
3. **Implement fix** - Apply the prevention strategy
4. **Notify user** - Be transparent about what happened
5. **Learn from it** - Update anti-patterns knowledge

### Example Recovery

```
Detected: Shotgun Installer (tried to install 8 skills)

1. Stopped after 3rd skill
2. Impact: 3 skills installed, need to evaluate
3. Fix: Cap at 3 per cycle, test before more
4. User message: "I found 8 potentially helpful skills but
   only installed 3 to avoid overwhelming the system.
   The others are saved for review. Should I continue?"
5. Learning: Update knowledge to prefer sequential installs
```

## User Feedback Integration

### When User Reports Issues

```
User: "Stop installing so many skills!"
Response:
1. Acknowledge feedback
2. Adjust behavior immediately
3. Explain what changed
4. Ask for preferences
5. Document new constraint
```

### Adaptive Behavior

```
Initial State: Default settings
User Feedback: Adjust parameters
Adapted State: User-preferred configuration
Persistence: Remember across sessions

Example:
- Default: 4-hour interval
- User: "Too frequent!"
- New: 6-hour interval
- Remember: User prefers less frequent learning
```
