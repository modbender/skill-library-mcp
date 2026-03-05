type ScamRecord = {
  id: string;
  type: 'domain' | 'contract' | 'pattern';
  value: string;
  label: string;
  risk: 'low' | 'medium' | 'high';
  notes: string;
  source: string;
  updated_at: string;
};

type RiskLevel = 'low' | 'medium' | 'high';

const KNOWN_SCAMS: ScamRecord[] = [
  {
    id: 'scam-domain-wallet-near-support',
    type: 'domain',
    value: 'wallet-near.support',
    label: 'Impersonates wallet.near.org support',
    risk: 'high',
    notes: 'Lookalike support domain pattern used in wallet-drain campaigns.',
    source: 'internal_seed_db',
    updated_at: '2026-02-20T00:00:00Z'
  },
  {
    id: 'scam-domain-near-airdrop-claim',
    type: 'domain',
    value: 'near-airdrop-claim.com',
    label: 'Fake airdrop claim page',
    risk: 'high',
    notes: 'Uses urgency and reward bait to collect seed phrases.',
    source: 'internal_seed_db',
    updated_at: '2026-02-20T00:00:00Z'
  },
  {
    id: 'scam-contract-fake-usn-minter',
    type: 'contract',
    value: 'usn-minter.near',
    label: 'Suspicious fake minter naming pattern',
    risk: 'medium',
    notes: 'Name resembles historical assets and can be abused for impersonation.',
    source: 'internal_seed_db',
    updated_at: '2026-02-20T00:00:00Z'
  },
  {
    id: 'pattern-seed-phrase-request',
    type: 'pattern',
    value: 'seed_phrase_request',
    label: 'Requests seed phrase/private key',
    risk: 'high',
    notes: 'No legitimate support flow requests seed phrase or private key.',
    source: 'near_security_best_practice',
    updated_at: '2026-02-20T00:00:00Z'
  }
];

function hashString(input: string): string {
  let hash = 2166136261;
  for (let i = 0; i < input.length; i += 1) {
    hash ^= input.charCodeAt(i);
    hash = Math.imul(hash, 16777619);
  }
  return (hash >>> 0).toString(16);
}

function normalizeDomain(domain: string): string {
  return domain.trim().toLowerCase().replace(/^www\./, '').replace(/\.+$/, '');
}

function extractDomain(url: string): string | null {
  try {
    const withProtocol = /^https?:\/\//i.test(url) ? url : `https://${url}`;
    const parsed = new URL(withProtocol);
    return normalizeDomain(parsed.hostname);
  } catch {
    return null;
  }
}

function tokenizeDomain(domain: string): string[] {
  return domain.split(/[-.]/).filter(Boolean);
}

function looksLikeNearTyposquat(domain: string): boolean {
  const normalized = normalizeDomain(domain);
  if (normalized.includes('xn--')) {
    return true;
  }

  const d = normalized.replace(/[^a-z0-9]/g, '');
  const suspiciousNearLookalikes = ['n3ar', 'nearw', 'nearwallet', 'near-support', 'wa1letnear', 'waIletnear'];
  if (suspiciousNearLookalikes.some((p) => normalized.includes(p.toLowerCase()))) {
    return true;
  }

  // Basic edit-distance-like heuristic around wallet.near.org style words
  return d.includes('wa11etnear') || d.includes('wallettnear') || d.includes('nearairdrop') || d.includes('nearclaim');
}

function computeRisk(points: number): RiskLevel {
  if (points >= 70) return 'high';
  if (points >= 35) return 'medium';
  return 'low';
}

function riskAdvice(level: RiskLevel): string[] {
  if (level === 'high') {
    return [
      'Do not connect wallet or sign transactions on this target.',
      'Verify through official NEAR channels only.',
      'Report immediately to security/community moderators.'
    ];
  }
  if (level === 'medium') {
    return [
      'Use read-only verification before any wallet interaction.',
      'Cross-check contract/domain with trusted docs.',
      'Treat as suspicious until independently validated.'
    ];
  }
  return [
    'No strong phishing signal detected from current heuristics.',
    'Still validate destination and transaction details before signing.'
  ];
}

export async function near_phishing_check_url(url: string): Promise<Record<string, unknown>> {
  const target = String(url ?? '').trim();
  if (!target) {
    return {
      ok: false,
      error: 'url_required',
      risk_level: 'high',
      risk_score: 100,
      reasons: ['URL is empty or invalid.'],
      recommendations: riskAdvice('high')
    };
  }

  const domain = extractDomain(target);
  if (!domain) {
    return {
      ok: false,
      error: 'url_parse_failed',
      risk_level: 'high',
      risk_score: 95,
      reasons: ['Could not parse URL. Often seen in obfuscated phishing payloads.'],
      recommendations: riskAdvice('high')
    };
  }

  let points = 0;
  const reasons: string[] = [];

  const knownDomain = KNOWN_SCAMS.find((s) => s.type === 'domain' && normalizeDomain(s.value) === domain);
  if (knownDomain) {
    points += 90;
    reasons.push(`Domain matches known scam record: ${knownDomain.id}`);
  }

  const tokens = tokenizeDomain(domain);
  if (tokens.length > 4) {
    points += 10;
    reasons.push('Domain has unusually high token count (common in deceptive links).');
  }

  if (looksLikeNearTyposquat(domain)) {
    points += 45;
    reasons.push('Domain appears to mimic NEAR/wallet branding (typosquat/lookalike).');
  }

  if (domain.endsWith('.zip') || domain.endsWith('.click') || domain.endsWith('.top')) {
    points += 25;
    reasons.push('High-abuse TLD category detected.');
  }

  if (/\d/.test(domain) && /[a-z]/.test(domain)) {
    points += 8;
    reasons.push('Mixed alphanumeric domain pattern can indicate obfuscation.');
  }

  const risk_level = computeRisk(points);

  return {
    ok: true,
    input_url: target,
    domain,
    risk_score: Math.min(points, 100),
    risk_level,
    reasons,
    matched_known_scam: knownDomain
      ? {
          id: knownDomain.id,
          label: knownDomain.label,
          source: knownDomain.source
        }
      : null,
    recommendations: riskAdvice(risk_level),
    checked_at: new Date().toISOString()
  };
}

function isValidNearAccountId(input: string): boolean {
  return /^[a-z0-9._-]{2,64}$/.test(input);
}

function suspiciousContractSignals(contract: string): string[] {
  const c = contract.toLowerCase();
  const reasons: string[] = [];

  if (!isValidNearAccountId(c)) {
    reasons.push('Contract ID does not match expected NEAR account format.');
  }
  if (/airdrop|claim|reward|bonus|gift/.test(c)) {
    reasons.push('Contract name uses high-risk incentive bait words.');
  }
  if (/support|help|verify|recovery/.test(c)) {
    reasons.push('Contract name mimics support/recovery workflow.');
  }
  if (/0x|wallet|seed|private/.test(c)) {
    reasons.push('Contract name contains terms often used in scam social engineering.');
  }
  if ((c.match(/[.-]/g) ?? []).length >= 2) {
    reasons.push('Contract naming structure is unusually segmented and may be deceptive.');
  }

  return reasons;
}

export async function near_phishing_check_contract(contract: string): Promise<Record<string, unknown>> {
  const target = String(contract ?? '').trim();
  if (!target) {
    return {
      ok: false,
      error: 'contract_required',
      risk_level: 'high',
      risk_score: 100,
      reasons: ['Contract is empty.'],
      recommendations: riskAdvice('high')
    };
  }

  const normalized = target.toLowerCase();
  let points = 0;
  const reasons: string[] = [];

  const knownContract = KNOWN_SCAMS.find((s) => s.type === 'contract' && s.value.toLowerCase() === normalized);
  if (knownContract) {
    points += 80;
    reasons.push(`Contract matches suspicious database record: ${knownContract.id}`);
  }

  const heuristics = suspiciousContractSignals(normalized);
  points += heuristics.length * 20;
  reasons.push(...heuristics);

  const risk_level = computeRisk(points);

  return {
    ok: true,
    contract: normalized,
    risk_score: Math.min(points, 100),
    risk_level,
    reasons,
    matched_known_scam: knownContract
      ? {
          id: knownContract.id,
          label: knownContract.label,
          source: knownContract.source
        }
      : null,
    recommendations: riskAdvice(risk_level),
    checked_at: new Date().toISOString()
  };
}

export async function near_phishing_report(url: string, details: string): Promise<Record<string, unknown>> {
  const targetUrl = String(url ?? '').trim();
  const note = String(details ?? '').trim();

  const urlCheck = await near_phishing_check_url(targetUrl);
  const risk_level = (urlCheck.risk_level as RiskLevel) || 'medium';
  const score = Number(urlCheck.risk_score ?? 0);

  const reportId = `near-phish-${hashString(`${targetUrl}|${note}|${new Date().toISOString().slice(0, 10)}`)}`;

  return {
    ok: true,
    report_id: reportId,
    category: 'near_phishing_attempt',
    target_url: targetUrl,
    details: note || null,
    triage: {
      risk_level,
      risk_score: score,
      priority: risk_level === 'high' ? 'p1' : risk_level === 'medium' ? 'p2' : 'p3'
    },
    next_actions: [
      'Archive evidence (URL, screenshots, wallet prompts).',
      'Share report with trusted security moderators.',
      'Warn affected users not to sign transactions.'
    ],
    generated_at: new Date().toISOString()
  };
}

export async function near_phishing_database(): Promise<ScamRecord[]> {
  return KNOWN_SCAMS.map((item) => ({ ...item }));
}
