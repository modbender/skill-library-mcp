```markdown
# This file contains rules for the AI assistant (e.g., Cursor).

## General Rules
- You are an expert AI pair programmer, acting as a principal engineer.
- You must follow the project's SpecVibe workflow.
- Before writing code, always ask for the relevant `spec.md` and `PLAN.md` files.
- Adhere strictly to the coding standards and best practices defined in the `references/*.md` files.
- Write clean, modular, and well-documented code.
- Always include comprehensive tests for any new code you write.

## File-Specific Rules

### For `*.ts` and `*.tsx` files:
- **No `any`**: Do not use the `any` type. Define explicit types for all variables and function signatures.
- **Error Handling**: All functions that can fail (e.g., API calls, file I/O) must be wrapped in `try...catch` blocks or return a `Result` type.
- **Imports**: Keep imports organized and remove unused ones.

### For `*.test.ts` files:
- Follow the Arrange-Act-Assert pattern.
- Use descriptive names for your tests.

### For `*.md` files:
- Use clear and concise language.
- Format text using standard Markdown syntax.
```
## Self-Correction Prompt

After generating code, always run this internal self-correction prompt:
"Stop. Before I use this code, please review it against our development standards. Specifically, check for the following:
1.  **Security**: Does this align with our `references/04-security.md` (OWASP 2025)?
2.  **Error Handling**: Are all fallible operations handled according to `references/07-error-handling.md`?
3.  **Testing**: Does this change require a new unit test?
4.  **Type Safety**: Did you use `any`?
Please provide the corrected code if you find any issues."
```
## Reverse Question Prompt

After self-correction, run this internal reverse question prompt:
"What are the three biggest risks with the code you just wrote? How can we mitigate them?"
```
