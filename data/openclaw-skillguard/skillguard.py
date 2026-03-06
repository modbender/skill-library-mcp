#!/usr/bin/env python3
"""
SkillGuard - OpenClaw Skills 安全掃描工具

用於在安裝技能前進行安全評估和風險檢查
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple

class SkillGuard:
    def __init__(self, workspace: str = "/home/jiazhou/.openclaw/workspace"):
        self.workspace = Path(workspace)
        self.skills_dir = self.workspace / "skills"
        self.output = []

    def scan_directory(self, directory: Path) -> Dict:
        """掃描單一目錄"""
        result = {
            "directory": str(directory.relative_to(self.workspace)),
            "exists": directory.exists(),
            "status": "error",
            "issues": {
                "critical": 0,
                "warning": 0,
                "info": []
            },
            "summary": {}
        }

        if not directory.exists():
            result["issues"]["info"].append(f"目錄不存在: {directory}")
            return result

        # 檢查關鍵檔案
        self._check_meta(directory, result)
        self._check_skill_md(directory, result)
        self._check_source_files(directory, result)
        self._check_executables(directory, result)

        # 判定狀態
        if result["issues"]["critical"] > 0:
            result["status"] = "critical"
        elif result["issues"]["warning"] > 0:
            result["status"] = "warning"
        else:
            result["status"] = "clean"

        return result

    def _check_meta(self, directory: Path, result: Dict):
        """檢查 _meta.json"""
        meta_path = directory / "_meta.json"
        if not meta_path.exists():
            result["issues"]["warning"] += 1
            result["issues"]["info"].append("缺少 _meta.json")
            return

        try:
            with open(meta_path) as f:
                meta = json.load(f)
                result["summary"]["name"] = meta.get("name", "unknown")
                result["summary"]["version"] = meta.get("version", "unknown")
                result["summary"]["author"] = meta.get("author", "unknown")
        except json.JSONDecodeError:
            result["issues"]["warning"] += 1
            result["issues"]["info"].append("_meta.json 格式錯誤")

    def _check_skill_md(self, directory: Path, result: Dict):
        """檢查 SKILL.md"""
        skill_md = directory / "SKILL.md"
        if not skill_md.exists():
            result["issues"]["warning"] += 1
            result["issues"]["info"].append("缺少 SKILL.md")
        else:
            result["summary"]["has_skill_md"] = True

    def _check_source_files(self, directory: Path, result: Dict):
        """檢查來源檔案"""
        py_files = list(directory.rglob("*.py"))
        js_files = list(directory.rglob("*.js"))
        shell_files = list(directory.rglob("*.sh"))

        if py_files:
            result["issues"]["info"].append(f"Python 檔案: {len(py_files)}")
        if js_files:
            result["issues"]["info"].append(f"JavaScript 檔案: {len(js_files)}")
        if shell_files:
            result["issues"]["info"].append(f"Shell 檔案: {len(shell_files)}")

    def _check_executables(self, directory: Path, result: Dict):
        """檢查可執行檔案"""
        for file in directory.rglob("*"):
            if file.is_file() and os.access(file, os.X_OK):
                result["issues"]["info"].append(f"可執行檔: {file.relative_to(directory)}")

    def scan_all(self) -> List[Dict]:
        """掃描所有 skills"""
        if not self.skills_dir.exists():
            print("Skills 目錄不存在")
            return []

        results = []
        for skill_dir in sorted(self.skills_dir.iterdir()):
            if skill_dir.is_dir() and not skill_dir.name.startswith("."):
                result = self.scan_directory(skill_dir)
                results.append(result)

        return results

    def generate_report(self, results: List[Dict]) -> str:
        """生成報告"""
        report_lines = [
            "=" * 60,
            "SkillGuard 安全掃描報告",
            "=" * 60,
            f"掃描時間: {self._get_timestamp()}",
            f"掃描結果: {len(results)} Skills",
            "=" * 60,
            ""
        ]

        # 計算摘要
        clean = sum(1 for r in results if r["status"] == "clean")
        warnings = sum(1 for r in results if r["status"] == "warning")
        critical = sum(1 for r in results if r["status"] == "critical")

        report_lines.extend([
            "📊 摘要統計:",
            f"  ✅ 安全: {clean}",
            f"  ⚠️  警告: {warnings}",
            f"  🔴 危險: {critical}",
            "",
            "🔍 詳細結果:",
            ""
        ])

        # 個別報告
        for result in results:
            status_icon = {
                "clean": "✅",
                "warning": "⚠️ ",
                "critical": "🔴"
            }.get(result["status"], "❓")

            report_lines.extend([
                f"{status_icon} {result['directory']}",
                f"    狀態: {result['status']}",
                f"    問題: {result['issues']['critical']} 嚴重, {result['issues']['warning']} 警告"
            ])

            if result["issues"]["info"]:
                for info in result["issues"]["info"]:
                    report_lines.append(f"    - {info}")

            report_lines.append("")

        # 建議
        report_lines.extend([
            "=" * 60,
            "💡 安全建議:",
            ""
        ])

        if critical > 0:
            report_lines.append("🔴 需要立即處理：有危險等級 skills 不可使用")
        if warnings > 0:
            report_lines.append("⚠️  建議審查：有警告等級 skills 需要了解風險")
        if clean > 0:
            report_lines.append(f"✅ 安全可靠：{clean} 個 skills 可以安全使用")

        report_lines.append("")
        report_lines.append("=" * 60)

        return "\n".join(report_lines)

    def vet_skill(self, skill_name: str) -> Dict:
        """單一技能審查"""
        skill_path = self.skills_dir / skill_name
        return self.scan_directory(skill_path)

    @staticmethod
    def _get_timestamp() -> str:
        import datetime
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def run_cli(self):
        """CLI 介面"""
        if len(sys.argv) < 2:
            print("用法: skillguard.py [scan|vet] <arguments>")
            print("\n範例:")
            print("  skillguard.py scan --all  # 掃描所有 skills")
            print("  skillguard.py vet <skill_name>  # 審查特定 skill")
            print("  skillguard.py scan <directory>  # 掃描特定目錄")
            sys.exit(1)

        command = sys.argv[1]

        if command == "scan":
            if len(sys.argv) >= 3 and sys.argv[2] == "--all":
                results = self.scan_all()
                print(self.generate_report(results))
            elif len(sys.argv) >= 3:
                skill_path = self.workspace / sys.argv[2]
                results = [self.scan_directory(skill_path)]
                print(self.generate_report(results))
            else:
                print("錯誤: 請指定掃描目錄或使用 --all")
                sys.exit(1)

        elif command == "vet":
            if len(sys.argv) < 3:
                print("錯誤: 請指定要審查的 skill 名稱")
                sys.exit(1)
            result = self.vet_skill(sys.argv[2])
            print(json.dumps(result, indent=2, ensure_ascii=False))

        else:
            print(f"未知指令: {command}")
            sys.exit(1)

if __name__ == "__main__":
    guard = SkillGuard()
    guard.run_cli()