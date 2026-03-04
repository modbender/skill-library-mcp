# Perplexity Research Examples

Practical examples demonstrating common research patterns.

## Import Setup

For all examples below, use this import pattern:

```python
import sys
from pathlib import Path

# Add scripts directory to path (adjust based on your location)
skill_dir = Path(".cursor/skills/perplexity-research")
sys.path.insert(0, str(skill_dir / "scripts"))

from perplexity_client import PerplexityClient
```

Or if running from the skill directory:

```python
import sys
sys.path.insert(0, "scripts")
from perplexity_client import PerplexityClient
```

## Investment Analysis

### Comprehensive Market Research

```python
from perplexity_client import PerplexityClient

client = PerplexityClient()

# Deep market analysis with high reasoning
result = client.research_query(
    query="Analyze the competitive landscape in electric vehicle battery technology, including key players, recent breakthroughs, and market share trends",
    model="openai/gpt-5.2",
    reasoning_effort="high",
    max_tokens=2000
)

print(result["answer"])
print(f"\nAnalysis cost: ${result['cost']:.6f}")
```

### Quick Company News Check

```python
# Fast search for current information
result = client.search_query(
    query="Apple latest product announcements February 2026",
    model="openai/gpt-5.2",
    max_tokens=800
)

print(result["answer"])
```

### Multi-Model Investment Decision

```python
# Compare perspectives from different models
results = client.compare_models(
    query="Should investors be concerned about rising interest rates in 2026?",
    models=[
        "openai/gpt-5.2",
        "anthropic/claude-3-5-sonnet",
        "google/gemini-2.0-flash"
    ],
    max_tokens=400
)

for result in results:
    if "error" not in result:
        print(f"\n{'='*60}")
        print(f"Model: {result['model']}")
        print(f"Cost: ${result['cost']:.6f}")
        print(f"{'-'*60}")
        print(result['answer'])
```

## Technology Research

### Emerging Tech Analysis

```python
from perplexity_client import PerplexityClient

client = PerplexityClient()

# Streaming for real-time insights
client.stream_query(
    query="What are the most significant AI breakthroughs announced in 2026, and which companies are leading the innovation?",
    model="openai/gpt-5.2",
    use_search=True,
    max_tokens=2000
)
```

### Patent and Innovation Research

```python
# Research with location context (for region-specific results)
location = {
    "city": "San Francisco",
    "country": "United States",
    "region": "California"
}

result = client.search_query(
    query="Recent AI patents filed in Silicon Valley",
    model="openai/gpt-5.2",
    location=location,
    max_tokens=1200
)

print(result["answer"])
```

## Conversational Research

### Building Context Over Multiple Queries

```python
from perplexity_client import PerplexityClient

client = PerplexityClient()

# First query
messages = [
    {"role": "user", "content": "What is the current state of quantum computing?"}
]

result1 = client.conversation(
    messages=messages,
    model="openai/gpt-5.2",
    use_search=True,
    max_tokens=1000
)

# Add response and follow-up
messages.append({"role": "assistant", "content": result1["answer"]})
messages.append({"role": "user", "content": "Which companies are most likely to achieve quantum advantage first?"})

result2 = client.conversation(
    messages=messages,
    use_search=True
)

print(result2["answer"])
```

## Preset Configurations

### Using Pro Search Preset

```python
from perplexity_client import PerplexityClient

client = PerplexityClient()

# Use optimized preset for comprehensive search
result = client.use_preset(
    query="Comprehensive analysis of renewable energy adoption rates globally",
    preset="pro-search"
)

print(result["answer"])
print(f"Tokens: {result['tokens']}, Cost: ${result['cost']:.6f}")
```

## Error Handling Patterns

### Robust Research Function

```python
from perplexity_client import PerplexityClient

def conduct_research(query: str, retry_count: int = 2):
    """Conduct research with error handling and retries."""
    client = PerplexityClient()
    
    for attempt in range(retry_count):
        result = client.research_query(
            query=query,
            model="openai/gpt-5.2",
            reasoning_effort="high"
        )
        
        if "error" not in result:
            return {
                "success": True,
                "data": result["answer"],
                "tokens": result["tokens"],
                "cost": result["cost"]
            }
        
        print(f"Attempt {attempt + 1} failed: {result['error']}")
        
        if attempt < retry_count - 1:
            print("Retrying...")
            time.sleep(2)
    
    return {
        "success": False,
        "error": result.get("error", "Unknown error after retries")
    }

# Use it
research_result = conduct_research(
    "What are the main drivers of inflation in 2026?"
)

if research_result["success"]:
    print(research_result["data"])
else:
    print(f"Research failed: {research_result['error']}")
```

## Batch Research

### Multiple Topics Analysis

```python
from perplexity_client import PerplexityClient

client = PerplexityClient()

topics = [
    "AI regulation developments in EU 2026",
    "Cryptocurrency market trends February 2026",
    "Supply chain innovations in manufacturing"
]

results = []

for topic in topics:
    print(f"\nResearching: {topic}")
    result = client.research_query(
        query=topic,
        model="openai/gpt-5.2",
        reasoning_effort="medium",
        max_tokens=800
    )
    
    if "error" not in result:
        results.append({
            "topic": topic,
            "analysis": result["answer"],
            "cost": result["cost"]
        })
    else:
        print(f"Error: {result['error']}")

# Aggregate results
total_cost = sum(r["cost"] for r in results)
print(f"\n\nTotal research cost: ${total_cost:.6f}")

for r in results:
    print(f"\n{'='*60}")
    print(f"Topic: {r['topic']}")
    print(f"{'-'*60}")
    print(r['analysis'])
```

## Cost Optimization Example

### Smart Token Management

```python
from perplexity_client import PerplexityClient

def smart_research(query: str, max_cost: float = 0.10):
    """Research with cost limits."""
    client = PerplexityClient()
    
    # Start with smaller token limit
    result = client.research_query(
        query=query,
        model="openai/gpt-5.2",
        reasoning_effort="medium",
        max_tokens=500  # Conservative start
    )
    
    if "error" in result:
        return result
    
    # Check if we need more detail and have budget
    if result["cost"] < max_cost * 0.6:
        # We have budget for a follow-up
        follow_up = client.research_query(
            query=f"Provide more detailed analysis: {query}",
            reasoning_effort="high",
            max_tokens=1000
        )
        
        if "error" not in follow_up:
            return {
                "answer": follow_up["answer"],
                "tokens": result["tokens"] + follow_up["tokens"],
                "cost": result["cost"] + follow_up["cost"]
            }
    
    return result

# Use it with cost control
result = smart_research(
    "What are the investment implications of recent Fed policy changes?",
    max_cost=0.15
)

print(result["answer"])
print(f"\nTotal cost: ${result['cost']:.6f}")
```

## Real-World Integration

### Research Report Generator

```python
from datetime import datetime
from perplexity_client import PerplexityClient

def generate_research_report(topic: str, output_file: str):
    """Generate comprehensive research report."""
    client = PerplexityClient()
    
    print(f"Generating research report on: {topic}")
    
    # Main research
    main_result = client.research_query(
        query=f"Provide comprehensive analysis of: {topic}",
        reasoning_effort="high",
        max_tokens=2000
    )
    
    if "error" in main_result:
        print(f"Error: {main_result['error']}")
        return
    
    # Get alternative perspective
    alt_models_result = client.compare_models(
        query=f"What are the key risks and opportunities in: {topic}",
        models=["anthropic/claude-3-5-sonnet", "google/gemini-2.0-flash"],
        max_tokens=400
    )
    
    # Generate report
    report = f"""# Research Report: {topic}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}

## Main Analysis

{main_result['answer']}

## Alternative Perspectives

"""
    
    for result in alt_models_result:
        if "error" not in result:
            report += f"\n### {result['model']}\n\n{result['answer']}\n"
    
    # Add metadata
    total_cost = main_result['cost'] + sum(
        r.get('cost', 0) for r in alt_models_result if 'error' not in r
    )
    
    report += f"\n---\n\n**Research Cost**: ${total_cost:.6f}\n"
    
    # Save report
    with open(output_file, 'w') as f:
        f.write(report)
    
    print(f"\nReport saved to: {output_file}")
    print(f"Total cost: ${total_cost:.6f}")

# Generate report
generate_research_report(
    "Impact of AI on healthcare industry 2026",
    "research_report_ai_healthcare.md"
)
```
