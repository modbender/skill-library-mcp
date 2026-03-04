# Agent Use Cases by Role

## Business Automation (Entrepreneur Perspective)

### High-Value Automations
| Task | Time Saved | Implementation |
|------|-----------|----------------|
| Lead qualification | 5-8 hrs/week | Email triage + CRM integration |
| Meeting scheduling | 3-5 hrs/week | Calendar + availability checking |
| Invoice follow-ups | 2-3 hrs/week | Payment tracking + email templates |
| Report generation | 2-4 hrs/week | Data aggregation + formatting |
| FAQ responses | 1-2 hrs/day | Knowledge base + similarity search |

### Success Criteria
- Response time drops (minutes, not hours)
- Measurable hours reclaimed weekly
- No embarrassing automated replies
- Clear ROI vs part-time hire cost

### Common Concerns
- "Will it sound robotic?" → Requires good persona training
- "What if it makes mistakes?" → Human-in-loop for first N interactions
- "Does it work with my tools?" → Check integrations before committing
- "How long until useful?" → Realistic: 1-2 weeks setup, 1 month refinement

## Personal Assistant (Solopreneur Perspective)

### Workflows to Automate
1. **Morning email triage** → Categorize: Urgent / Client / Admin / Newsletter
2. **Meeting prep** → 15 min before: gather context, last emails, notes
3. **Client onboarding** → Create folder, send docs, schedule kickoff
4. **Weekly review** → Pull tasks completed, hours logged, upcoming deadlines

### Context to Track
- Client communication preferences
- Payment history (fast payer vs always late)
- Personal productivity patterns
- Work boundaries (no notifications after 7pm)

### Key Integrations
- Email (read, draft, categorize)
- Calendar (read/write, block time)
- Project management (tasks, status)
- Invoicing (track, remind)

## Customer Service (Small Business Perspective)

### Automation Tiers

**Handle 100% Autonomously:**
- "Where is my order?" — Tracking lookup
- Store hours, location — Static info
- Return policy questions — Standard policy
- Shipping rates — Calculator-based

**Handle with Guardrails:**
- Product recommendations — Based on preferences
- Simple complaints ("late delivery") — Apologize, offer gesture
- Size/fit guidance — Product specs + customer input

**Escalate Always:**
- Angry/emotional customers — Sentiment detection
- Legal threats, health/safety concerns
- VIP customers (top 5% by value)
- Media/influencer inquiries

### Escalation Packet
When handing off to human, agent provides:
- Customer name + order history
- Conversation summary (3 bullets max)
- What was tried
- Recommended next action

## Content Creation (Creator Perspective)

### Mechanical vs Creative Split

**Automate 100%:**
- Cross-posting same content
- Resizing for platforms
- Comment spam filtering
- Scheduling, analytics aggregation
- Transcription, file organization

**Agent Assists, Human Decides:**
- Thumbnail variants (generate 5, human picks)
- Newsletter drafts (structure from video, human adds voice)
- SEO metadata (draft titles/descriptions, human approves)

**Keep Fully Manual:**
- Script hooks and storytelling
- Hot takes and opinions
- Personal anecdotes
- Community inside jokes

### Quality Control
- Style guide document with 50+ examples of your voice
- Banned phrases list
- Review queue: batch check agent drafts 2x/day
- Feedback loop: agent learns from your edits

## Developer Tools (Technical Perspective)

### Agent Categories for Developers

**Code Assistants:**
- Context: current file, errors, project structure
- Tools: read files, write files, run tests, search codebase
- Risk: can modify code, needs careful sandboxing

**DevOps Agents:**
- Context: infrastructure state, alerts, logs
- Tools: deploy, scale, rollback, query metrics
- Risk: production impact, needs approval gates

**Research Agents:**
- Context: documentation, web search results
- Tools: search, summarize, compare options
- Risk: low (read-only), can run freely

### Debugging Agent Issues
1. Check context window — Is relevant info present?
2. Check tool results — Did tools return expected data?
3. Check reasoning — Add chain-of-thought for visibility
4. Check confidence — Does agent know when it's uncertain?
