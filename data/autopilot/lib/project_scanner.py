#!/usr/bin/env python3
"""
Layer 2: Project Scanner
- 扫描项目文件系统
- 统计里程碑完成度
"""

import os
from dataclasses import dataclass
from glob import glob
from typing import Dict, List, Optional


@dataclass
class MilestoneProgress:
    name: str
    total_files: int
    existing_files: int
    
    @property
    def percentage(self) -> int:
        if self.total_files == 0:
            return 100
        return int((self.existing_files / self.total_files) * 100)
    
    @property
    def is_complete(self) -> bool:
        return self.existing_files >= self.total_files


@dataclass
class ProjectProgress:
    project_dir: str
    milestones: List[MilestoneProgress]
    
    @property
    def overall_percentage(self) -> int:
        if not self.milestones:
            return 0
        total = sum(m.total_files for m in self.milestones)
        existing = sum(m.existing_files for m in self.milestones)
        if total == 0:
            return 100
        return int((existing / total) * 100)


def scan_project_progress(project_dir: str, 
                          milestones: Optional[Dict[str, List[str]]] = None) -> ProjectProgress:
    """
    扫描项目文件系统，统计里程碑完成度
    
    Args:
        project_dir: 项目根目录
        milestones: 里程碑定义 {名称: [文件路径/glob 模式]}
                   如果为 None，使用默认检测逻辑
    
    Returns:
        ProjectProgress 对象
    """
    if milestones is None:
        milestones = _detect_default_milestones(project_dir)
    
    milestone_progress = []
    
    for name, patterns in milestones.items():
        total = len(patterns)
        existing = 0
        
        for pattern in patterns:
            full_pattern = os.path.join(project_dir, pattern)
            
            if '*' in pattern or '?' in pattern:
                # Glob 模式
                matches = glob(full_pattern, recursive=True)
                if matches:
                    existing += 1
            else:
                # 具体文件路径
                if os.path.exists(full_pattern):
                    existing += 1
        
        milestone_progress.append(MilestoneProgress(
            name=name,
            total_files=total,
            existing_files=existing
        ))
    
    return ProjectProgress(
        project_dir=project_dir,
        milestones=milestone_progress
    )


def _detect_default_milestones(project_dir: str) -> Dict[str, List[str]]:
    """
    根据项目类型检测默认的里程碑
    """
    milestones = {}
    
    # 检测项目类型
    has_package_json = os.path.exists(os.path.join(project_dir, "package.json"))
    has_cargo_toml = os.path.exists(os.path.join(project_dir, "Cargo.toml"))
    has_pyproject = os.path.exists(os.path.join(project_dir, "pyproject.toml"))
    has_requirements = os.path.exists(os.path.join(project_dir, "requirements.txt"))
    
    if has_package_json:
        # Node.js / Next.js / React 项目
        milestones["M1-Init"] = [
            "package.json",
            "tsconfig.json",
        ]
        milestones["M2-Core"] = [
            "src/**/*.ts",
            "src/**/*.tsx",
        ]
        milestones["M3-Tests"] = [
            "**/*.test.ts",
            "**/*.test.tsx",
            "**/*.spec.ts",
        ]
    elif has_cargo_toml:
        # Rust 项目
        milestones["M1-Init"] = [
            "Cargo.toml",
            "Cargo.lock",
        ]
        milestones["M2-Core"] = [
            "src/**/*.rs",
        ]
    elif has_pyproject or has_requirements:
        # Python 项目
        milestones["M1-Init"] = [
            "pyproject.toml" if has_pyproject else "requirements.txt",
        ]
        milestones["M2-Core"] = [
            "**/*.py",
        ]
        milestones["M3-Tests"] = [
            "tests/**/*.py",
            "test_*.py",
        ]
    else:
        # 未知项目类型
        milestones["M1-Files"] = [
            "*",
        ]
    
    return milestones


def format_progress(progress: ProjectProgress) -> str:
    """
    格式化进度输出
    
    格式: "M1[OK] > M2[75%] > M3[0%]"
    """
    parts = []
    
    for m in progress.milestones:
        if m.is_complete:
            parts.append(f"{m.name}[OK]")
        else:
            parts.append(f"{m.name}[{m.percentage}%]")
    
    return " > ".join(parts)


def get_current_milestone(progress: ProjectProgress) -> Optional[str]:
    """获取当前正在进行的里程碑名称"""
    for m in progress.milestones:
        if not m.is_complete:
            return m.name
    return None  # 所有里程碑都完成了


def get_remaining_work(progress: ProjectProgress) -> str:
    """获取剩余工作描述"""
    remaining = []
    for m in progress.milestones:
        if not m.is_complete:
            remaining.append(f"{m.name}({m.percentage}%)")
    
    if not remaining:
        return "无"
    
    return ", ".join(remaining)
