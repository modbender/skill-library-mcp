# Troubleshooting

When a workflow doesn't work as expected, use this guide to diagnose and fix the
issue. Start by checking the workflow run output with `getWorkflowRunById()` —
it usually tells you what went wrong.

---

## Data is empty or wrong

**Symptoms**: Workflow runs successfully but the data step returns null, empty
arrays, or unexpected values.

**Diagnose**:
1. Check `getWorkflowRunById({ workflowRunId, includeWorkflowData: true })` to see
   exactly what each node returned
2. Look at the data fetch node's output specifically

**Common causes and fixes**:

- **Wrong API endpoint or subgraph URL**: Verify the URL is correct. Subgraph URLs
  are chain-specific — the Uniswap V3 Ethereum subgraph is different from Arbitrum.
  Search the web for the correct URL.

- **Wrong pool/token address**: Addresses are chain-specific. The WETH/USDC pool on
  Ethereum has a different address than on Arbitrum. Verify with the protocol's UI
  or a block explorer.

- **Subgraph query returns wrong fields**: TheGraph subgraph schemas vary. Check
  what entities and fields are available by looking at the subgraph's schema. The
  orchestrator may have guessed wrong field names.

- **API requires authentication**: Some endpoints need an API key in headers. Check
  the API docs and add credentials if needed.

- **Rate limiting**: If the API returns 429 errors, you're hitting rate limits.
  Reduce frequency or add an API key for higher limits.

**Fix approach**: Create a minimal test workflow that only does the data fetch. Run
it, inspect the raw output. Fix the query/URL, test again. Once data looks right,
update the full workflow with `editGeneratedWorkflow()`.

---

## AI analysis is not useful

**Symptoms**: The AI node runs but the output is generic, doesn't reference the
actual data, or misses the point.

**Common causes and fixes**:

- **Prompt is too vague**: Instead of "analyze this data", write "analyze the pool's
  TVL change over 24 hours, flag any changes over 5%, compare volume to 7-day
  average, and note any unusual fee activity."

- **Data isn't structured**: If the AI receives a wall of text instead of JSON, it
  struggles. Make sure the data fetch returns structured data that the AI can parse.

- **Wrong model**: `gemini-2.5-flash` is good for most tasks but may struggle with
  complex multi-step analysis. Try a different model if the analysis quality is poor.

- **No output format specified**: Tell the AI exactly how to structure its response
  — sections, headings, what to include in each section.

**Fix approach**: Edit the AI node's prompt via `editGeneratedWorkflow()`. Be
specific about what to analyze, what to highlight, and how to format the output.
Include examples of the desired output if possible.

---

## Notification didn't arrive

**Symptoms**: Workflow ran, data looks good, AI analysis looks good, but the email
or Telegram message never arrived.

**Common causes and fixes**:

- **Email MCP not connected**: Check `listTeamMcpServerIntegrations()` to verify the
  Email (Composio) integration is active.

- **Wrong email address**: Verify the recipient email is correct in the workflow
  config. Typos happen.

- **Check spam folder**: AI-generated emails sometimes land in spam.

- **Telegram bot not configured**: If using WriteAPI to a Telegram bot, verify the
  bot token and chat ID are correct. The chat ID must be for the specific
  conversation where the bot should post.

- **WriteAPI endpoint is wrong**: If using a webhook, verify the URL is correct and
  the service is accepting requests.

---

## Scheduled workflow isn't running

**Symptoms**: You deployed a scheduled workflow but it never executes.

**Diagnose**:
1. `getWorkflowById()` — check if the workflow is paused
2. `getWorkflowRuns()` — check if there are any runs at all, or runs with errors

**Common causes and fixes**:

- **Workflow is paused**: Use `updateWorkflow()` to unpause it.

- **Trigger misconfigured**: The schedule interval might be wrong. Check the trigger
  node's config in the workflow details.

- **Workflow errored on first run and stopped**: Some errors can halt the schedule.
  Fix the error and re-enable.

---

## Orchestrator isn't building what I described

**Symptoms**: The `generateWorkflow` or `editGeneratedWorkflow` output doesn't match
what you asked for.

**Fixes**:

- **Be more specific**: Instead of "fetch pool data", say "use TheGraph Subgraph MCP
  (integration ID: ca0072f7-...) to query Uniswap V3 subgraph on Ethereum for pool
  0x8ad599... and get totalValueLockedUSD, volumeUSD, and feesUSD from poolDayDatas"

- **Break it into steps**: If your prompt asks for too much at once, the orchestrator
  may miss details. Start simple, then add complexity via `editGeneratedWorkflow`.

- **Provide the MCP integration ID**: Don't assume the orchestrator knows which
  integration to use. Give it the specific ID from
  `listTeamMcpServerIntegrations()`.

- **Iterate**: Remember the orchestrator is conversational. If the first attempt
  isn't right, explain what's wrong and what you want changed. 2-4 rounds is normal.
