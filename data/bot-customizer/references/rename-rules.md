# Agent-ID Renaming Decision Rules

## Core Principle

**Rename when specialization justifies a distinct identity.** The agent-id should reflect the agent's primary focus. Generic IDs serve general purposes; specific IDs serve specialized domains.

## Decision Framework

### Rename Triggers (YES)

Rename when custom content introduces:

1. **Specific Technology Stack**
   - Original: `code-viewer`
   - Custom: "专注于Python代码审查"
   - New ID: `python-code-reviewer` or `python-code-viewer`
   - **Reason**: Technology specificity warrants distinct identity

2. **Business Domain Specialization**
   - Original: `customer-service`
   - Custom: "PDF业务客服，处理文档相关问题"
   - New ID: `pdf-customer-service`
   - **Reason**: Business line creates distinct scope

3. **Functional Vertical**
   - Original: `assistant`
   - Custom: "数据分析专家，处理财务报表"
   - New ID: `financial-data-analyst`
   - **Reason**: From generalist to specialist role

4. **Combined Specialization**
   - Original: `writer`
   - Custom: "技术博客写作，专注于AI和云计算领域"
   - New ID: `tech-ai-writer` or `ai-cloud-writer`
   - **Reason**: Multiple specific dimensions combine

### Keep Original ID (NO)

Do NOT rename when:

1. **Minor Tone Adjustments**
   - Custom: "更友好一点，使用emoji"
   - **Reason**: Style change, not scope change

2. **Process Refinement**
   - Custom: "回答问题前先列出思考步骤"
   - **Reason**: Workflow enhancement, not specialization

3. **Quality Enhancement**
   - Custom: "提供更详细的解释和示例"
   - **Reason**: Depth increase, not domain shift

4. **General Capability Expansion**
   - Original: `assistant`
   - Custom: "帮我管理日程、发邮件、查天气"
   - **Reason**: Still general-purpose assistant

5. **Already Specific ID**
   - Original: `python-code-reviewer`
   - Custom: "也检查一下类型提示"
   - **Reason**: ID already specific enough

## Naming Conventions

### Pattern A: Technology + Role

- `{tech}-{role}`: `python-code-reviewer`, `react-developer`, `sql-tuner`
- Use when technology is primary differentiator

### Pattern B: Domain + Role

- `{domain}-{role}`: `pdf-customer-service`, `finance-analyst`, `legal-writer`
- Use when business domain is primary differentiator

### Pattern C: Function + Modifier

- `{function}-{modifier}`: `writer-technical`, `assistant-data`, `reviewer-security`
- Use when enhancing base function with specific focus

### Pattern D: Combined Specificity

- `{domain}-{tech}-{role}`: `finance-python-analyst`, `medical-nlp-researcher`
- Use when multiple dimensions are critical (avoid overly long IDs)

## Decision Process

### Step 1: Extract Key Specialization Dimensions

From custom content, identify:

- **Technology**: Specific languages, frameworks, tools
- **Domain**: Business area, industry, subject matter
- **Function**: Primary task or goal
- **Scope**: Breadth vs. depth of focus

### Step 2: Compare with Original ID

Ask:

- Is original ID generic? (e.g., `assistant`, `writer`, `helper`)
- Does custom content narrow scope significantly?
- Would users expect different IDs for original vs. customized?

### Step 3: Check Specialization Threshold

**Threshold Met (Rename):**

- Custom content mentions 3+ specific technologies/domains
- Role shifts from general to expert/specialist
- Target audience changes (general users → domain professionals)

**Threshold Not Met (Keep):**

- Custom content is qualitative (better, faster, clearer)
- No new domain knowledge required
- Target audience unchanged

### Step 4: Generate New ID

If renaming:

1. Choose naming pattern (A, B, C, or D)
2. Keep ID concise (2-3 words max, hyphen-separated)
3. Use lowercase, no spaces
4. Prefer clarity over brevity

### Step 5: Validate No Conflicts

Before finalizing:

- Check if new ID already exists in `easyclaw.json`
- If conflict → add numeric suffix (e.g., `python-reviewer-2`) or find alternative
- Report conflict error if no good alternative exists

## Examples with Reasoning

### Example 1: Rename

**Input:**

- Original ID: `code-viewer`
- Custom: "专注于Rust代码审查，重点关注内存安全和并发问题"

**Analysis:**

- Technology: Rust (specific)
- Function: 内存安全 + 并发 (specialized concerns)
- Threshold: YES (specific tech + specialized function)

**Decision:** Rename
**New ID:** `rust-code-reviewer`
**Reasoning:** Technology specialization + domain expertise justify distinct identity

---

### Example 2: Keep

**Input:**

- Original ID: `assistant`
- Custom: "回答更友好，多用表情符号，解释更详细"

**Analysis:**

- Technology: None
- Domain: None
- Function: Same (general assistance)
- Changes: Tone, style, quality

**Decision:** Keep `assistant`
**Reasoning:** No scope narrowing, only presentation changes

---

### Example 3: Rename

**Input:**

- Original ID: `customer-service`
- Custom: "PDF业务客服，处理文档格式转换、编辑、合并等问题"

**Analysis:**

- Domain: PDF业务 (specific business line)
- Function: Still customer service, but scoped
- Threshold: YES (business domain specialization)

**Decision:** Rename
**New ID:** `pdf-customer-service`
**Reasoning:** Business domain creates distinct support category

---

### Example 4: Keep

**Input:**

- Original ID: `python-code-reviewer`
- Custom: "也检查一下类型提示和docstring"

**Analysis:**

- Technology: Already Python-specific
- Function: Code review enhancement, not shift
- Threshold: NO (minor feature addition)

**Decision:** Keep `python-code-reviewer`
**Reasoning:** ID already specific; custom content adds depth, not new scope

---

### Example 5: Rename (Complex)

**Input:**

- Original ID: `writer`
- Custom: "技术写作专家，专注于云计算和DevOps领域的博客文章和技术文档"

**Analysis:**

- Domain: 云计算 + DevOps (specific domains)
- Function: 技术写作 (narrowed from general writing)
- Audience: Tech professionals (vs general readers)
- Threshold: YES (multiple specialization dimensions)

**Decision:** Rename
**New ID:** `devops-tech-writer` or `cloud-tech-writer`
**Reasoning:** Domain + function specialization create distinct role

## Edge Cases

### Case 1: Multiple Specializations

If custom content mentions many areas (e.g., "Python, Java, Go代码审查"):

- Don't use multi-tech ID: ❌ `python-java-go-reviewer`
- Keep generic or use most prominent: ✅ `multi-lang-code-reviewer` or keep `code-viewer`

### Case 2: Vague Specialization

If custom content is unclear (e.g., "更专业的助手"):

- Default to NO rename
- Ask user for clarification if needed

### Case 3: Original ID Already Perfect

If original ID matches customization exactly:

- Original: `python-code-reviewer`
- Custom: "审查Python代码"
- Decision: Keep (already aligned)

## Implementation Notes

When renaming:

1. Rename directory first: `workspace-{old}` → `workspace-{new}`
2. Update `easyclaw.json`:
   - `agents.list[n].id`: old → new
   - `agents.list[n].workspace`: update path
   - `agents.list[n].description`: update to reflect specialization
3. Do NOT modify other files (AGENTS.md path is relative to workspace)
4. Log the rename action for user confirmation
