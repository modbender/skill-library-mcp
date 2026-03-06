export function aggregateVotes(votes, policy) {
  let total = 0;
  let weighted_yes = 0;
  let weighted_no = 0;
  let weighted_rewrite = 0;
  let hard_block = false;

  for (const v of votes) {
    const w = Number(v.reputation_before || 0);
    total += w;
    if (v.vote === 'YES') weighted_yes += w;
    if (v.vote === 'NO') weighted_no += w;
    if (v.vote === 'REWRITE') weighted_rewrite += w;

    if ((v.red_flags || []).some((f) => /threat|harass|doxx|sensitive|legal_claim|medical_claim|wrongdoing|confidential/i.test(f))) {
      hard_block = true;
    }
  }

  if (total > 0) {
    weighted_yes = weighted_yes / total;
    weighted_no = weighted_no / total;
    weighted_rewrite = weighted_rewrite / total;
  }

  const threshold = policy.approve_threshold ?? 0.7;
  let final_decision = 'BLOCK';
  const rationale = [];

  if (hard_block) {
    final_decision = 'BLOCK';
    rationale.push('hard_block detected');
  } else if (weighted_yes >= threshold) {
    final_decision = 'APPROVE';
    rationale.push(`weighted_yes ${weighted_yes.toFixed(3)} >= threshold ${threshold}`);
  } else if (weighted_rewrite > 0) {
    final_decision = 'REWRITE';
    rationale.push('rewrite suggestions available');
  } else {
    final_decision = 'BLOCK';
    rationale.push('insufficient approval weight and no fixable path');
  }

  return {
    method: policy.method || 'WEIGHTED_APPROVAL_VOTE',
    weighted_yes: Number(weighted_yes.toFixed(6)),
    weighted_no: Number(weighted_no.toFixed(6)),
    weighted_rewrite: Number(weighted_rewrite.toFixed(6)),
    hard_block,
    rationale,
    final_decision
  };
}

export function updateReputations(personas, votes, finalDecision) {
  const voteById = new Map(votes.map((v) => [v.persona_id, v]));
  const updates = [];
  const next = personas.map((p) => {
    const v = voteById.get(p.persona_id);
    if (!v) return p;

    const aligned =
      (finalDecision === 'APPROVE' && v.vote === 'YES') ||
      (finalDecision === 'BLOCK' && v.vote === 'NO') ||
      (finalDecision === 'REWRITE' && v.vote === 'REWRITE');

    let delta = aligned ? 0.02 : -0.03;
    if (!aligned && Number(v.confidence || 0) > 0.85) delta -= 0.02;

    const reputation_after = Math.min(0.95, Math.max(0.05, Number((p.reputation + delta).toFixed(2))));
    updates.push({ persona_id: p.persona_id, reputation_after, delta: Number((reputation_after - p.reputation).toFixed(2)) });
    return { ...p, reputation: reputation_after };
  });

  return { personas: next, updates };
}
