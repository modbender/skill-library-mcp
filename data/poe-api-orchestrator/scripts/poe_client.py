#!/usr/bin/env python3
"""
Poe API Client - OpenAI Compatible Version
使用 OpenAI 兼容的 Poe API（更簡單！）

根據：https://poe.com/api
"""

import os
from typing import Optional, Dict, Any
from dataclasses import dataclass
import time

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("❌ openai 未安裝")
    print("請運行: pip install openai")


@dataclass
class PoeConfig:
    """Poe API Configuration"""
    api_key: str = os.getenv("POE_API_KEY", "w0womy7-r0RmMP-C1nFH2f_RXnBbPr1dfy34VHqzWck")
    base_url: str = "https://api.poe.com/v1"
    
    # Token control ⚠️ IMPORTANT
    # Note: max_tokens = response length limit, NOT total usage
    max_tokens_per_request: int = 8000  # Response length limit (higher for coding)
    max_total_tokens: int = 100000      # Total budget across all calls
    max_calls_per_task: int = 10        # Max API calls per task
    track_usage: bool = True
    
    # Usage tracking
    total_tokens_used: int = 0
    request_count: int = 0
    call_count: int = 0  # Track number of API calls
    
    # Available models
    models: Dict[str, str] = None
    
    def __post_init__(self):
        self.models = {
            "coding": "GPT-5.3-Codex",
            "design": "Gemini-3.1-Pro",
            "analysis": "Claude-Sonnet-4.6",
            "reasoning": "Claude-Opus-4.6"
        }
    
    def check_budget(self, tokens: int) -> bool:
        """Check if within token budget AND call limit"""
        # Check total tokens
        if self.total_tokens_used + tokens > self.max_total_tokens:
            return False
        # Check call count
        if self.call_count >= self.max_calls_per_task:
            return False
        return True
    
    def add_usage(self, tokens: int):
        """Track token usage and call count"""
        self.total_tokens_used += tokens
        self.request_count += 1
        self.call_count += 1
    
    def get_task_max_tokens(self, task_type: str) -> int:
        """Get appropriate max_tokens for task type"""
        task_tokens = {
            "coding": 8000,      # Coding needs more tokens for complete code
            "design": 4000,      # UI/UX design
            "analysis": 3000,    # Analysis and requirements
            "reasoning": 5000,   # Complex reasoning
        }
        return task_tokens.get(task_type, self.max_tokens_per_request)


class PoeClient:
    """Poe API Client using OpenAI-compatible interface"""
    
    def __init__(self, config: Optional[PoeConfig] = None):
        self.config = config or PoeConfig()
        
        if not OPENAI_AVAILABLE:
            raise ImportError(
                "openai not installed!\n"
                "Install with: pip install openai"
            )
        
        # Initialize OpenAI client with Poe base URL
        self.client = openai.OpenAI(
            api_key=self.config.api_key,
            base_url=self.config.base_url
        )
    
    def query(
        self,
        bot_name: str,
        message: str,
        context: Optional[str] = None,
        max_tokens: Optional[int] = None,
        task_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Query a Poe bot using OpenAI-compatible API
        
        Args:
            bot_name: Bot to query (e.g., "Claude-Sonnet-4.6")
            message: Your message/prompt
            context: Optional context (will be prepended to message)
            max_tokens: Max tokens for response (default: based on task type)
            task_type: Type of task (coding, design, analysis, reasoning)
        
        Returns:
            Response dict with 'response' or 'error'
        """
        # Get appropriate max_tokens for task type
        if max_tokens is None:
            if task_type:
                max_tokens = self.config.get_task_max_tokens(task_type)
            else:
                max_tokens = self.config.max_tokens_per_request
        
        # Check call count first
        if self.config.call_count >= self.config.max_calls_per_task:
            return {
                "success": False,
                "error": f"Call limit exceeded. Calls: {self.config.call_count}/{self.config.max_calls_per_task}",
                "model": bot_name
            }
        
        # Check token budget
        estimated_tokens = len(message.split()) * 1.5
        if not self.config.check_budget(estimated_tokens):
            return {
                "success": False,
                "error": f"Budget exceeded. Tokens: {self.config.total_tokens_used}/{self.config.max_total_tokens}, Calls: {self.config.call_count}/{self.config.max_calls_per_task}",
                "model": bot_name
            }
        
        # Prepare message
        full_message = f"{context}\n\n{message}" if context else message
        
        try:
            start_time = time.time()
            
            # Call OpenAI-compatible API
            response = self.client.chat.completions.create(
                model=bot_name,
                messages=[{
                    "role": "user",
                    "content": full_message
                }],
                max_tokens=max_tokens
            )
            
            elapsed_time = time.time() - start_time
            
            # Extract response
            response_text = response.choices[0].message.content
            
            # Track token usage (from API response)
            tokens_used = response.usage.total_tokens if hasattr(response, 'usage') else int(len(response_text.split()) * 1.5)
            
            if self.config.track_usage:
                self.config.add_usage(tokens_used)
            
            return {
                "success": True,
                "response": response_text,
                "model": bot_name,
                "timestamp": time.time(),
                "elapsed_time": elapsed_time,
                "tokens_used": tokens_used,
                "total_tokens": self.config.total_tokens_used,
                "call_count": self.config.call_count,
                "remaining_calls": self.config.max_calls_per_task - self.config.call_count
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "model": bot_name
            }
    
    def query_with_retry(
        self,
        bot_name: str,
        message: str,
        max_retries: int = 3,
        **kwargs
    ) -> Dict[str, Any]:
        """Query with automatic retry"""
        
        for attempt in range(max_retries):
            result = self.query(bot_name, message, **kwargs)
            
            if result.get("success"):
                return result
            
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt
                print(f"Retry {attempt + 1}/{max_retries} after {wait_time}s...")
                time.sleep(wait_time)
        
        return result
    
    # Convenience methods for specific models
    def query_coding(self, task: str, **kwargs) -> Dict[str, Any]:
        """Query coding model (GPT-5.3-Codex)"""
        return self.query_with_retry(
            self.config.models["coding"],
            task,
            **kwargs
        )
    
    def query_design(self, task: str, **kwargs) -> Dict[str, Any]:
        """Query design model (Gemini-3.1-Pro)"""
        return self.query_with_retry(
            self.config.models["design"],
            task,
            **kwargs
        )
    
    def query_analysis(self, task: str, **kwargs) -> Dict[str, Any]:
        """Query analysis model (Claude-Sonnet-4.6)"""
        return self.query_with_retry(
            self.config.models["analysis"],
            task,
            **kwargs
        )
    
    def query_reasoning(self, task: str, **kwargs) -> Dict[str, Any]:
        """Query reasoning model (Claude-Opus-4.6)"""
        return self.query_with_retry(
            self.config.models["reasoning"],
            task,
            **kwargs
        )


# Convenience functions for subagents
def code(task: str, context: Optional[str] = None, max_tokens: int = None) -> str:
    """
    Quick coding query with token control
    
    Args:
        task: Coding task
        context: Optional context
        max_tokens: Max tokens for response (default: 8000 for coding)
    
    Usage in subagent:
        from poe_client import code
        result = code("Write a Python function to sort a list")
    
    Returns:
        Response text or error message
    """
    if not OPENAI_AVAILABLE:
        return "Error: openai not installed. Run: pip install openai"
    
    client = PoeClient()
    # Use 8000 tokens for coding by default (if not specified)
    if max_tokens is None:
        max_tokens = 8000
    
    result = client.query_coding(task, context=context, max_tokens=max_tokens, task_type="coding")
    
    if result["success"]:
        # Log token usage
        if result.get("tokens_used"):
            print(f"📊 Tokens: {result['tokens_used']} | Total: {result['total_tokens']} | Calls: {result['call_count']}/{client.config.max_calls_per_task}")
        
        return result["response"]
    else:
        return f"Error: {result['error']}"


def design(task: str, context: Optional[str] = None, max_tokens: int = None) -> str:
    """
    Quick design query with token control
    
    Args:
        task: Design task
        context: Optional context
        max_tokens: Max tokens for response (default: 4000 for design)
    
    Usage in subagent:
        from poe_client import design
        result = design("Design a dashboard for trading bot")
    
    Returns:
        Response text or error message
    """
    if not OPENAI_AVAILABLE:
        return "Error: openai not installed. Run: pip install openai"
    
    client = PoeClient()
    if max_tokens is None:
        max_tokens = 4000
    
    result = client.query_design(task, context=context, max_tokens=max_tokens, task_type="design")
    
    if result["success"]:
        if result.get("tokens_used"):
            print(f"📊 Tokens: {result['tokens_used']} | Total: {result['total_tokens']} | Calls: {result['call_count']}/{client.config.max_calls_per_task}")
        
        return result["response"]
    else:
        return f"Error: {result['error']}"


def analyze(task: str, context: Optional[str] = None, max_tokens: int = None) -> str:
    """
    Quick analysis query with token control
    
    Args:
        task: Analysis task
        context: Optional context
        max_tokens: Max tokens for response (default: 3000 for analysis)
    
    Usage in subagent:
        from poe_client import analyze
        result = analyze("Analyze requirements for chatbot")
    
    Returns:
        Response text or error message
    """
    if not OPENAI_AVAILABLE:
        return "Error: openai not installed. Run: pip install openai"
    
    client = PoeClient()
    if max_tokens is None:
        max_tokens = 3000
    
    result = client.query_analysis(task, context=context, max_tokens=max_tokens, task_type="analysis")
    
    if result["success"]:
        if result.get("tokens_used"):
            print(f"📊 Tokens: {result['tokens_used']} | Total: {result['total_tokens']} | Calls: {result['call_count']}/{client.config.max_calls_per_task}")
        
        return result["response"]
    else:
        return f"Error: {result['error']}"


def reason(task: str, context: Optional[str] = None, max_tokens: int = None) -> str:
    """
    Quick reasoning query with token control
    
    Args:
        task: Reasoning task
        context: Optional context
        max_tokens: Max tokens for response (default: 5000 for reasoning)
    
    Usage in subagent:
        from poe_client import reason
        result = reason("Design microservices architecture")
    
    Returns:
        Response text or error message
    """
    if not OPENAI_AVAILABLE:
        return "Error: openai not installed. Run: pip install openai"
    
    client = PoeClient()
    if max_tokens is None:
        max_tokens = 5000
    
    result = client.query_reasoning(task, context=context, max_tokens=max_tokens, task_type="reasoning")
    
    if result["success"]:
        if result.get("tokens_used"):
            print(f"📊 Tokens: {result['tokens_used']} | Total: {result['total_tokens']} | Calls: {result['call_count']}/{client.config.max_calls_per_task}")
        
        return result["response"]
    else:
        return f"Error: {result['error']}"


# Test function
def test_connection():
    """Test Poe API connection"""
    if not OPENAI_AVAILABLE:
        print("❌ Cannot test: openai not installed")
        print("Install with: pip install openai")
        return
    
    print("=" * 80)
    print("🧪 Testing Poe API Connection (OpenAI-Compatible)")
    print("=" * 80)
    print()
    
    client = PoeClient()
    
    print(f"API Key: {client.config.api_key[:20]}...")
    print(f"Base URL: {client.config.base_url}")
    print()
    
    # Test each model with simple query
    for task_type, model in client.config.models.items():
        print(f"Testing {task_type} model: {model}")
        
        result = client.query(
            model,
            "Hello! Please respond with 'OK' to confirm you're working."
        )
        
        if result["success"]:
            print(f"✅ {model}: Connection successful!")
            print(f"   Response: {result['response'][:100]}...")
            print(f"   Time: {result['elapsed_time']:.2f}s")
            print(f"   Tokens: {result['tokens_used']}")
        else:
            print(f"❌ {model}: {result['error']}")
        
        print()
    
    print("=" * 80)
    print(f"Total tokens used: {client.config.total_tokens_used}")
    print("=" * 80)


if __name__ == "__main__":
    # Run test
    test_connection()
    
    # Example usage
    print("\n" + "="*80)
    print("Example: Coding Task")
    print("="*80)
    
    result = code("Write a Python function to calculate fibonacci")
    print(result)
