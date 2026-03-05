import { onRequest } from "firebase-functions/v2/https";
import { getFirestore } from "firebase-admin/firestore";

export const tokenUser = onRequest(
  {
    cors: true,
    region: "us-central1",
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

    const db = getFirestore();
    const snapshot = await db
      .collection("sessions")
      .where("session_id", "==", sessionId)
      .where("completed", "==", true)
      .limit(1)
      .get();

    if (snapshot.empty) {
      res.status(202).json({ status: "pending" });
      return;
    }

    const doc = snapshot.docs[0];
    const data = doc.data();

    res.json({
      access_token: data.access_token,
      refresh_token: data.refresh_token,
      expires_in: data.expires_in,
      token_type: data.token_type,
    });

    await doc.ref.delete();
  }
);
