#!/usr/bin/env python3
"""
Perplexity Agent API Client
A comprehensive Python script demonstrating Perplexity Agent API usage.

Usage:
    python perplexity_client.py search "What are the latest AI developments?"
    python perplexity_client.py stream "Explain quantum computing"
    python perplexity_client.py research "Impact of AI on healthcare"
    python perplexity_client.py compare "Explain machine learning"
"""

import os
import sys
from pathlib import Path
from typing import Optional, List, Dict
from perplexity import Perplexity, APIError

# Try to load .env file if it exists
try:
    from dotenv import load_dotenv
    # Look for .env in the script's directory
    env_path = Path(__file__).parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
except ImportError:
    # python-dotenv not installed, skip
    pass


class PerplexityClient:
    """Wrapper class for Perplexity Agent API with common use cases."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Perplexity client.
        
        Args:
            api_key: API key (defaults to PERPLEXITY_API_KEY env var)
        """
        self.client = Perplexity(api_key=api_key) if api_key else Perplexity()
    
    @staticmethod
    def _extract_usage_info(response) -> Dict:
        """
        Extract usage information from response safely.
        
        Args:
            response: API response object
            
        Returns:
            Dict with tokens and cost
        """
        tokens = 0
        cost = 0.0
        
        if hasattr(response, 'usage'):
            # Get tokens
            if hasattr(response.usage, 'total_tokens'):
                tokens = response.usage.total_tokens
            
            # Get cost - handle different response structures
            if hasattr(response.usage, 'total_cost'):
                cost = response.usage.total_cost
            elif hasattr(response.usage, 'cost'):
                if hasattr(response.usage.cost, 'total_cost'):
                    cost = response.usage.cost.total_cost
        
        return {"tokens": tokens, "cost": cost}
    
    def simple_query(
        self,
        query: str,
        model: str = "openai/gpt-5.2",
        max_tokens: int = 1000
    ) -> Dict:
        """
        Execute a simple query without tools.
        
        Args:
            query: The question or prompt
            model: Model to use
            max_tokens: Maximum output tokens
            
        Returns:
            Dict with answer, tokens, and cost
        """
        try:
            response = self.client.responses.create(
                model=model,
                input=query,
                max_output_tokens=max_tokens,
            )
            
            if response.status == "completed":
                usage_info = self._extract_usage_info(response)
                return {
                    "answer": response.output_text,
                    "tokens": usage_info["tokens"],
                    "cost": usage_info["cost"],
                    "model": response.model,
                }
            else:
                error_msg = response.error.message if response.error else "Unknown error"
                return {"error": error_msg}
                
        except APIError as e:
            return {"error": f"API Error: {e.message} (Status: {e.status_code})"}
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}"}
    
    def search_query(
        self,
        query: str,
        model: str = "openai/gpt-5.2",
        location: Optional[Dict] = None,
        max_tokens: int = 1000
    ) -> Dict:
        """
        Execute a query with web search tool.
        
        Args:
            query: The question or prompt
            model: Model to use
            location: Optional location dict with latitude, longitude, city, etc.
            max_tokens: Maximum output tokens
            
        Returns:
            Dict with answer, tokens, and cost
        """
        try:
            tools = [{"type": "web_search"}]
            
            # Add location if provided
            if location:
                tools[0]["user_location"] = location
            
            response = self.client.responses.create(
                model=model,
                input=query,
                tools=tools,
                instructions=(
                    "You have access to a web_search tool. Use it for questions about "
                    "current events, news, or recent developments. Use 1 query for simple "
                    "questions. Keep queries brief: 2-5 words. NEVER ask permission to "
                    "search - just search when appropriate."
                ),
                max_output_tokens=max_tokens,
            )
            
            if response.status == "completed":
                usage_info = self._extract_usage_info(response)
                return {
                    "answer": response.output_text,
                    "tokens": usage_info["tokens"],
                    "cost": usage_info["cost"],
                    "model": response.model,
                }
            else:
                error_msg = response.error.message if response.error else "Unknown error"
                return {"error": error_msg}
                
        except APIError as e:
            return {"error": f"API Error: {e.message} (Status: {e.status_code})"}
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}"}
    
    def stream_query(
        self,
        query: str,
        model: str = "openai/gpt-5.2",
        use_search: bool = False,
        max_tokens: int = 2000
    ) -> None:
        """
        Execute a streaming query and print results in real-time.
        
        Args:
            query: The question or prompt
            model: Model to use
            use_search: Whether to enable web search
            max_tokens: Maximum output tokens
        """
        try:
            kwargs = {
                "model": model,
                "input": query,
                "stream": True,
                "max_output_tokens": max_tokens,
            }
            
            if use_search:
                kwargs["tools"] = [{"type": "web_search"}]
                kwargs["instructions"] = (
                    "Use web_search for current information. Keep queries concise."
                )
            
            response = self.client.responses.create(**kwargs)
            
            print(f"\n{'='*60}")
            print(f"Streaming response from {model}:")
            print(f"{'='*60}\n")
            
            for chunk in response:
                if chunk.type == "response.output_text.delta":
                    print(chunk.delta, end="", flush=True)
                elif chunk.type == "response.completed":
                    usage_info = self._extract_usage_info(chunk.response)
                    print(f"\n\n{'='*60}")
                    print(f"✓ Completed")
                    print(f"Tokens: {usage_info['tokens']}")
                    print(f"Cost: ${usage_info['cost']:.6f}")
                    print(f"{'='*60}\n")
                elif chunk.type == "response.failed":
                    error_msg = chunk.error.message if chunk.error else "Unknown error"
                    print(f"\n\n✗ Failed: {error_msg}\n")
                    
        except APIError as e:
            print(f"\n✗ API Error: {e.message} (Status: {e.status_code})\n")
        except Exception as e:
            print(f"\n✗ Unexpected error: {str(e)}\n")
    
    def conversation(
        self,
        messages: List[Dict],
        model: str = "openai/gpt-5.2",
        use_search: bool = False,
        max_tokens: int = 1000
    ) -> Dict:
        """
        Execute a multi-turn conversation.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Model to use
            use_search: Whether to enable web search
            max_tokens: Maximum output tokens
            
        Returns:
            Dict with answer, tokens, and cost
        """
        try:
            # Convert to API format
            input_messages = [
                {"type": "message", "role": msg["role"], "content": msg["content"]}
                for msg in messages
            ]
            
            kwargs = {
                "model": model,
                "input": input_messages,
                "max_output_tokens": max_tokens,
            }
            
            if use_search:
                kwargs["tools"] = [{"type": "web_search"}]
                kwargs["instructions"] = "Use web_search when you need current information."
            
            response = self.client.responses.create(**kwargs)
            
            if response.status == "completed":
                usage_info = self._extract_usage_info(response)
                return {
                    "answer": response.output_text,
                    "tokens": usage_info["tokens"],
                    "cost": usage_info["cost"],
                    "model": response.model,
                }
            else:
                error_msg = response.error.message if response.error else "Unknown error"
                return {"error": error_msg}
                
        except APIError as e:
            return {"error": f"API Error: {e.message} (Status: {e.status_code})"}
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}"}
    
    def compare_models(
        self,
        query: str,
        models: List[str] = None,
        max_tokens: int = 300
    ) -> List[Dict]:
        """
        Compare responses from different models.
        
        Args:
            query: The question or prompt
            models: List of model identifiers
            max_tokens: Maximum output tokens per model
            
        Returns:
            List of dicts with model, answer, tokens, and cost
        """
        if models is None:
            models = [
                "openai/gpt-5.2",
                "anthropic/claude-3-5-sonnet",
                "google/gemini-2.0-flash",
            ]
        
        results = []
        
        for model in models:
            print(f"Querying {model}...", end=" ", flush=True)
            
            try:
                response = self.client.responses.create(
                    model=model,
                    input=query,
                    max_output_tokens=max_tokens,
                )
                
                if response.status == "completed":
                    usage_info = self._extract_usage_info(response)
                    results.append({
                        "model": model,
                        "answer": response.output_text,
                        "tokens": usage_info["tokens"],
                        "cost": usage_info["cost"],
                    })
                    print("✓")
                else:
                    error_msg = response.error.message if response.error else "Unknown"
                    results.append({
                        "model": model,
                        "error": error_msg,
                    })
                    print(f"✗ {error_msg}")
                    
            except APIError as e:
                results.append({
                    "model": model,
                    "error": f"API Error: {e.message}",
                })
                print(f"✗ {e.message}")
            except Exception as e:
                results.append({
                    "model": model,
                    "error": str(e),
                })
                print(f"✗ {str(e)}")
        
        return results
    
    def research_query(
        self,
        query: str,
        model: str = "openai/gpt-5.2",
        reasoning_effort: str = "high",
        max_tokens: int = 2000
    ) -> Dict:
        """
        Execute a research query with web search and high reasoning effort.
        
        Args:
            query: The research question
            model: Model to use
            reasoning_effort: "low", "medium", or "high"
            max_tokens: Maximum output tokens
            
        Returns:
            Dict with answer, tokens, and cost
        """
        try:
            response = self.client.responses.create(
                model=model,
                input=query,
                tools=[{"type": "web_search"}],
                instructions="""
                You are a research assistant with access to web_search.
                
                Guidelines:
                - Use web_search to find current, reliable information
                - Cite sources when possible
                - Focus on recent developments
                - Provide balanced analysis
                - Keep search queries concise (2-5 words)
                - Use multiple searches if needed for comprehensive coverage
                """,
                reasoning={"effort": reasoning_effort},
                max_output_tokens=max_tokens,
            )
            
            if response.status == "completed":
                usage_info = self._extract_usage_info(response)
                return {
                    "answer": response.output_text,
                    "tokens": usage_info["tokens"],
                    "cost": usage_info["cost"],
                    "model": response.model,
                }
            else:
                error_msg = response.error.message if response.error else "Unknown error"
                return {"error": error_msg}
                
        except APIError as e:
            return {"error": f"API Error: {e.message} (Status: {e.status_code})"}
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}"}
    
    def use_preset(
        self,
        query: str,
        preset: str = "pro-search"
    ) -> Dict:
        """
        Execute a query using a preset configuration.
        
        Args:
            query: The question or prompt
            preset: Preset identifier (e.g., "pro-search")
            
        Returns:
            Dict with answer, tokens, and cost
        """
        try:
            response = self.client.responses.create(
                preset=preset,
                input=query,
            )
            
            if response.status == "completed":
                usage_info = self._extract_usage_info(response)
                return {
                    "answer": response.output_text,
                    "tokens": usage_info["tokens"],
                    "cost": usage_info["cost"],
                    "model": response.model,
                }
            else:
                error_msg = response.error.message if response.error else "Unknown error"
                return {"error": error_msg}
                
        except APIError as e:
            return {"error": f"API Error: {e.message} (Status: {e.status_code})"}
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}"}


def print_result(result: Dict) -> None:
    """Pretty print a result dictionary."""
    print(f"\n{'='*60}")
    
    if "error" in result:
        print(f"✗ Error: {result['error']}")
    else:
        print(f"Model: {result.get('model', 'N/A')}")
        print(f"Tokens: {result.get('tokens', 0)}")
        print(f"Cost: ${result.get('cost', 0):.6f}")
        print(f"\n{'-'*60}")
        print(f"\n{result['answer']}")
    
    print(f"\n{'='*60}\n")


def main():
    """CLI interface for the Perplexity client."""
    
    # Check for API key
    if not os.getenv("PERPLEXITY_API_KEY"):
        print("Error: PERPLEXITY_API_KEY environment variable not set")
        print("\nSet it with:")
        print("  export PERPLEXITY_API_KEY='your_api_key'")
        sys.exit(1)
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python perplexity_client.py <command> <query>")
        print("\nCommands:")
        print("  query     - Simple query without tools")
        print("  search    - Query with web search")
        print("  stream    - Streaming query")
        print("  research  - Research with high reasoning")
        print("  compare   - Compare multiple models")
        print("  preset    - Use preset configuration")
        print("\nExamples:")
        print("  python perplexity_client.py search 'What are the latest AI developments?'")
        print("  python perplexity_client.py stream 'Explain quantum computing'")
        print("  python perplexity_client.py research 'Impact of AI on healthcare'")
        print("  python perplexity_client.py compare 'Explain machine learning'")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    query = sys.argv[2] if len(sys.argv) > 2 else ""
    
    if not query and command != "interactive":
        print(f"Error: Query required for command '{command}'")
        sys.exit(1)
    
    # Initialize client
    client = PerplexityClient()
    
    # Execute command
    if command == "query":
        result = client.simple_query(query)
        print_result(result)
    
    elif command == "search":
        result = client.search_query(query)
        print_result(result)
    
    elif command == "stream":
        client.stream_query(query, use_search=True)
    
    elif command == "research":
        result = client.research_query(query)
        print_result(result)
    
    elif command == "compare":
        results = client.compare_models(query)
        for result in results:
            if "error" in result:
                print(f"\n{result['model']}: ✗ {result['error']}")
            else:
                print(f"\n{'='*60}")
                print(f"Model: {result['model']}")
                print(f"Tokens: {result['tokens']} | Cost: ${result['cost']:.6f}")
                print(f"{'-'*60}")
                print(result['answer'])
                print(f"{'='*60}")
    
    elif command == "preset":
        result = client.use_preset(query)
        print_result(result)
    
    else:
        print(f"Unknown command: {command}")
        print("Use 'query', 'search', 'stream', 'research', 'compare', or 'preset'")
        sys.exit(1)


if __name__ == "__main__":
    main()
