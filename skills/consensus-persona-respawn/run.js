import fs from 'node:fs'; import path from 'node:path'; import { handler } from './src/index.mjs';
const i=process.argv.indexOf('--input'); if(i<0) throw new Error('Usage: run.js --input <file>');
const out=await handler(JSON.parse(fs.readFileSync(process.argv[i+1],'utf8'))); fs.mkdirSync('./out',{recursive:true}); const f=path.resolve(`./out/respawn-${Date.now()}.json`); fs.writeFileSync(f,JSON.stringify(out,null,2)); console.log(JSON.stringify({ok:!out.error,outFile:f,respawn_id:out.respawn_id||null},null,2));
