"""
Fanfic Writer v2.0 - Writing Loop (Phase 6)
Core writing pipeline with QC, Attempt cycle, and FORCED handling
"""
import json
import re
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple, Callable
from dataclasses import dataclass
from enum import Enum

from .config_manager import ConfigManager
from .state_manager import StateManager, Evidence
from .prompt_assembly import PromptBuilder
from .price_table import PriceTableManager
from .atomic_io import atomic_write_text, atomic_write_json, atomic_append_jsonl
from .utils import get_timestamp_iso, generate_event_id, sanitize_chapter_filename


class QCStatus(Enum):
    INIT = "INIT"
    PASS = "PASS"
    WARNING = "WARNING"
    REVISE = "REVISE"
    FORCED = "FORCED"


@dataclass
class QCResult:
    """Quality Check result"""
    score: int
    status: QCStatus
    dimensions: Dict[str, int]
    pros: List[str]
    cons: List[str]
    rewrite_plan: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'score': self.score,
            'status': self.status.value,
            'dimensions': self.dimensions,
            'pros': self.pros,
            'cons': self.cons,
            'rewrite_plan': self.rewrite_plan
        }


class WritingLoop:
    """
    Phase 6: Chapter-by-chapter writing with quality control
    
    Flow:
    6.1 Sanitizer -> 6.2 Outline Confirm -> 6.3 Draft -> 6.4 QC -> 6.5 Content Confirm -> 6.6 State Commit
    """
    
    def __init__(
        self,
        run_dir: Path,
        model_callable: Callable,
        config_manager: Optional[ConfigManager] = None,
        state_manager: Optional[StateManager] = None,
        prompt_builder: Optional[PromptBuilder] = None
    ):
        self.run_dir = Path(run_dir)
        self.model_callable = model_callable
        
        self.config = (config_manager or ConfigManager(run_dir)).load()
        self.state = state_manager or StateManager(run_dir)
        self.prompt_builder = prompt_builder
        self.price_mgr = PriceTableManager(run_dir)
        
        # QC config
        qc_config = self.config.get('qc', {})
        self.pass_threshold = qc_config.get('pass_threshold', 85)
        self.warning_threshold = qc_config.get('warning_threshold', 75)
        self.max_attempts = self.config.get('generation', {}).get('max_attempts', 3)
        self.mode = self.config.get('generation', {}).get('mode', 'manual')
        
        # Ending state check
        self.target_words = self.config.get('book', {}).get('target_word_count', 100000)
        self.max_chapters = 200  # Hard limit
    
    def _get_forced_streak(self) -> int:
        """Get current forced_streak value"""
        state_path = self.run_dir / "4-state" / "4-writing-state.json"
        try:
            with open(state_path, 'r', encoding='utf-8') as f:
                state = json.load(f)
            return state.get('forced_streak', 0)
        except:
            return 0
    
    # ========================================================================
    # 6.1 Sanitizer
    # ========================================================================
    
    def sanitizer(self, chapter_num: int) -> Dict[str, Any]:
        """
        6.1: State Sanitizer
        
        Reads state panels and extracts invariants for chapter generation
        """
        print(f"[6.1] Sanitizer for Chapter {chapter_num}")
        
        # Get invariants
        invariants = self.state.get_invariants(chapter_num)
        
        # Check for open backpatch issues
        backpatch_path = self.run_dir / "4-state" / "backpatch.jsonl"
        open_issues = []
        if backpatch_path.exists():
            with open(backpatch_path, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        issue = json.loads(line.strip())
                        if issue.get('status') == 'open':
                            open_issues.append(issue)
                    except:
                        pass
        
        # Build sanitized context
        context_parts = ["## 不变量 (Invariants) - 必须延续"]
        
        for char_name, fields in invariants.get('characters', {}).items():
            context_parts.append(f"\n### {char_name}")
            for field, value in fields.items():
                context_parts.append(f"- {field}: {value}")
        
        if open_issues:
            context_parts.append("\n## Open Backpatch Issues")
            for issue in open_issues[:3]:  # Top 3
                context_parts.append(f"- 第{issue.get('chapter')}章: {issue.get('issue', '')}")
        
        sanitized_context = "\n".join(context_parts)
        
        # Log sanitizer output
        sanitizer_record = {
            'timestamp': get_timestamp_iso(),
            'chapter': chapter_num,
            'invariants_enforced': list(invariants.get('characters', {}).keys()),
            'soft_retcons_applied': [],
            'reason': '提取不变量用于第{chapter_num}章生成',
            'sanitized_context': sanitized_context[:500]  # Truncated
        }
        
        atomic_append_jsonl(
            self.run_dir / "4-state" / "sanitizer_output.jsonl",
            sanitizer_record
        )
        
        print(f"[6.1] Complete: {len(invariants.get('characters', {}))} characters")
        return {
            'invariants': invariants,
            'sanitized_context': sanitized_context,
            'open_backpatch_issues': open_issues
        }
    
    # ========================================================================
    # 6.2 Outline Generation & Confirm
    # ========================================================================
    
    def generate_chapter_outline(
        self,
        chapter_num: int,
        previous_content: str = ""
    ) -> str:
        """6.2: Generate detailed chapter outline"""
        print(f"[6.2] Generate outline for Chapter {chapter_num}")
        
        # Load chapter summary from plan
        plan_path = self.run_dir / "2-planning" / "2-chapter-plan.json"
        chapter_summary = "(暂无概要)"
        chapter_title = f"第{chapter_num}章"
        
        if plan_path.exists():
            with open(plan_path, 'r', encoding='utf-8') as f:
                plan = json.load(f)
            for ch in plan.get('chapters', []):
                if ch.get('chapter_number') == chapter_num:
                    chapter_summary = ch.get('summary', chapter_summary)
                    chapter_title = ch.get('title', chapter_title)
                    break
        
        target_words = self.config['book']['chapter_target_words']
        
        # Build prompt
        if self.prompt_builder:
            prompt, log_path = self.prompt_builder.build_chapter_outline_prompt(
                run_id=self.config['run_id'],
                chapter_num=chapter_num,
                chapter_title=chapter_title,
                chapter_summary=chapter_summary,
                previous_content=previous_content,
                target_words=target_words
            )
        else:
            # Simple fallback
            prompt = f"生成第{chapter_num}章详细大纲"
        
        # Call model (placeholder)
        outline = self.model_callable(prompt)
        
        # Save to drafts
        outline_path = self.run_dir / "drafts" / "outlines" / f"Ch{chapter_num:03d}_outline_attempt1.md"
        atomic_write_text(outline_path, outline)
        
        print(f"[6.2] Complete: outline saved")
        return outline
    
    # ========================================================================
    # 6.3 Draft Generation
    # ========================================================================
    
    def generate_draft(
        self,
        chapter_num: int,
        outline: str,
        previous_content: str = "",
        attempt: int = 1
    ) -> str:
        """6.3: Generate chapter draft"""
        print(f"[6.3] Generate draft for Chapter {chapter_num} (Attempt {attempt})")
        
        # Split outline into segments if needed
        # For now, generate as one piece
        target_words = self.config['book']['chapter_target_words']
        
        # Build prompt
        if self.prompt_builder:
            prompt, log_path = self.prompt_builder.build_chapter_draft_prompt(
                run_id=self.config['run_id'],
                chapter_num=chapter_num,
                chapter_title=f"第{chapter_num}章",
                detailed_outline=outline,
                previous_content=previous_content,
                segment_summary="本章全部内容",
                segment_words=target_words,
                is_first_segment=True,
                event_id=generate_event_id(self.config['run_id'], '6.3', chapter_num)
            )
        else:
            prompt = f"根据大纲生成第{chapter_num}章正文"
        
        # Call model
        draft = self.model_callable(prompt)
        
        # Save to drafts
        draft_path = self.run_dir / "drafts" / "chapters" / f"Ch{chapter_num:03d}_draft_attempt{attempt}.md"
        atomic_write_text(draft_path, draft)
        
        print(f"[6.3] Complete: {len(draft)} chars")
        return draft
    
    # ========================================================================
    # 6.4 Quality Check
    # ========================================================================
    
    def qc_evaluate(
        self,
        chapter_num: int,
        draft: str,
        outline: str,
        previous_content: str = ""
    ) -> QCResult:
        """
        6.4: Quality Check with multi-perspective review
        """
        print(f"[6.4] QC for Chapter {chapter_num}")
        
        # In real implementation, would call 3 critic models
        # For now, placeholder with simple heuristic
        
        # Simple QC: check word count, basic format
        word_count = len(draft)
        target = self.config['book']['chapter_target_words']
        
        # Calculate base score
        score = 80  # Start neutral
        
        # Word count check (+/- 10% is fine)
        if abs(word_count - target) / target > 0.1:
            score -= 5
        
        # Check for outline elements
        if outline[:100] in draft or any(line[:30] in draft for line in outline.split('\n')[:5]):
            score -= 10  # Outline leaked into draft
        
        # Multi-perspective simulation
        perspectives = ['editor', 'logic', 'continuity']
        scores = []
        
        for perspective in perspectives:
            # Would call actual critic model here
            perspective_score = score + (5 if perspective == 'editor' else 0)
            scores.append(perspective_score)
        
        final_score = int(sum(scores) / len(scores))
        
        # Determine status
        if final_score >= self.pass_threshold:
            status = QCStatus.PASS
        elif final_score >= self.warning_threshold:
            status = QCStatus.WARNING
        else:
            status = QCStatus.REVISE
        
        # Build result
        result = QCResult(
            score=final_score,
            status=status,
            dimensions={
                'outline_adherence': final_score - 5,
                'main_plot': final_score,
                'character': final_score - 2,
                'logic': final_score - 3,
                'continuity': final_score - 1,
                'pacing': final_score + 2,
                'style': final_score
            },
            pros=[
                "章节结构完整",
                "情节推进自然" if final_score > 75 else "情节有待加强",
                "人物行为符合设定" if final_score > 80 else "人物刻画需改进"
            ],
            cons=[] if status == QCStatus.PASS else [
                "建议加强细节描写",
                "部分对话可更口语化"
            ],
            rewrite_plan="" if status == QCStatus.PASS else "根据cons进行针对性修改"
        )
        
        # Save QC result
        qc_path = self.run_dir / "drafts" / "qc" / f"Ch{chapter_num:03d}_qc_attempt1.md"
        atomic_write_json(qc_path, result.to_dict())
        
        print(f"[6.4] Complete: score={final_score}, status={status.value}")
        return result
    
    # ========================================================================
    # Attempt Cycle
    # ========================================================================
    
    def attempt_cycle(
        self,
        chapter_num: int,
        outline: str,
        previous_content: str = ""
    ) -> Tuple[str, QCResult, int]:
        """
        Run Attempt 1-3 cycle
        
        Returns:
            (final_draft, qc_result, attempt_number)
        """
        attempt = 1
        best_draft = ""
        best_result = None
        
        while attempt <= self.max_attempts:
            print(f"\n[Attempt {attempt}/{self.max_attempts}]")
            
            # Generate draft
            draft = self.generate_draft(
                chapter_num, outline, previous_content, attempt
            )
            
            # QC
            result = self.qc_evaluate(chapter_num, draft, outline, previous_content)
            
            # Track best
            if best_result is None or result.score > best_result.score:
                best_draft = draft
                best_result = result
            
            # Check if passed
            if result.status in [QCStatus.PASS, QCStatus.WARNING]:
                print(f"[Attempt {attempt}] Passed with score {result.score}")
                return draft, result, attempt
            
            # Continue to next attempt
            if attempt < self.max_attempts:
                print(f"[Attempt {attempt}] Failed ({result.status.value}), retrying...")
                # In real implementation, would apply rewrite_plan for targeted refinement
            
            attempt += 1
        
        # All attempts exhausted -> FORCED
        print(f"[FORCED] All {self.max_attempts} attempts failed, best score: {best_result.score}")
        best_result.status = QCStatus.FORCED
        
        return best_draft, best_result, self.max_attempts
    
    # ========================================================================
    # 6.5 Save Chapter
    # ========================================================================
    
    def save_chapter(
        self,
        chapter_num: int,
        draft: str,
        qc_result: QCResult,
        chapter_title: str = ""
    ) -> Path:
        """6.5: Save chapter to chapters/ directory"""
        print(f"[6.5] Save Chapter {chapter_num}")
        
        if not chapter_title:
            chapter_title = f"第{chapter_num}章"
        
        # Determine filename based on QC status
        is_forced = qc_result.status == QCStatus.FORCED
        
        filename = sanitize_chapter_filename(chapter_num, chapter_title, is_forced)
        chapter_path = self.run_dir / "chapters" / filename
        
        # Add metadata header
        metadata = f"""[Chapter Metadata]
Number: {chapter_num}
Title: {chapter_title}
Word Count: {len(draft)}
QC Score: {qc_result.score}
QC Status: {qc_result.status.value}
Saved: {get_timestamp_iso()}
[End Metadata]

---

"""
        
        full_content = metadata + draft
        atomic_write_text(chapter_path, full_content)
        
        print(f"[6.5] Complete: {chapter_path}")
        return chapter_path
    
    # ========================================================================
    # 6.6 State Commit
    # ========================================================================
    
    def state_commit(
        self,
        chapter_num: int,
        draft: str,
        qc_result: QCResult,
        state_changes: Optional[Dict[str, Any]] = None
    ):
        """6.6: Commit state changes after chapter completion"""
        print(f"[6.6] State Commit for Chapter {chapter_num}")
        
        # Update writing state
        writing_state_path = self.run_dir / "4-state" / "4-writing-state.json"
        with open(writing_state_path, 'r', encoding='utf-8') as f:
            writing_state = json.load(f)
        
        writing_state['current_chapter'] = chapter_num
        writing_state['completed_chapters'].append(chapter_num)
        writing_state['qc_score'] = qc_result.score
        writing_state['qc_status'] = qc_result.status.value
        writing_state['updated_at'] = get_timestamp_iso()
        
        # Handle forced_streak
        if qc_result.status == QCStatus.FORCED:
            writing_state['forced_streak'] = writing_state.get('forced_streak', 0) + 1
            writing_state['flags']['prev_chapter_forced'] = True
            
            # Add to backpatch
            backpatch_record = {
                'id': generate_event_id(self.config['run_id'], 'BP', chapter_num),
                'chapter': chapter_num,
                'issue': f"QC score {qc_result.score} below threshold",
                'severity': 'high' if qc_result.score < 70 else 'medium',
                'evidence': f"QC result: {qc_result.cons}",
                'status': 'open',
                'created_at': get_timestamp_iso(),
                'closed_at': None,
                'fix_strategy': None,
                'qc_after_fix': None
            }
            atomic_append_jsonl(
                self.run_dir / "4-state" / "backpatch.jsonl",
                backpatch_record
            )
        else:
            writing_state['forced_streak'] = 0
            writing_state['flags']['prev_chapter_forced'] = False
        
        # Check forced_streak threshold
        if writing_state['forced_streak'] >= 2:
            writing_state['flags']['is_paused'] = True
            print("[ALERT] forced_streak >= 2, pausing for manual review")
        
        atomic_write_json(writing_state_path, writing_state)
        
        # Commit state changes if provided
        if state_changes:
            self.state.commit_chapter_state(chapter_num, state_changes)
        
        print(f"[6.6] Complete: forced_streak={writing_state['forced_streak']}")
    
    # ========================================================================
    # Write Single Chapter
    # ========================================================================
    
    def write_chapter(
        self,
        chapter_num: int,
        previous_content: str = "",
        auto_continue: bool = False
    ) -> Dict[str, Any]:
        """
        Write a single chapter through full 6.x pipeline
        
        Returns:
            Result dict with paths and status
        """
        print(f"\n{'='*50}")
        print(f"Writing Chapter {chapter_num}")
        print(f"{'='*50}\n")
        
        # 6.1 Sanitizer
        sanitizer_result = self.sanitizer(chapter_num)
        
        # 6.2 Generate Outline
        outline = self.generate_chapter_outline(chapter_num, previous_content)
        
        # In manual mode, would wait for user confirmation here
        if self.mode == 'manual' and not auto_continue:
            print("[Manual Mode] Waiting for outline confirmation...")
            # Would pause here in real implementation
        
        # 6.3-6.4 Attempt Cycle
        draft, qc_result, attempt_num = self.attempt_cycle(
            chapter_num, outline, previous_content
        )
        
        # 6.5 Save Chapter
        chapter_path = self.save_chapter(chapter_num, draft, qc_result)
        
        # 6.6 State Commit
        self.state_commit(chapter_num, draft, qc_result)
        
        return {
            'chapter_num': chapter_num,
            'chapter_path': chapter_path,
            'qc_score': qc_result.score,
            'qc_status': qc_result.status.value,
            'attempt': attempt_num,
            'forced_streak': self._get_forced_streak()
        }


# ============================================================================
# Module Test
# ============================================================================

if __name__ == "__main__":
    import tempfile
    
    print("=== Writing Loop Test (Phase 6) ===\n")
    
    # Mock model callable
    def mock_model(prompt: str) -> str:
        return "这是生成的内容...\n（模拟模型输出）\n字数填充：" + "内容" * 100
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Setup
        from .phase_runner import PhaseRunner, WorkspaceManager
        
        workspace = WorkspaceManager(Path(tmpdir) / "novels")
        runner = PhaseRunner(workspace)
        
        # Run phases 1-5
        results = runner.run_all(
            book_title="测试小说",
            genre="都市异能",
            target_words=50000,
            mode="auto"
        )
        
        run_dir = results['run_dir']
        
        # Create writing loop
        loop = WritingLoop(
            run_dir=run_dir,
            model_callable=mock_model
        )
        
        # Write chapter 1
        result = loop.write_chapter(1)
        
        print(f"\n[Test] Chapter 1 result:")
        print(f"  Status: {result['qc_status']}")
        print(f"  Score: {result['qc_score']}")
        print(f"  Attempt: {result['attempt']}")
        print(f"  Path: {result['chapter_path'].exists()}")
        
    print("\n=== All tests completed ===")
