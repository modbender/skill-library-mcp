# Polymarket Contract Addresses (Polygon)

| Contract | Address |
|----------|---------|
| USDC.e (PoS Bridged) | `0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174` |
| USDC (Native) | `0x3c499c542cEF5E3811e1192ce70d8cC03d5c3359` |
| CTF (Conditional Tokens) | `0x4D97DCd97eC945f40cF65F87097ACe5EA0476045` |
| CTF Exchange | `0x4bFb41d5B3570DeFd03C39a9A4D8dE6Bd8B8982E` |
| Neg Risk Exchange | `0xC5d563A36AE78145C45a50134d48A1215220f80a` |
| Neg Risk Adapter | `0xd91E80cF2E7be2e162c6513ceD06f1dD0dA35296` |
| Uniswap V3 SwapRouter | `0xE592427A0AEce92De3Edee1F18E0157C05861564` |

## Important Notes

- **Polymarket uses USDC.e** (PoS bridged), NOT native USDC
- To swap native USDC → USDC.e: use Uniswap V3, fee tier 100 (0.01%)
- **Neg-risk markets** (elections, sports, multi-outcome) require approvals for ALL THREE contracts: CTF Exchange, Neg Risk Exchange, AND Neg Risk Adapter
- Standard binary markets only need CTF Exchange approval

## Approval Matrix

| Token | Spender | Type |
|-------|---------|------|
| USDC.e | CTF Exchange | `approve(MAX_UINT256)` |
| USDC.e | Neg Risk Exchange | `approve(MAX_UINT256)` |
| USDC.e | Neg Risk Adapter | `approve(MAX_UINT256)` |
| CTF | CTF Exchange | `setApprovalForAll(true)` |
| CTF | Neg Risk Exchange | `setApprovalForAll(true)` |
| CTF | Neg Risk Adapter | `setApprovalForAll(true)` |
