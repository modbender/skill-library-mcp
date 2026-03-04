# Roundtable Skill

Multi-perspective decision analysis through simulated expert discussion.

## Features

- **Dynamic Role Selection**: Automatically selects 3-8 relevant perspectives based on the decision
- **Two-Round Discussion**: Each role contributes twice for deeper analysis
- **Consensus Building**: Synthesizes viewpoints into actionable recommendations
- **Risk Assessment**: Evaluates decision risk level to determine discussion depth

## Installation

```bash
npx clawhub@latest install roundtable
```

## Usage

Trigger with:
- "roundtable this decision"
- "run a roundtable on [topic]"
- "I need multiple perspectives on [decision]"

## When to Use

- Important decisions that benefit from multiple viewpoints
- Before high-risk operations (major changes, public announcements)
- When you want to challenge your own thinking
- Complex trade-offs with no obvious right answer

## Example Output

```
## 🗣️ Round 1
### 🔧 Engineer
> "The implementation looks solid, but I'm concerned about..."

### 💼 Product Manager
> "From a user perspective, this could..."

## 🗣️ Round 2
[deeper discussion]

## 📊 Consensus
Based on the discussion, we recommend...
Action items:
1. ...
2. ...
```

## Version

v1.1.0

## License

MIT
