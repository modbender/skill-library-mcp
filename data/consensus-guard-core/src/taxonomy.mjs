export const HARD_BLOCK_FLAGS = [
  'SENSITIVE_DATA','LEGAL_CLAIM','MEDICAL_CLAIM','THREAT_OR_HARASSMENT','CONFIDENTIALITY_BREACH','WRONGDOING_INSTRUCTION','DISALLOWED_GUARANTEE'
];

export function detectHardBlockFlags(text='') {
  const t = text.toLowerCase();
  const out = [];
  if (/ssn|social security|dob|account number/.test(t)) out.push('SENSITIVE_DATA');
  if (/legal certainty|lawsuit|liable/.test(t)) out.push('LEGAL_CLAIM');
  if (/medical certainty|diagnose|cure/.test(t)) out.push('MEDICAL_CLAIM');
  if (/threat|harass|abuse/.test(t)) out.push('THREAT_OR_HARASSMENT');
  if (/confidential|nda|private key/.test(t)) out.push('CONFIDENTIALITY_BREACH');
  if (/bypass|exploit|steal|hack/.test(t)) out.push('WRONGDOING_INSTRUCTION');
  if (/guarantee|guaranteed|promise forever/.test(t)) out.push('DISALLOWED_GUARANTEE');
  return [...new Set(out)];
}
