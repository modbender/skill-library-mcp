#!/usr/bin/env node
// add.mjs — Add entity or relation to KG
// Usage:
//   node add.mjs entity --id X --type T --label L [--alias A] [--parent P] [--category C] [--tags t1,t2] [--attrs '{}']
//   node add.mjs rel --from X --to Y --rel R [--attrs '{}']
//   node add.mjs quick "Label:type" [--parent P] [--category C]

import { load, save, addNode, addEdge } from '../lib/graph.mjs';
const args = process.argv.slice(2);
const cmd = args[0];

function flag(name) {
  const i = args.indexOf('--' + name);
  return i !== -1 ? args[i + 1] : null;
}

try {
  const store = load();

  if (cmd === 'entity') {
    const id = flag('id');
    if (!id) { console.error('--id required'); process.exit(1); }
    const node = addNode(store, {
      id,
      alias: flag('alias'),
      type: flag('type') || 'concept',
      label: flag('label') || id,
      parent: flag('parent'),
      category: flag('category'),
      tags: flag('tags') ? flag('tags').split(',') : [],
      attrs: flag('attrs') ? JSON.parse(flag('attrs')) : {},
      confidence: flag('confidence')
    });
    save(store);
    console.log(`✅ Added entity: ${node.label} (${node.id})`);

  } else if (cmd === 'rel') {
    const from = flag('from'), to = flag('to'), rel = flag('rel');
    if (!from || !to || !rel) { console.error('--from, --to, --rel required'); process.exit(1); }
    const edge = addEdge(store, { from, to, rel, attrs: flag('attrs') ? JSON.parse(flag('attrs')) : {} });
    save(store);
    console.log(`✅ Added relation: ${from} >${rel}> ${to}`);

  } else if (cmd === 'quick') {
    // quick "Label:type" → auto-generate id, alias, and tags from label
    const spec = args[1];
    if (!spec) { console.error('Usage: add.mjs quick "Label:type"'); process.exit(1); }
    const [label, type] = spec.split(':');
    const id = label.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');

    // Auto-generate tags from label if none provided
    let tags = flag('tags') ? flag('tags').split(',') : [];
    if (tags.length === 0) {
      const words = label.split(/[\s\-_./]+/).filter(w => w.length > 0);
      // Add: lowercase label, individual words (>2 chars), acronym if multi-word
      tags.push(label.toLowerCase());
      for (const w of words) {
        const lw = w.toLowerCase();
        if (lw.length > 2 && !tags.includes(lw)) tags.push(lw);
      }
      // Generate acronym for multi-word labels (e.g. "Knowledge Graph" → "KG")
      if (words.length >= 2) {
        const acronym = words.map(w => w[0]).join('').toUpperCase();
        if (acronym.length >= 2 && !tags.includes(acronym)) tags.push(acronym);
      }
      // Add kebab-case id as tag if different from label
      if (!tags.includes(id) && id !== label.toLowerCase()) tags.push(id);
      // Deduplicate
      tags = [...new Set(tags)];
    }

    const node = addNode(store, {
      id,
      alias: flag('alias') || id.slice(0, 3).toUpperCase(),
      type: type || 'concept',
      label,
      parent: flag('parent'),
      category: flag('category'),
      tags,
      attrs: flag('attrs') ? JSON.parse(flag('attrs')) : {},
      confidence: flag('confidence')
    });
    save(store);
    console.log(`✅ Quick add: ${node.label} (${node.id}) [${node.type}]`);
    if (tags.length) console.log(`   Auto-tags: ${tags.join(', ')}`);

  } else {
    console.log('Usage: add.mjs <entity|rel|quick> [options]');
  }
} catch (e) {
  console.error('❌', e.message);
  process.exit(1);
}
