const fs = require('fs');
const path = require('path');

const root = path.resolve(__dirname, '..');
function detectDefaultSkillDir() {
  const bundledSkillDir = path.resolve(root, '..');
  const bundledMarkers = [
    path.join(bundledSkillDir, 'SKILL.md'),
    path.join(bundledSkillDir, 'scripts', 'spawn-agent.sh')
  ];
  if (bundledMarkers.every((file) => fs.existsSync(file))) {
    return bundledSkillDir;
  }
  return '/Users/Vint/.openclaw/workspace/skills/team-dev';
}

const teamDevSkillDir = process.env.TEAM_DEV_SKILL_DIR || detectDefaultSkillDir();
const checks = [
  path.join(root, 'apps/api/src/server.js'),
  path.join(root, 'apps/web/src/index.html'),
  path.join(root, 'packages/shared/index.js')
];

for (const file of checks) {
  if (!fs.existsSync(file)) {
    console.error(`Missing required file: ${file}`);
    process.exit(1);
  }
}

const activeTasks = path.join(teamDevSkillDir, 'assets', 'active-tasks.json');
console.log(JSON.stringify({
  ok: true,
  root,
  teamDevSkillDir,
  teamDevActiveTasksExists: fs.existsSync(activeTasks)
}, null, 2));
