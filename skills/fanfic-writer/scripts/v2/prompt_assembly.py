"""
Fanfic Writer v2.0 - Prompt Assembly
Handles prompt construction, variable injection, and audit logging
"""
import re
import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

from .prompt_registry import PromptRegistry
from .atomic_io import atomic_write_text, atomic_append_jsonl
from .utils import generate_event_id, get_timestamp_iso, sanitize_filename


class PromptAssembler:
    """
    Assembles prompts by combining templates with context
    Handles variable substitution and constraint injection
    """
    
    def __init__(self, registry: PromptRegistry):
        self.registry = registry
    
    def assemble(
        self,
        template_name: str,
        variables: Dict[str, Any],
        constraints: Optional[Dict[str, Any]] = None,
        context_blocks: Optional[List[str]] = None
    ) -> str:
        """
        Assemble a complete prompt
        
        Process:
        1. Load template
        2. Inject context blocks
        3. Substitute variables
        4. Inject constraints
        5. Add task instruction
        
        Args:
            template_name: Name of template to use
            variables: Variables to substitute {key} -> value
            constraints: Runtime constraints (style, format, etc.)
            context_blocks: Ordered list of context sections
            
        Returns:
            Complete assembled prompt
        """
        # Load template
        template_content = self.registry.get_template_content(template_name)
        if not template_content:
            raise ValueError(f"Template not found: {template_name}")
        
        # Start with template
        prompt_parts = [template_content]
        
        # Add context blocks if provided
        if context_blocks:
            prompt_parts.append("\n\n【上下文】")
            for i, block in enumerate(context_blocks, 1):
                prompt_parts.append(f"\n[上下文块 {i}]\n{block}")
        
        # Join parts
        prompt = "\n".join(prompt_parts)
        
        # Substitute variables
        prompt = self._substitute_variables(prompt, variables)
        
        # Inject constraints
        if constraints:
            prompt = self._inject_constraints(prompt, constraints)
        
        return prompt
    
    def _substitute_variables(self, template: str, variables: Dict[str, Any]) -> str:
        """Substitute {variable_name} with values"""
        result = template
        
        for key, value in variables.items():
            placeholder = f"{{{key}}}"
            if placeholder in result:
                result = result.replace(placeholder, str(value))
        
        return result
    
    def _inject_constraints(self, prompt: str, constraints: Dict[str, Any]) -> str:
        """Inject runtime constraints into prompt"""
        constraint_parts = ["\n\n【约束条件】"]
        
        if 'word_count' in constraints:
            constraint_parts.append(f"- 字数要求: {constraints['word_count']}字左右")
        
        if 'style' in constraints:
            constraint_parts.append(f"- 风格: {constraints['style']}")
        
        if 'tone' in constraints:
            constraint_parts.append(f"- 基调: {constraints['tone']}")
        
        if 'pov' in constraints:
            constraint_parts.append(f"- 视角: {constraints['pov']}")
        
        if 'forbidden' in constraints:
            constraint_parts.append(f"- 禁止: {', '.join(constraints['forbidden'])}")
        
        if 'must_include' in constraints:
            constraint_parts.append(f"- 必须包含: {', '.join(constraints['must_include'])}")
        
        # Add constraints to prompt
        return prompt + "\n".join(constraint_parts)


class PromptAuditor:
    """
    Handles prompt audit logging
    Every model call must have its final prompt logged
    """
    
    def __init__(self, run_dir: Path):
        self.run_dir = Path(run_dir)
        self.logs_prompts_dir = self.run_dir / "logs" / "prompts"
        self.logs_prompts_dir.mkdir(parents=True, exist_ok=True)
        
        self.token_report_path = self.run_dir / "logs" / "token-report.jsonl"
    
    def log_prompt(
        self,
        run_id: str,
        phase: str,
        chapter: Optional[int],
        attempt: Optional[int],
        event: str,
        template_name: str,
        final_prompt: str,
        model: str,
        event_id: Optional[str] = None
    ) -> Path:
        """
        Log the final assembled prompt for audit
        
        Returns:
            Path to log file
        """
        if event_id is None:
            from .utils import generate_event_id
            event_id = generate_event_id(run_id, phase, chapter)
        
        # Create filename
        if chapter is not None:
            filename = f"{phase}_ch{chapter:03d}_{event_id}.md"
        else:
            filename = f"{phase}_{event_id}.md"
        
        log_path = self.logs_prompts_dir / filename
        
        # Build log content
        content_parts = [
            f"<!-- Prompt Audit Log -->",
            f"<!-- Event ID: {event_id} -->",
            f"<!-- Run ID: {run_id} -->",
            f"<!-- Phase: {phase} -->",
            f"<!-- Chapter: {chapter if chapter else 'N/A'} -->",
            f"<!-- Attempt: {attempt if attempt else 'N/A'} -->",
            f"<!-- Event: {event} -->",
            f"<!-- Template: {template_name} -->",
            f"<!-- Model: {model} -->",
            f"<!-- Timestamp: {get_timestamp_iso()} -->",
            "",
            "---",
            "",
            final_prompt
        ]
        
        content = "\n".join(content_parts)
        
        # Write atomically - MANDATORY per design spec
        # Audit chain missing is a blocking error (fatal)
        success = atomic_write_text(log_path, content)
        if not success:
            raise RuntimeError(
                f"CRITICAL: Failed to write prompt audit log to {log_path}. "
                f"Audit chain is mandatory per design spec - cannot proceed without it."
            )
        
        # Update token report with prompt reference
        self._update_token_report(event_id, str(log_path))
        
        return log_path
    
    def _update_token_report(self, event_id: str, prompt_path: str):
        """Add prompt_path reference to token report"""
        # This will be called after the actual API call with token counts
        # For now, we just ensure the record can be linked
        pass


class ContextBuilder:
    """
    Builds context blocks for prompt assembly
    
    Reads from state panels and formats context for model consumption
    """
    
    def __init__(self, state_manager):
        from .state_manager import StateManager
        self.state_manager: StateManager = state_manager
    
    def build_character_context(self, character_names: Optional[List[str]] = None) -> str:
        """Build character context block"""
        lines = ["## 角色状态"]
        
        if character_names:
            # Specific characters
            for name in character_names:
                entity = self.state_manager.characters.get_entity(name)
                if entity:
                    lines.append(f"\n### {name}")
                    for field, value in entity.get('values', {}).items():
                        lines.append(f"- {field}: {value}")
        else:
            # All characters
            for name in self.state_manager.characters.list_entities():
                entity = self.state_manager.characters.get_entity(name)
                if entity:
                    lines.append(f"\n### {name}")
                    for field, value in entity.get('values', {}).items():
                        if field != 'relationships':  # Skip complex fields
                            lines.append(f"- {field}: {value}")
        
        return "\n".join(lines)
    
    def build_plot_context(self, max_threads: int = 10) -> str:
        """Build plot thread context block"""
        lines = ["## 剧情线索"]
        
        active = self.state_manager.plot_threads.get_active_threads()
        
        for thread in active[:max_threads]:
            lines.append(f"\n- {thread['name']}: {thread.get('promised_payoff', '待揭示')}")
            lines.append(f"  (第{thread.get('introduced_chapter', '?')}章引入，紧迫度: {thread.get('urgency', 'pending')})")
        
        return "\n".join(lines)
    
    def build_timeline_context(self, recent_events: int = 5) -> str:
        """Build timeline context block"""
        data = self.state_manager.timeline.load()
        
        lines = ["## 时间线"]
        lines.append(f"\n当前: {data.get('current_date', '未知')}")
        
        events = data.get('events', [])
        if events:
            lines.append(f"\n最近事件:")
            for event in events[-recent_events:]:
                lines.append(f"- 第{event.get('chapter', '?')}章: {event.get('event', '')}")
        
        return "\n".join(lines)
    
    def build_inventory_context(self, owner: Optional[str] = None) -> str:
        """Build inventory context block"""
        lines = ["## 道具/物品"]
        
        if owner:
            items = self.state_manager.inventory.get_items_by_owner(owner)
            lines.append(f"\n{owner}拥有:")
            for item in items:
                lines.append(f"- {item['name']}: {item.get('description', '')} ({item.get('status', 'unknown')})")
        else:
            # List all active items
            data = self.state_manager.inventory.load()
            for name, entity in data.get('entities', {}).items():
                if entity.get('values', {}).get('status') == 'active':
                    owner = entity['values'].get('owner', '未知')
                    lines.append(f"- {name}: 属于 {owner}")
        
        return "\n".join(lines)
    
    def build_sanitizer_output(self, chapter_num: int) -> str:
        """Build sanitizer output context for chapter N"""
        # Read from sanitizer_output.jsonl
        sanitizer_path = self.state_manager.run_dir / "4-state" / "sanitizer_output.jsonl"
        
        if not sanitizer_path.exists():
            return "## 状态净化\n(无输出)"
        
        lines = ["## 状态净化输出"]
        
        with open(sanitizer_path, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    record = json.loads(line.strip())
                    if record.get('chapter') == chapter_num:
                        lines.append(f"\n**不变量 (Invariants):**")
                        for inv in record.get('invariants_enforced', []):
                            lines.append(f"- {inv}")
                        
                        lines.append(f"\n**微调 (Soft Retcons):**")
                        for retcon in record.get('soft_retcons_applied', []):
                            lines.append(f"- {retcon}")
                        
                        lines.append(f"\n**理由:** {record.get('reason', '')}")
                        break
                except json.JSONDecodeError:
                    continue
        
        return "\n".join(lines)
    
    def build_summary_context(self, current_chapter: int, window_size: int = 3) -> str:
        """Build rolling summary context from session_memory"""
        data = self.state_manager.characters.run_dir  # hack to get run_dir
        session_memory_path = self.state_manager.characters.file_path.parent / "session_memory.json"
        
        if not session_memory_path.exists():
            return "## 前文摘要\n(无记录)"
        
        with open(session_memory_path, 'r', encoding='utf-8') as f:
            memory = json.load(f)
        
        chapters = memory.get('chapters', [])
        
        lines = ["## 前文摘要"]
        
        for ch in chapters[-window_size:]:
            ch_num = ch.get('chapter_number', 0)
            if ch_num < current_chapter:
                lines.append(f"\n### 第{ch_num}章")
                lines.append(ch.get('summary', ''))
                
                # Key changes
                key_changes = ch.get('key_changes', [])
                if key_changes:
                    lines.append("\n关键变更:")
                    for change in key_changes:
                        lines.append(f"- {change}")
        
        return "\n".join(lines)


# ============================================================================
# High-level Prompt Builder
# ============================================================================

class PromptBuilder:
    """
    High-level interface for building prompts for specific phases
    """
    
    def __init__(
        self,
        registry: PromptRegistry,
        state_manager,
        run_dir: Path
    ):
        from .state_manager import StateManager
        self.assembler = PromptAssembler(registry)
        self.auditor = PromptAuditor(run_dir)
        self.context_builder = ContextBuilder(state_manager)
        self.registry = registry
    
    def build_chapter_outline_prompt(
        self,
        run_id: str,
        chapter_num: int,
        chapter_title: str,
        chapter_summary: str,
        previous_content: str,
        target_words: int,
        event_id: Optional[str] = None
    ) -> Tuple[str, Path]:
        """Build prompt for chapter outline generation (Phase 6.1)"""
        
        # Build context blocks
        context_blocks = [
            self.context_builder.build_character_context(),
            self.context_builder.build_plot_context(),
            self.context_builder.build_timeline_context(),
            self.context_builder.build_inventory_context(),
            self.context_builder.build_summary_context(chapter_num)
        ]
        
        # Variables
        variables = {
            'previous_chapter_content': previous_content[:2000] if previous_content else "(首章无前文)",
            'chapter_summary': chapter_summary,
            'chapter_title': chapter_title,
            'target_words': target_words
        }
        
        # Constraints
        constraints = {
            'word_count': target_words,
            'style': '网文风格，节奏紧凑'
        }
        
        # Assemble
        prompt = self.assembler.assemble(
            template_name='chapter_outline',
            variables=variables,
            constraints=constraints,
            context_blocks=context_blocks
        )
        
        # Audit log
        log_path = self.auditor.log_prompt(
            run_id=run_id,
            phase='6.1',
            chapter=chapter_num,
            attempt=1,
            event='outline_generate',
            template_name='chapter_outline',
            final_prompt=prompt,
            model='nvidia/moonshotai/kimi-k2.5',
            event_id=event_id
        )
        
        return prompt, log_path
    
    def build_chapter_draft_prompt(
        self,
        run_id: str,
        chapter_num: int,
        chapter_title: str,
        detailed_outline: str,
        previous_content: str,
        segment_summary: str,
        segment_words: int,
        is_first_segment: bool,
        written_content: str = "",
        event_id: Optional[str] = None
    ) -> Tuple[str, Path]:
        """Build prompt for chapter draft generation (Phase 6.3)"""
        
        # Build context blocks
        context_blocks = [
            self.context_builder.build_sanitizer_output(chapter_num),
            self.context_builder.build_character_context(),
            self.context_builder.build_plot_context()
        ]
        
        # Select template based on segment
        template_name = 'chapter_draft_first' if is_first_segment else 'chapter_draft_continue'
        
        # Variables
        variables = {
            'previous_chapter_content': previous_content[:1500] if previous_content else "(首章)",
            'detailed_outline': detailed_outline,
            'chapter_title': chapter_title,
            'segment_summary': segment_summary,
            'segment_words': segment_words,
            'written_content': written_content if not is_first_segment else ""
        }
        
        # Constraints
        constraints = {
            'word_count': segment_words,
            'style': '网文风格，避免AI味'
        }
        
        # Assemble
        prompt = self.assembler.assemble(
            template_name=template_name if self.registry.get_template(template_name) else 'chapter_draft',
            variables=variables,
            constraints=constraints,
            context_blocks=context_blocks
        )
        
        # Audit log
        log_path = self.auditor.log_prompt(
            run_id=run_id,
            phase='6.3',
            chapter=chapter_num,
            attempt=1,
            event='draft_generate',
            template_name=template_name,
            final_prompt=prompt,
            model='nvidia/moonshotai/kimi-k2.5',
            event_id=event_id
        )
        
        return prompt, log_path


# ============================================================================
# Module Test
# ============================================================================

if __name__ == "__main__":
    import tempfile
    
    print("=== Prompt Assembly Test ===\n")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create mock structures
        skill_dir = Path(tmpdir) / "skill"
        prompts_v1 = skill_dir / "prompts" / "v1"
        prompts_v1.mkdir(parents=True)
        
        # Create test template
        template_content = """【输入】
上一章：{previous_chapter_content}
大纲：{chapter_summary}

【任务】写{chapter_title}的详细大纲
目标字数：{target_words}
"""
        (prompts_v1 / "chapter_outline.md").write_text(template_content)
        
        # Create run structure
        run_dir = Path(tmpdir) / "run"
        state_dir = run_dir / "4-state"
        state_dir.mkdir(parents=True)
        
        # Initialize registry
        from .prompt_registry import PromptRegistry
        registry = PromptRegistry(run_dir, skill_dir)
        registry.initialize("20260215_TEST", "2.0.0")
        
        # Test assembler
        assembler = PromptAssembler(registry)
        
        variables = {
            'previous_chapter_content': '这是上一章的内容...',
            'chapter_summary': '本章主角获得系统',
            'chapter_title': '第一章：系统觉醒',
            'target_words': 2500
        }
        
        constraints = {
            'word_count': 2500,
            'style': '网文风格'
        }
        
        context_blocks = [
            "## 角色状态\n主角：张大胆，外卖员",
            "## 剧情线索\n系统来源待揭示"
        ]
        
        prompt = assembler.assemble(
            template_name='chapter_outline',
            variables=variables,
            constraints=constraints,
            context_blocks=context_blocks
        )
        
        print("[Test] Assembled prompt:")
        print("-" * 40)
        print(prompt[:500])
        print("-" * 40)
        
        # Test auditor
        auditor = PromptAuditor(run_dir)
        log_path = auditor.log_prompt(
            run_id="20260215_TEST",
            phase="6.1",
            chapter=1,
            attempt=1,
            event="outline_generate",
            template_name="chapter_outline",
            final_prompt=prompt,
            model="nvidia/moonshotai/kimi-k2.5"
        )
        
        print(f"\n[Test] Audit log created: {log_path.exists()}")
        
    print("\n=== All tests completed ===")
