# NEAR Airdrop Hunter Skill

Discover and claim NEAR airdrops.

## Installation

The skill is installed in `~/.openclaw/skills/near-airdrop-hunter/`

## Usage

### Discover Active Airdrops

```bash
node scripts/airdrop.js discover
```

Filter by platform:
```bash
node scripts/airdrop.js discover aurora
```

### Check Eligibility

```bash
node scripts/airdrop.js check myaccount.near aurora
```

### Claim an Airdrop

```bash
node scripts/airdrop.js claim myaccount.near aurora
```

### List Claimed Airdrops

```bash
node scripts/airdrop.js list
```

### Track Stats

```bash
node scripts/airdrop.js track
```

## Notes

- Airdrop APIs vary by protocol
- Visit the provided URLs to check eligibility and claim
- Always verify airdrop legitimacy before participating

## Available Airdrops

- aurora: Aurora airdrops
- ref: Ref Finance airdrops
- metapool: Meta Pool airdrops

## License

MIT
