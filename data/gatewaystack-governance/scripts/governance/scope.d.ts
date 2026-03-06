import type { Policy } from "./types.js";
export declare function checkScope(tool: string, roles: string[], policy: Policy): {
    allowed: boolean;
    detail: string;
};
