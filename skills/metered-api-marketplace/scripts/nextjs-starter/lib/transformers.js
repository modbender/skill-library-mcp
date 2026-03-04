// Copy of the deterministic transformer registry (pure functions).
// Keep this file deterministic: no network, no storage.

function pick(obj, keys) {
  const out = {};
  for (const k of keys) if (obj && obj[k] != null) out[k] = obj[k];
  return out;
}

function asStr(x, d = '') {
  if (x == null) return d;
  return String(x);
}

function words(s) {
  return asStr(s).toLowerCase().split(/\s+/).filter(Boolean);
}

function simpleHashScore(s) {
  const buf = Buffer.from(asStr(s));
  let h = 2166136261;
  for (const b of buf) {
    h ^= b;
    h = Math.imul(h, 16777619);
  }
  return Math.abs(h) % 101;
}

export const transformers = {
  'revenue-amplifier': (input) => {
    const product = input?.product ?? {};
    const market = input?.market ?? {};
    const constraints = input?.constraints ?? {};
    return {
      positioning: `Position ${asStr(product.name, 'the product')} as the simplest path for ${asStr(market.customer, 'the customer')} to achieve ${asStr(market.niche, 'their goal')} with speed + clear proof.`,
      offer_stack: [
        'Core deliverable with measurable outcome',
        'Fast-start onboarding / setup',
        'Risk reversal (trial/guarantee)',
        'Bonus: templates + swipe files',
        'Bonus: weekly optimization review'
      ],
      pricing: { strategy: '3-option anchored pricing with value gates', numbers: [99, 299, 999] },
      headlines: [
        `Get ${asStr(market.niche, 'results')} in 7 days without the usual mess`,
        `The ${asStr(market.niche, 'system')} built for ${asStr(market.customer, 'busy operators')}`,
        `Stop guessing — use a proven offer stack for ${asStr(market.niche, 'this niche')}`
      ],
      risks: ['If promises are vague, conversion will be capped', 'If proof is missing, CAC rises', 'If onboarding is slow, churn spikes'],
      next_steps: ['Add one primary claim + one proof asset above the fold', 'Create a 3-step onboarding checklist', 'Test two headline variants with the same offer'],
      constraints
    };
  },

  'ad-copy-optimizer': (input) => {
    const offer = input?.offer ?? {};
    const niche = asStr(input?.niche, input?.market?.niche ?? 'your niche');
    const channel = asStr(input?.channel, 'ads');
    const tone = asStr(input?.tone, 'direct');

    const uvp = asStr(offer.uvp, `a faster path to ${niche} outcomes`);
    const pain = asStr(offer.pain, `wasting time and money in ${niche}`);

    const angles = [
      { angle: 'speed', hook: `Get results in days, not weeks.` },
      { angle: 'certainty', hook: `Stop guessing — use a proven playbook.` },
      { angle: 'risk-reversal', hook: `Try it without the downside.` },
      { angle: 'simplicity', hook: `No complex setup. Just run the system.` }
    ];

    const variants = angles.map((a) => ({
      channel,
      tone,
      angle: a.angle,
      primary_text: `${a.hook} ${uvp}. If you're dealing with ${pain}, this is the switch.`,
      headline: `${uvp} (without ${pain})`,
      cta: 'Get started'
    }));

    return {
      niche,
      channel,
      tone,
      angles,
      variants,
      compliance_notes: ['Avoid absolute guarantees unless you can prove them', 'Add disclaimers for financial/health claims where required']
    };
  },

  'lead-scoring-engine': (input) => {
    const lead = input?.lead ?? {};
    const icp = input?.icp ?? {};

    const title = asStr(lead.title);
    const company = asStr(lead.company);
    const domain = asStr(lead.domain);
    const employeeCount = Number(lead.employee_count ?? lead.employees ?? 0);
    const budget = Number(lead.budget_usd ?? 0);

    const titleWords = words(title);
    const decisionSignals = ['founder', 'ceo', 'owner', 'vp', 'head', 'director'].some((w) => titleWords.includes(w));

    let score = 0;
    const reasons = [];

    if (decisionSignals) { score += 30; reasons.push('Decision-maker or senior title'); }
    if (employeeCount >= Number(icp.min_employees ?? 0) && employeeCount <= Number(icp.max_employees ?? 1e9)) { score += 20; reasons.push('Company size fits ICP'); }
    if (budget > 0) { score += 20; reasons.push('Budget present'); }
    if (domain) { score += 10; reasons.push('Has domain'); }
    if (company) { score += 10; reasons.push('Has company'); }

    score = Math.min(100, score + Math.floor(simpleHashScore(`${company}|${domain}|${title}`) / 10));

    const band = score >= 80 ? 'hot' : score >= 55 ? 'warm' : 'cold';
    const next_best_action = band === 'hot' ? 'Book a call; send 2-slot scheduling link.' : band === 'warm' ? 'Send a 3-question qualification email and one case study.' : 'Add to nurture; send value-first resource.';

    return {
      score,
      band,
      reasons,
      next_best_action,
      lead_normalized: { title, company, domain, employee_count: employeeCount || null, budget_usd: budget || null }
    };
  },

  'landing-page-generator': (input) => {
    const product = input?.product ?? {};
    const audience = asStr(input?.audience, 'your ideal customer');
    const outcome = asStr(input?.outcome, 'a better outcome');

    const sections = [
      { section: 'hero', elements: ['headline', 'subheadline', 'primary_cta', 'social_proof'] },
      { section: 'problem', elements: ['pain_points', 'cost_of_inaction'] },
      { section: 'solution', elements: ['how_it_works_3_steps', 'differentiators'] },
      { section: 'proof', elements: ['case_study', 'testimonials', 'stats'] },
      { section: 'offer', elements: ['what_you_get', 'bonuses', 'pricing', 'guarantee'] },
      { section: 'objections', elements: ['faq'] },
      { section: 'final_cta', elements: ['cta', 'risk_reversal'] }
    ];

    return {
      product: pick(product, ['name', 'url']),
      outline: {
        headline: `The fastest way for ${audience} to get ${outcome}`,
        subheadline: `A simple system that removes friction and makes results predictable.`,
        primary_cta: 'Start now',
        sections
      },
      faq: [
        { q: 'Who is this for?', a: `${audience} who want ${outcome} without complexity.` },
        { q: 'How fast does it work?', a: 'Most users see early wins within days if they follow the steps.' },
        { q: 'What if it doesn’t work for me?', a: 'Add a guarantee that matches your risk tolerance.' }
      ]
    };
  },

  'competitor-price-monitor': (input) => {
    const items = Array.isArray(input?.items) ? input.items : [];
    const analyzed = items.map((it) => {
      const name = asStr(it.name, 'competitor');
      const price = Number(it.price ?? 0);
      const features = Array.isArray(it.features) ? it.features.map(String) : [];
      return { name, price: Number.isFinite(price) ? price : null, feature_count: features.length, key_features: features.slice(0, 6) };
    });

    const prices = analyzed.map((a) => a.price).filter((p) => typeof p === 'number' && p > 0);
    const avg = prices.length ? prices.reduce((s, p) => s + p, 0) / prices.length : null;

    return {
      mode: 'snapshot-analysis',
      competitors: analyzed,
      summary: { average_price: avg, recommendation: avg ? 'Anchor slightly above average with stronger proof, or slightly below with tighter scope.' : 'Provide competitor prices to compute benchmarks.' }
    };
  },

  'contract-risk-analyzer': (input) => {
    const text = asStr(input?.contract_text, '');
    const flags = [];

    const checks = [
      { key: 'unlimited-liability', re: /unlimited liability|without limitation/i, severity: 'high' },
      { key: 'auto-renew', re: /auto\-?renew|renews automatically/i, severity: 'medium' },
      { key: 'assignment', re: /assign(?:ment)?\b/i, severity: 'low' },
      { key: 'governing-law', re: /governing law|jurisdiction|venue/i, severity: 'low' },
      { key: 'termination-fee', re: /termination fee|early termination/i, severity: 'medium' },
      { key: 'indemnify', re: /indemnif/i, severity: 'medium' }
    ];

    for (const c of checks) if (c.re.test(text)) flags.push({ flag: c.key, severity: c.severity });

    const negotiation_points = flags.map((f) => {
      if (f.flag === 'unlimited-liability') return 'Cap liability (e.g., fees paid in last 12 months).';
      if (f.flag === 'auto-renew') return 'Require advance notice and easy cancellation; shorten renewal term.';
      if (f.flag === 'indemnify') return 'Limit indemnity scope and exclude indirect damages.';
      if (f.flag === 'termination-fee') return 'Reduce or prorate termination fees.';
      return 'Clarify scope and add mutuality where possible.';
    });

    return { risk_level: flags.some((f) => f.severity === 'high') ? 'high' : flags.length ? 'medium' : 'low', flags, negotiation_points: Array.from(new Set(negotiation_points)).slice(0, 10) };
  },

  'market-trend-signal-generator': (input) => {
    const keywords = Array.isArray(input?.keywords) ? input.keywords.map(String) : [];
    const sources = Array.isArray(input?.sources) ? input.sources.map(String) : [];

    const signals = keywords.slice(0, 10).map((k) => ({ keyword: k, signal: `If ${k} is increasing in your inbound/outbound conversations, build a dedicated offer page + 3 ads around it.`, confidence: ['low', 'medium', 'high'][simpleHashScore(k) % 3] }));

    return {
      mode: 'offline-framing',
      sources,
      signals,
      next_steps: ['Collect 20 recent customer quotes and map them to the keywords', 'Run a 7-day test campaign per top 2 signals', 'Promote the winning signal into your core positioning']
    };
  },

  'outbound-personalization-writer': (input) => {
    const prospect = input?.prospect ?? {};
    const offer = input?.offer ?? {};

    const name = asStr(prospect.name, 'there');
    const company = asStr(prospect.company, 'your company');
    const trigger = asStr(prospect.trigger, 'a recent initiative');

    const uvp = asStr(offer.uvp, 'reduce time-to-result');

    return {
      emails: [
        { subject: `Quick idea for ${company}`, body: `Hey ${name} — saw ${trigger}. If you're trying to ${uvp}, we can help.\n\nOpen to a 10-min chat this week?` },
        { subject: `Worth a quick look?`, body: `Circling back — if ${company} is prioritizing ${uvp}, I can send a 1-page plan tailored to your situation. Want it?` }
      ],
      linkedin_dm: `Hey ${name} — quick note: saw ${trigger}. If ${company} is working on ${uvp}, happy to share a short plan. Interested?`
    };
  },

  'seo-brief-content-plan': (input) => {
    const topic = asStr(input?.topic, 'your topic');
    const audience = asStr(input?.audience, 'your audience');

    const cluster = [`${topic} basics`, `${topic} checklist`, `${topic} templates`, `${topic} pricing`, `${topic} mistakes`, `${topic} best practices`];

    return {
      topic,
      audience,
      content_cluster: cluster,
      brief: { intent: 'commercial + informational', outline: ['What it is', 'Who it’s for', 'Step-by-step process', 'Common mistakes', 'Tools/templates', 'FAQ', 'CTA'], internal_links: cluster.slice(1, 5) }
    };
  },

  'arbitrage-spread-detector': (input) => {
    const legs = Array.isArray(input?.legs) ? input.legs : [];
    const opps = [];

    for (const leg of legs) {
      const buy = Number(leg.buy ?? 0);
      const sell = Number(leg.sell ?? 0);
      if (Number.isFinite(buy) && Number.isFinite(sell) && buy > 0 && sell > buy) {
        const spread = sell - buy;
        const pct = spread / buy;
        opps.push({ symbol: asStr(leg.symbol, 'asset'), buy, sell, spread, spread_pct: Number(pct.toFixed(4)), confidence: pct > 0.05 ? 'high' : pct > 0.02 ? 'medium' : 'low' });
      }
    }

    opps.sort((a, b) => b.spread_pct - a.spread_pct);
    return { opportunities: opps.slice(0, 25), notes: ['This is purely arithmetic on provided prices; add fees/slippage checks before live trading.'] };
  },

  'churn-risk-retention-playbook': (input) => {
    const customer = input?.customer ?? {};
    const events = Array.isArray(input?.events) ? input.events.map(String) : [];

    const negativeSignals = ['refund', 'cancel', 'downgrade', 'complaint', 'no-login', 'inactive'];
    const hit = events.some((e) => negativeSignals.some((s) => e.toLowerCase().includes(s)));

    const risk = hit ? 'high' : events.length > 5 ? 'medium' : 'low';

    return {
      risk,
      save_moves: risk === 'high' ? ['Offer fast human help', 'Reduce scope temporarily', 'Provide a clear success plan', 'Offer pause instead of cancel'] : ['Send best-practice guide', 'Invite to office hours', 'Highlight unused features'],
      customer: pick(customer, ['id', 'plan', 'mrr'])
    };
  },

  'support-triage-refund-risk': (input) => {
    const tickets = Array.isArray(input?.tickets) ? input.tickets : [];

    const out = tickets.map((t) => {
      const subject = asStr(t.subject);
      const body = asStr(t.body);
      const text = `${subject} ${body}`.toLowerCase();

      const urgent = /down|outage|can\'?t login|billing error|charged/i.test(text);
      const refund = /refund|chargeback|dispute/i.test(text);

      return {
        ticket_id: asStr(t.id),
        priority: urgent ? 'p0' : refund ? 'p1' : 'p2',
        refund_risk: refund ? 'high' : 'low',
        suggested_macro: urgent ? 'Apologize, confirm impact, provide immediate workaround + ETA.' : refund ? 'Acknowledge, gather details, offer resolution path, avoid blame.' : 'Answer question with steps + link to docs.'
      };
    });

    return { tickets: out, summary: { p0: out.filter((x) => x.priority === 'p0').length, p1: out.filter((x) => x.priority === 'p1').length, p2: out.filter((x) => x.priority === 'p2').length } };
  },

  // --- High-frequency conversion math endpoints (deterministic) ---
  'pricing-anchor': (input) => {
    const targetPrice = Number(input?.product_price ?? input?.price ?? 0);
    const market = asStr(input?.target_market, input?.market ?? 'market');
    const product = asStr(input?.product, input?.product_name ?? 'product');
    const anchor = targetPrice > 0 ? Math.round(targetPrice * 3) : null;
    const floor = targetPrice > 0 ? Math.round(targetPrice * 0.8) : null;
    return {
      product,
      target_market: market,
      target_price: targetPrice || null,
      anchor_price: anchor,
      price_floor_sanity: floor,
      justification_logic: ['Anchor frames the reference point; target feels reasonable by comparison', 'Higher anchor implies completeness / premium outcome', 'Use proof + specificity to defend the anchor'],
      framing_copy: anchor ? [`Comparable solutions in ${market} routinely cost $${anchor}+ when you include time, tools, and mistakes.`, `We priced ${product} at $${targetPrice} because it removes the expensive uncertainty and compresses time-to-result.`] : ['Provide product_price to compute anchor framing.']
    };
  },

  'objection-crush': (input) => {
    const objections = Array.isArray(input?.objections) ? input.objections.map(String) : [];
    const product = asStr(input?.product, 'the offer');
    const playbook = objections.slice(0, 3).map((o) => ({
      objection: o,
      counters: [
        `Reframe: ${o} is valid — which is why ${product} includes a step-by-step path and support.`,
        `Proof: add one measurable example that specifically addresses "${o}".`,
        'Risk removal: add a conditional guarantee tied to implementation.'
      ],
      trust_frames: ['specificity', 'transparency', 'process clarity', 'risk reversal']
    }));
    return {
      product,
      top_objections: objections.slice(0, 3),
      objection_playbook: playbook,
      guarantee_suggestions: ['Implementation-based guarantee ("Do X steps, if no progress, we fix it")', 'Milestone guarantee ("Hit milestone by day N or extend for free")']
    };
  },

  'offer-stack': (input) => {
    const core = asStr(input?.core_offer, input?.core ?? 'core offer');
    const industry = asStr(input?.industry, 'industry');
    const buyer = asStr(input?.target_buyer, input?.buyer ?? 'buyer');
    return {
      core_offer: core,
      industry,
      target_buyer: buyer,
      perceived_value_multipliers: ['Fast-start checklist (first 48 hours)', 'Templates/swipe file pack', 'Implementation review (15-min async audit)', 'Risk reversal / guarantee upgrade', 'Private community or office hours (limited seats)'],
      scarcity_triggers: ['limited cohort', 'deadline bonus removal', 'capacity cap', 'price increases on date'],
      notes: [`Stack bonuses that reduce time-to-value for ${buyer} in ${industry}.`]
    };
  },

  'cta-boost': (input) => {
    const cta = asStr(input?.current_cta, input?.cta ?? 'Get started');
    const stage = asStr(input?.funnel_stage, input?.stage ?? 'consideration');
    const base = ['Get the plan', 'See the breakdown', 'Unlock the playbook', 'Start the fast-track', 'Claim your spot'];
    const urgency = stage.toLowerCase().includes('bottom') || stage.toLowerCase().includes('purchase') ? ['(today)', '(before prices change)', '(limited slots)'] : ['(free)', '(2 min)', '(instant)'];
    const variants = base.map((b, i) => `${b} ${urgency[i % urgency.length]}`.trim());
    return { current_cta: cta, funnel_stage: stage, variants, guidance: ['Match CTA to stage: info CTAs early, commitment CTAs late.'] };
  },

  'headline-power-scorer': (input) => {
    const headline = asStr(input?.headline, '').trim();
    const h = headline.toLowerCase();
    const hasNumber = /\d/.test(headline);
    const hasYou = /\byou\b/.test(h);
    const hasOutcome = /(get|grow|increase|reduce|save|double|fix|stop|avoid|win)/.test(h);
    const hasTime = /(day|days|week|weeks|month|minutes|hour)/.test(h);
    const hasSpecific = headline.length >= 10 && headline.length <= 70;
    let score = 0;
    const missing = [];
    if (hasSpecific) score += 20; else missing.push('length/specificity');
    if (hasOutcome) score += 25; else missing.push('clear outcome verb');
    if (hasYou) score += 15; else missing.push('direct address ("you")');
    if (hasNumber) score += 20; else missing.push('specific number');
    if (hasTime) score += 20; else missing.push('timeframe');
    const hints = [];
    if (!hasOutcome) hints.push('Add an outcome verb: “Get / Increase / Reduce / Save …”');
    if (!hasNumber) hints.push('Add a number: %, $, days, steps, etc.');
    if (!hasTime) hints.push('Add a timeframe: “in 7 days”, “this week”, etc.');
    if (!hasYou) hints.push('Make it about the reader: include “you/your”.');
    return { headline, score, missing_elements: missing, improvement_hints: hints, example_upgrades: headline ? [`How to ${headline} (in 7 days)`, `${headline} — the 3-step system`, `Get ${headline} without the usual mess`] : [] };
  },

  'competitive-undercut': (input) => {
    const competitor = Number(input?.competitor_price ?? 0);
    const marginTarget = Number(input?.margin_target ?? 0.3);
    const cost = Number(input?.unit_cost ?? 0);
    const minPrice = cost > 0 ? cost / (1 - marginTarget) : null;
    const undercut = competitor > 0 ? Math.max(minPrice ?? 0, competitor * 0.95) : null;
    return {
      competitor_price: competitor || null,
      margin_target: marginTarget,
      unit_cost: cost || null,
      minimum_price_for_margin: minPrice ? Number(minPrice.toFixed(2)) : null,
      suggested_price: undercut ? Number(undercut.toFixed(2)) : null,
      positioning_strategy: ['If you undercut, narrow scope to protect margin', 'If you price above, increase proof + guarantees'],
      notes: ['Deterministic math; validate with churn/CAC before changing pricing.']
    };
  },

  'scarcity-clock': (input) => {
    const campaign = asStr(input?.campaign_type, input?.campaign ?? 'launch');
    const duration = asStr(input?.duration, '7 days');
    return {
      campaign_type: campaign,
      duration,
      scarcity_language: [`Enrollment closes in ${duration}.`, 'Capacity is capped to protect delivery quality.', 'Bonuses disappear at the deadline (not later).'],
      deadline_framework: ['hard close', 'bonus removal', 'price increase'],
      compliance_note: 'Only claim scarcity if it’s true.'
    };
  },

  'risk-reversal': (input) => {
    const product = asStr(input?.product, 'the product');
    const price = Number(input?.price ?? 0);
    const hesitation = asStr(input?.buyer_hesitation, input?.hesitation ?? 'risk');
    return {
      product,
      price: price || null,
      buyer_hesitation: hesitation,
      guarantee_models: ['Time-boxed refund guarantee (7/14/30 days)', 'Milestone guarantee (hit X by day N or we extend/support free)', 'Implementation guarantee (do the steps, we fix gaps)', 'Performance credit (partial refund as credits)'],
      refund_structure_notes: ['Keep terms simple', 'Require proof of attempt for implementation guarantees'],
      framing_copy: [`If ${product} isn’t the right fit, you won’t be stuck — we remove the downside.`]
    };
  },

  'upsell-ladder': (input) => {
    const baseOffer = asStr(input?.base_offer, 'base offer');
    const basePrice = Number(input?.base_price ?? 0);
    const audience = asStr(input?.audience_sophistication, input?.audience ?? 'medium');
    const tier1 = basePrice || 49;
    const tier2 = Math.round(tier1 * 3);
    const tier3 = Math.round(tier1 * 10);
    return {
      base_offer: baseOffer,
      audience_sophistication: audience,
      ladder: [{ tier: 'core', price: tier1, value_gate: 'DIY + templates' }, { tier: 'pro', price: tier2, value_gate: 'Done-with-you support + reviews' }, { tier: 'premium', price: tier3, value_gate: 'Done-for-you implementation / concierge' }],
      profit_projection_simple: { example_100_buyers: { core: 100 * tier1, pro_if_20pct: 20 * tier2, premium_if_5pct: 5 * tier3 } }
    };
  },

  'authority-positioning': (input) => {
    const niche = asStr(input?.niche, 'niche');
    const product = asStr(input?.product, 'product');
    const story = asStr(input?.founder_story, input?.story ?? '');
    return {
      niche,
      product,
      positioning_angles: ['Operator-led: built from real execution, not theory', 'Contrarian: avoid the common mistake everyone makes', 'Method: name a repeatable framework', 'Proof stack: quantify outcomes + show artifacts'],
      credibility_stack: ['case study', 'before/after', 'process screenshots', 'social proof', 'transparent methodology'],
      trust_hooks: story ? [`Founder story hook: ${story.slice(0, 140)}...`] : ['Add a 2-sentence founder origin tied to the pain.']
    };
  },

  'simple-arbitrage-signal': (input) => {
    const buy = Number(input?.buy_price ?? 0);
    const sell = Number(input?.sell_price ?? 0);
    const fees = Number(input?.fees ?? 0);
    const net = sell - buy - fees;
    const go = buy > 0 && net > 0;
    const breakevenSell = buy + fees;
    return { buy_price: buy || null, sell_price: sell || null, fees: fees || 0, net_margin: Number.isFinite(net) ? Number(net.toFixed(4)) : null, go_no_go: go ? 'go' : 'no-go', breakeven_sell_price: Number.isFinite(breakevenSell) ? Number(breakevenSell.toFixed(4)) : null };
  },

  'funnel-leak-detector': (input) => {
    const traffic = Number(input?.traffic ?? 0);
    const optin = Number(input?.opt_in_rate ?? input?.optin_rate ?? 0);
    const conv = Number(input?.conversion_rate ?? 0);
    const aov = Number(input?.aov ?? 0);
    const leads = traffic * optin;
    const customers = leads * conv;
    const revenue = customers * aov;
    const baselines = { optin: 0.03, conv: 0.02 };
    const optinGap = baselines.optin > 0 ? optin / baselines.optin : 1;
    const convGap = baselines.conv > 0 ? conv / baselines.conv : 1;
    const biggestLeak = optinGap < convGap ? 'opt_in_rate' : 'conversion_rate';
    return {
      inputs: { traffic, opt_in_rate: optin, conversion_rate: conv, aov },
      math: { leads: Number.isFinite(leads) ? Number(leads.toFixed(2)) : null, customers: Number.isFinite(customers) ? Number(customers.toFixed(2)) : null, revenue: Number.isFinite(revenue) ? Number(revenue.toFixed(2)) : null },
      biggest_leak: biggestLeak,
      recommended_fix: biggestLeak === 'opt_in_rate' ? ['Improve lead magnet + headline', 'Reduce form friction', 'Add proof above the opt-in'] : ['Tighten offer + risk reversal', 'Improve checkout friction', 'Add urgency + clearer CTA'],
      note: 'Pure math + heuristic baselines; replace baselines with your benchmarks.'
    };
  }
};

export const transformerNames = Object.keys(transformers);
