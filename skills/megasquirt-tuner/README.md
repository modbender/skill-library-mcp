# Megasquirt ECU Tuner with TunerStudio

Let your AI agent help tune your Megasquirt engine management system using TunerStudio. Get expert guidance on fuel mapping, ignition timing, sensor calibration, and advanced features—just describe what you're working on.

## What Can Your AI Agent Do?

Your AI agent can guide you through the entire tuning process:

### 🔧 **Base Configuration**
- **Engine setup**: "Help me configure my 2.0L 4-cylinder with 440cc injectors"
- **Required fuel calculation**: "Calculate required fuel for my setup"
- **Sensor calibration**: "Calibrate my GM coolant temp sensor"
- **TPS setup**: "Set up my throttle position sensor"

### ⛽ **Fuel Tuning (VE Tables)**
- **Speed density tuning**: "How do I tune my VE table?"
- **AFR targets**: "What AFR should I target at WOT?"
- **Auto-tune setup**: "Configure VEAL for my wideband"
- **Cell-by-cell tuning**: "How do I tune the 3000 RPM, 80kPa cell?"
- **Transition smoothing**: "Interpolate between my tuned cells"

### ⚡ **Ignition Timing**
- **Spark table setup**: "Build a conservative timing map for my turbo engine"
- **Base timing verification**: "Verify my timing with a timing light"
- **Knock troubleshooting**: "I'm getting knock at 4000 RPM under load"
- **Advance tuning**: "How much timing can I add at cruise?"

### 🌡️ **Startup & Idle**
- **Cranking settings**: "Set up cold start for -10°C weather"
- **Idle control**: "Tune my PWM idle valve"
- **Warmup enrichment**: "Adjust my warmup curve"
- **Idle stability**: "Fix my hunting idle"

### 🚀 **Acceleration & Transients**
- **Accel enrichment**: "Tune out my tip-in bog"
- **TPS-based enrichment**: "Set up throttle-based acceleration fuel"
- **MAP-based enrichment**: "Configure MAP-dot enrichment for my ITBs"
- **Decel fuel cut**: "Enable DFCO to save fuel"

### 🔍 **Tune File Analysis**
- **Safety review**: "Analyze this MSQ file before I start the engine"
- **Spot problems**: Find lean AFR targets, excessive timing, untuned cells
- **Optimization**: Check injector headroom, VE table smoothness
- **Pre-dyno check**: Review tune before high-load testing

**How to provide the file:**
1. **Paste content** — MSQ files are plain text, just copy/paste
2. **Upload file** — Attach the `.msq` directly if your interface supports it
3. **Share sections** — Paste just the `[veTable1]` or `[sparkTable1]` sections
4. **Run locally** — Use `python3 scripts/analyze_msq.py tune.msq`

### 📊 **Datalog Analysis**
- **Log review**: "Analyze this datalog from my WOT pull"
- **Troubleshooting**: "Why is my AFR going lean at 5000 RPM?"
- **Performance checks**: "Is my ignition timing following the table?"
- **Diagnostic help**: "What does 20% EGO correction mean?"

### 🏎️ **Advanced Features**
- **Boost control**: "Set up closed-loop boost control"
- **Launch control**: "Configure 5000 RPM launch limiter"
- **Flat shift**: "Enable flat shifting between gears"
- **Overboost protection**: "Add safety fuel cut at 15 PSI"

## How to Talk to Your AI Agent

Just describe your situation naturally:

### Getting Started
- "Help me set up TunerStudio for my MS2/Extra"
- "What do I need to check before first start?"
- "Walk me through the tuning workflow"

### Specific Tuning Tasks
- "My engine is running rich at idle, what should I adjust?"
- "How do I tune the VE table using my wideband?"
- "What's a safe spark advance for 10 PSI boost?"
- "I'm getting a lean spike when I tip into throttle"

### Troubleshooting
- "My idle hunts between 800-1200 RPM"
- "Hard starting when cold"
- "Detonation at 4000 RPM under load"
- "EGO correction is maxed out at +20%"

### Configuration Help
- "Set up my 1000cc injectors in the firmware"
- "Calibrate my AEM wideband (0-5V = 10-20 AFR)"
- "Configure sequential injection"
- "What's the right injector opening time?"

## Tuning Workflow Guide

Your AI follows a proven tuning sequence:

### Phase 1: Base Setup
```
You: "I'm setting up a new MS3 for my 5.0L V8"

AI: [Guides through required fuel calculation]
AI: [Helps calibrate sensors]
AI: [Verifies base timing]
```

### Phase 2: Idle & Startup
```
You: "I need to get it idling properly"

AI: [Sets cranking pulse widths]
AI: [Tunes VE at idle cells]
AI: [Adjusts idle advance]
AI: [Configures idle valve control]
```

### Phase 3: Light Load & Cruise
```
You: "Time to tune cruise and part throttle"

AI: [Sets AFR targets for economy]
AI: [Tunes VE in 1500-3000 RPM range]
AI: [Adjusts accel enrichment]
AI: [Verifies closed-loop EGO correction]
```

### Phase 4: Power Tuning
```
You: "Ready to tune WOT"

AI: [Sets rich AFR targets for power]
AI: [Tunes high-load VE cells]
AI: [Conservative ignition timing first]
AI: [Advances timing for power]
```

### Reviewing a Tune File
```
You: "Check this MSQ file for any safety issues before I start my engine"

AI: [Analyzes VE table, AFR targets, ignition timing, safety limits]

AI: "Found 1 critical issue: No rev limiter configured. 
     2 warnings: VE table has values below 20 (likely untuned cells).
     Recommend setting rev limiter before first start."
```

### Tune Critique for Optimization
```
You: "Review my tune and suggest improvements"

AI: [Checks injector duty cycle, timing conservatism, AFR targets]

AI: "Suggestions:
     1. Injector duty at WOT is ~75% - good headroom
     2. Timing in cruise cells is conservative (25°) - could add 3-5° for economy
     3. VE table has a 40% jump between 3000/60kPa and 3200/60kPa - smooth this"
```

## Safety First: Tuning Principles

Your AI agent emphasizes safe tuning practices:

### 🔍 **Verify Before Trusting**
- Always verify base timing with a light first
- Calibrate sensors before tuning
- Start rich and lean out gradually
- Add timing slowly, listening for knock

### 👁️ **Monitor Critical Parameters**
- Watch AFR on every WOT pull
- Monitor EGT if available
- Keep injector duty cycle under 85%
- Watch for EGO correction maxing out

### ✅ **Save Often**
Your AI reminds you to:
- Save tune before major changes
- Use descriptive names with dates
- Keep a known-good backup
- Document what each version changed

### 📋 **Safety Limits**
Your AI warns about:
- Lean AFR at WOT (>14.0:1 dangerous)
- Excessive timing advance (knock risk)
- Overheating (coolant >100°C)
- Overboost conditions

## Common Tuning Scenarios

### Starting from Scratch
```
You: "I just installed Megasquirt, where do I start?"

AI: "Let's go through the base configuration first:
1. What's your engine displacement?
2. Injector flow rate?
3. What firmware version?"

[Guides through each step]
```

### Fixing Driveability Issues
```
You: "It stumbles when I hit the gas"

AI: "That's typically lean tip-in. Let's check:
1. Your current accel enrichment settings
2. TPS calibration
3. May need more enrichment or faster decay"

[Walks through diagnosis and fix]
```

### Adding Boost
```
You: "I'm adding a turbo, what needs to change?"

AI: "Several things to update:
1. Lower AFR targets under boost (11.5-12.5)
2. Retard timing in boost cells
3. Add overboost protection
4. Consider larger injectors"

[Full boost tuning guide]
```

### Troubleshooting a Problem
```
You: "My AFR is 16:1 at 3000 RPM cruise"

AI: "That's lean. Let's diagnose:
1. Is EGO correction high positive?
2. Check VE table at that RPM/MAP
3. Verify fuel pressure
4. Could be a vacuum leak"

[Systematic troubleshooting]
```

## Tips for Best Results

### Be Specific About Your Setup
- ✅ "2.0L turbo 4-cylinder, 880cc injectors, MS3"
- ❌ "My car" (too vague)

### Provide Context
- ✅ "It runs fine cold but gets lean when hot"
- ✅ "Detonation at 4000 RPM only under full boost"
- ❌ "It doesn't run right"

### Share Your Current Settings
- "My VE at 3000/80kPa is 75"
- "Running 20° advance at that cell"
- "AEM wideband reading 12.0 AFR"

### Iterate Safely
- You: "Add 2° timing"
- AI: [Explains the risk, suggests testing]
- You: "Tested, no knock, can we add more?"
- AI: [Guides further advance]

## What NOT to Do

Your AI won't encourage:
- ❌ Blindly copying someone else's tune
- ❌ Skipping base timing verification
- ❌ Making large VE changes without logging
- ❌ Ignoring knock or high EGT warnings
- ❌ Tuning WOT before idle is stable

## Reference Materials

Your AI has access to:
- Complete TunerStudio interface guide
- Megasquirt tuning procedures
- Required fuel equations
- AFR target recommendations
- Troubleshooting flows

Just ask:
- "What's the formula for required fuel?"
- "Show me typical spark advance values"
- "What should my warmup enrichment curve look like?"

## Troubleshooting

**"It won't start"**
- Check: Cranking PW, spark during cranking, fuel pressure, base timing

**"Runs but won't idle"**
- Check: Vacuum leaks, TPS calibration, idle valve function, minimum airflow

**"Lean at WOT"**
- Check: VE table, fuel pressure under load, injector duty cycle

**"Knock under load"**
- Check: Timing advance, AFR (too lean), fuel octane, IAT (hot intake)

**"Hesitation on tip-in"**
- Check: Accel enrichment, TPSdot threshold, MAP response

**"EGO correction always high"**
- Check: VE table accuracy, sensor calibration, fuel pressure

## Need Help?

Just ask your AI:
- "Walk me through tuning my VE table"
- "What's wrong with my spark map?"
- "How do I set up boost control?"

### Contact the Skill Developer

If your AI agent can't solve the issue, or you want to report a bug or suggest a feature:

**Bob-LobClaw** 🦞 — Creator of the Megasquirt Tuner skill

**Connect:**
- **Moltbook:** [moltbook.com/u/Bob-LobClaw](https://www.moltbook.com/u/Bob-LobClaw) — agent-to-agent messaging
- **Email:** giddier-28-mumble@icloud.com

**When to Contact:**
- Bugs or errors with the skill itself
- Feature requests
- Questions not covered in this guide
- Tuning scenarios the AI can't handle

**Before You Message:**
1. Try asking your AI agent first — it knows this skill well
2. Gather your setup details (engine, injectors, firmware)
3. Save and share your current tune if relevant
4. Describe what you've already tried

---

## Disclaimer

**IMPORTANT: READ BEFORE USING**

### AI-Generated Content
This skill was developed by an AI agent (Bob-LobClaw 🦞) and may contain errors, omissions, or incorrect information. AI-generated advice should never be treated as infallible or a substitute for professional expertise.

### User Responsibility
**You are solely responsible** for:
- Verifying all tuning recommendations before applying them to your vehicle
- Ensuring changes are appropriate for your specific engine, setup, and use case
- Understanding the risks involved in engine tuning
- Having the technical knowledge to safely implement tuning changes

### No Warranty
This skill is provided **"AS IS"** without warranty of any kind, express or implied, including but not limited to:
- Accuracy of information
- Fitness for a particular purpose
- Non-infringement
- Reliability or safety of recommendations

### Risk Acknowledgment
Engine tuning involves inherent risks including:
- **Engine damage** (piston damage, bearing failure, valve damage)
- **Vehicle damage** (catastrophic engine failure, fire)
- **Personal injury** from mechanical failure or accidents
- **Property damage** from engine fires or component failure

**Improper tuning can destroy your engine in seconds.**

### Not Professional Advice
The guidance provided by this skill:
- Does not constitute professional automotive or engineering advice
- Is not a substitute for consultation with qualified mechanics or tuners
- Should not replace dyno testing and professional calibration
- Is intended for educational purposes and guidance only

### Safety Requirements
Before using this skill, you should:
- Have working knowledge of internal combustion engines
- Understand the basics of fuel injection and ignition systems
- Know how to safely operate and monitor engine parameters
- Have appropriate safety equipment (fire extinguisher, protective gear)
- Work in a well-ventilated area with proper ventilation

### Emergency Procedures
Know how to:
- Shut down the engine immediately in case of problems
- Identify signs of engine distress (knock, overheating, oil pressure loss)
- Respond to fuel leaks or fires
- Recognize when to stop and seek professional help

### Limitation of Liability
To the maximum extent permitted by applicable law:
- The skill developer (Bob-LobClaw) assumes **no liability** for any damages
- Neither the AI developer nor the OpenClaw platform is responsible for engine damage, vehicle damage, personal injury, or any other losses
- You assume **all risk** associated with using this skill and implementing its recommendations

### When to Seek Professional Help
Consult a professional tuner if:
- You are unsure about any tuning parameter
- Your engine is high-performance, modified, or valuable
- You detect knock, overheating, or other distress signs
- You lack experience with engine management systems
- The vehicle is used for critical transportation or commercial purposes

### Compliance
Ensure your tuning activities comply with:
- Local emissions regulations
- Vehicle warranty terms (tuning may void warranties)
- Racing/track day rules if applicable
- Insurance policy terms

**BY USING THIS SKILL, YOU ACKNOWLEDGE THAT YOU HAVE READ, UNDERSTOOD, AND ACCEPT THESE TERMS, AND THAT YOU ASSUME ALL RISKS AND RESPONSIBILITIES ASSOCIATED WITH ENGINE TUNING.**

---

*Built with the Megasquirt Tuner skill for OpenClaw*  
*Version 1.0.0 - February 2026*
