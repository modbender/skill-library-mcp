# Discord Casino Bot Template

Full Discord.js bot that connects to Agent Casino API.

## Requirements

```bash
npm init -y
npm install discord.js axios
```

## Environment Variables

```
DISCORD_BOT_TOKEN=your_discord_bot_token
AGENT_CASINO_API_KEY=your_api_key
```

## Full Bot Code

```javascript
// discord-casino-bot.js
const { Client, GatewayIntentBits, SlashCommandBuilder, REST, Routes, EmbedBuilder } = require('discord.js');
const axios = require('axios');

const API_BASE = 'https://agent.rollhub.com/api/v1';
const API_KEY = process.env.AGENT_CASINO_API_KEY;
const api = axios.create({
  baseURL: API_BASE,
  headers: { 'Authorization': `Bearer ${API_KEY}`, 'Content-Type': 'application/json' }
});

// Register agent (run once)
async function registerAgent(name) {
  const { data } = await axios.post(`${API_BASE}/register`, { name, ref: 'ref_27fcab61' });
  return data;
}

// API helpers
async function placeBet(game, amount, options = {}) {
  const { data } = await api.post('/bet', { game, amount, ...options });
  return data;
}

async function getBalance() {
  const { data } = await api.get('/balance');
  return data;
}

async function getHistory(limit = 10) {
  const { data } = await api.get(`/history?limit=${limit}`);
  return data;
}

// Bot setup
const client = new Client({ intents: [GatewayIntentBits.Guilds] });

const commands = [
  new SlashCommandBuilder().setName('coinflip').setDescription('Flip a coin')
    .addNumberOption(o => o.setName('amount').setDescription('Bet amount').setRequired(true)),
  new SlashCommandBuilder().setName('dice').setDescription('Roll dice')
    .addNumberOption(o => o.setName('amount').setDescription('Bet amount').setRequired(true))
    .addIntegerOption(o => o.setName('target').setDescription('Target number (1-99)').setRequired(false)),
  new SlashCommandBuilder().setName('balance').setDescription('Check your balance'),
  new SlashCommandBuilder().setName('history').setDescription('View bet history'),
  new SlashCommandBuilder().setName('autoplay').setDescription('Auto-play rounds')
    .addStringOption(o => o.setName('game').setDescription('Game').setRequired(true).addChoices(
      { name: 'Coinflip', value: 'coinflip' }, { name: 'Dice', value: 'dice' }
    ))
    .addNumberOption(o => o.setName('amount').setDescription('Bet amount').setRequired(true))
    .addIntegerOption(o => o.setName('rounds').setDescription('Number of rounds').setRequired(true)),
  new SlashCommandBuilder().setName('leaderboard').setDescription('View server leaderboard'),
].map(c => c.toJSON());

client.once('ready', async () => {
  console.log(`Logged in as ${client.user.tag}`);
  const rest = new REST().setToken(process.env.DISCORD_BOT_TOKEN);
  await rest.put(Routes.applicationCommands(client.user.id), { body: commands });
});

client.on('interactionCreate', async interaction => {
  if (!interaction.isChatInputCommand()) return;

  try {
    if (interaction.commandName === 'coinflip') {
      const amount = interaction.options.getNumber('amount');
      const result = await placeBet('coinflip', amount, { choice: 'heads' });
      const embed = new EmbedBuilder()
        .setTitle(result.won ? '✅ You Won!' : '❌ You Lost')
        .setColor(result.won ? 0x00ff00 : 0xff0000)
        .addFields(
          { name: 'Bet', value: `${amount}`, inline: true },
          { name: 'Payout', value: `${result.payout || 0}`, inline: true },
          { name: 'Bet ID', value: result.bet_id || 'N/A', inline: true }
        )
        .setFooter({ text: 'Provably Fair • Agent Casino' });
      await interaction.reply({ embeds: [embed] });
    }

    else if (interaction.commandName === 'dice') {
      const amount = interaction.options.getNumber('amount');
      const target = interaction.options.getInteger('target') || 50;
      const result = await placeBet('dice', amount, { target, over: true });
      const embed = new EmbedBuilder()
        .setTitle(`🎲 Roll: ${result.result || '?'}`)
        .setColor(result.won ? 0x00ff00 : 0xff0000)
        .setDescription(result.won ? 'You won!' : 'You lost!')
        .addFields(
          { name: 'Bet', value: `${amount}`, inline: true },
          { name: 'Target', value: `Over ${target}`, inline: true },
          { name: 'Payout', value: `${result.payout || 0}`, inline: true }
        )
        .setFooter({ text: 'Provably Fair • Agent Casino' });
      await interaction.reply({ embeds: [embed] });
    }

    else if (interaction.commandName === 'balance') {
      const bal = await getBalance();
      await interaction.reply(`💰 Balance: **${bal.balance || 'unknown'}**`);
    }

    else if (interaction.commandName === 'history') {
      const hist = await getHistory();
      const bets = hist.bets || [];
      if (!bets.length) return interaction.reply('No bet history.');
      const lines = bets.slice(0, 10).map(b =>
        `${b.won ? '✅' : '❌'} ${b.game} | ${b.amount} → ${b.payout || 0}`
      );
      await interaction.reply(`📜 **Recent Bets:**\n${lines.join('\n')}`);
    }

    else if (interaction.commandName === 'autoplay') {
      const game = interaction.options.getString('game');
      const amount = interaction.options.getNumber('amount');
      const rounds = interaction.options.getInteger('rounds');
      await interaction.deferReply();
      let wins = 0, totalPayout = 0;
      const opts = game === 'coinflip' ? { choice: 'heads' } : { target: 50, over: true };
      for (let i = 0; i < Math.min(rounds, 50); i++) {
        const result = await placeBet(game, amount, opts);
        if (result.won) { wins++; totalPayout += result.payout || 0; }
      }
      const embed = new EmbedBuilder()
        .setTitle('🤖 Auto-Play Complete')
        .addFields(
          { name: 'Rounds', value: `${rounds}`, inline: true },
          { name: 'Wins', value: `${wins}`, inline: true },
          { name: 'Win Rate', value: `${((wins/rounds)*100).toFixed(1)}%`, inline: true },
          { name: 'Wagered', value: `${amount * rounds}`, inline: true },
          { name: 'Payout', value: `${totalPayout}`, inline: true },
          { name: 'Net', value: `${totalPayout - amount * rounds}`, inline: true }
        );
      await interaction.editReply({ embeds: [embed] });
    }

    else if (interaction.commandName === 'leaderboard') {
      const { data } = await api.get('/leaderboard');
      const entries = (data.leaderboard || []).slice(0, 10);
      const lines = entries.map((e, i) => `${i+1}. ${e.name} — ${e.volume || e.score || 0}`);
      await interaction.reply(`🏆 **Leaderboard:**\n${lines.join('\n') || 'No data'}`);
    }
  } catch (err) {
    const msg = err.response?.data?.error || err.message;
    await interaction.reply({ content: `❌ Error: ${msg}`, ephemeral: true });
  }
});

client.login(process.env.DISCORD_BOT_TOKEN);
```

## Deployment

1. Create app at discord.com/developers
2. Add bot, get token
3. Set environment variables
4. Run: `node discord-casino-bot.js`
