// Try to reuse an existing XMTP database to revoke installations without creating a new one
import { createUser, createSigner, Agent } from '@xmtp/agent-sdk';

const KEY = process.env.WALLET_PRIVATE_KEY;
const DB = process.argv[2] || '.xmtp-db';

const user = createUser(KEY);
const signer = createSigner(user);
console.log('Address:', user.account.address);
console.log('Using existing DB:', DB);

try {
  const agent = await Agent.create(signer, { env: 'production', dbPath: DB });
  await agent.start();
  
  console.log('Connected. Revoking other installations...');
  await agent.client.revokeAllOtherInstallations();
  console.log('Revoked all other installations.');
  
  const state = await agent.client.inboxState(true);
  console.log('Remaining installations:', state.installations?.length);
  
  await agent.stop();
} catch(e) {
  console.error('Error:', e.message);
}
