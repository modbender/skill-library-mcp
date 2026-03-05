"""
Fanfic Writer v2.0
Main package entry point
"""

# Import all modules for easy access
from .utils import (
    generate_run_id,
    generate_book_uid,
    generate_event_id,
    to_slug,
    sanitize_filename,
    create_directory_structure,
    get_timestamp_iso
)

from .atomic_io import (
    atomic_write_text,
    atomic_write_json,
    atomic_write_jsonl,
    atomic_append_jsonl,
    SnapshotManager,
    RollbackManager,
    StateCommit
)

from .workspace import WorkspaceManager, generate_intent_checklist
from .config_manager import ConfigManager, get_model_config, get_qc_config
from .state_manager import StateManager, StatePanel, CharactersPanel, PlotThreadsPanel
from .prompt_registry import PromptRegistry
from .prompt_assembly import PromptAssembler, PromptAuditor, ContextBuilder, PromptBuilder
from .price_table import PriceTableManager, CostBudgetManager
from .resume_manager import RunLock, ResumeManager, RuntimeConfigManager
from .phase_runner import PhaseRunner
from .writing_loop import WritingLoop, QCStatus, QCResult
from .safety_mechanisms import (
    BackpatchManager,
    AutoRescue,
    AutoAbortGuardrail,
    FinalIntegration
)

__version__ = "2.0.0"
__all__ = [
    'WorkspaceManager',
    'PhaseRunner',
    'WritingLoop',
    'StateManager',
    'PromptRegistry',
    'PriceTableManager',
    'ResumeManager',
    'FinalIntegration',
    'atomic_write_text',
    'atomic_write_json',
    'get_timestamp_iso',
    'generate_run_id',
]
