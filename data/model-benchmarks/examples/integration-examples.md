# Integration Examples

## 1. OpenClaw Auto-Configuration

Automatically configure OpenClaw to use the most cost-effective model for your primary use case:

```bash
# Get the best model for coding tasks
CODING_MODEL=$(python3 skills/model-benchmarks/scripts/run.py recommend --task coding --format json | jq -r '.recommendations[0].model')

# Update OpenClaw config
openclaw config set agents.defaults.model.primary "openrouter/$CODING_MODEL"

echo "✅ OpenClaw configured to use $CODING_MODEL for coding tasks"
```

## 2. Cost Monitoring Alerts

Set up Slack alerts when model costs change significantly:

```bash
#!/bin/bash
# cost-monitor.sh

python3 skills/model-benchmarks/scripts/run.py fetch
COST_CHANGES=$(python3 skills/model-benchmarks/scripts/run.py analyze --cost-changes)

if [[ "$COST_CHANGES" != "No significant changes" ]]; then
    curl -X POST -H 'Content-type: application/json' \
        --data "{\"text\":\"🚨 AI Model Cost Alert: $COST_CHANGES\"}" \
        "$SLACK_WEBHOOK_URL"
fi
```

## 3. Dynamic Model Routing

Create a smart routing function that picks models based on task complexity:

```python
import subprocess
import json

def get_optimal_model(task_type, max_cost_per_1m=5.0):
    """Get the optimal model for a task within budget constraints."""
    
    cmd = [
        "python3", "skills/model-benchmarks/scripts/run.py", 
        "recommend", "--task", task_type, "--format", "json"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    recommendations = json.loads(result.stdout)
    
    for model in recommendations["recommendations"]:
        if model["avg_price"] <= max_cost_per_1m:
            return model["model"]
    
    # Fallback to cheapest model
    return recommendations["recommendations"][-1]["model"]

# Usage
coding_model = get_optimal_model("coding", max_cost_per_1m=3.0)
writing_model = get_optimal_model("writing", max_cost_per_1m=10.0)

print(f"Coding: {coding_model}")
print(f"Writing: {writing_model}")
```

## 4. Performance Tracking Dashboard

Create a simple dashboard to track your model performance over time:

```bash
#!/bin/bash
# dashboard-generator.sh

OUTPUT_DIR="model-dashboard"
mkdir -p "$OUTPUT_DIR"

# Generate cost efficiency report
python3 skills/model-benchmarks/scripts/run.py analyze --export csv > "$OUTPUT_DIR/cost-efficiency.csv"

# Generate task recommendations
for task in coding writing analysis translation math creative simple; do
    echo "# $task Task Recommendations" > "$OUTPUT_DIR/$task-recommendations.md"
    python3 skills/model-benchmarks/scripts/run.py recommend --task "$task" >> "$OUTPUT_DIR/$task-recommendations.md"
done

# Create summary HTML
cat > "$OUTPUT_DIR/index.html" << EOF
<!DOCTYPE html>
<html>
<head><title>AI Model Intelligence Dashboard</title></head>
<body>
    <h1>🧠 AI Model Intelligence Dashboard</h1>
    <p>Generated: $(date)</p>
    
    <h2>📊 Cost Efficiency Data</h2>
    <a href="cost-efficiency.csv">Download CSV</a>
    
    <h2>🎯 Task Recommendations</h2>
    <ul>
        <li><a href="coding-recommendations.md">Coding Tasks</a></li>
        <li><a href="writing-recommendations.md">Writing Tasks</a></li>
        <li><a href="analysis-recommendations.md">Analysis Tasks</a></li>
        <!-- Add more task types as needed -->
    </ul>
</body>
</html>
EOF

echo "✅ Dashboard generated in $OUTPUT_DIR/"
```

## 5. API Integration for Custom Applications

Use the skill programmatically in your own applications:

```python
import subprocess
import json

class ModelIntelligence:
    def __init__(self, skill_path="skills/model-benchmarks"):
        self.skill_path = skill_path
    
    def get_model_capabilities(self, model_name):
        """Get detailed capabilities for a specific model."""
        cmd = [
            "python3", f"{self.skill_path}/scripts/run.py",
            "query", "--model", model_name, "--format", "json"
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return json.loads(result.stdout)
    
    def get_task_recommendations(self, task_type, top_n=3):
        """Get top N model recommendations for a task."""
        cmd = [
            "python3", f"{self.skill_path}/scripts/run.py",
            "recommend", "--task", task_type, "--format", "json"
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        data = json.loads(result.stdout)
        return data["recommendations"][:top_n]
    
    def find_cost_efficient_models(self, min_efficiency=50):
        """Find models with high cost efficiency scores."""
        cmd = [
            "python3", f"{self.skill_path}/scripts/run.py",
            "analyze", "--min-efficiency", str(min_efficiency), "--format", "json"
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return json.loads(result.stdout)

# Example usage
intelligence = ModelIntelligence()

# Get best coding models
coding_models = intelligence.get_task_recommendations("coding", top_n=3)
print("Top coding models:")
for model in coding_models:
    print(f"  {model['model']}: {model['task_score']}/100 ({model['cost_efficiency']:.2f} efficiency)")

# Check specific model
gpt4o_info = intelligence.get_model_capabilities("gpt-4o")
print(f"\nGPT-4o capabilities: {gpt4o_info['capabilities']}")
```

## 6. Cost Budget Management

Set up automatic budget alerts and model downgrading:

```bash
#!/bin/bash
# budget-monitor.sh

MONTHLY_BUDGET=100.00  # USD
CURRENT_SPEND=$(openclaw usage --month --json | jq '.total_cost')

if (( $(echo "$CURRENT_SPEND > $MONTHLY_BUDGET * 0.8" | bc -l) )); then
    echo "⚠️  Approaching budget limit ($CURRENT_SPEND / $MONTHLY_BUDGET)"
    
    # Switch to more cost-efficient models
    EFFICIENT_MODEL=$(python3 skills/model-benchmarks/scripts/run.py recommend --task general --sort efficiency | head -1)
    
    openclaw config set agents.defaults.model.primary "$EFFICIENT_MODEL"
    echo "🔄 Switched to cost-efficient model: $EFFICIENT_MODEL"
fi
```

These examples demonstrate how to integrate Model Benchmarks into your OpenClaw workflow for maximum cost optimization and performance!