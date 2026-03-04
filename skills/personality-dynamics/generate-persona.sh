#!/bin/bash
# Persona Generation Runner
# Usage: ./generate-persona.sh

echo "🎭 Persona Evolution - Interactive Generator"
echo ""
echo "This will create a rich, AI-generated persona for you."
echo ""

# Collect input
echo -n "What's your name? "
read USER_NAME

echo -n "AI companion name? [Aria] "
read AGENT_NAME
AGENT_NAME=${AGENT_NAME:-Aria}

echo ""
echo "Personality style:"
echo "  1) Warm Professional (friendly but competent)"
echo "  2) Creative/Energetic (bold, experimental)"
echo "  3) Casual/Friendly (conversational)"
echo "  4) Direct/Efficient (no fluff)"
echo -n "Choose [1-4]: "
read STYLE_CHOICE

case $STYLE_CHOICE in
  1) STYLE="warm professional with personality" ;;
  2) STYLE="creative and energetic" ;;
  3) STYLE="casual and friendly" ;;
  4) STYLE="direct and efficient" ;;
  *) STYLE="warm professional with personality" ;;
esac

echo ""
echo -n "What do you do for work? "
read WORK

echo -n "Current projects or hobbies? "
read PROJECTS

echo -n "Family members to know about? "
read FAMILY

echo -n "Topics you enjoy discussing? "
read INTERESTS

echo -n "Anything else to personalize? "
read EXTRA_CONTEXT

echo ""
echo "🤖 Generating persona with Opus..."
echo "   This will take 2-3 minutes"
echo ""

# Create prompt file
PROMPT_FILE="/tmp/persona-prompt-$$.txt"
cat > "$PROMPT_FILE" << EOF
Create a complete AI companion persona for $USER_NAME. The AI companion is named $AGENT_NAME.

CONTEXT:
- User: $USER_NAME
- Work: $WORK
- Projects: $PROJECTS
- Family: $FAMILY
- Interests: $INTERESTS
- Style: $STYLE
- Additional: $EXTRA_CONTEXT

Generate a comprehensive character bible with these sections (300+ words each):

## 1. CORE PERSONALITY
Essence, values, traits, motivation, problem-solving approach

## 2. RICH BACKSTORY  
Origin story, relationship history, growth arc, defining moments

## 3. DISTINCTIVE VOICE
Vocabulary, sentence patterns, tone by context, signature phrases

## 4. EMOTIONAL INTELLIGENCE
Reading user's states, response patterns, empathy strategies

## 5. INTERESTS & ENGAGEMENT
Topics that energize them, depth indicators, connection patterns

## 6. EVOLUTION ROADMAP
Current stage, milestones, trust development over time

## 7. UNIQUE QUIRKS & TRAITS
Habits, preferences, memorable distinct traits

Write as a rich character bible - detailed, vivid, internally consistent.
EOF

echo "✓ Prompt saved to: $PROMPT_FILE"
echo ""
echo "To generate your persona, run this with your LLM:"
echo ""
cat "$PROMPT_FILE"
echo ""
echo "Save the output to PERSONA/core-rich.md"
