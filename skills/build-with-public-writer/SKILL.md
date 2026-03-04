---
name: build-with-public-writer
description: Systematically build a "Build with Public" technical blog writing workflow, including directory architecture, version management, multi-angle approaches, link sharing, and complete toolchain
---

# Build with Public - Technical Blog Writing System

## Overview

This skill helps you establish a complete **Build with Public** technical blog writing workflow. From directory architecture setup, Git version management, multi-angle writing approach design, to final article link sharing, it provides end-to-end toolchain support.

**Core Value**:
- 🏗️ Standardized blog project architecture
- 📝 Systematic multi-angle writing process  
- 🔄 Versioned iteration management mechanism
- 🌐 Instant link sharing capability

## When to Use

When you need to:
- Establish a personal technical blog writing workflow
- Systematically manage multi-version technical articles
- Build technical influence through public building
- Solidify the writing process into reusable assets

## Prerequisites

- Python 3.11+
- Git
- An accessible domain or IP (for link sharing)

---

## Workflow

### Phase 1: Project Initialization

#### Step 1: Determine Project Name

Confirm the blog project name with the user (e.g., codewithriver, techblog, buildinpublic, etc.):

```
Suggested name: codewithriver
Suggested name: tech-notes
Suggested name: buildlog
```

#### Step 2: Create Directory Architecture

```bash
mkdir -p ~/{project-name}/{articles,draft,images,logs,tweets}
cd ~/{project-name}
```

**Standard Directory Structure**:
```
{project-name}/
├── articles/          # Published articles (version managed)
│   ├── 2026-03-02-topic-v1.md
│   ├── 2026-03-02-topic-v2.md
│   └── ...
├── draft/             # Writing outlines and drafts
│   ├── 2026-03-02-topic-outline-01.md
│   └── ...
├── images/            # Article images
├── logs/              # Writing logs
├── tweets/            # Promotional copy
├── .env               # Configuration (port, password, domain)
├── server.py          # Web server
└── .git/              # Version control
```

#### Step 3: Initialize Git Repository

```bash
cd ~/{project-name}
git init
git config user.email "your@email.com"
git config user.name "your-name"
```

#### Step 4: Create Web Server

Create `server.py`:

```python
#!/usr/bin/env python3
"""Build with Public - Web Server"""

import os
import mimetypes
from functools import wraps
from flask import Flask, send_file, render_template_string, abort, request, Response
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

CONTENT_DIR = Path(os.environ.get('CONTENT_DIR', os.getcwd()))
PORT = int(os.environ.get('PORT', 12000))
HOST = os.environ.get('HOST', '0.0.0.0')
AUTH_PASSWORD = os.environ.get('AUTH_PASSWORD', 'openskill')
AUTH_USERNAME = os.environ.get('AUTH_USERNAME', 'user')

# [Server code template, full implementation omitted here]
# Full code reference: templates/server.py.template in skill package

def check_auth(username, password):
    return username == AUTH_USERNAME and password == AUTH_PASSWORD

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return Response('Authentication required', 401, {'WWW-Authenticate': 'Basic realm="BuildWithPublic"'})
        return f(*args, **kwargs)
    return decorated

@app.route('/')
@requires_auth
def index():
    # [Directory listing implementation]
    pass

@app.route('/<path:subpath>')
@requires_auth
def serve_path(subpath):
    # [File serving implementation]
    pass

if __name__ == '__main__':
    print(f"🚀 Server starting on http://{HOST}:{PORT}")
    app.run(host=HOST, port=PORT, debug=False)
```

#### Step 5: Create .env Configuration File

```bash
cat > .env << 'EOF'
# Build with Public - Configuration
PORT=12000
HOST=0.0.0.0
AUTH_USERNAME=user
AUTH_PASSWORD=openskill
CUSTOM_DOMAIN=your-domain.com
EOF
```

#### Step 6: Start Server and Commit

```bash
# Install dependencies
pip install flask python-dotenv

# Start server
python server.py &

# Initial commit
git add .
git commit -m "[$(date +%Y-%m-%d)] init: Initialize Build with Public writing system"
```

---

### Phase 2: Writing Requirements Analysis (with Completeness Check)

#### Requirements Completeness Assessment

Before officially starting, assess whether the information provided by the user is sufficient. Check the following **required items**:

| Check Item | Status | Follow-up Question |
|--------|:----:|----------|
| **Writing Topic** | ☐ | "What technical topic do you want to write about?" |
| **Target Audience** | ☐ | "What level are the readers? (Beginner/Intermediate/Expert)" |
| **Core Goal** | ☐ | "What's the main purpose of the article? (Teaching/Sharing/Problem-solving)" |
| **Expected Length** | ☐ | "How long do you want it? (Short/Medium/Long)" |
| **Technical Background** | ☐ | "What tech stacks/tools/frameworks are involved?" |
| **Personal Experience** | ☐ | "What's your hands-on experience in this area?" |
| **Reference Cases** | ☐ | "Do you have similar reference articles?" |
| **Deadline** | ☐ | "When do you expect to publish?" |

**Criteria**:
- ✅ **Sufficient Information** (≥6 items clear) → Proceed to Phase 3
- ⚠️ **Partially Missing** (4-5 items clear) → Ask for missing items, can continue
- ❌ **Severely Insufficient** (≤3 items clear) → **Must supplement before continuing**

#### Follow-up Strategy

When conditions are vague, use **progressive questioning**:

**Round 1 (Topic Focus)**:
```
The "{topic}" you mentioned is quite broad. To provide a precise writing plan,
could you tell me:
1. What specific tech stack/tools are involved?
2. Do you want to write a tutorial (How-to) or experience sharing (Lesson-learned)?
3. What's the approximate technical level of the readers?
```

**Round 2 (Deep Dive)**:
```
Thanks for the details! To make the plan more fitting, I'd like to know:
1. How much hands-on experience do you have in this area? (Affects article credibility positioning)
2. Are there any technical difficulties or pitfalls you want to emphasize?
3. What do you expect readers to gain after reading? (Learn skills/Avoid pitfalls/Understand principles)
```

**Round 3 (Feasibility Confirmation)**:
```
Finally, confirm two details:
1. How long do you want the article to be? (Affects structure depth)
2. When do you expect to publish? (Affects iteration count)
```

#### Minimum Viable Conditions (MVP)

Even if information is incomplete, the following **4 items are required**, otherwise cannot start:

1. ✅ **Writing Topic** - What to write?
2. ✅ **Target Audience** - Who to write for?
3. ✅ **Core Goal** - What to achieve?
4. ✅ **Technical Background** - What technology is involved?

**If any of the above is missing, must ask for clarification.**

#### Step 1: Deep Understanding of Writing Topic

After sufficient information, further clarify:

**Topic Dimension Analysis**:
- **Technical Depth**: Principle level / Application level / Tool level?
- **Time Dimension**: Historical review / Current analysis / Future outlook?
- **Practice Dimension**: Pure theory / With examples / Complete tutorial?

**Example Comparison**:

| Vague Input | After Clarification |
|----------|--------|
| "Write about AI" | "Write a specific tutorial on building skill assessment tools with OpenClaw" |
| "Share my experience" | "Share 12-hour hands-on record from skill consumer to contributor" |
| "Introduce a tool" | "Introduce skill-explorer: Design and implementation of 8-stage skill assessment framework" |

#### Step 2: Quality Goal Setting

Confirm quality expectations with the user:

| Dimension | Options | Impact |
|------|------|------|
| **Technical Depth** | Beginner intro / Advanced practice / Deep principles | Determines code examples and architecture diagram count |
| **Originality** | Experience reproduction / Solution integration / Original method | Determines research time and innovation point extraction |
| **Practicality** | Concept introduction / Follow-along operation / Production-ready | Determines code completeness and testing requirements |
| **Distribution Goal** | Personal notes / Community sharing / Professional publication | Determines polish level and promotion strategy |

---

### Phase 3: Multi-Angle Approach Design

Based on the writing topic, design 3-5 different writing angles.

#### Common Angle Templates

| Angle | Applicable Scenario | Characteristics |
|------|---------|------|
| **Tutorial** | Teach readers how to do | Clear steps, reproducible |
| **Problem-Solving** | Solve specific pain points | Problem-oriented, highly practical |
| **Deep Analysis** | Deep dive into technical principles | Technical depth, highly professional |
| **Hands-on Experience** | Share real cases | Authentic and credible, valuable reference |
| **Comparison Review** | Compare multiple solutions | Objective and neutral, helps decision-making |
| **Trend Outlook** | Analyze development direction | Forward-looking, thought-provoking |

#### Output Outline Files

Create outline files for each angle:

```bash
# File naming format: {date}-{topic}-{angle}-outline.md
# Examples:
# 2026-03-02-skill-explorer-tutorial-outline.md
# 2026-03-02-skill-explorer-case-study-outline.md
```

**Outline Content Structure**:
```markdown
# Outline Option: {Angle Name}

**Date**: YYYY-MM-DD
**Title**: "Article Title"

## Core Viewpoint
- One sentence summarizing the core argument

## Outline Structure
1. **Introduction**: Introduce problem and value
2. **Part One**: ...
3. **Part Two**: ...
4. **Conclusion**: Summary and outlook

## Target Audience
- Reader persona description

## Estimated Word Count
- XXXX words

## Keywords
keyword1, keyword2, ...
```

#### Save to draft Directory

```bash
# Example
draft/
├── 2026-03-02-skill-explorer-tutorial-outline.md
├── 2026-03-02-skill-explorer-case-study-outline.md
├── 2026-03-02-skill-explorer-methodology-outline.md
└── ...
```

---

### Phase 4: User Selection and Confirmation

Present options for user selection:

```markdown
## Available Writing Approaches

### Approach 1: Tutorial ⭐Recommended
- **Title**: "From Scratch: How to Build XXXX"
- **Features**: Clear steps, beginner-friendly
- **Estimate**: 4000 words, 25-minute read

### Approach 2: Hands-on Experience
- **Title**: "How I Solved XXXX in One Week"
- **Features**: Real case, pitfall guide
- **Estimate**: 3500 words, 20-minute read

### Approach 3: Deep Analysis
- **Title**: "The Architecture Design Behind XXXX"
- **Features**: Technical depth, principle analysis
- **Estimate**: 5000 words, 30-minute read

**Please select** (or request adjustments): ...
```

After user confirmation, proceed to writing phase.

---

### Phase 5: Article Writing

#### Version Numbering Rules

Use semantic versioning:

| Version | Meaning | Example |
|------|------|------|
| v1.0 | First draft complete | Basic content complete |
| v1.1 | Minor revision | Fix errors, optimize expression |
| v2.0 | Major revision | Structure adjustment, angle change |
| v2.1 | Fine-tuning based on v2.0 | Detail optimization |

#### File Naming Convention

```
{date}-{topic}-{slug}-v{version}.md

Examples:
- 2026-03-02-skill-explorer-tutorial-v1.md
- 2026-03-02-skill-explorer-tutorial-v2.md
- 2026-03-02-skill-explorer-tutorial-v2.1.md
```

#### Writing Process

1. **Create v1.0**
   ```bash
   # Create first draft based on selected outline
   cat > articles/2026-03-02-topic-v1.md << 'EOF'
   # Article content
   EOF
   ```

2. **Iterative Optimization**
   - Create v1.1, v1.2... based on feedback
   - Upgrade to v2.0 for major adjustments

3. **Commit to Git After Each Modification**
   ```bash
   git add articles/
   git commit -m "[YYYY-MM-DD] v{X.Y}: Modification description"
   ```

---

### Phase 6: Link Sharing

After article completion, provide access link:

```
Article link: http://your-domain.com:12000/articles/2026-03-02-topic-v2.md
```

**Default Information for Sharing**:
- Access requires password (default: openskill)
- Browser will remember password
- Supports direct Markdown file download

---

## Best Practices

### Git Commit Convention

```bash
# Format
[Date] Type: Description

- Change detail 1
- Change detail 2

# Types
feat:    New article/new feature
fix:     Error correction
docs:    Documentation update
refactor: Refactoring/renaming
style:   Format adjustment
```

### Version Control Strategy

- **Minor changes** (typos, formatting): Don't upgrade version number, overwrite directly
- **Content optimization** (paragraph adjustment, detail supplement): v1.0 → v1.1
- **Structure adjustment** (outline change, angle conversion): v1.x → v2.0

### Directory Maintenance

Regular cleanup:
- Deprecated outlines in `draft/`
- Outdated versions in `articles/` (keep latest 2-3 versions)

---

## Output Templates

### Approach Selection Display Template

```markdown
## 📝 Writing Approach Options

Based on your requirement "{topic}", I've designed {N} writing angles:

### Approach 1: {Angle Name}
**Title**: "{Suggested Title}"
**Core Viewpoint**: {One sentence summary}
**Target Audience**: {Reader persona}
**Estimated Length**: {word count} words
**Outline Points**:
1. {Point 1}
2. {Point 2}
3. {Point 3}

---

[Approach 2, 3 ...]

## Please Select

Reply with a number (1/{N}) to select an approach, or tell me what adjustments are needed.
```

### Article Completion Notification Template

```markdown
✅ Article completed!

**Version**: v{X.Y}
**File**: articles/{filename}
**Word Count**: {N} words
**Access Link**: http://{domain}:12000/articles/{filename}

**Access Password**: openskill

**Version History**:
- v1.0: First draft complete
- v1.1: Expression optimization
- v2.0: Structure adjustment
- v{X.Y}: Current version

If modifications are needed, please specify requirements.
```

---

## Examples

### Example 1: Skill Explorer Article Series

**Project**: codewithriver  
**Topic**: skill-explorer skill development  
**Output**:
- draft/2026-03-02-skill-explorer-tutorial-outline.md
- draft/2026-03-02-skill-explorer-case-study-outline.md
- draft/2026-03-02-skill-explorer-methodology-outline.md
- articles/2026-03-02-skill-explorer-tutorial-v1.md
- articles/2026-03-02-skill-explorer-tutorial-v2.md
- articles/2026-03-02-skill-explorer-tutorial-v2.1.md
- articles/2026-03-02-skill-explorer-tutorial-v2.2.md

---

## Related Skills

- **skill-explorer**: Evaluate and select ClawHub skills
- **tweet-writer**: Write promotional copy
- **marketing-mode**: Develop content marketing strategy

---

## Tips

1. **Keep iterating**: Good articles are refined through revisions, don't fear version number increases
2. **Commit promptly**: Commit every meaningful change to Git
3. **Try multiple angles**: Different angles on the same topic may attract different readers
4. **Share via links**: Cultivate the habit of sharing links rather than full text, train reader access habits

---

*Build with Public - Make Your Technical Growth Visible*


---

## Appendix B: Xiaohongshu Platform Adaptation Guide

### Why Platform Adaptation is Needed

The same technical content can be published to multiple platforms, but each platform has different user habits and content formats.

**Platform Comparison**:
- Technical Blog: Professional developers, in-depth long articles, 3000-8000 words
- Xiaohongshu: Young learners, casual short notes, 500-1500 words
- Twitter/X: Tech professionals, opinion threads, 280 chars/tweet
- WeChat Official Account: General tech audience, story-driven articles, 2000-5000 words

### Xiaohongshu Platform Characteristics

**1. Title Formula**:
[Emoji] + [Pain Point/Question] + [Solution] + [Emoji] + [Value Point]

Examples:
- 🦞 Too many OpenClaw skills to choose from? I mastered it in 8 steps! ✨
- 🔥 Must-see for programmers! OpenClaw skill explorer, say goodbye to pitfalls!
- 💡 One day from newbie to publishing first OpenClaw skill!

**2. Content Structure Template**:
- Opening pain point (golden 3 seconds)
- Solution introduction
- Step breakdown + emoji numbering
- Results showcase
- Bonus time
- Interaction guidance

**3. Language Style Conversion**:
- AI Agent → OpenClaw / AI Assistant
- Developer → Babes / Sisters
- Skill Assessment → Skill Selection Tips
- Systematic Process → 8 Steps to Master
- Experience Sharing → Tested and Proven

**4. File Naming Convention**:
```
{date}-{topic}-v{version}-xiaohongshu.md
```

### Multi-Version Management Best Practices

1. First determine base version (v1.0/v2.0) technical blog version
2. Then derive platform version: cp topic-v2.md topic-v2-xiaohongshu.md
3. Rewrite content and style according to Xiaohongshu template
4. Independent iteration: Technical blog version and Xiaohongshu version managed separately

### Quick Conversion Tips

Use sed command for batch term replacement:
```bash
sed -i 's/AI Agent/OpenClaw/g' article-xiaohongshu.md
sed -i 's/Developer/Babes/g' article-xiaohongshu.md
```

---

### Phase 7: Version Management and Iteration

#### Git Workflow

Execute after each file change:
```bash
git add -A
git commit -m "[YYYY-MM-DD] vX.Y: Modification description"
```

#### Version Control Strategy

| Change Type | Version Change | Example |
|---------|---------|------|
| Typos, formatting | No upgrade | Direct overwrite |
| Paragraph optimization | v1.0 → v1.1 | Minor revision |
| Structure adjustment | v1.x → v2.0 | Major revision |

#### Multi-Version Parallel Management

Technical blog version and Xiaohongshu version iterate independently:
```
articles/
├── topic-v2.md              # Technical blog version
├── topic-v2.1.md            # Technical blog version iteration
├── topic-v2-xiaohongshu.md  # Xiaohongshu version
└── topic-v2.1-xiaohongshu.md # Xiaohongshu version iteration
```

---

### Phase 8: Publishing and Promotion

#### Pre-Publishing Checklist

- [ ] Content complete, no typos
- [ ] Code tested
- [ ] Link accessible
- [ ] Git committed

#### Promotion Channels

1. **Tech Communities**: V2EX, Juejin, Zhihu
2. **Social Media**: Twitter, Xiaohongshu, WeChat Official Account
3. **Open Source Platforms**: GitHub, ClawHub

#### Interaction Strategy

- Pose interactive questions at article end
- Reply to comments, build connections
- Collect feedback, continuous iteration

---

*Build with Public - Make Your Technical Growth Visible*