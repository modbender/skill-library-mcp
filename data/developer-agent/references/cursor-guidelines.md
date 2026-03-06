# Cursor Interaction Guidelines

## When Sending to Cursor

**Always include:**
- Clear, concise requirement statement
- Minimal essential context (2-3 sentences max)
- All user-provided links
- All user-provided attachments
- Selected model (Opus/Sonnet/Composer)

**Never include:**
- Excessive explanations
- Predefined structure
- Step-by-step instructions
- Over-detailed specifications
- Unnecessary background information

**Let Cursor decide:**
- How to structure the plan
- Level of detail needed
- Best implementation approach
- Testing strategies
- Code organization

## Good Cursor Prompt Example

```
Create an implementation plan for adding user authentication.

Context: We use JWT tokens and have existing user model in database.

Resources:
• Authentication flow diagram: [link]
• API documentation: [attachment]

Analyze the codebase and create your comprehensive plan.
```

## Bad Cursor Prompt Example (Avoid)

```
Create a plan with these sections:
1. Overview (write 2 paragraphs)
2. Files to Change (list with bullet points)
3. Step by step instructions (number each step)
4. Testing section (write test cases)

First you need to look at auth.js, then user.model.js, then...
Make sure to include error handling in step 3...
The plan should be exactly 5 pages long...
```

This over-prompts and removes Cursor's creativity.
