"""
Fanfic Writer v2.0 - Phase Runner (Phases 1-5)
Orchestrates initialization through worldbuilding
"""
import json
import os
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, Callable
from datetime import datetime

from .workspace import WorkspaceManager, generate_intent_checklist
from .config_manager import ConfigManager
from .state_manager import StateManager
from .prompt_registry import PromptRegistry
from .price_table import PriceTableManager, CostBudgetManager
from .resume_manager import RunLock, ResumeManager, RuntimeConfigManager
from .atomic_io import atomic_write_json, atomic_write_text
from .utils import get_timestamp_iso


class PhaseRunner:
    """
    Runs Phases 1-5 of the novel writing pipeline:
    - Phase 1: Initialization (config, workspace)
    - Phase 2: Style Guide
    - Phase 3: Main Outline
    - Phase 4: Chapter Planning
    - Phase 5: World Building
    - Phase 5.5: Alignment Check
    """
    
    def __init__(
        self,
        workspace_manager: WorkspaceManager,
        model_callable: Optional[Callable] = None
    ):
        self.workspace = workspace_manager
        self.model_callable = model_callable
        self._current_run_dir: Optional[Path] = None
        self._config_manager: Optional[ConfigManager] = None
        self._state_manager: Optional[StateManager] = None
    
    # =========================================================================
    # Phase 1: Initialization
    # =========================================================================
    
    def phase1_initialize(
        self,
        book_title: str,
        genre: str,
        target_words: int,
        **kwargs
    ) -> Tuple[Path, str, str]:
        """
        Phase 1: Initialize book workspace
        
        Returns:
            (run_dir, book_uid, run_id)
        """
        print(f"[Phase 1] Initializing: {book_title}")
        
        # Create workspace
        run_dir, book_uid, run_id, paths = self.workspace.create_new_book(
            book_title=book_title,
            genre=genre,
            target_words=target_words,
            **kwargs
        )
        
        self._current_run_dir = run_dir
        
        # Initialize config manager
        self._config_manager = ConfigManager(run_dir)
        config = self._config_manager.load()
        
        # Generate intent checklist
        checklist = generate_intent_checklist(config)
        checklist_path = paths['intent_checklist']
        atomic_write_json(checklist_path, checklist)
        
        # Initialize price table
        price_mgr = PriceTableManager(run_dir)
        usd_cny_rate = kwargs.get('usd_cny_rate', 6.90)
        price_mgr.initialize(usd_cny_rate=usd_cny_rate)
        
        # Acquire run lock
        run_lock = RunLock(run_dir)
        lock_success, lock_error = run_lock.acquire(mode=kwargs.get('mode', 'manual'))
        if not lock_success:
            raise RuntimeError(f"Cannot acquire run lock: {lock_error}")
        
        # Generate runtime effective config
        rt_mgr = RuntimeConfigManager(run_dir)
        rt_mgr.generate(
            cli_args={k: v for k, v in kwargs.items() if v is not None},
            env_vars={k: v for k, v in os.environ.items() if k.startswith('FANFIC_')},
            config_file={'mode': config['generation']['mode'], 
                        'model': config['generation']['model']},
            defaults={'max_attempts': 3, 'auto_threshold': 85}
        )
        
        print(f"[Phase 1] Complete: {run_dir}")
        return run_dir, book_uid, run_id
    
    # =========================================================================
    # Phase 2: Style Guide
    # =========================================================================
    
    def phase2_style_guide(
        self,
        narrative_voice: str = "第三人称限知",
        dialogue_style: str = "口语化",
        description_density: str = "动作>心理>环境",
        humor_tension_balance: str = "70%轻松+30%紧张",
        custom_rules: Optional[list] = None
    ) -> Path:
        """
        Phase 2: Generate style guide
        
        Can be auto-generated or use provided values
        """
        print("[Phase 2] Generating style guide...")
        
        if not self._current_run_dir:
            raise RuntimeError("Must run Phase 1 first")
        
        style_guide_path = self._current_run_dir / "0-config" / "style_guide.md"
        
        # Build style guide content
        content_lines = [
            f"# Style Guide",
            "",
            f"## Narrative Voice",
            f"{narrative_voice}",
            "",
            f"## Dialogue Style",
            f"{dialogue_style}",
            "",
            f"## Description Density",
            f"{description_density}",
            "",
            f"## Humor/Tension Balance",
            f"{humor_tension_balance}",
            "",
            "## Forbidden Phrases",
            "- \"突然\" (用\"猛然\"或具体动作代替)",
            "- \"非常\"\"特别\" (用具体描写代替)",
            "- 连续超过3句对话无动作/心理描写",
        ]
        
        if custom_rules:
            content_lines.extend(["", "## Custom Rules"])
            for rule in custom_rules:
                content_lines.append(f"- {rule}")
        
        content = "\n".join(content_lines)
        atomic_write_text(style_guide_path, content)
        
        print(f"[Phase 2] Complete: {style_guide_path}")
        return style_guide_path
    
    # =========================================================================
    # Phase 3: Main Outline
    # =========================================================================
    
    def phase3_main_outline(
        self,
        outline_content: Optional[str] = None
    ) -> Path:
        """
        Phase 3: Generate or save main outline
        
        If outline_content provided, save it directly.
        Otherwise, would call model (placeholder for future)
        """
        print("[Phase 3] Main outline...")
        
        if not self._current_run_dir:
            raise RuntimeError("Must run Phase 1 first")
        
        outline_path = self._current_run_dir / "1-outline" / "1-main-outline.md"
        
        if outline_content:
            # Use provided content
            atomic_write_text(outline_path, outline_content)
        else:
            # Placeholder: would call model
            # For now, create template
            config = self._config_manager.load()
            title = config['book']['title']
            genre = config['book']['genre']
            
            template = f"""# {title} - 主线大纲

## 题材
{genre}

## 一句话简介
（待填写：20字内核心卖点）

## 核心卖点
- 卖点1：...
- 卖点2：...
- 卖点3：...

## 世界背景
（待填写）

## 主要角色

### 主角
- 姓名/代号：
- 身份背景：
- 性格特点：
- 核心目标：

## 主线剧情

### 第一卷：【卷名】（第1-?章）
卷主题：
核心冲突：

### 第二卷：【卷名】
...

## 关键转折点
1. 第X章：...

## 预计完结
（待填写）
"""
            atomic_write_text(outline_path, template)
        
        print(f"[Phase 3] Complete: {outline_path}")
        return outline_path
    
    # =========================================================================
    # Phase 4: Chapter Planning
    # =========================================================================
    
    def phase4_chapter_plan(
        self,
        chapters_data: Optional[list] = None
    ) -> Tuple[Path, Path]:
        """
        Phase 4: Generate chapter plan and detailed outlines index
        
        Returns:
            (chapter_plan_path, chapter_outlines_path)
        """
        print("[Phase 4] Chapter planning...")
        
        if not self._current_run_dir:
            raise RuntimeError("Must run Phase 1 first")
        
        config = self._config_manager.load()
        target_words = config['book']['target_word_count']
        chapter_target = config['book']['chapter_target_words']
        
        # Calculate chapter count
        estimated_chapters = max(10, target_words // chapter_target)
        
        if chapters_data:
            # Use provided data
            chapter_plan = {
                'total_chapters': len(chapters_data),
                'chapters': chapters_data
            }
            
            chapter_outlines = {
                'chapters': [
                    {
                        'chapter_number': c['number'],
                        'title': c['title'],
                        'theme': c.get('key_event', ''),
                        'purpose': c.get('summary', ''),
                        'word_count_target': c.get('target_words', chapter_target),
                        'hook': c.get('cliffhanger', '')
                    }
                    for c in chapters_data
                ]
            }
        else:
            # Create template structure
            chapter_plan = {
                'total_chapters': estimated_chapters,
                'chapters': [
                    {
                        'chapter_number': i,
                        'title': f"第{i}章",
                        'word_count': chapter_target,
                        'pacing': 'medium',
                        'tension': 'medium',
                        'scene_breakdown': []
                    }
                    for i in range(1, min(estimated_chapters + 1, 101))
                ],
                'volume_breakdown': [
                    {'volume': 1, 'name': '第一卷', 'chapters': f'1-{min(20, estimated_chapters)}'}
                ]
            }
            
            chapter_outlines = {
                'chapters': [
                    {
                        'chapter_number': i,
                        'title': f"第{i}章",
                        'theme': '待设定',
                        'purpose': '待设定',
                        'word_count_target': chapter_target,
                        'scenes': [],
                        'characters': [],
                        'plot_points': [],
                        'hook': ''
                    }
                    for i in range(1, min(estimated_chapters + 1, 101))
                ]
            }
        
        # Save files
        plan_path = self._current_run_dir / "2-planning" / "2-chapter-plan.json"
        outlines_path = self._current_run_dir / "1-outline" / "5-chapter-outlines.json"
        
        atomic_write_json(plan_path, chapter_plan)
        atomic_write_json(outlines_path, chapter_outlines)
        
        print(f"[Phase 4] Complete: {plan_path}, {outlines_path}")
        return plan_path, outlines_path
    
    # =========================================================================
    # Phase 5: World Building
    # =========================================================================
    
    def phase5_world_building(
        self,
        world_content: Optional[str] = None
    ) -> Path:
        """
        Phase 5: Generate world building document
        """
        print("[Phase 5] World building...")
        
        if not self._current_run_dir:
            raise RuntimeError("Must run Phase 1 first")
        
        world_path = self._current_run_dir / "3-world" / "3-world-building.md"
        
        if world_content:
            atomic_write_text(world_path, world_content)
        else:
            # Create template
            config = self._config_manager.load()
            title = config['book']['title']
            
            template = f"""# {title} - 世界观设定

## 世界观

### 时空背景
- 时间：
- 空间：
- 基本规则：

### 势力分布
（待填写）

### 力量/技能体系
- 体系名称：
- 等级划分：
- 核心规则：
- 限制条件：

## 主要角色

### 主角
【基础信息】
- 姓名：
- 年龄：
- 外貌特征：

【性格】
- 表层性格：
- 深层性格：
- 性格缺陷：

【背景】
- 出身：
- 关键经历：
- 关系网：

【目标与成长】
- 短期目标：
- 长期目标：
- 成长弧线：

## 关键设定

### 重要道具
...

### 重要地点
...

### 关键规则
...
"""
            atomic_write_text(world_path, template)
        
        print(f"[Phase 5] Complete: {world_path}")
        return world_path
    
    # =========================================================================
    # Phase 5.5: Alignment Check
    # =========================================================================
    
    def phase5_5_alignment_check(self) -> Tuple[float, Optional[Path]]:
        """
        Phase 5.5: Check alignment between intent checklist and world building
        
        Returns:
            (deviation_score, warning_path or None)
            deviation_score: 0.0 = perfect alignment, 1.0 = completely off
        """
        print("[Phase 5.5] Alignment check...")
        
        if not self._current_run_dir:
            raise RuntimeError("Must run Phase 1 first")
        
        # Load checklist
        checklist_path = self._current_run_dir / "0-config" / "intent_checklist.json"
        if not checklist_path.exists():
            print("[Phase 5.5] Warning: No checklist found")
            return 0.0, None
        
        with open(checklist_path, 'r', encoding='utf-8') as f:
            checklist = json.load(f)
        
        # Load world building
        world_path = self._current_run_dir / "3-world" / "3-world-building.md"
        if not world_path.exists():
            print("[Phase 5.5] Warning: No world building found")
            return 1.0, None
        
        with open(world_path, 'r', encoding='utf-8') as f:
            world_content = f.read()
        
        # Check each item
        items = checklist.get('items', [])
        failed_items = []
        
        for item in items:
            if not item.get('required', False):
                continue
            
            # Simple check: see if must_be content is in world_content
            must_be = item.get('must_be', '')
            if isinstance(must_be, list):
                must_be = ' '.join(must_be)
            
            # Very naive check - in real implementation would use more sophisticated matching
            if must_be and must_be != '待设定' and len(must_be) > 2:
                if must_be not in world_content:
                    failed_items.append(item)
        
        # Calculate deviation
        if not items:
            deviation = 0.0
        else:
            required_items = [i for i in items if i.get('required', False)]
            if not required_items:
                deviation = 0.0
            else:
                deviation = len(failed_items) / len(required_items)
        
        # Generate warning if needed
        warning_path = None
        if deviation >= 0.2:  # 20% or more deviation
            warning_path = self._current_run_dir / "drafts" / "alignment" / f"alignment-warning_{get_timestamp_iso().replace(':', '-')}.md"
            
            warning_content = f"""# Alignment Warning

Deviation Score: {deviation:.1%}
Failed Items: {len(failed_items)}/{len([i for i in items if i.get('required', False)])}

## Failed Checks
"""
            for item in failed_items:
                warning_content += f"\n- **{item['name']}**: {item['description']}\n"
                warning_content += f"  - Expected: {item.get('must_be', 'N/A')}\n"
            
            warning_content += """
## Recommended Actions
1. Review world building against intent checklist
2. Update world building to align with original intent
3. Or update intent checklist if requirements have changed
"""
            atomic_write_text(warning_path, warning_content)
            print(f"[Phase 5.5] Warning generated: {warning_path}")
        
        print(f"[Phase 5.5] Complete: deviation = {deviation:.1%}")
        return deviation, warning_path
    
    # =========================================================================
    # Run All Phases 1-5
    # =========================================================================
    
    def run_all(
        self,
        book_title: str,
        genre: str,
        target_words: int,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Run all phases 1-5 in sequence
        
        Returns:
            Dict with paths to all generated files
        """
        results = {}
        
        # Phase 1
        run_dir, book_uid, run_id = self.phase1_initialize(
            book_title, genre, target_words, **kwargs
        )
        results['run_dir'] = run_dir
        results['book_uid'] = book_uid
        results['run_id'] = run_id
        
        # Phase 2
        style_path = self.phase2_style_guide(
            **kwargs.get('style_guide', {})
        )
        results['style_guide'] = style_path
        
        # Phase 3
        outline_path = self.phase3_main_outline(
            kwargs.get('outline_content')
        )
        results['main_outline'] = outline_path
        
        # Phase 4
        plan_path, outlines_path = self.phase4_chapter_plan(
            kwargs.get('chapters_data')
        )
        results['chapter_plan'] = plan_path
        results['chapter_outlines'] = outlines_path
        
        # Phase 5
        world_path = self.phase5_world_building(
            kwargs.get('world_content')
        )
        results['world_building'] = world_path
        
        # Phase 5.5
        deviation, warning_path = self.phase5_5_alignment_check()
        results['alignment_deviation'] = deviation
        results['alignment_warning'] = warning_path
        
        print("\n[Phases 1-5] All complete!")
        return results


# ============================================================================
# Module Test
# ============================================================================

if __name__ == "__main__":
    import tempfile
    
    print("=== Phase Runner Test (Phases 1-5) ===\n")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        base_dir = Path(tmpdir) / "novels"
        
        # Create workspace manager
        workspace = WorkspaceManager(base_dir)
        
        # Create phase runner
        runner = PhaseRunner(workspace)
        
        # Test full run
        results = runner.run_all(
            book_title="阴间外卖",
            genre="都市灵异",
            target_words=100000,
            subgenre="系统流",
            mode="manual"
        )
        
        print(f"\n[Test] Run complete:")
        print(f"  run_dir: {results['run_dir']}")
        print(f"  book_uid: {results['book_uid']}")
        print(f"  style_guide: {results['style_guide'].exists()}")
        print(f"  main_outline: {results['main_outline'].exists()}")
        print(f"  chapter_plan: {results['chapter_plan'].exists()}")
        print(f"  world_building: {results['world_building'].exists()}")
        print(f"  alignment_deviation: {results['alignment_deviation']:.1%}")
        
    print("\n=== All tests completed ===")
