
import fs from 'node:fs';
import path from 'node:path';

const root = process.cwd();
const policy = JSON.parse(fs.readFileSync(path.join(root,'security-policy.json'),'utf8'));
const pkg = JSON.parse(fs.readFileSync(path.join(root,'package.json'),'utf8'));
const deps = Object.keys(pkg.dependencies || {});
const badDeps = deps.filter(d => policy.forbiddenRuntimeDeps.includes(d));
if (badDeps.length) {
  console.error('Blocked runtime dependencies:', badDeps.join(', '));
  process.exit(1);
}

const skillPath = path.join(root,'SKILL.md');
if (fs.existsSync(skillPath)) {
  const skill = fs.readFileSync(skillPath,'utf8');
  for (const key of policy.requiredSkillMetadata || []) {
    if (!new RegExp(`^${key}:`, 'm').test(skill)) {
      console.error(`SKILL.md missing required metadata key: ${key}`);
      process.exit(1);
    }
  }
}

function walk(dir){
  const out=[];
  for(const name of fs.readdirSync(dir)){
    if(['node_modules','.git','.consensus','dist','build','coverage'].includes(name)) continue;
    const p=path.join(dir,name);
    const st=fs.statSync(p);
    if(st.isDirectory()) out.push(...walk(p));
    else if(/\.(ts|js|mjs|cjs)$/.test(name)) out.push(p);
  }
  return out;
}

const files = walk(root);
const bad=[];
for(const f of files){
  const rel = path.relative(root,f).replace(/\\/g,'/');
  const txt = fs.readFileSync(f,'utf8');
  for(const pat of policy.forbiddenImportPatterns||[]){
    if(txt.includes(pat)){
      const allowed=(policy.allowInFiles||[]).some(prefix=>rel.startsWith(prefix));
      if(!allowed) bad.push(`${rel}: ${pat}`);
    }
  }
}
if (bad.length) {
  console.error(`Forbidden import patterns found:\n${bad.join('\n')}`);
  process.exit(1);
}
console.log('security-policy check passed');
