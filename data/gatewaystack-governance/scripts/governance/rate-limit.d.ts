import type { Policy } from "./types.js";
export declare function checkRateLimit(userId: string, session: string | undefined, policy: Policy): {
    allowed: boolean;
    detail: string;
};
