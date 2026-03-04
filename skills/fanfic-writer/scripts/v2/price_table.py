"""
Fanfic Writer v2.0 - Price Table Manager
Multi-platform pricing management with version control
"""
import json
import os
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime

from .atomic_io import atomic_write_json, atomic_append_jsonl
from .utils import get_timestamp_iso


# Default pricing table (RMB per 1M tokens)
DEFAULT_PRICE_TABLE = {
    "version": "1.0.0",
    "updated_at": "2026-02-16T00:00:00+08:00",
    "source": "default",
    "usd_cny_rate": 6.90,
    "currency": "CNY",
    "models": [
        {
            "key": "moonshot:kimi-k2.5:standard:<=128k:off:none",
            "provider": "moonshot",
            "model_id": "kimi-k2.5",
            "model_name": "Kimi K2.5",
            "tier": "standard",
            "context_bucket": "<=128k",
            "thinking_mode": "off",
            "cache_mode": "none",
            "currency": "CNY",
            "input_rate": 4.14,
            "output_rate": 20.70,
            "cached_input_rate": 0.69,
            "cache_write_rate": 0.0
        },
        {
            "key": "nvidia:moonshotai/kimi-k2.5:standard:<=128k:off:none",
            "provider": "nvidia",
            "model_id": "moonshotai/kimi-k2.5",
            "model_name": "Kimi 2.5 (NVIDIA)",
            "tier": "standard",
            "context_bucket": "<=128k",
            "thinking_mode": "off",
            "cache_mode": "none",
            "currency": "USD",
            "input_rate": 0.60,  # USD per 1M
            "output_rate": 3.00,
            "cached_input_rate": 0.0,
            "cache_write_rate": 0.0
        },
        {
            "key": "zhipu:glm-5:standard:<=32k:off:none",
            "provider": "zhipu",
            "model_id": "glm-5",
            "model_name": "GLM-5",
            "tier": "standard",
            "context_bucket": "<=32k",
            "thinking_mode": "off",
            "cache_mode": "none",
            "currency": "CNY",
            "input_rate": 4.00,
            "output_rate": 18.00,
            "cached_input_rate": 0.0,
            "cache_write_rate": 0.0
        },
        {
            "key": "zhipu:glm-5:standard:>=32k:off:none",
            "provider": "zhipu",
            "model_id": "glm-5",
            "model_name": "GLM-5 (Long)",
            "tier": "standard",
            "context_bucket": ">=32k",
            "thinking_mode": "off",
            "cache_mode": "none",
            "currency": "CNY",
            "input_rate": 6.00,
            "output_rate": 22.00,
            "cached_input_rate": 0.0,
            "cache_write_rate": 0.0
        },
        {
            "key": "google:gemini-3-flash-preview:standard:<=128k:off:none",
            "provider": "google",
            "model_id": "gemini-3-flash-preview",
            "model_name": "Gemini 3 Flash",
            "tier": "standard",
            "context_bucket": "<=128k",
            "thinking_mode": "off",
            "cache_mode": "none",
            "currency": "USD",
            "input_rate": 0.35,
            "output_rate": 0.70,
            "cached_input_rate": 0.0,
            "cache_write_rate": 0.0
        },
        {
            "key": "openai:gpt-5.2:standard:<=128k:off:none",
            "provider": "openai",
            "model_id": "gpt-5.2",
            "model_name": "GPT-5.2",
            "tier": "standard",
            "context_bucket": "<=128k",
            "thinking_mode": "off",
            "cache_mode": "none",
            "currency": "USD",
            "input_rate": 1.75,
            "output_rate": 14.00,
            "cached_input_rate": 0.0,
            "cache_write_rate": 0.0
        }
    ]
}


class PriceTableManager:
    """
    Manages pricing table with version control
    Supports multi-platform model selection and cost calculation
    """
    
    def __init__(self, run_dir: Path):
        self.run_dir = Path(run_dir)
        self.config_path = self.run_dir / "0-config" / "price-table.json"
        self.cost_report_path = self.run_dir / "logs" / "cost-report.jsonl"
        self._price_table: Optional[Dict[str, Any]] = None
    
    def initialize(self, usd_cny_rate: float = 6.90) -> bool:
        """Initialize default price table"""
        table = DEFAULT_PRICE_TABLE.copy()
        table['usd_cny_rate'] = usd_cny_rate
        table['updated_at'] = get_timestamp_iso()
        
        return atomic_write_json(self.config_path, table)
    
    def load(self) -> Dict[str, Any]:
        """Load price table"""
        if self._price_table is not None:
            return self._price_table
        
        if not self.config_path.exists():
            self.initialize()
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            self._price_table = json.load(f)
        
        return self._price_table
    
    def update_price_table(
        self,
        new_table: Dict[str, Any],
        keep_old: bool = True
    ) -> bool:
        """
        Update price table with hot-swap support
        
        Args:
            new_table: New price table
            keep_old: If True, backup old version
        """
        current = self.load()
        
        # Backup old version
        if keep_old:
            backup_name = f"price-table-v{current['version']}.json"
            backup_path = self.config_path.parent / backup_name
            atomic_write_json(backup_path, current)
        
        # Update with new version
        new_table['previous_version'] = current['version']
        new_table['updated_at'] = get_timestamp_iso()
        
        # Log the update
        self._log_price_update(current['version'], new_table['version'])
        
        self._price_table = new_table
        return atomic_write_json(self.config_path, new_table)
    
    def _log_price_update(self, old_version: str, new_version: str):
        """Log price table update to cost-report"""
        record = {
            'timestamp': get_timestamp_iso(),
            'event': 'price_table_update',
            'old_version': old_version,
            'new_version': new_version,
            'event_id': f"CP-UPDATE-{get_timestamp_iso()}"
        }
        atomic_append_jsonl(self.cost_report_path, record)
    
    def find_price_item(
        self,
        provider: str,
        model_id: str,
        tier: str = "standard",
        context_bucket: str = "<=128k",
        thinking_mode: str = "off",
        cache_mode: str = "none"
    ) -> Optional[Dict[str, Any]]:
        """
        Find pricing item with fallback matching
        
        Matching order (strict to loose):
        1. Exact match
        2. cache_mode=none
        3. thinking_mode=off
        4. closest context_bucket
        """
        table = self.load()
        models = table.get('models', [])
        
        # Build key components
        exact_key = f"{provider}:{model_id}:{tier}:{context_bucket}:{thinking_mode}:{cache_mode}"
        
        # Try exact match
        for model in models:
            if model.get('key') == exact_key:
                return model
        
        # Try with cache_mode=none
        if cache_mode != "none":
            for model in models:
                if model.get('provider') == provider and \
                   model.get('model_id') == model_id and \
                   model.get('tier') == tier and \
                   model.get('context_bucket') == context_bucket and \
                   model.get('thinking_mode') == thinking_mode and \
                   model.get('cache_mode') == "none":
                    return model
        
        # Try with thinking_mode=off
        if thinking_mode != "off":
            for model in models:
                if model.get('provider') == provider and \
                   model.get('model_id') == model_id and \
                   model.get('tier') == tier and \
                   model.get('context_bucket') == context_bucket and \
                   model.get('thinking_mode') == "off":
                    return model
        
        # Try closest context_bucket (use larger one to avoid underestimating)
        context_buckets = ["<=32k", "<=128k", ">128k"]
        current_idx = context_buckets.index(context_bucket) if context_bucket in context_buckets else 1
        
        for idx in range(current_idx, len(context_buckets)):
            bucket = context_buckets[idx]
            for model in models:
                if model.get('provider') == provider and \
                   model.get('model_id') == model_id and \
                   model.get('tier') == tier and \
                   model.get('context_bucket') == bucket:
                    return model
        
        # No match found - blocking error
        raise RuntimeError(
            f"No pricing match for {provider}:{model_id}:{tier}:{context_bucket}. "
            "Please update price-table.json"
        )
    
    def calculate_cost(
        self,
        provider: str,
        model_id: str,
        prompt_tokens: int,
        completion_tokens: int,
        cached_prompt_tokens: int = 0,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Calculate cost for a model call
        
        Returns cost in both original currency and RMB
        """
        table = self.load()
        usd_cny_rate = table.get('usd_cny_rate', 6.90)
        
        # Find price item
        price_item = self.find_price_item(provider, model_id, **kwargs)
        
        currency = price_item.get('currency', 'USD')
        input_rate = price_item.get('input_rate', 0)
        output_rate = price_item.get('output_rate', 0)
        cached_rate = price_item.get('cached_input_rate', 0)
        
        # Calculate cost
        prompt_cost = (prompt_tokens / 1_000_000) * input_rate
        cached_cost = (cached_prompt_tokens / 1_000_000) * cached_rate
        completion_cost = (completion_tokens / 1_000_000) * output_rate
        
        total_cost = prompt_cost + cached_cost + completion_cost
        
        # Convert to RMB if needed
        if currency == 'USD':
            cost_rmb = total_cost * usd_cny_rate
        else:
            cost_rmb = total_cost
        
        return {
            'currency': currency,
            'cost_original': total_cost,
            'cost_rmb': cost_rmb,
            'usd_cny_rate': usd_cny_rate,
            'price_table_version': table['version'],
            'breakdown': {
                'prompt_tokens': prompt_tokens,
                'prompt_cost': prompt_cost,
                'cached_tokens': cached_prompt_tokens,
                'cached_cost': cached_cost,
                'completion_tokens': completion_tokens,
                'completion_cost': completion_cost
            }
        }
    
    def log_cost(
        self,
        event_id: str,
        phase: str,
        chapter: Optional[int],
        event: str,
        provider: str,
        model_id: str,
        prompt_tokens: int,
        completion_tokens: int,
        cached_tokens: int = 0,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Log cost to cost-report.jsonl
        
        Returns the logged record
        """
        cost_result = self.calculate_cost(
            provider, model_id,
            prompt_tokens, completion_tokens, cached_tokens,
            **kwargs
        )
        
        record = {
            'timestamp': get_timestamp_iso(),
            'event_id': event_id,
            'run_id': self.run_dir.name,
            'phase': phase,
            'chapter': chapter,
            'event': event,
            'provider': provider,
            'model_id': model_id,
            'prompt_tokens': prompt_tokens,
            'completion_tokens': completion_tokens,
            'cached_prompt_tokens': cached_tokens,
            'total_tokens': prompt_tokens + completion_tokens,
            'currency': cost_result['currency'],
            'cost_original': round(cost_result['cost_original'], 6),
            'cost_rmb': round(cost_result['cost_rmb'], 6),
            'usd_cny_rate': cost_result['usd_cny_rate'],
            'price_table_version': cost_result['price_table_version'],
            'pricing_source': 'price-table.json'
        }
        
        atomic_append_jsonl(self.cost_report_path, record)
        
        return record
    
    def get_total_cost(self) -> Dict[str, float]:
        """Get total cost for this run"""
        if not self.cost_report_path.exists():
            return {'total_rmb': 0.0, 'total_usd': 0.0, 'record_count': 0}
        
        total_rmb = 0.0
        total_usd = 0.0
        record_count = 0
        
        with open(self.cost_report_path, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    record = json.loads(line.strip())
                    if record.get('currency') == 'USD':
                        total_usd += record.get('cost_original', 0)
                    total_rmb += record.get('cost_rmb', 0)
                    record_count += 1
                except:
                    pass
        
        return {
            'total_rmb': round(total_rmb, 4),
            'total_usd': round(total_usd, 4),
            'record_count': record_count
        }
    
    def get_model_alias_mapping(self, alias: str) -> Optional[str]:
        """Map old aliases to current model_ids"""
        alias_map = {
            'qwen3.5': 'qwen3-max',
            'qwen-3.5': 'qwen3-max',
            'kimi': 'kimi-k2.5',
            'gpt4': 'gpt-5.2',
            'claude': 'claude-sonnet-4.5'
        }
        return alias_map.get(alias.lower())


# ============================================================================
# Cost Budget Manager
# ============================================================================

class CostBudgetManager:
    """
    Manages cost budget and alerts
    """
    
    def __init__(self, run_dir: Path, price_manager: PriceTableManager):
        self.run_dir = Path(run_dir)
        self.price_manager = price_manager
        self.budget_file = self.run_dir / "0-config" / "cost-budget.json"
    
    def set_budget(self, max_rmb: float, warning_threshold: float = 0.8) -> bool:
        """Set cost budget"""
        budget = {
            'max_rmb': max_rmb,
            'warning_threshold': warning_threshold,
            'created_at': get_timestamp_iso()
        }
        return atomic_write_json(self.budget_file, budget)
    
    def check_budget(self) -> Dict[str, Any]:
        """Check current spending against budget"""
        if not self.budget_file.exists():
            return {'has_budget': False}
        
        with open(self.budget_file, 'r', encoding='utf-8') as f:
            budget = json.load(f)
        
        total = self.price_manager.get_total_cost()
        spent = total['total_rmb']
        max_rmb = budget.get('max_rmb', float('inf'))
        warning_threshold = budget.get('warning_threshold', 0.8)
        
        ratio = spent / max_rmb if max_rmb > 0 else 0
        
        return {
            'has_budget': True,
            'spent_rmb': spent,
            'max_rmb': max_rmb,
            'remaining_rmb': max_rmb - spent,
            'ratio': ratio,
            'status': 'exceeded' if ratio >= 1.0 else 'warning' if ratio >= warning_threshold else 'ok'
        }


# ============================================================================
# Module Test
# ============================================================================

if __name__ == "__main__":
    import tempfile
    
    print("=== Price Table Manager Test ===\n")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        run_dir = Path(tmpdir) / "run"
        run_dir.mkdir()
        config_dir = run_dir / "0-config"
        config_dir.mkdir()
        logs_dir = run_dir / "logs"
        logs_dir.mkdir()
        
        # Test initialization
        mgr = PriceTableManager(run_dir)
        mgr.initialize(usd_cny_rate=7.0)
        print("[Test] Price table initialized: PASS")
        
        # Test load
        table = mgr.load()
        print(f"[Test] Loaded version: {table['version']}")
        print(f"[Test] USD/CNY rate: {table['usd_cny_rate']}")
        
        # Test find price
        item = mgr.find_price_item('moonshot', 'kimi-k2.5')
        print(f"[Test] Found price item: {item['model_name']}")
        print(f"  Input: {item['input_rate']} CNY/1M")
        print(f"  Output: {item['output_rate']} CNY/1M")
        
        # Test cost calculation
        cost = mgr.calculate_cost(
            'moonshot', 'kimi-k2.5',
            prompt_tokens=1000,
            completion_tokens=2000
        )
        print(f"\n[Test] Cost calculation:")
        print(f"  Currency: {cost['currency']}")
        print(f"  Original: {cost['cost_original']:.6f}")
        print(f"  RMB: {cost['cost_rmb']:.6f}")
        
        # Test cost logging
        record = mgr.log_cost(
            event_id='test-001',
            phase='6.3',
            chapter=1,
            event='draft_generate',
            provider='moonshot',
            model_id='kimi-k2.5',
            prompt_tokens=1000,
            completion_tokens=2000
        )
        print(f"\n[Test] Cost logged: {record['event_id']}")
        
        # Test total cost
        total = mgr.get_total_cost()
        print(f"\n[Test] Total cost: {total['total_rmb']:.4f} RMB")
        
        # Test budget
        budget_mgr = CostBudgetManager(run_dir, mgr)
        budget_mgr.set_budget(max_rmb=100.0)
        status = budget_mgr.check_budget()
        print(f"\n[Test] Budget status: {status['status']}")
        
    print("\n=== All tests completed ===")
