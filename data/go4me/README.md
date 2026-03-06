<p align="center">
  <h1 align="center">🎯 Go4Me</h1>
  <p align="center">
    <strong>Send XCH to anyone using their Twitter handle</strong>
  </p>
  <p align="center">
    <em>Resolve Go4Me addresses and send Chia with a single command</em>
  </p>
</p>

<p align="center">
  <a href="https://opensource.org/licenses/MIT">
    <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT">
  </a>
  <a href="https://www.chia.net/">
    <img src="https://img.shields.io/badge/Blockchain-Chia-3AAC59.svg" alt="Chia Blockchain">
  </a>
  <a href="https://go4.me/">
    <img src="https://img.shields.io/badge/Platform-Go4Me-purple.svg" alt="Go4Me">
  </a>
  <a href="https://clawd.bot">
    <img src="https://img.shields.io/badge/Framework-Clawdbot-orange.svg" alt="Built for Clawdbot">
  </a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Commands-3-brightgreen.svg" alt="3 Commands">
  <img src="https://img.shields.io/badge/Dependency-sage--wallet-blue.svg" alt="Requires sage-wallet">
  <img src="https://img.shields.io/badge/Version-1.0.0-blue.svg" alt="Version">
</p>

---

## 🎯 Overview

**Go4Me** bridges Twitter identities to the Chia blockchain. Instead of asking someone for their XCH address, just send to their Twitter handle. The skill looks up their [Go4Me](https://go4.me/) profile, extracts their verified XCH address, and executes the transaction via [sage-wallet](https://clawdhub.com/Koba42Corp/sage-wallet).

---

## ✨ Features

<table>
<tr>
<td width="50%">

### 🔍 **Address Lookup**
- Resolve Twitter handles to XCH addresses
- Display user profile info
- View badge scores and stats
- Handle missing users gracefully

</td>
<td width="50%">

### 💸 **Send XCH**
- Send any amount to Twitter users
- Quick 1-mojo tips
- Confirmation before sending
- Full transaction details

</td>
</tr>
</table>

---

## 🚀 Commands

| Command | Description | Example |
|---------|-------------|---------|
| `/go4me lookup <user>` | Get user's XCH address and profile | `/go4me lookup @hoffmang` |
| `/go4me send <user> <amount>` | Send XCH to a user | `/go4me send @bramcohen 1 XCH` |
| `/go4me tip <user>` | Send 1 mojo tip | `/go4me tip @sage_wallet` |

---

## 💬 Natural Language

Just ask naturally:

- *"Send 1 XCH to @hoffmang"*
- *"Tip @sage_wallet"*
- *"What's @bramcohen's XCH address?"*
- *"Look up DracattusDev on Go4Me"*

---

## 📋 Example Output

### Lookup

```
$ /go4me lookup @DracattusDev

@DracattusDev on Go4Me
━━━━━━━━━━━━━━━━━━━━━━
Name:        🌱Drac 🍊
XCH Address: xch1rvgc3naytvzhv4lxhzphrdr2fzj2ka340tdj8fflt4872t2wqveq9lwz7t
Badge Score: 220
Copies Sold: 49
```

### Send

```
$ /go4me send @hoffmang 0.001 XCH

Send 0.001 XCH to @hoffmang (Gene Hoffman)?
Address: xch1abc...xyz
[Yes] [No]

> Yes

✓ Transaction submitted
  Amount: 0.001 XCH (1,000,000,000 mojos)
  To: xch1abc...xyz
  Fee: 0
```

---

## 📦 Dependencies

| Skill | Purpose |
|-------|---------|
| [sage-wallet](https://clawdhub.com/Koba42Corp/sage-wallet) | XCH transaction execution |

Install sage-wallet first:
```
/skill install Koba42Corp/sage-wallet
```

---

## 💰 Amount Formats

The skill understands various amount formats:

| Input | Interpreted As |
|-------|----------------|
| `1` | 1 mojo |
| `1 mojo` | 1 mojo |
| `1000000000000` | 1 XCH |
| `0.001 XCH` | 1,000,000,000 mojos |
| `1 XCH` | 1,000,000,000,000 mojos |

---

## 🔧 How It Works

```
User: "Send 1 mojo to @hoffmang"
         │
         ▼
┌─────────────────────────┐
│ 1. Parse Twitter handle │
│    → "hoffmang"         │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│ 2. Fetch Go4Me page     │
│    GET hoffmang.go4.me  │
└───────────┬─────────────┘
            │
      ┌─────┴─────┐
      │   404?    │
      └─────┬─────┘
         No │ Yes → "User not found on Go4Me"
            ▼
┌─────────────────────────┐
│ 3. Extract from JSON:   │
│    • xchAddress         │
│    • fullName           │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│ 4. Confirm with user    │
│    [Yes] [No]           │
└───────────┬─────────────┘
            │
     User confirms
            │
            ▼
┌─────────────────────────┐
│ 5. sage-wallet send_xch │
└───────────┬─────────────┘
            │
            ▼
         ✓ Done
```

---

## 📊 Data Available

Go4Me profiles include:

| Field | Description |
|-------|-------------|
| `username` | Twitter handle |
| `fullName` | Display name |
| `xchAddress` | Verified Chia address |
| `description` | Bio text |
| `avatarUrl` | Profile image |
| `totalBadgeScore` | Achievement score |
| `rankCopiesSold` | NFT sales rank |

---

## ⚠️ Error Handling

| Condition | Response |
|-----------|----------|
| User not on Go4Me | "User @{username} not found on Go4Me" |
| Invalid address | "Invalid XCH address returned" |
| Insufficient balance | "Insufficient balance for this transaction" |
| Network error | "Failed to connect to Go4Me" |

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

## 🙏 Credits

- [Go4Me](https://go4.me/) — Twitter-to-XCH address resolution
- [Sage Wallet](https://github.com/xch-dev/sage) — Chia wallet RPC
- [Chia Network](https://www.chia.net/) — Blockchain infrastructure

---

<p align="center">
  <strong>Built by <a href="https://koba42.com">KOBA42 Corp</a></strong>
</p>
