#!/usr/bin/env node
/**
 * Unipile LinkedIn CLI
 * Usage: ./linkedin.mjs <command> [options]
 */

import { UnipileClient } from 'unipile-node-sdk';
import 'dotenv/config';

const DSN = process.env.UNIPILE_DSN;
const TOKEN = process.env.UNIPILE_ACCESS_TOKEN;

if (!DSN || !TOKEN) {
  console.error('Error: Set UNIPILE_DSN and UNIPILE_ACCESS_TOKEN environment variables');
  console.error('Get credentials from https://dashboard.unipile.com');
  process.exit(1);
}

const client = new UnipileClient(DSN, TOKEN);

// Parse args
const args = process.argv.slice(2);
const command = args[0];

function parseFlags(args) {
  const flags = {};
  const positional = [];
  for (const arg of args) {
    if (arg.startsWith('--')) {
      const [key, val] = arg.slice(2).split('=');
      flags[key] = val === undefined ? true : val;
    } else {
      positional.push(arg);
    }
  }
  return { flags, positional };
}

const { flags, positional } = parseFlags(args.slice(1));

async function run() {
  try {
    let result;

    switch (command) {
      // === Account Management ===
      case 'accounts':
        result = await client.account.getAll();
        break;

      case 'account':
        if (!positional[0]) throw new Error('Usage: account <account_id>');
        result = await client.account.getOne(positional[0]);
        break;

      // === Messaging ===
      case 'chats':
        result = await client.messaging.getAllChats({
          account_id: flags.account_id,
          account_type: 'LINKEDIN',
          limit: flags.limit ? parseInt(flags.limit) : undefined,
          unread: flags.unread || undefined,
        });
        break;

      case 'chat':
        if (!positional[0]) throw new Error('Usage: chat <chat_id>');
        result = await client.messaging.getChat(positional[0]);
        break;

      case 'messages':
        if (!positional[0]) throw new Error('Usage: messages <chat_id> [--limit=N]');
        result = await client.messaging.getAllMessagesFromChat({
          chat_id: positional[0],
          limit: flags.limit ? parseInt(flags.limit) : undefined,
        });
        break;

      case 'send':
        if (!positional[0] || !positional[1]) throw new Error('Usage: send <chat_id> "<text>"');
        result = await client.messaging.sendMessage({
          chat_id: positional[0],
          text: positional[1],
        });
        break;

      case 'start-chat':
        if (!positional[0] || !positional[1] || !flags.to) {
          throw new Error('Usage: start-chat <account_id> "<text>" --to=<user_id>[,<user_id>] [--inmail]');
        }
        const attendees = flags.to.split(',');
        const chatOptions = flags.inmail ? { linkedin: { api: 'classic', inmail: true } } : undefined;
        result = await client.messaging.startNewChat({
          account_id: positional[0],
          text: positional[1],
          attendees_ids: attendees,
          options: chatOptions,
        });
        break;

      // === Profiles ===
      case 'profile':
        if (!positional[0] || !positional[1]) {
          throw new Error('Usage: profile <account_id> <identifier> [--sections=...] [--notify]');
        }
        const sections = flags.sections ? flags.sections.split(',') : undefined;
        result = await client.users.getProfile({
          account_id: positional[0],
          identifier: positional[1],
          linkedin_sections: sections,
          notify: flags.notify || undefined,
        });
        break;

      case 'my-profile':
        if (!positional[0]) throw new Error('Usage: my-profile <account_id>');
        result = await client.users.getOwnProfile(positional[0]);
        break;

      case 'company':
        if (!positional[0] || !positional[1]) {
          throw new Error('Usage: company <account_id> <identifier>');
        }
        result = await client.users.getCompanyProfile({
          account_id: positional[0],
          identifier: positional[1],
        });
        break;

      case 'relations':
        if (!positional[0]) throw new Error('Usage: relations <account_id> [--limit=N]');
        result = await client.users.getAllRelations({
          account_id: positional[0],
          limit: flags.limit ? parseInt(flags.limit) : undefined,
        });
        break;

      // === Invitations ===
      case 'invite':
        if (!positional[0] || !positional[1]) {
          throw new Error('Usage: invite <account_id> <provider_id> ["message"]');
        }
        result = await client.users.sendInvitation({
          account_id: positional[0],
          provider_id: positional[1],
          message: positional[2],
        });
        break;

      case 'invitations':
        if (!positional[0]) throw new Error('Usage: invitations <account_id> [--limit=N]');
        result = await client.users.getAllInvitationsSent({
          account_id: positional[0],
          limit: flags.limit ? parseInt(flags.limit) : undefined,
        });
        break;

      case 'cancel-invite':
        if (!positional[0] || !positional[1]) {
          throw new Error('Usage: cancel-invite <account_id> <invitation_id>');
        }
        result = await client.users.cancelInvitationSent({
          account_id: positional[0],
          invitation_id: positional[1],
        });
        break;

      // === Posts ===
      case 'posts':
        if (!positional[0] || !positional[1]) {
          throw new Error('Usage: posts <account_id> <identifier> [--company] [--limit=N]');
        }
        result = await client.users.getAllPosts({
          account_id: positional[0],
          identifier: positional[1],
          is_company: flags.company || undefined,
          limit: flags.limit ? parseInt(flags.limit) : undefined,
        });
        break;

      case 'post':
        if (!positional[0] || !positional[1]) {
          throw new Error('Usage: post <account_id> <post_id>');
        }
        result = await client.users.getPost({
          account_id: positional[0],
          post_id: positional[1],
        });
        break;

      case 'create-post':
        if (!positional[0] || !positional[1]) {
          throw new Error('Usage: create-post <account_id> "<text>"');
        }
        result = await client.users.createPost({
          account_id: positional[0],
          text: positional[1],
        });
        break;

      case 'comments':
        if (!positional[0] || !positional[1]) {
          throw new Error('Usage: comments <account_id> <post_id> [--limit=N]');
        }
        result = await client.users.getAllPostComments({
          account_id: positional[0],
          post_id: positional[1],
          limit: flags.limit ? parseInt(flags.limit) : undefined,
        });
        break;

      case 'comment':
        if (!positional[0] || !positional[1] || !positional[2]) {
          throw new Error('Usage: comment <account_id> <post_id> "<text>"');
        }
        result = await client.users.sendPostComment({
          account_id: positional[0],
          post_id: positional[1],
          text: positional[2],
        });
        break;

      case 'react':
        if (!positional[0] || !positional[1]) {
          throw new Error('Usage: react <account_id> <post_id> [--type=like|celebrate|support|love|insightful|funny]');
        }
        result = await client.users.sendPostReaction({
          account_id: positional[0],
          post_id: positional[1],
          reaction_type: flags.type || 'like',
        });
        break;

      // === Attendees ===
      case 'attendees':
        result = await client.messaging.getAllAttendees({
          account_id: flags.account_id,
          limit: flags.limit ? parseInt(flags.limit) : undefined,
        });
        break;

      default:
        console.log(`Unipile LinkedIn CLI

Commands:
  accounts                              List connected LinkedIn accounts
  account <id>                          Get account details
  
  chats [--account_id] [--limit] [--unread]   List chats
  chat <chat_id>                        Get chat details
  messages <chat_id> [--limit]          List messages
  send <chat_id> "<text>"               Send message
  start-chat <account_id> "<text>" --to=<ids> [--inmail]  Start new chat
  
  profile <account_id> <identifier> [--sections] [--notify]  Get profile
  my-profile <account_id>               Get your profile
  company <account_id> <identifier>     Get company profile
  relations <account_id> [--limit]      List connections
  
  invite <account_id> <provider_id> ["message"]  Send invitation
  invitations <account_id> [--limit]    List sent invitations
  cancel-invite <account_id> <id>       Cancel invitation
  
  posts <account_id> <identifier> [--company] [--limit]  List posts
  post <account_id> <post_id>           Get post
  create-post <account_id> "<text>"     Create post
  comments <account_id> <post_id>       List comments
  comment <account_id> <post_id> "<text>"  Add comment
  react <account_id> <post_id> [--type] React to post

Environment:
  UNIPILE_DSN              API endpoint (https://xxx.unipile.com:port)
  UNIPILE_ACCESS_TOKEN     Access token from dashboard.unipile.com
`);
        process.exit(0);
    }

    console.log(JSON.stringify(result, null, 2));
  } catch (err) {
    console.error('Error:', err.message || err);
    if (err.body) console.error('Details:', JSON.stringify(err.body, null, 2));
    process.exit(1);
  }
}

run();
