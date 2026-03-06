import { describe, it } from 'node:test';
import assert from 'node:assert';
import { Clawdio } from '../index.js';

describe('Clawdio P2P', () => {
  it('should perform Noise XX handshake and send encrypted messages', async () => {
    const alice = await Clawdio.create({ port: 19090 });
    const bob = await Clawdio.create({ port: 19091 });

    // Alice auto-accepts bob via connectionRequest handler
    alice.on('connectionRequest', (req: any) => alice.acceptPeer(req.id));

    const connStr = alice.getConnectionString('127.0.0.1');
    const aliceId = await bob.exchangeKeys(connStr);

    await new Promise(r => setTimeout(r, 200));

    // Fingerprints should match on both sides
    const fpBob = bob.getFingerprint(aliceId);
    const fpAlice = alice.getFingerprint(bob.publicKey);
    assert.strictEqual(fpBob, fpAlice, 'Fingerprints should match');
    assert.ok(fpBob.length > 0, 'Fingerprint should not be empty');

    // Safety numbers should also match
    const snBob = bob.getSafetyNumber(aliceId);
    const snAlice = alice.getSafetyNumber(bob.publicKey);
    assert.strictEqual(snBob, snAlice, 'Safety numbers should match');

    // Send message bob → alice
    const received = new Promise<{ msg: any; from: string }>((resolve) => {
      alice.onMessage((msg, from) => resolve({ msg, from }));
    });
    await bob.send(aliceId, { task: 'ping', status: 'ok' });
    const { msg, from } = await received;
    assert.strictEqual(msg.task, 'ping');
    assert.strictEqual(msg.status, 'ok');
    assert.strictEqual(from, bob.publicKey);

    // Reverse direction alice → bob
    const received2 = new Promise<{ msg: any; from: string }>((resolve) => {
      bob.onMessage((msg, from) => resolve({ msg, from }));
    });
    await alice.send(bob.publicKey, { result: 'pong', status: 'ok' });
    const r2 = await received2;
    assert.strictEqual(r2.msg.result, 'pong');

    await alice.stop();
    await bob.stop();
  });
});
