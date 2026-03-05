import { ethers } from 'ethers';
import fs from 'node:fs';
import modAbi from '../abi-mod.json' with { type: 'json' };
import notesAbi from '../abi-notes.json' with { type: 'json' };
import {
  MOD_ADDR,
  NOTES_ADDR,
  decryptMpBlob,
  buildIdHexFromRequestId,
  makeBitnotePayload,
  extractIdHexFromBlob,
} from './lib/bitnoteCompat.mjs';

function arg(name, fallback = null) {
  const idx = process.argv.indexOf(`--${name}`);
  if (idx >= 0 && process.argv[idx + 1]) return process.argv[idx + 1];
  return process.env[name.toUpperCase()] ?? fallback;
}

const profileName = arg('profile');
let profile = {};
if (profileName) {
  const p = `./profiles/${profileName}.json`;
  if (fs.existsSync(p)) profile = JSON.parse(fs.readFileSync(p, 'utf8'));
}

const username = arg('username', profile.username);
const passphrase = arg('passphrase', process.env.BITNOTE_PASSPHRASE);
const title = arg('title', 'BitNote note');
const body = arg('body', 'UI-compatible scripted note');
const rpc = arg('rpc', profile.rpc || 'https://api.avax.network/ext/bc/C/rpc');
const requestId = arg('request-id', ethers.keccak256(ethers.toUtf8Bytes(`${title}|${body}`)).slice(2, 18));
const dryRun = (arg('dry-run', '0') === '1');

if (!username || !passphrase) {
  console.error('MISSING_USERNAME_OR_PASSPHRASE');
  process.exit(2);
}

const provider = new ethers.JsonRpcProvider(rpc);
const mod = new ethers.Contract(MOD_ADDR, modAbi, provider);
const notesRO = new ethers.Contract(NOTES_ADDR, notesAbi, provider);

const unameHash = ethers.keccak256(ethers.toUtf8Bytes(username));
const address = await mod.getAddressLink(unameHash);
if (address === ethers.ZeroAddress) {
  console.error('USERNAME_NOT_FOUND');
  process.exit(3);
}

const [encPk, encEcdhPriv, ecdhPub] = await Promise.all([
  mod.getString(address),
  mod.getPrivString(address),
  mod.getPubString(address),
]);

const secpPriv = decryptMpBlob(encPk, passphrase);
const ecdhPrivPkcs8 = decryptMpBlob(encEcdhPriv, passphrase);
const wallet = new ethers.Wallet('0x' + secpPriv.toString('hex'), provider);
if (wallet.address.toLowerCase() !== address.toLowerCase()) {
  console.error('DECRYPTED_KEY_ADDRESS_MISMATCH');
  process.exit(4);
}

const idHex = buildIdHexFromRequestId(requestId);
const existingIdx = Array.from(await notesRO.getUserIndex(address));
if (existingIdx.length) {
  const existingBlobs = await notesRO.getDataAtIndexArray(existingIdx);
  const dup = existingBlobs.find((b) => extractIdHexFromBlob(b.toString()) === idHex);
  if (dup) {
    console.log('IDEMPOTENT_HIT', 'request-id already present');
    console.log('ADDRESS', address);
    console.log('REQUEST_ID', requestId);
    console.log('ID_HEX', idHex);
    process.exit(0);
  }
}

const noteHex = await makeBitnotePayload(title, body, ecdhPub.toString(), ecdhPrivPkcs8, idHex);
const noteIndex = ethers.keccak256(noteHex);

if (dryRun) {
  console.log('DRY_RUN', 1);
  console.log('ADDRESS', address);
  console.log('REQUEST_ID', requestId);
  console.log('ID_HEX', idHex);
  console.log('NOTE_INDEX', noteIndex);
  process.exit(0);
}

const notes = new ethers.Contract(NOTES_ADDR, notesAbi, wallet);
const gas = await notes.setUserBytes.estimateGas(noteIndex, noteHex);
const tx = await notes.setUserBytes(noteIndex, noteHex, { gasLimit: (gas * 12n) / 10n });
const rec = await tx.wait();

const idxAfter = Array.from(await notesRO.getUserIndex(address));
const hasNewIndex = idxAfter.some((x) => x.toLowerCase() === noteIndex.toLowerCase());

console.log('ADDRESS', address);
console.log('REQUEST_ID', requestId);
console.log('ID_HEX', idHex);
console.log('TX_HASH', tx.hash);
console.log('BLOCK', rec.blockNumber);
console.log('NOTE_INDEX', noteIndex);
console.log('INDEX_COUNT_NOW', idxAfter.length);
console.log('READ_AFTER_WRITE_OK', hasNewIndex ? 1 : 0);
