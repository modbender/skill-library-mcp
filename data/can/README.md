# CAN: automate naming

One bash command. Append-only log. Three columns.

```bash
echo -e "$(date +%s%3N)\t$(sha256sum file | awk '{print $1}')\tfile.txt" >> ~/.can/index.tsv
```

That's it. Everything below is why this specific combination doesn't exist yet.

## 3 columns, all the way down

```
WHEN    millisecond timestamp    when you saw it
WHERE   sha256 hash              what it actually was
WHAT    free text                what you called it
```

WHEN + WHERE together give you: this exact content existed at this exact moment. Verifiable. Reproducible. No external dependency.

## What already exists (and what doesn't)

**GIT** does content-addressing. SHA hashes for objects, merkle tree for history. But:
- No timestamp-first indexing. GIT logs time but doesn't index by it.
- No human name column. Filenames live in tree objects, not in the content address.
- Requires `.git` init, working tree, staging. Not one command.

**IPFS** does content-addressing for networks. But:
- No clock. CIDs are timeless. You can't ask "what did I have at 3pm Tuesday?"
- No local-first story. Needs a daemon. Needs peers. Doesn't work air-gapped.
- Dead project momentum. Filecoin pivoted.

**NDN** (Named Data Networking, Van Jacobson 2006) names data instead of machines. Jacobson wrote TCP/IP's congestion control — then spent 20 years watching location-based routing fail at scale and designed the alternative. NDN uses three tables:

```
PIT    "I want this data"        (pending interest)
FIB    "Try looking over there"  (forwarding info)
CS     "I already have it"       (content store)
```

Every node caches. Every request is a name lookup. Every response is hash-verified. The network gets faster with use. 

But:
- No rejection log. NDN can say "I have it" and "I want it." It can't say "it's fake."
- Never shipped at scale. Stayed academic.

**RINA** (Recursive InterNetwork Architecture, John Day 2008) says networking is one pattern at every scope. Day was on the original ARPANET — then argued the TCP/IP layer model was an accident of history, not good design. His insight: the way two processes talk on one machine is the same pattern as two continents talking across an ocean. Same operations, different scope. 

But:
- Zero adoption. The insight is correct. The engineering never shipped.

**Conventional logging** does timestamps + messages. But:
- No content hash. Can't verify what was logged hasn't changed.

**SQLite / any DB** can store all three columns. But:
- Nobody does. No standard schema for timestamp + hash + name.

The gap: timestamp-first + content-hash + human-name in one append operation with zero dependencies. Plus a rejection log. Plus recursive scoping. Each piece exists somewhere in research or in production. The combination doesn't ship as a single pattern.

## CAN and NOT

Every verification has two outcomes. Both are useful.

```
CAN:  hash matches → cache it, trust the sender a little more
NOT:  hash doesn't match → reject it, trust the sender a little less
```

CAN is NDN's three tables plus the fourth one NDN never built:

```
NDN PIT  "I want this"       → CAN: search the index
NDN FIB  "Try over there"    → CAN: ask peers who have that hash
NDN CS   "I have it"         → CAN: local store, hash-verified
NDN ???                      → NOT: rejection log — "I checked, it's fake"
```

The NOT log is what makes the network honest. Every NOT warns future lookups: don't trust that source for that hash. Trust goes down. NOT is signal, not failure.

## Route to trust, on any transport

CAN takes RINA's insight: same pattern at every scope.

```
My machine:        WHEN + WHERE + WHAT    (my index)
Me + you:          WHEN + WHERE + WHAT    (shared entries)
Me + you + 1000:   WHEN + WHERE + WHAT    (same three columns, bigger scope)
```

No new protocol at each layer. No TCP at one level and HTTP at another. Same three columns, same CAN/NOT verification, at every scope.

Routing emerges from verification:

```
Agent A stamps a file       → CAN entry exists
Agent B wants that hash     → checks local first (zero network if found)
Not local                   → asks peers: "who has this hash?"
Peer responds               → B hashes on arrival
Hash matches                → CAN. B caches. B is now a source too.
Hash doesn't match          → NOT. B rejects. B logs the failed source.
Agent C wants same hash     → TWO verified sources now (A and B)
```

Every successful CAN makes the network faster. Every NOT makes it more honest. No coordinator. No registry. No DNS lookup. The network IS the trust log.

## Trust

Trust is computed locally. Per-agent. Your log, your weights.

```
trust = (CAN_count × recency) + (vouch_count × voucher_weight) - (NOT_count × severity)
```

Accurate CAN → trust up. Correct NOT (caught a fake) → trust up. YOU get NOT'd by others → trust down. No ceremony. No certificate authority. The log is the reputation.

## What TCP/IP and blockchains don't do

```
TCP/IP:      routes packets       delivers bytes, doesn't verify content
BLOCKCHAIN:  routes consensus     verifies globally, burns energy
CAN:         routes verification  verifies locally, burns nothing
```

TCP/IP needs TLS + certificate authorities + HTTPS stacked on top to answer "is this what I asked for?" CAN answers it in one hash comparison.

Blockchains burn energy for global agreement. CAN doesn't need global agreement. Your log is yours. When we share, we verify. CAN or NOT. No mining. Just LOG.

## Use cases

**1. AI agent audit trail**

Agent calls an API via MCP. Gets a result. Hashes it, timestamps it, logs the tool name.

```bash
RESULT=$(curl -s api.example.com/data)
WHEN=$(date +%s%3N)
WHERE=$(echo -n "$RESULT" | sha256sum | awk '{print $1}')
echo -e "$WHEN\t$WHERE\tapi.example.com/data" >> ~/.can/index.tsv
echo -n "$RESULT" > ~/.can/store/$WHERE
```

Six lines. Verifiable cache. Audit trail. No framework. The MCP server doesn't know you're doing this. You just stamped what came through the pipe.

**2. Config/deploy verification**

```bash
# before deploy
echo -e "$(date +%s%3N)\t$(sha256sum config.yml | awk '{print $1}')\tconfig.yml PRE-DEPLOY" >> ~/.can/index.tsv

# after deploy, on target
echo -e "$(date +%s%3N)\t$(sha256sum config.yml | awk '{print $1}')\tconfig.yml POST-DEPLOY" >> ~/.can/index.tsv
```

Diff the hashes. Same = clean deploy. Different = something touched it.

**3. Multi-agent deduplication**

Ten agents fetch the same API response. All ten hash it. Same hash = store once. Timestamps say who got it first.

**4. Personal file integrity**

50,000 photos, half duplicates with different filenames. Hash them all. Same hash = same file. Timestamp says when you first saw each one.

## What CAN is not

- **Not a database.** Append-only log. TSV is the teaching format. SQLite for scale. Same schema.
- **Not a network protocol.** CAN doesn't move bytes. Pick any transport. CAN verifies what arrives.
- **Not a replacement for Git.** Git does branching and merging. CAN does naming and verification.
- **Not a blockchain.** No consensus. No global state. No mining. Your log is yours.

## Find by any column

Know the time? Search WHEN. Know the hash? Search WHERE. Know the name? Search WHAT. Two columns narrow fast. Three columns find exactly.

Every other system searches one axis. Filesystem: path. Git: commit or hash. Database: whatever you indexed. CAN indexes all three by default because all three are always present.

## Try it

```bash
mkdir -p ~/.can
echo -e "WHEN\tWHERE\tWHAT" > ~/.can/index.tsv

# stamp something
echo -e "$(date +%s%3N)\t$(sha256sum /etc/hostname | awk '{print $1}')\thostname" >> ~/.can/index.tsv

# check it
cat ~/.can/index.tsv
```

If you see a use for it, use it. If not, don't. It's one bash command either way.
