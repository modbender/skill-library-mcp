---
description: Generates structured, argument-driven book manuscript
  sections using modular 800--1000 word conceptual units.
name: book-manuscript-writer
---

# Book Manuscript Writer

## Overview

This skill is designed exclusively for writing book manuscripts,
theoretical chapters, and argument-driven academic essays.

It does NOT generate IMRaD-style conference or journal papers.

The fundamental unit of writing is:

A viewpoint-style subtitle\
→ followed by a structured 800--1000 word argument unit.

## workflow

### 1. Understanding the main point

When asked to write a book chapter:

1. **Clarify the topic and scope** with the user
   - What is the central argument or core claim of this chapter?
   - Who is the intended audience (e.g., general academic readers, specialists, interdisciplinary scholars)?
   - What is the desired length (approximate word count or page range)?
   - Are there specific structural emphases required (e.g., case analysis, theoretical construction, conceptual integration)?

2. **Require a chapter** outline from the user

   - The outline must specify the sequence of unit-level claims — not just topic labels. Each entry should express a proposition.

   - Each outline entry should indicate:

     - The core claim of that unit

     - Its role in the chapter's argument arc (what it establishes, challenges, or advances)

     - Key concepts, cases, or sources it will mobilize

   - If the user provides only topic labels (e.g., "Section 3: Social Media"), ask them to convert each into a claim (e.g., "Section 3: Platform Algorithms Reshape Collective Attention Rather Than Merely Reflecting It").

   - If no outline is provided, do NOT proceed to generation. Instead, collaborate with the user to construct one first.

3.  **Gather context** if needed

   - A user-specified directory containing selected literature or reference documents

   - Supplied research materials, empirical data, or cited sources

   - The relevant theoretical, methodological, and domain background

### 2. Chapter Structure

A chapter is not a collection of loosely related paragraphs. It is an **argument arc** composed of discrete, load-bearing **units**. Each unit advances one identifiable proposition; together, they form a chain of reasoning that moves the chapter from its opening question to its concluding position.

1. **A chapter is a sequence of argument units.** Each unit is a self-contained analytical move of 800–1000 words, organized around a single core claim crystallized as a subtitle. The subtitle is not a topic label — it is a compressed thesis. For example, "The Limits of Rational Choice" is a label; "Rational Choice Fails When Preferences Are Endogenous" is a claim.

2. **Units are ordered by logical dependency, not by topic proximity.** Unit N must create the conditions — conceptual, evidential, or logical — that make Unit N+1 possible. If two units can be swapped without loss of coherence, the chapter's argumentative spine is weak and must be restructured.

3. **A chapter typically contains 4–7 units.** Fewer than 4 suggests the argument is underdeveloped; more than 7 suggests the chapter tries to do too much and should be split.

Every unit must pass a single gatekeeping question: **can this unit be removed without weakening the chapter's argument?** If yes, the unit fails — it is decoration, not structure. Cut it or reconceive it until it becomes load-bearing.

### 3. Unit Generator

Each unit FOLLOWS the five-phase structure below. These phases are not optional sections to fill in — they are functional stages of an analytical move. A unit that skips a phase will be structurally incomplete.

```
Phase 1: Opening Claim (Positioning) — 3–5 sentences

Directly state the unit's core proposition.
The subtitle must express a defensible, non-trivial claim —
not a neutral description or general background.

Required:
-   A clear argumentative position (what this unit asserts)
-   Conceptual direction (where the reasoning will head)

Test: If the opening can belong to a textbook summary,
      it is too neutral. Rewrite.


Phase 2: Tension or Problem Field

Explain WHY the claim matters by surfacing the friction it addresses.
This may take the form of:
-   An empirical case that resists easy explanation
-   A practice dilemma where existing frameworks fall short
-   A conceptual conflict between competing accounts
-   A theoretical ambiguity that prior work has glossed over

Narrative and example are permitted only insofar as they serve analysis.
Any story told here must generate a question, not merely illustrate a point.


Phase 3: Analytical Development (Core Section)

This is the structural center of the unit —
where the actual intellectual work happens.
Must include:
-   Concept clarification: define or sharpen the key terms at stake
-   Logical decomposition: break the claim into its constituent parts
-   Mechanism explanation: show HOW or WHY the claimed relationship holds
-   Structured reasoning: build the argument through explicit inferential steps

Required: At least two explicit logical progression markers
(e.g., however, therefore, further, in contrast, this implies).
Their presence is a proxy for actual argumentative movement —
if the prose flows without them, it is likely describing rather than reasoning.


Phase 4: Conceptual Elevation

Move from the specific to the abstract.
This phase transforms the analytical work of Phase 3
into a broader intellectual contribution:
-   Introduce or refine a concept
-   Reframe the reader's understanding of a familiar phenomenon
-   Shift the interpretive lens through which the problem is viewed

Test: The reader should see the issue differently after this phase
      than they did at the beginning of the unit.
      If perception is unchanged, the elevation has failed.


Phase 5: Closure and Structural Contribution

Conclude by answering three questions explicitly:
1.  What new understanding has emerged from this unit?
2.  How does this advance the chapter's main thread —
    what does the next unit now have access to that it didn't before?
3.  Why is this unit structurally necessary —
    what would collapse without it?

Test: If closure does not produce advancement
      (i.e., the chapter's argument is in the same position
      as before the unit began), regenerate the unit.
```

Each 800–1000 word unit must satisfy ALL four criteria:

- Contains at least one identifiable **theoretical move** (not merely a claim, but a shift in conceptual territory)
- Includes **abstract-level conceptual articulation** (not only concrete examples or empirical description)
- Produces **structural advancement** (the chapter's argument is measurably further along)
- Is **indispensable** to the chapter's argument (passes the removal test)

A unit that meets three of four is a draft. A unit that meets fewer than three should be discarded and reconceived from scratch.

### Content Generation Process
Step-by-step approach:

1. **Validate the outline**
   * Confirm the user has provided a chapter outline with unit-level claims
   * Verify each outline entry specifies: core claim, role in the argument arc,
     key concepts/cases/sources
   * Check that the unit sequence follows logical dependency —
     Unit N must create the conditions for Unit N+1
   * If the outline contains fewer than 4 or more than 7 units,
     discuss with the user whether to expand or split
2. **Draft units iteratively**
   * Generate one unit at a time, following the five-phase structure
     (Opening Claim → Tension → Analytical Development →
     Conceptual Elevation → Closure)
   * Start with the pivot unit — the unit that makes
     the chapter's most consequential theoretical move (typically Unit 3 or 4)
   * Then draft backward — write the units that build toward the pivot
   * Then draft forward — write the units that extend from the pivot
     toward the chapter's concluding position
   * Write the chapter opening last
   * Run the Unit Quality Gate after each unit before proceeding to the next
3. **Build inter-unit transitions**
   * Review the closure of each unit against the opening of the next
   * Phase 5 of Unit N should connect directly to Phase 1 of Unit N+1
   * Add bridging language where the logical handoff is not self-evident
   * Eliminate redundant restatements that slow momentum
4. **Integrate sources and references**
   * Embed references within Analytical Development (Phase 3)
     where they support reasoning
   * Each unit should engage with at least one identifiable source
     or intellectual tradition
   * Distinguish between sources used as evidence,
     sources used as interlocutors, and sources used as conceptual tools
   * Compile a complete reference list and verify all in-text citations
5. **Review and refine**
   * Argument coherence: read only the subtitles in sequence —
     they should form a legible argument on their own
   * Indispensability test: for each unit, ask whether the chapter's
     argument would collapse without it
   * Conceptual consistency: key terms should carry the same meaning throughout,
     any shift in meaning must be explicitly marked
   * Progression check: the chapter must end in a different intellectual position
     from where it began
   * Elevation audit: at least half of the units should contain a Phase 4 move
     that genuinely reframes understanding

## DESIGN PHILOSOPHY

Book writing is treated as structured intellectual advancement through
modular argument units.

Each section functions as a self-contained yet structurally necessary
conceptual movement.

## Examples

**Example 1: User asks to write a chapter on a broad topic**

```
User: "帮我写一章关于人工智能对教育评价体系影响的内容"

Response:
1. Clarify scope:
   "我来帮你撰写这一章。先确认几个问题：
   - 这一章的核心论点是什么？比如'AI正在瓦解工业时代的标准化评价逻辑'
     还是'AI使多维评价从理念走向技术可行'？
   - 目标读者是教育研究者、政策制定者，还是更广泛的教育工作者？
   - 预期篇幅（5000字、8000字、10000字）？
   - 这一章在全书中的位置——前面的章节已经建立了哪些概念基础？"

2. Require outline:
   "请提供本章的单元级大纲，每个条目需要是一个命题而非标签。例如：
   - ✗ '第一节：传统评价体系'（标签）
   - ✓ '第一节：标准化考试的底层逻辑是工业时代对可量化劳动力的筛选需求'（命题）
   如果你目前只有大致思路，我们可以先一起把大纲搭建出来。"

3. After outline is confirmed, draft units iteratively:
   - Identify the pivot unit (e.g., "AI使过程性数据采集成为可能，
     从而瓦解了终结性评价的垄断地位")
   - Draft pivot unit first, then backward, then forward
   - Run Unit Quality Gate after each unit
   - Build inter-unit transitions
   - Write chapter opening last
```

**Example 2: User provides an outline and asks to generate**

```
User: "我已经有大纲了，请根据以下大纲帮我写第三章：
 1. 知识的本质正在从确定性走向概率性
 2. 课程体系的学科边界在AI时代失去了认识论基础
 3. 动态知识图谱为跨学科课程提供了技术可能
 4. 学习内容的更新速度必须匹配知识生产的速度
 5. 未来课程的核心不是知识本身而是知识生产的方法"

Response:
1. Validate outline:
   - 5个单元，数量合理
   - 每个条目都是命题，符合要求
   - 检查逻辑依赖：单元1（认识论基础）→ 单元2（制度性后果）
     → 单元3（技术条件）→ 单元4（时间维度要求）→ 单元5（范式结论）
   - 逻辑链条成立，确认进入生成

2. Identify pivot unit:
   - 单元3是枢纽——它将前两个单元的理论批判转化为建设性方案，
     为后两个单元提供技术前提

3. Draft in order: 单元3 → 单元2 → 单元1 → 单元4 → 单元5 → 章节开头
   - Each unit follows five-phase structure
     (Opening Claim → Tension → Analytical Development
     → Conceptual Elevation → Closure)
   - Each unit 800-1000 words
   - Run Unit Quality Gate after each

4. Build transitions and integrate references
5. Review: read subtitles in sequence, confirm argument arc holds
```

**Example 3: User provides reference materials and a vague direction**

```
User: "我有一些关于AI教师角色转变的文献资料，放在 /docs/teacher_role/ 目录下，
帮我写一章关于教师角色的内容"

Response:
1. Read reference materials in the specified directory

2. Clarify direction:
   "我已阅读了你提供的文献。在此基础上需要确认：
   - 本章的核心主张是什么？文献中有几种不同取向：
     a) 教师从知识传授者转变为学习设计师
     b) AI替代了教师的部分功能但强化了其不可替代的部分
     c) 教师角色的转变是整个教育系统重构的缩影
     请选择一
```

## Resources

### references/

- `writing_style_guide.md`: Detailed academic writing conventions extracted from example papers
- `ieee_formatting_specs.md`: Complete IEEE formatting specifications
- `acm_formatting_specs.md`: Complete ACM formatting specifications

## Important Notes

- **Always ask for clarification** on topic scope before starting
- **Quality over speed**: Take time to structure properly and write clearly
- **Cite appropriately**: Academic integrity requires proper attribution
- **Be honest about limitations**: Acknowledge gaps or constraints in the research
- **Maintain consistency**: Terminology, notation, and style throughout
- **User provides the research content**: This skill structures and writes; the user provides the technical contributions and findings
