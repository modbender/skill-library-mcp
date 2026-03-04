export interface Policy {
    allowedTools: Record<string, {
        roles?: string[];
        maxArgsLength?: number;
        description?: string;
    }>;
    rateLimits: {
        perUser: {
            maxCalls: number;
            windowSeconds: number;
        };
        perSession: {
            maxCalls: number;
            windowSeconds: number;
        };
    };
    identityMap: Record<string, {
        userId: string;
        roles: string[];
    }>;
    injectionDetection: {
        enabled: boolean;
        sensitivity: "low" | "medium" | "high";
        customPatterns?: string[];
        obfuscationDetection?: boolean;
        multiLanguage?: boolean;
        canaryTokens?: string[];
    };
    auditLog: {
        path: string;
        maxFileSizeMB: number;
    };
    outputDlp?: {
        enabled: boolean;
        mode: "log" | "block";
        redactionMode: "mask" | "remove";
        customPatterns?: string[];
    };
    escalation?: {
        enabled: boolean;
        reviewOnMediumInjection: boolean;
        reviewOnFirstToolUse: boolean;
        tokenTTLSeconds: number;
    };
    behavioralMonitoring?: {
        enabled: boolean;
        spikeThreshold: number;
        monitoringWindowSeconds: number;
        action: "log" | "review" | "block";
    };
}
export interface GovernanceRequest {
    action: "check" | "log-result" | "self-test" | "approve" | "dlp-scan" | "build-baseline";
    tool?: string;
    args?: string;
    user?: string;
    channel?: string;
    session?: string;
    requestId?: string;
    result?: string;
    output?: string;
}
export interface GovernanceCheckResult {
    allowed: boolean;
    reason?: string;
    requestId: string;
    identity?: string;
    roles?: string[];
    patterns?: string[];
    verdict?: "allow" | "block" | "review";
    reviewReason?: string;
}
export interface AuditEntry {
    timestamp: string;
    requestId: string;
    action: string;
    tool?: string;
    user?: string;
    resolvedIdentity?: string;
    roles?: string[];
    channel?: string;
    session?: string;
    allowed?: boolean;
    reason?: string;
    checks?: Record<string, {
        passed: boolean;
        detail: string;
    }>;
    result?: string;
    outputSummary?: string;
    dlpMatches?: string[];
    anomalies?: Array<{
        type: string;
        severity: string;
        detail: string;
    }>;
}
export interface RateLimitState {
    calls: {
        timestamp: number;
    }[];
}
