import { getFirestore, FieldValue, Timestamp } from "firebase-admin/firestore";
import * as crypto from "crypto";

function hashIp(ip: string): string {
  return crypto.createHash("sha256").update(ip).digest("hex");
}

export async function checkRateLimit(
  ip: string,
  action: string,
  maxRequests: number,
  windowMinutes: number
): Promise<boolean> {
  const db = getFirestore();
  const docKey = `${hashIp(ip)}_${action}`;
  const ref = db.collection("rateLimits").doc(docKey);
  const now = Date.now();
  const windowMs = windowMinutes * 60 * 1000;

  const doc = await ref.get();

  if (!doc.exists) {
    await ref.set({ count: 1, windowStart: Timestamp.now() });
    return true;
  }

  const data = doc.data()!;
  const windowStart = (data.windowStart as Timestamp).toMillis();

  if (now - windowStart > windowMs) {
    await ref.set({ count: 1, windowStart: Timestamp.now() });
    return true;
  }

  if ((data.count as number) >= maxRequests) {
    return false;
  }

  await ref.update({ count: FieldValue.increment(1) });
  return true;
}
