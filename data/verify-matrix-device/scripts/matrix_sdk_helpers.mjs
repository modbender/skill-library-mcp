export function normalizeRecoveryKey(value) {
  return value.replace(/[^A-Za-z0-9]/g, "");
}

export function pickSigningKeyId(keys) {
  const keyIds = Object.keys(keys || {});
  if (keyIds.length === 0) {
    throw new Error("No signing keys found.");
  }
  return keyIds[0];
}

export function isDeviceCrossSignedOnServer(serverData, userId, deviceId) {
  const selfSigning = serverData?.self_signing_keys?.[userId];
  const device = serverData?.device_keys?.[userId]?.[deviceId];
  if (!selfSigning || !device) {
    return false;
  }

  const selfSigningKeyId = pickSigningKeyId(selfSigning.keys);
  const signatures = device.signatures?.[userId] || {};
  return Boolean(signatures[selfSigningKeyId]);
}
