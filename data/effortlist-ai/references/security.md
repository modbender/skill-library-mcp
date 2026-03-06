# 🔒 EffortList AI — Security & Data Privacy

EffortList AI employs a defense-in-depth strategy to ensure user data remains secure and private.

---

## 1. Authentication & Access Control

- **Zero Trust Identity:** All authentication is handled via Firebase (Email/Password or Google OAuth). EffortList AI never stores or processes passwords directly.
- **Strict Data Isolation:** Firestore Security Rules enforce row-level access. Users can only access their own data; all other access is denied by default.
- **Server-Side Security:** The Developer REST API uses the Firebase Admin SDK to verify tokens and SHA-256 hashes of API keys.

## 2. Data Protection & Encryption

- **Encryption:** Data is encrypted in transit (TLS 1.3) and at rest (AES-256).
- **Transient Processing:**
  - **Documents:** Processed entirely in-memory for AI analysis and immediately discarded.
  - **Calendars:** EffortList AI does not mirror external calendars; only chosen events are saved as tasks.
- **Hashed API Keys:** Only the SHA-256 hash of API keys is stored. Raw keys are shown only once upon creation.

## 3. AI Safety & Privacy

- **Injection Protection:** User data is strictly isolated and labeled within system prompts to prevent malicious hijacking.
- **Enterprise-Tier Privacy:** EffortList AI uses enterprise APIs (Google Cloud Vertex AI). Personal data is **never** used to train the underlying AI models.
- **Strict Output Control:** AI is constrained to validated JSON schemas.

## 4. Infrastructure & Threat Mitigation

- **Bot Protection:** Shielded by Firebase App Check and reCAPTCHA v3.
- **DDoS Protection:** Enforced at the Edge network layer (Vercel) and database layer (Firestore quotas).
- **Wipe-on-Delete:** Deleting an account triggers a comprehensive wipe of tasks, folders, chat history, and Stripe customer data.

## 5. Offline Security (PWA)

- **Local Storage:** Data is stored securely in IndexedDB, protected by browser same-origin policies.
- **AI Isolation:** All AI features are strictly disabled when the device is offline to prevent stale or context-incorrect operations.
