/**
 * Governance Skill — XPR Network governance (gov contract)
 *
 * Read-only tools use fetch-based RPC helpers (no signing).
 * Write tools create a session from env vars for signing transactions.
 */

// ── Types ────────────────────────────────────────

interface ToolDef {
  name: string;
  description: string;
  parameters: { type: 'object'; required?: string[]; properties: Record<string, unknown> };
  handler: (params: any) => Promise<unknown>;
}

interface SkillApi {
  registerTool(tool: ToolDef): void;
  getConfig(): Record<string, unknown>;
}

// ── Constants ────────────────────────────────────

const GOV_CONTRACT = 'gov';
const GOV_API = 'https://gov.api.xprnetwork.org/api/v1/proposals';
const GOV_WEBSITE = 'https://gov.xprnetwork.org';

const MAINNET_RPC = 'https://xpr-mainnet-rpc.saltant.io';

// ── RPC Helper ───────────────────────────────────

const RPC_TIMEOUT = 15000;

async function rpcPost(endpoint: string, path: string, body: unknown): Promise<any> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), RPC_TIMEOUT);
  try {
    const resp = await fetch(`${endpoint}${path}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
      signal: controller.signal,
    });
    if (!resp.ok) {
      const text = await resp.text().catch(() => '');
      throw new Error(`RPC ${path} failed (${resp.status}): ${text.slice(0, 200)}`);
    }
    return await resp.json();
  } finally {
    clearTimeout(timer);
  }
}

async function getTableRows(endpoint: string, opts: {
  code: string; scope: string; table: string;
  lower_bound?: string | number; upper_bound?: string | number;
  limit?: number; key_type?: string; index_position?: number;
  json?: boolean; reverse?: boolean;
}): Promise<{ rows: any[]; more: boolean }> {
  const result = await rpcPost(endpoint, '/v1/chain/get_table_rows', {
    json: opts.json !== false,
    code: opts.code,
    scope: opts.scope,
    table: opts.table,
    lower_bound: opts.lower_bound,
    upper_bound: opts.upper_bound,
    limit: opts.limit || 100,
    key_type: opts.key_type,
    index_position: opts.index_position,
    reverse: opts.reverse || false,
  });
  return { rows: result.rows || [], more: !!result.more };
}

// ── Gov API Helper ───────────────────────────────

async function fetchGovApiProposal(contentId: string): Promise<any | null> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), RPC_TIMEOUT);
  try {
    const resp = await fetch(`${GOV_API}/${contentId}`, {
      signal: controller.signal,
      headers: { 'Accept': 'application/json' },
    });
    if (!resp.ok) return null;
    return await resp.json();
  } catch {
    return null;
  } finally {
    clearTimeout(timer);
  }
}

// ── Session Factory ──────────────────────────────

let cachedSession: { api: any; account: string; permission: string } | null = null;

async function getGovSession(): Promise<{ api: any; account: string; permission: string }> {
  if (cachedSession) return cachedSession;

  const privateKey = process.env.XPR_PRIVATE_KEY;
  const account = process.env.XPR_ACCOUNT;
  const permission = process.env.XPR_PERMISSION || 'active';

  if (!privateKey) throw new Error('XPR_PRIVATE_KEY is required for governance write operations');
  if (!account) throw new Error('XPR_ACCOUNT is required for governance write operations');

  const { Api, JsonRpc, JsSignatureProvider } = await import('@proton/js');
  const rpc = new JsonRpc(MAINNET_RPC);
  const signatureProvider = new JsSignatureProvider([privateKey]);
  const api = new Api({ rpc, signatureProvider });

  cachedSession = { api, account, permission };
  return cachedSession;
}

// ── Helpers ──────────────────────────────────────

function proposalStatus(proposal: any): string {
  const now = Math.floor(Date.now() / 1000);
  if (proposal.approve === 'Approved') return 'Approved';
  if (proposal.approve === 'Declined') return 'Declined';
  if (now < proposal.startTime) return 'Upcoming';
  if (now <= proposal.endTime) return 'Active';
  return 'Ended';
}

function formatTimestamp(ts: number): string {
  return new Date(ts * 1000).toISOString().replace('T', ' ').replace(/\.\d+Z$/, ' UTC');
}

function parseQuantity(qty: string): { amount: number; symbol: string; precision: number } | null {
  const parts = qty.trim().split(' ');
  if (parts.length !== 2) return null;
  const amount = parseFloat(parts[0]);
  const symbol = parts[1];
  const decParts = parts[0].split('.');
  const precision = decParts.length > 1 ? decParts[1].length : 0;
  return { amount, symbol, precision };
}

function formatAsset(amount: number, precision: number, symbol: string): string {
  return `${amount.toFixed(precision)} ${symbol}`;
}

// ── Skill Entry Point ────────────────────────────

export default function governanceSkill(api: SkillApi): void {
  const config = api.getConfig();
  const rpcEndpoint = MAINNET_RPC;

  // ════════════════════════════════════════════════
  // READ-ONLY TOOLS
  // ════════════════════════════════════════════════

  // ── 1. gov_list_communities ──
  api.registerTool({
    name: 'gov_list_communities',
    description: 'List all XPR Network governance communities with their voting strategies, proposal fees, quorum requirements, and admins.',
    parameters: {
      type: 'object',
      properties: {},
    },
    handler: async () => {
      try {
        const { rows } = await getTableRows(rpcEndpoint, {
          code: GOV_CONTRACT, scope: GOV_CONTRACT, table: 'communities', limit: 50,
        });

        return {
          communities: rows.map((c: any) => {
            const fee = parseQuantity(c.proposalFee?.quantity || '0 XPR');
            return {
              id: c.id,
              name: c.name,
              description: c.description,
              controller: c.controller,
              website: c.website,
              strategies: c.strategies,
              voting_systems: c.votingSystems,
              proposal_fee: c.proposalFee?.quantity || 'unknown',
              proposal_fee_contract: c.proposalFee?.contract || '',
              min_proposal_time_seconds: c.minProposalTime,
              quorum_basis_points: c.quorum,
              quorum_pct: `${(c.quorum / 100).toFixed(2)}%`,
              admins: c.admins,
              approving_proposals: !!c.approvingProposal,
            };
          }),
          total: rows.length,
        };
      } catch (err: any) {
        return { error: `Failed to list communities: ${err.message}` };
      }
    },
  });

  // ── 2. gov_list_proposals ──
  api.registerTool({
    name: 'gov_list_proposals',
    description: 'List governance proposals. Can filter by community ID and status (Active, Upcoming, Ended, Approved, Declined). Returns most recent proposals first.',
    parameters: {
      type: 'object',
      properties: {
        community_id: { type: 'number', description: 'Filter by community ID (e.g. 3 for XPR Network)' },
        status: { type: 'string', description: 'Filter by status: "Active", "Upcoming", "Ended", "Approved", "Declined"' },
        limit: { type: 'number', description: 'Max proposals to return (default 20, max 100)' },
      },
    },
    handler: async ({ community_id, status, limit }: {
      community_id?: number; status?: string; limit?: number;
    }) => {
      try {
        const maxResults = Math.min(limit || 20, 100);

        // Fetch proposals in reverse order (newest first)
        const allProposals: any[] = [];
        let more = true;
        let fetchLimit = maxResults * 3; // over-fetch to account for filters
        let attempts = 0;

        // Paginate backwards from the latest proposals
        const { rows: latestBatch } = await getTableRows(rpcEndpoint, {
          code: GOV_CONTRACT, scope: GOV_CONTRACT, table: 'proposals',
          limit: Math.min(fetchLimit, 100), reverse: true,
        });

        for (const p of latestBatch) {
          if (community_id !== undefined && p.communityId !== community_id) continue;
          const pStatus = proposalStatus(p);
          if (status && pStatus.toLowerCase() !== status.toLowerCase()) continue;
          allProposals.push(p);
          if (allProposals.length >= maxResults) break;
        }

        // If we need more and there are more rows, continue paginating
        if (allProposals.length < maxResults && latestBatch.length === Math.min(fetchLimit, 100)) {
          const lastId = latestBatch[latestBatch.length - 1]?.id;
          if (lastId > 0) {
            const { rows: nextBatch } = await getTableRows(rpcEndpoint, {
              code: GOV_CONTRACT, scope: GOV_CONTRACT, table: 'proposals',
              upper_bound: lastId - 1, limit: 100, reverse: true,
            });
            for (const p of nextBatch) {
              if (community_id !== undefined && p.communityId !== community_id) continue;
              const pStatus = proposalStatus(p);
              if (status && pStatus.toLowerCase() !== status.toLowerCase()) continue;
              allProposals.push(p);
              if (allProposals.length >= maxResults) break;
            }
          }
        }

        return {
          proposals: allProposals.map((p: any) => ({
            id: p.id,
            author: p.author,
            community_id: p.communityId,
            content_id: p.content,
            strategy: p.strategy,
            voting_system: p.votingSystem,
            candidates: p.candidates,
            start_time: formatTimestamp(p.startTime),
            end_time: formatTimestamp(p.endTime),
            status: proposalStatus(p),
            approve: p.approve || '',
            url: `${GOV_WEBSITE}/communities/${p.communityId}/proposals/${p.id}`,
          })),
          total: allProposals.length,
          filters: { community_id, status },
        };
      } catch (err: any) {
        return { error: `Failed to list proposals: ${err.message}` };
      }
    },
  });

  // ── 3. gov_get_proposal ──
  api.registerTool({
    name: 'gov_get_proposal',
    description: 'Get full details for a governance proposal by ID, including title and description from the Gov API and vote totals per candidate.',
    parameters: {
      type: 'object',
      required: ['proposal_id'],
      properties: {
        proposal_id: { type: 'number', description: 'Proposal ID' },
      },
    },
    handler: async ({ proposal_id }: { proposal_id: number }) => {
      if (proposal_id === undefined || proposal_id === null) {
        return { error: 'proposal_id is required' };
      }

      try {
        // Fetch proposal from chain
        const { rows } = await getTableRows(rpcEndpoint, {
          code: GOV_CONTRACT, scope: GOV_CONTRACT, table: 'proposals',
          lower_bound: proposal_id, upper_bound: proposal_id, limit: 1,
        });

        if (rows.length === 0) {
          return { error: `Proposal #${proposal_id} not found` };
        }

        const p = rows[0];

        // Fetch title + vote data from Gov API
        let govData: any = null;
        if (p.content) {
          govData = await fetchGovApiProposal(p.content);
        }

        // Fetch community for context
        const { rows: communities } = await getTableRows(rpcEndpoint, {
          code: GOV_CONTRACT, scope: GOV_CONTRACT, table: 'communities',
          lower_bound: p.communityId, upper_bound: p.communityId, limit: 1,
        });
        const community = communities[0] || null;

        return {
          id: p.id,
          author: p.author,
          community_id: p.communityId,
          community_name: community?.name || 'Unknown',
          content_id: p.content,
          title: govData?.title || '(title not available)',
          description: govData?.description
            ? govData.description.replace(/<[^>]+>/g, '').slice(0, 2000)
            : '(description not available)',
          strategy: p.strategy,
          voting_system: p.votingSystem,
          candidates: (govData?.candidates || p.candidates).map((c: any) => ({
            id: c.id,
            name: c.name,
            votes: c.tokenAmount ?? null,
          })),
          total_votes: govData?.tokenAmount ?? null,
          quorum_pct: govData?.quorum !== undefined ? `${govData.quorum}%` : null,
          community_quorum_pct: community ? `${(community.quorum / 100).toFixed(2)}%` : null,
          start_time: formatTimestamp(p.startTime),
          end_time: formatTimestamp(p.endTime),
          status: proposalStatus(p),
          approve: p.approve || '',
          url: `${GOV_WEBSITE}/communities/${p.communityId}/proposals/${p.id}`,
        };
      } catch (err: any) {
        return { error: `Failed to get proposal: ${err.message}` };
      }
    },
  });

  // ── 4. gov_get_votes ──
  api.registerTool({
    name: 'gov_get_votes',
    description: 'Get individual votes cast on a governance proposal. Scans from most recent votes. May be slow for old proposals with many votes.',
    parameters: {
      type: 'object',
      required: ['proposal_id'],
      properties: {
        proposal_id: { type: 'number', description: 'Proposal ID' },
        limit: { type: 'number', description: 'Max votes to return (default 50, max 200)' },
      },
    },
    handler: async ({ proposal_id, limit }: { proposal_id: number; limit?: number }) => {
      if (proposal_id === undefined || proposal_id === null) {
        return { error: 'proposal_id is required' };
      }

      const maxVotes = Math.min(limit || 50, 200);

      try {
        const matched: any[] = [];
        let scanKey: number | undefined;
        const MAX_SCAN_BATCHES = 20; // safety limit: scan at most 2000 rows

        for (let batch = 0; batch < MAX_SCAN_BATCHES && matched.length < maxVotes; batch++) {
          const opts: any = {
            code: GOV_CONTRACT, scope: GOV_CONTRACT, table: 'votes',
            limit: 100, reverse: true,
          };
          if (scanKey !== undefined) {
            opts.upper_bound = scanKey;
          }

          const { rows, more } = await getTableRows(rpcEndpoint, opts);

          if (rows.length === 0) break;

          for (const v of rows) {
            if (v.proposalId === proposal_id) {
              matched.push({
                vote_id: v.id,
                voter: v.voter,
                community_id: v.communityId,
                winners: v.winners,
                timestamp: formatTimestamp(v.timestamp),
              });
              if (matched.length >= maxVotes) break;
            }
          }

          if (!more) break;
          scanKey = rows[rows.length - 1].id - 1;
          if (scanKey < 0) break;
        }

        const totalWeight = matched.reduce((sum, v) => {
          return sum + v.winners.reduce((ws: number, w: any) => ws + (w.weight || 0), 0);
        }, 0);

        return {
          proposal_id,
          votes: matched,
          count: matched.length,
          total_weight_scanned: totalWeight,
          note: matched.length >= maxVotes
            ? `Returned first ${maxVotes} votes (most recent). Use Gov API for complete totals.`
            : `Found ${matched.length} votes for this proposal.`,
        };
      } catch (err: any) {
        return { error: `Failed to get votes: ${err.message}` };
      }
    },
  });

  // ── 5. gov_get_config ──
  api.registerTool({
    name: 'gov_get_config',
    description: 'Get XPR Network governance global configuration — paused state, total communities, proposals, and votes.',
    parameters: {
      type: 'object',
      properties: {},
    },
    handler: async () => {
      try {
        const { rows } = await getTableRows(rpcEndpoint, {
          code: GOV_CONTRACT, scope: GOV_CONTRACT, table: 'govglobal', limit: 1,
        });

        if (rows.length === 0) {
          return { error: 'Governance global config not found' };
        }

        const cfg = rows[0];
        return {
          is_paused: !!cfg.isPaused,
          next_community_id: cfg.communityId,
          total_communities: cfg.communityId - 1, // IDs start at 1
          next_proposal_id: cfg.proposalId,
          total_proposals: cfg.proposalId,
          next_vote_id: cfg.voteId,
          total_votes: cfg.voteId,
        };
      } catch (err: any) {
        return { error: `Failed to get config: ${err.message}` };
      }
    },
  });

  // ════════════════════════════════════════════════
  // WRITE TOOLS (require confirmation)
  // ════════════════════════════════════════════════

  // ── 6. gov_vote ──
  api.registerTool({
    name: 'gov_vote',
    description: 'Vote on a governance proposal. For Yes/No proposals, use winners=[{id:0, weight:100}] for the first option or [{id:1, weight:100}] for the second. Check the proposal\'s candidates first.',
    parameters: {
      type: 'object',
      required: ['community_id', 'proposal_id', 'winners', 'confirmed'],
      properties: {
        community_id: { type: 'number', description: 'Community ID (e.g. 3 for XPR Network)' },
        proposal_id: { type: 'number', description: 'Proposal ID to vote on' },
        winners: {
          type: 'array',
          description: 'Array of {id, weight} objects. id = candidate ID, weight = vote weight (typically 100 for full weight)',
        },
        confirmed: { type: 'boolean', description: 'Must be true to proceed' },
      },
    },
    handler: async ({ community_id, proposal_id, winners, confirmed }: {
      community_id: number; proposal_id: number; winners: { id: number; weight: number }[];
      confirmed?: boolean;
    }) => {
      if (!confirmed) {
        return {
          error: 'Confirmation required. Set confirmed=true to cast your vote.',
          community_id, proposal_id, winners,
        };
      }
      if (community_id === undefined) return { error: 'community_id is required' };
      if (proposal_id === undefined) return { error: 'proposal_id is required' };
      if (!Array.isArray(winners) || winners.length === 0) {
        return { error: 'winners must be a non-empty array of {id, weight} objects' };
      }

      try {
        const { api: eosApi, account, permission } = await getGovSession();

        const result = await eosApi.transact({
          actions: [{
            account: GOV_CONTRACT,
            name: 'vote',
            authorization: [{ actor: account, permission }],
            data: {
              voter: account,
              communityId: community_id,
              proposalId: proposal_id,
              winners: winners.map(w => ({ id: w.id, weight: w.weight })),
            },
          }],
        }, { blocksBehind: 3, expireSeconds: 30 });

        return {
          transaction_id: result.transaction_id || result.processed?.id,
          action: 'vote',
          voter: account,
          community_id,
          proposal_id,
          winners,
          url: `${GOV_WEBSITE}/communities/${community_id}/proposals/${proposal_id}`,
        };
      } catch (err: any) {
        return { error: `Failed to vote: ${err.message}` };
      }
    },
  });

  // ── 7. gov_post_proposal ──
  api.registerTool({
    name: 'gov_post_proposal',
    description: 'Create a new governance proposal. Requires a content ID from the Gov API and pays the community\'s proposal fee. The fee is sent as a token transfer to the gov contract, followed by the postprop action.',
    parameters: {
      type: 'object',
      required: ['community_id', 'content_id', 'strategy', 'voting_system', 'candidates', 'start_time', 'end_time', 'confirmed'],
      properties: {
        community_id: { type: 'number', description: 'Community ID to post in' },
        content_id: { type: 'string', description: 'Content ID from Gov API (MongoDB ObjectId)' },
        strategy: { type: 'string', description: 'Voting strategy (must match community strategies)' },
        voting_system: { type: 'string', description: 'Voting system: "0"=single, "1"=multiple, "2"=ranked, "5"=approval' },
        candidates: {
          type: 'array',
          description: 'Array of {id, name} candidates. e.g. [{id:0,name:"Yes"},{id:1,name:"No"}]',
        },
        start_time: { type: 'number', description: 'Unix timestamp (seconds) for voting start' },
        end_time: { type: 'number', description: 'Unix timestamp (seconds) for voting end' },
        confirmed: { type: 'boolean', description: 'Must be true to proceed' },
      },
    },
    handler: async ({ community_id, content_id, strategy, voting_system, candidates, start_time, end_time, confirmed }: {
      community_id: number; content_id: string; strategy: string; voting_system: string;
      candidates: { id: number; name: string }[]; start_time: number; end_time: number;
      confirmed?: boolean;
    }) => {
      if (!confirmed) {
        return {
          error: 'Confirmation required. Set confirmed=true to create this proposal. A proposal fee will be charged.',
          community_id, content_id, strategy, voting_system, candidates, start_time, end_time,
        };
      }
      if (community_id === undefined) return { error: 'community_id is required' };
      if (!content_id) return { error: 'content_id is required (from Gov API)' };
      if (!strategy) return { error: 'strategy is required' };
      if (!voting_system) return { error: 'voting_system is required' };
      if (!Array.isArray(candidates) || candidates.length < 2) {
        return { error: 'candidates must have at least 2 options' };
      }
      if (!start_time || !end_time) return { error: 'start_time and end_time are required (unix seconds)' };
      if (end_time <= start_time) return { error: 'end_time must be after start_time' };

      try {
        // Look up community to get proposal fee
        const { rows: communities } = await getTableRows(rpcEndpoint, {
          code: GOV_CONTRACT, scope: GOV_CONTRACT, table: 'communities',
          lower_bound: community_id, upper_bound: community_id, limit: 1,
        });

        if (communities.length === 0) {
          return { error: `Community #${community_id} not found` };
        }

        const community = communities[0];
        const fee = community.proposalFee;

        if (!fee || !fee.quantity || !fee.contract) {
          return { error: 'Could not determine proposal fee for this community' };
        }

        // Validate strategy is allowed
        if (!community.strategies.includes(strategy)) {
          return {
            error: `Strategy "${strategy}" not allowed for this community. Allowed: ${community.strategies.join(', ')}`,
          };
        }

        // Validate voting system is allowed
        if (!community.votingSystems.includes(voting_system)) {
          return {
            error: `Voting system "${voting_system}" not allowed. Allowed: ${community.votingSystems.join(', ')}`,
          };
        }

        const { api: eosApi, account, permission } = await getGovSession();

        // Build transaction: fee transfer + postprop
        const result = await eosApi.transact({
          actions: [
            // 1. Pay proposal fee
            {
              account: fee.contract,
              name: 'transfer',
              authorization: [{ actor: account, permission }],
              data: {
                from: account,
                to: GOV_CONTRACT,
                quantity: fee.quantity,
                memo: `proposal fee for community ${community_id}`,
              },
            },
            // 2. Post the proposal
            {
              account: GOV_CONTRACT,
              name: 'postprop',
              authorization: [{ actor: account, permission }],
              data: {
                author: account,
                communityId: community_id,
                content: content_id,
                strategy,
                votingSystem: voting_system,
                candidates: candidates.map(c => ({ id: c.id, name: c.name })),
                startTime: start_time,
                endTime: end_time,
                approve: '',
              },
            },
          ],
        }, { blocksBehind: 3, expireSeconds: 30 });

        return {
          transaction_id: result.transaction_id || result.processed?.id,
          action: 'post_proposal',
          author: account,
          community_id,
          community_name: community.name,
          content_id,
          fee_paid: fee.quantity,
          candidates,
          start_time: formatTimestamp(start_time),
          end_time: formatTimestamp(end_time),
          note: 'Proposal created. It will appear on the governance dashboard after admin approval.',
        };
      } catch (err: any) {
        return { error: `Failed to create proposal: ${err.message}` };
      }
    },
  });
}
