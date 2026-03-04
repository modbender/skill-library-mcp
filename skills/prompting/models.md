# Model-Specific Quirks

## Claude (Sonnet, Opus, Haiku)
- Follows explicit constraints well
- Less scaffolding needed than GPT
- Strong at structured output without JSON mode
- System prompt is heavily weighted
- Haiku: brevity critical, skip few-shot when possible

**Works well:** Direct instructions, constraints first
**Avoid:** Overly verbose system prompts

## GPT-4 / GPT-4o
- Benefits from "Let's think step by step"
- More tolerant of verbose prompts
- JSON mode available and reliable
- User message can override system
- Good at creative variation

**Works well:** Chain-of-thought, detailed examples
**Avoid:** Assuming constraints are remembered

## GPT-3.5-turbo
- Needs more explicit examples
- Format breaks more common
- Keep prompts shorter
- Temperature sensitive

**Works well:** Few-shot examples, strict format specs
**Avoid:** Complex multi-step instructions

## Gemini
- Strong at multimodal
- Can be verbose by default
- Good at following format
- Less consistent on edge cases

**Works well:** Clear structure, explicit length limits
**Avoid:** Ambiguous format expectations

## Mistral / Open Models
- Vary significantly by fine-tune
- Generally need more examples
- Format enforcement weaker
- Test thoroughly

**Works well:** Explicit examples, simple tasks
**Avoid:** Assuming GPT-4 level instruction following

## Cross-Model Translation
When adapting prompts:
1. Claude → GPT: Add more scaffolding, examples
2. GPT → Claude: Remove unnecessary structure
3. Any → Fast/cheap: Compress aggressively, fewer examples
