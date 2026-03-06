#!/usr/bin/env node
/**
 * Swarm CLI Client
 * Quick way to execute Swarm tasks from command line
 * 
 * Usage:
 *   swarm research "OpenAI" "Anthropic" "Google" --topic "AI products"
 *   swarm parallel "prompt1" "prompt2" "prompt3"
 *   swarm status
 */

const { SwarmClient } = require('../lib/client');

const client = new SwarmClient();

async function main() {
  const args = process.argv.slice(2);
  const command = args[0];

  if (!command || command === 'help' || command === '--help') {
    console.log('🐝 Swarm CLI');
    console.log('');
    console.log('Usage:');
    console.log('  swarm status');
    console.log('  swarm capabilities                          — Discover available execution modes');
    console.log('  swarm parallel <prompt1> <prompt2> ...      — N prompts, N workers, one pass');
    console.log('  swarm research <subj1> <subj2> --topic "t"  — Multi-phase web research');
    console.log('  swarm chain <json-file>                     — Refinement pipeline from JSON def');
    console.log('  swarm chain --stdin                         — Read chain def from stdin');
    console.log('');
    console.log('Options:');
    console.log('  --context    Pre-fetch BrainDB memories and inject into worker prompts');
    console.log('');
    console.log('Chain modes:');
    console.log('  parallel   — N inputs → N workers (same perspective)');
    console.log('  single     — merged input → 1 worker');
    console.log('  fan-out    — 1 input → N workers (different perspectives)');
    console.log('  reduce     — N inputs → 1 synthesized output');
    console.log('');
    console.log('Built-in perspectives:');
    console.log('  extractor, filter, enricher, analyst, synthesizer,');
    console.log('  challenger, optimizer, strategist, researcher, critic');
    console.log('');
    console.log('Examples:');
    console.log('  swarm research OpenAI Anthropic Google --topic "AI products 2024"');
    console.log('  swarm parallel "What is 2+2?" "What is 3+3?"');
    console.log('  swarm chain my-pipeline.json');
    console.log('  swarm capabilities');
    console.log('');
    console.log('Make sure daemon is running: swarm-daemon start');
    return;
  }

  // Check daemon
  const ready = await client.isReady();
  if (!ready && command !== 'status') {
    console.error('❌ Swarm Daemon is not running');
    console.error('   Start it with: swarm-daemon start');
    process.exit(1);
  }

  switch (command) {
    case 'status': {
      if (!ready) {
        console.log('❌ Swarm Daemon is not running');
        console.log('   Start with: swarm-daemon start');
      } else {
        const status = await client.status();
        console.log('🐝 Swarm Status');
        console.log('─'.repeat(40));
        console.log(`   Workers:   ${status.workers?.totalNodes || 0}`);
        console.log(`   Requests:  ${status.requests}`);
        console.log(`   Tasks:     ${status.totalTasks}`);
        console.log(`   Avg time:  ${status.avgResponseMs}ms`);
        console.log(`   Uptime:    ${Math.round(status.uptime / 1000)}s`);
        if (status.cache && status.cache.entries > 0) {
          console.log('');
          console.log('📦 Cache');
          console.log('─'.repeat(40));
          console.log(`   Entries:   ${status.cache.entries}/${status.cache.maxEntries}`);
          console.log(`   Hit rate:  ${status.cache.hitRate}`);
          console.log(`   Hits:      ${status.cache.hits} | Misses: ${status.cache.misses}`);
        }
        if (status.cost) {
          const s = status.cost.session || status.cost;
          const d = status.cost.daily;
          console.log('');
          console.log('💰 Cost (this session)');
          console.log('─'.repeat(40));
          console.log(`   Tokens:    ${s.inputTokens.toLocaleString()} in / ${s.outputTokens.toLocaleString()} out`);
          console.log(`   Swarm:     $${s.swarmCost}`);
          console.log(`   Opus eq:   $${s.opusEquivalent}`);
          console.log(`   Saved:     $${s.saved} (${s.savingsMultiplier})`);
          if (d && parseFloat(d.swarmCost) !== parseFloat(s.swarmCost)) {
            console.log('');
            console.log('📊 Cost (today total)');
            console.log('─'.repeat(40));
            console.log(`   Tokens:    ${d.inputTokens.toLocaleString()} in / ${d.outputTokens.toLocaleString()} out`);
            console.log(`   Swarm:     $${d.swarmCost}`);
            console.log(`   Opus eq:   $${d.opusEquivalent}`);
            console.log(`   Saved:     $${d.saved} (${d.savingsMultiplier})`);
          }
        }
      }
      break;
    }

    case 'research': {
      // Parse: swarm research subj1 subj2 subj3 --topic "topic" [--context]
      const useContextR = args.includes('--context');
      const filteredArgsR = args.filter(a => a !== '--context');
      const topicIdx = filteredArgsR.indexOf('--topic');
      let subjects, topic;
      
      if (topicIdx !== -1) {
        subjects = filteredArgsR.slice(1, topicIdx);
        topic = filteredArgsR.slice(topicIdx + 1).join(' ');
      } else {
        subjects = filteredArgsR.slice(1);
        topic = 'latest news and information';
      }

      if (subjects.length === 0) {
        console.error('Usage: swarm research <subject1> <subject2> ... --topic "topic"');
        process.exit(1);
      }

      console.log(`🐝 Researching ${subjects.length} subjects: ${subjects.join(', ')}`);
      console.log(`   Topic: ${topic}`);
      if (useContextR) console.log(`   🧠 BrainDB context: enabled`);
      console.log('');

      const startTime = Date.now();
      
      for await (const event of client.research(subjects, topic, { context: useContextR })) {
        switch (event.event) {
          case 'context':
            console.log(`🧠 ${event.message}`);
            break;
          case 'start':
            console.log(`⚡ ${event.message}`);
            break;
          case 'phase':
            console.log(`   Phase: ${event.name} (${event.taskCount} tasks)`);
            break;
          case 'task':
            // Progress indicator
            process.stdout.write('.');
            break;
          case 'complete':
            console.log('\n');
            console.log(`✓ Complete in ${event.duration}ms`);
            console.log('');
            for (const analysis of event.analyses) {
              console.log(`=== ${analysis.subject} ===`);
              console.log(analysis.analysis || '(no output)');
              console.log('');
            }
            break;
          case 'error':
            console.error(`❌ Error: ${event.error}`);
            break;
        }
      }
      break;
    }

    case 'parallel': {
      const useContextP = args.includes('--context');
      const prompts = args.slice(1).filter(a => a !== '--context');
      
      if (prompts.length === 0) {
        console.error('Usage: swarm parallel <prompt1> <prompt2> ... [--context]');
        process.exit(1);
      }

      console.log(`🐝 Executing ${prompts.length} prompts in parallel`);
      if (useContextP) console.log(`   🧠 BrainDB context: enabled`);

      for await (const event of client.parallel(prompts, { context: useContextP })) {
        switch (event.event) {
          case 'context':
            console.log(`🧠 ${event.message}`);
            break;
          case 'start':
            console.log(`⚡ ${event.message}`);
            break;
          case 'progress':
            process.stdout.write('.');
            break;
          case 'complete':
            console.log('\n');
            console.log(`✓ Complete in ${event.duration}ms`);
            console.log('');
            event.results.forEach((result, i) => {
              console.log(`[${i + 1}] ${result || '(no output)'}`);
              console.log('');
            });
            break;
          case 'error':
            console.error(`❌ Error: ${event.error}`);
            break;
        }
      }
      break;
    }

    case 'capabilities':
    case 'caps': {
      const capsResp = await fetch(`http://localhost:9999/capabilities`);
      const caps = await capsResp.json();
      console.log('🐝 Swarm Capabilities');
      console.log('─'.repeat(50));
      console.log(`   Provider: ${caps.provider} (${caps.model})`);
      console.log(`   Web search: ${caps.webSearch ? '✅' : '❌'}`);
      console.log(`   Max workers: ${caps.limits.maxWorkers}`);
      console.log('');
      console.log('Execution Modes:');
      for (const [name, mode] of Object.entries(caps.modes)) {
        console.log(`\n   📌 ${name}`);
        console.log(`      ${mode.description}`);
        console.log(`      When: ${mode.when}`);
        if (mode.stageModes) {
          console.log('      Stage types:');
          for (const [sm, desc] of Object.entries(mode.stageModes)) {
            console.log(`        • ${sm}: ${desc}`);
          }
        }
        if (mode.builtInPerspectives) {
          console.log(`      Perspectives: ${mode.builtInPerspectives.join(', ')}`);
        }
      }
      console.log('');
      break;
    }

    case 'chain': {
      const fs = require('fs');
      let chainDef;
      
      if (args[1] === '--stdin') {
        // Read from stdin
        const chunks = [];
        for await (const chunk of process.stdin) chunks.push(chunk);
        chainDef = JSON.parse(Buffer.concat(chunks).toString());
      } else if (args[1]) {
        // Read from file
        const filePath = require('path').resolve(args[1]);
        chainDef = JSON.parse(fs.readFileSync(filePath, 'utf8'));
      } else {
        console.error('Usage: swarm chain <json-file> | swarm chain --stdin');
        process.exit(1);
      }

      console.log(`🐝 Running chain: ${chainDef.name || 'unnamed'}`);
      console.log(`   Stages: ${chainDef.stages?.length || 0}`);
      for (const stage of chainDef.stages || []) {
        console.log(`   → ${stage.name || '?'} (${stage.mode || 'single'}) [${stage.perspective || stage.perspectives?.join(', ') || 'default'}]`);
      }
      console.log('');

      const resp = await fetch('http://localhost:9999/chain', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(chainDef),
      });

      const reader = resp.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        
        const lines = buffer.split('\n');
        buffer = lines.pop();
        
        for (const line of lines) {
          if (!line.trim()) continue;
          try {
            const event = JSON.parse(line);
            switch (event.event) {
              case 'start':
                console.log(`⚡ ${event.message}`);
                break;
              case 'phase_start':
                console.log(`\n📍 Stage: ${event.name} (${event.taskCount} tasks)`);
                break;
              case 'phase_complete':
                console.log(`   ✅ ${event.name} — ${event.durationMs}ms`);
                break;
              case 'task':
                process.stdout.write('.');
                break;
              case 'complete':
                console.log('\n');
                console.log(`✅ Chain complete in ${event.duration}ms`);
                console.log(`   Tasks: ${event.stats.totalTasks} (${event.stats.successful} ok, ${event.stats.failed} failed)`);
                if (event.cost?.session) {
                  console.log(`   Cost:  $${event.cost.session.swarmCost} (Opus eq: $${event.cost.session.opusEquivalent}, ${event.cost.session.savingsMultiplier} cheaper)`);
                }
                console.log('');
                console.log('─'.repeat(50));
                console.log('FINAL OUTPUT:');
                console.log('─'.repeat(50));
                if (typeof event.output === 'string') {
                  console.log(event.output);
                } else {
                  console.log(JSON.stringify(event.output, null, 2));
                }
                console.log('');
                // Stage breakdown
                console.log('Stage breakdown:');
                for (const stage of event.stages) {
                  console.log(`   ${stage.success ? '✅' : '❌'} ${stage.stage} (${stage.mode}) — ${stage.durationMs}ms — ${stage.results.length} results`);
                }
                break;
              case 'error':
                console.error(`❌ Error: ${event.error || JSON.stringify(event.errors)}`);
                break;
            }
          } catch (e) {
            // Partial JSON, wait for more data
          }
        }
      }
      break;
    }

    default:
      console.error(`Unknown command: ${command}`);
      console.error('Run "swarm help" for usage');
      process.exit(1);
  }
}

main().catch(err => {
  console.error('Error:', err.message);
  process.exit(1);
});
