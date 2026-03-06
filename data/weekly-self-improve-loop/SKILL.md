---
name: weekly-self-improve-loop
description: Weekly review of memory and blocked items. Extract friction patterns, create skills, and update autonomy baseline.
---

# Weekly Self-Improve Loop

Weekly review for continuous improvement.

## Problem

Without regular review:
- Same mistakes repeat
- Friction patterns unnoticed
- Skills don't evolve
- Autonomy degrades

## Workflow

### 1. Weekly Review (Every 7 Days)

```powershell
# Get last 7 days of memory
$startDate = (Get-Date).AddDays(-7)
$memoryFiles = Get-ChildItem "memory/" -Filter "*.md" | 
    Where-Object { $_.LastWriteTime -ge $startDate }

# Aggregate metrics
$totalTasks = 0
$completedTasks = 0
$blockedTasks = 0
$patterns = @{}

foreach ($file in $memoryFiles) {
    $content = Get-Content $file.FullName -Raw
    
    # Count tasks
    $totalTasks += ([regex]::Matches($content, "Task:")).Count
    $completedTasks += ([regex]::Matches($content, "Status: complete")).Count
    $blockedTasks += ([regex]::Matches($content, "Blocker:")).Count
    
    # Extract patterns
    $blockers = [regex]::Matches($content, "Blocker: (.+)")
    foreach ($b in $blockers) {
        $key = $b.Groups[1].Value
        $patterns[$key] = $patterns[$key] + 1
    }
}

# Calculate rates
$completionRate = [math]::Round(($completedTasks / $totalTasks) * 100, 1)
$blockerRate = [math]::Round(($blockedTasks / $totalTasks) * 100, 1)
```

### 2. Pattern Extraction

```powershell
# Find top friction patterns
$topPatterns = $patterns.GetEnumerator() | 
    Sort-Object Value -Descending | 
    Select-Object -First 3

foreach ($p in $topPatterns) {
    Write-Host "Pattern: $($p.Key) ({$p.Value} occurrences)"
    
    # Create or update skill
    $skillName = $p.Key -replace '[^a-z]', '-' -replace '-+', '-'
    $skillPath = "skills/local/$skillName-recovery"
    
    if (Test-Path $skillPath) {
        Write-Host "  Updating existing skill..."
    } else {
        Write-Host "  Creating new skill..."
        # Create skill (see memory-to-skill-crystallizer)
    }
}
```

### 3. Report Generation

```markdown
## Weekly Report (YYYY-MM-DD)

**Metrics**:
- Total tasks: X
- Completion rate: Y%
- Blocker rate: Z%

**Top Friction Patterns**:
1. Pattern A (N occurrences)
2. Pattern B (N occurrences)
3. Pattern C (N occurrences)

**New Skills Created**:
- skill-name-1
- skill-name-2

**Next Week Focus**:
- Address pattern A with automated fix
- Review skill effectiveness
```

## Executable Completion Criteria

| Criteria | Verification |
|----------|-------------|
| Review executed | Report file created |
| Metrics calculated | Completion/blocker rates present |
| Patterns extracted | Top 3 patterns identified |
| Skills created/updated | At least 1 skill actioned |

## Privacy/Safety

- Aggregate data only (no specifics)
- Rates and counts, not content
- Local report (not published)

## Self-Use Trigger

Use when:
- Day of week = Sunday (or configured)
- Manual review requested
- After major project completion

---

**Review weekly. Improve continuously.**
