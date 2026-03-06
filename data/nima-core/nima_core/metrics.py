"""NIMA metrics - lightweight thread-safe metrics collector."""

import time
import threading
from typing import Dict, Any, Optional


# Pre-defined metric constants for key operations
RECALL_QUERY_MS = 'recall_query_ms'
RECALL_CACHE_HITS = 'recall_cache_hits'
AFFECT_UPDATE_MS = 'affect_update_ms'
MEMORY_STORE_MS = 'memory_store_ms'


class MetricsCollector:
    """Lightweight thread-safe metrics collector with counters, timings, and gauges."""
    
    _instance = None
    _lock = threading.Lock()
    
    def __init__(self):
        raise RuntimeError("Use get_instance() or get_metrics() to get MetricsCollector singleton")
    
    @classmethod
    def get_instance(cls):
        """Get the singleton instance of MetricsCollector."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls.__new__(cls)
                    cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize the metrics storage."""
        self._metrics = {}  # {name: {'count': int, 'sum': float, 'values': [], 'type': str, 'tags': {}}}
        self._lock = threading.Lock()
    
    def _make_key(self, name: str, tags: Optional[Dict[str, str]] = None) -> str:
        """Create a unique key for a metric based on name and tags."""
        if not tags:
            return name
        tag_str = ','.join(f'{k}={v}' for k, v in sorted(tags.items()))
        return f'{name}#{tag_str}'
    
    def increment(self, name: str, value: int = 1, tags: Optional[Dict[str, str]] = None):
        """
        Increment a counter metric.
        
        Args:
            name: The metric name
            value: The value to add (default 1)
            tags: Optional tags for the metric
        """
        key = self._make_key(name, tags)
        with self._lock:
            if key not in self._metrics:
                self._metrics[key] = {'count': 0, 'sum': 0, 'type': 'counter', 'base_name': name, 'tags': tags or {}}
            self._metrics[key]['count'] += value
    
    def timing(self, name: str, duration_ms: float, tags: Optional[Dict[str, str]] = None):
        """
        Record a timing metric in milliseconds.
        
        Args:
            name: The metric name
            duration_ms: Duration in milliseconds
            tags: Optional tags for the metric
        """
        key = self._make_key(name, tags)
        with self._lock:
            if key not in self._metrics:
                self._metrics[key] = {'count': 0, 'sum': 0, 'values': [], 'type': 'timing', 'base_name': name, 'tags': tags or {}}
            self._metrics[key]['count'] += 1
            self._metrics[key]['sum'] += duration_ms
            # Keep last 100 values for calculating avg/min/max
            self._metrics[key]['values'].append(duration_ms)
            if len(self._metrics[key]['values']) > 100:
                self._metrics[key]['values'].pop(0)
    
    def gauge(self, name: str, value: float, tags: Optional[Dict[str, str]] = None):
        """
        Set a gauge metric (point-in-time value).
        
        Args:
            name: The metric name
            value: The current value
            tags: Optional tags for the metric
        """
        key = self._make_key(name, tags)
        with self._lock:
            if key not in self._metrics:
                self._metrics[key] = {'value': 0, 'type': 'gauge', 'base_name': name, 'tags': tags or {}}
            self._metrics[key]['value'] = value
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get all metrics as a dictionary.
        
        Returns:
            Dictionary containing all metrics with their values
        """
        with self._lock:
            summary = {}
            for key, data in self._metrics.items():
                # Use full key (including tags) to avoid overwrites
                tags = data['tags']
                
                if data['type'] == 'counter':
                    summary[key] = {
                        'type': 'counter',
                        'value': data['count'],
                        'tags': tags if tags else None
                    }
                elif data['type'] == 'timing':
                    values = data['values']
                    summary[key] = {
                        'type': 'timing',
                        'count': data['count'],
                        'sum_ms': data['sum'],
                        'avg_ms': data['sum'] / data['count'] if data['count'] > 0 else 0,
                        'min_ms': min(values) if values else 0,
                        'max_ms': max(values) if values else 0,
                        'tags': tags if tags else None
                    }
                elif data['type'] == 'gauge':
                    summary[key] = {
                        'type': 'gauge',
                        'value': data['value'],
                        'tags': tags if tags else None
                    }
            
            return summary
    
    def reset(self):
        """Reset all metrics to initial state."""
        with self._lock:
            self._metrics = {}


class Timer:
    """Context manager for timing code blocks."""
    
    def __init__(self, collector: MetricsCollector, name: str, tags: Optional[Dict[str, str]] = None):
        """
        Create a timer context manager.
        
        Args:
            collector: The MetricsCollector instance
            name: The metric name to record timing under
            tags: Optional tags for the metric
        """
        self._collector = collector
        self._name = name
        self._tags = tags
        self._start_time = None
    
    def __enter__(self):
        """Start the timer."""
        self._start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Stop the timer and record the duration."""
        if self._start_time is not None:
            duration_ms = (time.time() - self._start_time) * 1000
            self._collector.timing(self._name, duration_ms, self._tags)
        return False  # Don't suppress exceptions


# Module-level convenience function
def get_metrics() -> MetricsCollector:
    """Get the global MetricsCollector instance."""
    return MetricsCollector.get_instance()
