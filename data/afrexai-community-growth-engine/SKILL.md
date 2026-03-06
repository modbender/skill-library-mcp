---
name: afrexai-community-growth-engine
description: "Complete community building, engagement, and monetization system. From zero to thriving community — launch strategy, member engagement loops, content programming, moderation frameworks, growth tactics, monetization models, and health metrics. Works for Discord, Slack, Telegram, Circle, forums, or any platform."
metadata: {"clawdbot":{"emoji":"🏘️","os":["linux","darwin","win32"]}}
---

# Community Growth Engine 🏘️

Complete 12-phase system for building, growing, and monetizing communities. From launch strategy through engagement loops, moderation, growth tactics, and revenue — everything you need to run a thriving community.

**Important:** Community advice, not legal counsel. Verify platform ToS, privacy laws (GDPR/CCPA), and local regulations for your jurisdiction.

---

## Phase 1: Community Strategy & Foundation

### Community Brief

```yaml
community_brief:
  name: ""
  mission: ""  # One sentence: who + what value
  tagline: ""  # 8 words max
  type: ""     # interest | practice | product | action | place
  
  target_member:
    who: ""           # Specific person, not "everyone"
    pain_points: []   # 3-5 problems they have
    desired_outcome: "" # What transformation do they want?
    where_now: []     # Where do they currently hang out?
    willingness_to_pay: "" # free-only | low ($5-20) | mid ($20-100) | high ($100+)
  
  anti_members:       # Who is NOT welcome (be specific)
    - ""
  
  value_proposition: "" # "The only community where [specific group] can [specific outcome]"
  
  differentiator: ""  # Why this vs Reddit/Facebook/existing communities?
  
  business_model: ""  # free | freemium | paid | hybrid
  revenue_target: ""  # Monthly target
  
  platform: ""        # discord | slack | telegram | circle | forum | other
  platform_rationale: "" # Why this platform specifically?
```

### Platform Selection Guide

| Platform | Best For | Pros | Cons | Cost |
|----------|----------|------|------|------|
| Discord | Gaming, tech, creator, large | Free, rich features, bots | Noisy, learning curve | Free |
| Slack | Professional, B2B, small-mid | Familiar, threaded | Expensive at scale, history limits (free) | $7.25/user/mo |
| Telegram | Crypto, international, quick | Fast, global, bots | Limited structure, spam-prone | Free |
| Circle | Course creators, premium | Clean, integrations, paywall | Monthly cost, less sticky | $49+/mo |
| Mighty Networks | Coaches, courses + community | All-in-one | Expensive, lock-in | $41+/mo |
| Reddit (subreddit) | Discovery, SEO, niche | Massive reach, free | No ownership, algorithm changes | Free |
| Geneva | Gen Z, social, casual | Mobile-first, clean | Smaller user base | Free |
| Discourse | Long-form, knowledge base | SEO, ownership, self-host | Technical setup, less real-time | Free (self-host) |

**Decision tree:**
1. Budget = $0 + tech audience → **Discord**
2. Budget = $0 + professional audience → **Slack** (free tier) or **LinkedIn Group**
3. Need paywall + courses → **Circle** or **Mighty Networks**
4. International/mobile-first → **Telegram**
5. Want SEO + discovery → **Reddit** (owned subreddit) or **Discourse**
6. Want full ownership → **Discourse** (self-hosted)

### Community Type Framework

| Type | Definition | Examples | Key Metric |
|------|-----------|----------|------------|
| Interest | Shared passion | Photography clubs, book clubs | Engagement rate |
| Practice | Shared profession | DevOps community, founders group | Knowledge sharing |
| Product | Around a product | OpenClaw Discord, Figma community | Support deflection + advocacy |
| Action | Shared cause | Climate groups, open source | Contribution rate |
| Place | Geographic | City tech scenes, local groups | Event attendance |

---

## Phase 2: Community Architecture

### Channel/Space Structure

**Discord example (adapt for your platform):**

```
📌 START HERE
  #welcome — Auto-message, rules, role select
  #introduce-yourself — Template: name, role, what you're working on
  #rules — Community guidelines (link, not wall of text)

💬 GENERAL
  #general — Main conversation
  #off-topic — Non-community-topic chat
  #wins — Celebrate achievements (positive reinforcement loop)

🎓 KNOWLEDGE
  #resources — Curated links, tools, guides
  #ask-anything — Q&A (encourage answers from members, not just staff)
  #tutorials — Member-created guides
  #[topic-1] — Specific topic channel
  #[topic-2] — Specific topic channel

🔨 BUILD
  #show-your-work — Share projects for feedback
  #accountability — Public goals and check-ins
  #collabs — Find collaborators

📢 ANNOUNCEMENTS
  #announcements — Official updates (admin-only post)
  #events — Upcoming events, AMAs, workshops

🔒 PREMIUM (if applicable)
  #premium-general — Paid members only
  #premium-resources — Exclusive content
  #office-hours — Direct access to experts
```

**Channel rules:**
- Start with 5-8 channels max — add more only when existing ones are consistently active
- Archive channels with <5 messages/week for 3 consecutive weeks
- Every channel needs a clear purpose in its description
- Pin the "what this channel is for" message

### Role System

```yaml
roles:
  - name: "New Member"
    auto_assign: true
    permissions: "read + post in general channels"
    visual: "🆕"
    
  - name: "Member"
    earn_criteria: "7 days + 10 messages + intro posted"
    permissions: "full access to public channels"
    visual: "✅"
    
  - name: "Active Member"
    earn_criteria: "30 days + 50 messages + helped 3 people"
    permissions: "member + create threads"
    visual: "⭐"
    
  - name: "Champion"
    earn_criteria: "90 days + consistent value + nominated by staff"
    permissions: "active member + moderate threads + beta access"
    visual: "🏆"
    
  - name: "Moderator"
    earn_criteria: "Champion + invitation"
    permissions: "full moderation powers"
    visual: "🛡️"
    
  - name: "Admin"
    earn_criteria: "Core team only"
    permissions: "everything"
    visual: "👑"
```

### Onboarding Flow

**0-24 hours (critical window — 70% of members who don't engage in 24h never will):**

1. **Immediate** (auto): Welcome DM with 3 specific actions
   ```
   Welcome to [Community]! 🎉
   
   Here's how to get started:
   1. Introduce yourself in #introduce-yourself (use the template pinned there)
   2. Check out #resources for our top guides
   3. Jump into #general and say hi
   
   Pro tip: [one specific valuable thing they can do right now]
   
   Questions? Drop them in #ask-anything — someone usually responds within [X] hours.
   ```

2. **Within 1 hour** (auto or manual): React to their intro with relevant emoji
3. **Within 4 hours**: A human (mod or champion) replies to their intro with a genuine, specific comment
4. **Day 2-3**: Tag them in a conversation relevant to their interests (from intro)
5. **Day 7**: Check-in DM: "How's it going? Finding what you need?"

**Onboarding completion checklist:**
- [ ] Posted introduction
- [ ] Made first comment in a topic channel
- [ ] Reacted to someone else's post
- [ ] Received a reply from another member (not staff)
- [ ] Accessed one resource

---

## Phase 3: Content Programming & Engagement Loops

### Weekly Content Calendar

```yaml
weekly_calendar:
  monday:
    name: "Monday Momentum"
    type: "prompt"
    description: "Share your #1 goal for the week"
    channel: "#accountability"
    engagement_type: "participation"
    
  tuesday:
    name: "Tutorial Tuesday"
    type: "educational"
    description: "Member or staff shares a how-to"
    channel: "#tutorials"
    engagement_type: "learning"
    
  wednesday:
    name: "Wins Wednesday"
    type: "celebration"
    description: "Share something you're proud of this week"
    channel: "#wins"
    engagement_type: "positive reinforcement"
    
  thursday:
    name: "AMA / Expert Hour"
    type: "event"
    description: "Rotating guest or community expert"
    channel: "#events"
    engagement_type: "access"
    frequency: "bi-weekly"
    
  friday:
    name: "Feedback Friday"
    type: "peer_review"
    description: "Share work for constructive feedback"
    channel: "#show-your-work"
    engagement_type: "collaboration"
    
  weekend:
    name: "Weekend Reading"
    type: "curated"
    description: "Top 3 links from the week"
    channel: "#resources"
    engagement_type: "value delivery"
```

### Engagement Loop Design

**The CORE Loop (drives daily engagement):**
```
Trigger → Action → Variable Reward → Investment
```

1. **Notification trigger**: New question in your area of expertise
2. **Action**: Answer the question
3. **Variable reward**: Social recognition (thanks, reactions, role upgrade)
4. **Investment**: Profile/reputation grows, making future rewards more valuable

**7 Engagement Mechanics:**

| Mechanic | Description | Example | Frequency |
|----------|-------------|---------|-----------|
| Prompts | Open-ended questions that invite sharing | "What's your biggest challenge this week?" | Daily |
| Challenges | Time-bound goals with public accountability | "30-day shipping challenge" | Monthly |
| Showcases | Members share work for feedback | "Show Your Work Friday" | Weekly |
| AMAs | Expert access creates FOMO | "AMA with [expert] Thursday 2pm" | Bi-weekly |
| Debates | Friendly disagreement drives engagement | "Hot take: [controversial opinion]" | Weekly |
| Collaborations | Members work together | "Find a collab partner for [project]" | Monthly |
| Celebrations | Public wins reinforce participation | "🎉 [member] just hit [milestone]!" | As earned |

### Conversation Starters That Actually Work

**High-response templates:**
- "What's one thing you learned this week that surprised you?"
- "Hot take: [mild controversy in your niche]. Agree or disagree?"
- "If you could only use ONE tool for [topic], what would it be and why?"
- "[Before/after] — Share your transformation"
- "What's your unpopular opinion about [topic]?"
- "Rate your week 1-10 and explain in one sentence"
- "Roast my [project/idea/setup] — I want honest feedback"

**Low-response patterns to avoid:**
- Yes/no questions
- "What do you think about [thing]?" (too vague)
- Questions requiring expertise most members don't have
- Posts that are really announcements disguised as questions

---

## Phase 4: Moderation & Community Health

### Community Guidelines Template

```markdown
# [Community Name] Guidelines

**Our vibe:** [2-3 words describing the culture — e.g., "helpful, honest, humble"]

## The Basics
1. **Be kind, be specific.** Disagree with ideas, not people. Add context, not just opinions.
2. **No spam, no self-promo** (unless in designated channels). Sharing your work when relevant = cool. Drive-by links = not cool.
3. **Search before asking.** Someone probably answered it. When they didn't, ask away.
4. **Give more than you take.** Answer questions. Share resources. Celebrate others.
5. **Keep it on-topic.** #off-topic exists for a reason.
6. **No hate speech, harassment, or discrimination.** Zero tolerance. One strike.
7. **Protect privacy.** Don't share others' information without consent.

## Enforcement
- **Gentle reminder** → **Warning** → **24h mute** → **Permanent ban**
- Exception: Hate speech, doxxing, illegal content = immediate ban
- Appeals: DM a moderator within 7 days

## Report Issues
React with 🚩 or DM a moderator. All reports are confidential.
```

### Moderation Decision Matrix

| Behavior | Severity | First Offense | Second | Third |
|----------|----------|---------------|--------|-------|
| Off-topic post | Low | Redirect to correct channel | Gentle reminder | Mute 1h |
| Self-promotion spam | Medium | Delete + DM warning | 24h mute | 7-day ban |
| Heated argument | Medium | Cool-down reminder (public) | Thread lock + DM both | 24h mute |
| Misinformation | Medium | Correct publicly (kindly) | Warning DM | 7-day ban |
| Harassment | High | Immediate mute + investigate | Permanent ban | — |
| Hate speech/slurs | Critical | Immediate ban | — | — |
| Doxxing | Critical | Immediate ban + delete content | — | — |
| Illegal content | Critical | Immediate ban + report to platform | — | — |

### Moderator Playbook

**When someone is being difficult (but not rule-breaking):**
1. Assume good intent first — they might be having a bad day
2. Redirect publicly: "Hey, let's keep this constructive. What specifically would help?"
3. If continuing: DM privately — "I noticed some tension. What's going on?"
4. If still escalating: "Taking a quick break on this thread. Let's revisit in 24h."

**When two members are fighting:**
1. Don't take sides publicly
2. Acknowledge both perspectives: "You both make valid points"
3. Lock the thread if it's derailing
4. DM both separately to de-escalate
5. If recurring: mediated conversation or separate them

**Moderator burnout prevention:**
- Rotate on-call moderators (never one person 24/7)
- Maximum 2-hour active moderation shifts
- Monthly moderator check-in: "How are you doing?"
- Clear escalation path — mods shouldn't handle everything alone
- Celebrate moderator contributions publicly

---

## Phase 5: Growth Engine

### The Growth Flywheel

```
Content creates value → Value attracts members → Members create content → Repeat
```

### 12 Growth Tactics (Ranked by Effort/Impact)

| Tactic | Effort | Impact | Best For |
|--------|--------|--------|----------|
| 1. SEO content → community | Medium | High | Long-term discovery |
| 2. Cross-promotion with adjacent communities | Low | High | Quick growth |
| 3. Guest AMAs | Low | Medium | Authority + reach |
| 4. Member referral program | Medium | High | Quality growth |
| 5. Social proof posts | Low | Medium | Conversion |
| 6. Free resources with community CTA | Medium | High | Lead gen |
| 7. Twitter/LinkedIn threads → community | Low | Medium | Audience funnel |
| 8. Podcast/YouTube → community | High | High | Authority + funnel |
| 9. Challenges (public + invite friends) | Medium | Medium | Viral loops |
| 10. Partnership with tool/product | Medium | High | Aligned audiences |
| 11. Paid acquisition (targeted) | High | Variable | Scale after PMF |
| 12. Conference/event presence | High | Medium | B2B/professional |

### Member Referral Program

```yaml
referral_program:
  mechanic: "unique invite link per member"
  
  tiers:
    - invites: 3
      reward: "Custom role badge"
      
    - invites: 10
      reward: "Access to premium channel for 1 month"
      
    - invites: 25
      reward: "Free month of premium membership"
      
    - invites: 50
      reward: "Lifetime premium + featured member spotlight"
  
  rules:
    - "Referred member must complete onboarding (post intro + 5 messages)"
    - "Self-referrals or bot accounts don't count"
    - "Tracked via platform invite link or custom bot"
  
  anti_gaming:
    - "Minimum 7-day activity from referred member"
    - "Manual review for sudden spikes"
```

### Content-to-Community Funnel

```
Blog/SEO article
  ↓ CTA: "Join 500+ [role] discussing this daily"
Social media post
  ↓ CTA: "The conversation continues in our community"
YouTube/Podcast
  ↓ CTA: "Get the resources mentioned → community"
Free resource/template
  ↓ CTA: "Get feedback on your version → community"
Newsletter
  ↓ CTA: "This week's best community discussion"
```

---

## Phase 6: Monetization Models

### Revenue Strategy Matrix

| Model | Revenue | Effort | Best For | Typical Range |
|-------|---------|--------|----------|---------------|
| Free + premium tier | Recurring | Medium | Established communities | $10-50/mo |
| Paid-only (gated) | Recurring | Low | High-value niche | $20-200/mo |
| Course + community | One-time + recurring | High | Educators, experts | $200-2000 + $20-50/mo |
| Sponsorships | One-time | Medium | Large audiences (5k+) | $500-5000/post |
| Events/workshops | One-time | High | Practice communities | $50-500/ticket |
| Job board | Recurring | Low | Professional communities | $100-500/listing |
| Affiliate/referral | Commission | Low | Product communities | 10-30% commission |
| Merch | One-time | Medium | Strong brand identity | $5-20/unit profit |

### Freemium Architecture

```yaml
free_tier:
  access:
    - "General discussion channels"
    - "Weekly newsletter"
    - "Community events (limited)"
    - "Resource library (basics)"
  purpose: "Demonstrate value, build habit"

premium_tier:
  price: "$[X]/month or $[X*10]/year"
  access:
    - "Everything in free"
    - "Premium discussion channels"
    - "Expert office hours (weekly)"
    - "Full resource library"
    - "Member directory"
    - "Priority support"
    - "Exclusive events/workshops"
  purpose: "Deeper value for committed members"

vip_tier:
  price: "$[X*3]/month"
  access:
    - "Everything in premium"
    - "1:1 monthly call with expert"
    - "Private mastermind group (max 20)"
    - "Early access to everything"
    - "Input on community direction"
  purpose: "High-touch for power users"
```

### Pricing Psychology for Communities

- **Anchor high:** Show annual price, then monthly feels cheap
- **Social proof in pricing:** "$29/mo — join 340 members"
- **Loss framing:** "Members saved an average of $X last month"
- **Grandfathering:** Lock in early members at lower price — they become loyal advocates
- **Free trial:** 7 days for paid communities (not 30 — urgency matters)
- **Community-specific:** Price should be <1% of the value members get (if you help people earn $10K more, $50/mo is nothing)

---

## Phase 7: Events & Programming

### Event Types & Frequency

| Event | Format | Frequency | Prep Time | Engagement |
|-------|--------|-----------|-----------|------------|
| AMA (Ask Me Anything) | Text or voice | Bi-weekly | 2h | High |
| Workshop | Live teaching + exercises | Monthly | 8h | Very High |
| Co-working session | Silent work + check-ins | Weekly | 0.5h | Medium |
| Challenge | Multi-day goals | Monthly | 4h | High |
| Showcase/Demo day | Members present work | Monthly | 2h | High |
| Book/Article club | Read + discuss | Bi-weekly | 1h | Medium |
| Networking mixer | Breakout rooms | Monthly | 1h | Medium |
| Town hall | Community updates + Q&A | Quarterly | 3h | Medium |

### Event Execution Template

```yaml
event:
  name: ""
  type: ""
  date: ""
  time: ""  # Include timezone + "your local time" link
  duration: ""
  host: ""
  
  pre_event:
    - "Announce 2 weeks before"
    - "Reminder 3 days before"
    - "Day-of reminder 2 hours before"
    - "Prep materials/questions sent 24h before"
  
  during:
    - "Start 2 min late (grace period)"
    - "Welcome + ground rules (2 min)"
    - "Main content (70% of time)"
    - "Q&A / discussion (25% of time)"
    - "Wrap-up + next steps (5% of time)"
  
  post_event:
    - "Summary posted in #events within 24h"
    - "Recording shared (if applicable)"
    - "Follow-up prompt in relevant channel"
    - "Feedback form (3 questions max)"
    
  success_metrics:
    attendance_rate: "" # RSVPs who showed up
    engagement: ""      # Questions asked, chat messages
    satisfaction: ""    # Post-event rating
    follow_through: ""  # Action taken after event
```

---

## Phase 8: Member Journey & Lifecycle

### The 5-Stage Member Lifecycle

```
Visitor → New Member → Active Member → Champion → Alumnus
```

| Stage | Duration | Goal | Actions | Risk |
|-------|----------|------|---------|------|
| Visitor | Pre-join | Convert to member | Landing page, social proof, free preview | Never joins |
| New Member | 0-30 days | First value moment | Onboarding flow, personal welcome, quick win | Ghost (70% risk) |
| Active Member | 1-6 months | Regular participation | Content loops, role progression, relationships | Fade out |
| Champion | 6+ months | Leadership + advocacy | Mod roles, teaching, referrals, co-creation | Burnout |
| Alumnus | Post-active | Positive relationship | Alumni channel, re-engagement campaigns | Negative word-of-mouth |

### Engagement Recovery Playbook

**Detecting disengagement (leading indicators):**
- Message frequency drops >50% week-over-week
- Stops reacting to posts
- Doesn't attend events they usually attend
- Unsubscribes from notifications

**Re-engagement sequence:**

| Day | Action | Channel | Message |
|-----|--------|---------|---------|
| 7 (quiet) | Soft nudge | In-community | Tag in relevant conversation |
| 14 | Direct reach-out | DM | "Hey [name], noticed you've been quiet. Everything ok? We miss your perspective on [topic]." |
| 21 | Value delivery | DM | Share exclusive resource or early access to something |
| 30 | Exit survey | DM | "No pressure at all — if you've moved on, we get it. Quick question: what could we do better?" |
| 60 | Final reach-out | Email | "The door's always open. Here's what you missed: [best 3 things]" |

### Champion Development Program

```yaml
champion_program:
  identification:
    signals:
      - "Consistently helpful answers (3+ per week)"
      - "Other members mention them positively"
      - "Creates original content/resources"
      - "Attends events regularly"
      - "Defends community culture naturally"
    
  development:
    month_1:
      - "Invitation conversation (DM)"
      - "Explain the role and expectations"
      - "Grant champion role and access"
    
    month_2:
      - "Shadow a moderator session"
      - "Lead one discussion or event segment"
      - "Feedback session with community lead"
    
    month_3:
      - "Independent moderation responsibilities"
      - "Create one piece of community content"
      - "Mentor one new member"
    
  rewards:
    - "Public recognition (featured member)"
    - "Free premium access"
    - "Early access to new features/content"
    - "Input on community decisions"
    - "Letter of recommendation / LinkedIn endorsement"
    - "Revenue share if applicable"
  
  burnout_prevention:
    - "Maximum 5 hours/week commitment"
    - "Scheduled breaks (1 week off per quarter)"
    - "Monthly 1:1 check-in"
    - "Right to step down gracefully anytime"
```

---

## Phase 9: Community Health Metrics

### Dashboard

```yaml
community_health:
  period: ""  # weekly / monthly
  
  growth:
    new_members: 0
    churned_members: 0
    net_growth: 0
    total_members: 0
    growth_rate: ""  # (new - churned) / total × 100
    
  engagement:
    dau_mau_ratio: ""     # Daily active / Monthly active (healthy: 20-50%)
    messages_per_day: 0
    messages_per_member: 0 # Per active member
    threads_created: 0
    avg_response_time: ""  # Time to first reply on a question
    members_posting: 0     # Unique posters this period
    lurker_ratio: ""       # Members who read but don't post (normal: 70-90%)
    
  quality:
    questions_answered: ""  # % of questions that got a useful reply
    member_to_member: ""    # % of replies from non-staff
    negative_incidents: 0
    reported_messages: 0
    member_satisfaction: "" # Monthly pulse survey (1-10)
    
  retention:
    day_7_retention: ""    # % still active after 7 days
    day_30_retention: ""   # % still active after 30 days
    day_90_retention: ""   # % still active after 90 days
    onboarding_completion: "" # % completing onboarding steps
    
  revenue:
    mrr: ""               # If monetized
    arpmm: ""             # Average revenue per monetized member
    conversion_rate: ""   # Free to paid
    churn_rate: ""        # Paid member churn
```

### Health Score (0-100)

| Dimension | Weight | Scoring |
|-----------|--------|---------|
| Growth rate | 15% | >10%/mo = 100, 5-10% = 75, 1-5% = 50, 0% = 25, negative = 0 |
| DAU/MAU ratio | 20% | >40% = 100, 25-40% = 75, 15-25% = 50, 5-15% = 25, <5% = 0 |
| Member-to-member ratio | 20% | >70% = 100, 50-70% = 75, 30-50% = 50, 10-30% = 25, <10% = 0 |
| 30-day retention | 20% | >60% = 100, 40-60% = 75, 25-40% = 50, 10-25% = 25, <10% = 0 |
| Question answer rate | 15% | >90% = 100, 70-90% = 75, 50-70% = 50, 30-50% = 25, <30% = 0 |
| Satisfaction score | 10% | >8/10 = 100, 7-8 = 75, 6-7 = 50, 5-6 = 25, <5 = 0 |

**Score interpretation:**
- **80-100:** Thriving — optimize and scale
- **60-79:** Healthy — address weak dimensions
- **40-59:** Warning — focused intervention needed
- **20-39:** Critical — fundamental strategy review
- **0-19:** Emergency — consider restart or pivot

### Benchmarks by Community Size

| Metric | <100 | 100-500 | 500-2000 | 2000-10000 | 10000+ |
|--------|------|---------|----------|------------|--------|
| DAU/MAU | 30-50% | 25-40% | 20-35% | 15-30% | 10-25% |
| Messages/day | 10-30 | 30-100 | 100-500 | 500-2000 | 2000+ |
| Lurker rate | 60-70% | 70-80% | 80-90% | 85-95% | 90-95% |
| Churn/month | 5-10% | 8-15% | 10-20% | 15-25% | 15-25% |
| Staff ratio | 1:20 | 1:50 | 1:100 | 1:200 | 1:500 |

---

## Phase 10: Scaling & Advanced Patterns

### Scaling Milestones

**0-100 members: "The Campfire"**
- You (founder) are in every conversation
- Personally welcome every member
- Hand-pick early members for culture fit
- Focus: relationships > content > growth

**100-500 members: "The Village"**
- Recruit first champions/moderators
- Implement role system
- Start weekly programming
- Focus: engagement loops > growth

**500-2000 members: "The Town"**
- Formalize moderation team
- Launch premium tier
- Sub-communities/topic channels
- Focus: retention > growth > monetization

**2000-10000 members: "The City"**
- Full moderator team with shifts
- Ambassador program
- Events team
- Focus: culture maintenance > scaling > revenue

**10000+ members: "The Metropolis"**
- Regional/topic sub-communities
- Paid community manager
- Partner/sponsor program
- Focus: governance > decentralization > sustainability

### Community-Led Growth (CLG)

**Turning community into a growth engine for your product/business:**

1. **Support deflection:** Community answers questions → reduces support costs
2. **Product feedback loop:** Community surfaces bugs/requests → better product → happier customers
3. **Social proof factory:** Member success stories → testimonials → acquisition
4. **Content engine:** Members create content → SEO + social → new members
5. **Referral machine:** Happy members → invite peers → organic growth

**Metrics that prove community ROI to leadership:**
- Support tickets deflected ($ saved)
- Feature requests surfaced → shipped
- NPS of community members vs non-members
- Customer lifetime value: community vs non-community
- Pipeline influenced by community (B2B)

### Multi-Platform Strategy

```yaml
multi_platform:
  primary: ""       # Where deep conversations happen
  secondary: ""     # Where discovery happens
  distribution: ""  # Where content gets amplified
  
  example:
    primary: "Discord (core community)"
    secondary: "Reddit (discovery + SEO)"
    distribution: "Twitter + LinkedIn (content funnel)"
    
  sync_rules:
    - "Best community discussions → social media highlights"
    - "Social conversations → invite to community"
    - "Reddit answers → also post in community knowledge base"
    - "Never cross-post everything — curate"
```

---

## Phase 11: Difficult Situations Playbook

### Scenario 1: Toxic Member Who's Also a Top Contributor

1. Private DM: specific examples of problematic behavior
2. "Your contributions are genuinely valuable. AND this behavior is hurting the community."
3. Clear expectations: "Here's specifically what needs to change"
4. 2-week observation period
5. If unchanged: remove. No one is bigger than the community.

### Scenario 2: Community Drama / Public Conflict

1. Don't delete (unless rule-breaking) — it looks like censorship
2. Lock the thread: "Pausing this for everyone to cool down"
3. Post a measured response acknowledging both sides
4. Address structural issues that caused the conflict
5. If recurring: create explicit policy and announce it

### Scenario 3: Growth Has Stalled

**Diagnostic questions:**
- Is the value proposition still clear and relevant?
- Are existing members happy? (Ask them)
- Where are potential members finding out about us? (Or not?)
- Has a competitor emerged?
- Is the content stale or repetitive?

**Recovery tactics:**
1. Member interviews (5-10): "Why did you join? What keeps you here? What's missing?"
2. Relaunch energy: new event series, updated branding, "Season 2" framing
3. Strategic cross-promotion with 3 adjacent communities
4. Content audit: kill what's not working, double down on what is
5. Invite 10 "anchor members" who bring energy

### Scenario 4: Key Moderator/Champion Leaves

1. Thank them publicly and genuinely
2. Transition responsibilities over 2 weeks (not overnight)
3. Identify successor from active members
4. Document everything they did (processes, not just duties)
5. Alumni role — keep the door open

### Scenario 5: Platform Migration

1. Announce 4-6 weeks in advance with clear reasons
2. Run both platforms in parallel for 2-4 weeks
3. Make migration easy: step-by-step guide, welcome wagon on new platform
4. Migrate content/resources first, then direct conversations
5. Accept 20-40% member loss as normal — focus on retaining active members
6. Post-migration: gather feedback, fix pain points fast

---

## Phase 12: Community Audit & Review

### Monthly Review Checklist

- [ ] Update health dashboard metrics
- [ ] Review moderation log — patterns or recurring issues?
- [ ] Check channel activity — any dead channels to archive?
- [ ] Review onboarding completion rate — bottlenecks?
- [ ] Read 20 random conversations — what's the vibe?
- [ ] Check champion program — anyone burning out? New candidates?
- [ ] Review growth sources — where are new members coming from?
- [ ] Content audit — which programming gets engagement? What falls flat?
- [ ] Revenue check (if monetized) — conversion rate, churn, ARPMM
- [ ] Member feedback — any recurring requests or complaints?

### Quarterly Strategic Review

```yaml
quarterly_review:
  what_worked:
    - ""
  what_didnt:
    - ""
  member_feedback_themes:
    - ""
  biggest_risk:
    - ""
  next_quarter_priorities:
    1: ""
    2: ""
    3: ""
  experiments_to_run:
    - ""
  kill_list:
    - ""  # What to stop doing
```

### 100-Point Community Quality Rubric

| Dimension | Weight | Score (0-10) | Weighted |
|-----------|--------|-------------|----------|
| Clear mission & value prop | 10% | | |
| Onboarding experience | 10% | | |
| Content quality & programming | 15% | | |
| Member engagement (depth, not just volume) | 15% | | |
| Moderation & safety | 10% | | |
| Growth trajectory | 10% | | |
| Member-to-member connections | 15% | | |
| Retention & lifecycle management | 15% | | |
| **TOTAL** | **100%** | | **/100** |

---

## Natural Language Commands

| Command | What It Does |
|---------|-------------|
| "Design my community" | Full Phase 1-2 brief with architecture |
| "Create community guidelines" | Custom guidelines from Phase 4 template |
| "Plan this week's content" | Generate weekly content calendar |
| "Set up onboarding flow" | Complete onboarding sequence |
| "Build growth strategy" | 12-tactic plan prioritized for your stage |
| "Design monetization model" | Revenue strategy with pricing |
| "Plan an event" | Event template with pre/during/post |
| "Run community health check" | Full metrics dashboard and score |
| "Re-engage inactive members" | Recovery playbook with messages |
| "Build champion program" | Champion identification and development plan |
| "Handle [situation]" | Scenario-specific playbook from Phase 11 |
| "Quarterly review" | Full audit with recommendations |

---

*Built by [AfrexAI](https://afrexai-cto.github.io/context-packs/) — AI-powered business systems that actually work.*
