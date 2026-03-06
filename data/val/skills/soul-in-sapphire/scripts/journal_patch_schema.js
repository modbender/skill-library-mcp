#!/usr/bin/env node
import fs from 'fs';
import os from 'os';
import path from 'path';
import { patchDataSource } from './notionctl_bridge.js';

function die(msg){ process.stderr.write(String(msg)+'\n'); process.exit(1); }

function readConfig(){
  const p=path.join(os.homedir(),'.config','soul-in-sapphire','config.json');
  if(!fs.existsSync(p)) die(`Missing config: ${p}`);
  return JSON.parse(fs.readFileSync(p,'utf-8'));
}

async function main(){
  const cfg=readConfig();
  const dsid = cfg?.journal?.data_source_id || cfg.journal_data_source_id;
  if(!dsid) die('Config missing journal_data_source_id. Re-run setup_ltm.js.');

  const moodOpts = ['clear','wired','dull','tense','playful','guarded','tender'].map(name=>({name}));
  const intentOpts = ['build','fix','organize','explore','rest','socialize','reflect'].map(name=>({name}));
  const sourceOpts = ['cron','manual'].map(name=>({name}));

  await patchDataSource(dsid, {
    when: { date: {} },
    body: { rich_text: {} },
    worklog: { rich_text: {} },
    session_summary: { rich_text: {} },
    mood_label: { select: { options: moodOpts } },
    intent: { select: { options: intentOpts } },
    future: { rich_text: {} },
    world_news: { rich_text: {} },
    tags: { multi_select: { options: [] } },
    source: { select: { options: sourceOpts } },
  });

  console.log(JSON.stringify({ok:true, journal_data_source_id: dsid}, null, 2));
}

main().catch(err=>die(err?.stack || err?.message || String(err)));
