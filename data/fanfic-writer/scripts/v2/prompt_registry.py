"""
Fanfic Writer v2.0 - Prompt Registry
Manages prompt templates with versioning and audit trail
"""
import json
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass

from .atomic_io import atomic_write_json
from .utils import get_timestamp_iso


@dataclass
class PromptTemplate:
    """A registered prompt template"""
    name: str
    path: Path
    version: str
    description: str
    source: str  # 'v1', 'v2_addons', or 'builtin'
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'path': str(self.path),
            'version': self.version,
            'description': self.description,
            'source': self.source
        }


class PromptRegistry:
    """
    Manages prompt template registry
    
    Ensures v1.0 prompts are used for core functions (chapter_outline, chapter_draft)
    as required by design spec.
    """
    
    # Required templates with their expected sources
    REQUIRED_TEMPLATES = {
        'chapter_outline': {'source': 'v1', 'required': True},
        'chapter_draft': {'source': 'v1', 'required': True},
        'critic_editor': {'source': 'v2_addons', 'required': True},
        'critic_logic': {'source': 'v2_addons', 'required': True},
        'critic_continuity': {'source': 'v2_addons', 'required': True},
        'backpatch_plan': {'source': 'v2_addons', 'required': True},
        'sanitizer': {'source': 'v2_addons', 'required': True},
        'main_outline': {'source': 'v1', 'required': True},
        'chapter_plan': {'source': 'v1', 'required': True},
        'world_building': {'source': 'v1', 'required': True},
        'style_guide': {'source': 'v1', 'required': False},
        'qc_evaluate': {'source': 'v2_addons', 'required': True}
    }
    
    def __init__(self, run_dir: Path, skill_dir: Path):
        """
        Initialize PromptRegistry
        
        Args:
            run_dir: Current run directory
            skill_dir: Skill root directory (for accessing prompts/)
        """
        self.run_dir = Path(run_dir)
        self.skill_dir = Path(skill_dir)
        self.registry_path = self.run_dir / "4-state" / "prompt_registry.json"
        self.prompts_dir = self.skill_dir / "prompts"
        
        self._registry: Optional[Dict[str, Any]] = None
        self._templates: Dict[str, PromptTemplate] = {}
    
    def initialize(self, run_id: str, skill_version: str = "2.0.0") -> bool:
        """
        Initialize registry for a new run
        
        Returns:
            True on success
            
        Raises:
            RuntimeError: If required v1 templates are missing (blocking error)
        """
        # Discover available templates
        templates = self._discover_templates()
        
        # Validate required templates
        missing_required = []
        for name, spec in self.REQUIRED_TEMPLATES.items():
            if spec['required'] and name not in templates:
                missing_required.append(name)
        
        if missing_required:
            raise RuntimeError(
                f"Missing required prompt templates: {missing_required}. "
                f"Auto mode requires v1.0 templates for chapter_outline and chapter_draft."
            )
        
        # Verify audit chain capability (logs/prompts/ must be writable)
        audit_dir = self.run_dir / "logs" / "prompts"
        try:
            audit_dir.mkdir(parents=True, exist_ok=True)
            # Test write access
            test_file = audit_dir / ".write_test"
            test_file.write_text("test")
            test_file.unlink()
        except Exception as e:
            raise RuntimeError(
                f"CRITICAL: Cannot create prompt audit directory: {audit_dir}. "
                f"Audit chain is mandatory per design spec. Error: {e}"
            )
        
        # Build registry
        self._registry = {
            'run_id': run_id,
            'skill_version': skill_version,
            'initialized_at': get_timestamp_iso(),
            'templates': {name: tmpl.to_dict() for name, tmpl in templates.items()},
            'audit_chain': {
                'enabled': True,
                'directory': str(audit_dir),
                'mandatory': True  # Design spec: missing audit = fatal
            }
        }
        
        self._templates = templates
        
        # Save registry
        return atomic_write_json(self.registry_path, self._registry)
    
    def load(self) -> Dict[str, Any]:
        """Load existing registry"""
        if self._registry is not None:
            return self._registry
        
        if not self.registry_path.exists():
            raise FileNotFoundError(f"Prompt registry not found: {self.registry_path}")
        
        with open(self.registry_path, 'r', encoding='utf-8') as f:
            self._registry = json.load(f)
        
        # Rebuild template objects
        self._templates = {}
        for name, data in self._registry.get('templates', {}).items():
            self._templates[name] = PromptTemplate(
                name=data['name'],
                path=Path(data['path']),
                version=data['version'],
                description=data['description'],
                source=data['source']
            )
        
        return self._registry
    
    def _discover_templates(self) -> Dict[str, PromptTemplate]:
        """Discover all available prompt templates"""
        templates = {}
        
        # Check v1 prompts
        v1_dir = self.prompts_dir / "v1"
        if v1_dir.exists():
            for md_file in v1_dir.glob("*.md"):
                name = md_file.stem
                templates[name] = PromptTemplate(
                    name=name,
                    path=md_file,
                    version="1.0.0",
                    description=f"v1.0 template: {name}",
                    source="v1"
                )
        
        # Check v2 addons
        v2_dir = self.prompts_dir / "v2_addons"
        if v2_dir.exists():
            for md_file in v2_dir.glob("*.md"):
                name = md_file.stem
                # v2 overrides v1 if same name
                templates[name] = PromptTemplate(
                    name=name,
                    path=md_file,
                    version="2.0.0",
                    description=f"v2.0 addon: {name}",
                    source="v2_addons"
                )
        
        return templates
    
    def get_template(self, name: str) -> Optional[PromptTemplate]:
        """Get a template by name"""
        self.load()
        return self._templates.get(name)
    
    def get_template_content(self, name: str) -> Optional[str]:
        """Get the actual content of a template"""
        template = self.get_template(name)
        if not template:
            return None
        
        if not template.path.exists():
            return None
        
        with open(template.path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def validate_for_auto_mode(self) -> Tuple[bool, List[str]]:
        """
        Validate that registry is ready for auto mode
        
        Returns:
            (is_valid, list_of_errors)
        """
        errors = []
        
        try:
            self.load()
        except FileNotFoundError as e:
            return False, [str(e)]
        
        # Check v1 templates for auto mode
        for name, spec in self.REQUIRED_TEMPLATES.items():
            if spec['source'] == 'v1' and spec['required']:
                template = self._templates.get(name)
                if not template:
                    errors.append(f"Missing required v1 template: {name}")
                elif template.source != 'v1':
                    errors.append(
                        f"Template {name} must be from v1 source for auto mode, "
                        f"got: {template.source}"
                    )
                elif not template.path.exists():
                    errors.append(f"Template file missing: {template.path}")
        
        return len(errors) == 0, errors
    
    def list_templates(self) -> List[PromptTemplate]:
        """List all registered templates"""
        self.load()
        return list(self._templates.values())
    
    def get_template_path(self, name: str) -> Optional[Path]:
        """Get the file path for a template"""
        template = self.get_template(name)
        return template.path if template else None


# ============================================================================
# Template Validation Helpers
# ============================================================================

def validate_template_content(content: str, template_type: str) -> Tuple[bool, List[str]]:
    """
    Validate that a template contains required placeholders
    
    Args:
        content: Template content
        template_type: Type of template (chapter_outline, chapter_draft, etc.)
        
    Returns:
        (is_valid, list_of_warnings)
    """
    warnings = []
    
    # Common placeholders all templates should have
    common_placeholders = ['{', '}']  # Basic check for placeholder syntax
    
    # Type-specific required placeholders
    type_placeholders = {
        'chapter_outline': [
            'previous_chapter_content',
            'chapter_summary',
            'chapter_title',
            'target_words'
        ],
        'chapter_draft': [
            'previous_chapter_content',
            'detailed_outline',
            'chapter_title',
            'segment_summary',
            'segment_words'
        ]
    }
    
    # Check for placeholder syntax
    if '{' not in content or '}' not in content:
        warnings.append("Template may be missing placeholder syntax {}")
    
    # Check type-specific placeholders
    required = type_placeholders.get(template_type, [])
    for placeholder in required:
        if placeholder not in content:
            warnings.append(f"Template may be missing required placeholder: {placeholder}")
    
    return len(warnings) == 0, warnings


# ============================================================================
# Default Template Generation (for initial setup)
# ============================================================================

def generate_default_templates(skill_dir: Path) -> bool:
    """
    Generate default prompt templates if they don't exist
    
    This is called during skill installation to ensure prompts/ directory
    is populated with default templates.
    """
    prompts_dir = Path(skill_dir) / "prompts"
    prompts_dir.mkdir(parents=True, exist_ok=True)
    
    v1_dir = prompts_dir / "v1"
    v1_dir.mkdir(parents=True, exist_ok=True)
    
    v2_dir = prompts_dir / "v2_addons"
    v2_dir.mkdir(parents=True, exist_ok=True)
    
    # Note: Actual template content should be written separately
    # This function just ensures directory structure
    
    return True


# ============================================================================
# Module Test
# ============================================================================

if __name__ == "__main__":
    import tempfile
    
    print("=== Prompt Registry Test ===\n")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create mock skill structure
        skill_dir = Path(tmpdir) / "skill"
        prompts_v1 = skill_dir / "prompts" / "v1"
        prompts_v1.mkdir(parents=True)
        
        # Create test templates
        (prompts_v1 / "chapter_outline.md").write_text("# Chapter Outline\n{chapter_title}")
        (prompts_v1 / "chapter_draft.md").write_text("# Chapter Draft\n{previous_chapter_content}")
        
        prompts_v2 = skill_dir / "prompts" / "v2_addons"
        prompts_v2.mkdir(parents=True)
        (prompts_v2 / "critic_editor.md").write_text("# Critic Editor\nAnalyze:")
        
        # Create run directory
        run_dir = Path(tmpdir) / "run"
        state_dir = run_dir / "4-state"
        state_dir.mkdir(parents=True)
        
        # Test registry initialization
        registry = PromptRegistry(run_dir, skill_dir)
        
        try:
            registry.initialize("20260215_224500_TEST", "2.0.0")
            print("[Test] Registry initialized: PASS")
        except RuntimeError as e:
            print(f"[Test] Registry initialized: FAIL - {e}")
        
        # Test load
        data = registry.load()
        print(f"[Test] Registry loaded: {len(data['templates'])} templates")
        
        # Test get template
        tmpl = registry.get_template("chapter_outline")
        print(f"[Test] Get template: {'PASS' if tmpl else 'FAIL'}")
        if tmpl:
            print(f"  Source: {tmpl.source}")
        
        # Test get content
        content = registry.get_template_content("chapter_outline")
        print(f"[Test] Get content: {'PASS' if content else 'FAIL'}")
        
        # Test validation
        is_valid, errors = registry.validate_for_auto_mode()
        print(f"[Test] Auto mode validation: {'PASS' if is_valid else 'FAIL'}")
        if errors:
            for err in errors:
                print(f"  Error: {err}")
        
    print("\n=== All tests completed ===")
