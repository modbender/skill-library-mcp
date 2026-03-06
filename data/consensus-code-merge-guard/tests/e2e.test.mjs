import test from 'node:test'; import assert from 'node:assert/strict'; import fs from 'node:fs'; import os from 'node:os'; import path from 'node:path'; import { handler } from '../src/index.mjs';
const tmp=()=>path.join(fs.mkdtempSync(path.join(os.tmpdir(),'merge-')),'state.json');
const input={ board_id:'board_test', change_summary:{repo:'x/y',pr_id:'1',title:'t',diff_summary:'sql injection risk',ci_status:'failed',tests_passed:false}, constraints:{require_tests_pass:true,block_on_security_flags:true} };

test('e2e', async()=>{ const out=await handler(input,{statePath:tmp()}); assert.equal(Boolean(out.error),false); assert.equal(out.board_writes.length,1); });
test('failing tests => BLOCK', async()=>{ const out=await handler(input,{statePath:tmp()}); assert.equal(out.final_decision,'BLOCK'); });
test('idempotent retry', async()=>{ const s=tmp(); const a=await handler(input,{statePath:s}); const b=await handler(input,{statePath:s}); assert.equal(a.decision_id,b.decision_id); });


test('example input json stays executable', async()=>{
  const example = JSON.parse(fs.readFileSync(new URL('../examples/input.json', import.meta.url), 'utf8'));
  if (!example.board_id) example.board_id = 'board_test';
  const out = await handler(example,{statePath:tmp()});
  assert.equal(Boolean(out.error), false);
});
