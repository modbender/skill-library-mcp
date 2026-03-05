---
name: substack-post-writer
description: Write long-form Substack newsletters about GenAI, education, edtech, and their intersections. This skill should be used when the user requests a Substack post, newsletter, or long-form article about AI/education topics. Produces essays using Made to Stick principles adapted for long-form, maintains the user's distinctive voice (Dr. Shiva Kakkar's style), and positions him as a thought leader at the GenAI-education intersection. Posts are data-driven, contrarian without being preachy, and designed for deep reader engagement.
---

# Substack Post Writing Skill

## User Profile

**Dr. Shiva Kakkar** - Faculty member positioned for future leadership roles in Indian higher education. Writes to build personal brand beyond institutional affiliation. His sweet spot: GenAI + education intersection (schools through B-schools in India).

**Target audiences:**
1. B-school leadership & faculty (decision-makers seeking practical implementation)
2. Students & parents (reality check seekers)
3. EdTech/academia commentators (idea spreaders)
4. Corporate recruiters & industry (quality signal seekers)

**Voice characteristics:**
- Numbers anchor credibility ($500 vs $6000, 65% stat, ₹4L courses)
- Contrarian without preaching ("IIMs aren't responsible—you are")
- Concrete over abstract (specific examples, not platitudes)
- Forward-looking pragmatism
- No false humility ("perhaps one of the most comprehensive" stated plainly)
- Industry voice validation (CEO quotes > personal opinion)
- Quick, clever humor when appropriate
- Explains concepts lucidly with analogies (like Sangeet Paul Choudhary or Paul Daugherty)

## Key Difference from LinkedIn

Substack is long-form. LinkedIn is a billboard. Substack is a conversation over coffee.

**LinkedIn**: 200-350 words. Violation → Credential → Insight → Hook. Quick hit.

**Substack**: 1500-3000 words. Violation → Deep Exploration → Multiple Angles → Actionable Framework → Uncomfortable Question.

Substack readers subscribed because they want depth. They want to understand not just what happened, but why it matters, how it connects, and what to do about it.

## Writing Process

### Step 1: Search for Topic

Use `web_search` to find major GenAI/education/edtech announcements, trends, or controversies:

```
Query patterns:
- "major AI education announcement 2025"
- "India GenAI students announcement 2025"
- "education technology breakthrough 2025"
- "OpenAI Google Microsoft education 2025"
- "[topic] controversy debate 2025"
```

**Critical: Always contextualize to India.** If announcement is global, search specifically for India impact:
- "India [announcement topic] 2025"
- Check if tools/policies mentioned apply to Indian users
- Verify pricing/availability for Indian market

### Step 2: Gather Framework Material

Use MCPs to enrich the post with depth:

**Readwise MCP** (`search_readwise_highlights`):
```json
{
  "full_text_queries": [
    {"field_name": "highlight_plaintext", "search_term": "[topic keyword 1]"},
    {"field_name": "highlight_plaintext", "search_term": "[topic keyword 2]"}
  ],
  "vector_search_term": "[conceptual theme of post]"
}
```

**LlamaCloud MCP** (`query_AI-Strategy-Studies` or `query_AI-Change-and-leadership` or `query_Persuasion-and-communication-OB`):
```
Query: "[topic] frameworks adoption implementation"
```

**Extract insights, NOT quotes:**
- Identify mental models, frameworks, patterns
- Rewrite in user's voice and context
- Remove original author names
- Make audience-friendly (non-technical readers)
- Example: "Curse of Knowledge" → "Recognition Deficit" or similar reframing

For Substack, gather MORE material than LinkedIn. Aim for 3-5 frameworks/concepts to weave together.

### Step 3: Select Theme from Rotation

Choose from 6-week cycle (avoid repetition):

1. **Cost Arbitrage Deep Dive**: Real numbers violating assumptions + why the economics work this way + what institutions miss
2. **Fusion Skills Exploration**: Redefining AI literacy + case studies + what it looks like in practice
3. **Implementation Playbook**: Open-sourcing tools, frameworks with detailed how-to (highest engagement)
4. **Industry Reality Report**: What recruiters/CEOs actually think + data + implications
5. **Institutional Autopsy**: Gap between claims and actions + why it persists + what breaks the loop
6. **Future Scenario Analysis**: Agentic era implications + what it means for different stakeholders + how to prepare

### Step 4: Apply the 5-Act Structure

Substack needs a different architecture than LinkedIn. Think of it as a play in five acts:

**Act 1: The Hook (150-300 words)**

Open with violation, just like LinkedIn. But then expand into WHY this matters.

Structure:
- Counterintuitive data point (first line)
- Context that makes it worse ("And here's the kicker...")
- Stakes for the reader ("This isn't just about X. It's about...")

Example pattern:
```
[Shocking stat or fact]

[Second stat that compounds it]

[Explanation of why this should concern the reader]

This isn't about [surface-level interpretation]. It's about [deeper implication that affects reader].
```

**Act 2: The Backstory (300-500 words)**

Give context that LinkedIn doesn't have room for. How did we get here? What's the history?

Structure:
- Historical context or evolution
- Failed approaches or attempts
- Why obvious solutions don't work
- Personal experience or institutional example

This is where storytelling shines. Use specific characters, situations, failures.

**Act 3: The Framework (400-700 words)**

The meat of the post. Introduce a way of thinking about the problem.

Structure:
- Name the pattern or mental model (in user's own words)
- Explain it with concrete examples
- Show how it applies to different situations
- Include one counter-example or limitation

**Critical: Vary how frameworks are presented:**
- Sometimes as numbered steps (but not every post)
- Sometimes as contrasting approaches (Employee A vs Employee B)
- Sometimes as a narrative ("Here's what happened when we tried...")
- Sometimes as questions ("Ask yourself three things...")
- Sometimes embedded in prose without explicit structure

**Act 4: The Application (300-500 words)**

Make it actionable. What does the reader DO with this?

Structure:
- Specific actions for different audience segments (implied, not labeled)
- Examples of implementation
- Common pitfalls to avoid
- Resources or starting points

**Act 5: The Uncomfortable Close (150-300 words)**

End with provocation, not inspiration. Leave the reader thinking.

Structure:
- Circle back to opening violation
- Escalate the implications
- Pose an uncomfortable question or challenge
- No inspirational padding

## Section Headers

Unlike LinkedIn, Substack can use headers. But use them sparingly and strategically.

**Good header style:**
- Questions that provoke ("What if we're asking the wrong question?")
- Contrarian statements ("The real problem isn't what you think")
- Concrete specifics ("The ₹500 vs ₹50,000 gap")
- Narrative transitions ("What happened when we actually tried")

**Avoid:**
- Generic headers ("Introduction", "Conclusion", "Key Takeaways")
- Numbered lists in headers ("3 Ways to...", "5 Steps to...")
- Buzzword headers ("Leveraging AI for Success")

Use 3-5 headers per post, not more. Let prose breathe.

## Tone & Style Guidelines

**Explanation style:**
- Use analogies and metaphors (like Sangeet Paul Choudhary)
- Show how concepts connect to each other
- Explain why, not just what
- Use concrete examples over abstract principles

**Narrative techniques:**
- Specific characters (Employee A vs B, the marketing professor, the CEO)
- Dialogue where appropriate
- Sensory details ("the 3-second Google search", "a smartphone in their pocket")
- Escalation ("Weird... Weirder... Weirdest")

**Data integration:**
- Lead with specific numbers
- Cite sources naturally (not academically)
- Contrast numbers that reveal gaps ($6000 vs $500)
- Use percentages for human scale (65%, not "majority")

**Voice markers:**
- Direct address to reader ("Here's what you need to understand")
- Admission of uncertainty when appropriate ("I don't know if this will work, but...")
- Self-aware humor (not forced)
- No false modesty or excessive hedging

## Length & Formatting

**Target**: 1500-3000 words

- Under 1500: May lack depth readers expect from Substack
- Over 3000: Risks losing reader attention

**Paragraph length:**
- 2-5 sentences per paragraph
- Vary length for rhythm
- Use single-sentence paragraphs for emphasis (sparingly)

**White space:**
- Generous line breaks between paragraphs
- Headers create visual breaks
- Pull quotes or emphasis for key points (bold or italic, not both)

**Formatting:**
- Bold for key terms or emphasis (sparingly)
- Italics for internal dialogue or hypotheticals
- No bullet points in main body (breaks narrative flow)
- Lists only in Application section if needed

## SUCCESs Framework for Long-Form

All six elements still apply, but expanded:

- **Simple**: Core message still distillable to one sentence (but explored fully)
- **Unexpected**: Multiple violations throughout, not just opening
- **Concrete**: Many specific examples, characters, numbers (LinkedIn has 1-2, Substack has 5-8)
- **Credentialed**: Implementation proof, industry voices, verifiable claims
- **Emotional**: Build emotional arc (frustration → insight → possibility → challenge)
- **Stories**: Full narrative arcs, not just anecdotes

## Critical Reminders

**Never:**
- Mention original book/framework names
- Quote sources verbatim
- Use generic headers ("Introduction", "Conclusion")
- Default to institutional positioning
- Forget India context for global announcements
- Include pre-text, post-text, acknowledgments, or padding
- Use bullet points for main arguments
- End with inspirational fluff

**Always:**
- Search for India-specific implications
- Use MCPs to enrich with frameworks (but rewrite)
- Verify numbers and claims
- Lead with violation, not context
- Vary structural presentation
- Build to uncomfortable close
- Include specific, verifiable data
- Explain WHY, not just WHAT

## Example Quality Checks

**Good post indicators:**
- Opens with number that surprises
- Contains 5+ concrete examples
- Has clear framework but varied presentation
- Builds emotional arc
- Ends with provocation, not summary
- Uses headers strategically
- Shows deep understanding of WHY things work the way they do

**Bad post indicators:**
- Opens with context or scene-setting
- Uses "Three X Framework" in headers
- Mentions books or original authors
- Generic inspirational close
- Bullet-point heavy
- Headers are generic ("Key Insights")
- Tells reader what to think instead of making them think

## Output Format

**CRITICAL - ABSOLUTE REQUIREMENT**:

Output MUST begin IMMEDIATELY with the title. Zero exceptions.

❌ FORBIDDEN - Never include:
- "I'll read the skill..."
- "Let me create..."
- "Here's your post..."
- "Based on the announcement..."
- "I found this news..."
- Separators like "---" or "========="
- "Would you like me to adjust..."
- "Let me know if..."
- Any explanatory text before or after the post

✅ REQUIRED format:
```
[Title: Provocative, specific, not clickbait]

[Opening paragraph - violation first]

[Continue with natural prose and strategic headers]

[Uncomfortable close - no summary]

---

[Source URL if news-based]
```

**The very first character output must be the title of the post. Period.**

## Post Creation Workflow Summary

1. **Search**: Find recent GenAI/edu topic (India-contextualized)
2. **Gather**: Use MCPs for 3-5 frameworks (rewrite in user voice)
3. **Select**: Choose theme from 6-week rotation
4. **Outline**: Map 5-act structure with specific examples
5. **Draft**: Write with prose flow, varied presentation
6. **Verify**: Check SUCCESs framework (all 6 elements present)
7. **Polish**: Ensure voice authenticity, header quality, emotional arc
8. **Output**: Post text only (no wrapper text)