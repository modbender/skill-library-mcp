---
name: brave-web-search
description: Searches the web and returns ranked results or AI-generated summarized answers using the Brave Search API. Use for real-time web lookups and factual Q&A.
metadata:
  clawdbot:
    emoji: "🔍"
    requires:
      env: ["BRAVE_SEARCH_API_KEY", "BRAVE_ANSWERS_API_KEY"]
      bins: ["node"]
    primaryEnv: "BRAVE_SEARCH_API_KEY"
    category: "Search & Research"
---

# Brave Web Search

Searches the web and fetches AI-generated summarized answers using the Brave Search API. Exposes two commands: `brave-search` for ranked web results and `brave-answer` for concise AI summaries.

## Instructions

1. **Trigger**: Activate when the user wants to look something up on the web, check recent news, or get a factual answer to a question.
2. **Setup**: No installation step is required — this skill has zero external dependencies and runs on native Node.js.
3. **Command selection**:
   - Use `brave-search` for general web searches where ranked results with URLs and snippets are useful.
   - Use `brave-answer` for direct factual questions where a concise AI summary is more appropriate.
4. **Execution**: Invoke the script by passing the command name and parameters as **separate arguments**, never by interpolating user input into a shell command string. Use an argument array / `execFile`-style invocation so the shell never parses user-supplied values. Example (Node-style pseudo-code):

   ```javascript
   execFile('node', ['index.js', 'brave-search', '--query', userQuery, '--count', '10'])
   ```

   Do **not** construct the command as a single concatenated string such as `"node index.js brave-search --query " + userQuery`.

5. **Freshness**: For time-sensitive queries, pass `--freshness` followed by `pd` (past day), `pw` (past week), or `pm` (past month) as a separate argument to `brave-search`.
6. **Fallback**: If `brave-answer` returns `answer: null`, present the `fallback_results` to the user instead.
7. **Completion**: Present the results clearly, citing titles and URLs for web search results, or the summary text for answer results.

## Security & Privacy

- **Shell Injection Prevention**: User queries **must** be passed as discrete arguments (e.g. via `execFile` or an argv array), never interpolated into a shell command string. Concatenating user input into a shell string (e.g. `shell: true` with template literals) enables shell injection and is strictly forbidden.
- **Instruction Scope**: This skill only sends query strings to the Brave Search and Brave Summarizer APIs.
- **Environment**: It uses the `BRAVE_SEARCH_API_KEY` and `BRAVE_ANSWERS_API_KEY` provided by the OpenClaw environment.
- **Data Access**: It does not read local files or .env files. All configuration is handled by the agent.