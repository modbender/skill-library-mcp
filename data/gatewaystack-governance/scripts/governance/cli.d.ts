import type { Policy, GovernanceRequest } from "./types.js";
export declare function parseArgs(argv: string[]): GovernanceRequest;
export declare function runGovernanceCheck(req: GovernanceRequest): void;
export declare function runSelfTest(policy: Policy): void;
