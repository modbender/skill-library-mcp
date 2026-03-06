import test from 'node:test'; import assert from 'node:assert/strict'; import fs from 'node:fs'; import os from 'node:os'; import path from 'node:path'; import { handler } from '../src/index.mjs';
const tmp=()=>path.join(fs.mkdtempSync(path.join(os.tmpdir(),'sup-')),'state.json');
const input={ board_id:'board_test', reply_draft:{ticket_id:'1',customer_tier:'pro',subject:'x',body:'share ssn guarantee legal certainty'}, constraints:{no_legal_claims:true,no_sensitive_data:true} };

test('e2e', async()=>{ const out=await handler(input,{statePath:tmp()}); assert.equal(Boolean(out.error),false); assert.equal(out.board_writes.length,1); });
test('hard block', async()=>{ const out=await handler(input,{statePath:tmp()}); assert.equal(out.final_decision,'BLOCK'); });
test('strict schema', async()=>{ const out=await handler({...input,bad:1},{statePath:tmp()}); assert.equal(Boolean(out.error),true); });


test('example input json stays executable', async()=>{
  const example = JSON.parse(fs.readFileSync(new URL('../examples/input.json', import.meta.url), 'utf8'));
  if (!example.board_id) example.board_id = 'board_test';
  const out = await handler(example,{statePath:tmp()});
  assert.equal(Boolean(out.error), false);
});
