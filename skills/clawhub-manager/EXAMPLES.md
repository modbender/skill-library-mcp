# ClawHub 管理技能使用示例

## 查询技能信息

```bash
# 查看技能基本信息
bash /root/.openclaw/workspace/skills/clawhub-manager/scripts/inspect.sh feishu-voice

# 查看 JSON 格式的详细信息（便于脚本处理）
bash /root/.openclaw/workspace/skills/clawhub-manager/scripts/inspect.sh feishu-voice --json
```

## 搜索技能

```bash
# 搜索包含 "feishu" 的技能
bash /root/.openclaw/workspace/skills/clawhub-manager/scripts/search.sh feishu

# 搜索并限制结果数量
bash /root/.openclaw/workspace/skills/clawhub-manager/scripts/search.sh pdf --limit 20
```

## 列出本地技能

```bash
# 列出所有已安装的技能
bash /root/.openclaw/workspace/skills/clawhub-manager/scripts/list.sh
```

## 发布技能

```bash
# 基本发布
bash /root/.openclaw/workspace/skills/clawhub-manager/scripts/publish.sh \
  /root/.openclaw/workspace/skills/my-skill \
  --version 1.0.0

# 带更新日志的发布
bash /root/.openclaw/workspace/skills/clawhub-manager/scripts/publish.sh \
  /root/.openclaw/workspace/skills/my-skill \
  --version 1.0.1 \
  --changelog "修复了若干 bug，添加了新功能"

# 自定义 slug 和名称
bash /root/.openclaw/workspace/skills/clawhub-manager/scripts/publish.sh \
  /root/.openclaw/workspace/skills/my-skill \
  --slug my-custom-slug \
  --name "My Custom Skill Name" \
  --version 1.0.0
```

## 删除技能

```bash
# 删除技能（需要确认）
bash /root/.openclaw/workspace/skills/clawhub-manager/scripts/delete.sh my-skill
```

## 实际使用场景

### 场景 1: 批量查询多个技能的统计信息

```bash
#!/bin/bash
# 查询多个技能的下载量

SKILLS=("feishu-voice" "zhipu-tts" "zhipu-asr")

for skill in "${SKILLS[@]}"; do
  echo "=== $skill ==="
  bash /root/.openclaw/workspace/skills/clawhub-manager/scripts/inspect.sh "$skill" --json | jq '{downloads, installs}'
  echo ""
done
```

### 场景 2: 搜索并筛选技能

```bash
# 搜索 PDF 相关技能
bash /root/.openclaw/workspace/skills/clawhub-manager/scripts/search.sh pdf

# 查看最相关的技能详情
bash /root/.openclaw/workspace/skills/clawhub-manager/scripts/inspect.sh markdown-to-pdf-weasyprint
```

### 场景 3: 发布新技能的完整流程

```bash
# 1. 检查技能目录
ls -la /root/.openclaw/workspace/skills/my-new-skill/

# 2. 列出本地技能确认
bash /root/.openclaw/workspace/skills/clawhub-manager/scripts/list.sh

# 3. 发布技能
bash /root/.openclaw/workspace/skills/clawhub-manager/scripts/publish.sh \
  /root/.openclaw/workspace/skills/my-new-skill \
  --version 1.0.0 \
  --changelog "🎉 首次发布"

# 4. 验证发布（等待几分钟后）
sleep 60
bash /root/.openclaw/workspace/skills/clawhub-manager/scripts/inspect.sh my-new-skill
```

### 场景 4: 重新发布技能

```bash
# 1. 删除旧技能
bash /root/.openclaw/workspace/skills/clawhub-manager/scripts/delete.sh old-slug

# 2. 用新 slug 重新发布
bash /root/.openclaw/workspace/skills/clawhub-manager/scripts/publish.sh \
  /root/.openclaw/workspace/skills/my-skill \
  --slug new-slug \
  --name "New Skill Name" \
  --version 1.0.0 \
  --changelog "🔄 重新发布：使用更简洁的 slug"
```

## 注意事项

1. **删除操作不可逆** - 删除技能前请确认
2. **slug 命名规范** - 只能包含小写字母、数字和连字符
3. **版本号规范** - 遵循语义化版本（如 1.0.0）
4. **权限要求** - 删除技能需要管理员/审核员权限
5. **速率限制** - 大量操作时注意 API 速率限制
