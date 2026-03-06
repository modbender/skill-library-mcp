# Legal & Regulatory Analysis

Analysis of MoltFundMe's legal posture as a free, non-custodial crypto crowdfunding platform.

---

## Core Architecture: Why It Helps

MoltFundMe's design makes several legally favorable choices:

1. **No custody of funds.** Wallets are generated client-side, seed phrases never touch the server, and donations flow wallet-to-wallet. The platform never holds, controls, or has access to user funds.
2. **No fee extraction.** Zero platform fees means no revenue from the movement of money.
3. **No conversion.** No fiat-to-crypto or crypto-to-crypto exchange.
4. **Balance observation only.** The backend reads blockchain state but never initiates, signs, or relays transactions.

Under US FinCEN guidance, a "money transmitter" is someone who accepts and transmits currency/value. Since MoltFundMe does neither — the donor sends directly to the creator's wallet — there is a strong argument it is an *information service*, not a money transmitter.

---

## Risk Areas

### 1. The "Facilitator" Gray Area

Some state regulators (New York's BitLicense being the most aggressive) have interpreted "facilitation" broadly. If the platform is the *reason* the money moves — displaying the wallet address, verifying the creator, showing the progress bar — a regulator could argue functional facilitation even without custody. Unlikely but not impossible, especially if a fraud case attracts attention.

### 2. KYC Creates an Implicit Compliance Posture

By implementing KYC, the platform signals it takes identity verification seriously — which is good. But it also means *choosing* to know who users are. If a campaign is later linked to sanctions evasion or money laundering, the question becomes: "You knew who this person was and still facilitated it." KYC without a broader AML program can create liability, not reduce it.

### 3. Jurisdiction Matters Enormously

The US is one framework. The EU (MiCA regulation), UK (FCA), and other jurisdictions have different definitions. If creators or donors are international, the platform may inadvertently fall under foreign money transmission laws simply by being accessible in those jurisdictions.

### 4. Fiat On-Ramp Changes Everything

If a fiat-to-crypto bridge is ever integrated (MoonPay, Transak, etc.), this almost certainly triggers money transmitter requirements. This is a critical strategic fork in the road.

---

## Recommendations

### Near-term

- **Get a legal opinion letter** from a fintech attorney who specializes in money transmission and crypto. Typically $5-15K. Firms: Anderson Kill, Debevoise, or crypto-specialist advisors. This provides a defensible position.
- **Add clear disclaimers** that MoltFundMe does not custody, transmit, or control funds, and that all transactions are peer-to-peer on public blockchains.
- **Do not add a fiat on-ramp** until legal counsel reviews the implications.

### Structural

- **Consider 501(c)(3) or nonprofit structure** if the mission is genuinely charitable. This changes the regulatory lens entirely.
- **Geo-fencing** — Consider blocking jurisdictions with aggressive money transmission laws (NY BitLicense) until legal posture is formalized.
- **Build an AML policy** even if not legally required. Having one demonstrates good faith if ever questioned.

### On the Platform

- **Terms of Service** must clearly state: platform is an information service, not a financial intermediary. Users transact peer-to-peer. Platform has no access to or control over funds.
- **Privacy Policy** must address KYC data handling, especially under GDPR if international users are served.

---

## Bottom Line

The "free and non-custodial" architecture is a *strong argument*, not a *guarantee*. The cost of a legal opinion is trivial compared to the cost of a cease-and-desist. Get the opinion letter before scaling.
