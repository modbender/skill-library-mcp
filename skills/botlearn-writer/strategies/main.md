---
strategy: writer
version: 1.0.0
steps: 7
---

# Article Writing Strategy

## Step 1: Topic Research & Scoping
- Parse the user's request to identify: **topic**, **target audience**, **desired length**, **publication context**, **tone preference**
- Use @botlearn/keyword-extractor to extract core terms, related concepts, and semantic clusters from the topic
- Use @botlearn/summarizer to condense any provided reference materials, sources, or background documents into key evidence points
- IF the topic is ambiguous or underspecified THEN ask clarifying questions:
  - "Who is the target audience?"
  - "What is the desired length and format?"
  - "Is there a specific angle or thesis you want to pursue?"
- Identify 3-5 key subtopics that the article must address for comprehensive coverage
- Assess available evidence: what data, examples, or expert perspectives exist for this topic?

## Step 2: Outline Construction
- SELECT article structure from knowledge/domain.md based on topic and purpose:
  - Persuasive or opinion → Analytical Framework
  - News or time-sensitive → Inverted Pyramid
  - Feature or case study → Narrative Arc
  - How-to or reference → Listicle / Modular
  - Technical or consulting → Problem-Solution
- Draft a hierarchical outline:
  - **Level 1**: Major sections (introduction, argument blocks, conclusion)
  - **Level 2**: Key points within each section
  - **Level 3**: Evidence placeholders (type of evidence needed for each point)
- VERIFY outline covers all subtopics identified in Step 1
- VERIFY each argument block maps directly to the thesis
- IF outline has fewer than 3 argument blocks THEN expand — the article needs sufficient depth
- IF outline has more than 5 argument blocks THEN consolidate — focus risks dilution

## Step 3: Argument Building
- SELECT argumentation framework from knowledge/domain.md:
  - Default: Toulmin Model (Claim → Data → Warrant → Backing → Qualifier → Rebuttal)
  - Contentious topics: Rogerian Argument (Acknowledge opposition → Common ground → Position → Synthesis)
  - Persuasive essays: Classical Rhetorical Appeals (Ethos → Pathos → Logos)
- For each argument block in the outline:
  1. State the **claim** in one clear sentence
  2. Identify the **evidence** needed (type and source)
  3. Write the **warrant** — the logical bridge between evidence and claim
  4. Add a **qualifier** if the claim has conditions or limitations
  5. IF a counterargument exists THEN draft a **rebuttal**
- VERIFY logical consistency: no argument should contradict another; each should build on the previous
- SELF-CHECK: Does each argument independently support the thesis? Remove any that don't

## Step 4: Evidence Integration
- For each evidence placeholder in the outline, SELECT evidence from available sources:
  - Apply evidence selection criteria from knowledge/best-practices.md: relevance, recency, authority, representativeness
  - Target a minimum of 3 different evidence types across the article (statistics, expert quotes, case studies, analogies, logical reasoning)
  - High-stakes claims (central to thesis) require 2-3 supporting evidence items
- Integrate evidence using appropriate introduction patterns from knowledge/best-practices.md:
  - Signal phrase for attributed authority
  - Data-first for maximum impact
  - Contextual embedding for narrative flow
- APPLY the PEEL structure to each paragraph: Point → Evidence → Explain → Link
  - Never leave evidence unanalyzed — always explain what it means and how it connects to the argument
- VERIFY source attribution: every piece of evidence must identify who, when, and in what context
- CHECK against knowledge/anti-patterns.md:
  - No unsupported claims (anti-pattern #5)
  - No evidence without analysis (anti-pattern #6)
  - No cherry-picked evidence (anti-pattern #7)
  - No outdated evidence (anti-pattern #8)
  - No single-source dependency (anti-pattern #9)

## Step 5: Draft Composition
- Write the complete article following the outline and assembled arguments:
- **Introduction** (1-2 paragraphs):
  - Open with a hook: a surprising statistic, provocative question, vivid anecdote, or bold claim
  - Provide necessary context for the topic
  - State the thesis clearly within the first two paragraphs
- **Body** (per outline):
  - Follow the selected article structure from Step 2
  - Use the argumentation framework from Step 3 for each argument block
  - Embed evidence per Step 4 integration patterns
  - Include transitions between every section and paragraph
- **Conclusion** (1-2 paragraphs):
  - Restate the thesis in light of the evidence presented (do not copy-paste the introduction)
  - Synthesize the key arguments into a higher-order insight
  - End with a call to action, forward-looking prediction, or thought-provoking question
- APPLY sentence rhythm: alternate short and long sentences for readability
- MAINTAIN consistent tone throughout — refer to the tone selection framework in knowledge/best-practices.md

## Step 6: Style Check & Polish
- VERIFY tone consistency: read the full draft and flag any shifts in register, formality, or voice
  - Check: Does the introduction and conclusion use the same register?
  - Check: Are all sections using the same person (first, second, third)?
  - Check: Is vocabulary level consistent throughout?
- VERIFY readability:
  - Paragraphs are 3-6 sentences (digital) or 4-8 sentences (print)
  - Sentence variety: mix of short (8-12 words) and long (20-30 words)
  - Active voice usage is at 80%+ — convert passive constructions where possible
  - Eliminate filler words: "very," "really," "basically," "actually," "just"
  - Replace nominalizations: "made an improvement" → "improved"
- VERIFY transitions:
  - Every paragraph opens with a connection to the previous one
  - Subheadings are used every 200-300 words for scannable content
- CHECK against knowledge/anti-patterns.md:
  - No tone inconsistency (anti-pattern #11)
  - No register mismatch (anti-pattern #12)
  - No passive voice overuse (anti-pattern #13)
  - No filler/hedge overload (anti-pattern #14)
  - No wall of text (anti-pattern #15)
  - No buried lead (anti-pattern #16)
  - No weak conclusion (anti-pattern #17)
  - No missing transitions (anti-pattern #18)

## Step 7: Revision & Final Quality Assurance
- SELF-CHECK — Thesis integrity:
  - Can you identify the thesis in one sentence? Is it in the first two paragraphs?
  - Does the conclusion restate it consistently (not contradict it)?
  - Does every argument block connect back to the thesis? (anti-pattern #4: moving thesis)
- SELF-CHECK — Evidence sufficiency:
  - Are there at least 3 different evidence types used?
  - Is every major claim supported?
  - Are counterarguments acknowledged for contentious claims?
- SELF-CHECK — Structural coherence:
  - Does the article follow the selected structure pattern consistently?
  - Is the information prioritized appropriately (most important first for inverted pyramid; tension built for narrative)?
  - Are there clear section markers and logical flow?
- SELF-CHECK — Audience alignment:
  - Is the vocabulary appropriate for the target audience?
  - Is the depth of explanation correct (not too basic, not too advanced)?
  - Would the target reader find this article valuable?
- IF any check fails THEN revise the specific section and re-run the failed check
- Use @botlearn/keyword-extractor to verify final keyword coverage — ensure core topic terms appear with appropriate frequency
- Output the final article with clear formatting: title, subheadings, paragraphs, and source attributions
