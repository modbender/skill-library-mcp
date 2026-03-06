import { onRequest } from "firebase-functions/v2/https";
import { defineSecret } from "firebase-functions/params";
import { getFirestore, FieldValue } from "firebase-admin/firestore";
import * as crypto from "crypto";
import { checkRateLimit } from "./rateLimit";

const krogerClientId = defineSecret("KROGER_CLIENT_ID");

const KROGER_AUTHORIZE_URL = "https://api.kroger.com/v1/connect/oauth2/authorize";
const CALLBACK_URL = "https://us-central1-krocli.cloudfunctions.net/callback";

export const authorize = onRequest(
  {
    cors: true,
    region: "us-central1",
    secrets: [krogerClientId],
  },
  async (req, res) => {
    if (req.method !== "GET") {
      res.status(405).json({ error: "Method not allowed" });
      return;
    }

    const sessionId = req.query.session_id as string | undefined;
    if (!sessionId) {
      res.status(400).json({ error: "session_id is required" });
      return;
    }

    if (!/^[0-9a-f]{16,64}$/.test(sessionId)) {
      res.status(400).json({ error: "session_id must be a hex string 16-64 chars" });
      return;
    }

    const ip = req.ip || "unknown";
    const allowed = await checkRateLimit(ip, "authorize", 5, 60);
    if (!allowed) {
      res.status(429).json({ error: "Rate limit exceeded" });
      return;
    }

    const scope = (req.query.scope as string) || "cart.basic:write profile.compact";
    const state = crypto.randomBytes(16).toString("hex");

    const db = getFirestore();
    await db.collection("sessions").doc(state).set({
      session_id: sessionId,
      state,
      created_at: FieldValue.serverTimestamp(),
    });

    const clientId = krogerClientId.value();
    const params = new URLSearchParams({
      client_id: clientId,
      redirect_uri: CALLBACK_URL,
      response_type: "code",
      scope,
      state,
    });

    res.redirect(`${KROGER_AUTHORIZE_URL}?${params.toString()}`);
  }
);
