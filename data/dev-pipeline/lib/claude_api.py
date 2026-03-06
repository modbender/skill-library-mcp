"""
Claude Opus 4.6 API 调用模块
"""

import requests
from pathlib import Path


class ClaudeAPI:
    """调用 Claude Opus 4.6 进行架构分析、代码编写和代码审查"""
    
    BASE_URL = "https://xh.v1api.cc/v1"
    API_KEY = "sk-ZGawDWk0YPZCDEJ7vvzC8rQuipmXhvg8YfqfqHcWjnqZNAuV"
    MODEL = "claude-opus-4-6"
    
    def __init__(self):
        self.headers = {
            "Authorization": f"Bearer {self.API_KEY}",
            "Content-Type": "application/json"
        }
    
    def _call(self, messages, max_tokens=8192, temperature=0.7):
        """调用 API"""
        payload = {
            "model": self.MODEL,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": False
        }
        
        response = requests.post(
            f"{self.BASE_URL}/chat/completions",
            headers=self.headers,
            json=payload,
            timeout=360
        )
        response.raise_for_status()
        
        result = response.json()
        return result["choices"][0]["message"]["content"]
    
    def analyze_project(self, requirements, project_files):
        """
        架构分析
        
        Args:
            requirements: 需求文档内容
            project_files: 项目文件列表 [{"path": ..., "content": ...}]
        
        Returns:
            开发计划文档 (Markdown)
        """
        # 构建项目上下文
        context = "\n\n".join([
            f"=== 文件: {f['path']} ===\n{f['content'][:2000]}"
            for f in project_files[:10]
        ])
        
        system_prompt = """你是一位资深架构师，负责分析项目需求并输出详细的开发计划。

你的任务：
1. 理解业务需求，进行技术解读
2. 分析现有项目结构和代码
3. 设计技术方案（架构、模块、接口）
4. 拆解开发任务（必须包含任务ID、名称、优先级、依赖、输出文件）
5. 评估技术风险和缓解措施

【输出格式要求】
必须按以下结构输出 Markdown：

# 项目开发方案

## 1. 需求理解
- 业务目标
- 核心业务流程
- 关键技术特性

## 2. 技术架构
- 整体架构图（ASCII）
- 技术选型表格
- 目录结构设计

## 3. 数据库设计
- 完整的 SQL 建表语句
- 索引设计

## 4. API 接口设计
- 每个接口的 Method/Path
- Request/Response 格式

## 5. 任务清单（关键！）

### 阶段一：基础设施（P0）
| 任务ID | 任务名称 | 优先级 | 依赖 | 预估工时 | 输出文件 |
|--------|---------|--------|------|---------|----------|
| T001 | 项目初始化 | P0 | 无 | 2h | package.json, .gitignore |
| T002 | 数据库模块 | P0 | T001 | 3h | shared/db.js |

## 6. 风险评估
- 技术风险表格
- 缓解措施

## 7. 工时评估
- 按阶段汇总
- 按优先级汇总"""

        user_prompt = f"""请根据以下需求和项目上下文，输出完整的开发计划：

## 需求文档

{requirements}

## 项目上下文

{context}

请严格按照系统提示中的格式要求输出开发方案。"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        return self._call(messages, max_tokens=16384, temperature=0.6)
    
    def write_code(self, task, dev_plan, project_files, review_feedback=None):
        """
        编写代码 - 严格按照 FILE: 格式输出
        
        Args:
            task: 任务信息 {"id": ..., "name": ..., ...}
            dev_plan: 开发计划内容
            project_files: 项目文件列表
            review_feedback: 审查反馈（修复模式时使用）
        
        Returns:
            生成的代码（按 FILE: 格式组织）
        """
        context = "\n\n".join([
            f"=== 文件: {f['path']} ===\n{f['content'][:3000]}"
            for f in project_files[:5]
        ])
        
        mode = "修复代码" if review_feedback else "编写代码"
        
        system_prompt = f"""你是一位资深开发工程师，负责{mode}。

## 📁 文件输出格式（必须严格遵守）

对于每个需要创建的文件，必须按以下格式输出：

### FILE: [相对路径]
**操作类型**: [create | overwrite | append]
**描述**: [该文件的用途说明]

```[语言]
[完整的文件代码内容]
```

---

### 示例输出：

### FILE: package.json
**操作类型**: create
**描述**: Node.js 项目配置文件

```json
{{
  "name": "my-project",
  "version": "1.0.0",
  "dependencies": {{
    "express": "^4.18.0"
  }}
}}
```

---

### FILE: src/server.js
**操作类型**: create
**描述**: Express 服务器入口

```javascript
const express = require('express');
const app = express();

app.listen(3000, () => {{
  console.log('Server running on port 3000');
}});
```

---

## ⚠️ 格式规则

1. **每个文件必须以 `### FILE: 路径` 开头**
2. **操作类型必须明确**：
   - `create` - 新建文件（文件不存在）
   - `overwrite` - 覆盖文件（文件已存在，需要替换）
   - `append` - 追加内容（在文件末尾添加）
3. **代码块必须完整**：包含所有必要的导入、配置、实现
4. **路径使用相对路径**：相对于项目根目录
5. **不要省略任何文件**：任务要求的所有文件都必须输出
6. **用 --- 分隔多个文件**

## 💡 代码质量要求

1. 代码质量高，可读性强
2. 遵循项目现有代码风格
3. 包含适当的错误处理
4. 添加必要的注释
5. 确保代码可以运行"""

        if review_feedback:
            user_prompt = f"""请根据以下审查反馈修复代码：

## 任务

[{task['id']}] {task['name']}

## 开发计划（相关部分）

{dev_plan[:5000]}

## 项目上下文

{context}

## 审查反馈

{review_feedback}

请输出修复后的完整代码，严格使用 FILE: 格式。"""
        else:
            user_prompt = f"""请根据以下任务和开发计划编写代码：

## 任务

[{task['id']}] {task['name']}

## 开发计划（相关部分）

{dev_plan[:5000]}

## 项目上下文

{context}

请输出完整的实现代码，严格使用 FILE: 格式。

必须包含任务要求的所有文件，每个文件都要有：
1. ### FILE: 路径
2. **操作类型**: create/overwrite/append
3. **描述**: 文件用途
4. 代码块"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        return self._call(messages, max_tokens=16384, temperature=0.4)
    
    def review_code(self, task, code_files, dev_plan):
        """
        审查代码 - 严格按照审查报告格式输出
        
        Args:
            task: 任务信息
            code_files: 代码文件列表 [{"path": ..., "content": ...}]
            dev_plan: 开发计划内容
        
        Returns:
            审查报告 (Markdown)
        """
        code = "\n\n".join([
            f"=== 文件: {f['path']} ===\n```\n{f['content'][:5000]}\n```"
            for f in code_files[:5]
        ])
        
        system_prompt = """你是一位资深代码审查员，负责审查代码质量。

## 📋 审查报告格式（必须严格遵守）

```markdown
# 代码审查报告

## 基本信息
| 项目 | 内容 |
|------|------|
| 任务编号 | [TASK_ID] |
| 任务名称 | [TASK_NAME] |
| 审查日期 | [日期] |

## 审查发现

### 🔴 严重问题（必须修复）
1. **[问题类型]** [问题描述]
   - **位置**: [文件路径]:[行号]
   - **影响**: [影响描述]
   - **修复建议**: [具体建议]

### 🟡 警告（建议修复）
1. **[问题类型]** [问题描述]
   - **位置**: [文件路径]:[行号]
   - **建议**: [改进建议]

### 🟢 建议（可选优化）
1. **[问题类型]** [问题描述]
   - **建议**: [优化建议]

## 代码质量评分

| 维度 | 评分 | 说明 |
|------|------|------|
| 功能完整性 | [0-10] | |
| 代码规范 | [0-10] | |
| 安全性 | [0-10] | |
| 性能 | [0-10] | |
| 可维护性 | [0-10] | |
| **总分** | **[0-10]** | |

## 审查结论

[✅ 通过 / ❌ 不通过]

**原因**:
[详细说明]

**下一步行动**:
- 如果通过：进入下一阶段
- 如果不通过：执行修复
```

## ⚠️ 评分规则

- 总分 >= 7.0：✅ 通过
- 总分 < 7.0 或有 🔴 严重问题：❌ 不通过

## 🔍 审查维度

1. 代码质量（可读性、可维护性）
2. 安全性（注入、XSS、敏感信息）
3. 性能（算法复杂度、资源使用）
4. 逻辑正确性（边界情况、错误处理）
5. 是否符合开发计划"""

        user_prompt = f"""请审查以下代码：

## 任务

[{task['id']}] {task['name']}

## 开发计划（相关部分）

{dev_plan[:3000]}

## 代码

{code}

请严格按照系统提示中的审查报告格式输出，最后明确给出审查结论（通过/不通过）。"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        return self._call(messages, max_tokens=12288, temperature=0.3)
