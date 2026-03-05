"""
LLM prompt templates for SRE Agent.

These prompts are used for:
- Root cause analysis
- Incident summarization
- Remediation suggestions
"""

# Root Cause Analysis Prompt
RCA_PROMPT = """You are an expert SRE analyzing a system anomaly. Analyze the following information and provide root cause insights.

## Anomaly Details
- **Metric**: {metric_name}
- **Category**: {category}
- **Current Value**: {current_value:.4f}
- **Baseline Value**: {baseline_value:.4f}
- **Deviation**: {deviation:.2f} sigma ({deviation_percent:+.1f}%)
- **Severity**: {severity}
- **Duration**: {duration_minutes} minutes
- **Type**: {anomaly_type}

## Current Hypotheses
{hypotheses}

## Recent Logs
{logs}

## Recent Events
{events}

## Correlated Anomalies
{correlated}

Based on this information:
1. What is the most likely root cause?
2. What additional evidence should we look for?
3. What immediate action should be taken?
4. What is the potential business impact?

Keep your response concise and actionable (max 300 words).
"""

# Incident Summary Prompt
INCIDENT_SUMMARY_PROMPT = """Summarize the following incident for a post-mortem report.

## Incident Details
- **ID**: {incident_id}
- **Started**: {started_at}
- **Resolved**: {resolved_at}
- **Duration**: {duration_minutes} minutes
- **Severity**: {severity}

## Affected Metrics
{affected_metrics}

## Root Cause
{root_cause}

## Actions Taken
{actions}

## Resolution
{resolution}

Provide a concise incident summary including:
1. Impact assessment (1-2 sentences)
2. Timeline of key events
3. Root cause (1-2 sentences)
4. Resolution steps
5. Recommendations for prevention

Format as a structured report suitable for stakeholders.
"""

# Remediation Suggestion Prompt
REMEDIATION_PROMPT = """Based on the anomaly analysis, suggest appropriate remediation actions.

## Anomaly
- **Metric**: {metric_name}
- **Root Cause**: {root_cause}
- **Severity**: {severity}
- **Affected Services**: {services}

## Available Actions
{available_actions}

## Constraints
- Max risk tolerance: {max_risk}
- Auto-remediation enabled: {auto_enabled}
- Current time: {current_time}

Suggest the most appropriate remediation:
1. Recommended action(s) in order of priority
2. Expected outcome
3. Potential risks
4. Rollback procedure if needed

Be specific and actionable.
"""

# Knowledge Base Query Prompt
KNOWLEDGE_QUERY_PROMPT = """You are helping search a knowledge base of past incidents.

## Current Anomaly
- **Metric**: {metric_name}
- **Symptoms**: {symptoms}
- **Severity**: {severity}

Generate 3 search queries to find similar past incidents:
1. A query focusing on the specific metric and symptoms
2. A query focusing on the root cause pattern
3. A broader query for similar impact scenarios

Output as JSON array of strings.
"""

# Alert Message Templates
ALERT_TEMPLATES = {
    "anomaly_detected": """
🚨 **{severity} Anomaly Detected**

**Metric**: {metric_name}
**Category**: {category}
**Current**: {current_value:.4f} ({unit})
**Baseline**: {baseline_value:.4f}
**Deviation**: {deviation:.2f}σ ({deviation_percent:+.1f}%)
**Duration**: {duration_minutes} min

{context}
""",

    "prediction_warning": """
⚠️ **Trend Warning**

**Metric**: {metric_name}
**Current**: {current_value:.4f}
**Predicted**: {predicted_value:.4f} (in {eta_hours:.1f}h)
**Threshold**: {threshold:.4f}

Action recommended to prevent threshold breach.
""",

    "remediation_started": """
🔧 **Remediation Started**

**Plan ID**: {plan_id}
**Action**: {action_type}
**Target**: {target}
**Risk Level**: {risk_level}

Executing {step_count} step(s)...
""",

    "remediation_complete": """
✅ **Remediation Complete**

**Plan ID**: {plan_id}
**Status**: {status}
**Duration**: {duration}s

{summary}
""",

    "approval_required": """
🔐 **Approval Required**

**Plan ID**: {plan_id}
**Action**: {action_type}
**Target**: {target}
**Risk Score**: {risk_score:.2f}

**Root Cause**: {root_cause}

Requires {approvals_required} approval(s) within {timeout_minutes} minutes.

Approve: `POST /api/v1/approvals/{plan_id}/approve`
Reject: `POST /api/v1/approvals/{plan_id}/reject`
""",
}


def format_rca_prompt(
    metric_name: str,
    category: str,
    current_value: float,
    baseline_value: float,
    deviation: float,
    deviation_percent: float,
    severity: str,
    duration_minutes: int,
    anomaly_type: str,
    hypotheses: list[str],
    logs: list[str],
    events: list[str],
    correlated: list[str],
) -> str:
    """Format the RCA prompt with actual values."""
    return RCA_PROMPT.format(
        metric_name=metric_name,
        category=category,
        current_value=current_value,
        baseline_value=baseline_value,
        deviation=deviation,
        deviation_percent=deviation_percent,
        severity=severity,
        duration_minutes=duration_minutes,
        anomaly_type=anomaly_type,
        hypotheses="\n".join(f"- {h}" for h in hypotheses) if hypotheses else "- No strong hypotheses yet",
        logs="\n".join(f"- {log}" for log in logs[:10]) if logs else "No relevant logs",
        events="\n".join(f"- {event}" for event in events[:10]) if events else "No recent events",
        correlated="\n".join(f"- {c}" for c in correlated) if correlated else "None detected",
    )


def format_alert(
    template_name: str,
    **kwargs,
) -> str:
    """Format an alert message using a template."""
    template = ALERT_TEMPLATES.get(template_name)
    if not template:
        raise ValueError(f"Unknown alert template: {template_name}")
    return template.format(**kwargs).strip()
