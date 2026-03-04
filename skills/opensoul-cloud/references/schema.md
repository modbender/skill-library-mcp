# OpenSoul Schema Reference

## SoulProfile

The core data structure for sharing.

```typescript
interface SoulProfile {
  // Display info
  title: string;           // Agent name (anonymized)
  tagline: string;         // One-line description
  avatar?: string;         // Optional avatar URL
  
  // Persona characteristics
  persona: {
    tone: string[];        // e.g., ["friendly", "professional"]
    style: string[];       // e.g., ["concise", "resourceful"]
    boundaries: string[];  // e.g., ["confirms before external actions"]
  };
  
  // What the agent can do
  capabilities: string[];  // e.g., ["browser integration", "calendar"]
  useCases: string[];      // e.g., ["research", "scheduling"]
  
  // Technical setup
  skills: string[];        // Installed skill names
  workflowHighlights: string[];  // Key workflow sections
}
```

## Anonymization Rules

### Always Strip
- Real names → `[USER]`, `[PERSON]`
- Email addresses → `[EMAIL]`
- API keys/tokens → `[API_KEY]`, `[TOKEN]`
- File paths with usernames → `/Users/[USER]/`
- Phone numbers → `[PHONE]`
- Birth dates → `[BIRTH_DATE]`

### Preserve (anonymized form)
- Persona descriptions
- Workflow patterns
- Tool names (not credentials)
- Use case descriptions
- Skill names and descriptions

### Never Include
- USER.md contents
- MEMORY.md contents
- .env files
- Credential files
- Private notes

## Categories

Standard use case categories for discovery:

- **Personal Assistant** - General help, reminders, scheduling
- **Coding** - Code review, generation, debugging
- **Research** - Web search, document analysis
- **Communication** - Email, messaging, social
- **Home Automation** - IoT, smart home control
- **Finance** - Budgeting, tracking, analysis
- **Health** - Fitness, wellness, medical notes
- **Creative** - Writing, art, music
- **Learning** - Education, language, skills
- **Work** - Project management, CRM, ops

## Persona Tags

Standard persona descriptors:

**Tone:**
- friendly, professional, casual, formal
- witty, serious, warm, empathetic
- technical, creative, analytical

**Style:**
- concise, thorough, detailed, brief
- proactive, reactive, resourceful
- opinionated, neutral, cautious
