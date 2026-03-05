# Brand Strategy Engine

Complete brand building and go-to-market system — from identity foundations through positioning, messaging, visual systems, and launch execution. Works for solopreneurs, startups, and established businesses rebranding.

---

## Phase 1: Brand Discovery & Foundations

Strategy before aesthetics. Every visual decision flows from these answers.

### 1.1 Brand Purpose Statement

Answer in one sentence: **Why does this business exist beyond revenue?**

Template: "We exist to [verb] [audience] by [method] so they can [outcome]."

Examples:
- "We exist to arm solo consultants with enterprise-grade tools so they can compete with agencies."
- "We exist to simplify legal compliance for startups so founders can focus on building."

**Test:** If you removed your company, would anyone notice? The answer reveals your true purpose.

### 1.2 Brand Values (Pick Exactly 3)

More than 3 = forgettable. Fewer = too vague. Each value needs a **behavior** — what it looks like in practice.

```yaml
brand_values:
  - value: "Radical Clarity"
    behavior: "We never use jargon. Every email, doc, and UI element passes the 'would my mom understand this?' test."
    anti_pattern: "Hiding behind buzzwords or complexity"
  - value: "Speed Over Perfection"
    behavior: "We ship MVPs in days, not months. We'd rather fix live than polish in private."
    anti_pattern: "Endless planning cycles, waiting for 'ready'"
  - value: "Skin in the Game"
    behavior: "We use our own products daily. Our pricing has a money-back guarantee."
    anti_pattern: "Recommending things we wouldn't buy ourselves"
```

### 1.3 Brand Personality (The Archetype Method)

Pick ONE primary archetype + ONE secondary flavor:

| Archetype | Core Drive | Voice Tone | Best For |
|-----------|-----------|------------|----------|
| **Sage** | Knowledge, truth | Authoritative, measured | Consulting, education, analytics |
| **Creator** | Innovation, vision | Inspiring, unconventional | Design, tech, creative agencies |
| **Hero** | Mastery, achievement | Bold, confident, direct | Fitness, coaching, enterprise tools |
| **Explorer** | Freedom, discovery | Adventurous, curious | Travel, startup tools, research |
| **Rebel** | Revolution, disruption | Provocative, irreverent | Challenger brands, indie products |
| **Caregiver** | Service, protection | Warm, reassuring | Healthcare, insurance, support |
| **Ruler** | Control, stability | Premium, authoritative | Finance, luxury, enterprise |
| **Everyman** | Belonging, honesty | Friendly, down-to-earth | Community tools, consumer products |
| **Magician** | Transformation | Visionary, mystical | AI, wellness, life coaching |
| **Jester** | Joy, humor | Witty, playful | Consumer apps, food, entertainment |
| **Lover** | Intimacy, experience | Sensual, emotional | Fashion, beauty, hospitality |
| **Innocent** | Simplicity, optimism | Clean, hopeful | Wellness, kids, organic products |

**Output format:**
```yaml
brand_personality:
  primary: "Rebel"
  secondary: "Sage"
  summary: "We challenge the status quo with data to back it up. Think punk rock meets MIT."
  we_are: ["bold", "evidence-driven", "unapologetic", "sharp"]
  we_are_not: ["corporate", "safe", "fluffy", "slow"]
```

### 1.4 Competitive Landscape Map

Before positioning, know the territory:

```yaml
competitive_map:
  category: "[Your market category]"
  competitors:
    - name: "[Competitor A]"
      positioning: "[How they position themselves]"
      strengths: ["...", "..."]
      weaknesses: ["...", "..."]
      price_tier: "premium|mid|budget"
      brand_vibe: "[1-3 words]"
    - name: "[Competitor B]"
      # ...
  white_space: "[Where NO competitor plays — this is your opportunity]"
  category_conventions: "[What everyone in this space does — colors, language, promises]"
  our_contrarian_angle: "[How we'll deliberately break conventions]"
```

---

## Phase 2: Positioning & Messaging

### 2.1 Positioning Statement (April Dunford Method)

Fill in each element, then combine:

```yaml
positioning:
  competitive_alternatives: "[What would customers use if you didn't exist?]"
  unique_capabilities: "[What you do that alternatives can't]"
  enabled_value: "[The measurable benefit those capabilities create]"
  best_fit_customers: "[Who cares MOST about that value — be specific]"
  market_category: "[The frame of reference that makes your value obvious]"
```

**Combined statement:**
"For [best_fit_customers] who [pain point], [Brand] is the [market_category] that [unique_capabilities]. Unlike [competitive_alternatives], we [enabled_value]."

**Positioning test — answer YES to all:**
- [ ] Can a 12-year-old understand what you do from this?
- [ ] Does it make clear who this is NOT for?
- [ ] Would a competitor cringe reading it? (If not, it's too generic)
- [ ] Does it contain a falsifiable claim, not just adjectives?

### 2.2 Messaging Architecture

Three layers — never mix them:

**Layer 1: Strategic Narrative (The Big Idea)**
- One paragraph that frames the world as changing, positions you as the guide
- Pattern: "The old way of [X] is broken because [shift]. Companies that [Y] are winning. [Brand] gives you [Z]."
- Used in: About page, pitch deck, keynote openings

**Layer 2: Value Propositions (3 Pillars)**
```yaml
value_propositions:
  - pillar: "[Pillar Name]"
    headline: "[Benefit-driven, 8 words max]"
    subhead: "[How it works, 1 sentence]"
    proof: "[Specific stat, case study, or demo]"
    objection_it_handles: "[What skeptics say, and how this answers it]"
  - pillar: "..."
  - pillar: "..."
```

**Layer 3: Proof Points**
For each value prop, stack evidence:
- Customer quote (with name + company + result)
- Metric ("43% faster onboarding")
- Third-party validation (award, press mention, certification)
- Demo/screenshot showing it in action

### 2.3 Ideal Customer Profile (ICP)

```yaml
icp:
  demographics:
    company_size: "[range]"
    industry: ["...", "..."]
    revenue_range: "[range]"
    geography: ["..."]
    tech_stack: ["..."]  # if relevant
  psychographics:
    biggest_pain: "[The thing that keeps them up at night]"
    current_workaround: "[How they solve it today — badly]"
    buying_trigger: "[What event makes them search for a solution?]"
    decision_maker: "[Title + what they care about]"
    influencer: "[Who researches options before the DM sees them]"
    budget_holder: "[Who signs the check]"
  anti_signals:  # who NOT to target
    - "[Red flag 1 — e.g., 'wants custom everything']"
    - "[Red flag 2 — e.g., 'decision cycle > 6 months']"
    - "[Red flag 3 — e.g., 'budget under $X']"
  buying_journey:
    awareness: "[Where they first discover solutions — channels, searches]"
    consideration: "[What they compare — features, pricing, reviews]"
    decision: "[What tips them over — demo, trial, social proof, champion]"
```

### 2.4 Tagline & Elevator Pitch

**Tagline formulas (pick one, refine):**
1. **Verb + Outcome:** "Ship faster. Break nothing."
2. **Contrast:** "Enterprise power. Startup speed."
3. **Challenge:** "Stop guessing. Start knowing."
4. **Promise:** "From pipeline to paycheck in 14 days."
5. **Identity:** "Built for builders."

**Tagline quality checklist:**
- [ ] ≤6 words
- [ ] No jargon or buzzwords
- [ ] Works without context (on a billboard)
- [ ] Implies a benefit, not a feature
- [ ] Memorable — has rhythm, alliteration, or contrast

**Elevator Pitch (30-second):**
"You know how [target audience] struggles with [problem]? We built [Product] which [solution]. Unlike [alternative], we [key differentiator]. [Customer] used it to [specific result]."

---

## Phase 3: Brand Voice & Tone

### 3.1 Voice Guidelines

Voice is constant. Tone adapts to context.

```yaml
brand_voice:
  voice_in_3_words: ["direct", "warm", "sharp"]
  writing_rules:
    - "Short sentences. Max 20 words unless making a complex point."
    - "Active voice always. 'We built X' not 'X was built by us.'"
    - "Contractions: yes. 'We're' not 'We are.'"
    - "First person plural ('we') for company, 'you' for customer."
    - "No hedge words: 'very', 'quite', 'somewhat', 'a bit.'"
    - "Specific > vague. '$40K saved' not 'significant savings.'"
    - "One idea per paragraph. If you need a semicolon, make two sentences."
  
  vocabulary:
    use: ["ship", "build", "real", "prove", "earn", "move", "own"]
    avoid: ["leverage", "synergy", "streamline", "cutting-edge", "revolutionize", "ecosystem", "holistic"]
  
  tone_spectrum:
    celebration: "Bold, high-energy. Short punchy sentences. Exclamation marks OK (max 1 per paragraph)."
    education: "Clear, patient, structured. Use examples liberally. No condescension."
    error_state: "Honest, calm, action-oriented. Say what happened, what we're doing, when it'll be fixed."
    sales: "Confident, proof-heavy. Lead with outcomes, not features. Never desperate."
    support: "Warm, specific, fast. Mirror the customer's urgency level."
```

### 3.2 Channel-Specific Adaptations

| Channel | Tone Shift | Formatting | Length |
|---------|-----------|------------|--------|
| Website copy | Benefit-led, scannable | H2s, bullets, social proof | 50-100 words/section |
| Email (marketing) | Conversational, CTA-focused | Short paragraphs, 1 CTA | 150-300 words |
| Email (support) | Warm, solution-focused | Steps numbered, links inline | As short as possible |
| Social (LinkedIn) | Professional, insight-led | Hook → Story → CTA | 150-300 words |
| Social (Twitter/X) | Sharp, pithy, opinionated | Thread for depth, single for hooks | 280 chars or 5-8 tweet thread |
| Blog/Content | Educational, comprehensive | H2/H3 structure, examples | 1500-2500 words |
| Sales deck | Confident, customer-centric | Visuals > text, 6 words/slide | 10-15 slides |
| Product UI | Minimal, action-oriented | Verb-first buttons, no jargon | 3-8 words |

### 3.3 Brand Voice Scorecard

Rate any piece of content 1-5 on each dimension:

| Dimension | 1 (Off-brand) | 5 (On-brand) | Weight |
|-----------|--------------|--------------|--------|
| Clarity | Jargon-heavy, confusing | Crystal clear, instant understanding | 25% |
| Personality | Generic, could be anyone | Unmistakably us | 20% |
| Specificity | Vague claims, adjective-heavy | Numbers, examples, proof | 20% |
| Action | Passive, informational | Drives clear next step | 15% |
| Consistency | Contradicts other brand comms | Reinforces brand story | 10% |
| Audience-fit | Wrong level, wrong concerns | Speaks directly to ICP | 10% |

**Score:** <60 = rewrite. 60-79 = revise. 80+ = publish.

---

## Phase 4: Visual Identity System

### 4.1 Color Palette

**Primary (2 colors):**
```yaml
colors:
  primary:
    main: "#[hex]"  # Dominant brand color — used in logo, CTAs, headers
    accent: "#[hex]"  # Secondary emphasis — used in highlights, hover states
  neutral:
    dark: "#[hex]"   # Text, headings (near-black, never pure #000)
    medium: "#[hex]"  # Secondary text, borders
    light: "#[hex]"   # Backgrounds, cards
    white: "#[hex]"   # Page background (often #FAFAFA, not pure white)
  semantic:
    success: "#[hex]"
    warning: "#[hex]"
    error: "#[hex]"
    info: "#[hex]"
```

**Color psychology quick guide:**
- Blue = trust, stability (finance, enterprise, healthcare)
- Green = growth, health (sustainability, wellness, finance)
- Red/Orange = energy, urgency (food, entertainment, sales)
- Purple = premium, creative (luxury, education, design)
- Yellow = optimism, attention (consumer, youth, caution)
- Black = premium, power (luxury, tech, fashion)
- Teal = modern, approachable (SaaS, fintech)

**Ratio rule:** 60% neutral / 30% primary / 10% accent

### 4.2 Typography

```yaml
typography:
  heading:
    family: "[Font name]"
    weights: ["Bold (700)", "Semibold (600)"]
    style: "serif|sans-serif|display"
  body:
    family: "[Font name]"
    weights: ["Regular (400)", "Medium (500)"]
    style: "sans-serif"
    size_base: "16px"
    line_height: "1.6"
  mono:  # for code/technical content
    family: "[Font name]"
  pairing_rationale: "[Why these fonts work together]"
```

**Safe pairings:**
- Modern SaaS: Inter + Inter (single font system)
- Premium: Playfair Display + Source Sans Pro
- Technical: Space Grotesk + IBM Plex Sans
- Friendly: DM Sans + DM Sans
- Editorial: Lora + Open Sans

### 4.3 Logo Direction Brief

If working with a designer, provide this:

```yaml
logo_brief:
  type: "wordmark|lettermark|icon+wordmark|abstract|mascot"
  must_convey: ["[feeling 1]", "[feeling 2]", "[feeling 3]"]
  avoid: ["[cliche 1]", "[cliche 2]"]
  usage_contexts: ["favicon", "social avatar", "email signature", "merchandise"]
  competitors_look_like: "[Describe what's common in the space]"
  we_want_to_feel: "[Different how?]"
  min_size: "Must be legible at 32x32px (favicon)"
  variations_needed: ["full color", "single color", "reversed (white)", "icon only"]
```

### 4.4 Imagery & Photography Style

```yaml
imagery:
  style: "photography|illustration|3D|abstract|mixed"
  mood: "[2-3 adjective description — e.g., 'bright, candid, energetic']"
  subjects: ["real people working", "product screenshots", "abstract patterns"]
  avoid: ["stock photo handshakes", "generic office scenes", "clip art"]
  filters: "[Any consistent treatment — e.g., 'slight warm tint, high contrast']"
  aspect_ratios:
    hero: "16:9"
    social: "1:1"
    blog: "2:1"
```

---

## Phase 5: Go-to-Market Strategy

### 5.1 GTM Motion Selection

| Motion | Best When | Resources Needed | Time to Revenue |
|--------|----------|-----------------|-----------------|
| **Product-led (PLG)** | Low price, self-serve, viral potential | Engineering-heavy, analytics | 3-6 months |
| **Sales-led** | High ACV ($10K+), complex solution | Sales team, collateral | 1-3 months |
| **Community-led** | Developer tools, niche markets | Content, community management | 6-12 months |
| **Content-led** | Education market, long buying cycles | Writing, SEO, distribution | 6-12 months |
| **Partner-led** | Established ecosystem, integrations | Partnerships, co-marketing | 3-9 months |

**Decision framework:**
- ACV < $1K → PLG or Content-led
- ACV $1K-$10K → PLG + Sales assist
- ACV $10K-$50K → Sales-led + Content
- ACV $50K+ → Sales-led + Partner

### 5.2 Launch Playbook

**Pre-launch (T-30 to T-0):**

```yaml
pre_launch:
  week_4:
    - "Finalize positioning & messaging (Phase 2)"
    - "Set up analytics (website, product, marketing)"
    - "Create launch landing page with waitlist/early access"
  week_3:
    - "Draft all launch content (blog, email, social)"
    - "Brief sales team on positioning + battlecards"
    - "Set up CRM pipeline stages for launch leads"
  week_2:
    - "Seed content to early community (beta users, advisors)"
    - "Prepare PR/media list if relevant"
    - "Test all funnels end-to-end (landing → signup → onboarding → payment)"
  week_1:
    - "Final content review (voice scorecard — all pieces score 80+)"
    - "Load email sequences"
    - "Prepare real-time monitoring dashboard"
    - "Write the 'things went wrong' playbook (site down, negative feedback, etc.)"
```

**Launch day checklist:**
- [ ] Publish landing page / make product public
- [ ] Send email to waitlist / existing customers
- [ ] Post to primary social channels (stagger by 2 hours)
- [ ] Submit to relevant directories (Product Hunt, HN, industry-specific)
- [ ] Monitor: traffic, signups, errors, social mentions (every 30 min)
- [ ] Respond to every comment/question within 1 hour
- [ ] End-of-day: metrics snapshot + lessons learned

**Post-launch (T+1 to T+30):**
- Day 1-3: Respond to all feedback, fix critical issues
- Day 4-7: First customer stories / testimonials
- Day 8-14: Analyze funnel — where are people dropping?
- Day 15-30: Iterate messaging based on what resonated

### 5.3 Channel Strategy

For each channel, define:

```yaml
channels:
  - name: "[Channel name]"
    purpose: "awareness|consideration|conversion|retention"
    target_audience: "[Specific segment]"
    content_types: ["...", "..."]
    posting_cadence: "[frequency]"
    kpi: "[Primary metric]"
    target: "[Specific number by when]"
    budget: "[$/month or time investment]"
    owner: "[Who manages this]"
```

### 5.4 Sales Battlecard

```yaml
battlecard:
  competitor: "[Name]"
  their_pitch: "[How they describe themselves]"
  their_strengths: ["...", "..."]
  their_weaknesses: ["...", "..."]
  landmine_questions:  # Questions that expose their weakness
    - "[Question that makes prospect think about competitor's gap]"
    - "..."
  our_counter:
    when_they_say: "[Competitor claim]"
    we_say: "[Our response — specific, proof-backed]"
  win_themes: ["...", "..."]
  loss_reasons: ["...", "..."]
  trap_to_avoid: "[What NOT to say when this competitor comes up]"
```

---

## Phase 6: Brand Measurement & Evolution

### 6.1 Brand Health Dashboard

Track monthly:

| Metric | How to Measure | Benchmark |
|--------|---------------|-----------|
| **Aided awareness** | Survey: "Have you heard of [Brand]?" | Track trend |
| **Share of voice** | Brand mentions vs competitors (social, search) | Growing |
| **Brand sentiment** | % positive/neutral/negative mentions | >70% positive |
| **NPS** | "How likely to recommend?" (0-10) | >40 |
| **Direct traffic** | People typing your URL | Growing MoM |
| **Branded search** | "[Brand name]" Google searches | Growing MoM |
| **Repeat purchase rate** | Returning customers / total customers | >30% |
| **Content engagement** | Avg time on page, shares, saves | Improving |

### 6.2 Brand Audit (Quarterly)

Run this checklist every quarter:

**Consistency check:**
- [ ] All customer-facing channels use current logo, colors, fonts
- [ ] Website copy matches current positioning statement
- [ ] Sales materials match current messaging architecture
- [ ] Social profiles have consistent bios, links, imagery
- [ ] Email templates use current brand voice

**Effectiveness check:**
- [ ] Voice scorecard: score 5 recent content pieces — average 80+?
- [ ] Review last quarter's campaigns — which messaging resonated most?
- [ ] Read 10 recent customer reviews — do they echo our intended positioning?
- [ ] Mystery shop: visit our own site fresh — is the value prop clear in 5 seconds?

**Evolution signals:**
- [ ] Market has shifted — new competitors, new category, new buyer expectations
- [ ] Product has expanded — brand no longer covers what we actually do
- [ ] Audience has changed — attracting different customers than ICP
- [ ] Values feel hollow — things we say we value but don't practice

### 6.3 Rebrand Decision Framework

**Don't rebrand when:**
- You're bored of your own brand (customers aren't)
- A competitor changed their brand
- Revenue is flat (brand probably isn't the problem)
- New leadership just "wants their stamp"

**Do rebrand when:**
- Brand actively confuses people about what you do
- Product pivot makes current positioning misleading
- Merger/acquisition requires unified identity
- Negative brand associations that can't be overcome with marketing
- Outgrew the original brand (started as SMB tool, now enterprise)

**Rebrand scope options:**
1. **Refresh** (low risk): Update colors, fonts, imagery. Keep name + positioning.
2. **Reposition** (medium risk): Same name, new messaging + visual system.
3. **Rename** (high risk): New name, new everything. Only when absolutely necessary.

---

## Edge Cases & Advanced Patterns

### Multi-Brand Architecture

If you manage multiple products/brands:

| Strategy | When | Example |
|----------|------|---------|
| **Branded House** | Products share master brand | Google Maps, Google Drive |
| **House of Brands** | Products have distinct identities | P&G → Tide, Gillette, Pampers |
| **Endorsed** | Sub-brands with parent endorsement | Marriott → Courtyard by Marriott |
| **Hybrid** | Mix based on product type | Apple (branded house) + Beats (endorsed) |

### Personal Brand vs Company Brand

When founder IS the brand:
- Company brand: what you build (can be sold)
- Personal brand: who you are (can't be sold)
- Build both, but ensure the company can survive without the founder's face
- Use personal brand to drive attention → funnel to company brand for conversion

### International Brand Adaptation

Before entering new markets:
- [ ] Name check: Does it mean something offensive in local language?
- [ ] Color audit: Color meanings vary by culture (white = death in some Asian cultures)
- [ ] Voice localization: Translate voice guidelines, not just words
- [ ] Local proof points: Global stats don't resonate — find local references
- [ ] Legal: Trademark search in target jurisdiction

### Brand Crisis Playbook

**Severity 1 (Minor — negative review, social complaint):**
- Respond publicly within 2 hours
- Acknowledge, don't defend
- Take the conversation private to resolve

**Severity 2 (Moderate — trending criticism, competitor attack):**
- Internal alignment on response within 1 hour
- Transparent public statement
- Monitor for 48 hours, respond to follow-ups

**Severity 3 (Major — data breach, product failure, public scandal):**
- CEO/founder response within 4 hours
- Accept responsibility + specific remediation plan
- Regular updates until resolved
- Post-incident: what we changed (not just what we're sorry about)

---

## Quick Reference: Natural Language Commands

| Command | What It Does |
|---------|-------------|
| "Build my brand identity" | Full Phase 1-4 walkthrough |
| "Write my positioning" | Phase 2.1 Dunford method |
| "Create messaging for [product]" | Phase 2.2 full messaging architecture |
| "Define my ICP" | Phase 2.3 customer profile |
| "Write brand voice guidelines" | Phase 3.1 complete voice system |
| "Plan my GTM" | Phase 5 go-to-market strategy |
| "Create a battlecard for [competitor]" | Phase 5.4 sales battlecard |
| "Audit my brand" | Phase 6.2 quarterly checklist |
| "Score this content" | Phase 3.3 voice scorecard |
| "Should we rebrand?" | Phase 6.3 decision framework |
| "Launch plan for [product]" | Phase 5.2 full playbook |
| "Adapt brand for [market]" | International adaptation checklist |
