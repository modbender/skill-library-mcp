import { describe, it } from 'node:test';
import assert from 'node:assert';
import { Clawdio } from '../index.js';

/** Wire two nodes together: A's sends go to B's receive and vice versa */
function wire(a: Clawdio, b: Clawdio) {
  a.onSend((peerId, msg) => b.receive(a.publicKey, msg));
  b.onSend((peerId, msg) => a.receive(b.publicKey, msg));
}

describe('Clawdio P2P', () => {
  it('should perform Noise XX handshake and send encrypted messages', async () => {
    const alice = await Clawdio.create({ autoAccept: true });
    const bob = await Clawdio.create({ autoAccept: true });
    wire(alice, bob);

    const aliceId = await bob.connect(alice.publicKey);

    // Fingerprints should match
    const fpBob = bob.getFingerprint(aliceId);
    const fpAlice = alice.getFingerprint(bob.publicKey);
    assert.strictEqual(fpBob, fpAlice, 'Fingerprints should match');
    assert.ok(fpBob.length > 0, 'Fingerprint should not be empty');

    // Safety numbers should match
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

    // Reverse: alice → bob
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
