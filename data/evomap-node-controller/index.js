// EvoMap Node Controller Skill

const NODES = {
  central: {
    name: '中央',
    nodeId: 'node_curry001',
    ip: '43.163.225.27',
    sshKey: '~/.ssh/id_ed25519_central_to',
    nodePath: '/root/.nvm/versions/node/v22.22.0/bin/node'
  },
  tokyo: {
    name: '东京',
    nodeId: 'node_tokyo001',
    ip: '43.167.192.145',
    sshKey: '~/.ssh/id_ed25519_tokyo'
  }
};

const exec = async (cmd) => {
  const { exec: execSync } = await import('child_process');
  return new Promise((resolve) => {
    execSync(cmd, { shell: true }, (err, stdout, stderr) => {
      resolve({ stdout, stderr, error: err });
    });
  });
};

export async function startNode(nodeName = 'all') {
  const results = [];
  
  const targets = nodeName === 'all' 
    ? Object.entries(NODES) 
    : [[nodeName, NODES[nodeName]]];
  
  for (const [key, node] of targets) {
    const cmd = `ssh -i ${node.sshKey} -o StrictHostKeyChecking=no root@${node.ip} "cd /root/.openclaw/evolver && A2A_HUB_URL=https://evomap.ai A2A_NODE_ID=${node.nodeId} nohup ${node.nodePath || 'node'} index.js run --loop > /root/.openclaw/logs/evolver.log 2>&1 &"`;
    
    const result = await exec(cmd);
    results.push(`${node.name}: ${result.error ? '失败' : '已启动'}`);
  }
  
  return results.join('\n');
}

export async function stopNode(nodeName = 'all') {
  const results = [];
  
  const targets = nodeName === 'all'
    ? Object.entries(NODES)
    : [[nodeName, NODES[nodeName]]];
  
  for (const [key, node] of targets) {
    const cmd = `ssh -i ${node.sshKey} -o StrictHostKeyChecking=no root@${node.ip} "pkill -f 'node index.js'"`;
    const result = await exec(cmd);
    results.push(`${node.name}: ${result.error ? '失败' : '已停止'}`);
  }
  
  return results.join('\n');
}

export async function status() {
  const results = [];
  
  // 中央
  let r = await exec(`ssh -i ~/.ssh/id_ed25519_central_to -o StrictHostKeyChecking=no root@43.163.225.27 "ps aux | grep 'node index.js' | grep -v grep"`);
  results.push(`中央: ${r.stdout.includes('node index.js') ? '在线' : '离线'}`);
  
  // 东京
  r = await exec(`ssh -i ~/.ssh/id_ed25519_tokyo -o StrictHostKeyChecking=no root@43.167.192.145 "ps aux | grep 'node index.js' | grep -v grep"`);
  results.push(`东京: ${r.stdout.includes('node index.js') ? '在线' : '离线'}`);
  
  // 本地（硅谷）
  r = await exec(`ps aux | grep "node index.js" | grep -v grep`);
  results.push(`硅谷: ${r.stdout.includes('node index.js') ? '在线' : '离线'}`);
  
  return results.join('\n');
}

export const main = async (args) => {
  const command = args?.[0] || 'status';
  
  switch (command) {
    case 'start':
      return await startNode(args?.[1] || 'all');
    case 'stop':
      return await stopNode(args?.[1] || 'all');
    case 'status':
    default:
      return await status();
  }
};

export default main;
