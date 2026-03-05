# 🧠 Psychology Master

**The world's most comprehensive psychology skill for AI agents** — combining learning science, cognitive psychology, marketing psychology, and human behavior optimization into one powerful toolkit.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Skill Version](https://img.shields.io/badge/version-1.0.0-green.svg)]()
[![References](https://img.shields.io/badge/references-20-purple.svg)]()
[![Scripts](https://img.shields.io/badge/scripts-3-orange.svg)]()

---

## ✨ What is this?

A production-ready AI skill that transforms any AI agent into a **psychology expert** capable of:

- 🎓 **Designing age-appropriate learning plans** (ages 3-65+) for any skill
- 📈 **Optimizing conversion funnels** using behavioral economics
- 🎯 **Creating persuasive messaging** without manipulation
- 🧪 **Analyzing marketing copy** for ethical compliance
- 👥 **Understanding human decision-making** at a deep level
- 🧩 **Building better products** with UX psychology
- 💼 **Improving team dynamics** with organizational psychology

---

## 🚀 Key Features

### 📚 20 Comprehensive Reference Modules

| Category | References | Topics Covered |
|----------|------------|----------------|
| **Learning & Development** | 5 files | Developmental psychology, skill acquisition, memory systems, neuroplasticity, sleep & circadian rhythms |
| **Marketing & Conversion** | 4 files | JTBD, behavioral economics, persuasion science, conversion optimization, color psychology |
| **Motivation & Behavior** | 3 files | Self-determination theory, habit formation, stress & resilience, creativity |
| **Interpersonal & Social** | 5 files | Social influence, personality (Big Five, MBTI), emotional intelligence, communication, negotiation |
| **Design & Organization** | 2 files | UX psychology, team dynamics, leadership, organizational culture |
| **Ethics** | 1 file | Safety guidelines, dark patterns to avoid, vulnerable populations |

### 🛠️ 3 Python Assessment Tools

```bash
# Generate personalized learning plans by age and skill
python scripts/learner_assessment.py --age 25 --skill coding --context work

# Audit conversion funnels with psychology-based insights
python scripts/conversion_audit.py --funnel signup --segment new_users

# Detect manipulation patterns in marketing copy
python scripts/bias_detector.py --copy "Your marketing text here"
```

### ✅ Evidence-Based & Ethical

- Built on peer-reviewed research and established frameworks
- Strong ethical guardrails against dark patterns
- Safety guidelines for vulnerable populations
- Transparent about limitations and when to refer out

---

## 📖 Reference Modules

### Learning & Development
| File | Content |
|------|---------|
| `learning-development.md` | Age-specific learning (3-65+), memory systems, cognitive load theory |
| `skill-acquisition.md` | Languages, coding, math, music — optimized by age |
| `cognitive-systems.md` | Memory, attention, decision-making, executive function |
| `neuropsychology-basics.md` | Brain systems, neuroplasticity, neurotransmitters |
| `sleep-circadian.md` | Sleep stages, chronotypes, optimal learning timing |

### Marketing & Conversion
| File | Content |
|------|---------|
| `marketing-psychology.md` | JTBD, behavioral economics, ethical persuasion |
| `conversion-optimization.md` | Funnel psychology, pricing, CTAs, experimentation |
| `customer-psychology.md` | Decision journey, emotions, loyalty, segmentation |
| `color-psychology.md` | Color meanings, cultural variations, brand applications |

### Motivation & Behavior
| File | Content |
|------|---------|
| `motivation-frameworks.md` | SDT, goal theory, habit formation, behavior change |
| `stress-resilience.md` | Coping mechanisms, burnout prevention, recovery |
| `creativity-psychology.md` | Divergent thinking, ideation techniques, creative blocks |

### Interpersonal & Social
| File | Content |
|------|---------|
| `social-psychology.md` | Group dynamics, conformity, social influence, in-group/out-group |
| `personality-psychology.md` | Big Five, MBTI applications, persona design |
| `emotional-intelligence.md` | EQ framework, empathy design, emotional triggers |
| `communication-psychology.md` | Active listening, verbal/nonverbal, difficult conversations |
| `negotiation-psychology.md` | BATNA, principled negotiation, cross-cultural |

### Design & Organization
| File | Content |
|------|---------|
| `ux-psychology.md` | Gestalt principles, cognitive load in UX, interaction design |
| `organizational-psychology.md` | Team dynamics, leadership, culture, change management |

### Ethics
| File | Content |
|------|---------|
| `safety-ethics.md` | Hard boundaries, vulnerable populations, dark patterns to avoid |

---

## 💡 Use Cases

### 🎓 Education & Learning
- Design optimal curricula for different age groups
- Create effective study schedules based on memory science
- Build motivation systems that don't rely on extrinsic rewards

### 📈 Marketing & Growth
- Increase conversions through ethical behavioral design
- Write persuasive copy that respects user autonomy
- Audit funnels for dark patterns and manipulation

### 🎨 Product & UX
- Apply Gestalt principles to interface design
- Reduce cognitive load for better usability
- Design for emotional engagement and delight

### 👥 Teams & Leadership
- Build psychologically safe team environments
- Navigate organizational change effectively
- Develop leadership presence and influence

### 💼 Sales & Negotiation
- Understand customer decision psychology
- Apply principled negotiation techniques
- Build trust and long-term relationships

---

## 🛠️ Installation

### For Claude/AI Agents

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/psychology-master.git

# Copy to your skills directory
cp -r psychology-master ~/.agent/skills/

# Or for Claude Desktop
cp -r psychology-master ~/.claude/skills/
```

### Verify Installation

```bash
# Test the learner assessment script
python ~/.agent/skills/psychology-master/scripts/learner_assessment.py --age 12 --skill coding --context school
```

---

## 📋 Quick Start

### Basic Workflow

```
1. Identify domain → Learning OR Marketing OR Both
2. Gather context → Audience, goals, constraints  
3. Apply framework → Select from 20 references
4. Validate → Run ethics checklist before output
```

### Example: Learning Plan

```
User: "Design a learning plan for a 10-year-old to learn Python"

AI loads: learning-development.md, skill-acquisition.md

Output: Age-appropriate plan using visual programming (Scratch → Python),
        30-minute sessions, project-based with games, peer collaboration
```

### Example: Conversion Optimization

```
User: "Improve our signup funnel conversion"

AI loads: conversion-optimization.md, marketing-psychology.md

Output: Stage-by-stage analysis with psychological levers,
        friction points, and ethical recommendations
```

---

## 🔧 Scripts Reference

### learner_assessment.py

```bash
python scripts/learner_assessment.py \
  --age 25 \
  --skill coding \
  --context work \
  --time 30

# Options:
#   --age: Learner age (required)
#   --skill: coding, english, math, music, language
#   --context: school, work, hobby, career_change
#   --time: Available minutes per day
#   --json: Output as JSON
```

### conversion_audit.py

```bash
python scripts/conversion_audit.py \
  --funnel signup \
  --segment new_users \
  --stage decision

# Options:
#   --funnel: signup, checkout, lead_gen, saas_trial, ecommerce
#   --segment: new_users, returning, price_sensitive, enterprise, mobile
#   --stage: awareness, interest, consideration, decision, conversion, retention
#   --json: Output as JSON
```

### bias_detector.py

```bash
python scripts/bias_detector.py \
  --copy "Limited time offer! Act now!" \
  --strict

# Options:
#   --copy: Text to analyze
#   --file: File containing text
#   --strict: Stricter analysis
#   --json: Output as JSON
```

---

## 🤝 Contributing

Contributions are welcome! Areas for expansion:

- [ ] Additional cultural psychology contexts (non-Western perspectives)
- [ ] Industry-specific applications (healthcare, finance, etc.)
- [ ] More assessment scripts (personality profiler, team diagnostic)
- [ ] Translations to other languages
- [ ] Case studies and examples

### How to Contribute

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-addition`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-addition`)
5. Open a Pull Request

---

## 📄 License

MIT License — Use freely, ethically.

See [LICENSE](LICENSE) for full text.

---

## 🙏 Acknowledgments

This skill synthesizes knowledge from decades of psychological research including:

- Cognitive psychology (Baddeley, Kahneman, Tversky)
- Developmental psychology (Piaget, Vygotsky)
- Learning science (Roediger, Bjork, Dunlosky)
- Social psychology (Cialdini, Milgram, Asch)
- Motivation theory (Deci & Ryan, Dweck)
- Behavioral economics (Thaler, Ariely)
- UX psychology (Norman, Nielsen)

---

## ⚠️ Disclaimer

This skill provides educational information based on psychological research. It is not a substitute for professional psychological, medical, or therapeutic advice. Always consult qualified professionals for clinical matters.

---

**Built with evidence-based psychology for the AI age.** 🧠✨

