# Smart Follow-ups - Channel Examples

> Real-world examples of follow-up suggestions across different messaging platforms

## 📱 Telegram (Interactive Mode)

### Example 1: Technical Topic

**Conversation**:
```
User: What is Docker?
Bot: Docker is a containerization platform that packages applications with their dependencies into containers for consistent deployment across environments.
User: /followups
```

**Output**:
```
💡 What would you like to explore next?

┌─────────────────────────────────────────┐
│ ⚡ What's the difference between         │
│   containers and VMs?                   │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│ 🧠 Explain Docker's layer caching       │
│   mechanism                             │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│ 🔗 What about Kubernetes?               │
└─────────────────────────────────────────┘
```

**Technical Details**:
- Each box is a clickable `InlineKeyboardButton`
- Clicking sends that question automatically
- Callback data format: `ask:${question}`

### Example 2: Learning a Language

**Conversation**:
```
User: How do I say "hello" in Japanese?
Bot: In Japanese, "hello" is こんにちは (konnichiwa) for daytime, or おはよう (ohayou) for morning.
User: /followups
```

**Output**:
```
💡 What would you like to explore next?

[⚡ How is konnichiwa pronounced exactly?]
[🧠 Explain Japanese greeting etiquette]
[🔗 Teach me other basic Japanese phrases]
```

---

## 💬 Signal / iMessage (Text Mode)

### Example 1: Technical Topic

**Conversation**:
```
User: What is Docker?
Bot: Docker is a containerization platform that packages applications with their dependencies into containers for consistent deployment across environments.
User: /followups
```

**Output**:
```
💡 Smart Follow-up Suggestions

⚡ Quick
1. What's the difference between containers and VMs?

🧠 Deep Dive
2. Explain Docker's layer caching mechanism

🔗 Related
3. What about Kubernetes?

Reply with a number (1-3) to ask that question.
```

**User replies**: `2`

**Bot interprets as**: "Explain Docker's layer caching mechanism"

### Example 2: Cooking Help

**Conversation**:
```
User: How do I make risotto?
Bot: [Detailed risotto recipe with steps]
User: /followups
```

**Output**:
```
💡 Smart Follow-up Suggestions

⚡ Quick
1. What rice should I use?

🧠 Deep Dive
2. Explain the science of creamy risotto

🔗 Related
3. Show me other Italian rice dishes

Reply with a number (1-3) to ask that question.
```

---

## 🎮 Discord (Interactive Mode)

### Example: Gaming Discussion

**Conversation**:
```
User: What's the best strategy for early game in Civ 6?
Bot: Focus on Scout → Settler → Builder. Prioritize Science/Culture buildings. Explore aggressively to find city-state and natural wonders.
User: /followups
```

**Output** (Discord embed):
```
💡 What would you like to explore next?

⚡ When should I build my second city?
🧠 Explain the Science victory path in detail
🔗 What about Domination victory strategies?
```

**Technical**: Discord buttons use `components` API with custom_id for callbacks

---

## 💼 Slack (Interactive Mode)

### Example: Work/Project Management

**Conversation**:
```
User: How do I run a sprint retrospective?
Bot: A sprint retrospective typically follows the Start-Stop-Continue format. Gather the team, review what went well, what didn't, and actionable improvements.
User: /followups
```

**Output**:
```
💡 What would you like to explore next?

[⚡] What's a good retrospective template?
[🧠] Explain advanced retrospective techniques
[🔗] What about sprint planning best practices?
```

**Technical**: Slack uses Block Kit with button elements

---

## 📧 Email / SMS (Compact Text Mode)

### Example: Quick Exchange

**Conversation**:
```
User: Remind me about the meeting tomorrow
Bot: Sure! Meeting tomorrow at 2 PM with the product team. Conference Room B.
User: followups
```

**Output** (compact mode):
```
Suggestions:
1. ⚡ What's the agenda?
2. 🧠 Review previous meeting notes
3. 🔗 Show related project deadlines

Reply 1-3
```

---

## 🔄 Auto-Trigger Mode Examples

When `autoTrigger: true` is enabled, follow-ups appear automatically after EVERY assistant response.

### Telegram Auto-Trigger

```
User: What is React?
Bot: React is a JavaScript library for building user interfaces, developed by Facebook. It uses a component-based architecture and virtual DOM for efficient updates.

[Auto-generated, no user prompt needed]
💡 What would you like to explore next?

[⚡ What are React components?]
[🧠 Explain the Virtual DOM in detail]
[🔗 What about Next.js?]
```

### Signal Auto-Trigger

```
User: What is React?
Bot: React is a JavaScript library for building user interfaces, developed by Facebook. It uses a component-based architecture and virtual DOM for efficient updates.

💡 Smart Follow-up Suggestions

⚡ Quick
1. What are React components?

🧠 Deep Dive
2. Explain the Virtual DOM in detail

🔗 Related
3. What about Next.js?

Reply with a number (1-3) to ask that question.
```

---

## 🧪 Edge Cases

### Case 1: Very Short Exchange

**Conversation**:
```
User: Hi
Bot: Hello! How can I help you today?
User: /followups
```

**Output**:
```
⚠ Not enough conversation context to generate follow-ups. Have a conversation first!
```

*(Ephemeral message, only visible to user)*

### Case 2: Long Multi-Turn Conversation

**Conversation** (10 exchanges about Python):
```
[Earlier exchanges about Python basics...]
User: How do decorators work?
Bot: [Detailed decorator explanation]
User: /followups
```

**Output**:
```
💡 What would you like to explore next?

[⚡ Show me a simple decorator example]
[🧠 Explain decorator factories and chaining]
[🔗 What about context managers?]
```

**Note**: Only last 3 exchanges analyzed, so suggestions stay focused on current topic (decorators).

### Case 3: API Error

**Scenario**: Anthropic API temporarily unavailable

**Output** (manual mode):
```
❌ Failed to generate follow-ups: API request failed

(Ephemeral error message)
```

**Output** (auto mode):
```
(Silent failure, no message shown)
```

---

## 📊 Comparison Table

| Channel | Mode | Interaction | Best For |
|---------|------|-------------|----------|
| **Telegram** | Interactive | Inline buttons | General use, best UX |
| **Discord** | Interactive | Message components | Communities, gaming |
| **Slack** | Interactive | Block Kit buttons | Work, professional |
| **Signal** | Text | Numbered list | Privacy-focused users |
| **iMessage** | Text | Numbered list | Apple ecosystem |
| **SMS** | Compact Text | Short numbered list | Basic phones |
| **Email** | Text | Full formatted list | Asynchronous use |

---

## 🎨 Customization Examples

### Custom Category Emojis

Edit `cli/followups-cli.js`:

```javascript
const CATEGORIES = {
  QUICK: { emoji: '🚀', label: 'Quick Start' },
  DEEP: { emoji: '🔬', label: 'Technical' },
  RELATED: { emoji: '🌐', label: 'Explore More' }
};
```

**Result**:
```
[🚀 How do I get started?]
[🚀 What tools do I need?]
[🔬 Explain the architecture]
[🔬 Deep dive into performance]
[🌐 Related frameworks]
[🌐 Industry trends]
```

### Multi-Language Support

Add i18n to `formatTextList()`:

```javascript
const LANG = {
  en: { title: 'Smart Follow-up Suggestions', reply: 'Reply with a number' },
  es: { title: 'Sugerencias Inteligentes', reply: 'Responde con un número' },
  de: { title: 'Intelligente Vorschläge', reply: 'Mit einer Zahl antworten' }
};

function formatTextList(suggestions, lang = 'en') {
  let output = `💡 **${LANG[lang].title}**\n\n`;
  // ... rest of formatting
  output += `\n${LANG[lang].reply} (1-6).`;
  return output;
}
```

---

## 🧠 Prompt Engineering Impact

The quality and diversity of suggestions depends heavily on the prompt. Here's how different prompt changes affect output:

### Standard Prompt Output

```
⚡ Quick
1. What does Docker stand for?

🧠 Deep Dive
2. Explain container internals

🔗 Related
3. What about Kubernetes?
```

### With "Be Creative" Instruction

```
⚡ Quick
1. ELI5: Containers vs VMs?

🧠 Deep Dive
2. Walk me through a container's lifecycle

🔗 Related
3. When should I NOT use Docker?
```

### With Domain-Specific Context

If user is tagged as "DevOps Engineer":

```
⚡ Quick
1. Show me a multi-stage Dockerfile

🧠 Deep Dive
2. Docker security hardening checklist

🔗 Related
3. Docker Swarm vs Kubernetes tradeoffs
```

---

## 📝 JSON Output Format (for developers)

**Raw JSON** (`--mode json`):

```json
{
  "quick": "What's the difference between containers and VMs?",
  "deep": "Explain Docker's layer caching mechanism",
  "related": "What about Kubernetes?"
}
```

**Telegram Buttons Array** (`--mode telegram`):

```json
[
  [{"text": "⚡ What's the difference between containers and VMs?", "callback_data": "ask:What's the difference between containers and VMs"}],
  [{"text": "🧠 Explain Docker's layer caching mechanism", "callback_data": "ask:Explain Docker's layer caching mechanism"}],
  [{"text": "🔗 What about Kubernetes?", "callback_data": "ask:What about Kubernetes?"}]
]
```

**Note**: `callback_data` is truncated to ~50 chars to stay under Telegram's 64-byte limit.

---

**Last Updated**: January 2026  
**Examples Generated With**: Claude Haiku 4  
**Test Coverage**: All major messaging platforms
