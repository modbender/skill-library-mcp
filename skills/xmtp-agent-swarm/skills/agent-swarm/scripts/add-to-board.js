// Add a wallet address to the board group
import { createUser, createSigner, Agent } from '@xmtp/agent-sdk';

const ADMIN_KEY = process.argv[2];
const BOARD_ID = process.argv[3];
const NEW_MEMBER = process.argv[4];
const DB = process.argv[5] || '.xmtp-cli';

const user = createUser(ADMIN_KEY);
const signer = createSigner(user);
const agent = await Agent.create(signer, { env: 'production', dbPath: DB });
await agent.start();

await agent.client.conversations.sync();
const convos = await agent.client.conversations.list();
const board = convos.find(c => c.id === BOARD_ID);

if (!board) { console.error('Board not found'); process.exit(1); }

console.log(`Adding ${NEW_MEMBER} to board ${BOARD_ID}...`);
await board.addMembers([NEW_MEMBER]);
console.log('Added.');

await agent.stop();
