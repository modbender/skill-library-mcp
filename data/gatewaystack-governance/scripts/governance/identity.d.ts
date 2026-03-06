import type { Policy } from "./types.js";
export declare function verifyIdentity(user: string | undefined, channel: string | undefined, policy: Policy): {
    verified: boolean;
    userId: string;
    roles: string[];
    detail: string;
};
