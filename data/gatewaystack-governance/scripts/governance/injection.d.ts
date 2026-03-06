import type { Policy } from "./types.js";
interface DecodedCandidate {
    method: string;
    decoded: string;
}
/**
 * Extract plausible encoded segments from `input`, decode them, and return
 * candidates that look like printable text.
 *
 * Intentionally non-recursive to prevent exponential blowup.
 */
export declare function deobfuscate(input: string): DecodedCandidate[];
export declare function checkCanaryTokens(input: string, tokens: string[]): string[];
export declare function detectInjection(args: string, policy: Policy): {
    clean: boolean;
    detail: string;
    matches: string[];
};
export {};
