# 🚀 Taskline AI - Installation Guide

**Complete setup guide for AI-powered task management through [MyTaskline.com](https://mytaskline.com)**

## 📋 Prerequisites

- **Python 3.7+** with `requests` module  
- **Internet connection** for MyTaskline.com API access
- **5 minutes** for complete setup

## 🌟 Step 1: Get Your MyTaskline.com Account

### **Create Account**
1. Visit [**mytaskline.com**](https://mytaskline.com)
2. Sign up for your free account
3. Verify your email and log in

### **Generate API Key**  
1. Navigate to **Settings** in your dashboard
2. Click **API Keys** section
3. Click **"Generate New API Key"**
4. Copy the generated key (keep it secure!)

> **🔒 Security Note**: Your API key provides full access to your tasks. Keep it private and never share it.

## ⚙️ Step 2: Configure the Skill

### **Edit Configuration**
1. Open `references/config.json` in the skill directory
2. Replace the placeholder with your actual API key:

```json
{
  "baseUrl": "https://mytaskline.com/api/v1",
  "apiKey": "your-actual-api-key-here",
  "timezone": "America/Denver"
}
```

### **Optional: Update Timezone**
Change the timezone to match your location:
- **US Eastern**: `"America/New_York"`
- **US Central**: `"America/Chicago"`  
- **US Mountain**: `"America/Denver"`
- **US Pacific**: `"America/Los_Angeles"`
- **UTC**: `"UTC"`

## 🧪 Step 3: Test Your Installation

### **Basic Functionality Test**
```bash
# Test 1: Simple task creation
python taskline.py "Add task: test my AI system"

# Expected output: ✅ Task created with full details
```

### **AI Intelligence Test**
```bash
# Test 2: Complex AI parsing  
python taskline.py "Create high priority task for TestProject: implement login feature by tomorrow"

# Expected output: 
# - Task created with high priority
# - Due date set to tomorrow  
# - TestProject auto-created
# - Full AI processing details shown
```

### **Query Test**
```bash
# Test 3: Intelligent reporting
python taskline.py "What tasks do I have?"

# Expected output: List of your tasks with formatting
```

## ✅ Verification Checklist

### **Configuration Check**
- [ ] API key correctly set in `references/config.json`
- [ ] No placeholder text remains (`YOUR_MYTASKLINE_API_KEY_HERE`)
- [ ] Timezone matches your location

### **Functionality Check**  
- [ ] Simple task creation works
- [ ] AI parsing processes complex requests
- [ ] Task queries return results
- [ ] Date intelligence works ("tomorrow", "Friday")
- [ ] Priority detection works ("high priority")

### **MyTaskline.com Dashboard Check**
- [ ] Tasks appear in your [mytaskline.com](https://mytaskline.com) dashboard
- [ ] Projects are auto-created when referenced  
- [ ] Task details match what you specified

## 🚀 Advanced Examples

Once basic installation works, try these advanced AI features:

### **Multi-Entity Parsing**
```bash
python taskline.py "Ask Jennifer to handle Mobile project deployment by Friday with high priority and include Mike as stakeholder"
```

### **Smart Date Intelligence**
```bash
python taskline.py "Deploy API updates by end of week"
python taskline.py "Create task due next Monday: review documentation"
```

### **Project Auto-Creation**
```bash
python taskline.py "Add urgent task for NewProduct project: create landing page mockup"
# → Creates NewProduct project automatically if it doesn't exist
```

### **Intelligent Analytics**
```bash
python taskline.py "What's overdue?"
python taskline.py "Show my task summary"
python taskline.py "What's in the Mobile project?"
```

## 🔧 Troubleshooting

### **"API Error 401: Unauthorized"**
- **Issue**: Invalid or missing API key
- **Solution**: 
  1. Check your API key in `references/config.json`
  2. Verify key is correct by logging into [mytaskline.com/settings](https://mytaskline.com/settings)
  3. Ensure no extra spaces or quotes around the key

### **"No tasks found"**
- **Issue**: No tasks in your account yet
- **Solution**: Create a test task first:
  ```bash
  python taskline.py "Add task: my first AI task"
  ```

### **"Script not found"**
- **Issue**: Running from wrong directory or missing files
- **Solution**: 
  1. Ensure you're in the skill directory
  2. Check all files are present (see file structure below)
  3. Verify script permissions: `chmod +x *.py scripts/*.py`

### **"Module not found: requests"**
- **Issue**: Missing Python requests module
- **Solution**: Install with `pip install requests`

### **Date parsing not working**
- **Issue**: Timezone mismatch or ambiguous dates
- **Solution**: 
  1. Update timezone in `config.json`
  2. Use clearer date references ("next Friday" vs "Friday")

## 📁 Required File Structure

Verify all files are present:

```
taskline-ai-skill/
├── taskline.py                    # Main entry point ✅
├── SKILL.md                       # Skill definition ✅  
├── README.md                      # Documentation ✅
├── INSTALL.md                     # This file ✅
├── scripts/
│   ├── taskline_ai.py            # AI dispatcher ✅
│   ├── create_task_enhanced.py   # Enhanced creation ✅
│   ├── create_task_smart.py      # Smart creation ✅
│   ├── create_task.py            # Basic creation ✅
│   ├── list_tasks.py             # Task queries ✅
│   ├── update_task.py            # Status updates ✅
│   └── reports.py                # Analytics ✅
└── references/
    ├── config.json               # Configuration ✅
    └── api_examples.md           # API docs ✅
```

## 🎯 Success Indicators

**You're ready to go when:**

1. ✅ **Task creation works**: AI parses complex requests
2. ✅ **Projects auto-create**: Referenced projects appear in MyTaskline.com  
3. ✅ **Dates parse correctly**: "tomorrow", "Friday" become proper dates
4. ✅ **Priorities detected**: "high priority" sets priority field
5. ✅ **Dashboard syncs**: Tasks appear on [mytaskline.com](https://mytaskline.com)

## 🌟 Next Steps

### **Explore AI Features**
- Try complex multi-entity requests
- Experiment with different date formats
- Test people assignment ("Ask John to...")
- Use priority keywords ("urgent", "high", "low")

### **Integrate with OpenClaw**  
- Set up voice commands for task creation
- Create automation workflows
- Build custom integrations

### **Optimize Your Workflow**
- Customize the timezone setting
- Learn advanced query patterns
- Use the MyTaskline.com dashboard for visual management

---

**🎉 You're all set!** Start managing tasks with AI intelligence through [MyTaskline.com](https://mytaskline.com)!

**Need help?** Visit [mytaskline.com](https://mytaskline.com) for platform support.