#!/usr/bin/env node
// neuroboost-elixir/src/cli.mjs
// CLI: neuroboost diagnose / neuroboost demo

import { NeuroBoost } from './index.mjs';

const cmd = process.argv[2];

if (cmd === 'demo') {
  console.log('🧠💊 NeuroBoost Elixir v2.1 — Demo Run\n');

  const nb = new NeuroBoost({
    models: [
      { name: 'mini', costPerCall: 0.003 },
      { name: 'mid', costPerCall: 0.015 },
      { name: 'frontier', costPerCall: 0.05 },
    ],
    targetBurnRate: 0.02
  });

  // Add strategies
  nb.optimizer.addStrategy('meme-scan');
  nb.optimizer.addStrategy('arb-scan');
  nb.optimizer.addStrategy('social-outreach');

  // Simulate 30 turns
  console.log('Simulating 30 turns...\n');
  nb.updateBalance(10.00); // Start with $10

  for (let i = 0; i < 30; i++) {
    const { model, strategy, mode } = nb.beforeTurn();
    
    // Simulate outcomes
    const cost = model.costPerCall * (0.5 + Math.random());
    const success = Math.random() > 0.3;
    const reward = success ? cost * (1 + Math.random() * 3) : 0;
    
    nb.afterTurn({
      model: model.name,
      strategy,
      cost,
      reward,
      error: Math.random() > 0.9,
      hadEffect: success
    });

    const balance = 10 - nb.sentinel.turns.reduce((s, t) => s + (t.cost || 0), 0);
    nb.updateBalance(Math.max(0, balance));
  }

  // Output diagnosis
  const diag = nb.diagnose();
  console.log('=== Status ===');
  console.log(nb.status());
  console.log('\n=== Resource Control ===');
  console.log(diag.resource);
  console.log('\n=== Model Performance ===');
  console.table(diag.models);
  console.log('\n=== Strategy Performance ===');
  console.table(diag.strategies);
  console.log('\n=== Diagnostics ===');
  console.log('Waste ratio:', diag.diagnostics.wasteRatio);
  console.log('Error rate:', diag.diagnostics.errorRate);
  console.log('Error trend:', diag.diagnostics.errorTrend);
  console.log('Actions:', diag.diagnostics.actions.length > 0 ? diag.diagnostics.actions : 'None needed');
  console.log('\n=== Meta Learning ===');
  console.log(diag.meta);

  console.log('\n✅ Demo complete. Install: clawhub install neuroboost-elixir');

} else if (cmd === 'version') {
  console.log('neuroboost-elixir v2.1.0');

} else {
  console.log(`🧠💊 NeuroBoost Elixir v2.1

Usage:
  neuroboost demo      Run a 100-turn simulation demo
  neuroboost version   Show version

Integration:
  import { NeuroBoost } from 'neuroboost-elixir'
  const nb = new NeuroBoost({ targetBurnRate: 0.02 })
  
  // Before each turn
  const { model, strategy, mode } = nb.beforeTurn()
  
  // After each turn
  nb.afterTurn({ model: model.name, cost, reward, error, hadEffect })
  
  // Diagnose
  console.log(nb.diagnose())

Free: clawhub.com/skills/neuroboost-elixir`);
}
