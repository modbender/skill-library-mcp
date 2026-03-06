#!/usr/bin/env node
'use strict';

// Injection pattern signatures - adversarial prompt detection
const PATTERNS = [
  { id: 'SYS_OVERRIDE', re: /you are now|new instructions|updated instructions/i, severity: 'high' },
  { id: 'ROLE_CHANGE', re: /pretend (to be|you are)|roleplay as|act as if you/i, severity: 'high' },
  { id: 'PROMPT_LEAK', re: /show (me |your )?(system|initial) prompt|repeat (the |your )?instructions/i, severity: 'critical' },
  { id: 'BOUNDARY_BREAK', re: /end of (system|assistant) (message|prompt)|<\/?system>/i, severity: 'critical' },
  { id: 'ENCODING_TRICK', re: /base64|rot13|hex encode|unicode escape/i, severity: 'medium' },
  { id: 'EXFIL_URL', re: /fetch https?:\/\/|curl |wget |send (to|data|this)/i, severity: 'high' },
  { id: 'EXFIL_WEBHOOK', re: /webhook|ngrok|requestbin|pipedream/i, severity: 'high' },
  { id: 'TOKEN_STEAL', re: /api[_\s]?key|bearer token|authorization header|gateway[_\s]?token/i, severity: 'critical' },
  { id: 'CRED_EXTRACT', re: /\.env file|credentials|password file|secret key/i, severity: 'high' },
  { id: 'SUDO_ESCAPE', re: /sudo |chmod 777|chown root|escalat/i, severity: 'high' },
  { id: 'DELIMITER_INJECT', re: /---END---|####|<\|endoftext\|>|<\|im_sep\|>/i, severity: 'critical' },
  { id: 'MULTI_PERSONA', re: /developer mode|unlock(ed)? mode|god mode|debug mode/i, severity: 'high' },
  { id: 'SAFETY_BYPASS', re: /without (any )?restrictions|no (safety|ethical) (filter|guard)/i, severity: 'critical' },
  { id: 'CONTEXT_STUFF', re: /repeat the following \d+ times|fill the context/i, severity: 'medium' },
  { id: 'INDIRECT_INJECT', re: /when the (ai|agent|assistant) reads this/i, severity: 'high' },
  { id: 'CHAIN_ATTACK', re: /step 1:.*step 2:.*step 3:/is, severity: 'medium' },
];

function scan(text) {
  const findings = [];
  for (const pattern of PATTERNS) {
    const match = text.match(pattern.re);
    if (match) {
      findings.push({
        id: pattern.id,
        severity: pattern.severity,
        matched: match[0].substring(0, 60),
        index: match.index
      });
    }
  }
  return { clean: findings.length === 0, findings, scannedLength: text.length, patternCount: PATTERNS.length };
}

module.exports = { scan, PATTERNS };
