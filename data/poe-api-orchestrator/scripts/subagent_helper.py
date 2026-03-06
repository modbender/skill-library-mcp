#!/usr/bin/env python3
"""
Subagent Helper - Quick Reference

This shows how subagents can use Poe API
"""

# ============================================
# QUICK USAGE EXAMPLES
# ============================================

# 1. CODING TASKS (GPT-5.3-Codex)
# ============================================

from poe_client import code

# Example 1: Write a function
result = code("""
Write a Python function that:
1. Connects to WebSocket
2. Subscribes to price updates
3. Detects arbitrage opportunities
4. Returns opportunities as JSON
""")

print(result)


# 2. UI/UX DESIGN (Gemini-3.1-Pro)
# ============================================

from poe_client import design

# Example 2: Design a dashboard
result = design("""
Design a trading bot dashboard with:
1. Real-time price charts
2. Active positions panel
3. Profit/Loss summary
4. Alert notifications

Output: HTML + CSS mockup
""")

print(result)


# 3. DATA ANALYSIS (Claude-Sonnet-4.6)
# ============================================

from poe_client import analyze

# Example 3: Analyze requirements
result = analyze("""
Analyze requirements for building a real-time arbitrage bot:

1. Identify core features
2. List technical requirements
3. Suggest architecture
4. Estimate complexity

Data source: 1000 trades from Polymarket
""")

print(result)


# 4. COMPLEX REASONING (Claude-Opus-4.6)
# ============================================

from poe_client import reason

# Example 4: Architecture design
result = reason("""
Design a scalable microservices architecture for:

1. Real-time data ingestion
2. ML-based prediction
3. Risk management
4. Order execution

Requirements:
- Handle 10,000 events/second
- 99.9% uptime
- Sub-millisecond latency
""")

print(result)


# ============================================
# ADVANCED USAGE
# ============================================

from poe_client import PoeClient

client = PoeClient()

# Query with context
result = client.query_coding(
    task="Optimize this function for performance",
    context="""
    Current code:
    ```python
    def find_arbitrage(markets):
        # Slow implementation
        for m1 in markets:
            for m2 in markets:
                check_arbitrage(m1, m2)
    ```
    """
)

print(result)


# ============================================
# BATCH PROCESSING
# ============================================

tasks = [
    "Write API client",
    "Add error handling",
    "Write unit tests"
]

results = []
for task in tasks:
    result = code(task)
    results.append(result)
    print(f"✅ {task}")

print("\nAll tasks complete!")


# ============================================
# ERROR HANDLING
# ============================================

result = code("Some complex task")

if "Error:" in result:
    print(f"Failed: {result}")
    # Handle error
else:
    print(f"Success: {result}")
    # Process result


# ============================================
# INTEGRATION EXAMPLE
# ============================================

def build_feature(feature_name: str):
    """Complete workflow using multiple models"""
    
    # Step 1: Analyze requirements
    print(f"📋 Analyzing {feature_name}...")
    requirements = analyze(f"Analyze requirements for: {feature_name}")
    
    # Step 2: Design UI/UX
    print(f"🎨 Designing UI/UX...")
    ui_design = design(f"Design UI for: {feature_name}\n\nRequirements:\n{requirements}")
    
    # Step 3: Implement code
    print(f"💻 Writing code...")
    implementation = code(f"""
    Implement: {feature_name}
    
    Requirements:
    {requirements}
    
    UI Design:
    {ui_design}
    """)
    
    return {
        "requirements": requirements,
        "design": ui_design,
        "code": implementation
    }


# Run complete workflow
result = build_feature("Real-time arbitrage detector")
print("\n✅ Feature complete!")
print(result["code"])


# ============================================
# TESTING
# ============================================

if __name__ == "__main__":
    print("="*80)
    print("Testing Poe API Client")
    print("="*80)
    
    # Quick test
    result = code("Say 'Hello, I am GPT-5.3-Codex!'")
    print(f"Coding model: {result}\n")
    
    result = design("Say 'Hello, I am Gemini-3.1-Pro!'")
    print(f"Design model: {result}\n")
    
    result = analyze("Say 'Hello, I am Claude-Sonnet-4.6!'")
    print(f"Analysis model: {result}\n")
    
    result = reason("Say 'Hello, I am Claude-Opus-4.6!'")
    print(f"Reasoning model: {result}\n")
    
    print("✅ All models working!")
