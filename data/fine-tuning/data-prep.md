# Data Preparation

## Format Requirements

### OpenAI Chat Format (Standard)
```jsonl
{"messages": [{"role": "system", "content": "..."}, {"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]}
```

### Multi-Turn Conversations
```jsonl
{"messages": [
  {"role": "system", "content": "You are a helpful assistant."},
  {"role": "user", "content": "What's the weather?"},
  {"role": "assistant", "content": "I don't have access to weather data."},
  {"role": "user", "content": "Can you check?"},
  {"role": "assistant", "content": "No, I can't access external services."}
]}
```

## Minimum Dataset Sizes

| Use Case | Minimum | Recommended |
|----------|---------|-------------|
| Format/style adaptation | 50-100 | 200-500 |
| Classification | 200-500 | 1,000-2,000 |
| Complex reasoning | 500-1,000 | 2,000-5,000 |
| Domain expertise | 1,000+ | 5,000-10,000 |

**Quality > Quantity** — LIMA paper showed 1,000 high-quality examples beat 52,000 low-quality.

## Data Quality Checklist

Before training, verify:
- [ ] Consistent format across ALL examples
- [ ] No contradictory examples (same input, different outputs)
- [ ] Examples match production input distribution
- [ ] Edge cases included (10-20% of dataset)
- [ ] No duplicate or near-duplicate entries
- [ ] Proper train/val/test split (80/10/10)

## Validation Script

```python
import json
from collections import Counter

def validate_jsonl(path):
    errors = []
    examples = []
    
    with open(path) as f:
        for i, line in enumerate(f, 1):
            try:
                obj = json.loads(line)
                if "messages" not in obj:
                    errors.append(f"Line {i}: Missing 'messages' key")
                    continue
                    
                messages = obj["messages"]
                roles = [m["role"] for m in messages]
                
                # Check role sequence
                if not roles[-1] == "assistant":
                    errors.append(f"Line {i}: Must end with assistant")
                
                # Check for empty content
                for m in messages:
                    if not m.get("content", "").strip():
                        errors.append(f"Line {i}: Empty content")
                        
                examples.append(obj)
                
            except json.JSONDecodeError:
                errors.append(f"Line {i}: Invalid JSON")
    
    print(f"Total examples: {len(examples)}")
    print(f"Errors: {len(errors)}")
    for e in errors[:10]:
        print(f"  - {e}")
    
    return examples, errors
```

## Deduplication

```python
import hashlib

def dedupe_by_input(examples):
    seen = set()
    unique = []
    
    for ex in examples:
        # Hash user messages only
        user_msgs = [m["content"] for m in ex["messages"] if m["role"] == "user"]
        key = hashlib.md5(str(user_msgs).encode()).hexdigest()
        
        if key not in seen:
            seen.add(key)
            unique.append(ex)
    
    print(f"Removed {len(examples) - len(unique)} duplicates")
    return unique
```

## Synthetic Data Generation

When you need more examples:

```python
def augment_example(example, model="gpt-4o"):
    """Generate variations of an existing example"""
    prompt = f"""
    Given this training example, generate 3 variations that:
    - Keep the same intent and output format
    - Vary the phrasing and specifics
    - Maintain quality
    
    Original: {json.dumps(example)}
    """
    
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}]
    )
    
    return parse_variations(response.choices[0].message.content)
```

## Common Data Issues

| Issue | Detection | Fix |
|-------|-----------|-----|
| Inconsistent formats | Check output structure variance | Standardize template |
| Contradictions | Hash inputs, compare outputs | Manual review, remove |
| Distribution mismatch | Compare to production logs | Add production examples |
| Missing edge cases | Analyze failure modes | Targeted collection |
| Token length issues | Count tokens per example | Truncate or split |
