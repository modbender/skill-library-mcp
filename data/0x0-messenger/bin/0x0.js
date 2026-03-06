#!/usr/bin/env node
import { program } from 'commander'
import { cmdInit } from '../src/commands/init.js'
import { cmdWhoami } from '../src/commands/whoami.js'
import { cmdRenew } from '../src/commands/renew.js'
import {
  cmdPinNew, cmdPinList, cmdPinRotate, cmdPinRevoke, cmdPinInfo
} from '../src/commands/pin.js'
import { cmdSend } from '../src/commands/send.js'
import { cmdInbox } from '../src/commands/inbox.js'
import { cmdRead } from '../src/commands/read.js'
import { cmdChat } from '../src/commands/chat.js'
import { cmdWeb } from '../src/commands/web.js'
import { cmdListen } from '../src/commands/listen.js'
import { cmdPipe } from '../src/commands/pipe.js'
import {
  cmdContactAdd, cmdContactList, cmdContactLabel, cmdContactRemove
} from '../src/commands/contact.js'
import { cmdQr } from '../src/commands/qr.js'
import { cmdRequests } from '../src/commands/requests.js'
import { cmdApprove } from '../src/commands/approve.js'
import { cmdQueue } from '../src/commands/queue.js'

program
  .name('0x0')
  .description('P2P disposable number messenger')
  .version('1.0.0')

program
  .command('init')
  .description('initialize 0x0 and generate your number')
  .action(cmdInit)

program
  .command('whoami')
  .description('show your number and active pins')
  .action(cmdWhoami)

program
  .command('renew')
  .description('renew your number (resets all PINs)')
  .action(cmdRenew)

// pin subcommands
const pin = program.command('pin').description('manage PINs')

pin
  .command('new')
  .description('create a new PIN')
  .option('-l, --label <label>', 'label for this PIN')
  .option('-e, --expires <duration>', 'expiry duration (e.g. 24h, 7d, 1w)')
  .option('--once', 'expire after receiving one message')
  .option('--public', 'public PIN for requests (SNS / business card)')
  .action((opts) => cmdPinNew({ ...opts, lobby: !!opts.public }))

pin
  .command('list')
  .description('list all active PINs')
  .action(cmdPinList)

pin
  .command('rotate <pin>')
  .description('rotate a PIN (generates new value)')
  .action(cmdPinRotate)

pin
  .command('revoke <pin>')
  .description('revoke a PIN immediately')
  .action(cmdPinRevoke)

pin
  .command('info <pin>')
  .description('show PIN details')
  .action(cmdPinInfo)

program
  .command('chat <number> <pin>')
  .description('start interactive P2P chat')
  .action(cmdChat)

program
  .command('send <number> <pin> <message>')
  .description('send a single message and exit')
  .action(cmdSend)

program
  .command('inbox')
  .description('show inbox (all pins)')
  .option('--json', 'output as JSON')
  .action((opts) => cmdInbox(opts))

program
  .command('read <pin>')
  .description('read messages for a specific PIN')
  .option('--json', 'output as JSON')
  .action((p, opts) => cmdRead(p, opts))

program
  .command('listen')
  .description('listen for incoming messages (daemon mode)')
  .option('-p, --pin <pin>', 'listen on a specific PIN only')
  .action((opts) => cmdListen(opts))

program
  .command('pipe <number> <pin>')
  .description('stdio mode for agents (JSON stream)')
  .action(cmdPipe)

program
  .command('web')
  .description('start browser UI (localhost)')
  .option('-p, --port <port>', 'port number', '3000')
  .option('--no-open', 'do not open browser automatically')
  .option('--lan', 'expose to local network (mobile access)')
  .action((opts) => cmdWeb({ port: parseInt(opts.port), noOpen: !opts.open, lan: !!opts.lan }))

// contact subcommands
const contact = program.command('contact').description('manage contacts')

contact
  .command('add <uri-or-number> [pin]')
  .description('add a contact (URI or number+pin)')
  .option('-l, --label <label>', 'label for this contact')
  .action((uriOrNumber, pin, opts) => cmdContactAdd(uriOrNumber, pin, opts))

contact
  .command('list')
  .description('list all contacts')
  .action(cmdContactList)

contact
  .command('label <id> <label>')
  .description('update contact label')
  .action(cmdContactLabel)

contact
  .command('remove <id>')
  .description('remove a contact')
  .action(cmdContactRemove)

program
  .command('qr <pin>')
  .description('show QR code for a PIN (share to let others connect)')
  .action(cmdQr)

program
  .command('requests')
  .description('show pending requests from your public PINs')
  .action(cmdRequests)

program
  .command('approve <shortKey> <message>')
  .description('approve a request by replying (creates a dedicated PIN automatically)')
  .action(cmdApprove)

program
  .command('queue')
  .description('show pending offline messages (TTL: 72h)')
  .action(cmdQueue)

program.parse()
