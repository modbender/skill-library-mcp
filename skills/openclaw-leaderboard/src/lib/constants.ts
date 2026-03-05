export const SITE_NAME = "OpenClaw Leaderboard";
export const SITE_DESCRIPTION =
  "Public leaderboard ranking OpenClaw instances by autonomous earnings — with proof.";
export const SITE_URL = (
  process.env.NEXT_PUBLIC_SITE_URL ?? "https://openclaw-leaderboard-omega.vercel.app"
).trim();

export const MAX_FILE_SIZE = 5 * 1024 * 1024; // 5MB
export const ALLOWED_IMAGE_TYPES = [
  "image/jpeg",
  "image/png",
  "image/webp",
  "image/gif",
];

export const SUSPICIOUS_VOTE_THRESHOLD = 0.5; // 50% suspicious votes = auto-flag
export const VERIFICATION_MIN_VOTES = 5;
export const VERIFICATION_LEGIT_THRESHOLD = 0.7; // 70% legit votes = auto-verify

export const DEFAULT_PAGE_SIZE = 20;
export const MAX_PAGE_SIZE = 100;
