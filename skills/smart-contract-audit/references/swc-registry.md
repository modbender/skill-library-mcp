# SWC Registry — Smart Contract Weakness Classification

Standard taxonomy for tagging audit findings. Use SWC IDs in reports for standardized vulnerability classification.

## Classification Table

| SWC ID | Title | Severity | Our Category |
|--------|-------|----------|-------------|
| SWC-100 | Function Default Visibility | Medium | Access Control |
| SWC-101 | Integer Overflow and Underflow | High | Logic/Math |
| SWC-102 | Outdated Compiler Version | Info | Informational |
| SWC-103 | Floating Pragma | Info | Informational |
| SWC-104 | Unchecked Call Return Value | Medium | Logic/Edge Cases |
| SWC-105 | Unprotected Ether Withdrawal | Critical | Access Control |
| SWC-106 | Unprotected SELFDESTRUCT | Critical | Access Control |
| SWC-107 | Reentrancy | High | Reentrancy |
| SWC-108 | State Variable Default Visibility | Medium | Access Control |
| SWC-109 | Uninitialized Storage Pointer | High | Logic/Edge Cases |
| SWC-110 | Assert Violation | Medium | Logic/Edge Cases |
| SWC-111 | Use of Deprecated Functions | Info | Informational |
| SWC-112 | Delegatecall to Untrusted Callee | Critical | Access Control |
| SWC-113 | DoS with Failed Call | Medium | Gas/DoS |
| SWC-114 | Transaction Order Dependence | Medium | Flash Loan/Economic |
| SWC-115 | Authorization through tx.origin | High | Access Control |
| SWC-116 | Block values as a proxy for time | Low | Logic/Edge Cases |
| SWC-117 | Signature Malleability | Medium | Logic/Edge Cases |
| SWC-118 | Incorrect Constructor Name | Critical | Access Control |
| SWC-119 | Shadowing State Variables | Medium | Logic/Edge Cases |
| SWC-120 | Weak Sources of Randomness | High | Oracle/Price |
| SWC-121 | Missing Protection against Signature Replay | High | Logic/Edge Cases |
| SWC-122 | Lack of Proper Signature Verification | High | Access Control |
| SWC-123 | Requirement Violation | Medium | Logic/Edge Cases |
| SWC-124 | Write to Arbitrary Storage Location | Critical | Access Control |
| SWC-125 | Incorrect Inheritance Order | Medium | Logic/Edge Cases |
| SWC-126 | Insufficient Gas Griefing | Medium | Gas/DoS |
| SWC-127 | Arbitrary Jump with Function Type Variable | Critical | Logic/Edge Cases |
| SWC-128 | DoS With Block Gas Limit | Medium | Gas/DoS |
| SWC-129 | Typographical Error | Low | Logic/Edge Cases |
| SWC-130 | Right-To-Left-Override Control Character | Medium | Logic/Edge Cases |
| SWC-131 | Presence of Unused Variables | Info | Informational |
| SWC-132 | Unexpected Ether balance | Medium | Logic/Edge Cases |
| SWC-133 | Hash Collisions With Multiple Variable Length Arguments | Medium | Logic/Edge Cases |
| SWC-134 | Message call with hardcoded gas amount | Low | Gas/DoS |
| SWC-135 | Code With No Effects | Info | Informational |
| SWC-136 | Unencrypted Private Data On-Chain | Info | Informational |

## Key SWCs for DeFi Audits

### Critical Attack Vectors
- **SWC-107 (Reentrancy):** Check all external calls for CEI violations. Includes cross-contract and read-only reentrancy.
- **SWC-105 (Unprotected Withdrawal):** Missing access control on fund-transfer functions.
- **SWC-112 (Delegatecall):** Proxy patterns, diamond proxies — verify implementation trust.
- **SWC-114 (Front-running/MEV):** Sandwich attacks, oracle manipulation, governance flash loans.

### Math & Logic
- **SWC-101 (Overflow/Underflow):** Pre-0.8 contracts or `unchecked` blocks. Also covers precision loss from division-before-multiplication.
- **SWC-104 (Unchecked Return):** ERC20 `approve`/`transfer` return values, low-level `call` results.

### Access Control
- **SWC-100/108 (Visibility):** Default visibility issues. Check all functions for correct access modifiers.
- **SWC-115 (tx.origin):** Never use for authorization.

### DoS
- **SWC-113 (Failed Call DoS):** Push patterns where one failed transfer blocks all.
- **SWC-128 (Block Gas Limit):** Unbounded loops over arrays.

## Usage in Reports

Tag findings like:
```
**SWC Classification:** SWC-107 (Reentrancy)
```

Multiple SWCs can apply to a single finding (e.g., reentrancy + unchecked return).
