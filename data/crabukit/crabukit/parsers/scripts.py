"""Parser for discovering and loading script files."""

from pathlib import Path
from dataclasses import dataclass
from typing import List, Optional
import ast


@dataclass
class ScriptFile:
    """A discovered script file."""
    path: Path
    relative_path: str
    content: str
    language: str  # 'python', 'bash', 'unknown'
    ast_tree: Optional[ast.AST] = None


class ScriptParser:
    """Discover and parse script files in a skill."""
    
    PYTHON_EXTENSIONS = {'.py'}
    BASH_EXTENSIONS = {'.sh', '.bash'}
    SHELL_INTERPRETERS = {'sh', 'bash', 'zsh', 'fish'}
    
    def __init__(self, skill_path: Path):
        self.skill_path = Path(skill_path)
        self.scripts_dir = self.skill_path / "scripts"
        
    def discover_scripts(self) -> List[ScriptFile]:
        """Find all script files in the skill."""
        scripts = []
        
        if not self.scripts_dir.exists():
            return scripts
        
        for file_path in self.scripts_dir.rglob("*"):
            if not file_path.is_file():
                continue
                
            # Skip hidden files
            if file_path.name.startswith('.'):
                continue
            
            script = self._parse_file(file_path)
            if script:
                scripts.append(script)
        
        return scripts
    
    def _parse_file(self, file_path: Path) -> Optional[ScriptFile]:
        """Parse a single file."""
        try:
            content = file_path.read_text()
        except (IOError, UnicodeDecodeError):
            return None
        
        # Detect language
        language = self._detect_language(file_path, content)
        
        # Parse AST for Python files
        ast_tree = None
        if language == 'python':
            try:
                ast_tree = ast.parse(content)
            except SyntaxError:
                pass  # Invalid Python, still analyze as text
        
        relative_path = str(file_path.relative_to(self.skill_path))
        
        return ScriptFile(
            path=file_path,
            relative_path=relative_path,
            content=content,
            language=language,
            ast_tree=ast_tree,
        )
    
    def _detect_language(self, file_path: Path, content: str) -> str:
        """Detect the language of a file."""
        ext = file_path.suffix.lower()
        
        if ext in self.PYTHON_EXTENSIONS:
            return 'python'
        
        if ext in self.BASH_EXTENSIONS:
            return 'bash'
        
        # Check shebang for extensionless scripts
        if content.startswith('#!'):
            shebang = content.split('\n')[0]
            for interpreter in self.SHELL_INTERPRETERS:
                if interpreter in shebang:
                    return 'bash'
            if 'python' in shebang:
                return 'python'
        
        return 'unknown'
