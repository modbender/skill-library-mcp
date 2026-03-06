import { getFailoverStatus } from './status.ts';
const order = ["anthropic/claude-opus-4-6", "github-copilot/gpt-5-mini", "google-gemini-cli/gemini-2.5-flash", "google-gemini-cli/gemini-2.5-pro", "github-copilot/gpt-5.2", "github-copilot/gpt-5.1"];
const status = getFailoverStatus({modelOrder: order});
console.log(JSON.stringify(status,null,2));
