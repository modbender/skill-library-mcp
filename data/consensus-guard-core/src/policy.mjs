export function aggregateVotes(votes, policy={}) {
  let yes=0,no=0,rewrite=0,total=0,hard_block=false;
  for (const v of votes) {
    const w = Number(v.reputation_before||0); total += w;
    if (v.vote==='YES') yes += w;
    if (v.vote==='NO') no += w;
    if (v.vote==='REWRITE') rewrite += w;
    if ((v.red_flags||[]).length) hard_block = true;
  }
  if (total>0) { yes/=total; no/=total; rewrite/=total; }
  const threshold = Number(policy.approve_threshold ?? 0.7);
  let final_decision = 'BLOCK';
  const rationale = [];
  if (hard_block) { final_decision='BLOCK'; rationale.push('hard_block detected'); }
  else if (yes>=threshold) { final_decision='APPROVE'; rationale.push('approval threshold met'); }
  else if (rewrite>0) { final_decision='REWRITE'; rationale.push('fixable issues exist'); }
  else { final_decision='BLOCK'; rationale.push('insufficient approval'); }
  return { method: policy.method || 'WEIGHTED_APPROVAL_VOTE', weighted_yes:+yes.toFixed(6), weighted_no:+no.toFixed(6), weighted_rewrite:+rewrite.toFixed(6), hard_block, rationale, final_decision };
}

export function updateReputations(personas, votes, finalDecision) {
  const map = new Map(votes.map(v=>[v.persona_id,v]));
  const updates=[];
  const next = personas.map((p)=>{
    const v = map.get(p.persona_id); if (!v) return p;
    const aligned = (finalDecision==='APPROVE'&&v.vote==='YES')||(finalDecision==='BLOCK'&&v.vote==='NO')||(finalDecision==='REWRITE'&&v.vote==='REWRITE');
    let delta = aligned ? 0.02 : -0.03;
    if (!aligned && Number(v.confidence||0)>0.85) delta -= 0.02;
    const after = Math.min(0.95, Math.max(0.05, +(p.reputation + delta).toFixed(2)));
    updates.push({ persona_id:p.persona_id, reputation_after:after, delta:+(after-p.reputation).toFixed(2) });
    return { ...p, reputation: after };
  });
  return { personas: next, updates };
}
