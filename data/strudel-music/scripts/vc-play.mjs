#!/usr/bin/env node
/**
 * Play an audio file into a Discord Voice Channel.
 * Usage: node scripts/vc-play.mjs <audio-file> [--channel <id>]
 *
 * Uses the same Discord bot token and VC setup as the openclaw-discord-vc bridge.
 * Joins the configured channel, plays the file, then leaves.
 */
import { createReadStream } from 'fs';
import { join } from 'path';
import dotenv from 'dotenv';
import {
  AudioPlayerStatus,
  createAudioPlayer,
  createAudioResource,
  entersState,
  joinVoiceChannel,
  VoiceConnectionStatus,
} from '@discordjs/voice';
import { Client, GatewayIntentBits, ChannelType } from 'discord.js';

// Load env
const vcEnvPath = process.env.OPENCLAW_DISCORD_VC_ENV_FILE
  || join(process.env.HOME, '.config/openclaw/openclaw-discord-vc.env');
dotenv.config({ path: vcEnvPath });

// Also load main openclaw env for bot token
const mainEnvPath = process.env.OPENCLAW_ENV_FILE
  || join(process.env.HOME, '.config/openclaw/openclaw.env');
dotenv.config({ path: mainEnvPath });

const audioFile = process.argv[2];
if (!audioFile) {
  console.error('Usage: node scripts/vc-play.mjs <audio-file> [--channel <id>]');
  process.exit(1);
}

const channelIdx = process.argv.indexOf('--channel');
const channelId = channelIdx >= 0 ? process.argv[channelIdx + 1] : process.env.DISCORD_VC_CHANNEL_ID;
const botToken = process.env.DISCORD_BOT_TOKEN;

if (!botToken) {
  console.error('No DISCORD_BOT_TOKEN found in env');
  process.exit(1);
}
if (!channelId) {
  console.error('No channel ID. Set DISCORD_VC_CHANNEL_ID or use --channel <id>');
  process.exit(1);
}

console.log(`🎵 Playing ${audioFile} in VC ${channelId}`);

const client = new Client({
  intents: [
    GatewayIntentBits.Guilds,
    GatewayIntentBits.GuildVoiceStates,
  ],
});

client.once('ready', async () => {
  console.log(`  Bot ready: ${client.user.tag}`);
  
  try {
    const channel = await client.channels.fetch(channelId);
    if (!channel || channel.type !== ChannelType.GuildVoice) {
      console.error(`Channel ${channelId} is not a voice channel`);
      process.exit(1);
    }

    const connection = joinVoiceChannel({
      channelId: channel.id,
      guildId: channel.guild.id,
      adapterCreator: channel.guild.voiceAdapterCreator,
      selfDeaf: true,  // Music streamer — output only, no listening
    });

    await entersState(connection, VoiceConnectionStatus.Ready, 15_000);
    console.log('  ✅ Joined VC');

    const player = createAudioPlayer();
    connection.subscribe(player);

    const resource = createAudioResource(createReadStream(audioFile));
    player.play(resource);

    console.log('  ▶️  Playing...');
    await entersState(player, AudioPlayerStatus.Playing, 15_000);
    await entersState(player, AudioPlayerStatus.Idle, 300_000); // up to 5 min

    console.log('  ✅ Done playing');
    connection.destroy();
    client.destroy();
    process.exit(0);
  } catch (err) {
    console.error('Error:', err.message);
    client.destroy();
    process.exit(1);
  }
});

client.login(botToken);
