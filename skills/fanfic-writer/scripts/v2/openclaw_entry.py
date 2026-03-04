"""
Fanfic Writer v2.1 - OpenClaw Skill Entry Point
This function is called by OpenClaw to run the skill
"""
import json
from pathlib import Path
from typing import Dict, Any, Optional

# Import all modules
from .workspace import WorkspaceManager
from .phase_runner import PhaseRunner
from .writing_loop import WritingLoop
from .safety_mechanisms import FinalIntegration, BackpatchManager
from .resume_manager import RunLock, ResumeManager, RuntimeConfigManager
from .price_table import PriceTableManager, CostBudgetManager
from .config_manager import ConfigManager
from .state_manager import StateManager
from .atomic_io import atomic_write_json, atomic_write_text
from .utils import get_timestamp_iso


def run_skill(
    # Book configuration
    book_config: Optional[Dict[str, Any]] = None,
    book_title: Optional[str] = None,
    genre: Optional[str] = None,
    target_words: int = 100000,
    
    # Writing mode - "manual" requires confirmation at each phase
    mode: str = "manual",  # "manual" or "auto"
    
    # Paths
    workspace_root: Optional[str] = None,
    run_dir: Optional[str] = None,
    
    # Resume
    resume: str = "off",  # "off", "auto", "force"
    
    # Budget
    budget: Optional[float] = None,
    
    # Chapters to write
    chapters: Optional[str] = None,  # "1" or "1-5"
    
    # OpenClaw context - provides the model automatically!
    oc_context: Optional[Dict[str, Any]] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Main entry point for OpenClaw to call this skill.
    
    This function handles the complete workflow:
    - Phase 1-5: Initialization (with human confirmation required)
    - Phase 6: Writing loop (with human confirmation between chapters)
    - Phase 7-9: Backpatch and finalization
    
    Args:
        book_config: Complete book configuration dict
        book_title: Book title
        genre: Genre (都市/玄幻/仙侠/etc)
        target_words: Target word count
        mode: "manual" or "auto"
        model: Model to use
        api_key: API key for model
        workspace_root: Where to store novels
        run_dir: Specific run directory (for resume)
        resume: "off", "auto", "force"
        budget: Cost budget in RMB
        chapters: Chapter range "1-10" or single "5"
        oc_context: OpenClaw context (provides model calling)
        
    Returns:
        Dict with status and paths
    """
    results = {
        "status": "pending",
        "phase": None,
        "message": "",
        "run_dir": None,
        "chapters_written": [],
        "errors": []
    }
    
    # Get workspace root
    if workspace_root:
        base_dir = Path(workspace_root)
    else:
        base_dir = Path.home() / ".openclaw" / "novels"
    
    # Determine mode
    # In manual mode, require human confirmation at each phase
    # In auto mode, run automatically but still save for review
    
    try:
        # Initialize workspace
        workspace = WorkspaceManager(base_dir)
        
        # Handle resume
        if resume != "off" and run_dir:
            # Resume existing run
            run_dir = Path(run_dir)
            resume_mgr = ResumeManager(run_dir)
            can_resume, reason, resume_info = resume_mgr.can_resume(mode=resume)
            
            if can_resume:
                resume_mgr.resume(resume_info)
                results["message"] = f"Resumed at chapter {resume_info['resume_point']['chapter']}"
            elif resume == "force":
                results["message"] = f"Force resume: {reason}"
            else:
                results["message"] = f"Cannot resume: {reason}, starting new run"
        
        # Get model callable from OpenClaw context
        # The model is whatever OpenClaw is currently using - no hardcoding!
        def call_model(prompt: str, **model_kwargs) -> str:
            """
            Call model via OpenClaw context.
            
            IMPORTANT: This uses OpenClaw's current model automatically.
            No model configuration needed in the skill itself.
            """
            if oc_context and hasattr(oc_context, 'model_call'):
                # OpenClaw provides model_call method
                return oc_context.model_call(prompt, **model_kwargs)
            elif oc_context and 'model_callable' in oc_context:
                # Or as a callable in context
                return oc_context['model_callable'](prompt, **model_kwargs)
            elif oc_context and 'generate' in oc_context:
                # Alternative method name
                return oc_context['generate'](prompt, **model_kwargs)
            else:
                # Fallback: use prompt as-is (for debugging)
                return f"[Please configure model in OpenClaw - prompt length: {len(prompt)} chars]"
        
        # If no book config, we need to create one
        if not book_config and not book_title:
            results["status"] = "awaiting_config"
            results["message"] = "Please provide book_title and genre"
            return results
        
        # Create book config if not provided
        # Note: model is provided by OpenClaw automatically, not hardcoded in skill
        if not book_config:
            book_config = {
                "version": "2.1.0",
                "book": {
                    "title": book_title,
                    "genre": genre,
                    "target_word_count": target_words,
                },
                "generation": {
                    "mode": mode
                }
            }
        
        # Phase 1-5: Initialization (always require human confirmation in design)
        # For OpenClaw, we check if mode is "auto" or "manual"
        # In manual mode, we return the generated files for review
        
        if not run_dir:
            # Create new book
            runner = PhaseRunner(workspace)
            
            # Phase 1: Initialize
            results["phase"] = "1_init"
            run_path, book_uid, run_id = runner.phase1_initialize(
                book_title=book_config.get("book", {}).get("title", "未命名"),
                genre=book_config.get("book", {}).get("genre", "都市"),
                target_words=book_config.get("book", {}).get("target_word_count", 100000),
                mode=mode
            )
            results["run_dir"] = str(run_path)
            
            # Phase 2-5 would be here but require human confirmation
            # For now, return to get confirmation
            
            results["status"] = "awaiting_confirmation"
            results["message"] = f"Phase 1 complete. Please confirm to continue to Phase 2."
            return results
        
        # If we have run_dir, continue with writing
        run_dir = Path(run_dir)
        
        # Acquire lock
        run_lock = RunLock(run_dir)
        lock_success, lock_error = run_lock.acquire(mode=mode)
        if not lock_success:
            results["status"] = "error"
            results["errors"].append(f"Cannot acquire lock: {lock_error}")
            return results
        
        try:
            # Get current state
            state_path = run_dir / "4-state" / "4-writing-state.json"
            with open(state_path, 'r', encoding='utf-8') as f:
                state = json.load(f)
            
            current_chapter = state.get('current_chapter', 0)
            
            # Determine chapters to write
            if chapters:
                if '-' in chapters:
                    start, end = map(int, chapters.split('-'))
                    chapter_list = list(range(start, end + 1))
                else:
                    chapter_list = [int(chapters)]
            else:
                chapter_list = [current_chapter + 1]
            
            # Create writing loop with real model
            loop = WritingLoop(
                run_dir=run_dir,
                model_callable=call_model,
                config_manager=ConfigManager(run_dir),
                state_manager=StateManager(run_dir)
            )
            
            # Write chapters
            for ch in chapter_list:
                # Check if paused
                if state.get('flags', {}).get('is_paused'):
                    results["message"] = f"Paused at chapter {ch}"
                    break
                
                result = loop.write_chapter(ch)
                
                results["chapters_written"].append({
                    "chapter": ch,
                    "status": result.get('qc_status'),
                    "score": result.get('qc_score')
                })
                
                # In manual mode, require confirmation after each chapter
                if mode == "manual":
                    results["status"] = "awaiting_confirmation"
                    results["message"] = f"Chapter {ch} complete. Score: {result.get('qc_score')}. Confirm to continue?"
                    return results
            
            results["status"] = "complete"
            results["message"] = f"Wrote {len(results['chapters_written'])} chapters"
            
        finally:
            run_lock.release()
    
    except Exception as e:
        results["status"] = "error"
        results["errors"].append(str(e))
        results["message"] = f"Error: {str(e)}"
    
    return results


def get_required_confirmations(phase: str) -> list:
    """
    Return list of items that require human confirmation for a given phase
    
    This helps OpenClaw know what to ask the user
    """
    confirmations = {
        "1_init": [
            "书名 (book_title)",
            "类型 (genre)", 
            "目标字数 (target_words)",
            "存放目录 (workspace_root)"
        ],
        "2_style": [
            "风格指南 (style_guide.md)"
        ],
        "3_outline": [
            "主线大纲 (main_outline.md)"
        ],
        "4_planning": [
            "章节规划 (chapter_plan.json)"
        ],
        "5_world": [
            "世界观设定 (world_building.md)"
        ],
        "6_write": [
            "每章正文生成后确认",
            "每章评分确认"
        ],
        "7_backpatch": [
            "回补修复确认"
        ],
        "8_merge": [
            "合并后确认"
        ],
        "9_final": [
            "最终检查报告确认"
        ]
    }
    
    return confirmations.get(phase, [])
