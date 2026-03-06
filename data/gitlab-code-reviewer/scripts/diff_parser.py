"""
Diff Parser Module

Parses GitLab MR changes and extracts file modifications with context.
"""

import re
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum


class ChangeType(Enum):
    ADDED = "added"
    DELETED = "deleted"
    MODIFIED = "modified"
    RENAMED = "renamed"
    COPIED = "copied"


@dataclass
class DiffLine:
    """Represents a single line in a diff."""
    line_number_old: Optional[int]
    line_number_new: Optional[int]
    content: str
    is_addition: bool
    is_deletion: bool


@dataclass
class FileChange:
    """Represents changes to a single file."""
    old_path: str
    new_path: str
    change_type: ChangeType
    diff: str
    lines: List[DiffLine] = field(default_factory=list)
    additions: int = 0
    deletions: int = 0
    hunks: List[Dict] = field(default_factory=list)

    @property
    def path(self) -> str:
        return self.new_path if self.new_path else self.old_path

    @property
    def extension(self) -> str:
        """Get file extension without the dot."""
        path = self.path
        if "." in path:
            return path.rsplit(".", 1)[-1].lower()
        return ""


@dataclass
class ParsedDiff:
    """Complete parsed diff result."""
    files: List[FileChange] = field(default_factory=list)
    total_additions: int = 0
    total_deletions: int = 0
    merge_request_info: Optional[Dict] = None

    @property
    def total_changes(self) -> int:
        return self.total_additions + self.total_deletions

    def get_files_by_extension(self, extension: str) -> List[FileChange]:
        """Filter files by extension."""
        return [f for f in self.files if f.extension == extension.lower()]

    def get_files_by_pattern(self, pattern: str) -> List[FileChange]:
        """Filter files by glob pattern."""
        import fnmatch
        return [f for f in self.files if fnmatch.fnmatch(f.path, pattern)]


class DiffParser:
    """
    Parses unified diff format from GitLab API.
    """

    # Regex patterns for parsing diffs
    DIFF_HEADER_PATTERN = re.compile(
        r'^diff --git (?P<old_path>"?[^\s"]+)"? (?P<new_path>"?[^\s"]+)"?$'
    )
    INDEX_PATTERN = re.compile(r'^index [a-f0-9]+\.\.[a-f0-9]+')
    OLD_FILE_PATTERN = re.compile(r'^--- (?P<path>[^\t]+)(?:\t(?P<old_info>.*))?$')
    NEW_FILE_PATTERN = re.compile(r'^\+\+\+ (?P<path>[^\t]+)(?:\t(?P<new_info>.*))?$')
    HUNK_PATTERN = re.compile(
        r'^@@ -(?P<old_start>\d+)(?:,(?P<old_count>\d+))? \+(?P<new_start>\d+)(?:,(?P<new_count>\d+))? @@(?: (?P<hunk_header>.*))?$'
    )
    ADDITION_PATTERN = re.compile(r'^\+(?!\+\+)')
    DELETION_PATTERN = re.compile(r'^-(?!--)')
    CONTEXT_PATTERN = re.compile(r'^[^+-]')
    SIMILARITY_PATTERN = re.compile(r'^similarity index (\d+)%')
    RENAME_FROM_PATTERN = re.compile(r'^rename from (.+)')
    RENAME_TO_PATTERN = re.compile(r'^rename to (.+)')

    def __init__(self, ignore_patterns: Optional[List[str]] = None):
        """
        Initialize parser with optional ignore patterns.

        Args:
            ignore_patterns: List of glob patterns to ignore (e.g., ["*.lock", "forms/*.json"])
        """
        self.ignore_patterns = ignore_patterns or []
        # Default ignores
        self.default_ignores = [
            "*.min.js",
            "*.min.css",
            "package-lock.json",
            "yarn.lock",
            "*.lock",
            "pnpm-lock.yaml",
            "forms/*.json",
        ]

    def parse(self, diff_text: str, include_ignored: bool = False) -> ParsedDiff:
        """
        Parse unified diff text into structured format.

        Args:
            diff_text: Raw diff text from GitLab API
            include_ignored: If True, include files matching ignore patterns

        Returns:
            ParsedDiff object with all file changes
        """
        result = ParsedDiff()
        lines = diff_text.split('\n')
        current_file: Optional[FileChange] = None
        current_hunk: Optional[Dict] = None
        old_line_num = 0
        new_line_num = 0

        i = 0
        while i < len(lines):
            line = lines[i]

            # Check for new file diff
            if line.startswith('diff --git'):
                if current_file:
                    result.files.append(current_file)
                    result.total_additions += current_file.additions
                    result.total_deletions += current_file.deletions

                current_file = self._parse_diff_header(lines, i)
                old_line_num = 0
                new_line_num = 0
                i += 1
                continue

            if not current_file:
                i += 1
                continue

            # Parse hunk header
            hunk_match = self.HUNK_PATTERN.match(line)
            if hunk_match:
                current_hunk = {
                    'old_start': int(hunk_match.group('old_start')),
                    'old_count': int(hunk_match.group('old_count') or 1),
                    'new_start': int(hunk_match.group('new_start')),
                    'new_count': int(hunk_match.group('new_count') or 1),
                    'header': hunk_match.group('hunk_header') or '',
                }
                current_file.hunks.append(current_hunk)
                old_line_num = current_hunk['old_start']
                new_line_num = current_hunk['new_start']
                i += 1
                continue

            # Parse diff content lines
            if current_hunk:
                diff_line = self._parse_diff_line(line, old_line_num, new_line_num)
                if diff_line:
                    current_file.lines.append(diff_line)

                    if diff_line.is_addition:
                        current_file.additions += 1
                        new_line_num += 1
                    elif diff_line.is_deletion:
                        current_file.deletions += 1
                        old_line_num += 1
                    else:
                        old_line_num += 1
                        new_line_num += 1

            i += 1

        # Don't forget the last file
        if current_file:
            result.files.append(current_file)
            result.total_additions += current_file.additions
            result.total_deletions += current_file.deletions

        # Filter ignored files
        if not include_ignored:
            result.files = self._filter_ignored_files(result.files)

        return result

    def _parse_diff_header(self, lines: List[str], start_idx: int) -> FileChange:
        """Parse the header of a diff section to extract file paths and change type."""
        old_path = None
        new_path = None
        change_type = ChangeType.MODIFIED
        diff_lines = [lines[start_idx]]

        i = start_idx + 1
        while i < len(lines):
            line = lines[i]
            if line.startswith('diff --git'):
                break
            diff_lines.append(line)

            # Check for file paths
            if line.startswith('--- '):
                match = self.OLD_FILE_PATTERN.match(line)
                if match:
                    path = match.group('path')
                    if path != '/dev/null':
                        old_path = self._clean_path(path)
                    else:
                        change_type = ChangeType.ADDED

            elif line.startswith('+++ '):
                match = self.NEW_FILE_PATTERN.match(line)
                if match:
                    path = match.group('path')
                    if path != '/dev/null':
                        new_path = self._clean_path(path)
                    else:
                        change_type = ChangeType.DELETED

            # Check for rename
            elif line.startswith('rename from '):
                match = self.RENAME_FROM_PATTERN.match(line)
                if match:
                    old_path = match.group(1)
                    change_type = ChangeType.RENAMED

            elif line.startswith('rename to '):
                match = self.RENAME_TO_PATTERN.match(line)
                if match:
                    new_path = match.group(1)
                    change_type = ChangeType.RENAMED

            # Check for similarity (rename/copy detection)
            elif line.startswith('similarity index'):
                match = self.SIMILARITY_PATTERN.match(line)
                if match:
                    similarity = int(match.group(1))
                    if similarity < 100 and change_type == ChangeType.MODIFIED:
                        # Likely a rename
                        change_type = ChangeType.RENAMED

            i += 1

        return FileChange(
            old_path=old_path or '',
            new_path=new_path or '',
            change_type=change_type,
            diff='\n'.join(diff_lines),
        )

    def _parse_diff_line(
        self, line: str, old_line_num: int, new_line_num: int
    ) -> Optional[DiffLine]:
        """Parse a single diff content line."""
        if not line:
            return None

        is_addition = self.ADDITION_PATTERN.match(line) is not None
        is_deletion = self.DELETION_PATTERN.match(line) is not None
        is_context = self.CONTEXT_PATTERN.match(line) is not None

        if not (is_addition or is_deletion or is_context):
            return None

        content = line[1:] if (is_addition or is_deletion) else line

        return DiffLine(
            line_number_old=old_line_num if not is_addition else None,
            line_number_new=new_line_num if not is_deletion else None,
            content=content,
            is_addition=is_addition,
            is_deletion=is_deletion,
        )

    def _clean_path(self, path: str) -> str:
        """Clean path by removing quotes and a/ b/ prefixes."""
        path = path.strip('"')
        if path.startswith('a/') or path.startswith('b/'):
            path = path[2:]
        return path

    def _filter_ignored_files(self, files: List[FileChange]) -> List[FileChange]:
        """Filter out files matching ignore patterns."""
        import fnmatch

        all_patterns = self.default_ignores + self.ignore_patterns

        filtered = []
        for f in files:
            ignored = False
            for pattern in all_patterns:
                if fnmatch.fnmatch(f.path, pattern):
                    ignored = True
                    break
                # Also check old path for renames
                if f.old_path and fnmatch.fnmatch(f.old_path, pattern):
                    ignored = True
                    break
            if not ignored:
                filtered.append(f)

        return filtered

    def parse_from_gitlab_response(self, response_data: Dict) -> ParsedDiff:
        """
        Parse GitLab API response for MR changes.

        Args:
            response_data: JSON response from GitLab MR changes endpoint

        Returns:
            ParsedDiff object
        """
        result = ParsedDiff()

        # Store merge request info
        result.merge_request_info = {
            'id': response_data.get('id'),
            'iid': response_data.get('iid'),
            'project_id': response_data.get('project_id'),
            'title': response_data.get('title'),
            'source_branch': response_data.get('source_branch'),
            'target_branch': response_data.get('target_branch'),
        }

        # Parse each file's diff
        for file_diff in response_data.get('changes', []):
            old_path = file_diff.get('old_path', '')
            new_path = file_diff.get('new_path', '')
            diff_text = file_diff.get('diff', '')

            # Determine change type
            change_type_str = file_diff.get('change_type', 'changed')
            change_type_map = {
                'new': ChangeType.ADDED,
                'deleted': ChangeType.DELETED,
                'renamed': ChangeType.RENAMED,
                'changed': ChangeType.MODIFIED,
                'moved': ChangeType.RENAMED,
            }
            change_type = change_type_map.get(change_type_str, ChangeType.MODIFIED)

            # Parse the diff
            file_change = FileChange(
                old_path=old_path,
                new_path=new_path,
                change_type=change_type,
                diff=diff_text,
                additions=file_diff.get('new_lines', 0),
                deletions=file_diff.get('deleted_lines', 0),
            )

            # Parse individual lines from diff
            self._parse_diff_content(file_change)

            result.files.append(file_change)
            result.total_additions += file_change.additions
            result.total_deletions += file_change.deletions

        # Filter ignored files
        result.files = self._filter_ignored_files(result.files)

        return result

    def _parse_diff_content(self, file_change: FileChange) -> None:
        """Parse diff content into structured lines."""
        lines = file_change.diff.split('\n')
        old_line_num = 0
        new_line_num = 0
        current_hunk = None

        for line in lines:
            # Skip diff metadata
            if line.startswith('diff --git') or line.startswith('index ') or \
               line.startswith('--- ') or line.startswith('+++ ') or \
               line.startswith('@@ ') is False and line.startswith('@@'):
                continue

            # Parse hunk header
            hunk_match = self.HUNK_PATTERN.match(line)
            if hunk_match:
                current_hunk = {
                    'old_start': int(hunk_match.group('old_start')),
                    'old_count': int(hunk_match.group('old_count') or 1),
                    'new_start': int(hunk_match.group('new_start')),
                    'new_count': int(hunk_match.group('new_count') or 1),
                    'header': hunk_match.group('hunk_header') or '',
                }
                file_change.hunks.append(current_hunk)
                old_line_num = current_hunk['old_start']
                new_line_num = current_hunk['new_start']
                continue

            if current_hunk:
                diff_line = self._parse_diff_line(line, old_line_num, new_line_num)
                if diff_line:
                    file_change.lines.append(diff_line)

                    if diff_line.is_addition:
                        new_line_num += 1
                    elif diff_line.is_deletion:
                        old_line_num += 1
                    else:
                        old_line_num += 1
                        new_line_num += 1


def load_diff_from_file(file_path: str) -> str:
    """Load diff text from a JSON or text file."""
    import json

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Try to parse as JSON (GitLab API response)
    try:
        data = json.loads(content)
        if 'changes' in data:
            # GitLab API response format
            return content
        elif 'diff' in data:
            # Single file diff
            return data['diff']
    except json.JSONDecodeError:
        pass

    return content
