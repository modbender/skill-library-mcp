/**
 * Quick integration test for governance skill read-only tools.
 * Calls mainnet gov contract directly — no signing needed.
 *
 * Usage: node test-read.mjs
 */

const RPC = 'https://proton.eosusa.io';
const GOV_API = 'https://gov.api.xprnetwork.org/api/v1/proposals';
const GOV = 'gov';

async function getTableRows(opts) {
  const resp = await fetch(`${RPC}/v1/chain/get_table_rows`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      json: true,
      code: opts.code,
      scope: opts.scope,
      table: opts.table,
      lower_bound: opts.lower_bound,
      upper_bound: opts.upper_bound,
      limit: opts.limit || 100,
      key_type: opts.key_type,
      index_position: opts.index_position,
      reverse: opts.reverse || false,
    }),
  });
  const data = await resp.json();
  return data;
}

let passed = 0;
let failed = 0;

function assert(condition, msg) {
  if (condition) { passed++; console.log(`  PASS: ${msg}`); }
  else { failed++; console.log(`  FAIL: ${msg}`); }
}

// ── Test 1: gov_list_communities ──
console.log('\n--- gov_list_communities ---');
const { rows: communities } = await getTableRows({ code: GOV, scope: GOV, table: 'communities', limit: 50 });
assert(communities.length >= 6, `Found ${communities.length} communities (expected >= 6)`);

const xprCommunity = communities.find(c => c.name === 'XPR Network');
assert(!!xprCommunity, 'XPR Network community exists');
assert(xprCommunity.id === 3, `XPR Network id = 3 (got ${xprCommunity.id})`);
assert(xprCommunity.strategies.includes('xpr-unstaked-and-staked-balances'), 'Has XPR staking strategy');
assert(xprCommunity.proposalFee?.quantity === '20000.0000 XPR', `Fee = 20000 XPR (got ${xprCommunity.proposalFee?.quantity})`);
assert(xprCommunity.proposalFee?.contract === 'eosio.token', 'Fee contract = eosio.token');
assert(xprCommunity.quorum === 300, `Quorum = 300 basis points (got ${xprCommunity.quorum})`);
assert(Array.isArray(xprCommunity.admins), 'Has admins array');

const loanCommunity = communities.find(c => c.name === 'LOAN Protocol');
assert(!!loanCommunity, 'LOAN Protocol community exists');
assert(loanCommunity.proposalFee?.contract === 'loan.token', 'LOAN fee contract = loan.token');

const dogeCommunity = communities.find(c => c.name === 'D.O.G.E. Community');
assert(!!dogeCommunity, 'D.O.G.E. community exists');

// ── Test 2: gov_get_config ──
console.log('\n--- gov_get_config ---');
const { rows: globals } = await getTableRows({ code: GOV, scope: GOV, table: 'govglobal', limit: 1 });
assert(globals.length === 1, 'govglobal singleton exists');
assert(globals[0].isPaused === 0, 'Governance is not paused');
assert(globals[0].proposalId >= 300, `${globals[0].proposalId} proposals (>= 300)`);
assert(globals[0].voteId >= 17000, `${globals[0].voteId} votes (>= 17000)`);
assert(globals[0].communityId >= 9, `Next community ID >= 9 (got ${globals[0].communityId})`);

// ── Test 3: gov_list_proposals ──
console.log('\n--- gov_list_proposals (latest 10) ---');
const { rows: proposals } = await getTableRows({ code: GOV, scope: GOV, table: 'proposals', limit: 10, reverse: true });
assert(proposals.length === 10, `Got 10 proposals (got ${proposals.length})`);
assert(proposals[0].id > proposals[9].id, 'Reverse order (newest first)');

const latestProp = proposals[0];
assert(typeof latestProp.author === 'string' && latestProp.author.length > 0, `Author = ${latestProp.author}`);
assert(typeof latestProp.communityId === 'number', 'Has communityId');
assert(typeof latestProp.content === 'string' && latestProp.content.length > 0, `Content hash = ${latestProp.content}`);
assert(Array.isArray(latestProp.candidates), 'Has candidates array');
assert(latestProp.candidates.length >= 2, `${latestProp.candidates.length} candidates`);
assert(typeof latestProp.startTime === 'number', 'Has startTime');
assert(typeof latestProp.endTime === 'number', 'Has endTime');
assert(latestProp.endTime > latestProp.startTime, 'endTime > startTime');

// ── Test 4: gov_list_proposals filtered by community ──
console.log('\n--- gov_list_proposals (community 3 = XPR Network) ---');
const { rows: allProps } = await getTableRows({ code: GOV, scope: GOV, table: 'proposals', limit: 100, reverse: true });
const xprProps = allProps.filter(p => p.communityId === 3);
assert(xprProps.length > 0, `Found ${xprProps.length} XPR Network proposals`);
assert(xprProps.every(p => p.communityId === 3), 'All filtered to community 3');

// ── Test 5: gov_get_proposal (with Gov API) ──
console.log('\n--- gov_get_proposal (with Gov API title) ---');
const testProp = proposals[0];
const govResp = await fetch(`${GOV_API}/${testProp.content}`, {
  headers: { 'Accept': 'application/json' },
});
const govData = await govResp.json();
assert(typeof govData.title === 'string' && govData.title.length > 0, `Title = "${govData.title.slice(0, 60)}..."`);
assert(typeof govData.description === 'string' && govData.description.length > 0, `Description length = ${govData.description.length} chars`);
assert(typeof govData.tokenAmount === 'number', `Total votes = ${govData.tokenAmount}`);
assert(Array.isArray(govData.candidates), 'Gov API returns candidates');

// Verify candidate vote amounts
for (const c of govData.candidates) {
  assert(typeof c.tokenAmount === 'number', `Candidate "${c.name}" votes = ${c.tokenAmount}`);
}

// ── Test 6: gov_get_proposal (known proposal) ──
console.log('\n--- gov_get_proposal (specific proposal #298) ---');
const { rows: prop298 } = await getTableRows({ code: GOV, scope: GOV, table: 'proposals', lower_bound: 298, upper_bound: 298, limit: 1 });
assert(prop298.length === 1, 'Found proposal #298');
assert(prop298[0].communityId === 3, 'Proposal #298 is in XPR Network community');
assert(prop298[0].candidates.length >= 2, `Has ${prop298[0].candidates.length} candidates`);

const gov298 = await fetch(`${GOV_API}/${prop298[0].content}`).then(r => r.json());
assert(typeof gov298.title === 'string' && gov298.title.length > 0, `Title = "${gov298.title.slice(0, 60)}"`);

// ── Test 7: gov_get_votes (scan for recent votes) ──
console.log('\n--- gov_get_votes (scan recent votes) ---');
const { rows: recentVotes } = await getTableRows({ code: GOV, scope: GOV, table: 'votes', limit: 20, reverse: true });
assert(recentVotes.length > 0, `Got ${recentVotes.length} recent votes`);

const firstVote = recentVotes[0];
assert(typeof firstVote.voter === 'string', `Voter = ${firstVote.voter}`);
assert(typeof firstVote.communityId === 'number', 'Has communityId');
assert(typeof firstVote.proposalId === 'number', `ProposalId = ${firstVote.proposalId}`);
assert(Array.isArray(firstVote.winners), 'Has winners array');
assert(firstVote.winners.length > 0, `${firstVote.winners.length} winner selections`);
assert(typeof firstVote.winners[0].id === 'number', `Winner id = ${firstVote.winners[0].id}`);
assert(typeof firstVote.winners[0].weight === 'number', `Winner weight = ${firstVote.winners[0].weight}`);
assert(typeof firstVote.timestamp === 'number', 'Has timestamp');

// Filter votes for a specific proposal
const targetProposal = firstVote.proposalId;
const matchedVotes = recentVotes.filter(v => v.proposalId === targetProposal);
assert(matchedVotes.length > 0, `Found ${matchedVotes.length} votes for proposal #${targetProposal}`);
const totalWeight = matchedVotes.reduce((sum, v) => sum + v.winners.reduce((ws, w) => ws + w.weight, 0), 0);
assert(totalWeight > 0, `Total weight for proposal #${targetProposal} = ${totalWeight}`);

// ── Test 8: non-existent proposal returns empty ──
console.log('\n--- non-existent proposal ---');
const { rows: noProps } = await getTableRows({ code: GOV, scope: GOV, table: 'proposals', lower_bound: 999999, upper_bound: 999999, limit: 1 });
assert(noProps.length === 0, 'Non-existent proposal returns empty');

// ── Test 9: proposal status logic ──
console.log('\n--- proposal status logic ---');
const now = Math.floor(Date.now() / 1000);

function proposalStatus(p) {
  if (p.approve === 'Approved') return 'Approved';
  if (p.approve === 'Declined') return 'Declined';
  if (now < p.startTime) return 'Upcoming';
  if (now <= p.endTime) return 'Active';
  return 'Ended';
}

const approvedProps = allProps.filter(p => proposalStatus(p) === 'Approved');
assert(approvedProps.length > 0, `${approvedProps.length} approved proposals`);

const declinedProps = allProps.filter(p => proposalStatus(p) === 'Declined');
assert(declinedProps.length >= 0, `${declinedProps.length} declined proposals`);

// ── Test 10: community quorum math ──
console.log('\n--- community quorum math ---');
for (const c of communities) {
  const quorumPct = (c.quorum / 100).toFixed(2);
  assert(typeof c.quorum === 'number' && c.quorum >= 0, `${c.name}: quorum = ${quorumPct}%`);
}

// ── Summary ──
console.log(`\n${'='.repeat(40)}`);
console.log(`Results: ${passed} passed, ${failed} failed`);
process.exit(failed > 0 ? 1 : 0);
