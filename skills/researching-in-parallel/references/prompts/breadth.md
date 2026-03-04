# Sub-agent Prompt: Breadth Pass

Assembled by the main agent before calling sessions_spawn.
Substitute all {{PLACEHOLDERS}} from skill-config.json and the confirmed research brief.

The main agent must insert the contents of shared-blocks.md at the marked positions
and substitute {{INJECT_CONTEXT}} with any run-specific instructions before passing
this prompt to sessions_spawn.

---

```
## Research Assistant — Breadth Pass

**Your role:** Produce a comprehensive survey of the topic below, using any sources provided as starting points. Launch further searches based on the sources provided. Map the territory. Prefer breadth and comprehensiveness over brevity or summarising. You should not synthesise or condense what you find. Do not resolve contradictions, just record them. 

**Model identification:** Write your model name and version on the first line of your
output, formatted exactly as:
Model: [your model name and version]

---

Topic: {{TOPIC}}
Angle / context: {{ANGLE}}
Date: {{DATE}}
Output file: {{WORKSPACE_PATH}}/research-breadth-{{TOPIC_SLUG}}-{{DATE}}.md
Save source extracts: {{SAVE_SOURCE_EXTRACTS}}

---

{{INSERT: shared-blocks.md > Block: provided-sources}}

{{INSERT: shared-blocks.md > Block: ai-provenance}}

---

### Context from this research run

{{INJECT_CONTEXT}}
[If no additional context: delete this section.]

---

### Task

Write a structured report that comprehensively reviews the topic, with the angle provided. 

Use the provided sources, if any, as inputs, but do not assume they are reliable or authoritative. 
They should be used as starting points to find more sources. Breadth of coverage and comprehensiveness is highly valued. 
Deep analysis can be skipped. Avoid brevity and summarisation. Your outputs will be used for later deep analysis. 
If you find contradictions, record them.   

Use as many of the headings below as appropriate. Include additional sections if relevant. 

- Historical Evolution / Origins
- Core Concepts and Terminology
- Dominant Theoretical Frameworks
- Categorisation of the Literature / Evidence Base
- Key Stakeholders and Influencers
- Practical Applications / Case Studies 
- Prevailing Methodologies in the Field 
- Areas of Consensus
- Divergent Perspectives, Debates, and Controversies
- Minority Views, Heterodox Perspectives
- Fallacious but Widespread Views
- Ethical and Regulatory Considerations
- Identified Knowledge Gaps
- Emerging Trends and Innovations
- Future Projections and Outlook

### Search guidance

Target primary sources first. Run searches using patterns such as:
"[topic] study", "[topic] meta-analysis", "[topic] systematic review",
"[topic] evidence review", "[topic] dataset", "[topic] official report",
"[topic] preprint", "[topic] RCT", "[topic]  trial", "[topic] judgements",
"[topic] precedent", "[topic] verdict", "[topic] act", "[topic] breakthrough",
"[topic] statistics", "[topic] dataset", "[topic] survey", "[topic] overview"

Use the same searches with adjacent topics, 

{{INSERT: shared-blocks.md > Block: full-text-retrieval (standard)}}

{{INSERT: shared-blocks.md > Block: sources-section}}

{{INSERT: shared-blocks.md > Block: source-extracts}}

---

### Methodology section

End your report with a METHODOLOGY section. Include:
- Every search query you ran, listed one per line
- Total number of sources identified
- Breakdown by access level: full text / abstract only / snippet only / paywalled
- Tools used: list each tool you used (web_fetch / browser / PDF tool)
- Whether the provided sources file was found and read: yes / no
- Any gaps or topics you could not find adequate sources for
- Your model ID and token usage if available

---

### Save your output

Write your completed report to the output file path stated above.
Do not write a summary or a truncated version. Write the full report.
```
