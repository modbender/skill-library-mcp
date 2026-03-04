---
name: marila-skill-publish
description: 马锐拉的 ClawHub 技能发布流程与经验总结。包含完整的技能发布步骤、元数据规范、常见问题解决方案。
version: 1.0.0
metadata:
  openclaw:
    requires:
      bins:
        - clawhub
        - git
    homepage: https://github.com/aliramw/dingtalk-ai-table
---

# ClawHub 技能发布流程

本文档总结了从 0 到发布一个 ClawHub 技能的完整流程和经验。

## 📋 前置要求

- Node.js >= 18
- `clawhub` CLI (`npm install -g clawhub`)
- Git
- ClawHub 账号（已登录）

## 🚀 完整流程

### 1. 准备技能文件夹

```bash
# 创建技能目录
mkdir -p ~/my-skill
cd ~/my-skill

# 初始化 Git
git init
```

### 2. 创建必需文件

#### SKILL.md（必需）

```markdown
---
name: my-skill
description: 简短描述技能功能
version: 1.0.0
metadata:
  openclaw:
    requires:
      env:
        - MY_API_KEY
      bins:
        - curl
    primaryEnv: MY_API_KEY
    homepage: https://github.com/username/my-skill
---

# 技能说明文档

## 功能描述
...

## 使用方法
...
```

**⚠️ 关键：元数据必须准确声明**

ClawHub 安全分析会检查声明与实际代码是否一致：
- `requires.env` - 代码中引用的所有环境变量
- `requires.bins` - 代码中调用的所有 CLI 工具
- `primaryEnv` - 主要凭证变量名

#### package.json

```json
{
  "name": "my-skill",
  "version": "1.0.0",
  "description": "技能描述",
  "repository": {
    "type": "git",
    "url": "https://github.com/username/my-skill.git"
  },
  "clawhub": {
    "requiresBinaries": ["curl"],
    "credentials": [
      {
        "name": "MY_API_KEY",
        "description": "API 密钥说明",
        "docs": "https://example.com/docs"
      }
    ]
  }
}
```

#### README.md

```markdown
# my-skill

简短介绍。

## 安装

```bash
clawhub install my-skill
```

## 配置

1. 获取凭证...
2. 配置环境变量...

## 使用

...
```

#### CHANGELOG.md

```markdown
# Changelog

## [1.0.0] - 2026-02-27

### 新增
- 初始版本
```

### 3. 推送到 GitHub

```bash
git add -A
git commit -m "Initial commit"
git remote add origin https://github.com/username/my-skill.git
git push -u origin main
```

### 4. 发布到 ClawHub

```bash
# 方式一：直接发布
clawhub publish . --slug my-skill --name "My Skill" --version 1.0.0 --changelog "初始版本"

# 方式二：使用 sync（推荐）
clawhub sync
```

### 5. 验证发布

```bash
# 检查技能信息
clawhub inspect my-skill

# 查看网页
open https://clawhub.ai/username/my-skill
```

## ⚠️ 常见问题与解决方案

### 问题 1: `fetch failed` 错误

**症状：**
```
✖ fetch failed
Error: fetch failed
```

**原因：** SSL 证书验证失败或网络问题

**解决：**
```bash
# 临时方案
export NODE_TLS_REJECT_UNAUTHORIZED=0

# 或检查网络连接
curl -I https://clawhub.ai
```

### 问题 2: `SKILL.md required` 错误

**症状：**
```
Error: SKILL.md required
```

**原因：**
- 文件不存在
- 文件名大小写错误（必须是 `SKILL.md` 或 `skill.md`）
- 当前目录错误

**解决：**
```bash
ls -la SKILL.md
pwd
clawhub publish /absolute/path/to/skill --slug my-skill ...
```

### 问题 3: 发布超时（Timeout）

**症状：**
```
✖ Timeout
Error: Timeout
```

**原因：** 服务器响应慢或网络问题

**解决：**
```bash
# 检查服务器状态
curl -I https://clawhub.ai

# 重试发布
clawhub publish . --slug my-skill ...

# 或使用 sync
clawhub sync
```

### 问题 4: 元数据不一致（审核失败）

**症状：** 审核反馈 "metadata mismatch"

**原因：** SKILL.md frontmatter 声明与实际代码不符

**解决：** 确保 frontmatter 准确声明：

```yaml
---
name: my-skill
version: 1.0.0
metadata:
  openclaw:
    requires:
      env:
        - ACTUAL_ENV_VAR_USED_IN_CODE
      bins:
        - actual_binary_used_in_code
    primaryEnv: ACTUAL_ENV_VAR_USED_IN_CODE
    homepage: https://github.com/username/repo
---
```

### 问题 5: 登录失败

**症状：**
```
- Verifying token
✖ fetch failed
```

**解决：**
```bash
# 检查 token 文件
cat ~/.clawhub/config.json

# 重新登录
clawhub login

# 或手动设置 token
clawhub auth login
```

## 📝 版本更新流程

```bash
# 1. 更新版本号
# 修改 SKILL.md frontmatter 中的 version
# 修改 package.json 中的 version

# 2. 更新 CHANGELOG.md
# 在顶部添加新版本记录

# 3. 提交并推送
git add -A
git commit -m "chore: bump version to 1.0.1"
git push

# 4. 发布新版本
clawhub publish . --slug my-skill --version 1.0.1 --changelog "修复 xxx"

# 或使用 sync
clawhub sync
```

## 🔐 安全注意事项

1. **凭证安全**
   - 不要在代码中硬编码密钥
   - 使用环境变量或 `mcporter config` 存储
   - 在 `.gitignore` 中排除敏感文件

2. **脚本审查**
   - 如果包含脚本文件，建议在文档中说明需要审查
   - 建议用户先在测试环境验证

3. **元数据准确性**
   - 准确声明所有依赖的环境变量和二进制文件
   - 这有助于安全分析和用户理解

## 📚 参考资源

- ClawHub 文档：https://clawhub.ai/docs
- 技能格式规范：https://github.com/openclaw/clawhub/blob/main/docs/skill-format.md
- 安全规范：https://github.com/openclaw/clawhub/blob/main/docs/security.md
- ClawHub 技能市场：https://clawhub.ai/skills

## 💡 最佳实践

1. **小步迭代** - 每次发布只做一个主要改动
2. **详细 Changelog** - 清晰记录每个版本的变更
3. **测试先行** - 在发布前充分测试技能功能
4. **文档完善** - 好的文档减少用户问题
5. **语义化版本** - 遵循 semver (major.minor.patch)

---

*最后更新：2026-02-27*
*作者：马锐拉 (@aliramw)*
