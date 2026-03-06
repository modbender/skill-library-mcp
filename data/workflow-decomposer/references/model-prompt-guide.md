# Model-Specific Prompt Guide

Generate prompts optimized for each model's strengths and preferred communication style.

## Alibaba Qwen Series (bailian/qwen*)

### Characteristics
- Strong with structured, step-by-step instructions
- Handles Chinese and English equally well
- Good at following explicit formatting requirements
- Prefers clear, direct language

### Prompt Pattern

```markdown
## 任务：[任务名称]

### 背景
[简要说明任务背景]

### 要求
1. [具体要求 1]
2. [具体要求 2]
3. [具体要求 3]

### 输出格式
[明确说明期望的输出格式]

### 约束条件
- [约束 1]
- [约束 2]
```

### Example

```markdown
## 任务：创建 React 组件

### 背景
需要创建一个天气显示组件，展示温度、湿度、风速

### 要求
1. 使用 TypeScript
2. 支持 Props 传入天气数据
3. 包含错误处理
4. 响应式设计

### 输出格式
- 完整的 TSX 代码
- 类型定义
- 使用示例

### 约束条件
- 不使用外部 CSS 库
- 支持深色模式
```

---

## Claude Series (claude-*)

### Characteristics
- Excels with context-rich explanations
- Good at reasoning chains and analysis
- Appreciates ethical considerations
- Responds well to "think step by step" prompts

### Prompt Pattern

```markdown
I need help with [task]. Here's the context:

**Background:** [detailed context]
**Goal:** [clear objective]
**Constraints:** [limitations]

Please approach this by:
1. First, analyze [aspect 1]
2. Then, consider [aspect 2]
3. Finally, produce [deliverable]

Think through this step-by-step, explaining your reasoning as you go.
```

### Example

```markdown
I need help building a weather dashboard component. Here's the context:

**Background:** We're building a personal weather tracking app that displays current conditions and forecasts
**Goal:** Create a React component that shows temperature, humidity, and wind speed with proper error handling
**Constraints:** Must use TypeScript, no external CSS libraries, support dark mode

Please approach this by:
1. First, analyze the data structure we'll receive from the weather API
2. Then, consider edge cases (loading states, errors, missing data)
3. Finally, produce a complete, production-ready component

Think through this step-by-step, explaining your reasoning as you go.
```

---

## GPT Series (gpt-*)

### Characteristics
- Prefers concise, focused prompts
- Good with examples and few-shot learning
- Handles creative tasks well
- Responds to role-playing ("You are an expert...")

### Prompt Pattern

```markdown
You are an expert [role]. 

Task: [clear, concise task description]

Examples:
Input: [example input]
Output: [example output]

Requirements:
- [requirement 1]
- [requirement 2]

Deliver: [specific deliverable]
```

### Example

```markdown
You are an expert React developer.

Task: Create a weather display component

Examples:
Input: { temp: 22, humidity: 65, wind: 12 }
Output: A styled component showing "22°C, 65% humidity, 12 km/h wind"

Requirements:
- TypeScript
- Props-based data input
- Error boundaries
- Responsive design

Deliver: Complete TSX file with types and usage example
```

---

## Coding-Specialized Models

### Characteristics
- Technical precision over explanation
- Input/output examples critical
- Version/environment specs needed
- Test cases appreciated

### Prompt Pattern

```markdown
## Implementation Task

**Language:** [language + version]
**Framework:** [framework + version]
**Environment:** [runtime details]

**Input:**
```[language]
[example input]
```

**Expected Output:**
```[language]
[example output]
```

**Requirements:**
- [technical requirement 1]
- [technical requirement 2]

**Tests:**
- [test case 1]
- [test case 2]
```

---

## Research/Web Models

### Characteristics
- Source citation important
- Date sensitivity matters
- Multiple perspectives valued
- Verification steps needed

### Prompt Pattern

```markdown
Research Task: [topic]

**Scope:**
- Time period: [date range]
- Sources: [preferred source types]
- Regions: [geographic focus]

**Deliverables:**
1. Summary of findings
2. Key sources with citations
3. Confidence level for each claim
4. Areas needing verification

**Constraints:**
- Prioritize sources from [timeframe]
- Include [specific perspectives]
- Flag any conflicting information
```

---

## Quick Reference Table

| Model Family | Prompt Style | Key Elements | Avoid |
|--------------|--------------|--------------|-------|
| Qwen/Alibaba | Structured, bilingual | Numbered lists, clear format specs | Vague instructions |
| Claude | Context-rich, reasoning | Background, step-by-step thinking | Overly terse prompts |
| GPT | Concise, example-driven | Role, examples, clear deliverable | Long preamble |
| Coding | Technical, precise | Versions, I/O examples, tests | Non-technical fluff |
| Research | Source-focused | Citations, dates, verification | Uncited claims |

---

## Prompt Generation Function

When decomposing a task, use this logic:

```python
def generate_prompt_for_model(step, model):
    if 'qwen' in model or 'bailian' in model:
        return format_qwen_prompt(step)
    elif 'claude' in model:
        return format_claude_prompt(step)
    elif 'gpt' in model:
        return format_gpt_prompt(step)
    elif is_coding_task(step):
        return format_coding_prompt(step)
    else:
        return format_generic_prompt(step)
```
