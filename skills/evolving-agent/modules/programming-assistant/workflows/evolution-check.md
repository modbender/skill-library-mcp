# Evolution Check - 进化检查

**必须**在每个开发/修复循环结束后执行。

---

## ⚠️ 重要：知识归纳格式

```
❌ 错误方式（多行文本会返回空结果）:
cat << 'EOF' | python ... knowledge summarize --auto-store
问题1：xxx
问题2：xxx
EOF

✅ 正确方式（每条经验单独存储）:
echo "问题：xxx → 解决：yyy" | python ... knowledge summarize --auto-store
echo "问题：aaa → 解决：bbb" | python ... knowledge summarize --auto-store
```

**原则**: 一条命令存储一条经验，格式为 `问题：xxx → 解决：yyy`

---

## 激活进化模式条件

| 场景                | 激活 |
| ------------------- | ---- |
| 修复失败2次后成功   | ✅ |
| 用户说"记住这个"    | ✅ |
| 发现更优方案        | ✅ |
| 特定环境 workaround | ✅ |
| 简单修改一行代码    | ❌ |
| 用户说"很好"、"ok"  | ❌ |

---

## 检查流程

```
步骤1: 检测任务复杂度
    读取 .opencode/feature_list.json 检查任务数
    ├─ 任务数 > 10 或 会话轮数 > 50 → 需要压缩
    └─ 简单任务 → 直接归纳

步骤2: 会话压缩（如需要）
    执行 /compact 命令压缩会话历史
    保留关键决策、问题解决方案、技术栈选择等

步骤3: 激活进化模式
    根据激活条件判断：
    ├─ 满足条件：执行 python $SKILLS_DIR/evolving-agent/scripts/run.py mode --init
    └─ 不满足：直接返回

步骤4: 知识归纳
    从以下内容提取经验：
    - .opencode/progress.txt 的"遇到的问题"和"关键决策"
    - 会话中的关键发现
    ⚠️ 每条经验单独存储，不要批量存储！
```

---

## 存储命令

```bash
# 设置路径变量（每个 shell 会话执行一次）
SKILLS_DIR=$([ -d ~/.config/opencode/skills/evolving-agent ] && echo ~/.config/opencode/skills || echo ~/.claude/skills)

# ⚠️ 每条经验单独存储
echo "问题：xxx → 解决：yyy" | python $SKILLS_DIR/evolving-agent/scripts/run.py knowledge summarize --auto-store
```

---

## 示例

### 示例1: 单个问题修复

```bash
# 修复跨域问题后存储经验
echo "问题：Vite项目跨域报错 → 解决：配置 server.proxy" | \
  python $SKILLS_DIR/evolving-agent/scripts/run.py knowledge summarize --auto-store
```

### 示例2: 多个问题（分开存储）

```bash
# ⚠️ 每条经验单独一行命令
echo "问题：bcrypt 编译报错 → 解决：使用 @node-rs/bcrypt 替代" | \
  python $SKILLS_DIR/evolving-agent/scripts/run.py knowledge summarize --auto-store

echo "问题：JWT 中间件顺序错误 → 解决：需要在路由之前注册" | \
  python $SKILLS_DIR/evolving-agent/scripts/run.py knowledge summarize --auto-store

echo "决策：选择 bcrypt 而非 argon2，因为 bcrypt 更成熟" | \
  python $SKILLS_DIR/evolving-agent/scripts/run.py knowledge summarize --auto-store
```

### 示例3: 快速存储偏好

```bash
echo "偏好：Node.js 项目统一使用 pnpm 作为包管理器" | \
  python $SKILLS_DIR/evolving-agent/scripts/run.py knowledge summarize --auto-store
```

---

## 注意事项

- **单条存储**: 每条经验单独一个 `echo | python` 命令，不要批量
- **格式规范**: 使用 `问题：xxx → 解决：yyy` 或 `决策：xxx` 格式
- **去重机制**: 知识库会自动去重相似条目
- **静默模式**: 只在存储成功后简短通知，不阻塞主流程
