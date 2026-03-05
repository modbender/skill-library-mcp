# NEAR Intents Skill — Release Notes

## Version 2.0.0 (2026-02-15) — Production Release 🎉

**Status**: ✅ Production Ready

### 🛡️ Critical Safety Features

#### Mandatory Refund Address Protection
- **NEW**: `refundAddress` parameter for cross-chain swaps
- **Validation**: Automatic detection when origin is not NEAR
- **Error Handling**: Clear, educational error messages if refund address is missing
- **User Safety**: Prevents permanent fund loss on failed cross-chain swaps

**Why this matters**: When swapping from chains like Base, Arbitrum, Ethereum, or Bitcoin to NEAR (or any destination), if the swap fails, tokens are automatically refunded to the `refundAddress` on the origin chain. Using the wrong address or skipping this parameter could result in **permanent fund loss**.

**Example Error Message**:
```
⚠️ CRITICAL: Cross-chain swap from base:USDC requires a refund address!

If the swap fails, your tokens will be refunded to this address on BASE.
Please provide your BASE wallet address using the 'refundAddress' parameter.

Example:
  refundAddress: '0x...'  // Your BASE address

This is required for your fund safety - never skip this!
```

### 🔧 Technical Improvements

- **Full 1Click SDK Integration**: Updated to use official `@defuse-protocol/one-click-sdk-typescript` v0.1.1
- **Enhanced Token Map**: Added ETH support for NEAR, Base, and Arbitrum
- **Better Chain Detection**: Automatic origin chain detection for validation
- **Improved Error Messages**: Context-aware errors with actionable suggestions
- **TypeScript Types**: Proper interfaces for all parameters

### 📚 Documentation Overhaul

#### SKILL.md
- Added "⚠️ CRITICAL: Refund Address Safety" section
- Updated all cross-chain examples to include `refundAddress`
- Marked parameter importance in the API reference table
- Added comprehensive safety warnings

#### AI-AGENT-GUIDE.md
- New section: "⚠️ CRITICAL: Refund Address for Cross-Chain Swaps"
- Example conversation flows for agents
- Updated all workflows to demonstrate proper refund address collection
- Made refund address check #1 priority in agent tips

#### TOKENS.md
- Added ETH token entries for multiple chains
- Clarified Rainbow Bridge vs. OMFT tokens
- Enhanced decimal reference table

#### README.md
- Complete rewrite for v2.0.0
- Quick start guide
- Safety warnings prominently displayed
- Version history and changelog

### 🌐 Blockchain Support

**Fully Tested**:
- ✅ NEAR Protocol (native and cross-chain)
- ✅ Base (USDC, ETH)
- ✅ Arbitrum (USDC, ARB, ETH)
- ✅ Ethereum (ETH, USDC)
- ✅ Solana (SOL, USDC)

**Supported (via 1Click SDK)**:
- Bitcoin, Dogecoin, Litecoin, Zcash (native only)
- BSC, Gnosis, Optimism, Aptos, Starknet

### 🎯 API Changes

#### New Parameter: `refundAddress`

```typescript
interface ExecuteIntentParams {
  assetIn: string;
  assetOut: string;
  amount: string;
  recipient?: string;
  refundAddress?: string;  // ⚠️ REQUIRED for non-NEAR origins
  mode?: 'auto' | 'manual';
  swapType?: 'EXACT_INPUT' | 'EXACT_OUTPUT';
}
```

**Behavior**:
- **NEAR origin** → `refundAddress` optional (defaults to NEAR account)
- **Non-NEAR origin** → `refundAddress` **REQUIRED** or throws error
- **Validation**: Automatic checking based on `assetIn` format

### 🧪 Testing

- Unit tests passing
- Integration tests with live 1Click API
- Manual testing of cross-chain swaps (NEAR → Base, Base → NEAR)
- Error handling validated

### 📦 Package Contents

**Core Files**:
- `index.ts` — Main entry point with `executeIntent()`
- `package.json` — v2.0.0 metadata
- `manifest.json` — OpenClaw skill manifest
- `.env.example` — Configuration template

**Documentation**:
- `README.md` — Quick start and overview
- `SKILL.md` — Primary AI agent reference
- `AI-AGENT-GUIDE.md` — Detailed workflow guide
- `TOKENS.md` — Token reference with decimals
- `USAGE_GUIDE.md` — Common patterns
- `INSTALL.md` — Setup instructions
- `RELEASE_NOTES.md` — This file

**Examples**:
- `lib-1click/` — Step-by-step SDK examples
- `test-*.ts` — Test scripts for various scenarios

**Configuration**:
- `.gitignore` — Excludes sensitive files
- `tsconfig.json` — TypeScript configuration
- `jest.config.js` — Test configuration

### ⚠️ Breaking Changes from v1.0.0

1. **`refundAddress` is now mandatory for cross-chain swaps**
   - v1.0.0: Optional, defaulted to NEAR account (unsafe)
   - v2.0.0: Required for non-NEAR origins, throws error if missing

2. **Error messages are more verbose**
   - v1.0.0: Generic errors
   - v2.0.0: Educational, context-aware errors

### 🔄 Migration Guide (v1.0.0 → v2.0.0)

**If you were doing NEAR-origin swaps**: No changes needed
```typescript
// Still works
executeIntent({
  assetIn: 'NEAR',
  assetOut: 'base:USDC',
  amount: '1.0',
  recipient: '0x...',
});
```

**If you were doing cross-chain swaps**: Add `refundAddress`
```typescript
// v1.0.0 (would fail silently or use wrong address)
executeIntent({
  assetIn: 'base:USDC',
  assetOut: 'NEAR',
  amount: '0.5',
  recipient: 'user.near',
  mode: 'manual',
});

// v2.0.0 (safe, requires user's Base address)
executeIntent({
  assetIn: 'base:USDC',
  assetOut: 'NEAR',
  amount: '0.5',
  recipient: 'user.near',
  refundAddress: '0xUserBaseAddress',  // NEW: Required!
  mode: 'manual',
});
```

### 🎓 Agent Implementation Guidelines

For AI agents integrating this skill:

1. **Always ask for refund address** when origin is not NEAR
2. **Explain why** to the user: "For refunds if the swap fails"
3. **Verify it's their address**: "What's YOUR [chain] wallet address?"
4. **Never assume or infer** the refund address from context

**Example Flow**:
```
User: "Swap 0.5 USDC from Base to NEAR"
Agent: "Got it! What's your Base wallet address? (This is where 
        refunds will go if the swap fails)"
User: "0x123..."
Agent: [Generates quote with refundAddress: '0x123...']
```

### 🐛 Bug Fixes

- Fixed token resolution for ETH on multiple chains
- Corrected decimal handling for EXACT_OUTPUT swaps
- Improved error propagation from 1Click API
- Fixed status polling timeout handling

### 🚀 Performance Improvements

- Reduced unnecessary API calls
- Optimized token map lookups
- Better async/await patterns
- Cleaner error handling flow

### 📊 Statistics

- **Total Blockchains**: 14+
- **Total Tokens**: 140+ (via 1Click API)
- **Lines of Code**: ~500 (main) + 1000+ (examples/tests)
- **Documentation**: 5 comprehensive files
- **Test Coverage**: Unit + Integration tests

### 🙏 Acknowledgments

- **NEAR Intents Team** for the 1Click SDK
- **Defuse Protocol** for the infrastructure
- **OpenClaw Community** for feedback and testing

### 🔗 Resources

- **1Click SDK**: https://github.com/defuse-protocol/one-click-sdk-typescript
- **NEAR Intents Docs**: https://docs.near-intents.org
- **Partners Program**: https://partners.near-intents.org
- **OpenClaw**: https://openclaw.ai
- **Clawhub**: https://clawhub.com

---

## Version 1.0.0 (2026-02-14) — Initial Release

### Features
- Basic 1Click SDK integration
- Support for major chains (NEAR, Base, Arbitrum, Ethereum, Solana)
- Auto and manual swap modes
- Token map for common assets
- Basic documentation

### Known Issues
- Refund address safety not enforced (fixed in v2.0.0)
- Limited error messages (fixed in v2.0.0)
- Missing ETH token entries (fixed in v2.0.0)

---

**Current Version**: v2.0.0 (Production)
**Release Date**: February 15, 2026
**Status**: ✅ Production Ready
**License**: MIT
