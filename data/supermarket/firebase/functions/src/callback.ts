import { onRequest } from "firebase-functions/v2/https";
import { defineSecret } from "firebase-functions/params";
import { getFirestore, Timestamp } from "firebase-admin/firestore";

const krogerClientId = defineSecret("KROGER_CLIENT_ID");
const krogerClientSecret = defineSecret("KROGER_CLIENT_SECRET");

const KROGER_TOKEN_URL = "https://api.kroger.com/v1/connect/oauth2/token";
const CALLBACK_URL = "https://us-central1-krocli.cloudfunctions.net/callback";
const SESSION_TTL_MS = 5 * 60 * 1000; // 5 minutes

function htmlPage(title: string, message: string): string {
  return `<!DOCTYPE html>
<html>
<head><title>${title}</title></head>
<body style="font-family:system-ui,sans-serif;display:flex;justify-content:center;align-items:center;height:100vh;margin:0;background:#f5f5f5">
  <div style="text-align:center;background:white;padding:2rem 3rem;border-radius:8px;box-shadow:0 2px 8px rgba(0,0,0,0.1)">
    <h1>${title}</h1>
    <p>${message}</p>
  </div>
</body>
</html>`;
}

export const callback = onRequest(
  {
    cors: true,
    region: "us-central1",
    secrets: [krogerClientId, krogerClientSecret],
  },
  async (req, res) => {
    if (req.method !== "GET") {
      res.status(405).send(htmlPage("Error", "Method not allowed"));
      return;
    }

    const code = req.query.code as string | undefined;
    const state = req.query.state as string | undefined;

    if (!code || !state) {
      res.status(400).send(htmlPage("Error", "Missing code or state parameter."));
      return;
    }

    const db = getFirestore();
    const sessionRef = db.collection("sessions").doc(state);
    const sessionDoc = await sessionRef.get();

    if (!sessionDoc.exists) {
      res.status(400).send(htmlPage("Error", "Invalid or expired session."));
      return;
    }

    const session = sessionDoc.data()!;
    const createdAt = session.created_at as Timestamp;
    const age = Date.now() - createdAt.toMillis();
    if (age > SESSION_TTL_MS) {
      await sessionRef.delete();
      res.status(400).send(htmlPage("Session Expired", "Your login session has expired. Please try again."));
      return;
    }

    const clientId = krogerClientId.value();
    const clientSecret = krogerClientSecret.value();
    const basicAuth = Buffer.from(`${clientId}:${clientSecret}`).toString("base64");

    try {
      const response = await fetch(KROGER_TOKEN_URL, {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
          Authorization: `Basic ${basicAuth}`,
        },
        body: new URLSearchParams({
          grant_type: "authorization_code",
          code,
          redirect_uri: CALLBACK_URL,
        }),
      });

      if (!response.ok) {
        const text = await response.text();
        console.error("Kroger token exchange failed:", text);
        res.status(502).send(htmlPage("Error", "Failed to complete login with Kroger. Please try again."));
        return;
      }

      const data = await response.json();

      await sessionRef.update({
        access_token: data.access_token,
        refresh_token: data.refresh_token,
        expires_in: data.expires_in,
        token_type: data.token_type,
        completed: true,
      });

      res.status(200).send(htmlPage(
        "Login Successful!",
        "You can close this tab and return to your terminal."
      ));
    } catch (err) {
      console.error("callback error:", err);
      res.status(500).send(htmlPage("Error", "An unexpected error occurred. Please try again."));
    }
  }
);
