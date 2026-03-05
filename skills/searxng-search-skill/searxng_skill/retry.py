"""
Retry logic with exponential backoff
"""

import time
import functools
from typing import Callable, Any, Optional, Type, Tuple
import requests

from .exceptions import TimeoutException, ConnectionException


def retry_with_backoff(
    max_retries: int = 3,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0,
    exceptions: Tuple[Type[Exception], ...] = (
        requests.exceptions.Timeout,
        requests.exceptions.ConnectionError,
    ),
    verbose: bool = True
):
    """
    Decorator for retrying function calls with exponential backoff
    
    Args:
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay between retries in seconds
        backoff_factor: Exponential backoff multiplier
        exceptions: Tuple of exceptions to catch and retry
        verbose: Whether to print retry information
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                    
                except exceptions as e:
                    last_exception = e
                    
                    if attempt < max_retries - 1:
                        delay = initial_delay * (backoff_factor ** attempt)
                        if verbose:
                            print(
                                f"Attempt {attempt + 1}/{max_retries} failed: {e}. "
                                f"Retrying in {delay:.2f}s..."
                            )
                        time.sleep(delay)
                    else:
                        if verbose:
                            print(f"All {max_retries} attempts failed.")
            
            raise last_exception
        
        return wrapper
    return decorator


class RetryStrategy:
    """Configurable retry strategy"""
    
    def __init__(
        self,
        max_retries: int = 3,
        initial_delay: float = 1.0,
        backoff_factor: float = 2.0,
        max_delay: float = 60.0,
        jitter: bool = True
    ):
        self.max_retries = max_retries
        self.initial_delay = initial_delay
        self.backoff_factor = backoff_factor
        self.max_delay = max_delay
        self.jitter = jitter
    
    def get_delay(self, attempt: int) -> float:
        """Calculate delay for given attempt number"""
        import random
        
        delay = self.initial_delay * (self.backoff_factor ** attempt)
        delay = min(delay, self.max_delay)
        
        if self.jitter:
            delay *= (0.5 + random.random())
        
        return delay
    
    def execute(
        self,
        func: Callable,
        *args,
        **kwargs
    ) -> Any:
        """Execute function with retry strategy"""
        last_exception = None
        
        for attempt in range(self.max_retries):
            try:
                return func(*args, **kwargs)
            except (requests.exceptions.Timeout, 
                    requests.exceptions.ConnectionError) as e:
                last_exception = e
                
                if attempt < self.max_retries - 1:
                    delay = self.get_delay(attempt)
                    time.sleep(delay)
        
        raise last_exception