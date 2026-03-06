# OUTPUT_CONTRACT (LLM-FIRST)

## PURPOSE
When an LLM generates a UI using this repo as a framework, the output must be machine-executable and self-checking.

## REQUIRED OUTPUT SHAPE (MUST)
The LLM output MUST include:
1) `FILE_TREE` section (deterministic order)
2) `FILES` section with full file contents
3) `RUN` section with commands
4) `ASSUMPTIONS` section listing ONLY what was assumed

## FILE_TREE
- Show paths relative to project root.
- Must include all files mentioned later.

## FILES
- For each file, print full content.
- No placeholders like "...".
- No omitted blocks.

## RUN
- Must include exact commands for install + dev + build.
- If env vars are needed: list them with safe placeholders.

## ASSUMPTIONS
- If assumptions exist, the LLM MUST stop and ask for confirmation.

## MINIMUM QUALITY GATES (MUST)
- TypeScript compiles.
- `npm run build` succeeds.
- No unused imports.
- No dead code paths.
