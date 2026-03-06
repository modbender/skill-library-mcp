// SuiteBridge — Connects SuiteGate to guard-scanner runtime hook
// Why: Suite status determines the security posture of the runtime guard
// - Suite ACTIVE → strict mode (block HIGH + CRITICAL)
// - Suite INACTIVE → enforce mode (block CRITICAL only, OSS default)
// This is the "value add" of GuavaSuite: paying users get stronger protection

import { SuiteGate } from "./suiteGate.js";

/**
 * @typedef {Object} BridgeConfig
 * @property {SuiteGate} gate - SuiteGate instance
 * @property {Function} [onModeChange] - Callback when mode changes
 */

export class SuiteBridge {
    /**
     * @param {BridgeConfig} config
     */
    constructor({ gate, onModeChange = null }) {
        if (!gate) throw new Error("SuiteBridge requires a SuiteGate instance");
        this._gate = gate;
        this._onModeChange = onModeChange;
        this._lastMode = this.getMode();
    }

    /**
     * Get the current guard mode based on SuiteGate status.
     * @returns {"monitor" | "enforce" | "strict"}
     */
    getMode() {
        const status = this._gate.check();

        if (status.suiteEnabled) {
            // Suite active → premium protection
            return "strict";
        }

        // Suite inactive → OSS default
        return "enforce";
    }

    /**
     * Check if mode has changed and notify if callback is registered.
     * Called periodically or on gate status change.
     * @returns {{ mode: string, changed: boolean }}
     */
    checkModeChange() {
        const currentMode = this.getMode();
        const changed = currentMode !== this._lastMode;

        if (changed && this._onModeChange) {
            this._onModeChange(this._lastMode, currentMode);
        }

        this._lastMode = currentMode;
        return { mode: currentMode, changed };
    }

    /**
     * Get the full status report for display/logging.
     * @returns {Object}
     */
    getStatus() {
        const gateStatus = this._gate.check();
        const mode = this.getMode();

        return {
            suiteEnabled: gateStatus.suiteEnabled,
            guardEnabled: gateStatus.guardEnabled,
            guardMode: mode,
            reason: gateStatus.reason,
            expiresAt: gateStatus.expiresAt,
            graceDeadline: gateStatus.graceDeadline,
            features: {
                // OSS features (always available)
                staticScan: true,           // guard-scanner CLI
                runtimeGuard: true,         // Plugin Hook (enforce mode)
                auditLog: true,             // JSONL audit trail

                // Suite features (only when suiteEnabled)
                strictMode: gateStatus.suiteEnabled,       // HIGH+CRITICAL blocking
                soulLock: gateStatus.suiteEnabled,          // SOUL.md integrity check
                memoryGuard: gateStatus.suiteEnabled,       // Memory V4 protection
                onchainVerify: gateStatus.suiteEnabled,     // SoulRegistry V2
            },
        };
    }

    /**
     * Determine if a specific threat should be blocked based on current suite status.
     * This is the core decision function used by the runtime hook.
     *
     * @param {"CRITICAL" | "HIGH" | "MEDIUM"} severity
     * @returns {{ block: boolean, reason: string }}
     */
    shouldBlock(severity) {
        const mode = this.getMode();

        if (mode === "monitor") {
            return { block: false, reason: "Monitor mode — log only" };
        }

        if (mode === "strict") {
            // Suite active → block CRITICAL and HIGH
            if (severity === "CRITICAL" || severity === "HIGH") {
                return {
                    block: true,
                    reason: `GuavaSuite strict mode — ${severity} threat blocked`,
                };
            }
            return { block: false, reason: `${severity} below strict threshold` };
        }

        // enforce (default OSS)
        if (severity === "CRITICAL") {
            return { block: true, reason: `CRITICAL threat blocked (enforce mode)` };
        }

        return { block: false, reason: `${severity} below enforce threshold` };
    }
}
