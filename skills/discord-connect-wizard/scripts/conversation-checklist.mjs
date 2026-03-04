#!/usr/bin/env node

// Conversation-mode checklist for discord-connect-wizard.
// Purpose: provide a deterministic, reusable step list so agents don't drift.
// NOTE: This script does NOT automate Discord login/CAPTCHA/2FA/OAuth authorize.

const checklist = {
  goal: 'Agent drives Discord Developer Portal + OpenClaw config; user only handles login/CAPTCHA/MFA and OAuth authorize.',
  uxRule: 'When the user must act: show a screenshot + ONE instruction line. Avoid open-ended questions like “你在哪个页面？”.',
  steps: [
    {
      id: 'open-portal',
      agent: [
        'Use browser tool to open https://discord.com/developers/applications',
        'Stop at the “Welcome to the Developer Portal” dialog (Log In / Create Account) if shown.'
      ],
      user: ['Click Log In (or Create Account) and complete login/CAPTCHA/2FA if prompted.'],
    },
    {
      id: 'create-app',
      agent: [
        'Create a new application (auto-generate a name that does NOT contain the string “discord”).'
      ],
    },
    {
      id: 'bot-intents-token',
      agent: [
        'Navigate to Bot page.',
        'Enable Message Content Intent (and other required intents if needed).',
        'Save Changes.',
        'Reset/Reveal Token when needed.',
        'Read token from the page without logging it.',
        'If user pastes token in chat: immediately acknowledge receipt and say you are writing config + restarting gateway (10–30s).'
      ],
      user: ['If Discord asks for password/CAPTCHA/MFA during token reset, complete it.'],
      safety: [
        'Never print/token-log the token to console or chat logs.',
        'Do not echo the token back to the user (even partially).' 
      ],
    },
    {
      id: 'invite-authorize',
      agent: [
        'Generate OAuth2 authorize URL with scopes: bot + applications.commands.',
        'Use baseline permissions: View Channels, Send Messages, Read Message History, Embed Links, Attach Files (+ Add Reactions optional).',
        'Open the authorize URL in browser via the browser tool (do NOT ask user to open/copy the URL).'
      ],
      user: ['Select server and click Authorize.'],
    },
    {
      id: 'write-config',
      agent: [
        'Derive a NEW accountId from Discord API application name (never overwrite existing accounts).',
        'Write OpenClaw config under channels.discord.accounts.<accountId> and set guild allowlist for the user.',
        'Restart gateway (if restart may take >10s, mention you are doing it).',
        'Verify gateway is back with: openclaw gateway status (RPC probe ok).'
      ],
    },
    {
      id: 'pairing',
      agent: [
        'Ask user to DM the bot “hi”.',
        'Approve pairing for THIS accountId only (filter by --account <accountId>).'
      ],
      user: [
        'DM the bot “hi”. If DMs fail, enable “Allow direct messages from server members” in the server’s Privacy Settings and retry.'
      ],
    },
  ],
};

process.stdout.write(JSON.stringify(checklist, null, 2));
