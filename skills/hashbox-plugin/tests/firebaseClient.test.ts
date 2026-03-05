import { describe, it, expect, vi, beforeEach } from "vitest";

// --- Mock firebase/app ---
const mockInitializeApp = vi.fn().mockReturnValue({ name: "mock-app" });
vi.mock("firebase/app", () => ({
  initializeApp: (...args: unknown[]) => mockInitializeApp(...args),
}));

// --- Mock firebase/auth ---
const mockSignInWithCustomToken = vi.fn().mockResolvedValue({ user: { uid: "mock-uid" } });
const mockGetAuth = vi.fn().mockReturnValue({ currentUser: null });
vi.mock("firebase/auth", () => ({
  getAuth: (...args: unknown[]) => mockGetAuth(...args),
  signInWithCustomToken: (...args: unknown[]) => mockSignInWithCustomToken(...args),
}));

// --- Mock firebase/firestore ---
const mockGetFirestore = vi.fn().mockReturnValue({ type: "firestore" });
vi.mock("firebase/firestore", () => ({
  getFirestore: (...args: unknown[]) => mockGetFirestore(...args),
}));

import {
  initFirebaseClient,
  reauthenticate,
  getDb,
  resetFirebaseClient,
} from "../src/firebaseClient.js";

describe("firebaseClient", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    resetFirebaseClient();
  });

  describe("initFirebaseClient", () => {
    it("should initialize app, authenticate, and return Firestore", async () => {
      const db = await initFirebaseClient("custom-token-1");

      expect(mockInitializeApp).toHaveBeenCalledOnce();
      expect(mockGetAuth).toHaveBeenCalledOnce();
      expect(mockSignInWithCustomToken).toHaveBeenCalledOnce();
      expect(mockGetFirestore).toHaveBeenCalledOnce();
      expect(db).toEqual({ type: "firestore" });
    });

    it("should return cached Firestore on second call", async () => {
      const db1 = await initFirebaseClient("token-a");
      const db2 = await initFirebaseClient("token-b");

      expect(db1).toBe(db2);
      expect(mockInitializeApp).toHaveBeenCalledOnce(); // Only once
    });

    it("should pass custom token to signInWithCustomToken", async () => {
      await initFirebaseClient("my-special-token");

      const authInstance = mockGetAuth.mock.results[0].value;
      expect(mockSignInWithCustomToken).toHaveBeenCalledWith(
        authInstance,
        "my-special-token",
      );
    });

    it("should propagate signIn errors", async () => {
      mockSignInWithCustomToken.mockRejectedValueOnce(
        new Error("Invalid custom token"),
      );

      await expect(initFirebaseClient("bad-token")).rejects.toThrow(
        "Invalid custom token",
      );
    });
  });

  describe("reauthenticate", () => {
    it("should call signInWithCustomToken with new token", async () => {
      await initFirebaseClient("initial-token");
      mockSignInWithCustomToken.mockClear();

      await reauthenticate("refreshed-token");

      expect(mockSignInWithCustomToken).toHaveBeenCalledOnce();
      const authInstance = mockGetAuth.mock.results[0].value;
      expect(mockSignInWithCustomToken).toHaveBeenCalledWith(
        authInstance,
        "refreshed-token",
      );
    });

    it("should throw if Firebase not initialized", async () => {
      await expect(reauthenticate("token")).rejects.toThrow(
        "Firebase not initialized",
      );
    });
  });

  describe("getDb", () => {
    it("should return Firestore after init", async () => {
      await initFirebaseClient("token");
      const db = getDb();
      expect(db).toEqual({ type: "firestore" });
    });

    it("should throw if not initialized", () => {
      expect(() => getDb()).toThrow("Firebase not initialized");
    });
  });

  describe("resetFirebaseClient", () => {
    it("should clear cached state", async () => {
      await initFirebaseClient("token");
      resetFirebaseClient();

      expect(() => getDb()).toThrow("Firebase not initialized");
    });

    it("should allow re-initialization after reset", async () => {
      await initFirebaseClient("token-1");
      resetFirebaseClient();
      await initFirebaseClient("token-2");

      expect(mockInitializeApp).toHaveBeenCalledTimes(2);
    });
  });
});
