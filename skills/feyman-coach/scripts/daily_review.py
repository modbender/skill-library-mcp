#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
费曼学习法教练 - 每日自动回顾脚本

功能：
1. 根据配置选择需要回顾的笔记
2. 生成费曼学习问题
3. 创建 Obsidian 每日笔记中的回顾任务
4. 发送通知提醒

使用方法：
    python daily_review.py [--config path/to/config.json]

配置说明：
    在项目根目录的 .opencode/config.toml 中添加：

    [feynman-coach]
    enabled = true
    review_time = "09:00"
    days_between_reviews = 1
    review_scope = "recent_notes"  # recent_notes, random, tagged, weak_points
    review_tags = ["#学习", "#重要"]
    max_daily_concepts = 3
    output_format = "obsidian"  # obsidian, markdown, anki
"""

import os
import sys
import json
import random
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional

# 配置默认值
DEFAULT_CONFIG = {
    "enabled": True,
    "review_time": "09:00",
    "days_between_reviews": 1,
    "review_scope": "recent_notes",  # recent_notes, random, tagged, weak_points
    "review_tags": ["#费曼回顾", "#学习"],
    "max_daily_concepts": 3,
    "output_format": "obsidian",
    "history_dir": "Z_Utils/feynman-coach/history",
    "vault_path": ".",  # 相对于脚本的位置
}


class FeynmanCoach:
    """费曼学习法教练核心类"""

    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path)
        self.vault_path = Path(self.config.get("vault_path", "."))
        self.history_dir = Path(
            self.config.get("history_dir", "Z_Utils/feynman-coach/history")
        )
        self.history_dir.mkdir(parents=True, exist_ok=True)

    def _load_config(self, config_path: Optional[str]) -> Dict:
        """加载配置文件"""
        # 首先尝试从 .opencode/config.toml 读取
        opencode_config = Path(".opencode/config.toml")
        if opencode_config.exists():
            try:
                # Python 3.11+ 使用 tomllib，否则使用 tomli
                try:
                    import tomllib
                except ImportError:
                    import tomli as tomllib

                with open(opencode_config, "rb") as f:
                    config = tomllib.load(f)
                    if "feynman-coach" in config:
                        return {**DEFAULT_CONFIG, **config["feynman-coach"]}
            except ImportError:
                print("警告：未安装 toml 解析库，使用默认配置")
                print("提示：运行 'pip install tomli' 以支持 .toml 配置文件")
            except Exception as e:
                print(f"警告：读取 .opencode/config.toml 失败: {e}")

        # 然后尝试从指定路径读取
        if config_path and Path(config_path).exists():
            with open(config_path, "r", encoding="utf-8") as f:
                return {**DEFAULT_CONFIG, **json.load(f)}

        # 使用默认配置
        return DEFAULT_CONFIG.copy()

    def select_notes_for_review(self) -> List[Dict]:
        """根据配置选择需要回顾的笔记"""
        scope = self.config.get("review_scope", "recent_notes")
        max_concepts = self.config.get("max_daily_concepts", 3)

        if scope == "recent_notes":
            return self._get_recent_notes(days=7, limit=max_concepts)
        elif scope == "random":
            return self._get_random_notes(limit=max_concepts)
        elif scope == "tagged":
            tags = self.config.get("review_tags", ["#费曼回顾"])
            return self._get_tagged_notes(tags, limit=max_concepts)
        elif scope == "weak_points":
            return self._get_weak_points_notes(limit=max_concepts)
        else:
            return self._get_recent_notes(days=7, limit=max_concepts)

    def _get_recent_notes(self, days: int = 7, limit: int = 3) -> List[Dict]:
        """获取最近修改的笔记"""
        cutoff_date = datetime.now() - timedelta(days=days)
        notes = []

        # 搜索所有 markdown 文件
        for md_file in self.vault_path.rglob("*.md"):
            try:
                stat = md_file.stat()
                mtime = datetime.fromtimestamp(stat.st_mtime)

                if mtime >= cutoff_date:
                    # 读取文件内容获取标题
                    content = md_file.read_text(encoding="utf-8", errors="ignore")
                    title = self._extract_title(content) or md_file.stem

                    notes.append(
                        {
                            "path": str(md_file.relative_to(self.vault_path)),
                            "title": title,
                            "mtime": mtime.isoformat(),
                            "size": stat.st_size,
                        }
                    )
            except Exception as e:
                print(f"警告：读取文件 {md_file} 失败: {e}")
                continue

        # 按修改时间排序，取最新的
        notes.sort(key=lambda x: x["mtime"], reverse=True)
        return notes[:limit]

    def _get_random_notes(self, limit: int = 3) -> List[Dict]:
        """随机选择笔记"""
        all_notes = []

        for md_file in self.vault_path.rglob("*.md"):
            try:
                content = md_file.read_text(encoding="utf-8", errors="ignore")
                title = self._extract_title(content) or md_file.stem

                all_notes.append(
                    {"path": str(md_file.relative_to(self.vault_path)), "title": title}
                )
            except Exception:
                continue

        if len(all_notes) <= limit:
            return all_notes

        return random.sample(all_notes, limit)

    def _get_tagged_notes(self, tags: List[str], limit: int = 3) -> List[Dict]:
        """获取带特定标签的笔记"""
        tagged_notes = []

        for md_file in self.vault_path.rglob("*.md"):
            try:
                content = md_file.read_text(encoding="utf-8", errors="ignore")

                # 检查是否包含标签
                if any(tag in content for tag in tags):
                    title = self._extract_title(content) or md_file.stem

                    tagged_notes.append(
                        {
                            "path": str(md_file.relative_to(self.vault_path)),
                            "title": title,
                            "tags": [tag for tag in tags if tag in content],
                        }
                    )
            except Exception:
                continue

        # 随机选择
        if len(tagged_notes) <= limit:
            return tagged_notes

        return random.sample(tagged_notes, limit)

    def _get_weak_points_notes(self, limit: int = 3) -> List[Dict]:
        """获取之前诊断出有薄弱点的笔记"""
        weak_notes = []

        # 读取历史记录
        for history_file in self.history_dir.glob("*.json"):
            try:
                with open(history_file, "r", encoding="utf-8") as f:
                    record = json.load(f)

                    # 检查是否有薄弱点
                    if record.get("weak_points") and len(record["weak_points"]) > 0:
                        weak_notes.append(
                            {
                                "path": record.get("note_path", ""),
                                "title": record.get("title", "Unknown"),
                                "weak_points_count": len(record["weak_points"]),
                                "last_review": record.get("timestamp", ""),
                            }
                        )
            except Exception:
                continue

        # 按薄弱点数量排序
        weak_notes.sort(key=lambda x: x["weak_points_count"], reverse=True)
        return weak_notes[:limit]

    def _extract_title(self, content: str) -> Optional[str]:
        """从 markdown 内容中提取标题"""
        lines = content.split("\n")

        # 首先尝试从 YAML frontmatter 中提取
        if lines and lines[0].strip() == "---":
            for i, line in enumerate(lines[1:], 1):
                if line.strip() == "---":
                    break
                if line.startswith("theme:"):
                    return line.split(":", 1)[1].strip()

        # 然后尝试从第一个 # 标题提取
        for line in lines:
            if line.startswith("# "):
                return line[2:].strip()

        return None

    def generate_review_questions(self, note_path: str) -> List[str]:
        """为笔记生成费曼学习问题"""
        try:
            content = (self.vault_path / note_path).read_text(
                encoding="utf-8", errors="ignore"
            )
        except Exception:
            content = ""

        # 基于内容生成问题模板
        questions = [
            f"请用一句话解释 [[{Path(note_path).stem}]] 的核心概念",
            "这个概念与什么生活例子最相似？请用类比说明",
            "如果向一个完全不懂的人解释，你会怎么说？",
            "这个概念的关键组成部分有哪些？",
            "在实际应用中，这个概念如何发挥作用？",
            "这个概念容易与什么混淆？它们的区别是什么？",
            "你能举一个具体的例子来说明吗？",
        ]

        # 根据内容长度调整问题数量
        if len(content) < 500:
            return questions[:3]
        elif len(content) < 1500:
            return questions[:5]
        else:
            return questions

    def create_daily_review_task(self, notes: List[Dict]) -> str:
        """创建每日回顾任务"""
        today = datetime.now().strftime("%Y-%m-%d")
        output_format = self.config.get("output_format", "obsidian")

        if output_format == "obsidian":
            return self._create_obsidian_task(notes, today)
        elif output_format == "markdown":
            return self._create_markdown_task(notes, today)
        else:
            return self._create_obsidian_task(notes, today)

    def _create_obsidian_task(self, notes: List[Dict], date: str) -> str:
        """创建 Obsidian 格式的回顾任务"""
        task_content = f"""---
theme: 费曼学习回顾 - {date}
date: {date}
time: 09:00
tags:
  - Record/费曼回顾
---

# 🧠 费曼学习每日回顾 - {date}

> 💡 **费曼学习法**：如果你不能用简单的语言解释某件事，那你并没有真正理解它。

## 📋 今日回顾清单

"""

        for i, note in enumerate(notes, 1):
            questions = self.generate_review_questions(note["path"])
            question_list = "\n".join(
                [f"   {j + 1}. {q}" for j, q in enumerate(questions)]
            )

            task_content += f"""### {i}. [[{note["title"]}]]

**文件路径**：`{note["path"]}`

**费曼挑战问题**：
{question_list}

**我的解释**：
（在这里写下你的解释...）

**理解自评**：
- [ ] 完全理解，可以清晰解释
- [ ] 基本理解，但有些地方模糊
- [ ] 不太理解，需要重新学习

**薄弱环节记录**：
（AI 诊断后会在这里记录...）

---

"""

        task_content += f"""## 📊 今日学习统计

- **回顾概念数**：{len(notes)}
- **预计用时**：{len(notes) * 15} 分钟
- **完成状态**：
  - [ ] 完成所有回顾
  - [ ] 记录了薄弱环节
  - [ ] 生成了复习卡片

## 🎯 明日建议

（根据今日回顾情况自动生成...）

---

**触发时间**：{datetime.now().strftime("%Y-%m-%d %H:%M")}  
**配置模式**：{self.config.get("review_scope", "recent_notes")}
"""

        return task_content

    def _create_markdown_task(self, notes: List[Dict], date: str) -> str:
        """创建标准 Markdown 格式的回顾任务"""
        # 简化版本，不含 Obsidian 特定语法
        task_content = f"""# 费曼学习回顾 - {date}

## 今日回顾清单

"""

        for i, note in enumerate(notes, 1):
            questions = self.generate_review_questions(note["path"])
            question_list = "\n".join(
                [f"{j + 1}. {q}" for j, q in enumerate(questions)]
            )

            task_content += f"""### {i}. {note["title"]}

**费曼挑战问题**：
{question_list}

---

"""

        return task_content

    def save_review_task(self, content: str, date: str) -> Path:
        """保存回顾任务到文件"""
        # 保存到每日回顾目录
        review_dir = Path("Z_Utils/feynman-coach/daily-reviews")
        review_dir.mkdir(parents=True, exist_ok=True)

        output_file = review_dir / f"review-{date}.md"
        output_file.write_text(content, encoding="utf-8")

        # 同时保存到 Obsidian 日记（如果存在）
        daily_notes_dir = Path("3_flomo卡片笔记")  # 或其他日记目录
        if daily_notes_dir.exists():
            daily_file = daily_notes_dir / f"{date}.md"
            if daily_file.exists():
                # 追加到现有日记
                existing = daily_file.read_text(encoding="utf-8", errors="ignore")
                daily_file.write_text(existing + "\n\n" + content, encoding="utf-8")
            else:
                daily_file.write_text(content, encoding="utf-8")

        return output_file

    def send_notification(self, message: str):
        """发送通知提醒"""
        # Windows
        if sys.platform == "win32":
            try:
                # 尝试使用 win10toast 发送系统通知
                from win10toast import ToastNotifier

                toaster = ToastNotifier()
                toaster.show_toast("费曼教练", message, duration=10)
            except ImportError:
                # 如果没有安装 win10toast，使用 PowerShell 通知
                try:
                    import subprocess

                    subprocess.run(
                        [
                            "powershell",
                            "-Command",
                            f"Add-Type -AssemblyName System.Windows.Forms; "
                            f"[System.Windows.Forms.MessageBox]::Show('{message}', '费曼教练')",
                        ],
                        check=False,
                    )
                except Exception:
                    print(f"[通知] {message}")

        # macOS
        elif sys.platform == "darwin":
            os.system(
                f'osascript -e \'display notification "{message}" with title "费曼教练"\''
            )

        # Linux
        else:
            os.system(f'notify-send "费曼教练" "{message}"')

    def run_daily_review(self):
        """执行每日回顾流程"""
        print("🧠 费曼学习教练 - 每日回顾")
        print("=" * 50)

        # 1. 选择笔记
        print("\n📚 正在选择今日回顾内容...")
        notes = self.select_notes_for_review()

        if not notes:
            print("⚠️ 没有找到合适的笔记进行回顾")
            return

        print(f"✅ 已选择 {len(notes)} 个概念：")
        for note in notes:
            print(f"   - {note['title']}")

        # 2. 生成回顾任务
        print("\n📝 正在生成回顾任务...")
        task_content = self.create_daily_review_task(notes)

        # 3. 保存任务
        today = datetime.now().strftime("%Y-%m-%d")
        output_file = self.save_review_task(task_content, today)
        print(f"✅ 回顾任务已保存到：{output_file}")

        # 4. 发送通知
        self.send_notification(
            f"今日费曼回顾已准备就绪！共 {len(notes)} 个概念等待复习。"
        )

        print("\n✨ 每日回顾任务已生成！")
        print(f"📄 文件位置：{output_file}")
        print(
            "\n💡 提示：使用 Obsidian 打开查看完整任务，或运行 'opencode' 开始交互式回顾。"
        )


def main():
    parser = argparse.ArgumentParser(description="费曼学习法教练 - 每日自动回顾")
    parser.add_argument("--config", "-c", help="配置文件路径")
    parser.add_argument(
        "--dry-run", "-d", action="store_true", help="试运行，不保存文件"
    )
    parser.add_argument(
        "--list", "-l", action="store_true", help="列出最近可回顾的笔记"
    )

    args = parser.parse_args()

    # 初始化教练
    coach = FeynmanCoach(args.config)

    if args.list:
        # 只列出笔记，不生成任务
        print("📚 最近可回顾的笔记：")
        notes = coach.select_notes_for_review()
        for i, note in enumerate(notes, 1):
            print(f"{i}. {note['title']} ({note.get('path', 'N/A')})")
        return

    if args.dry_run:
        print("🔍 试运行模式（不会保存文件）")
        notes = coach.select_notes_for_review()
        print(f"\n将会选择以下 {len(notes)} 个笔记：")
        for note in notes:
            print(f"  - {note['title']}")
        return

    # 执行每日回顾
    coach.run_daily_review()


if __name__ == "__main__":
    main()
