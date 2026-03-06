import { onRequest } from "firebase-functions/v2/https";
import { defineSecret } from "firebase-functions/params";
import { checkRateLimit } from "./rateLimit";

const krogerClientId = defineSecret("KROGER_CLIENT_ID");
const krogerClientSecret = defineSecret("KROGER_CLIENT_SECRET");

const KROGER_TOKEN_URL = "https://api.kroger.com/v1/connect/oauth2/token";

export const tokenRefresh = onRequest(
  {
    cors: true,
    region: "us-central1",
    secrets: [krogerClientId, krogerClientSecret],
  },
  async (req, res) => {
    if (req.method !== "POST") {
      res.status(405).json({ error: "Method not allowed" });
      return;
    }

    const ip = req.ip || "unknown";
    const allowed = await checkRateLimit(ip, "tokenRefresh", 10, 1);
    if (!allowed) {
      res.status(429).json({ error: "Rate limit exceeded" });
      return;
    }

    const { refresh_token: refreshToken } = req.body || {};
    if (!refreshToken) {
      res.status(400).json({ error: "refresh_token is required" });
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
          grant_type: "refresh_token",
          refresh_token: refreshToken,
        }),
      });

      if (!response.ok) {
        const text = await response.text();
        res.status(response.status).json({ error: "Kroger API error", details: text });
        return;
      }

      const data = await response.json();
      res.json({
        access_token: data.access_token,
        refresh_token: data.refresh_token,
        expires_in: data.expires_in,
        token_type: data.token_type,
      });
    } catch (err) {
      console.error("tokenRefresh error:", err);
      res.status(500).json({ error: "Internal server error" });
    }
  }
);
