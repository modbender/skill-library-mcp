import { createUser, createSigner, Agent } from '@xmtp/agent-sdk';
const KEY = process.argv[2];
const DB = process.argv[3] || '.xmtp-worker-new';
const user = createUser(KEY);
console.log('Registering:', user.account.address);
const agent = await Agent.create(createSigner(user), { env: 'production', dbPath: DB });
await agent.start();
console.log('Registered on XMTP.');
await agent.stop();
