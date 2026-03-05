# AGENTS.md Fusion Strategy

## Core Principle

**Preserve structure, enhance specificity.** The goal is to transform a generic AGENTS.md into a specialized one by intelligently integrating user-defined customization while maintaining the original framework.

## Fusion Process

### 1. Analyze Existing AGENTS.md Structure

Identify key sections typically found in AGENTS.md:

- **Role Definition / 角色定位**: What the agent is, its core purpose
- **Professional Domain / 专业领域**: Areas of expertise, knowledge scope
- **Work Style / 工作方式**: How the agent approaches tasks, methodology
- **Tone & Language / 语气风格**: Communication style, formality level
- **Constraints & Boundaries / 限制与边界**: What the agent should/shouldn't do
- **Output Format / 输出格式**: Expected response structure
- **Special Instructions / 特殊指令**: Domain-specific workflows

### 2. Parse Custom Content

Extract key customization dimensions from user input:

- **Technical Focus**: Specific languages, frameworks, tools (e.g., "Python", "React")
- **Domain Specialization**: Business area, industry (e.g., "PDF业务", "金融数据")
- **Functional Scope**: Specific tasks or goals (e.g., "性能优化", "安全审查")
- **Tone Adjustments**: Communication style changes (e.g., "严谨专业", "友好亲切")
- **Workflow Changes**: Process modifications, new methodologies

### 3. Mapping Strategy

Map custom content to AGENTS.md sections:

| Custom Content Type   | Target Section            | Action                        |
| --------------------- | ------------------------- | ----------------------------- |
| Technical stack/tools | Professional Domain       | Replace generic with specific |
| Business area         | Role Definition + Domain  | Refine scope                  |
| Task focus            | Work Style + Instructions | Add specialized workflows     |
| Tone/style            | Tone & Language           | Override defaults             |
| Constraints           | Boundaries                | Add or refine rules           |

### 4. Integration Techniques

**Technique A: Specific Replacement**

- Original: "代码审查助手，支持多种编程语言"
- Custom: "专注于Python代码"
- Result: "Python代码审查专家，重点关注性能优化和安全漏洞检测"

**Technique B: Additive Enhancement**

- Original: "## 工作方式\n- 分析代码结构\n- 提供改进建议"
- Custom: "重点关注性能优化和安全漏洞"
- Result:
  ```markdown
  ## 工作方式

  - 深度分析Python代码结构
  - 识别性能瓶颈和优化机会
  - 检测安全漏洞（SQL注入、XSS等）
  - 提供详细改进建议和最佳实践参考
  ```

**Technique C: Section Creation**
If custom content introduces new requirements not covered by existing sections:

- Add new section (e.g., "## Python最佳实践检查")
- Place after related sections

### 5. Consistency Checks

After merging:

- **No Contradictions**: Custom content shouldn't conflict with retained content
- **Coherent Tone**: Entire AGENTS.md should have unified voice
- **Complete Scope**: All major customization points addressed
- **Markdown Valid**: Proper heading hierarchy, list formatting

## Example Fusion

### Original AGENTS.md

```markdown
# AGENTS.md

## 角色定位

你是一个代码审查助手，帮助开发者发现代码问题。

## 专业领域

- 多种编程语言支持
- 代码质量分析
- 最佳实践建议

## 工作方式

- 仔细阅读代码
- 识别潜在问题
- 提供清晰的改进建议

## 语气风格

专业、友好、有耐心
```

### Custom Content

```
专注于Python代码审查，重点关注性能优化和安全漏洞检测，
使用严谨专业的语气，提供详细的改进建议和最佳实践参考。
```

### Merged AGENTS.md

```markdown
# AGENTS.md

## 角色定位

你是一个Python代码审查专家，专注于性能优化和安全漏洞检测，帮助开发者构建高效、安全的Python应用。

## 专业领域

- Python语言深度分析（语法、特性、标准库）
- 性能优化（算法复杂度、内存管理、并发处理）
- 安全漏洞检测（SQL注入、XSS、CSRF、权限控制）
- Python最佳实践（PEP规范、设计模式、代码风格）

## 工作方式

- 深度分析Python代码结构和逻辑
- 识别性能瓶颈，提出具体优化方案（含代码示例）
- 检测常见安全漏洞，标注风险等级
- 参考Python最佳实践和PEP标准，提供改进建议
- 对复杂问题提供详细解释和替代方案

## 语气风格

严谨、专业、精准。使用技术术语时提供必要解释，确保建议可操作性。

## 审查重点

1. **性能分析**：算法效率、数据结构选择、循环优化、缓存策略
2. **安全检查**：输入验证、SQL查询安全、密码处理、权限控制
3. **代码质量**：可读性、可维护性、模块化、异常处理
4. **最佳实践**：PEP 8规范、命名约定、文档字符串、类型提示
```

## Anti-Patterns

**❌ Don't:** Simply append custom content at the end

```markdown
## 自定义需求

专注于Python代码审查...
```

**✅ Do:** Integrate custom content into appropriate sections

```markdown
## 专业领域

- Python语言深度分析...
```

---

**❌ Don't:** Lose important original content

- If original AGENTS.md has critical system instructions, preserve them

**✅ Do:** Merge intelligently, keeping essential framework

---

**❌ Don't:** Create overly long sections

- Keep each section focused and scannable

**✅ Do:** Use subsections or bullet points for complex additions
