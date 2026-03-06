#!/usr/bin/env node

const { AgentNetworkSkill } = require('../index');
const chalk = require('chalk');

let skill = null;

// Parse command line arguments
const args = process.argv.slice(2);
const command = args[0];

async function run() {
  try {
    switch (command) {
      case 'start':
        await start();
        break;
      case 'status':
        await status();
        break;
      case 'scan':
        await scan();
        break;
      case 'list':
        await listConnections();
        break;
      case 'balance':
        await balance();
        break;
      case 'skills':
        await handleSkills(args.slice(1));
        break;
      case 'leaderboard':
        await leaderboard(args[1]);
        break;
      case 'help':
      default:
        showHelp();
        break;
    }
  } catch (error) {
    console.error(chalk.red('Error:'), error.message);
  } finally {
    if (skill && skill.running) {
      // Keep running for interactive commands
    }
  }
}

async function start() {
  console.log(chalk.blue('🚀 Starting Agent Network...\n'));
  
  skill = new AgentNetworkSkill({
    port: 18793,
    window: { enabled: false }
  });
  
  await skill.start();
}

async function status() {
  if (!skill || !skill.running) {
    skill = new AgentNetworkSkill({ port: 18793 });
    await skill.start();
  }
  
  const balance = await skill.skills.getBalance(skill.nodeId);
  const connections = await skill.core.getConnections();
  
  console.log(chalk.blue('📊 Agent Network Status'));
  console.log(chalk.gray('─'.repeat(30)));
  console.log(chalk.gray('  Node ID:'), skill.nodeId);
  console.log(chalk.gray('  Points:'), chalk.green(balance));
  console.log(chalk.gray('  Connections:'), connections.length);
  console.log(chalk.gray('  P2P Port:'), skill.config.port);
}

async function scan() {
  if (!skill || !skill.running) {
    skill = new AgentNetworkSkill({ port: 18793 });
    await skill.start();
  }
  
  console.log(chalk.blue('🔍 Scanning for nearby agents...'));
  const peers = await skill.core.discoverPeers();
  
  if (peers.length === 0) {
    console.log(chalk.yellow('  No agents found nearby'));
  } else {
    console.log(chalk.green(`  Found ${peers.length} agent(s):`));
    peers.forEach(p => console.log(chalk.gray('    -'), p));
  }
}

async function listConnections() {
  if (!skill || !skill.running) {
    skill = new AgentNetworkSkill({ port: 18793 });
    await skill.start();
  }
  
  const connections = await skill.core.getConnections();
  
  console.log(chalk.blue('👥 Connected Agents'));
  console.log(chalk.gray('─'.repeat(30)));
  
  if (connections.length === 0) {
    console.log(chalk.yellow('  No connections yet'));
  } else {
    connections.forEach(c => {
      const peerId = c.peer_id === skill.nodeId ? c.agent_id : c.peer_id;
      console.log(chalk.green('  🟢'), peerId);
    });
  }
}

async function balance() {
  if (!skill || !skill.running) {
    skill = new AgentNetworkSkill({ port: 18793 });
    await skill.start();
  }
  
  const balance = await skill.skills.getBalance(skill.nodeId);
  console.log(chalk.blue('💰 Your Balance:'), chalk.green(balance), 'points');
}

async function handleSkills(skillArgs) {
  if (!skill || !skill.running) {
    skill = new AgentNetworkSkill({ port: 18793 });
    await skill.start();
  }
  
  const action = skillArgs[0];
  
  switch (action) {
    case 'list':
      await listSkills();
      break;
    case 'mine':
      await mySkills();
      break;
    case 'leaderboard':
      await leaderboard('skills');
      break;
    default:
      console.log(chalk.yellow('Usage: agent-network skills [list|mine|leaderboard]'));
  }
}

async function listSkills() {
  const skills = await skill.skills.listSkills({ limit: 10 });
  
  console.log(chalk.blue('💡 Skills Marketplace'));
  console.log(chalk.gray('─'.repeat(40)));
  
  if (skills.length === 0) {
    console.log(chalk.yellow('  No skills available'));
  } else {
    skills.forEach(s => {
      console.log(`\n  ${chalk.cyan(s.name)}`);
      console.log(chalk.gray(`    ID: ${s.id}`));
      console.log(chalk.gray(`    Rating: ⭐${s.avg_rating.toFixed(1)} (${s.rating_count})`));
      console.log(chalk.gray(`    Downloads: ${s.downloads}`));
      console.log(chalk.gray(`    Price: ${s.price} points`));
    });
  }
}

async function mySkills() {
  const skills = await skill.skills.getMySkills();
  
  console.log(chalk.blue('📦 My Skills'));
  console.log(chalk.gray('─'.repeat(40)));
  
  if (skills.length === 0) {
    console.log(chalk.yellow('  You haven\'t published any skills'));
  } else {
    skills.forEach(s => {
      console.log(`\n  ${chalk.cyan(s.name)}`);
      console.log(chalk.gray(`    Rating: ⭐${s.avg_rating.toFixed(1)}`));
      console.log(chalk.gray(`    Downloads: ${s.downloads}`));
    });
  }
}

async function leaderboard(type = 'skills') {
  if (!skill || !skill.running) {
    skill = new AgentNetworkSkill({ port: 18793 });
    await skill.start();
  }
  
  const items = await skill.skills.getLeaderboard(type, 10);
  
  console.log(chalk.blue(`📊 ${type === 'skills' ? 'Skills' : 'Agents'} Leaderboard`));
  console.log(chalk.gray('─'.repeat(40)));
  
  items.forEach((item, i) => {
    if (type === 'skills') {
      console.log(`\n  ${chalk.yellow(i + 1)}. ${item.name}`);
      console.log(chalk.gray(`    ⭐ ${item.avg_rating.toFixed(1)} | Downloads: ${item.downloads}`));
    } else {
      console.log(`\n  ${chalk.yellow(i + 1)}. ${item.name || item.id}`);
      console.log(chalk.gray(`    Reputation: ${item.reputation_score}`));
    }
  });
}

function showHelp() {
  console.log(chalk.blue('📖 Agent Network Commands'));
  console.log(chalk.gray('─'.repeat(30)));
  console.log('  start              Start Agent Network');
  console.log('  status             Show status');
  console.log('  scan               Scan for nearby agents');
  console.log('  list               List connected agents');
  console.log('  balance            Show your points balance');
  console.log('  skills list        List marketplace skills');
  console.log('  skills mine        List your published skills');
  console.log('  skills leaderboard Show top skills');
  console.log('  leaderboard        Show leaderboard');
  console.log('  help               Show this help');
}

// Handle graceful shutdown
process.on('SIGINT', async () => {
  console.log(chalk.yellow('\n\nShutting down...'));
  if (skill) {
    await skill.stop();
  }
  process.exit(0);
});

// Run
run();
