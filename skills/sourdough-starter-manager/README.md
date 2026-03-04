# 🍞 Sourdough Starter Manager

An OpenClaw skill for maintaining healthy sourdough starters with intelligent feeding schedules, precise calculations, and expert troubleshooting.

## What This Skill Does

The Sourdough Starter Manager transforms your AI assistant into a sourdough expert that helps you:

- **Calculate perfect feeding ratios** for any situation
- **Generate feeding schedules** for daily maintenance or pre-bake preparation  
- **Troubleshoot starter problems** with expert diagnosis and recovery protocols
- **Convert between hydration levels** (100%, 75%, etc.)
- **Plan baking timelines** to have starter ready exactly when you need it
- **Track starter health** with clear indicators and monitoring
- **Store starters properly** for vacations or long breaks

## Installation

### Via ClawHub CLI (Recommended)

```bash
# Search for the skill
clawhub search sourdough

# Install
clawhub install sourdough-starter-manager
```

### Manual Installation

1. Create the skill directory:
```bash
mkdir -p ~/.openclaw/skills/sourdough-starter-manager
```

2. Copy `SKILL.md` to the directory:
```bash
cp SKILL.md ~/.openclaw/skills/sourdough-starter-manager/
```

3. Restart OpenClaw or reload skills:
```bash
openclaw reload-skills
```

## Usage Examples

### Basic Feeding
```
You: I need to feed my starter. I have 50g left.
AI: For daily maintenance, I recommend a 1:1:1 ratio feeding:
    - 50g starter (what you have)
    - 50g flour
    - 50g water
    Total: 150g starter after feeding
    
    Timeline: Feed now, it'll be ready in 4-8 hours at room temperature...
```

### Baking Preparation
```
You: I want to bake on Saturday morning. My recipe needs 200g of active starter.
AI: Let me create a preparation timeline for you:

    Thursday Evening (8 PM):
    - Take starter from fridge
    - Feed 1:2:2 ratio (30g starter + 60g flour + 60g water)
    
    Friday Evening (8 PM):
    - Discard down to 50g
    - Feed 1:3:3 ratio (50g starter + 150g flour + 150g water)
    - This gives you 350g total
    
    Saturday Morning (6-8 AM):
    - Starter should be at peak rise
    - Use 200g for your recipe
    - Feed the remaining 150g and return to fridge...
```

### Troubleshooting
```
You: My starter has liquid on top and smells weird
AI: The liquid (hooch) means your starter is hungry. Here's what to do:

    1. Pour off the liquid or stir it back in
    2. Discard all but 50g of starter
    3. Feed with 1:2:2 ratio for extra food:
       - 50g starter + 100g flour + 100g water
    4. Feed every 12 hours for the next 3 days
    5. Monitor for sweet-sour smell and doubling
    
    Your starter should be back to full health in 3-4 days...
```

### Hydration Conversion
```
You: How do I convert my 100% hydration starter to 75%?
AI: Here's how to convert 100g of your 100% starter to 75% hydration:

    Your current starter:
    - 50g flour + 50g water = 100% hydration
    
    To convert to 75%:
    - Keep the 50g flour
    - Reduce water to 37.5g (75% of 50g)
    
    Practical method:
    1. Take 100g of your starter
    2. Add 13g flour
    3. Mix well
    4. You now have ~113g at 75% hydration...
```

## Features

### Smart Calculations
- Automatic hydration percentage calculations
- Feeding ratio conversions (1:1:1, 1:2:2, etc.)
- Target amount back-calculations
- Temperature-adjusted timelines

### Health Monitoring
- Visual indicators (bubbles, rise, texture)
- Smell diagnostics (sweet-sour vs. acetone vs. mold)
- Float test guidance
- Recovery protocols for weak starters

### Timeline Planning
- Same-day baking preparation
- Multi-day advance planning
- Temperature-adjusted schedules
- Contingency planning

### Storage Solutions
- Refrigeration protocols (1-4 weeks)
- Dehydration method (long-term)
- Revival instructions
- Vacation planning

## Requirements

- **OpenClaw**: Compatible with OpenClaw 2.0+
- **Dependencies**: None - pure knowledge skill
- **API Keys**: Not required
- **External Tools**: Not required

## Skill Structure

```
sourdough-starter-manager/
├── SKILL.md           # Main skill definition
└── README.md          # This file
```

## Configuration

No configuration needed! This is a pure knowledge skill that doesn't require any API keys or external services.

If you want to customize when this skill is triggered, you can add this to your `~/.openclaw/openclaw.json`:

```json
{
  "skills": {
    "entries": {
      "sourdough-starter-manager": {
        "enabled": true
      }
    }
  }
}
```

## Use Cases

Perfect for:
- **Home Bakers**: Maintain a healthy starter with minimal effort
- **Beginner Sourdoughers**: Learn the fundamentals with expert guidance
- **Busy Bakers**: Quick calculations and timeline planning
- **Weekend Bakers**: Perfect preparation schedules
- **Travelers**: Storage and revival protocols
- **Troubleshooters**: Diagnose and fix starter problems

## Why This Skill?

Sourdough starters require consistent care and understanding, but the math and timing can be confusing. This skill:

1. **Removes the guesswork** from feeding calculations
2. **Prevents common mistakes** with expert troubleshooting
3. **Saves time** with instant ratio calculations
4. **Reduces waste** with precise amount targeting
5. **Builds confidence** through clear explanations
6. **Adapts to your schedule** with flexible timelines

## Contributing

Found a bug or have a suggestion? Contributions welcome!

1. Fork the repository
2. Create a feature branch
3. Submit a pull request with your improvements

## Tips for Best Results

1. **Provide context**: "I have 50g of starter" vs. just "how do I feed it"
2. **Mention your schedule**: "I want to bake Saturday morning"
3. **Describe issues clearly**: "liquid on top, sour smell" vs. "something's wrong"
4. **Include temperature**: Room temp affects all timelines
5. **Ask follow-ups**: The skill adapts to conversation flow

## Version History

- **v1.0.0** (February 2026): Initial release
  - Core feeding calculations
  - Hydration conversions
  - Troubleshooting guide
  - Baking preparation timelines
  - Storage protocols

## License

MIT License - Feel free to use, modify, and share!

## Author

Created by AM for the OpenClaw community.

## Acknowledgments

Built on the collective wisdom of sourdough bakers worldwide and years of fermentation science.

---

**Happy Baking! 🍞**

*May your starter rise strong and your bread be delicious!*
