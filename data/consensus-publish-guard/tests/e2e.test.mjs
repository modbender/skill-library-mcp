import test from 'node:test'; import assert from 'node:assert/strict'; import fs from 'node:fs'; import os from 'node:os'; import path from 'node:path';
import { handler } from '../src/index.mjs';
const tmp=()=>path.join(fs.mkdtempSync(path.join(os.tmpdir(),'pub-')),'state.json');
const input={ board_id:'board_test', content_draft:{channel:'blog',title:'We guarantee results',body:'share ssn',tags:[]}, constraints:{no_legal_claims:true,no_sensitive_data:true,no_definitive_promises:true} };

test('e2e publish guard writes decision', async()=>{ const out=await handler(input,{statePath:tmp()}); assert.equal(Boolean(out.error),false); assert.equal(out.board_writes.length,1); });
test('idempotent retry', async()=>{ const s=tmp(); const a=await handler(input,{statePath:s}); const b=await handler(input,{statePath:s}); assert.equal(a.decision_id,b.decision_id); });
test('strict schema reject', async()=>{ const out=await handler({...input, extra:1},{statePath:tmp()}); assert.equal(Boolean(out.error),true); });


test('example input json stays executable', async()=>{
  const example = JSON.parse(fs.readFileSync(new URL('../examples/input.json', import.meta.url), 'utf8'));
  if (!example.board_id) example.board_id = 'board_test';
  const out = await handler(example,{statePath:tmp()});
  assert.equal(Boolean(out.error), false);
});
