#!/usr/bin/env node
const yargs = require('yargs');
const { hideBin } = require('yargs/helpers');
const { IAMMeter } = require('./iammeter_client');
const fs = require('fs');

function writeCsv(header, rows, out){
  const csv = [header.join(',')].concat(rows.map(r => header.map(h => (r[h]===undefined?'':String(r[h]).replace(/\n/g,' '))).join(','))).join('\n');
  fs.writeFileSync(out, csv);
}

async function run(){
  const argv = yargs(hideBin(process.argv))
    .command('sitelist', 'List sites (places)', () => {}, async (argv) => {
      const c = new IAMMeter();
      const r = await c.sitelist();
      if (argv.json) console.log(JSON.stringify(r, null, 2)); else console.log(r.data.map(s=>({ id:s.id, name:s.name, meters: s.meters ? s.meters.map(m=>m.name) : [] })));
    })
    .command('meters', 'Get latest data for all meters', () => {}, async (argv) => {
      const c = new IAMMeter();
      const r = await c.metersData();
      if (argv.json) console.log(JSON.stringify(r, null, 2)); else console.log(r.data || r);
    })
    .command('meter <sn>', 'Get latest data for a meter', (yargs) => {
      yargs.positional('sn', { type: 'string' });
    }, async (argv) => {
      const c = new IAMMeter();
      const r = await c.meterData(argv.sn);
      if (argv.json) console.log(JSON.stringify(r, null, 2)); else console.log(r.data || r);
    })
    .command('history <placeId> <start> <end>', 'Get energy history for a place and optionally write CSV', (yargs)=>{
      yargs.positional('placeId',{type:'number'})
           .positional('start',{type:'string'})
           .positional('end',{type:'string'})
           .option('out',{type:'string',describe:'Write CSV to file'})
    }, async (argv)=>{
      const c = new IAMMeter();
      const r = await c.energyHistory(argv.placeId, argv.start, argv.end, argv.groupby || 'hour');
      const rows = (r.data || []);
      if (argv.out){
        const header = ['time','yield','fromGrid','toGrid','specialLoad','selfUse'];
        writeCsv(header, rows, argv.out);
        console.log('Wrote', argv.out);
      } else if (argv.json) console.log(JSON.stringify(rows, null, 2)); else console.log(rows);
    })
    .command('poweranalysis <sn> <start> <end>', 'Power analysis', (yargs)=>{
      yargs.positional('sn',{type:'string'}).positional('start',{type:'string'}).positional('end',{type:'string'})
    }, async (argv)=>{
      const c = new IAMMeter();
      const r = await c.powerAnalysis(argv.sn, argv.start, argv.end);
      if (argv.json) console.log(JSON.stringify(r, null, 2)); else console.log(r.data || r);
    })
    .command('offlineanalysis <sn> <start> <end>', 'Offline analysis', (yargs)=>{
      yargs.positional('sn',{type:'string'}).positional('start',{type:'string'}).positional('end',{type:'string'}).option('interval',{type:'number',default:5})
    }, async (argv)=>{
      const c = new IAMMeter();
      const r = await c.offlineAnalysis(argv.sn, argv.start, argv.end, argv.interval);
      if (argv.json) console.log(JSON.stringify(r, null, 2)); else console.log(r.data || r);
    })
    .option('json',{type:'boolean',describe:'Output full JSON'})
    .demandCommand(1)
    .help()
    .argv;
}

run().catch(err=>{ console.error(err && err.stack?err.stack:err); process.exit(1); });
