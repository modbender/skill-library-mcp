import { createUser, createSigner, Agent } from '@xmtp/agent-sdk';

const KEY = process.env.WALLET_PRIVATE_KEY;
const user = createUser(KEY);
const signer = createSigner(user);
console.log('Address:', user.account.address);

const agent = await Agent.create(signer, { env: 'production', dbPath: '/tmp/.xmtp-revoke' });
await agent.start();

const state = await agent.client.inboxState(true);
const installs = state.installations || [];
console.log(`Installations: ${installs.length}`);

if (installs.length > 1) {
  // Keep current installation, revoke the rest
  const currentId = agent.client.installationId;
  console.log('Current:', currentId?.slice(0, 16));
  const toRevoke = installs.filter(i => {
    const id = typeof i.id === 'string' ? i.id : Buffer.from(i.id).toString('hex');
    return id !== currentId;
  }).map(i => typeof i.id === 'string' ? i.id : Buffer.from(i.id).toString('hex'));
  
  console.log(`Revoking ${toRevoke.length} old installations...`);
  // The SDK method might be different - try both
  try {
    await agent.client.revokeInstallations(toRevoke);
    console.log('Done');
  } catch(e) {
    console.log('revokeInstallations failed:', e.message?.slice(0, 100));
    try {
      await agent.client.revokeAllOtherInstallations();
      console.log('Revoked all other installations');
    } catch(e2) {
      console.log('revokeAllOtherInstallations failed:', e2.message?.slice(0, 100));
    }
  }
}

await agent.stop();
