# PMP-Agentclaw — For Non-Technical Users 🎯

## What Is This?

A simple tool to check if your project is on track, over budget, or at risk.

Think of it like a **health checker** for your projects.

---

## What Can It Do?

### 1. 🚦 Project Health Check
**Tells you:** Are we on time? On budget? In trouble?

**Example:**
```bash
node dist/cli/calc-evm.js 10000 5000 4500 4800
```
**Result:** 🟡 Yellow — "Watch out, spending too much!"

---

### 2. ⚠️ Risk Check  
**Tells you:** How dangerous is this problem?

**Example:**
```bash
node dist/cli/score-risks.js 3 4
```
**Result:** 🟡 Yellow — "Keep an eye on it"

---

### 3. 📅 When Will We Finish?
**Tells you:** Based on your speed, when will the project end?

**Example:**
```bash
node dist/cli/calc-velocity.js 34 28 42 --forecast 200
```
**Result:** "At this speed, you'll finish in about 6 weeks"

---

## Traffic Light System

| Color | Means | Action |
|-------|-------|--------|
| 🟢 **Green** | All good! | Keep going |
| 🟡 **Yellow** | Pay attention | Fix small problems |
| 🔴 **Red** | Emergency! | Stop and fix now |

---

## How to Use

1. **Open terminal** (the black box that types commands)
2. **Go to this folder:** `cd ~/Desktop/PMP-Agentclaw`
3. **Run a command** (see examples above)
4. **Look for 🟢 🟡 or 🔴**

---

## Need Help?

- **Too technical?** See `SIMPLE_GUIDE.md` for even simpler instructions
- **Commands not working?** Make sure you ran `npm run build` first
- **Still stuck?** Ask Bob (your AI assistant)

---

*No programming needed. Just copy, paste, and change the numbers!*
