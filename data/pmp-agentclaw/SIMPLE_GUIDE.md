# PMP-Agentclaw — Simple User Guide
*No technical jargon, just plain English*

---

## 🎯 What Is This?

**PMP-Agentclaw** is a tool that helps you manage projects without getting lost in complicated charts and reports.

Think of it like a **smart calculator** for your projects.

---

## 🚀 Quick Commands

### 1. Check Your Project Health

**What it does:** Tells you if your project is healthy, getting sick, or in trouble.

**How to run:**
```bash
cd ~/Desktop/PMP-Agentclaw
node dist/cli/calc-evm.js 10000 5000 4500 4800
```

**What the numbers mean:**

| Number | Simple Meaning |
|--------|----------------|
| **10,000** | Total money for the project (budget) |
| **5,000** | Work we SHOULD have finished by now |
| **4,500** | Work we ACTUALLY finished |
| **4,800** | Money we ACTUALLY spent |

**What you'll see:**
```
💚 Green  = All good!
💛 Yellow = Needs attention
❤️ Red    = Emergency!
```

---

### 2. Check a Risk (What Could Go Wrong?)

**What it does:** Tells you how dangerous a problem might be.

**How to run:**
```bash
node dist/cli/score-risks.js 3 4
```

**What the numbers mean:**

| Number | Chance It Will Happen | How Bad If It Does |
|--------|----------------------|--------------------|
| **1** | Almost never | Small problem |
| **2** | Unlikely | Minor issue |
| **3** | Possible | Medium problem |
| **4** | Likely | Big problem |
| **5** | Almost certain | Disaster |

**Example:** `"Project might be late" → 3 (possible) × 4 (big problem) = 12`

**Result:**
- 1-8: 🟢 Don't worry
- 9-14: 🟡 Watch it
- 15-25: 🔴 Fix it NOW

---

### 3. Check Team Speed (Agile Projects)

**What it does:** Predicts when you'll finish based on how fast you're working.

**How to run:**
```bash
node dist/cli/calc-velocity.js 34 28 42 35 --forecast 200
```

**What the numbers mean:**
| Numbers | Meaning |
|---------|---------|
| **34, 28, 42, 35** | Work completed in last 4 weeks |
| **200** | Total work remaining |

**What you'll see:**
```
Average speed: 35 points per week
200 ÷ 35 = 5.7 weeks to finish
```

---

## 📁 What's in the Folder?

| Folder | What's Inside |
|--------|---------------|
| **dist/** | Ready-to-use programs (compiled) |
| **src/** | Source code (for developers) |
| **templates/** | Blank forms for your projects |
| **configs/** | Settings files |
| **tests/** | Tests to make sure it works |

---

## 🎯 When to Use It

### Use This When...
- ✅ You want to know if you're over budget
- ✅ You want to predict when the project will finish
- ✅ Something might go wrong and you want to know how serious
- ✅ You need to make a simple project plan

### Don't Use This When...
- ❌ You just need a simple todo list (use your phone's notes)
- ❌ The project is tiny (1-2 days)
- ❌ You don't have any budget or timeline to track

---

## 💡 Common Questions

**Q: Do I need to be a programmer?**
A: No! Just copy and paste the commands. Change the numbers for your project.

**Q: What if I get an error?**
A: Make sure you ran `npm run build` first (only once).

**Q: Can I use this for personal projects?**
A: Yes! Works for any project: home renovation, wedding planning, business launch...

**Q: What's the difference between this and a spreadsheet?**
A: This does the math automatically and gives you clear answers (Green/Yellow/Red).

---

## 🔧 Step-by-Step First Time

1. **Open your terminal** (the black box that runs commands)

2. **Go to the folder:**
   ```bash
   cd ~/Desktop/PMP-Agentclaw
   ```

3. **Build the tool** (only once):
   ```bash
   npm install
   npm run build
   ```

4. **Run a test:**
   ```bash
   node dist/cli/calc-evm.js 10000 5000 4500 4800
   ```

5. **See the results!** It will tell you 🟢 🟡 or 🔴

---

## 📞 Need Help?

**If something doesn't work:**
1. Make sure you're in the right folder (`~/Desktop/PMP-Agentclaw`)
2. Make sure you ran `npm run build`
3. Check the numbers you entered (must be actual numbers, not words)

**Still stuck?** Ask Bob (your AI assistant)!

---

## 🎬 Try These Examples

### Example 1: Birthday Party
```bash
node dist/cli/calc-evm.js 500 250 200 280
```
- Budget: $500
- Planned: $250 of work
- Actually done: $200 worth
- Actually spent: $280

**Result:** 🟡 You're spending more than planned!

---

### Example 2: Website Project
```bash
node dist/cli/calc-evm.js 10000 5000 5200 4800
```
- Budget: $10,000
- Planned: 50% complete
- Actually: 52% complete (ahead!)
- Spent: $4,800 (under budget!)

**Result:** 🟢 You're doing great! Ahead of schedule AND under budget!

---

### Example 3: Risk Assessment
```bash
node dist/cli/score-risks.js 4 5
```
- Chance: 4 out of 5 (likely)
- Impact: 5 (huge disaster)
- Score: 4 × 5 = 20

**Result:** 🔴 This is dangerous! Make a backup plan NOW!

---

## ✅ Remember

- 🟢 **Green** = Keep going
- 🟡 **Yellow** = Pay attention
- 🔴 **Red** = Stop and fix

**Simple as traffic lights!** 🚦

---

*Now go manage that project!* 🚀
