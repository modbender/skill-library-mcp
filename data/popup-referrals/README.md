# ClawHub Skill — PopUp Referrals

This directory contains the ClawHub skill definition for the PopUp referral dashboard.

**Scope:** Read-only access to referral data (code, earnings, referred vendor status). Does not send messages, contact vendors, or share links autonomously.

## Publishing

### 1. Authenticate (one-time)

```bash
npx clawhub@latest auth login --token "clh_..." --no-browser --registry "https://www.clawhub.ai/"
```

Replace `clh_...` with your actual CLI token.

### 2. Publish

```bash
npx clawhub@latest publish ./clawhub-skill \
  --slug popup-referrals \
  --name "PopUp Referrals" \
  --version 1.1.0 \
  --changelog "v1.1.0: Improved skill description and metadata" \
  --tags "referrals,earnings,vendors,popup"
```

### 3. Verify

```bash
npx clawhub@latest info popup-referrals
```

## Updating

```bash
npx clawhub@latest publish ./clawhub-skill \
  --slug popup-referrals \
  --name "PopUp Referrals" \
  --version 1.2.0 \
  --changelog "Description of changes" \
  --tags "referrals,earnings,vendors,popup"
```
