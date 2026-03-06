import { initializeApp, type FirebaseApp } from "firebase/app";
import {
  getAuth,
  signInWithCustomToken,
  type Auth,
} from "firebase/auth";
import { getFirestore, type Firestore } from "firebase/firestore";

// Public Firebase config — security is enforced by Custom Auth + Firestore rules
const FIREBASE_CONFIG = {
  apiKey: "AIzaSyDummy-placeholder-replace-with-real",
  authDomain: "hashbox-app.firebaseapp.com",
  projectId: "hashbox-app",
};

let app: FirebaseApp | null = null;
let auth: Auth | null = null;
let db: Firestore | null = null;

/**
 * Initialize the Firebase Client SDK and authenticate with a Custom Token.
 * The Custom Token is obtained from the backend's exchangeToken endpoint.
 *
 * Firebase Auth in Node.js uses inMemoryPersistence by default,
 * so the session does not survive process restarts. The caller must
 * handle token refresh (re-call exchangeToken) when auth expires.
 */
export async function initFirebaseClient(
  customToken: string,
): Promise<Firestore> {
  if (db) return db;

  app = initializeApp(FIREBASE_CONFIG);
  auth = getAuth(app);
  await signInWithCustomToken(auth, customToken);

  db = getFirestore(app);
  return db;
}

/**
 * Re-authenticate with a fresh Custom Token.
 * Used when the previous token has expired (Custom Tokens are valid for 1 hour).
 */
export async function reauthenticate(customToken: string): Promise<void> {
  if (!auth) {
    throw new Error("Firebase not initialized. Call initFirebaseClient first.");
  }
  await signInWithCustomToken(auth, customToken);
}

/** Get the Firestore instance. Throws if not initialized. */
export function getDb(): Firestore {
  if (!db) {
    throw new Error("Firebase not initialized. Call initFirebaseClient first.");
  }
  return db;
}

/** Clean up Firebase resources. */
export function resetFirebaseClient(): void {
  app = null;
  auth = null;
  db = null;
}
