const PACKS = {
  founder: ['Pragmatic Founder', 'Brand Guardian', 'Risk Auditor', 'Growth Operator', 'User Advocate'],
  comms: ['Clarity Editor', 'Trust Builder', 'Tone Coach', 'Audience Analyst', 'Crisis Communicator'],
  security: ['Threat Modeler', 'Compliance Skeptic', 'Data Minimizer', 'Abuse Analyst', 'Policy Enforcer'],
  creator: ['Narrative Stylist', 'Engagement Maximizer', 'Platform Strategist', 'Monetization Guard', 'Authenticity Keeper']
};

export async function generatePersonas({ task_context, n_personas = 5, persona_pack = 'founder' }) {
  const names = (PACKS[persona_pack] || PACKS.founder).slice(0, n_personas);
  return names.map((name, i) => ({
    persona_id: `persona_${i + 1}`,
    name,
    role: name,
    voice: i % 2 ? 'direct and skeptical' : 'concise and practical',
    bias: i % 2 ? 'risk avoidance' : 'execution speed',
    non_negotiables: ['No fabricated claims', 'Clear user impact'],
    reputation: Number((0.55 + (i * (0.35 / Math.max(1, n_personas - 1)))).toFixed(2)),
    risk_posture: i % 3 === 0 ? 'low' : i % 3 === 1 ? 'medium' : 'high',
    voting_style: i % 3 === 0 ? 'strict' : i % 3 === 1 ? 'balanced' : 'lenient',
    failure_modes: ['Over-index on own bias', 'Miss hidden stakeholder constraints']
  }));
}
