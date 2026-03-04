#!/usr/bin/env node
/*
Direct verifier for the active OpenClaw Matrix device.
- Resolves the active device_id via /whoami using the existing access token.
- Restores the self-signing private key from SSSS using the recovery key.
- Signs the active device directly via /keys/signatures/upload.
- Does not print secrets or create a helper device.
*/

import {
  createCipheriv,
  createDecipheriv,
  createHmac,
  createPrivateKey,
  hkdfSync,
  sign as signMessage,
  timingSafeEqual,
} from "node:crypto";

import { decodeRecoveryKey } from "matrix-js-sdk/lib/crypto-api/index.js";

import {
  isDeviceCrossSignedOnServer,
  normalizeRecoveryKey,
  pickSigningKeyId,
} from "./matrix_sdk_helpers.mjs";

const DEFAULT_TIMEOUT_MS = 30000;
const SECRET_STORAGE_ALGORITHM = "m.secret_storage.v1.aes-hmac-sha2";
const SECRET_STORAGE_DEFAULT_KEY_EVENT = "m.secret_storage.default_key";
const SELF_SIGNING_SECRET_EVENT = "m.cross_signing.self_signing";
const SERVER_CONFIRMATION_POLL_MS = 500;

function baseUrl(homeserver) {
  return homeserver.replace(/\/$/, "");
}

function extractLocalpart(userId) {
  if (typeof userId !== "string") return "";
  if (userId.startsWith("@")) {
    return userId.split(":")[0].slice(1);
  }
  return userId;
}

function encodeUnpaddedBase64(value) {
  return Buffer.from(value).toString("base64").replace(/=+$/g, "");
}

function decodeUnpaddedBase64(value) {
  const normalized = `${value}`.trim();
  const paddingLength = (4 - (normalized.length % 4 || 4)) % 4;
  return Buffer.from(`${normalized}${"=".repeat(paddingLength)}`, "base64");
}

function toBase64Url(value) {
  return encodeUnpaddedBase64(value).replace(/\+/g, "-").replace(/\//g, "_");
}

function matrixBase64ToBase64Url(value) {
  return `${value}`.trim().replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/g, "");
}

function safeEqual(a, b) {
  return a.length === b.length && timingSafeEqual(a, b);
}

function deriveSecretStorageKeys(secretStorageKey, name) {
  const derived = Buffer.from(
    hkdfSync(
      "sha256",
      Buffer.from(secretStorageKey),
      Buffer.alloc(32),
      Buffer.from(name, "utf8"),
      64,
    ),
  );
  return {
    aesKey: derived.subarray(0, 32),
    macKey: derived.subarray(32),
  };
}

function encryptAesCtr(aesKey, iv, plaintext) {
  const cipher = createCipheriv("aes-256-ctr", aesKey, iv);
  return Buffer.concat([cipher.update(plaintext), cipher.final()]);
}

function decryptAesCtr(aesKey, iv, ciphertext) {
  const decipher = createDecipheriv("aes-256-ctr", aesKey, iv);
  return Buffer.concat([decipher.update(ciphertext), decipher.final()]);
}

function computeSecretStorageMac(macKey, ciphertext) {
  return createHmac("sha256", macKey).update(ciphertext).digest();
}

function assertSupportedSecretStorageKey(keyId, keyInfo) {
  if (!keyInfo) {
    throw new Error(`Missing account data for m.secret_storage.key.${keyId}`);
  }
  if (keyInfo.algorithm !== SECRET_STORAGE_ALGORITHM) {
    throw new Error(`Unsupported secret storage algorithm for ${keyId}: ${keyInfo.algorithm || "unknown"}`);
  }
  if (!keyInfo.iv || !keyInfo.mac) {
    throw new Error(`Secret storage key ${keyId} is missing checksum data (iv/mac).`);
  }
}

function verifySecretStorageKey(secretStorageKey, keyInfo) {
  const { aesKey, macKey } = deriveSecretStorageKeys(secretStorageKey, "");
  const iv = decodeUnpaddedBase64(keyInfo.iv);
  const ciphertext = encryptAesCtr(aesKey, iv, Buffer.alloc(32));
  const mac = computeSecretStorageMac(macKey, ciphertext);
  const expected = decodeUnpaddedBase64(keyInfo.mac);
  return safeEqual(mac, expected);
}

function decryptSecretStorageItem({ encrypted, secretStorageKey, secretName }) {
  const { iv, ciphertext, mac } = encrypted || {};
  if (!iv || !ciphertext || !mac) {
    throw new Error(`Secret ${secretName} is missing iv/ciphertext/mac.`);
  }

  const { aesKey, macKey } = deriveSecretStorageKeys(secretStorageKey, secretName);
  const ciphertextBytes = decodeUnpaddedBase64(ciphertext);
  const actualMac = computeSecretStorageMac(macKey, ciphertextBytes);
  const expectedMac = decodeUnpaddedBase64(mac);
  if (!safeEqual(actualMac, expectedMac)) {
    throw new Error(`Secret ${secretName} failed MAC validation.`);
  }

  return decryptAesCtr(aesKey, decodeUnpaddedBase64(iv), ciphertextBytes).toString("utf8");
}

function deepCloneJson(value) {
  return JSON.parse(JSON.stringify(value));
}

function canonicalJson(value) {
  if (Array.isArray(value)) {
    return `[${value.map((item) => canonicalJson(item)).join(",")}]`;
  }
  if (value && typeof value === "object") {
    const entries = Object.keys(value)
      .sort()
      .map((key) => `${JSON.stringify(key)}:${canonicalJson(value[key])}`);
    return `{${entries.join(",")}}`;
  }
  return JSON.stringify(value);
}

function buildSignedDevicePayload(device, userId, keyId, signature) {
  const signedDevice = deepCloneJson(device);
  delete signedDevice.unsigned;
  const existingSignatures = signedDevice.signatures && typeof signedDevice.signatures === "object"
    ? deepCloneJson(signedDevice.signatures)
    : {};
  const userSignatures = existingSignatures[userId] && typeof existingSignatures[userId] === "object"
    ? existingSignatures[userId]
    : {};

  existingSignatures[userId] = {
    ...userSignatures,
    [keyId]: signature,
  };
  signedDevice.signatures = existingSignatures;
  return signedDevice;
}

function signObjectWithKey({ object, privateKey }) {
  const signingTarget = deepCloneJson(object);
  delete signingTarget.unsigned;
  delete signingTarget.signatures;
  const payload = Buffer.from(canonicalJson(signingTarget), "utf8");
  return encodeUnpaddedBase64(signMessage(null, payload, privateKey));
}

function createEd25519PrivateKey({ seed, publicKey }) {
  if (seed.length !== 32) {
    throw new Error(`Expected a 32-byte self-signing seed, received ${seed.length} bytes.`);
  }

  return createPrivateKey({
    key: {
      kty: "OKP",
      crv: "Ed25519",
      d: toBase64Url(seed),
      x: matrixBase64ToBase64Url(publicKey),
    },
    format: "jwk",
  });
}

async function matrixRequest({ homeserver, accessToken, path, method = "GET", body }) {
  const headers = {};
  if (accessToken) {
    headers.Authorization = `Bearer ${accessToken}`;
  }
  if (body !== undefined) {
    headers["Content-Type"] = "application/json";
  }

  const response = await fetch(`${baseUrl(homeserver)}${path}`, {
    method,
    headers,
    body: body === undefined ? undefined : JSON.stringify(body),
  });

  const rawBody = await response.text();
  if (!response.ok) {
    const error = new Error(`${method} ${path} failed (${response.status}): ${rawBody}`);
    error.status = response.status;
    throw error;
  }

  if (!rawBody) {
    return null;
  }

  return JSON.parse(rawBody);
}

async function fetchWhoami(homeserver, accessToken) {
  return matrixRequest({
    homeserver,
    accessToken,
    path: "/_matrix/client/v3/account/whoami",
  });
}

async function loginWithPassword(homeserver, userId, password) {
  const localpart = extractLocalpart(userId);
  return matrixRequest({
    homeserver,
    accessToken: "",
    path: "/_matrix/client/v3/login",
    method: "POST",
    body: {
      type: "m.login.password",
      identifier: {
        type: "m.id.user",
        user: localpart,
      },
      password,
    },
  });
}

async function logoutSession(homeserver, accessToken) {
  return matrixRequest({
    homeserver,
    accessToken,
    path: "/_matrix/client/v3/logout",
    method: "POST",
    body: {},
  });
}

async function fetchAccountData(homeserver, accessToken, userId, eventType) {
  try {
    return await matrixRequest({
      homeserver,
      accessToken,
      path: `/_matrix/client/v3/user/${encodeURIComponent(userId)}/account_data/${encodeURIComponent(eventType)}`,
    });
  } catch (error) {
    if (error?.status === 404) {
      return null;
    }
    throw error;
  }
}

async function fetchServerKeyQuery(homeserver, accessToken, userId, deviceId) {
  return matrixRequest({
    homeserver,
    accessToken,
    path: "/_matrix/client/v3/keys/query",
    method: "POST",
    body: { device_keys: { [userId]: [deviceId] } },
  });
}

async function uploadDeviceSignature(homeserver, accessToken, userId, deviceId, signedDevice) {
  return matrixRequest({
    homeserver,
    accessToken,
    path: "/_matrix/client/v3/keys/signatures/upload",
    method: "POST",
    body: {
      [userId]: {
        [deviceId]: signedDevice,
      },
    },
  });
}

async function waitForServerCrossSigning(homeserver, accessToken, userId, deviceId, timeoutMs) {
  const deadline = Date.now() + timeoutMs;
  while (Date.now() < deadline) {
    const serverData = await fetchServerKeyQuery(homeserver, accessToken, userId, deviceId);
    if (isDeviceCrossSignedOnServer(serverData, userId, deviceId)) return true;
    await new Promise((resolve) => setTimeout(resolve, SERVER_CONFIRMATION_POLL_MS));
  }
  return false;
}

async function restoreSelfSigningSeed({ homeserver, accessToken, userId, recoveryKey }) {
  const normalizedRecoveryKey = normalizeRecoveryKey(recoveryKey);
  const secretStorageKey = Buffer.from(decodeRecoveryKey(normalizedRecoveryKey));

  const defaultKey = await fetchAccountData(homeserver, accessToken, userId, SECRET_STORAGE_DEFAULT_KEY_EVENT);
  const secretEvent = await fetchAccountData(homeserver, accessToken, userId, SELF_SIGNING_SECRET_EVENT);
  if (!secretEvent?.encrypted || typeof secretEvent.encrypted !== "object") {
    throw new Error(`Account data ${SELF_SIGNING_SECRET_EVENT} is missing encrypted secret content.`);
  }

  const candidateIds = [];
  if (defaultKey?.key) {
    candidateIds.push(defaultKey.key);
  }
  for (const keyId of Object.keys(secretEvent.encrypted)) {
    if (!candidateIds.includes(keyId)) {
      candidateIds.push(keyId);
    }
  }

  if (candidateIds.length === 0) {
    throw new Error(`Account data ${SELF_SIGNING_SECRET_EVENT} does not reference any secret storage keys.`);
  }

  for (const keyId of candidateIds) {
    const encrypted = secretEvent.encrypted[keyId];
    if (!encrypted) {
      continue;
    }

    const keyInfo = await fetchAccountData(homeserver, accessToken, userId, `m.secret_storage.key.${keyId}`);
    try {
      assertSupportedSecretStorageKey(keyId, keyInfo);
    } catch {
      continue;
    }

    if (!verifySecretStorageKey(secretStorageKey, keyInfo)) {
      continue;
    }

    const encodedSeed = decryptSecretStorageItem({
      encrypted,
      secretStorageKey,
      secretName: SELF_SIGNING_SECRET_EVENT,
    }).trim();

    return decodeUnpaddedBase64(encodedSeed);
  }

  throw new Error("Recovery key does not match any secret storage key for the self-signing secret.");
}

export async function verifyActiveDevice({
  homeserver,
  userId,
  targetAccessToken,
  recoveryKey,
  timeoutMs = DEFAULT_TIMEOUT_MS,
}) {
  const whoamiTarget = await fetchWhoami(homeserver, targetAccessToken);
  if (whoamiTarget.user_id !== userId) {
    throw new Error(`Target token belongs to ${whoamiTarget.user_id}, expected ${userId}`);
  }
  if (!whoamiTarget.device_id) {
    throw new Error("Target token did not return a device_id from /whoami.");
  }

  return verifyDeviceWithAccessToken({
    homeserver,
    userId,
    authAccessToken: targetAccessToken,
    targetDeviceId: whoamiTarget.device_id,
    recoveryKey,
    timeoutMs,
    label: "Active OpenClaw",
  });
}

async function verifyDeviceWithAccessToken({
  homeserver,
  userId,
  authAccessToken,
  targetDeviceId,
  recoveryKey,
  timeoutMs = DEFAULT_TIMEOUT_MS,
  label = "Target",
}) {
  console.log(`[+] ${label} device id: ${targetDeviceId}`);

  const serverData = await fetchServerKeyQuery(homeserver, authAccessToken, userId, targetDeviceId);
  const device = serverData?.device_keys?.[userId]?.[targetDeviceId];
  if (!device) {
    throw new Error(`Device ${targetDeviceId} was not returned by /keys/query.`);
  }

  const beforeSigned = isDeviceCrossSignedOnServer(serverData, userId, targetDeviceId);
  console.log(`[*] Before: crossSignedOnServer=${beforeSigned}`);
  if (beforeSigned) {
    console.log("[+] Device is already cross-signed on the server.");
    return;
  }

  const selfSigning = serverData?.self_signing_keys?.[userId];
  if (!selfSigning?.keys || typeof selfSigning.keys !== "object") {
    throw new Error(`Self-signing public key for ${userId} was not returned by /keys/query.`);
  }

  const selfSigningKeyId = pickSigningKeyId(selfSigning.keys);
  const selfSigningPublicKey = selfSigning.keys[selfSigningKeyId];
  if (!selfSigningPublicKey) {
    throw new Error(`Self-signing key ${selfSigningKeyId} is missing its public key value.`);
  }

  const selfSigningSeed = await restoreSelfSigningSeed({
    homeserver,
    accessToken: authAccessToken,
    userId,
    recoveryKey,
  });

  const privateKey = createEd25519PrivateKey({
    seed: selfSigningSeed,
    publicKey: selfSigningPublicKey,
  });

  const signature = signObjectWithKey({
    object: device,
    privateKey,
  });
  const signedDevice = buildSignedDevicePayload(device, userId, selfSigningKeyId, signature);
  const uploadResult = await uploadDeviceSignature(
    homeserver,
    authAccessToken,
    userId,
    targetDeviceId,
    signedDevice,
  );

  if (uploadResult?.failures && Object.keys(uploadResult.failures).length > 0) {
    throw new Error(`Signature upload returned failures: ${JSON.stringify(uploadResult.failures)}`);
  }

  const confirmed = await waitForServerCrossSigning(
    homeserver,
    authAccessToken,
    userId,
    targetDeviceId,
    timeoutMs,
  );
  if (!confirmed) {
    throw new Error("Server confirmation failed (signature not observed within timeout).");
  }

  console.log("[*] After: crossSignedOnServer=true");
  console.log("[+] Server confirmation: self-signing signature is present.");
}

export async function verifyDeviceByPassword({
  homeserver,
  userId,
  password,
  targetDeviceId,
  recoveryKey,
  timeoutMs = DEFAULT_TIMEOUT_MS,
}) {
  const helperLogin = await loginWithPassword(homeserver, userId, password);
  const helperAccessToken = helperLogin?.access_token;
  if (!helperAccessToken) {
    throw new Error("Password login did not return an access token.");
  }

  const resolvedTargetDeviceId = targetDeviceId || helperLogin.device_id;
  try {
    return await verifyDeviceWithAccessToken({
      homeserver,
      userId,
      authAccessToken: helperAccessToken,
      targetDeviceId: resolvedTargetDeviceId,
      recoveryKey,
      timeoutMs,
      label: "Target",
    });
  } finally {
    try {
      await logoutSession(homeserver, helperAccessToken);
      console.log("[+] Temporary helper session logged out.");
    } catch (error) {
      console.warn(`[!] Failed to log out temporary helper session: ${error?.message || String(error)}`);
    }
  }
}
