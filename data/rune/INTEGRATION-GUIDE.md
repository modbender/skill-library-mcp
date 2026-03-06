# RUNE INTEGRATION GUIDE - Critical for Success

## ⚠️ WARNING: Installation Alone Is Insufficient

**Common Mistake**: Installing Rune CLI but never integrating it into daily workflow.

**Result**: Sophisticated memory system sits unused, providing zero value.

**Solution**: Mandatory workflow integration with forcing functions.

## 🚨 Why This Guide Exists

**Our Experience**: We built a complete memory system, stored 177+ facts, and then completely ignored it for weeks because we never integrated it into our actual workflow.

**Lesson**: Tools without workflow integration are just fancy unused software.

## 📋 MANDATORY INTEGRATION CHECKLIST

### 1. Basic Installation
```bash
# Install the CLI
./install.sh

# Verify installation
rune --version
```

### 2. CRITICAL: Workflow Integration
```bash
# This is the step most people skip!
./setup-workflow.sh
```

### 3. Test Memory System
```bash
# Add test fact
rune add test "integration.working" "Memory system is integrated" --tier working

# Recall test fact  
rune recall "integration"

# Should show your test fact - if not, integration failed
```

### 4. Session Start Automation
```bash
# Run this at the start of every work session
~/.openclaw/workspace/scripts/session-start.sh
```

### 5. Context Injection Before Work
```bash
# Before responding to any substantial request
~/.openclaw/workspace/scripts/context-inject.sh "topic_keywords"
```

## 🔄 DAILY WORKFLOW EXAMPLE

### Bad Workflow (What NOT to Do)
```
1. User asks question
2. Respond immediately without context
3. Forget to store important decisions  
4. Lose project continuity
5. Memory system goes unused
```

### Good Workflow (Mandatory Process)
```
1. User asks question
2. Recall relevant context: `rune recall "project_name topic"`
3. Inject context: Use recalled information in response  
4. Store decisions: `rune add decision "key" "what we decided"`
5. Update project status: `rune add project "name.status" "current state"`
```

## 🧠 MEMORY CATEGORIES

### Essential Categories to Use
```bash
# Decisions (critical for continuity)
rune add decision "project.architecture" "chose SQLite for simplicity" --tier long-term

# Project status (prevents context loss)
rune add project "myapp.status" "deployed to production" --tier working

# Lessons learned (institutional memory)
rune add lesson "deployment.issues" "always test backup restore" --tier long-term

# People context (relationship management)  
rune add person "client.preferences" "prefers email over Slack" --tier long-term

# Tool configurations (environment memory)
rune add tool "database.connection" "localhost:5432 with SSL required" --tier working
```

## 🚨 FAILURE INDICATORS

### Signs You're NOT Using Memory Properly
- [ ] Giving "cold start" responses without context
- [ ] Asking for information previously provided
- [ ] Repeating explanations of recent work
- [ ] Lost project continuity between sessions
- [ ] Making decisions without considering past choices
- [ ] No growth in institutional knowledge

### Signs You ARE Using Memory Properly  
- [x] Starting responses with relevant recalled context
- [x] Building on previous conversations seamlessly  
- [x] Referencing past decisions in new work
- [x] Growing knowledge base over time
- [x] Never losing project context
- [x] Making informed decisions based on history

## 🔧 TROUBLESHOOTING

### "I installed it but never use it"
**Problem**: No forcing functions in your workflow  
**Solution**: Set up automation that requires memory checks before work

### "I forget to store things"  
**Problem**: Storage is manual and optional  
**Solution**: Create decision capture templates and make storage automatic

### "Context recall returns nothing"
**Problem**: Either nothing stored or search terms don't match  
**Solution**: Use broader search terms, check `rune stats` for fact count

### "System feels too complex"
**Problem**: Trying to use every feature instead of starting simple  
**Solution**: Start with just decisions and project status, expand gradually

## 🎯 SUCCESS METRICS

### Weekly Goals
- [ ] Memory used for 80%+ of substantial responses  
- [ ] At least 5 new facts stored per week
- [ ] Zero instances of repeating recent explanations
- [ ] Project context maintained across all sessions

### Monthly Goals
- [ ] 50+ new facts in memory system
- [ ] Demonstrable improvement in response quality
- [ ] Clear institutional memory patterns emerging
- [ ] Other people can query your memory for project context

## 📚 ADVANCED USAGE

### Context-Rich Responses
Instead of: "Let me check the project status..."  
Do this: "Based on our last decision to use SQLite and the current production deployment status, here's what we should do next..."

### Institutional Memory Building
```bash
# Capture patterns
rune add lesson "client.communication" "always follow up emails with Slack pings" --tier long-term

# Build decision trees
rune add decision "architecture.database" "PostgreSQL for >10GB, SQLite for smaller" --tier long-term

# Track what works
rune add tool "deployment.success" "Vercel works well for Next.js, use Railway for APIs" --tier long-term
```

## 💡 META-LESSON

**The memory system is only as good as your discipline in using it.**

Building the tool was 20% of the work.  
Building the habit is 80% of the value.

---

**Don't be like us: Use the memory system you install.**