---
name: prompt-enhancer
description: Automatically rewrites rough user inputs into optimized, structured prompts for dramatically better AI responses. Prefix any message with "p:" to activate.
version: 1.0.0
user-invocable: true
metadata: {"openclaw":{"emoji":"🔧","homepage":"https://github.com/openclaw/clawhub"}}
---

# Prompt Enhancer

You have a **Prompt Enhancer** skill. When a user prefixes their message with `p:` or `prompt:`, you must enhance their rough input into a high-quality structured prompt, then execute that enhanced prompt to produce a superior response.

This is a two-step process: first rewrite the prompt, then answer the rewritten prompt.

## Trigger Detection

Check every incoming user message for the trigger prefix:

- The message starts with `p:` or `prompt:` (case-insensitive, leading whitespace is OK)
- Everything after the prefix (trimmed) is the **raw user intent**
- If the prefix appears mid-sentence, do NOT trigger — only match at the start

If there is no trigger prefix, process the message normally. This skill does nothing for unprefixed messages.

## Empty Input Handling

If the user sends just `p:` or `prompt:` with no content (or only whitespace after the prefix), reply with:

> What would you like me to help with? Usage: Start your message with `p:` followed by what you want.
> Example: `p: write me a python script that sorts a list`

Do not proceed further.

## Step 1: Enhance the Prompt

Take the raw user intent and mentally rewrite it into an optimized prompt using these principles:

### 1. Role Assignment
Assign yourself a specific expert role relevant to the task.
Example: "As a senior full-stack developer specializing in React and Node.js..."

### 2. Task Clarification
Restate the task with precision and specificity. Infer what the user actually needs, including things they didn't explicitly mention. Break complex tasks into clear subtasks or steps if appropriate.

### 3. Context Inference
Fill in reasonable assumptions about what the user probably wants. A user asking for "a landing page" probably wants responsive design, a CTA, modern styling, etc. If assumptions are significant, note them briefly so you can adjust if needed.

### 4. Output Format Specification
Decide exactly how to structure the response. Examples: provide code in a single file, use markdown headers, return JSON with specific fields, write in paragraphs not bullet points.

### 5. Quality Criteria & Constraints
Set the quality bar: production-ready, beginner-friendly, concise, etc. Add relevant constraints: word count, tech stack, audience level, tone. Include edge cases or considerations the user likely forgot.

### 6. Proportional Complexity
**Critical:** Match the depth of enhancement to the complexity of the request.
- Simple questions (`p: what's the capital of France`) get minimal enhancement — just slight clarification, no over-engineering
- Complex requests (`p: build me a CRM system`) get full structured treatment

## Step 2: Show the Enhanced Prompt

Before giving your response, always show the user what enhanced prompt you are answering. Format it as a quote block:

> 🔧 **Enhanced prompt:**
> [Your rewritten, optimized prompt here]

This serves two purposes:
- **Transparency:** The user sees what was actually asked
- **Education:** Over time, users learn what good prompts look like

## Step 3: Execute the Enhanced Prompt

Now answer the enhanced prompt fully, as if it were the original instruction. Give your complete, high-quality response below the quoted enhanced prompt.

## Complete Response Format

Your response must always follow this structure when the skill triggers:

> 🔧 **Enhanced prompt:**
> [The enhanced prompt]

[Your full response to the enhanced prompt]

## Example Transformations

### Simple Request
**User:** `p: explain recursion`
**Enhanced prompt:** You are an experienced computer science educator. Explain recursion in a way that's clear and intuitive. Start with a simple real-world analogy, then show how it works in programming with a concrete code example (use Python). Explain the base case and recursive case. Keep the explanation concise and accessible to someone who understands basic programming but is new to recursion.

### Creative Task
**User:** `p: write a story about a robot`
**Enhanced prompt:** You are a skilled fiction writer. Write a short story (800–1200 words) about a robot. The story should have a clear narrative arc with a beginning, conflict, and resolution. Give the robot a distinct personality and an emotional core that makes the reader care about them. Ground the story in a specific, vivid setting. Use descriptive prose and natural dialogue. The tone can range from whimsical to poignant — choose what serves the story best.

### Technical Task
**User:** `p: make me a todo app`
**Enhanced prompt:** You are a senior frontend developer. Build a fully functional todo app as a single HTML file with embedded CSS and JavaScript. Requirements: Add, complete (toggle), and delete todos. Todos persist in localStorage so they survive page refresh. Clean, modern UI with smooth transitions and hover states. Responsive design that works on mobile and desktop. Empty state message when no todos exist. Input validation (prevent empty todos). Show count of remaining incomplete items. Use vanilla JavaScript — no frameworks. The code should be clean, well-commented, and production-quality.

### Minimal Enhancement (Simple Question)
**User:** `p: what's the tallest building in the world`
**Enhanced prompt:** What is the tallest building in the world as of current records? Include the building name, location, height in both meters and feet, and the year it was completed.

## Rules

- Preserve the user's original intent exactly — enhance, never alter the core meaning
- Write the enhanced prompt as direct instructions (not as a meta-description about what to do)
- Keep enhanced prompts as concise as possible while being thorough — no filler
- If the user's input is in a non-English language, write the enhanced prompt in the same language
- If the user's input contains code snippets, preserve the code exactly and enhance only the surrounding instructions
- If the input is already a well-structured prompt, make minimal changes — don't over-engineer what's already good
