---
name: ai-prompt-gen
description: "Generate optimized prompts for AI models including ChatGPT, Midjourney, and code generation. Use when: (1) creating AI prompts for writing, coding, design, or research, (2) optimizing prompts for specific AI models, (3) analyzing prompt quality, or (4) any AI prompt engineering needs. Supports multiple categories and AI platforms."
---

# AI Prompt Generator

Generate optimized prompts for various AI models. Create prompts for ChatGPT, Midjourney, code generation, and more with customizable styles and parameters.

## When to Use

- Create prompts for AI writing and content generation
- Generate prompts for AI art and design
- Optimize prompts for code generation
- Analyze and improve existing prompts
- Build prompt engineering workflows

## Quick Start

### Generate Writing Prompt
```bash
python3 scripts/ai-prompt-gen.py general writing "人工智能" creative general long
```

### Generate ChatGPT Prompt
```bash
python3 scripts/ai-prompt-gen.py chatgpt "专业作家" "写一篇关于AI的文章" "背景信息" "字数500字"
```

### Generate Midjourney Prompt
```bash
python3 scripts/ai-prompt-gen.py midjourney "未来城市" "futuristic" "科技感" "high"
```

### Analyze Prompt Quality
```bash
python3 scripts/ai-prompt-gen.py analyze "写一个关于AI的文章"
```

## Commands

### `general <category> <topic> [style] [audience] [length]`
Generate general AI prompts for various categories.

**Categories:**
- `writing` - Content writing and creative writing
- `coding` - Code generation and programming
- `marketing` - Marketing and SEO
- `design` - Graphic and UI design
- `research` - Research and analysis
- `analysis` - Data and business analysis

**Style Options:**
- `concise` - Brief and to the point
- `creative` - Creative and imaginative
- `technical` - Technical and detailed
- `detailed` - Comprehensive and thorough

**Length Options:**
- `short` - Brief output
- `medium` - Moderate length (default)
- `long` - Detailed and comprehensive

**Examples:**
```bash
# Creative writing prompt
python3 scripts/ai-prompt-gen.py general writing "人工智能" creative general long

# Technical coding prompt
python3 scripts/ai-prompt-gen.py general coding "排序算法" technical developer medium

# Marketing prompt
python3 scripts/ai-prompt-gen.py general marketing "SEO优化" detailed business short
```

### `chatgpt <role> <task> [context] [constraints]`
Generate ChatGPT-specific prompts with role-playing.

**Examples:**
```bash
# Basic prompt
python3 scripts/ai-prompt-gen.py chatgpt "专业作家" "写一篇关于AI的文章"

# With context and constraints
python3 scripts/ai-prompt-gen.py chatgpt "数据分析师" "分析销售数据" "过去一年的销售数据" "包含趋势分析和预测"
```

### `midjourney <subject> <style> <mood> [quality]`
Generate prompts for Midjourney AI art generation.

**Style Options:**
- `realistic` - Photorealistic style
- `artistic` - Artistic and creative
- `cartoon` - Cartoon and animated
- `minimalist` - Simple and clean
- `vintage` - Vintage and retro
- `futuristic` - Sci-fi and futuristic

**Quality Options:**
- `high` - High quality (default)
- `medium` - Good quality
- `low` - Basic quality

**Examples:**
```bash
# Futuristic city
python3 scripts/ai-prompt-gen.py midjourney "未来城市" "futuristic" "科技感" "high"

# Artistic portrait
python3 scripts/ai-prompt-gen.py midjourney "人像" "artistic" "优雅" "high"
```

### `code <language> <task> [difficulty]`
Generate prompts for code generation.

**Difficulty Options:**
- `beginner` - Simple and well-commented
- `intermediate` - Moderate complexity (default)
- `advanced` - Complex and optimized

**Examples:**
```bash
# Python sorting algorithm
python3 scripts/ai-prompt-gen.py code "Python" "排序算法" "intermediate"

# JavaScript web app
python3 scripts/ai-prompt-gen.py code "JavaScript" "待办事项应用" "beginner"
```

### `analyze <prompt>`
Analyze the quality of a prompt and provide feedback.

**Examples:**
```bash
python3 scripts/ai-prompt-gen.py analyze "写一个关于AI的文章"

python3 scripts/ai-prompt-gen.py analyze "你是一个程序员，帮我写代码"
```

### `list`
List all available prompt templates and categories.

```bash
python3 scripts/ai-prompt-gen.py list
```

## Prompt Categories

### Writing
- **Creative Writing**: Generate original, engaging content
- **Technical Writing**: Create professional documentation
- **Business Writing**: Produce data-driven reports

### Coding
- **Algorithms**: Implement efficient algorithms
- **Web Development**: Build modern web applications
- **Data Analysis**: Process and visualize data

### Marketing
- **SEO**: Optimize for search engines
- **Social Media**: Plan social campaigns
- **Email Marketing**: Design email campaigns

### Design
- **Logo Design**: Create brand identities
- **UI Design**: Design user interfaces
- **Brand Design**: Develop brand guidelines

### Research
- **Market Research**: Analyze market trends
- **Technical Research**: Evaluate technology solutions
- **Academic Research**: Write scholarly reviews

### Analysis
- **Financial Analysis**: Analyze financial data
- **Business Analysis**: Diagnose business problems
- **Data Analysis**: Discover data insights

## Examples

### Content Creation
```bash
# Blog post about AI
python3 scripts/ai-prompt-gen.py general writing "人工智能的未来" creative general long

# Technical documentation
python3 scripts/ai-prompt-gen.py general writing "API文档" technical developer medium
```

### AI Art Generation
```bash
# Cyberpunk city
python3 scripts/ai-prompt-gen.py midjourney "赛博朋克城市" "futuristic" "霓虹灯" "high"

# Minimalist logo
python3 scripts/ai-prompt-gen.py midjourney "简约logo" "minimalist" "现代" "high"
```

### Code Generation
```bash
# Python data analysis
python3 scripts/ai-prompt-gen.py code "Python" "数据分析脚本" "intermediate"

# JavaScript calculator
python3 scripts/ai-prompt-gen.py code "JavaScript" "计算器应用" "beginner"
```

### ChatGPT Optimization
```bash
# Role-playing prompt
python3 scripts/ai-prompt-gen.py chatgpt "历史学家" "解释二战历史" "面向中学生" "用简单易懂的语言"

# Expert consultation
python3 scripts/ai-prompt-gen.py chatgpt "财务顾问" "分析投资策略" "高风险承受能力" "包含具体建议"
```

## Tips

- Use specific, clear language in your prompts
- Provide context and constraints when relevant
- Choose appropriate difficulty levels
- Test different styles for optimal results
- Use the analyze feature to improve prompts
- Combine multiple prompt types for complex tasks

## Prompt Quality Analysis

The `analyze` command evaluates prompts based on:
- **Length**: Prompts should be sufficiently detailed
- **Requirements**: Clear objectives and expectations
- **Context**: Background information when needed
- **Constraints**: Limitations and specific requirements

## Troubleshooting

**"Unsupported category" error:**
- Check spelling of category names
- Use `list` command to see available categories
- Ensure category is one of: writing, coding, marketing, design, research, analysis

**Generic prompts:**
- Add more specific details to the topic
- Include audience information
- Specify desired style and length
- Use role-playing for ChatGPT prompts

**Poor AI results:**
- Use the `analyze` command to improve prompt quality
- Add more context and constraints
- Try different style options
- Be more specific about requirements

## Advanced Usage

### Combining Prompts
```bash
# Generate a writing prompt, then optimize it
python3 scripts/ai-prompt-gen.py general writing "气候变化" creative general long
python3 scripts/ai-prompt-gen.py analyze "生成的提示词"
```

### Batch Generation
```bash
# Generate multiple prompts for comparison
python3 scripts/ai-prompt-gen.py general writing "AI" concise general short
python3 scripts/ai-prompt-gen.py general writing "AI" creative general long
```

### Custom Templates
The script includes built-in templates, but you can modify the code to add your own custom prompt templates for specific use cases.
