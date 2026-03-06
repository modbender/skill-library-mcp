---
name: dev-task
description: 开发项目任务管理，支持版本化开发流程。当用户需要启动开发任务、创建新版本、管理项目版本文档时使用。每次启动开发任务必须向用户确认版本编号，按版本号管理代码、开发文档、需求文档、发布配置。严格执行版本归档纪律，封版必须立即归档完整代码和文档。
---

# 开发任务管理 Skill

本 Skill 用于规范化的项目版本管理和开发任务流程。

---

## ⚠️ 版本管理纪律（强制执行）

### 铁律
> **每个版本封版后必须立即归档完整代码和文档！**
> **严禁在没有存档的情况下开始新版本号的开发！**

### 违规后果
- **v1.X 代码永久丢失** — 未归档即开始 v1.X+1 开发
- 无法回滚到中间版本
- 版本历史断档

### 必须归档的内容
| 类别 | 必须文件 | 说明 |
|------|---------|------|
| **代码** | `src/` 目录 | 封版时的完整代码快照 |
| **变更** | `docs/CHANGELOG.md` | 功能列表、Bug修复、已知问题 |
| **需求** | `docs/REQUIREMENTS.md` | 需求规格、功能清单 |
| **运维** | `docs/DEPLOY.md` | 部署步骤、回滚方案、监控方法 |

---

## 项目版本结构规范

```
project-name/
├── [当前开发文件]              # 正在开发的代码
└── versions/                   # ★版本归档目录（不可跳过）
    ├── README.md              # 版本管理说明、当前版本
    ├── v1.0/                  # v1.0 版本（完整归档）
    │   ├── docs/
    │   │   ├── CHANGELOG.md   # 变更日志
    │   │   ├── REQUIREMENTS.md # 需求文档
    │   │   └── DEPLOY.md      # 部署文档
    │   ├── src/               # ★完整代码备份
    │   └── release/           # 发布包（可选）
    ├── v1.1/                  # v1.1 版本（完整归档）
    └── v1.2/                  # v1.2 版本（完整归档）
```

---

## 开发任务启动流程

### Step 1: 确认版本编号（必须）

**必须**向用户确认版本号，格式为 `v主版本.次版本.修订号`：

> "请确认本次开发任务的版本编号（例如：v1.1.0）："

**版本号规则：**
- **主版本号 (X.0.0)**: 重大功能变更、架构调整
- **次版本号 (0.X.0)**: 新增功能、向下兼容  
- **修订号 (0.0.X)**: Bug 修复、小优化

**检查规则：**
- 如果 versions/vX.Y.Z 已存在 → 询问继续开发还是换新版本
- 如果当前开发目录有未归档代码 → **必须先封版上一个版本！**

### Step 2: 检查上一个版本是否已归档

```bash
# 检查最新版本
ls -la versions/ | tail -5

# 如果上一个版本未完成归档，必须提醒用户：
# "⚠️ 警告：上一个版本 vX.Y.Z 尚未封版归档！"
# "必须先完成 vX.Y.Z 的归档，才能开始新版本开发。"
```

### Step 3: 创建新版本目录结构

```bash
# 创建目录
mkdir -p versions/vX.Y.Z/{docs,src,release}

# 初始化文档
cp references/CHANGELOG.template.md versions/vX.Y.Z/docs/CHANGELOG.md
cp references/REQUIREMENTS.template.md versions/vX.Y.Z/docs/REQUIREMENTS.md
cp references/DEPLOY.template.md versions/vX.Y.Z/docs/DEPLOY.md

# 替换版本号占位符
sed -i 's/vX.Y.Z/vX.Y.Z/g' versions/vX.Y.Z/docs/*.md
```

### Step 4: 更新 REQUIREMENTS.md

根据用户描述，填写本次开发的需求：
- 功能需求清单
- 技术规格
- 约束条件

### Step 5: 开始开发

在当前目录进行开发工作。

---

## 版本封版流程（★关键步骤）

### 何时封版
- 功能开发完成
- 测试通过
- 准备部署或发布

### 封版检查清单

**必须完成以下所有项，缺一不可：**

- [ ] **CHANGELOG.md** 已更新
  - [ ] 新增功能列表
  - [ ] Bug 修复记录
  - [ ] 已知问题说明
  - [ ] 部署日期

- [ ] **REQUIREMENTS.md** 已更新
  - [ ] 需求完成情况
  - [ ] 功能清单核对

- [ ] **DEPLOY.md** 已更新
  - [ ] 部署步骤
  - [ ] 环境要求
  - [ ] 回滚方案

- [ ] **代码已归档**
  ```bash
  cp -r client versions/vX.Y.Z/src/
  cp -r server versions/vX.Y.Z/src/
  cp package.json versions/vX.Y.Z/src/
  cp [其他必要文件] versions/vX.Y.Z/src/
  ```

- [ ] **versions/README.md** 已更新
  - 当前版本信息
  - 版本历史记录

### 封版命令

```bash
#!/bin/bash
VERSION=$1  # 传入版本号，如 v1.1.0

echo "=== 版本封版: $VERSION ==="

# 1. 验证文档存在
for doc in CHANGELOG REQUIREMENTS DEPLOY; do
    if [ ! -f "versions/$VERSION/docs/${doc}.md" ]; then
        echo "❌ 错误: ${doc}.md 不存在！"
        exit 1
    fi
done

# 2. 归档代码
echo "归档代码..."
cp -r client versions/$VERSION/src/
cp -r server versions/$VERSION/src/
cp package.json versions/$VERSION/src/ 2>/dev/null || true

# 3. 验证归档
if [ -d "versions/$VERSION/src/client" ] && [ -d "versions/$VERSION/src/server" ]; then
    echo "✅ 版本 $VERSION 封版完成！"
else
    echo "❌ 归档失败！"
    exit 1
fi
```

---

## 版本回滚

```bash
VERSION=$1  # 目标版本

echo "回滚到 $VERSION..."

# 1. 停止服务
pm2 stop [服务名]

# 2. 验证版本存在
if [ ! -d "versions/$VERSION/src" ]; then
    echo "❌ 版本 $VERSION 代码不存在！"
    exit 1
fi

# 3. 恢复代码
cp -r versions/$VERSION/src/* ./

# 4. 重新安装依赖
npm install

# 5. 启动服务
pm2 start [服务名]

echo "✅ 已回滚到 $VERSION"
```

---

## 参考模板

文档模板位于 `references/doc-templates/`：

| 模板文件 | 用途 | 输出位置 |
|---------|------|---------|
| `CHANGELOG.template.md` | 变更日志 | `docs/CHANGELOG.md` |
| `REQUIREMENTS.template.md` | 需求文档 | `docs/REQUIREMENTS.md` |
| `DEPLOY.template.md` | 部署说明 | `docs/DEPLOY.md` |

---

## 违规处理

如果发现以下情况，必须立即纠正：

| 违规情况 | 处理方式 |
|---------|---------|
| 未归档即开始新版本 | **立即停止**，先完成上一个版本归档 |
| 缺少 CHANGELOG.md | 补充编写，记录变更 |
| 缺少 REQUIREMENTS.md | 补充编写，明确需求 |
| 缺少 DEPLOY.md | 补充编写，确保可部署 |
| src/ 目录为空或不完整 | 重新归档完整代码 |

---

## CSS/样式调试检查清单

**遇到样式不生效时，按此顺序排查：**

### Step 1: 确认选择器匹配（最常见错误！）
```
✅ 检查 HTML 中元素的 id/class 是否与 CSS 选择器一致
   - id: chatInput vs #chat-input （命名不匹配！）
   - class: my-class vs .myClass （大小写敏感！）
✅ 用 DevTools Elements 面板确认元素的实际属性
```

### Step 2: 确认文件加载
```
✅ Network 面板 → CSS 文件状态 200
✅ 文件名和路径是否正确（大小写敏感！）
```

### Step 3: 确认样式应用
```
✅ DevTools Computed 面板 → 查看实际生效的样式
✅ Styles 面板 → 查看哪些规则被划掉（特异性问题）
✅ 检查是否有更高优先级的规则覆盖
```

### Step 4: 复杂问题排查
```
✅ 浏览器默认样式 → 用 !important 或 appearance: none
✅ JS 动态修改 → 检查脚本是否修改了样式
✅ CSS 变量未定义 → 检查 var(--xxx) 是否有值
```

### 黄金法则
> **90% 的 CSS 问题是基础错误（选择器不匹配、文件未加载），只有 10% 是复杂的优先级/兼容性问题。先查基础，再查复杂。**

### 经验教训归档
- 参考 `workspace/lessons/CSS_DEBUG_LESSON.md`
- 每次遇到典型问题，更新此文档

---

## 一句话总结

> **封版必归档，文档不能少，跳过是违规！**
> **CSS 调试先查选择器，90% 问题都是命名不匹配！**
