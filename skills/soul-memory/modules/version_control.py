#!/usr/bin/env python3
"""
Soul Memory Module D: Version Control
Git integration for memory versioning

Features:
- Automatic commits on memory changes
- Diff viewing
- Version rollback

Author: Soul Memory System
Date: 2026-02-17
"""

import os
import subprocess
import json
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
from datetime import datetime


@dataclass
class CommitInfo:
    """Git commit information"""
    hash: str
    message: str
    date: str
    author: str


class VersionControl:
    """
    Version Control System
    
    Git-based version control for memory files.
    """
    
    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)
        self.versions_file = self.repo_path / "versions.json"
    
    def _run_git(self, *args) -> Tuple[bool, str]:
        """Run git command"""
        try:
            result = subprocess.run(
                ['git'] + list(args),
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.returncode == 0, result.stdout + result.stderr
        except Exception as e:
            return False, str(e)
    
    def is_git_repo(self) -> bool:
        """Check if directory is a git repo"""
        git_dir = self.repo_path / '.git'
        return git_dir.exists()
    
    def init_repo(self) -> Tuple[bool, str]:
        """Initialize git repository"""
        if self.is_git_repo():
            return True, "Repository already initialized"
        
        success, output = self._run_git('init')
        if success:
            return True, "Repository initialized"
        return False, output
    
    def commit(self, message: str, files: Optional[List[str]] = None) -> Tuple[bool, str]:
        """Create a commit"""
        if not self.is_git_repo():
            ok, msg = self.init_repo()
            if not ok:
                return False, msg
        
        # Add files
        if files:
            for f in files:
                self._run_git('add', f)
        else:
            self._run_git('add', '.')
        
        # Commit
        success, output = self._run_git('commit', '-m', message)
        return success, output
    
    def get_log(self, max_count: int = 10) -> List[CommitInfo]:
        """Get commit log"""
        if not self.is_git_repo():
            return []
        
        success, output = self._run_git(
            'log', f'--max-count={max_count}',
            '--pretty=format:%H|%s|%ai|%an'
        )
        
        if not success:
            return []
        
        commits = []
        for line in output.strip().split('\n'):
            if '|' in line:
                parts = line.split('|')
                if len(parts) >= 4:
                    commits.append(CommitInfo(
                        hash=parts[0][:8],
                        message=parts[1],
                        date=parts[2],
                        author=parts[3]
                    ))
        
        return commits
    
    def get_diff(self, commit1: str, commit2: str = 'HEAD') -> str:
        """Get diff between commits"""
        success, output = self._run_git('diff', commit1, commit2)
        return output if success else ""
    
    def rollback(self, commit_hash: str) -> Tuple[bool, str]:
        """Rollback to a specific commit"""
        success, output = self._run_git('reset', '--hard', commit_hash)
        return success, output
    
    def save_version(self, version_name: str, description: str = ""):
        """Save a version marker"""
        versions = {}
        if self.versions_file.exists():
            with open(self.versions_file, 'r', encoding='utf-8') as f:
                versions = json.load(f)
        
        success, output = self._run_git('rev-parse', 'HEAD')
        commit_hash = output.strip()[:8] if success else "unknown"
        
        versions[version_name] = {
            'commit': commit_hash,
            'date': datetime.now().isoformat(),
            'description': description
        }
        
        with open(self.versions_file, 'w', encoding='utf-8') as f:
            json.dump(versions, f, ensure_ascii=False, indent=2)
    
    def list_versions(self) -> Dict:
        """List all saved versions"""
        if self.versions_file.exists():
            with open(self.versions_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}


if __name__ == "__main__":
    # Test
    vc = VersionControl(".")
    
    if vc.is_git_repo():
        print("Git repository found")
        log = vc.get_log(5)
        for commit in log:
            print(f"  {commit.hash} {commit.message[:40]}")
    else:
        print("Not a git repository")
