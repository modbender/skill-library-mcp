---
name: proposal-interview
description: Structured interview to discover personal facts and generate reusable, approved statements for proposals and cover letters. Creates personalized content for Upwork, LinkedIn, email, job portals, and grants. Multi-person support. Use when drafting proposals, cover letters, or building a library of professional statements.
---

# Proposal & Cover Letter Discovery Interview

**This is NOT a CV builder.** This skill creates high-quality, reusable statements for proposals and cover letters by running a structured interview to extract personal-but-professional facts.

## The Problem with Generic Letters

Generic cover letter and proposal writers are bland because they don't know YOU. They can't capture:
- Your living in Dubai and Seoul, and what that taught you about cross-cultural collaboration
- The robotics project you tinkered with at home that shows your passion
- The class that changed how you think about systems
- The boring job that taught you what quality really means
- Your unfair advantage that clients actually hire you for

This skill solves that through **interview → facts → statements → approval → assembly**.

## How It Works

### Phase 1: Discovery Interview
The skill asks structured questions to extract:
- Geographic and cultural context (places lived, travel, cross-cultural work)
- Work experience beyond the resume (lessons, standout moments, what colleagues rely on you for)
- Education (specific classes, formative learning, projects)
- Projects and proof (side projects, demos, artifacts)
- Awards and recognition (scholarships, competitions, certifications)
- Past hobbies (skills hidden in former interests)
- Books and influences (working philosophy)
- The boring stuff (what you learned from frustrating work)
- Proposal leverage (what you want to be hired for)
- Constraints (topics to avoid, boundaries)

### Phase 2: Statement Generation
From gathered facts, the skill drafts **3-8 candidate statements** per round. Each statement:
- Is grounded in real facts (no invention)
- Is usable in proposals/cover letters
- Has multiple variants (Upwork short, standard cover letter, technical/proof-first)
- Has tags (#leadership #robotics #global-living)

### Phase 3: Approval Loop
You review each statement: **Approve / Edit / Reject**
- Approved statements go into `statements.md`
- Edits refine the statement and update preferences
- Rejections inform future drafting

### Phase 4: Assembly (Future)
When you need a proposal, the skill pulls relevant approved statements and assembles them for the target platform and company.

## Storage Model: Folders + Files

**All data is stored INSIDE the skill folder** at:
`skills/proposal-interview/personal/` and `skills/proposal-interview/companies/`

### Directory Structure

```
skills/proposal-interview/
  personal/
    <person_id_or_name>/
      profile.md           # Current snapshot: name, what they do, where, objectives (ALWAYS READ FIRST)
      user.md              # Raw facts about this person (APPEND ONLY - NEVER DELETE)
      statements.md        # Approved statements (APPEND ONLY - NEVER DELETE APPROVED STATEMENTS)
      preferences.md       # Writing style preferences
      coherence.md         # Conflicts, gaps, clarifications needed

  companies/
    <company_or_initiative_slug>/
      profile.md           # Current snapshot: company name, what they do, where, objectives
      org.md               # Company facts, domain, relationships (APPEND ONLY - NEVER DELETE)
      statements.md        # Company-specific approved statements (APPEND ONLY - NEVER DELETE)
      preferences.md       # Company-specific style preferences
      projects.md          # (Optional) Project history with this org
      coherence.md         # (Optional) Company-specific conflicts/gaps
```

### Routing Rules

**Personal vs Company:**
- Personal facts → `skills/proposal-interview/personal/<person>/user.md`
- Company-specific facts → `skills/proposal-interview/companies/<slug>/org.md`

**Multi-person support:**
- Default: current user
- If doing this for someone else (e.g., spouse), use `skills/proposal-interview/personal/<their_name>/`

**Relationships:**
- If a company has an owner/founder relevant to letters, record in `org.md`

### File Rules (Append-Only)

⚠️ **CRITICAL FOR ALL MODELS - READ THIS:**

**NEVER DELETE OR REWRITE LINES IN ANY FILE.**
**ALWAYS APPEND. NEVER DELETE. ONLY ADD.**

This applies to:
- ❌ NEVER delete approved statements from `statements.md`
- ❌ NEVER delete facts from `user.md` or `org.md`
- ❌ NEVER rewrite existing lines
- ✅ ALWAYS append new information
- ✅ ALWAYS read existing files before appending

If a conflict is detected:
1. Append the new info (don't delete the old info)
2. Append a note to `coherence.md`
3. Ask a clarifying question next round

**profile.md is the EXCEPTION** - this file CAN be edited/rewritten as it's a current snapshot, not a permanent record.

#### profile.md (personal or company) — ALWAYS READ FIRST

Current snapshot of the person or company. Simple, clear, updated format.

**Personal profile.md format:**
```
# [Full Name]

## What They Do
[Simple description - "AI consultant specializing in OpenClaw implementations and AI strategy"]

## Where Based
[Location - "Amsterdam, Netherlands" or "Remote" or "San Francisco, CA"]

## Primary Objective
[Main goal for proposals/applications - "Secure OpenClaw implementation contracts with mid-size tech companies"]

## Secondary Objective (Optional)
[Secondary goal - "Build reputation as AI strategy consultant for startups"]

## Current Status
[Brief context - "Actively applying to Upwork projects and direct outreach to companies"]

## Last Updated
[Date - "2026-02-24"]
```

**Company profile.md format:**
```
# [Company Name]

## What They Do
[Simple description - "Industrial automation, warehouse robotics"]

## Where Based
[Location - "San Francisco, CA"]

## Primary Relationship Objective
[Why we're tracking them - "Potential client for OpenClaw implementation"]

## Secondary Objective (Optional)
[Additional context - "Investor prospect for Way Back Project"]

## Key Contact
[Name and role if known - "Jane Doe, CTO"]

## Last Updated
[Date - "2026-02-24"]
```

**Workflow:** Always read `profile.md` FIRST (before user.md, statements.md, etc.) to get current context.

#### user.md (personal) — ⚠️ APPEND ONLY, NEVER DELETE ⚠️

**CRITICAL REMINDER: Before writing to this file, ALWAYS read existing content first to avoid duplicates and incorporate existing facts.**

Raw facts and concise notes. Facts only, no polished marketing.

**Example:**
```
- Lived in Dubai 2018-2020, worked with clients across EMEA
- Lived in South Korea 2015-2017, learned Korean to intermediate level
- Built robotic arms at home using Arduino and 3D-printed parts
- Took MIT OCW Machine Learning course, applied to personal project predicting stock trends
- Won regional robotics competition in high school, team captain
- Former competitive swimmer (stopped 2016), coached youth swim team 2017-2018
- Speaks English (native), Korean (intermediate), Arabic (basic)
- Prefers remote work, available 9am-5pm EST
```

#### statements.md (personal or company) — ⚠️ APPEND ONLY, NEVER DELETE APPROVED STATEMENTS ⚠️

**CRITICAL REMINDER: Once a statement is approved and written here, NEVER delete it. Only append new approved statements. Read existing statements before generating new ones to avoid duplicates.**

User-approved statements only. Each entry includes:
- Statement text
- Tags
- Evidence pointer (which facts support this)

**Example:**
```
---
statement: "I bring a global perspective from living and working across three continents—from collaborating with EMEA clients in Dubai to navigating cross-cultural teams in South Korea. I've learned to adapt communication styles and build trust across cultures, which is essential for remote, distributed work."
tags: #global-living #dubai #korea #cross-cultural #remote-work #client-facing
evidence: user.md lines 1-2, 7
platform: standard cover letter
---

statement: "I'm passionate about robotics and hands-on engineering—I've built robotic arms at home using Arduino and 3D-printed custom parts. This isn't just work for me; it's how I spend my evenings."
tags: #robotics #hands-on #passion #arduino #3d-printing #side-projects
evidence: user.md line 3
platform: Upwork short pitch, technical/proof-first
---

statement: "My background in competitive swimming taught me discipline and coaching—skills I later applied when coaching a youth swim team. I understand how to break down complex skills, provide feedback, and build confidence."
tags: #coaching #leadership #discipline #teaching #past-hobbies
evidence: user.md line 6
platform: standard cover letter, leadership-focused
---
```

#### preferences.md (personal or company)
Writing style preferences by platform.

**Example:**
```
# Writing Preferences

## Tone
- Confident but not arrogant
- Warm and approachable
- Direct, minimal fluff
- Technical when relevant (show don't just tell)

## Platform Settings

### Upwork
- Length: 2-4 sentences + optional 2-3 bullet proof points
- Structure: Hook → proof → call-to-action
- Metrics-first when available

### LinkedIn / Email Outreach
- Length: 3-5 sentences
- Friendly, personal, brief
- Lead with common ground or mutual connection

### Job Portal / Formal Cover Letter
- Length: 3-4 paragraphs
- Structured: intro → experience/proof → why this role → close
- Slightly more formal tone

### Grants / Proposals
- Length: longer, evidence-heavy
- Structure: narrative with metrics and citations
- Emphasize impact and outcomes

## Avoid List
- Buzzwords: "synergy", "rockstar", "ninja", "guru"
- Overused phrases: "I'm passionate about", "proven track record"
- Sensitive info: exact salary history, medical details

## Structure Preferences
- Prefer bullets for proof points
- Use short paragraphs (3-4 sentences max)
- Open with strongest differentiator
- Close with clear next step
```

#### org.md (company)
Company/initiative facts.

**Example:**
```
# Acme Robotics Inc

## Domain
- Industrial automation, warehouse robotics
- Focus on AI-driven pick-and-place systems
- Series B funded, 50-200 employees

## Key People
- Jane Doe, Founder/CEO (former Google engineer)
- John Smith, CTO (robotics background)

## Positioning
- "We make warehouses smarter"
- Emphasis on practical, deployable solutions (not research)

## Constraints
- Remote-first company
- Looking for senior engineers with production experience

## History with User
- Applied via Upwork 2024-02-20
- Initial call scheduled for 2024-02-28
```

#### coherence.md (optional but recommended)
Track conflicts, gaps, clarifications needed.

**Example:**
```
# Coherence Notes

## Possible Conflicts
- 2024-02-24: User said "intermediate Korean" but earlier mentioned "basic conversational". Clarify level.

## Missing Info
- Need timeframe for Dubai work (years? months?)
- Need scope/metrics for robotics project (how many built? any demos?)
- Need GPA or honors for MIT OCW course mention

## Clarifications Needed
- Is Arabic "basic" = conversational or just tourist phrases?
- Does "remote work preference" mean fully remote only, or hybrid OK?
```

## How to Use This Skill

### ⚠️ QUESTION CADENCE - VERY IMPORTANT ⚠️

**First time with a person (onboarding):**
- Ask **10 initial discovery questions** in one session
- Then generate first batch of statements

**All subsequent sessions (updates/refinement):**
- Ask only **3 questions per round**
- Then generate statements from those 3 answers
- This keeps sessions manageable and can run via cron for continuous learning

**Why this matters:** You can schedule this skill as a cron job to periodically learn more about the person (every week, every month, etc.). The 3-question pattern keeps token usage reasonable while continuously building your statement library.

### Starting Fresh (First Run)

1. **Read this skill document** to understand the workflow

2. **Create folder structure** if it doesn't exist:
   ```bash
   mkdir -p skills/proposal-interview/personal/<user_name> skills/proposal-interview/companies
   ```

3. **Create `profile.md`** with current snapshot (name, what they do, where, objectives)

4. **Explain the process to the user:**
   "I'm going to ask you **10 onboarding questions** to build your initial profile. After this first session, future updates will only ask **3 questions at a time** to keep things manageable. This can even run on a schedule to continuously learn more about you."

5. **Run onboarding questions** (see below)

6. **Ask the 10 initial discovery questions**

7. **Draft 3-8 statements**, get approval, store approved ones

8. **Future sessions: switch to 3-question rounds**

### Continuing Work (Existing User) — ⚠️ READ BEFORE WRITING ⚠️

**CRITICAL: Always read existing files BEFORE asking questions or appending facts. This prevents duplicates and helps you incorporate existing knowledge.**

1. **Read existing files IN THIS ORDER**:
   - `skills/proposal-interview/personal/<user>/profile.md` **(READ FIRST - current context)**
   - `skills/proposal-interview/personal/<user>/user.md` (facts gathered - NEVER DELETE, ONLY APPEND)
   - `skills/proposal-interview/personal/<user>/statements.md` (approved statements - NEVER DELETE, ONLY APPEND)
   - `skills/proposal-interview/personal/<user>/preferences.md` (style guide)
   - `skills/proposal-interview/personal/<user>/coherence.md` (gaps/conflicts)

2. **Ask only 3 new questions** (fill gaps, drill down on threads)

3. **Append new facts** to `user.md` (NEVER delete existing facts, always append)

4. **Draft 2-4 new statements** based on new facts

5. **Get approval**, append to `statements.md` (NEVER delete approved statements, always append)

### Working with a Company/Initiative

1. **Create company folder**: `skills/proposal-interview/companies/<slug>/`
2. **Ask company-specific questions**:
   - What do they do? Domain?
   - Key people? Relationships?
   - Why is user interested?
   - What's the user's angle/fit?

3. **Store company facts** in `org.md`
4. **Draft company-specific statements** (e.g., "why I'm a fit for Acme Robotics")
5. **Store in company's `statements.md`**

### Question Cadence (Hard Requirement)

**First-ever run for a person:**
- Ask **exactly 10 questions** before generating statements

**After first batch:**
- Ask **3 questions per round**
- Generate statements
- Get feedback
- Update files
- Repeat

**If user gives very short answers:**
- Comment briefly: "That's shorter than ideal, but I can work with it."
- Ask a follow-up only if critical

## Onboarding Script (Always First)

When starting with a new person, ask these setup questions:

### 1. Who is this for?
"Are you creating this for yourself, or for someone else (e.g., spouse, client)?"
- If for someone else, create `skills/proposal-interview/personal/<their_name>/`

### 2. Which platforms do you use?
"Which platforms do you apply through? Check all that apply:
- Upwork / Freelance marketplaces
- LinkedIn (applications or outreach)
- Email outreach (cold/warm)
- Company career portals
- Grants / funding applications
- Other (specify)"

### 3. Style preferences per platform
For each platform they checked, ask:
"For [platform], what's your preferred style?
- Tone: confident / warm / direct / humble / technical / playful / formal
- Length: short (2-4 sentences) / medium (1-2 paragraphs) / long (3-4 paragraphs)
- Structure: bullets / narrative / metrics-first / story-first
- What does success look like? (get a reply / win a contract / advance to interview)"

### 4. What do you want to be hired for?
"What type of work do you want more of? What's your unfair advantage?"

### 5. Anything to avoid?
"Any topics, buzzwords, or sensitive info we should avoid in proposals?"

**After onboarding, write preferences to `skills/proposal-interview/personal/<user>/preferences.md`.**

## The 10 Initial Questions (Template)

After onboarding, ask these 10 questions (adapt based on their work/goals):

### 1. Geographic & Cultural Context
"Where have you lived or traveled that shaped how you work? (Dubai, Seoul, remote teams, etc.) Answer in 3 bullets or a short paragraph."

### 2. Work Beyond the Resume
"What have you learned in your work that doesn't fit neatly on a resume? What was surprisingly hard and how did you handle it?"

### 3. What Colleagues Rely On You For
"What do colleagues, clients, or teammates repeatedly come to you for? What's your 'thing'?"

### 4. Education & Formative Learning
"Any classes, courses, or learning experiences that changed how you think or work? (Formal or self-taught—include MOOCs, bootcamps, workshops.)"

### 5. Projects & Proof
"What's a project you're proud of that shows your skills? (Side project, work project, personal tinkering, GitHub repo, portfolio piece.) Describe scope and outcome."

### 6. Awards & Recognition
"Any awards, scholarships, competitions, certifications, or public recognition? (School, work, industry, community.)"

### 7. Past Hobbies
"What hobbies did you used to do a lot but don't anymore? What skills did they build? (Sports, arts, teaching, community involvement, etc.)"

### 8. Books & Influences (Optional)
"Any books, ideas, or people that shaped your approach to work or leadership? (Use sparingly, only if it produces something concrete.)"

### 9. The Boring Story
"Tell me about a role, class, or project you found boring or frustrating. What did you learn? What do you now avoid or demand in your work?"

### 10. Your Unfair Advantage
"If you had to pitch yourself in one sentence, what's your unfair advantage? What makes you different from 100 other people with similar skills?"

**After these 10 questions:**
1. Extract facts → append to `user.md`
2. Draft 3-8 statements (see below)
3. Get approval
4. Store approved statements → `statements.md`
5. Update `preferences.md` based on feedback

## The 3-Question Round (Subsequent Runs)

After the initial 10 questions, switch to asking **3 questions per round**.

**How to choose the next 3 questions:**

1. **Check `coherence.md`** for gaps or conflicts that need clarification
2. **Review `statements.md`** to see which categories are under-represented
3. **Drill down on strong threads**:
   - If user mentioned robots → ask about tools, scope, outcomes, demos
   - If user mentioned Dubai/Korea → ask about cross-cultural teamwork, languages, client communication
   - If user mentioned a specific company → ask domain-specific questions

**Question design principles:**
- Allow short or long replies
- Use phrasing like: "Answer in 3 bullets or a short paragraph."
- If dates/metrics uncertain: "Approximate is fine."
- Always explain why it matters (briefly): "This helps me write more personal proposals."

**After each 3-question round:**
1. Extract facts → append to `user.md` or `org.md`
2. Draft 2-4 new statements
3. Get approval
4. Update files

## Statement Drafting + Approval Loop

### When to Draft Statements

- After the first 10 questions (initial run)
- After every 3-question round (subsequent runs)

### How to Draft Statements

Generate **3-8 candidate statements** per round.

**Each statement must:**
- Be grounded in gathered facts (no invention)
- Be usable in proposals/cover letters
- Be written in multiple variants when helpful:
  - **Upwork short pitch** (1-2 lines)
  - **Standard cover letter** (2-4 sentences)
  - **Technical/proof-first variant** (metrics, tools, outcomes)

**Statement structure:**
```
---
statement: "[The actual statement text]"
tags: #tag1 #tag2 #tag3
evidence: user.md line X, org.md line Y
platform: Upwork short / standard cover letter / technical
---
```

### Approval Process

**For each statement, ask the user:**

"Here's a draft statement. Choose one:
1. **Approve** - Store as-is
2. **Edit** - Suggest changes (I'll rewrite and confirm)
3. **Reject** - Don't store, move on"

**If user chooses Edit:**
- Propose a rewrite
- Get confirmation
- If confirmed, store

**If user chooses Approve:**
- **Read existing `statements.md` first** to avoid duplicates
- **Append** the approved statement to `statements.md` in the correct folder (`skills/proposal-interview/personal/` or `skills/proposal-interview/companies/`)
- **NEVER delete previously approved statements**

**If user chooses Reject:**
- Don't store (obviously, since it's rejected)
- Note the rejection reason in `preferences.md` if it reveals a style preference

⚠️ **CRITICAL REMINDER: Once a statement is approved and appended to statements.md, it must NEVER be deleted. Only append new approved statements.**

### Update Preferences Based on Feedback

After each approval round, update `preferences.md` if you learn:
- Tone preferences (user prefers "confident" over "humble")
- Length preferences (user always wants shorter)
- Structure preferences (user likes bullets over narrative)
- Word choice (user hates "passionate", prefers "focused on")

## Platform-Aware Statement Variants

### Upwork Short Pitch (2-4 sentences + bullets)

**Example:**
```
I've built robotic arms at home using Arduino and 3D-printed parts—this isn't just work for me, it's how I spend my evenings. I bring 5 years of experience with ROS, Python, and mechatronics, plus a global perspective from working with EMEA and APAC clients.

• Built 3 functional robotic arms with custom inverse kinematics
• MIT OCW Machine Learning graduate (applied to robotics path planning)
• Available for 20-30 hrs/week, overlap with US/EU time zones
```

### Standard Cover Letter (2-4 sentences)

**Example:**
```
I bring a global perspective from living and working across three continents—from collaborating with EMEA clients in Dubai to navigating cross-cultural teams in South Korea. I've learned to adapt communication styles and build trust across cultures, which is essential for remote, distributed work. My technical background in robotics and hands-on engineering complements my ability to work with diverse teams and deliver practical solutions.
```

### Technical / Proof-First Variant

**Example:**
```
I've designed and built three functional robotic arms using Arduino, custom inverse kinematics algorithms (Python), and 3D-printed components. I completed MIT OCW's Machine Learning course and applied it to a path-planning optimization project that reduced movement time by 18%. My GitHub portfolio includes ROS packages, simulation environments (Gazebo), and documentation that's been forked 40+ times.
```

### Email Outreach (3-5 sentences, friendly)

**Example:**
```
Hi [Name],

I noticed Acme Robotics is hiring for a Senior Robotics Engineer. I've been tinkering with robotic arms at home for years—building them from scratch using Arduino and 3D-printed parts—and I'd love to bring that hands-on passion to a team working on real-world automation challenges.

I've worked with clients across Dubai and South Korea, so I'm comfortable with remote collaboration and adapting to different working styles. Would you be open to a quick call to discuss the role?

Best,
[User]
```

### Grant / Long Proposal (Evidence-heavy, structured)

**Example:**
```
My unique combination of hands-on robotics experience and cross-cultural collaboration positions me well for this initiative. Over the past four years, I have:

1. **Designed and built functional robotic systems**: I independently developed three robotic arms using Arduino microcontrollers, custom inverse kinematics algorithms (Python), and 3D-printed mechanical components. These projects demonstrate my ability to work across hardware, software, and mechanical design.

2. **Applied machine learning to robotics**: I completed MIT OpenCourseWare's Machine Learning curriculum and applied those techniques to optimize path planning for robotic arm movement, achieving an 18% reduction in task completion time.

3. **Collaborated across cultures and time zones**: My professional experience spans Dubai (EMEA clients) and South Korea (APAC teams), where I learned to navigate language barriers, cultural differences, and asynchronous communication. I speak English natively, Korean at an intermediate level, and basic Arabic.

This background enables me to contribute both technical expertise and the adaptability required for distributed, international teams.
```

## Adaptive Question Generation

### How to Decide What to Ask Next

**Maintain an internal checklist** of what categories are covered:
- [ ] Geographic / cultural context
- [ ] Work experience beyond resume
- [ ] Education / formative learning
- [ ] Projects / proof
- [ ] Awards / recognition
- [ ] Past hobbies
- [ ] Books / influences
- [ ] Boring stories / frustrations
- [ ] Proposal leverage / unfair advantage
- [ ] Constraints / boundaries

**Prioritize questions that:**
- Fill gaps in under-represented categories
- Drill down on strong signals (unique experiences like living abroad)
- Produce demonstrable proof (projects, metrics, artifacts)
- Align to target work (if a company/initiative is provided)

### Triggered Recall Questions

**If user mentions robots:**
- "What tools did you use? What was the scope? Any metrics or demos?"
- "What's sitting in your office/workshop right now? How does it map to client value?"

**If user mentions Dubai/Korea:**
- "Tell me about a time cross-cultural communication was challenging. How did you adapt?"
- "What languages do you speak? At what level?"
- "How did living there change your approach to remote work or global clients?"

**If user mentions a specific job/company:**
- Prioritize questions that produce domain-aligned statements
- Store company-specific learnings in `skills/proposal-interview/companies/<slug>/`

### Fact Capture Rules (Very Explicit) — ⚠️ READ THEN APPEND ⚠️

**CRITICAL WORKFLOW - DO THIS EVERY TIME:**

**BEFORE appending any facts:**
1. **READ the existing `user.md` or `org.md` file** to check what's already captured
2. **Check for duplicates** - don't re-add facts that are already there
3. **Incorporate existing facts** when generating statements

**After each user answer:**

1. **Read existing facts first** (see above)

2. **Extract discrete factual lines** from the answer

3. **Append them** to the correct file (NEVER delete existing content):
   - Personal facts → `skills/proposal-interview/personal/<user>/user.md`
   - Company facts → `skills/proposal-interview/companies/<slug>/org.md`

4. **If a fact is uncertain**, ask a one-line confirmation before writing:
   - "You mentioned living in Dubai—was that 2018-2020, or different years?"

5. **Never delete or rewrite** previous lines. If a conflict is detected:
   - Append the new info (DO NOT DELETE THE OLD INFO)
   - Append a "possible conflict" note to `coherence.md`
   - Ask a targeted clarifying question next round

**REMINDER: APPEND ONLY. NEVER DELETE. ALWAYS READ BEFORE WRITING.**

## Example Session Flow

### Session 1: Onboarding + Initial 10 Questions

```
[Onboarding]
Me: "Are you creating this for yourself, or for someone else?"
User: "For myself."

Me: "Which platforms do you apply through? Upwork, LinkedIn, email, job portals, grants?"
User: "Upwork and LinkedIn mostly."

Me: "For Upwork, what's your preferred style? Tone, length, structure?"
User: "Confident but not cocky, short (2-4 sentences + bullets), metrics-first."

[Preferences captured → write to preferences.md]

[Initial 10 Questions]
Me: "Question 1: Where have you lived or traveled that shaped how you work?"
User: "I lived in Dubai for 2 years (2018-2020) and Seoul for 3 years (2015-2017). Dubai taught me how to work with clients across EMEA time zones. Korea taught me patience and indirect communication styles."

[Extract facts → append to user.md]
- Lived in Dubai 2018-2020, worked with EMEA clients
- Lived in Seoul 2015-2017, learned indirect communication styles

Me: "Question 2: What have you learned that doesn't fit neatly on a resume?"
User: "I learned how to handle ambiguity. Clients don't always know what they want, and I've gotten good at asking clarifying questions early."

[Extract facts → append to user.md]
- Skilled at handling ambiguous client requirements, asks clarifying questions early

[... continue through 10 questions ...]

[After 10 questions: Draft statements]
Me: "Based on what you've shared, here are 5 draft statements. For each, tell me: Approve / Edit / Reject."

Statement 1 (Upwork short):
"I bring a global perspective from living in Dubai and Seoul, where I collaborated with EMEA and APAC clients across time zones. I'm comfortable with remote work and cross-cultural communication."
Tags: #global-living #dubai #korea #remote-work #cross-cultural

User: "Approve."

[Write to statements.md]

Statement 2 (Standard cover letter):
"I excel at navigating ambiguous client requirements. Early in projects, I ask targeted clarifying questions to uncover what clients really need—even when they don't know themselves yet."
Tags: #client-facing #ambiguity #discovery #consultative

User: "Edit—sounds too soft. Make it more confident."

Me: "How about: 'I thrive in ambiguous situations. When clients aren't sure what they need, I ask the right questions upfront to define clear goals and avoid costly rework later.'"

User: "Perfect. Approve."

[Write revised version to statements.md, update preferences.md: prefer confident tone]

[... continue through all statements ...]
```

### Session 2: 3-Question Round

```
[Read existing files: user.md, statements.md, preferences.md, coherence.md]

Me: "I see you mentioned robotics earlier. Let's drill down on that."

Question 1: "You said you built robotic arms at home. How many? What tools and frameworks? Any demos or GitHub repos?"
User: "I've built 3 so far. Arduino for controllers, Python for kinematics, 3D-printed the parts. I have videos on YouTube and code on GitHub—one repo has 40+ forks."

[Extract facts → append to user.md]
- Built 3 robotic arms at home: Arduino controllers, Python kinematics, 3D-printed parts
- YouTube demos, GitHub repo with 40+ forks

Question 2: "What was the hardest part of building them?"
User: "Getting the inverse kinematics right. Took me weeks to debug the math. Eventually used a library but modified it for my joint constraints."

[Extract facts → append to user.md]
- Struggled with inverse kinematics math, debugged and modified existing library

Question 3: "How does this hobby map to the type of work you want?"
User: "I want to work on practical, deployable robotics—not research. I like solving real engineering constraints, not publishing papers."

[Extract facts → append to user.md]
- Prefers practical/deployable robotics over research, enjoys engineering constraints

[Draft new statements based on these 3 answers]
Me: "Here are 3 new draft statements based on your robotics work. Approve / Edit / Reject?"

Statement (Technical/proof-first):
"I've built 3 functional robotic arms from scratch using Arduino, custom Python kinematics, and 3D-printed components. My GitHub repo has been forked 40+ times, and I've published video demos on YouTube. I focus on practical, deployable solutions—not academic research."
Tags: #robotics #arduino #python #github #practical #hands-on

User: "Approve."

[Write to statements.md]

[... continue ...]
```

## Safety and Integrity

### No Invented Achievements
- Only write statements grounded in gathered facts
- If user didn't mention it, don't make it up

### No Sensitive Data (Unless Explicit)
- Don't include salary history, medical details, or private info unless user explicitly provides and approves it

### If User Requests Exaggeration or Fabrication
- Refuse politely: "I can't invent achievements, but I can help you frame what you've done more compellingly. Let's work with the real facts."
- Offer truthful alternatives

### Conflicts and Uncertainty
- If something doesn't add up, note it in `coherence.md` and ask for clarification
- Never guess or fill in blanks

## Running as a Cron Job (Continuous Learning)

You can schedule this skill to run periodically (weekly, monthly) to continuously learn more about the person and build their statement library.

**Example cron job payload:**
```json
{
  "kind": "agentTurn",
  "message": "Run the proposal-interview skill for Mike. This is a continuation session (not first run), so ask 3 new questions, gather facts, draft 2-4 statements, and get approval. Focus on filling gaps in his profile or drilling deeper on OpenClaw implementation experience."
}
```

**Benefits of cron-based learning:**
- Builds statement library over time without overwhelming the user
- 3-question rounds keep sessions short and token-efficient
- Can be scheduled during low-activity periods
- Gradually captures more depth and nuance

**Important:** Always use the 3-question pattern for cron sessions, never the initial 10-question onboarding.

## Checklist: Every Run

⚠️ **CRITICAL CHECKS - READ THESE EVERY TIME:**

Before you start:
- [ ] Have I identified which person/company this is for?
- [ ] Have I read `profile.md` FIRST to get current context?
- [ ] Have I read existing `user.md` or `org.md` to see what facts are already captured?
- [ ] Have I read existing `statements.md` to avoid duplicating approved statements?
- [ ] Have I read `preferences.md` and `coherence.md`?
- [ ] Have I determined if this is a first run (10 questions) or continuation (3 questions)?

During the interview:
- [ ] Am I asking questions that allow short or long replies?
- [ ] Am I **reading existing facts BEFORE appending** to avoid duplicates?
- [ ] Am I **appending** facts (NEVER deleting) to the correct file (`user.md` or `org.md`)?
- [ ] Am I noting conflicts in `coherence.md` instead of rewriting?
- [ ] Am I tagging statements with relevant keywords?

When drafting statements:
- [ ] Have I read existing statements to avoid duplicates?
- [ ] Are all statements grounded in gathered facts?
- [ ] Have I written variants for relevant platforms (Upwork, cover letter, technical)?
- [ ] Have I asked: Approve / Edit / Reject for each statement?
- [ ] Have I **appended** approved statements (NEVER deleting old ones) to `statements.md`?
- [ ] Have I updated `preferences.md` based on user feedback?

After the session:
- [ ] Have I noted any gaps or missing info in `coherence.md`?
- [ ] Have I identified categories that need more coverage for next round?
- [ ] Have I maintained the append-only rule (no deletions, only additions)?
- [ ] Did I update `profile.md` if any current information changed?

## Summary

This skill transforms generic proposals into personalized, compelling letters by:
1. **Interviewing** you to extract unique, personal-but-professional facts
2. **Drafting** reusable statements grounded in those facts
3. **Refining** statements through an approval loop
4. **Storing** approved statements for future assembly

The result: a library of high-quality, pre-approved statements you can mix and match for any proposal, tailored to the platform and company.

**Next steps:**
- Run the onboarding + 10 initial questions
- Approve your first batch of statements
- Run 3-question rounds to fill gaps and drill down
- Build a library of 20-50 statements covering different angles
- (Future) Use those statements to assemble custom proposals on demand

---

**File locations:**
- Personal: `skills/proposal-interview/personal/<name>/`
- Companies: `skills/proposal-interview/companies/<slug>/`
- Always append, never delete
- Check `coherence.md` for gaps
