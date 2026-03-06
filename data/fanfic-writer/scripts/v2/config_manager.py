"""
Fanfic Writer v2.0 - Configuration Manager
Handles loading, validation, and updates of 0-book-config.json
"""
import os
import json
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime

from .atomic_io import atomic_write_json, atomic_append_jsonl
from .utils import get_timestamp_iso


# ============================================================================
# Configuration Schema
# ============================================================================

CONFIG_SCHEMA = {
    'version': {'type': str, 'required': True, 'default': '2.0.0'},
    'book': {
        'type': dict,
        'required': True,
        'fields': {
            'title': {'type': str, 'required': True},
            'title_slug': {'type': str, 'required': True},
            'book_uid': {'type': str, 'required': True},
            'subtitle': {'type': (str, type(None)), 'required': False, 'default': None},
            'genre': {'type': str, 'required': True},
            'subgenre': {'type': (str, type(None)), 'required': False, 'default': None},
            'target_word_count': {'type': int, 'required': True, 'min': 50000, 'max': 500000},
            'chapter_target_words': {'type': int, 'required': False, 'default': 2500, 'min': 1500, 'max': 8000},
            'language': {'type': str, 'required': False, 'default': 'zh'},
            'rating': {'type': str, 'required': False, 'default': 'PG-13'},
            'tone': {'type': str, 'required': False, 'default': '轻松'}
        }
    },
    'generation': {
        'type': dict,
        'required': True,
        'fields': {
            'model': {'type': str, 'required': True, 'default': 'nvidia/moonshotai/kimi-k2.5'},
            'temperature_outline': {'type': float, 'required': False, 'default': 0.8, 'min': 0.0, 'max': 1.0},
            'temperature_chapter': {'type': float, 'required': False, 'default': 0.75, 'min': 0.0, 'max': 1.0},
            'max_attempts': {'type': int, 'required': False, 'default': 3, 'min': 1, 'max': 5},
            'mode': {'type': str, 'required': True, 'default': 'manual', 'allowed': ['auto', 'manual']},
            'auto_threshold': {'type': int, 'required': False, 'default': 85, 'min': 0, 'max': 100},
            'auto_rescue_enabled': {'type': bool, 'required': False, 'default': True},
            'auto_rescue_max_rounds': {'type': int, 'required': False, 'default': 3, 'min': 1, 'max': 10}
        }
    },
    'qc': {
        'type': dict,
        'required': True,
        'fields': {
            'enabled': {'type': bool, 'required': False, 'default': True},
            'dimensions': {
                'type': list,
                'required': False,
                'default': ['outline_adherence', 'main_plot', 'character', 'logic', 'continuity', 'pacing', 'style']
            },
            'weights': {
                'type': dict,
                'required': False,
                'default': {
                    'outline_adherence': 20,
                    'main_plot': 15,
                    'character': 15,
                    'logic': 20,
                    'continuity': 10,
                    'pacing': 10,
                    'style': 10
                }
            },
            'pass_threshold': {'type': int, 'required': False, 'default': 85, 'min': 0, 'max': 100},
            'warning_threshold': {'type': int, 'required': False, 'default': 75, 'min': 0, 'max': 100}
        }
    },
    'backpatch': {
        'type': dict,
        'required': False,
        'default': {},
        'fields': {
            'frequency_chapters': {'type': int, 'required': False, 'default': 5, 'min': 1},
            'severity_threshold_for_block': {'type': str, 'required': False, 'default': 'high'}
        }
    },
    'time': {
        'type': dict,
        'required': False,
        'default': {},
        'fields': {
            'timezone_standard': {'type': str, 'required': False, 'default': 'Asia/Shanghai'},
            'timezone_offset': {'type': str, 'required': False, 'default': '+08:00'},
            'timestamp_format': {'type': str, 'required': False, 'default': 'ISO8601'}
        }
    },
    'run_id': {'type': str, 'required': True},
    'price_table_version': {'type': str, 'required': False, 'default': '1.0.0'},
    'created_at': {'type': str, 'required': True},
    'updated_at': {'type': str, 'required': True}
}


# ============================================================================
# Configuration Manager
# ============================================================================

class ConfigManager:
    """
    Manages book configuration lifecycle:
    - Load config from file
    - Validate against schema
    - Update with change tracking
    - Maintain update history
    """
    
    def __init__(self, run_dir: Path):
        """
        Initialize ConfigManager
        
        Args:
            run_dir: Path to run directory
        """
        self.run_dir = Path(run_dir)
        self.config_path = self.run_dir / "0-config" / "0-book-config.json"
        self._config: Optional[Dict[str, Any]] = None
        self._original_config: Optional[Dict[str, Any]] = None
    
    def load(self, force_reload: bool = False) -> Dict[str, Any]:
        """
        Load configuration from file
        
        Args:
            force_reload: Force reload even if already cached
            
        Returns:
            Configuration dictionary
            
        Raises:
            FileNotFoundError: If config file doesn't exist
            ValueError: If config is invalid JSON
        """
        if self._config is not None and not force_reload:
            return self._config
        
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            self._config = json.load(f)
        
        # Store original for change tracking
        self._original_config = json.loads(json.dumps(self._config))
        
        return self._config
    
    def validate(self, config: Optional[Dict[str, Any]] = None) -> Tuple[bool, List[str]]:
        """
        Validate configuration against schema
        
        Args:
            config: Config to validate (uses loaded config if None)
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        if config is None:
            config = self.load()
        
        errors = []
        
        def validate_field(field_name: str, field_spec: Dict, value: Any, path: str = ""):
            current_path = f"{path}.{field_name}" if path else field_name
            
            # Check required
            if field_spec.get('required', False) and value is None:
                errors.append(f"{current_path}: Required field is missing")
                return
            
            if value is None:
                return  # Optional field with None value
            
            # Check type
            expected_type = field_spec.get('type')
            if expected_type:
                if isinstance(expected_type, tuple):
                    if not isinstance(value, expected_type):
                        errors.append(f"{current_path}: Expected type {expected_type}, got {type(value)}")
                        return
                else:
                    if not isinstance(value, expected_type):
                        errors.append(f"{current_path}: Expected type {expected_type.__name__}, got {type(value).__name__}")
                        return
            
            # Check min/max for numbers
            if isinstance(value, (int, float)):
                if 'min' in field_spec and value < field_spec['min']:
                    errors.append(f"{current_path}: Value {value} is below minimum {field_spec['min']}")
                if 'max' in field_spec and value > field_spec['max']:
                    errors.append(f"{current_path}: Value {value} is above maximum {field_spec['max']}")
            
            # Check allowed values
            if 'allowed' in field_spec and value not in field_spec['allowed']:
                errors.append(f"{current_path}: Value '{value}' not in allowed values: {field_spec['allowed']}")
            
            # Recurse into nested dicts
            if isinstance(value, dict) and 'fields' in field_spec:
                for nested_name, nested_spec in field_spec['fields'].items():
                    nested_value = value.get(nested_name)
                    validate_field(nested_name, nested_spec, nested_value, current_path)
        
        # Validate all fields in schema
        for field_name, field_spec in CONFIG_SCHEMA.items():
            value = config.get(field_name)
            validate_field(field_name, field_spec, value)
        
        # Validate specific constraints
        # QC thresholds must make sense
        if 'qc' in config:
            qc = config['qc']
            if qc.get('warning_threshold', 75) >= qc.get('pass_threshold', 85):
                errors.append("qc.warning_threshold must be less than qc.pass_threshold")
        
        return len(errors) == 0, errors
    
    def update(self, updates: Dict[str, Any], reason: str = "manual_update") -> bool:
        """
        Update configuration with change tracking
        
        Args:
            updates: Dictionary of updates (supports nested paths like "book.title")
            reason: Reason for update (logged to user_interactions)
            
        Returns:
            True on success
        """
        config = self.load()
        
        # Apply updates
        for key, value in updates.items():
            if '.' in key:
                # Nested update
                parts = key.split('.')
                target = config
                for part in parts[:-1]:
                    if part not in target:
                        target[part] = {}
                    target = target[part]
                target[parts[-1]] = value
            else:
                config[key] = value
        
        # Validate
        is_valid, errors = self.validate(config)
        if not is_valid:
            print(f"[Config Error] Validation failed: {errors}")
            return False
        
        # Update timestamp
        config['updated_at'] = get_timestamp_iso()
        
        # Write atomically
        if not atomic_write_json(self.config_path, config):
            return False
        
        # Log to user_interactions
        self._log_config_change(updates, reason)
        
        # Update cache
        self._config = config
        self._original_config = json.loads(json.dumps(config))
        
        return True
    
    def _log_config_change(self, updates: Dict[str, Any], reason: str):
        """Log configuration change to user_interactions.jsonl"""
        user_interactions_path = self.run_dir / "4-state" / "user_interactions.jsonl"
        
        record = {
            'timestamp': get_timestamp_iso(),
            'type': 'setting_change',
            'trigger': reason,
            'affected_scope': 'global',
            'diff_summary': json.dumps(updates, ensure_ascii=False),
            'processed': True,
            'alignment_triggered': self._check_alignment_trigger(updates)
        }
        
        atomic_append_jsonl(user_interactions_path, record)
    
    def _check_alignment_trigger(self, updates: Dict[str, Any]) -> bool:
        """Check if update should trigger alignment check"""
        # Key fields that affect book direction
        alignment_fields = [
            'book.genre', 'book.subgenre', 'book.tone', 'book.target_word_count'
        ]
        
        for key in updates.keys():
            if any(key.startswith(field) or field.startswith(key) for field in alignment_fields):
                return True
        
        return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value (supports nested keys like "book.title")
        """
        config = self.load()
        
        if '.' in key:
            parts = key.split('.')
            value = config
            for part in parts:
                if isinstance(value, dict) and part in value:
                    value = value[part]
                else:
                    return default
            return value
        
        return config.get(key, default)
    
    def has_changed(self) -> bool:
        """Check if config has unsaved changes"""
        if self._config is None or self._original_config is None:
            return False
        return json.dumps(self._config, sort_keys=True) != json.dumps(self._original_config, sort_keys=True)
    
    def get_price_table_path(self) -> Path:
        """Get path to price table file"""
        return self.run_dir / "0-config" / "price-table.json"
    
    def get_style_guide_path(self) -> Path:
        """Get path to style guide"""
        return self.run_dir / "0-config" / "style_guide.md"
    
    def get_intent_checklist_path(self) -> Path:
        """Get path to intent checklist"""
        return self.run_dir / "0-config" / "intent_checklist.json"


# ============================================================================
# Configuration Helpers
# ============================================================================

def get_model_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """Extract model configuration from book config"""
    gen = config.get('generation', {})
    return {
        'model': gen.get('model', 'nvidia/moonshotai/kimi-k2.5'),
        'temperature_outline': gen.get('temperature_outline', 0.8),
        'temperature_chapter': gen.get('temperature_chapter', 0.75),
        'max_attempts': gen.get('max_attempts', 3),
        'mode': gen.get('mode', 'manual'),
        'auto_threshold': gen.get('auto_threshold', 85)
    }


def get_qc_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """Extract QC configuration from book config"""
    qc = config.get('qc', {})
    return {
        'enabled': qc.get('enabled', True),
        'dimensions': qc.get('dimensions', ['outline_adherence', 'main_plot', 'character', 
                                            'logic', 'continuity', 'pacing', 'style']),
        'weights': qc.get('weights', {
            'outline_adherence': 20,
            'main_plot': 15,
            'character': 15,
            'logic': 20,
            'continuity': 10,
            'pacing': 10,
            'style': 10
        }),
        'pass_threshold': qc.get('pass_threshold', 85),
        'warning_threshold': qc.get('warning_threshold', 75)
    }


def get_book_metadata(config: Dict[str, Any]) -> Dict[str, Any]:
    """Extract book metadata from config"""
    book = config.get('book', {})
    return {
        'title': book.get('title', 'Untitled'),
        'title_slug': book.get('title_slug', 'untitled'),
        'book_uid': book.get('book_uid', ''),
        'genre': book.get('genre', ''),
        'subgenre': book.get('subgenre', ''),
        'target_word_count': book.get('target_word_count', 100000),
        'chapter_target_words': book.get('chapter_target_words', 2500),
        'language': book.get('language', 'zh'),
        'tone': book.get('tone', '轻松')
    }


# ============================================================================
# Module Test
# ============================================================================

if __name__ == "__main__":
    import tempfile
    
    print("=== Config Manager Test ===\n")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        run_dir = Path(tmpdir) / "test_run"
        config_dir = run_dir / "0-config"
        config_dir.mkdir(parents=True)
        state_dir = run_dir / "4-state"
        state_dir.mkdir(parents=True)
        
        # Create test config
        test_config = {
            'version': '2.0.0',
            'book': {
                'title': '阴间外卖',
                'title_slug': 'yin_jian_wai_mai',
                'book_uid': 'a1b2c3d4',
                'genre': '都市灵异',
                'target_word_count': 250000,
                'chapter_target_words': 2500
            },
            'generation': {
                'model': 'nvidia/moonshotai/kimi-k2.5',
                'mode': 'manual',
                'max_attempts': 3
            },
            'qc': {
                'enabled': True,
                'pass_threshold': 85,
                'warning_threshold': 75
            },
            'run_id': '20260215_224500_ABC123',
            'created_at': '2026-02-15T22:45:00+08:00',
            'updated_at': '2026-02-15T22:45:00+08:00'
        }
        
        config_path = config_dir / "0-book-config.json"
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(test_config, f, indent=2, ensure_ascii=False)
        
        # Test load
        mgr = ConfigManager(run_dir)
        config = mgr.load()
        print(f"[Test] Load config: {'PASS' if config['book']['title'] == '阴间外卖' else 'FAIL'}")
        
        # Test validate
        is_valid, errors = mgr.validate()
        print(f"[Test] Validate config: {'PASS' if is_valid else 'FAIL'}")
        if errors:
            for err in errors:
                print(f"  Error: {err}")
        
        # Test get
        title = mgr.get('book.title')
        print(f"[Test] Get nested value: {'PASS' if title == '阴间外卖' else 'FAIL'}")
        
        # Test update
        success = mgr.update({'book.tone': '暗黑'}, reason="改基调")
        print(f"[Test] Update config: {'PASS' if success else 'FAIL'}")
        
        # Verify update
        config = mgr.load(force_reload=True)
        print(f"[Test] Verify update: {'PASS' if config['book']['tone'] == '暗黑' else 'FAIL'}")
        
        # Test helpers
        model_cfg = get_model_config(config)
        print(f"[Test] Model config: {model_cfg['model']}")
        
        qc_cfg = get_qc_config(config)
        print(f"[Test] QC pass threshold: {qc_cfg['pass_threshold']}")
        
        metadata = get_book_metadata(config)
        print(f"[Test] Book title: {metadata['title']}")
        
    print("\n=== All tests completed ===")
