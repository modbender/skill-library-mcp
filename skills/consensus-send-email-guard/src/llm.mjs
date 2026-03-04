export async function generatePersonaVotes(personaSet, emailDraft, constraints = {}) {
  const text = `${emailDraft.subject || ''}\n${emailDraft.body || ''}`.toLowerCase();

  return personaSet.personas.map((p) => {
    let vote = 'YES';
    const red_flags = [];
    const suggested_edits = [];

    if (/guarantee|guaranteed|promise/.test(text) && constraints.no_pricing_promises) {
      vote = 'REWRITE';
      red_flags.push('pricing_guarantee');
      suggested_edits.push('Remove guarantees and convert to probabilistic wording.');
    }

    if (/confidential|ssn|social security|dob/.test(text) && constraints.no_sensitive_data) {
      vote = 'NO';
      red_flags.push('sensitive_data');
    }

    if (/lawsuit|legal certainty|medical certainty/.test(text) && constraints.no_legal_claims) {
      vote = 'NO';
      red_flags.push('legal_claim');
    }

    return {
      persona_id: p.persona_id,
      name: p.name,
      reputation_before: p.reputation,
      vote,
      confidence: vote === 'NO' ? 0.9 : vote === 'REWRITE' ? 0.75 : 0.7,
      reasons: vote === 'YES' ? ['No blocking risk found.'] : ['Policy/constraint risk found.'],
      red_flags,
      suggested_edits
    };
  });
}

export async function generateRewritePatch(emailDraft) {
  return {
    subject: (emailDraft.subject || '').replace(/guarantee/gi, 'plan').replace(/promise/gi, 'expectation'),
    body: (emailDraft.body || '')
      .replace(/guarantee(d)?/gi, 'aim')
      .replace(/promise/gi, 'intend')
      .replace(/confidential[^\n]*/gi, 'We will protect your data under our privacy policy.')
  };
}
