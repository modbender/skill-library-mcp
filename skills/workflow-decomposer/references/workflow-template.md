# Workflow Decomposition Template

## Standard Output Format

Every task decomposition must include these three required elements:

### 1. Task Decomposition Model

Always state which model performed the decomposition:

```
**Decomposition Model:** `bailian/qwen3.5-plus`
```

### 2. Current Workflow Step

Track progress with step numbers:

```
**Current Step:** 2 of 5 - Setting up project structure
```

### 3. Current Step Model

State which model is executing the current step:

```
**Current Step Model:** `bailian/qwen3.5-plus`
```

## Complete Status Block

```markdown
## Workflow Status

**Decomposition Model:** `bailian/qwen3.5-plus`
**Current Step:** 2 of 5 - Setting up project structure
**Current Step Model:** `bailian/qwen3.5-plus`
**Status:** in-progress

### Steps

- [x] **Step 1:** Analyze requirements ✅ - Model: `bailian/qwen3.5-plus`
- [~] **Step 2:** Setting up project structure 🔄 - Model: `bailian/qwen3.5-plus`
- [ ] **Step 3:** Implement core logic - Model: `bailian/qwen3.5-plus`
- [ ] **Step 4:** Write tests - Model: `bailian/qwen3.5-plus`
- [ ] **Step 5:** Documentation - Model: `bailian/qwen3.5-plus`
```

## Step Decomposition Format

Each step should include:

```markdown
### Step X: <Step Name>

**Model:** <selected-model>
**Dependencies:** <what must be complete before this>
**Description:** <detailed, actionable description>
**Expected Output:** <clear completion criteria>
**Estimated Complexity:** <low|medium|high>
```

## Stuck Step Report Format

When a step is blocked:

```markdown
## ⚠️ Step X Blocked

**Issue:** <what's preventing progress>

**Cause:** <root cause analysis>

**Solutions:**
1. <solution 1>
2. <solution 2>
3. <solution 3>

**Recommendation:** <best option with reasoning>

**Current Step Model:** <model that encountered the issue>
```

## Example: Full Decomposition

```markdown
## Task: Build a weather dashboard

**Decomposition Model:** `bailian/qwen3.5-plus`

### Analysis

Building a weather dashboard requires:
- Frontend UI components
- API integration with weather service
- Data display and updates
- Responsive design

### Steps

- [ ] **Step 1:** Project setup and dependencies
  - Model: `bailian/qwen3.5-plus`
  - Output: Initialized project with package.json
  
- [ ] **Step 2:** Create UI components
  - Model: `bailian/qwen3.5-plus`
  - Output: React components for weather display
  
- [ ] **Step 3:** Integrate weather API
  - Model: `bailian/qwen3.5-plus` (with web_fetch)
  - Output: Working API calls with error handling
  
- [ ] **Step 4:** Connect UI to data
  - Model: `bailian/qwen3.5-plus`
  - Output: Live weather display
  
- [ ] **Step 5:** Styling and polish
  - Model: `bailian/qwen3.5-plus`
  - Output: Responsive, styled dashboard
```

## Best Practices

1. **Be specific** - "Set up React project" not "Do the setup"
2. **Make steps independent** - Each should be verifiable alone
3. **Note dependencies** - What must come before
4. **Select appropriate models** - Match model to task type
5. **Track progress visibly** - Always show current step
6. **Report blockers early** - Don't let steps stall silently
