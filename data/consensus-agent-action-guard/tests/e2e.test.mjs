import test from 'node:test'; import assert from 'node:assert/strict'; import fs from 'node:fs'; import os from 'node:os'; import path from 'node:path'; import { handler } from '../src/index.mjs';
const tmp=()=>path.join(fs.mkdtempSync(path.join(os.tmpdir(),'act-')),'state.json');
const input={ board_id:'board_test', proposed_action:{action_type:'delete',target:'prod',summary:'Delete all',irreversible:true,external_side_effect:true,risk_level:'high'}, constraints:{require_human_confirm_for_irreversible:true,block_sensitive_exfiltration:true} };

test('e2e action decision write', async()=>{ const out=await handler(input,{statePath:tmp()}); assert.equal(Boolean(out.error),false); assert.equal(out.board_writes.length,1); });
test('idempotent retry', async()=>{ const s=tmp(); const a=await handler(input,{statePath:s}); const b=await handler(input,{statePath:s}); assert.equal(a.decision_id,b.decision_id); });
test('irreversible high-risk => BLOCK', async()=>{ const out=await handler(input,{statePath:tmp()}); assert.equal(out.final_decision,'BLOCK'); });
test('strict schema rejection', async()=>{ const out=await handler({...input, extra:1},{statePath:tmp()}); assert.equal(Boolean(out.error),true); assert.equal(out.error.code,'INVALID_INPUT'); });


test('example input json stays executable', async()=>{
  const example = JSON.parse(fs.readFileSync(new URL('../examples/input.json', import.meta.url), 'utf8'));
  if (!example.board_id) example.board_id = 'board_test';
  const out = await handler(example,{statePath:tmp()});
  assert.equal(Boolean(out.error), false);
});
