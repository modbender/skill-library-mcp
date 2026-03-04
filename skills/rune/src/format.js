const CATEGORY_TITLES = {
  person: 'People',
  project: 'Projects',
  preference: 'Preferences',
  decision: 'Decisions',
  lesson: 'Lessons',
  environment: 'Environment',
  tool: 'Tools'
};

function titleForCategory(category) {
  if (CATEGORY_TITLES[category]) {
    return CATEGORY_TITLES[category];
  }
  return category.charAt(0).toUpperCase() + category.slice(1);
}

function formatDuration(ms) {
  const abs = Math.max(0, Math.floor(ms / 1000));
  const units = [
    { size: 86400, label: 'd' },
    { size: 3600, label: 'h' },
    { size: 60, label: 'm' },
    { size: 1, label: 's' }
  ];

  for (const unit of units) {
    if (abs >= unit.size) {
      return `${Math.floor(abs / unit.size)}${unit.label}`;
    }
  }

  return '0s';
}

function workingHeader(workingFacts) {
  const now = Date.now();
  const remaining = workingFacts
    .map((fact) => (fact.expires_at ? new Date(fact.expires_at).valueOf() - now : null))
    .filter((ms) => ms != null && Number.isFinite(ms) && ms > 0)
    .sort((a, b) => a - b);

  if (remaining.length === 0) {
    return '## Working Memory';
  }
  return `## Working Memory (expires in ${formatDuration(remaining[0])})`;
}

function formatFactLine(fact) {
  if (!fact.expires_at) {
    return `- **${fact.key}**: ${fact.value}`;
  }

  const delta = new Date(fact.expires_at).valueOf() - Date.now();
  if (!Number.isFinite(delta)) {
    return `- **${fact.key}**: ${fact.value}`;
  }

  if (delta <= 0) {
    return `- **${fact.key}**: ${fact.value} _(expired)_`;
  }

  return `- **${fact.key}**: ${fact.value} _(expires in ${formatDuration(delta)})_`;
}

export function factsToMarkdown(facts) {
  const working = facts.filter((fact) => fact.tier === 'working');
  const longTerm = facts.filter((fact) => fact.tier !== 'working');

  const grouped = new Map();
  for (const fact of longTerm) {
    if (!grouped.has(fact.category)) {
      grouped.set(fact.category, []);
    }
    grouped.get(fact.category).push(fact);
  }

  const categories = [...grouped.keys()].sort((a, b) => a.localeCompare(b));
  const lines = [
    '# Rune - Known Facts',
    '> These are recalled facts from persistent memory. Verify if uncertain.',
    '',
    workingHeader(working)
  ];

  if (working.length === 0) {
    lines.push('- _(none)_');
  } else {
    for (const fact of working) {
      lines.push(formatFactLine(fact));
    }
  }

  for (const category of categories) {
    lines.push('');
    lines.push(`## ${titleForCategory(category)}`);
    for (const fact of grouped.get(category)) {
      lines.push(`- **${fact.key}**: ${fact.value}`);
    }
  }

  return `${lines.join('\n').trim()}\n`;
}

export { titleForCategory };
