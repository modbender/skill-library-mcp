// =============================================================================
// acp bounty create [query]
// acp bounty list
// acp bounty status <bountyId>
// acp bounty select <bountyId>
// =============================================================================

import readline from "readline";
import client from "../lib/client.js";
import * as output from "../lib/output.js";
import { requireActiveAgent } from "../lib/wallet.js";
import {
    type ActiveBounty,
    type BountyCreateInput,
    createBounty,
    getActiveBounty,
    getMatchStatus,
    listActiveBounties,
    removeActiveBounty,
    rejectCandidates,
    saveActiveBounty,
    syncBountyJobStatus,
    confirmMatch,
} from "../lib/bounty.js";
import { ROOT } from "../lib/config.js";
import {
    ensureBountyPollCron,
    removeBountyPollCronIfUnused,
} from "../lib/openclawCron.js";

function question(rl: readline.Interface, prompt: string): Promise<string> {
    return new Promise((resolve) => rl.question(prompt, resolve));
}

function parseCandidateId(raw: unknown): number | null {
    if (typeof raw === "number" && Number.isFinite(raw)) return raw;
    if (typeof raw === "string" && /^\d+$/.test(raw.trim())) {
        return parseInt(raw.trim(), 10);
    }
    return null;
}

function candidateField(candidate: any, names: string[]): string | undefined {
    for (const name of names) {
        const value = candidate?.[name];
        if (typeof value === "string" && value.trim()) return value.trim();
    }
    return undefined;
}

function candidatePriceDisplay(candidate: Record<string, unknown>): string {
    const rawPrice =
        candidate.price ??
        candidate.job_offering_price ??
        candidate.jobOfferingPrice ??
        candidate.job_fee ??
        candidate.jobFee ??
        candidate.fee;
    const rawType =
        candidate.priceType ??
        candidate.price_type ??
        candidate.jobFeeType ??
        candidate.job_fee_type;

    if (rawPrice == null) return "Unknown";
    const price = String(rawPrice);
    const type = rawType != null ? String(rawType).toLowerCase() : "";
    if (type === "fixed") return `${price} USDC`;
    if (type === "percentage") return `${price} (${type})`
    return rawType != null ? `${price} ${String(rawType)}` : price;
}

type JsonSchemaProperty = {
    type?: string;
    description?: string;
};

type RequirementSchema = {
    type?: string;
    required?: string[];
    properties?: Record<string, JsonSchemaProperty>;
};

function getCandidateRequirementSchema(candidate: Record<string, unknown>): RequirementSchema | null {
    const schemaCandidate =
        candidate.requirementSchema ??
        candidate.requirement_schema ??
        candidate.requirement;
    if (!schemaCandidate || typeof schemaCandidate !== "object" || Array.isArray(schemaCandidate)) {
        return null;
    }
    return schemaCandidate as RequirementSchema;
}

async function collectRequirementsFromSchema(
    rl: readline.Interface,
    schema: RequirementSchema
): Promise<Record<string, unknown>> {
    const properties = schema.properties ?? {};
    const requiredSet = new Set((schema.required ?? []).filter((k) => typeof k === "string"));
    const keys = Object.keys(properties);
    const out: Record<string, unknown> = {};

    if (keys.length === 0) return out;

    output.log("\n  Fill service requirements:");
    for (const key of keys) {
        const prop = properties[key] ?? {};
        const isRequired = requiredSet.has(key);
        const desc =
            typeof prop.description === "string" && prop.description.trim()
                ? ` - ${prop.description.trim()}`
                : "";
        while (true) {
            const answer = (
                await question(
                    rl,
                    `  ${key}${isRequired ? " [required]" : " [optional]"}${desc}: `
                )
            ).trim();

            if (!answer) {
                if (isRequired) {
                    output.error(`"${key}" is required.`);
                    continue;
                }
                out[key] = "";
                break;
            }
            out[key] = answer;
            break;
        }
    }

    return out;
}

export async function createInteractive(query?: string, sourceChannel?: string): Promise<void> {
    if (output.isJsonMode()) {
        output.fatal(
            "Interactive bounty creation is not supported in --json mode. Use human mode."
        );
    }

    const rl = readline.createInterface({
        input: process.stdin,
        output: process.stdout,
    });

    try {
        const agent = await requireActiveAgent();
        const poster_name = agent.name;

        const querySeed = query?.trim() || "";
        const defaultTitle = querySeed
            ? `${querySeed}`
            : "Need service provider";
        const defaultDescription = querySeed
            ? `${querySeed}`
            : "Need a provider to fulfill this request.";

        const title =
            (await question(rl, `  Title [${defaultTitle}]: `)).trim() ||
            defaultTitle;
        const description =
            (await question(rl, `  Description [${defaultDescription}]: `)).trim() ||
            defaultDescription;
        const budgetRaw = (await question(rl, "  Budget in USD (number, e.g. 50): ")).trim();
        let categoryInput = "digital";
        while (true) {
            const raw = (
                await question(rl, "  Category [digital|physical] (default: digital): ")
            )
                .trim()
                .toLowerCase();
            if (!raw) {
                categoryInput = "digital";
                break;
            }
            if (raw === "digital" || raw === "physical") {
                categoryInput = raw;
                break;
            }
            output.error('Invalid category. Enter only "digital" or "physical".');
        }
        const tags =
            (await question(rl, `  Tags comma-separated [defi,web3,ai]: `)).trim() ||
            "";

        const budget = Number(budgetRaw);
        if (!Number.isFinite(budget) || budget <= 0) {
            output.fatal("Budget must be a positive number.");
        }
        const payload: BountyCreateInput = {
            poster_name,
            poster_wallet_address: agent.walletAddress,
            title,
            description,
            budget,
            category: categoryInput,
            tags,
        };

        const created = await createBounty(payload);

        const active: ActiveBounty = {
            bountyId: created.bountyId,
            createdAt: new Date().toISOString(),
            status: "open",
            title,
            description,
            budget,
            category: categoryInput,
            tags,
            posterName: poster_name,
            posterSecret: created.posterSecret,
            sourceChannel: sourceChannel || "cli",
        };
        saveActiveBounty(active);

        let cronRegistered = false;
        try {
            const cron = ensureBountyPollCron();
            cronRegistered = cron.enabled && cron.created;
            if (cronRegistered) {
                output.log("  OpenClaw cron job registered for `acp bounty poll`.\n");
            }
        } catch {
            // Cron registration failed — include instruction in output
        }

        output.output(
            {
                bountyId: created.bountyId,
                status: "open",
                cronRegistered,
                ...(!cronRegistered ? {
                    cronAction: "required",
                    cronCommand: `openclaw cron add --id "openclaw-acp-bounty-poll" --schedule "*/10 * * * *" --command "cd \\"${ROOT}\\" && npx acp bounty poll --json"`,
                } : {}),
            },
            (data) => {
                output.heading("Bounty Created");
                output.field("Bounty ID", data.bountyId);
                output.field("Status", data.status);
                if (!cronRegistered) {
                    output.log(
                        "\n  IMPORTANT: Register the bounty poll cron job by running:"
                    );
                    output.log(
                        `    openclaw cron add --id "openclaw-acp-bounty-poll" --schedule "*/10 * * * *" --command "cd \\"${ROOT}\\" && npx acp bounty poll --json"`
                    );
                }
                output.log("");
            }
        );
    } finally {
        rl.close();
    }
}

export interface BountyCreateFlags {
    title?: string;
    description?: string;
    budget?: number;
    category?: string;
    tags?: string;
    sourceChannel?: string;
}

export async function createFromFlags(flags: BountyCreateFlags): Promise<void> {
    // Always use the active agent as poster
    const agent = await requireActiveAgent();
    const posterName = agent.name;

    const title = flags.title?.trim();
    const description = flags.description?.trim() || title;
    const budget = flags.budget;
    const category = (flags.category?.trim() || "digital").toLowerCase();
    const tags = flags.tags?.trim() || "";
    const sourceChannel = flags.sourceChannel?.trim() || "cli";

    if (!title) output.fatal("--title is required.");
    if (budget == null || !Number.isFinite(budget) || budget <= 0) {
        output.fatal("--budget must be a positive number.");
    }
    if (category !== "digital" && category !== "physical") {
        output.fatal('--category must be "digital" or "physical".');
    }

    const payload: BountyCreateInput = {
        poster_name: posterName,
        poster_wallet_address: agent.walletAddress,
        title: title!,
        description: description || title!,
        budget: budget!,
        category,
        tags,
    };

    const created = await createBounty(payload);

    const active: ActiveBounty = {
        bountyId: created.bountyId,
        createdAt: new Date().toISOString(),
        status: "open",
        title: title!,
        description: description || title!,
        budget: budget!,
        category,
        tags,
        posterName,
        posterSecret: created.posterSecret,
        ...(sourceChannel ? { sourceChannel } : {}),
    };
    saveActiveBounty(active);

    let cronRegistered = false;
    try {
        const cron = ensureBountyPollCron();
        cronRegistered = cron.enabled && cron.created;
        if (cronRegistered) {
            output.log("  OpenClaw cron job registered for `acp bounty poll`.\n");
        }
    } catch {
        // Cron registration failed — include instruction in output
    }

    output.output(
        {
            bountyId: created.bountyId,
            status: "open",
            sourceChannel: sourceChannel || null,
            cronRegistered,
            ...(!cronRegistered ? {
                cronAction: "required",
                cronCommand: `openclaw cron add --id "openclaw-acp-bounty-poll" --schedule "*/10 * * * *" --command "cd \\"${ROOT}\\" && npx acp bounty poll --json"`,
            } : {}),
        },
        (data) => {
            output.heading("Bounty Created");
            output.field("Bounty ID", data.bountyId);
            output.field("Status", data.status);
            if (data.sourceChannel) output.field("Source Channel", data.sourceChannel);
            if (!cronRegistered) {
                output.log(
                    "\n  IMPORTANT: Register the bounty poll cron job by running:"
                );
                output.log(
                    `    openclaw cron add --id "openclaw-acp-bounty-poll" --schedule "*/10 * * * *" --command "cd \\"${ROOT}\\" && npx acp bounty poll --json"`
                );
            }
            output.log("");
        }
    );
}

export async function create(query?: string, flags?: BountyCreateFlags): Promise<void> {
    // If any structured flag is provided, use the non-interactive path
    if (flags && (flags.title || flags.budget != null)) {
        return createFromFlags(flags);
    }
    return createInteractive(query, flags?.sourceChannel);
}

export async function list(): Promise<void> {
    const bounties = listActiveBounties();
    output.output({ bounties }, (data) => {
        output.heading("Active Bounties");
        if (data.bounties.length === 0) {
            output.log("  No active bounties.\n");
            return;
        }
        for (const b of data.bounties) {
            output.field("Bounty ID", b.bountyId);
            output.field("Status", b.status);
            output.field("Title", b.title);
            if (b.acpJobId) output.field("ACP Job ID", b.acpJobId);
            output.log("");
        }
    });
}

function normalizeCandidateForWatch(candidate: Record<string, unknown>): Record<string, unknown> {
    return {
        id: candidate.id,
        agentName: candidateField(candidate, ["agent_name", "agentName", "name"]) || "(unknown)",
        agentWallet: candidateField(candidate, [
            "agent_wallet", "agentWallet", "agent_wallet_address",
            "agentWalletAddress", "walletAddress", "providerWalletAddress", "provider_address",
        ]) || "",
        offeringName: candidateField(candidate, [
            "job_offering", "jobOffering", "offeringName",
            "jobOfferingName", "offering_name", "name",
        ]) || "",
        price: candidate.price ?? candidate.job_offering_price ?? candidate.jobOfferingPrice ?? candidate.job_fee ?? candidate.jobFee ?? candidate.fee ?? null,
        priceType: candidate.priceType ?? candidate.price_type ?? candidate.jobFeeType ?? candidate.job_fee_type ?? null,
        requirementSchema: candidate.requirementSchema ?? candidate.requirement_schema ?? candidate.requirement ?? null,
    };
}

export async function poll(): Promise<void> {
    const bounties = listActiveBounties();
    const result: {
        checked: number;
        pendingMatch: Array<{
            bountyId: string;
            title: string;
            description: string;
            budget: number;
            sourceChannel?: string;
            candidates: Record<string, unknown>[];
        }>;
        claimedJobs: Array<{
            bountyId: string;
            acpJobId: string;
            title: string;
            jobPhase: string;
            deliverable?: string;
            sourceChannel?: string;
        }>;
        cleaned: Array<{
            bountyId: string;
            status: string;
            sourceChannel?: string;
        }>;
        errors: Array<{
            bountyId: string;
            error: string;
        }>;
    } = {
        checked: 0,
        pendingMatch: [],
        claimedJobs: [],
        cleaned: [],
        errors: [],
    };

    for (const b of bounties) {
        result.checked += 1;
        try {
            // --- Claimed bounties: track ACP job status ---
            if (b.status === "claimed" && b.acpJobId) {
                let jobPhase = "";
                let deliverable: string | undefined;
                try {
                    const jobRes = await client.get(`/acp/jobs/${b.acpJobId}`);
                    const jobData = jobRes.data?.data ?? jobRes.data;
                    jobPhase = String(jobData?.phase ?? "").toUpperCase();
                    deliverable = jobData?.deliverable ?? undefined;
                } catch {
                    // If job fetch fails, skip this bounty for now
                    result.errors.push({
                        bountyId: b.bountyId,
                        error: `Failed to fetch ACP job ${b.acpJobId} status`,
                    });
                    continue;
                }

                const isTerminalJob = jobPhase === "COMPLETED" || jobPhase === "REJECTED" || jobPhase === "EXPIRED";

                if (isTerminalJob) {
                    // Sync bounty status via /job-status endpoint
                    if (b.posterSecret) {
                        try {
                            await syncBountyJobStatus({ bountyId: b.bountyId, posterSecret: b.posterSecret });
                        } catch {
                            // non-fatal — continue with cleanup
                        }
                    }

                    const terminalStatus = jobPhase === "COMPLETED" ? "fulfilled" : jobPhase.toLowerCase();
                    removeActiveBounty(b.bountyId);
                    result.cleaned.push({ bountyId: b.bountyId, status: terminalStatus, ...(b.sourceChannel ? { sourceChannel: b.sourceChannel } : {}) });
                } else {
                    // Job still in progress — save current phase
                    saveActiveBounty({ ...b });
                    result.claimedJobs.push({
                        bountyId: b.bountyId,
                        acpJobId: b.acpJobId,
                        title: b.title,
                        jobPhase,
                        deliverable,
                        ...(b.sourceChannel ? { sourceChannel: b.sourceChannel } : {}),
                    });
                }
                continue;
            }

            // --- Non-claimed bounties: check match status ---
            const remote = await getMatchStatus(b.bountyId);
            const status = String(remote.status).toLowerCase();

            if (status === "fulfilled" || status === "expired" || status === "rejected") {
                removeActiveBounty(b.bountyId);
                result.cleaned.push({ bountyId: b.bountyId, status, ...(b.sourceChannel ? { sourceChannel: b.sourceChannel } : {}) });
                continue;
            }

            const isNewPendingMatch =
                status === "pending_match" &&
                Array.isArray(remote.candidates) &&
                remote.candidates.length > 0 &&
                !b.notifiedPendingMatch;

            saveActiveBounty({
                ...b,
                status: remote.status,
                // Mark as notified once we include it in pendingMatch output
                ...(isNewPendingMatch ? { notifiedPendingMatch: true } : {}),
            });

            if (isNewPendingMatch) {
                const candidates = remote.candidates.map((c) =>
                    normalizeCandidateForWatch(c as Record<string, unknown>)
                );

                result.pendingMatch.push({
                    bountyId: b.bountyId,
                    title: b.title,
                    description: b.description,
                    budget: b.budget,
                    ...(b.sourceChannel ? { sourceChannel: b.sourceChannel } : {}),
                    candidates,
                });
            }
        } catch (e) {
            result.errors.push({
                bountyId: b.bountyId,
                error: e instanceof Error ? e.message : String(e),
            });
        }
    }

    try {
        removeBountyPollCronIfUnused();
    } catch {
        // non-fatal
    }

    output.output(result, (r) => {
        output.heading("Bounty Poll");
        output.field("Checked", r.checked);
        output.field("Pending Match", r.pendingMatch.length);
        output.field("Claimed Jobs", r.claimedJobs.length);
        output.field("Cleaned", r.cleaned.length);
        output.field("Errors", r.errors.length);
        if (r.pendingMatch.length > 0) {
            output.log("\n  Pending Match (candidates ready):");
            for (const p of r.pendingMatch) {
                output.log(
                    `    - Bounty ${p.bountyId}: "${p.title}" — ${p.candidates.length} candidate(s)`
                );
                for (const c of p.candidates) {
                    const price = c.priceType === "fixed"
                        ? `${c.price} USDC`
                        : c.price != null ? String(c.price) : "N/A";
                    output.log(
                        `        ${c.agentName} — ${c.offeringName} (${price})`
                    );
                }
                output.log(
                    `      -> run: acp bounty select ${p.bountyId}`
                );
            }
        }
        if (r.claimedJobs.length > 0) {
            output.log("\n  Claimed Jobs (in progress):");
            for (const j of r.claimedJobs) {
                output.log(
                    `    - Bounty ${j.bountyId}: "${j.title}" — Job ${j.acpJobId} phase: ${j.jobPhase}`
                );
            }
        }
        if (r.cleaned.length > 0) {
            output.log("\n  Cleaned (terminal):");
            for (const c of r.cleaned) {
                output.log(`    - ${c.bountyId}: ${c.status}`);
            }
        }
        if (r.errors.length > 0) {
            output.log("\n  Errors:");
            for (const err of r.errors) {
                output.log(`    - ${err.bountyId}: ${err.error}`);
            }
        }
        output.log("");
    });
}

export async function status(bountyId: string): Promise<void> {
    if (!bountyId) output.fatal("Usage: acp bounty status <bountyId>");
    const active = getActiveBounty(bountyId);
    if (!active) output.fatal(`Bounty not found in local state: ${bountyId}`);

    if (active.posterSecret) {
        try {
            await syncBountyJobStatus({
                bountyId,
                posterSecret: active.posterSecret,
            });
        } catch (e) {
            output.warn(
                `Failed to sync bounty job status: ${e instanceof Error ? e.message : String(e)}`
            );
        }
    }

    const remote = await getMatchStatus(bountyId);
    const normalized = String(remote.status).toLowerCase();
    const isTerminal =
        normalized === "fulfilled" || normalized === "expired" || normalized === "rejected";
    const next = { ...active, status: remote.status };
    if (isTerminal) {
        removeActiveBounty(bountyId);
        try {
            removeBountyPollCronIfUnused();
        } catch {
            // non-fatal
        }
    } else {
        saveActiveBounty(next);
    }

    output.output(
        {
            bountyId,
            local: next,
            remote,
        },
        (data) => {
            output.heading(`Bounty ${data.bountyId}`);
            output.field("Status", data.remote.status);
            output.field("Title", data.local.title);
            output.field("Candidates", data.remote.candidates.length);
            if (isTerminal) {
                output.log("  Local bounty record cleaned up (terminal status).");
            }
            output.log("");
        }
    );

    if (!output.isJsonMode() && String(remote.status).toLowerCase() === "pending_match") {
        const rl = readline.createInterface({
            input: process.stdin,
            output: process.stdout,
        });
        let shouldSelect = false;
        try {
            const answer = (
                await question(rl, "  Bounty is pending_match. Select provider now? (Y/n): ")
            )
                .trim()
                .toLowerCase();
            shouldSelect = answer === "y" || answer === "yes" || answer === "";
        } finally {
            rl.close();
        }
        if (shouldSelect) {
            await select(bountyId);
        }
    }
}

export async function select(bountyId: string): Promise<void> {
    if (!bountyId) output.fatal("Usage: acp bounty select <bountyId>");
    const active = getActiveBounty(bountyId);
    if (!active) output.fatal(`Bounty not found in local state: ${bountyId}`);
    const posterSecret = active.posterSecret;
    if (!posterSecret) {
        output.fatal("Missing poster secret for this bounty.");
    }

    const match = await getMatchStatus(bountyId);
    if (String(match.status).toLowerCase() !== "pending_match") {
        output.fatal(`Bounty is not pending_match. Current status: ${match.status}`);
    }
    if (!Array.isArray(match.candidates) || match.candidates.length === 0) {
        output.fatal("No candidates available for this bounty.");
    }

    if (output.isJsonMode()) {
        output.output({ bountyId, status: match.status, candidates: match.candidates }, () => { });
        return;
    }

    const rl = readline.createInterface({
        input: process.stdin,
        output: process.stdout,
    });

    try {
        output.heading(`Select Candidate for Bounty ${bountyId}`);
        for (let i = 0; i < match.candidates.length; i++) {
            const c = match.candidates[i] as Record<string, unknown>;
            const candidateId = parseCandidateId(c.id) ?? -1;
            output.log(
                `  [${i + 1}] candidateId=${candidateId} ${JSON.stringify(c)}`
            );
        }
        output.log("  [0] None of these candidates");

        const choiceRaw = (await question(rl, "  Choose candidate number: ")).trim();
        if (choiceRaw === "0") {
            await rejectCandidates({
                bountyId,
                posterSecret,
            });
            saveActiveBounty({
                ...active,
                status: "open",
                selectedCandidateId: undefined,
                acpJobId: undefined,
                notifiedPendingMatch: false,
            });
            output.log(
                "  Rejected current candidates. Bounty moved back to open for new matching.\n"
            );
            return;
        }
        const idx = parseInt(choiceRaw, 10) - 1;
        if (!Number.isInteger(idx) || idx < 0 || idx >= match.candidates.length) {
            output.fatal("Invalid candidate selection.");
        }
        const selected = match.candidates[idx] as Record<string, unknown>;
        const candidateId = parseCandidateId(selected.id);
        if (candidateId == null) output.fatal("Selected candidate has invalid id.");

        const walletDefault = candidateField(selected, [
            "agent_wallet",
            "agentWallet",
            "agent_wallet_address",
            "agentWalletAddress",
            "walletAddress",
            "providerWalletAddress",
            "provider_address",
        ]);
        const offeringDefault = candidateField(selected, [
            "job_offering",
            "jobOffering",
            "offeringName",
            "jobOfferingName",
            "offering_name",
            "name",
        ]);

        const wallet = walletDefault || "";
        const offering = offeringDefault || "";

        if (!wallet) {
            output.fatal(
                "Selected candidate is missing provider wallet (expected agent_wallet or walletAddress fields)."
            );
        }
        if (!offering) {
            output.fatal(
                "Selected candidate is missing job offering (expected job_offering/offeringName fields)."
            );
        }

        const providerName =
            candidateField(selected, ["agent_name", "agentName", "name"]) || "(unknown)";
        const offeringPrice = candidatePriceDisplay(selected);

        output.log("\n  Selected Candidate");
        output.log("  ------------------");
        output.log(`  Provider: ${providerName}`);
        output.log(`  Wallet:   ${wallet}`);
        output.log(`  Offering: ${offering}`);
        output.log(`  Price:    ${offeringPrice}`);
        const confirm = (
            await question(rl, "\n  Continue and create ACP job for this candidate? (Y/n): ")
        )
            .trim()
            .toLowerCase();
        if (!(confirm === "y" || confirm === "yes" || confirm === "")) {
            output.log("  Candidate selection cancelled.\n");
            return;
        }

        const schema = getCandidateRequirementSchema(selected);
        const serviceRequirements =
            schema != null
                ? await collectRequirementsFromSchema(rl, schema)
                : {};

        const job = await client.post<{ data?: { jobId?: number }; jobId?: number }>(
            "/acp/jobs",
            {
                providerWalletAddress: wallet,
                jobOfferingName: offering,
                serviceRequirements,
            }
        );
        const acpJobId = String(job.data?.data?.jobId ?? job.data?.jobId ?? "");
        if (!acpJobId) output.fatal("Failed to create ACP job for selected candidate.");

        await confirmMatch({
            bountyId,
            posterSecret,
            candidateId,
            acpJobId,
        });

        const next: ActiveBounty = {
            ...active,
            status: "claimed",
            selectedCandidateId: candidateId,
            acpJobId,
        };
        saveActiveBounty(next);

        output.output(
            {
                bountyId,
                candidateId,
                acpJobId,
                status: "claimed",
            },
            (data) => {
                output.heading("Bounty Claimed");
                output.field("Bounty ID", data.bountyId);
                output.field("Candidate ID", data.candidateId);
                output.field("ACP Job ID", data.acpJobId);
                output.field("Status", data.status);
                output.log(
                    `\n  Use \`acp job status <jobId>\` to monitor the ACP job.`
                );
                output.log(
                    `  Then run \`acp bounty status ${data.bountyId}\` to sync/update bounty status.\n`
                );
            }
        );
    } finally {
        rl.close();
    }
}

export async function cleanup(bountyId: string): Promise<void> {
    if (!bountyId) output.fatal("Usage: acp bounty cleanup <bountyId>");
    const active = getActiveBounty(bountyId);
    if (!active) {
        output.log(`  Bounty not found locally: ${bountyId}`);
        return;
    }
    removeActiveBounty(bountyId);
    try {
        removeBountyPollCronIfUnused();
    } catch {
        // non-fatal
    }
    output.log(`  Cleaned up bounty ${bountyId}\n`);
}

