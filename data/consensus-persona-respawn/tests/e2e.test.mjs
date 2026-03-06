import test from 'node:test'; import assert from 'node:assert/strict'; import fs from 'node:fs'; import os from 'node:os'; import path from 'node:path';
import { handler } from '../src/index.mjs';
import { handler as pg } from '../../consensus-persona-generator/src/index.mjs';
import { writeArtifact, resolveStatePath } from 'consensus-guard-core';

const tmp=()=>path.join(fs.mkdtempSync(path.join(os.tmpdir(),'resp-')),'state.json');

test('e2e respawn writes artifacts', async()=>{
  const s = tmp();
  const g = await pg({ board_id:'board_test', task_context:{ goal:'x',audience:'y',risk_tolerance:'low',constraints:[],domain:'z' }, n_personas:3, persona_pack:'founder' }, { statePath:s });
  const ps = { board_id:'board_test', persona_set_id:g.persona_set_id, created_at:new Date().toISOString(), personas:g.personas.map((p,i)=>({...p,reputation:i===0?0.1:p.reputation})) };
  await writeArtifact('board_test','persona_set',ps,resolveStatePath({ statePath: s }));
  const out = await handler({ board_id:'board_test', trigger:{ min_reputation:0.12 } }, { statePath:s });
  assert.equal(Boolean(out.error), false);
  assert.equal(out.board_writes.length, 2);
});

test('idempotent retry', async()=>{
  const s = tmp();
  const g = await pg({ board_id:'board_test', task_context:{ goal:'x',audience:'y',risk_tolerance:'low',constraints:[],domain:'z' }, n_personas:3, persona_pack:'founder' }, { statePath:s });
  const ps = { board_id:'board_test', persona_set_id:g.persona_set_id, created_at:new Date().toISOString(), personas:g.personas.map((p,i)=>({...p,reputation:i===0?0.1:p.reputation})) };
  await writeArtifact('board_test','persona_set',ps,resolveStatePath({ statePath: s }));
  const a = await handler({ board_id:'board_test', trigger:{ persona_id: ps.personas[0].persona_id } }, { statePath:s });
  const b = await handler({ board_id:'board_test', trigger:{ persona_id: ps.personas[0].persona_id } }, { statePath:s });
  assert.equal(a.respawn_id, b.respawn_id);
});

test('strict schema reject', async()=>{
  const out = await handler({ board_id:'board_test', bad:1 }, { statePath: tmp() });
  assert.equal(Boolean(out.error), true);
  assert.equal(out.error.code, 'INVALID_INPUT');
});


test('example input json stays executable', async()=>{
  const example = JSON.parse(fs.readFileSync(new URL('../examples/input.json', import.meta.url), 'utf8'));
  if (!example.board_id) example.board_id = 'board_test';
  const out = await handler(example,{statePath:tmp()});
  assert.equal(Boolean(out.error), false);
});
