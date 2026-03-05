#!/usr/bin/env python3
"""
init_guide.py — 项目文档结构初始化脚本

为项目创建标准化的 guide 文档体系（start.md + guide/ 目录）。

用法:
    python3 init_guide.py --project-name "项目名" --type game --root /path/to/project
    python3 init_guide.py --project-name "我的Web应用" --type web --root . --force
"""

import argparse
import os
import sys
from datetime import datetime

# ============================================================
# 项目类型配置
# ============================================================

PROJECT_TYPES = {
    "game": {
        "emoji": "🎮",
        "02": {"slug": "map", "emoji": "🗺️", "name": "地图设计", "desc": "场景布局、地标、配色方案"},
        "03": {"slug": "npc", "emoji": "👥", "name": "NPC/实体设计", "desc": "角色设定、AI行为、日程表"},
        "04": {"slug": "attributes", "emoji": "📊", "name": "属性系统", "desc": "属性定义、数值平衡、效果公式"},
        "05": {"slug": "ai", "emoji": "🤖", "name": "AI系统", "desc": "Prompt设计、LLM集成、决策逻辑"},
        "start_cmd": "# 直接双击 index.html 即可运行\nopen index.html",
    },
    "web": {
        "emoji": "🌐",
        "02": {"slug": "routes", "emoji": "🔗", "name": "路由设计", "desc": "URL结构、权限、中间件"},
        "03": {"slug": "components", "emoji": "🧩", "name": "组件设计", "desc": "组件树、Props、状态流"},
        "04": {"slug": "state", "emoji": "📦", "name": "状态管理", "desc": "Store设计、Action/Mutation"},
        "05": {"slug": "api", "emoji": "📡", "name": "API设计", "desc": "端点列表、请求/响应格式"},
        "start_cmd": "npm install\nnpm run dev",
    },
    "cli": {
        "emoji": "⌨️",
        "02": {"slug": "commands", "emoji": "📋", "name": "命令设计", "desc": "子命令、参数、选项"},
        "03": {"slug": "modules", "emoji": "🔧", "name": "核心模块", "desc": "模块职责、接口、依赖"},
        "04": {"slug": "models", "emoji": "📐", "name": "数据模型", "desc": "结构定义、序列化、验证"},
        "05": {"slug": "algorithms", "emoji": "🧮", "name": "算法/逻辑", "desc": "核心算法、流程、复杂度"},
        "start_cmd": "pip install -e .\n# 或\npython main.py --help",
    },
    "lib": {
        "emoji": "📚",
        "02": {"slug": "commands", "emoji": "📋", "name": "命令/接口", "desc": "公开API、参数、选项"},
        "03": {"slug": "modules", "emoji": "🔧", "name": "核心模块", "desc": "模块职责、接口、依赖"},
        "04": {"slug": "models", "emoji": "📐", "name": "数据模型", "desc": "结构定义、序列化、验证"},
        "05": {"slug": "algorithms", "emoji": "🧮", "name": "算法/逻辑", "desc": "核心算法、流程、复杂度"},
        "start_cmd": "pip install -e .\npython -c \"import mylib; print(mylib.__version__)\"",
    },
    "general": {
        "emoji": "📦",
        "02": {"slug": "architecture", "emoji": "🏗️", "name": "架构设计", "desc": "分层、模块划分、通信机制"},
        "03": {"slug": "modules", "emoji": "🔧", "name": "核心模块", "desc": "模块职责、接口、依赖"},
        "04": {"slug": "models", "emoji": "📐", "name": "数据模型", "desc": "实体定义、关系、存储"},
        "05": {"slug": "logic", "emoji": "🧠", "name": "核心逻辑", "desc": "业务规则、流程、算法"},
        "start_cmd": "# 请替换为实际启动命令",
    },
}

# ============================================================
# 模板生成函数
# ============================================================

def gen_start_md(name, ptype):
    """生成 start.md 内容"""
    cfg = PROJECT_TYPES[ptype]
    return f"""# {cfg['emoji']} {name} — 启动说明

## 网页地址

<!-- 填写服务/访问地址，如 http://localhost:8080 -->

## 启动服务

```bash
{cfg['start_cmd']}
```

## 关闭服务

```bash
# 请填写关闭命令
```

## 快速重启

```bash
# 请填写重启命令
```

## 项目文件说明

| 文件 | 说明 |
|------|------|
| <!-- 请逐行添加项目文件 --> | |
"""


def gen_guide_md(name, ptype):
    """生成 guide/guide.md 内容"""
    cfg = PROJECT_TYPES[ptype]
    today = datetime.now().strftime("%Y-%m-%d")

    # 构建文档索引表
    index_rows = f"| [01-design.md](01-design.md) | 🎯 设计理念 | 项目定位、设计决策 |\n"
    for num in ["02", "03", "04", "05"]:
        d = cfg[num]
        index_rows += f"| [{num}-{d['slug']}.md]({num}-{d['slug']}.md) | {d['emoji']} {d['name']} | {d['desc']} |\n"
    index_rows += "| [06-tech.md](06-tech.md) | ⚙️ 技术架构 | 文件结构、核心类/模块 |\n"
    index_rows += "| [07-plan.md](07-plan.md) | 📅 开发计划 | 分期计划、Checklist |\n"
    index_rows += "| [08-changelog.md](08-changelog.md) | 📝 更新日志 | 版本历史、Bug修复 |\n"
    index_rows += "| [09-pitfalls.md](09-pitfalls.md) | 🚧 踩坑记录 | 经验教训、通用原则 |"

    return f"""# {cfg['emoji']} {name} — 项目总览

> **技术路线**: <!-- 请填写 -->
> **核心目标**: <!-- 请填写 -->
> **当前版本**: v0.1

---

## 📋 文档索引

| 文档 | 内容 | 说明 |
|------|------|------|
{index_rows}

---

## 🚀 快速开始

```bash
{cfg['start_cmd']}
```

## 🏗️ 当前核心系统

```mermaid
graph LR
    A[模块A] --> B[模块B]
    B --> C[模块C]
```

<!-- 请替换为实际架构图 -->
"""


def gen_design_md():
    """生成 01-design.md 内容"""
    return """# 设计理念 & 项目定位

## 1. 设计理念

### 1.1 为什么做这个项目？

<!-- 项目的起源、灵感、要解决的问题 -->

### 1.2 核心设计原则

<!-- 项目遵循的设计原则（3-5条） -->

---

## 2. 与同类项目的关系

<!-- 如有参考项目，说明差异和复用策略 -->
"""


def gen_domain_md(num, slug, emoji, name, desc):
    """生成 02~05 领域文档内容"""
    return f"""# {emoji} {name}

> {desc}

---

<!-- 请根据项目实际内容填充此文档 -->
"""


def gen_tech_md(name):
    """生成 06-tech.md 内容"""
    return f"""# 技术架构

## 文件结构

```
project-root/
├── ...
└── ...
```

<!-- 请填写实际文件结构 -->

## 核心类/模块设计

<!-- 请列出核心类/模块的签名和功能描述 -->

## 数据流

```
用户操作 → ... → 数据层
```

<!-- 请描述实际数据流 -->
"""


def gen_plan_md():
    """生成 07-plan.md 内容"""
    return """# 开发计划

## 当前阶段：Phase 1 — 基础骨架

### 分期计划

| 阶段 | 内容 | 状态 |
|------|------|------|
| Phase 1 | 基础骨架 | 🔧 进行中 |
| Phase 2 | 核心功能 | ⏳ 待开始 |
| Phase 3 | 优化完善 | ⏳ 待开始 |

### 下一步 TODO

- [ ] 待办1
- [ ] 待办2
"""


def gen_changelog_md(name):
    """生成 08-changelog.md 内容"""
    today = datetime.now().strftime("%Y-%m-%d")
    return f"""# 📝 更新日志

> 详细记录每个版本的改动、Bug 修复和新功能。

---

## v0.1 — 项目初始化 ({today})

### 🎉 初始版本
- 项目骨架搭建
- guide 文档体系创建

### 📝 代码改动
- 创建项目基础文件

---

## 当前已实现功能 Checklist

- [x] 项目初始化
- [x] guide 文档体系
- [ ] <!-- 下一个功能 -->
"""


def gen_pitfalls_md():
    """生成 09-pitfalls.md 内容"""
    return """# 🚧 踩坑记录 & 开发注意事项

> 这是项目开发过程中积累的经验教训，都是实际遇到的坑。后续开发时务必参考此文档，避免重蹈覆辙。

---

<!-- 按以下格式添加踩坑记录：

## 🔥 坑1：简短标题

### 问题现象
具体描述遇到的问题。

### 问题根因
代码/架构层面的原因分析。

### 解决方案
具体修复步骤。

### ⚠️ 开发注意
- **加粗的通用原则**
- 后续注意事项

-->

---

## 📋 通用开发原则（从以上踩坑总结）

<!-- 从踩坑记录中提炼的通用原则，格式：
### 1. 原则标题
原则描述。
-->
"""


# ============================================================
# 主逻辑
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="初始化项目 guide 文档体系",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python3 init_guide.py --project-name "福音雪镇" --type game --root /path/to/project
  python3 init_guide.py --project-name "MyWebApp" --type web --root . --force
        """,
    )
    parser.add_argument("--project-name", required=True, help="项目名称")
    parser.add_argument(
        "--type",
        required=True,
        choices=["game", "web", "cli", "lib", "general"],
        help="项目类型",
    )
    parser.add_argument("--root", default=".", help="项目根目录（默认当前目录）")
    parser.add_argument("--force", action="store_true", help="强制覆盖已有文件")

    args = parser.parse_args()
    root = os.path.abspath(args.root)
    name = args.project_name
    ptype = args.type
    cfg = PROJECT_TYPES[ptype]

    # 检查是否已有文档
    start_path = os.path.join(root, "start.md")
    guide_dir = os.path.join(root, "guide")

    if not args.force:
        existing = []
        if os.path.exists(start_path):
            existing.append("start.md")
        if os.path.exists(guide_dir):
            existing.append("guide/")
        if existing:
            print(f"⚠️  目标目录已有: {', '.join(existing)}")
            confirm = input("是否覆盖？(y/N): ").strip().lower()
            if confirm != "y":
                print("已取消。使用 --force 跳过确认。")
                sys.exit(0)

    # 创建目录
    os.makedirs(guide_dir, exist_ok=True)

    # 生成文件列表
    files = {}

    # start.md
    files[start_path] = gen_start_md(name, ptype)

    # guide/guide.md
    files[os.path.join(guide_dir, "guide.md")] = gen_guide_md(name, ptype)

    # 01-design.md
    files[os.path.join(guide_dir, "01-design.md")] = gen_design_md()

    # 02~05 领域文档
    for num in ["02", "03", "04", "05"]:
        d = cfg[num]
        filename = f"{num}-{d['slug']}.md"
        files[os.path.join(guide_dir, filename)] = gen_domain_md(
            num, d["slug"], d["emoji"], d["name"], d["desc"]
        )

    # 06-tech.md
    files[os.path.join(guide_dir, "06-tech.md")] = gen_tech_md(name)

    # 07-plan.md
    files[os.path.join(guide_dir, "07-plan.md")] = gen_plan_md()

    # 08-changelog.md
    files[os.path.join(guide_dir, "08-changelog.md")] = gen_changelog_md(name)

    # 09-pitfalls.md
    files[os.path.join(guide_dir, "09-pitfalls.md")] = gen_pitfalls_md()

    # 写入文件
    created = []
    for path, content in files.items():
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        rel = os.path.relpath(path, root)
        created.append(rel)

    # 输出摘要
    print(f"\n✅ 项目文档初始化完成！")
    print(f"   项目名: {name}")
    print(f"   类型:   {ptype}")
    print(f"   根目录: {root}")
    print(f"\n📁 创建了 {len(created)} 个文件:")
    for f in sorted(created):
        print(f"   · {f}")
    print(f"\n下一步:")
    print(f"   1. 编辑 start.md — 填写启动命令和文件清单")
    print(f"   2. 编辑 guide/guide.md — 填写元信息和架构图")
    print(f"   3. 编辑 guide/01-design.md — 写下设计理念")


if __name__ == "__main__":
    main()
