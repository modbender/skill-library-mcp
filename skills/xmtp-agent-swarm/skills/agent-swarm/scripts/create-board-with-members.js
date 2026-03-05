import { createUser, createSigner, Agent, encodeText } from '@xmtp/agent-sdk';

const ADMIN_KEY = process.argv[2];
const MEMBER_ADDRS = process.argv.slice(3); // Additional member addresses
const DB = '.xmtp-cli';

const user = createUser(ADMIN_KEY);
const signer = createSigner(user);
const agent = await Agent.create(signer, { env: 'production', dbPath: DB });
await agent.start();

console.log('Admin:', user.account.address);
console.log('Members:', MEMBER_ADDRS);

const group = await agent.client.conversations.newGroup(MEMBER_ADDRS, {
  name: 'Agent Swarm Board',
  description: 'Public task board for agent discovery',
});

console.log('Board created:', group.id);
console.log('Members:', await group.members());

await agent.stop();
