#!/usr/bin/env python3
"""
wallet_commands.py — MeneseSDK wallet operations via dfx CLI

Usage:
    python3 wallet_commands.py addresses              # Get all 19 chain addresses
    python3 wallet_commands.py balance sol             # Check SOL balance
    python3 wallet_commands.py balance icp             # Check ICP balance
    python3 wallet_commands.py send sol 0.01 <addr>    # Send 0.01 SOL
    python3 wallet_commands.py send icp 1.5 <principal> # Send 1.5 ICP
    python3 wallet_commands.py send btc 0.001 <addr>   # Send BTC
    python3 wallet_commands.py send eth 0.01 <addr>    # Send ETH (requires EVM_RPCS config)
    python3 wallet_commands.py swap sol <input> <output> <amount> <slippage>  # Raydium swap

Calls MeneseSDK canister (urs2a-ziaaa-aaaad-aembq-cai) via dfx.
All address/balance queries are FREE. Sends cost $0.05 each. Swaps cost $0.075.

IMPORTANT: For EVM chains (ETH, ARB, BASE, etc.), you must provide your own
RPC endpoint. Configure EVM_RPCS below with your own URLs.

Tested: Feb 11, 2026
"""

import subprocess
import sys

CANISTER_ID = "urs2a-ziaaa-aaaad-aembq-cai"
NETWORK = "ic"  # "ic" for mainnet, "local" for local replica

# ── EVM RPC config ──────────────────────────────────────────────
# You MUST provide your own RPC endpoints for EVM operations.
# MeneseSDK does NOT manage EVM RPCs — this keeps costs low.
# Free public RPCs work for testing; use Alchemy/Infura for production.
EVM_RPCS = {
    "ethereum":  {"rpc": "https://eth.llamarpc.com",         "chain_id": 1},
    "arbitrum":  {"rpc": "https://arb1.arbitrum.io/rpc",     "chain_id": 42161},
    "base":      {"rpc": "https://mainnet.base.org",         "chain_id": 8453},
    "polygon":   {"rpc": "https://polygon-rpc.com",          "chain_id": 137},
    "bsc":       {"rpc": "https://bsc-dataseed1.binance.org","chain_id": 56},
    "optimism":  {"rpc": "https://mainnet.optimism.io",      "chain_id": 10},
}


def dfx_call(method: str, args: str = "()", is_query: bool = False) -> str:
    """Call a canister method via dfx and return the raw output."""
    cmd = [
        "dfx", "canister", "call",
        "--network", NETWORK,
        CANISTER_ID,
        method, args,
    ]
    if is_query:
        cmd.insert(3, "--query")

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if result.returncode != 0:
        return f"ERROR: {result.stderr.strip()}"
    return result.stdout.strip()


def get_addresses():
    """Get wallet addresses on all 19 chains."""
    print("Fetching addresses on all 19 chains...\n")

    # Call individual address functions — field names matter!
    # SolanaAddressInfo: .address
    # EvmAddressInfo: .evmAddress (NOT "address")
    # AddressInfo (BTC/LTC/Thor): .bech32Address (NOT Text)
    # SuiAddressInfo: .suiAddress
    # XrpAddressInfo: .classicAddress
    # TonAddressInfo: .nonBounceable (NOT "address")
    # CardanoAddressInfo: .bech32Address
    # AptosAddressInfo: .address
    # PubKeyInfo (NEAR): .implicitAccountId (NOT "accountId")
    # TronAddressInfo: .base58Address (NOT "base58")
    # CloakAddressInfo: .base58Address

    methods = [
        ("Solana",    "getMySolanaAddress"),
        ("EVM",       "getMyEvmAddress"),
        ("Bitcoin",   "getMyBitcoinAddress"),
        ("Litecoin",  "getMyLitecoinAddress"),
        ("SUI",       "getMySuiAddress"),
        ("XRP",       "getMyXrpAddress"),
        ("TON",       "getMyTonAddress"),
        ("Cardano",   "getMyCardanoAddress"),
        ("Aptos",     "getMyAptosAddress"),
        ("NEAR",      "getMyNearAddress"),
        ("Tron",      "getTronAddress"),
        ("CloakCoin", "getMyCloakAddress"),
        ("THORChain", "getMyThorAddress"),
    ]

    print("Your multi-chain wallet addresses:")
    print("=" * 60)
    for chain_name, method in methods:
        output = dfx_call(method)
        note = ""
        if chain_name == "EVM":
            note = " (same for ETH/ARB/BASE/POLY/BNB/OP)"
        print(f"  {chain_name:12s}: {output}{note}")
    print("=" * 60)


def get_balance(chain: str):
    """Check balance on a specific chain."""
    chain = chain.lower()

    if chain in ("sol", "solana"):
        output = dfx_call("getMySolanaBalance")
        print(f"SOL balance: {output}")
    elif chain == "icp":
        output = dfx_call("getICPBalance")
        print(f"ICP balance: {output}")
    elif chain == "xrp":
        output = dfx_call("getMyXrpBalance")
        print(f"XRP balance: {output}")
    elif chain == "sui":
        output = dfx_call("getMySuiBalance")
        print(f"SUI balance: {output}")
    elif chain in EVM_RPCS:
        # getMyEvmBalance takes RPC endpoint URL (not chain name!)
        rpc = EVM_RPCS[chain]["rpc"]
        output = dfx_call("getMyEvmBalance", f'("{rpc}")')
        print(f"{chain.upper()} balance: {output}")
    else:
        print(f"Unsupported chain: {chain}")
        print(f"Supported: sol, icp, xrp, sui, {', '.join(EVM_RPCS.keys())}")


def send_tokens(chain: str, amount: str, to_address: str):
    """Send tokens on a specific chain."""
    chain = chain.lower()

    if chain in ("sol", "solana"):
        lamports = int(float(amount) * 1e9)
        print(f"Sending {amount} SOL ({lamports} lamports) to {to_address}...")
        # sendSolTransaction returns Result<Text, Text> — ok = txHash
        output = dfx_call("sendSolTransaction", f'("{to_address}", {lamports})')

    elif chain == "icp":
        e8s = int(float(amount) * 1e8)
        print(f"Sending {amount} ICP ({e8s} e8s) to {to_address}...")
        # sendICP returns Result<SendICPResult, Text>
        #   SendICPResult = { amount, blockHeight, fee, from, to }
        output = dfx_call("sendICP", f'(principal "{to_address}", {e8s})')

    elif chain in ("btc", "bitcoin"):
        satoshis = int(float(amount) * 1e8)
        print(f"Sending {amount} BTC ({satoshis} satoshis) to {to_address}...")
        # sendBitcoin returns Result<SendResultBtcLtc, Text>
        #   SendResultBtcLtc = { txid, amount, fee, senderAddress, recipientAddress, note }
        output = dfx_call("sendBitcoin", f'("{to_address}", {satoshis})')

    elif chain in ("ltc", "litecoin"):
        litoshis = int(float(amount) * 1e8)
        print(f"Sending {amount} LTC ({litoshis} litoshis) to {to_address}...")
        # sendLitecoin returns Result<SendResult, Text> — NOT SendResultBtcLtc!
        #   SendResult = { txHash, senderAddress, note }
        output = dfx_call("sendLitecoin", f'("{to_address}", {litoshis})')

    elif chain in EVM_RPCS:
        # sendEvmNativeTokenAutonomous(to, valueWei:Nat, rpcEndpoint, chainId:Nat, ?quoteId)
        config = EVM_RPCS[chain]
        wei = int(float(amount) * 1e18)
        print(f"Sending {amount} on {chain} ({wei} wei) to {to_address}...")
        print(f"  RPC: {config['rpc']} | Chain ID: {config['chain_id']}")
        output = dfx_call(
            "sendEvmNativeTokenAutonomous",
            f'("{to_address}", {wei} : nat, "{config["rpc"]}", {config["chain_id"]} : nat, null)'
        )

    elif chain == "xrp":
        # sendXrpAutonomous(destAddress, amountXrp:Text, ?destinationTag)
        # Returns FLAT SendResultXrp (NOT a variant!)
        print(f"Sending {amount} XRP to {to_address}...")
        output = dfx_call("sendXrpAutonomous", f'("{to_address}", "{amount}", null)')

    elif chain == "sui":
        mist = int(float(amount) * 1e9)
        print(f"Sending {amount} SUI ({mist} mist) to {to_address}...")
        # sendSui returns Result<SendResult, Text>
        output = dfx_call("sendSui", f'("{to_address}", {mist})')

    elif chain == "ton":
        nanotons = int(float(amount) * 1e9)
        print(f"Sending {amount} TON ({nanotons} nanotons) to {to_address}...")
        # sendTonSimple returns FLAT SendResultTon (NOT a variant!)
        output = dfx_call("sendTonSimple", f'("{to_address}", {nanotons})')

    elif chain in ("apt", "aptos"):
        octas = int(float(amount) * 1e8)
        print(f"Sending {amount} APT ({octas} octas) to {to_address}...")
        output = dfx_call("sendAptos", f'("{to_address}", {octas})')

    elif chain == "near":
        yocto = int(float(amount) * 1e24)
        print(f"Sending {amount} NEAR to {to_address}...")
        # sendNearTransfer takes (Text, Nat)
        output = dfx_call("sendNearTransfer", f'("{to_address}", {yocto} : nat)')

    elif chain in ("trx", "tron"):
        sun = int(float(amount) * 1e6)
        print(f"Sending {amount} TRX ({sun} sun) to {to_address}...")
        output = dfx_call("sendTrx", f'("{to_address}", {sun})')

    elif chain in ("ada", "cardano"):
        lovelace = int(float(amount) * 1e6)
        print(f"Sending {amount} ADA ({lovelace} lovelace) to {to_address}...")
        output = dfx_call("sendCardanoTransaction", f'("{to_address}", {lovelace})')

    elif chain == "cloak":
        satoshis = int(float(amount) * 1e8)
        print(f"Sending {amount} CLOAK to {to_address}...")
        output = dfx_call("sendCloak", f'("{to_address}", {satoshis})')

    elif chain == "rune":
        units = int(float(amount) * 1e8)
        print(f"Sending {amount} RUNE to {to_address}...")
        # sendThor takes (toAddress, amount, memo)
        output = dfx_call("sendThor", f'("{to_address}", {units}, "")')

    else:
        print(f"Unsupported chain for send: {chain}")
        print("Supported: sol, icp, btc, ltc, eth/ethereum, arb/arbitrum, base, polygon, bsc, optimism, xrp, sui, ton, apt, near, trx, ada, cloak, rune")
        return

    print(f"\nResult: {output}")


def swap_raydium(input_mint: str, output_mint: str, amount: str, slippage_bps: str):
    """Swap tokens on Raydium (Solana DEX)."""
    amount_int = int(float(amount))
    slippage = int(float(slippage_bps))
    print(f"Swapping {amount} of {input_mint[:8]}... → {output_mint[:8]}...")
    print(f"  Slippage: {slippage} bps")

    # swapRaydiumApiUser takes 8 params:
    #   inputMint, outputMint, amount, slippageBps, wrapSol, unwrapSol, ?inputAta, ?outputAta
    # Returns FLAT RaydiumApiSwapResult = { inputAmount, outputAmount, priceImpactPct, txSignature }
    #
    # Set wrapSol=true when input is native SOL (So11111111111111111111111111111111111111112)
    # Set unwrapSol=true when output is native SOL
    SOL_MINT = "So11111111111111111111111111111111111111112"
    wrap = "true" if input_mint == SOL_MINT else "false"
    unwrap = "true" if output_mint == SOL_MINT else "false"

    output = dfx_call(
        "swapRaydiumApiUser",
        f'("{input_mint}", "{output_mint}", {amount_int} : nat64, {slippage} : nat64, {wrap}, {unwrap}, null, null)'
    )
    print(f"\nResult: {output}")


def print_usage():
    print("""
MeneseSDK Wallet Commands (19 chains)
======================================

  addresses                              Get addresses on all 19 chains (FREE)
  balance <chain>                        Check balance (FREE)
  send <chain> <amount> <to>             Send tokens ($0.05)
  swap <input_mint> <output_mint> <amount> <slippage_bps>  Raydium swap ($0.075)

Chains for send: sol, icp, btc, ltc, eth, arb, base, polygon, bsc, optimism,
                 xrp, sui, ton, apt, near, trx, ada, cloak, rune

Chains for balance: sol, icp, xrp, sui, ethereum, arbitrum, base, polygon, bsc, optimism

IMPORTANT: EVM chains (eth, arb, base, etc.) require RPC endpoints.
Edit EVM_RPCS in this script to set your own. Free public RPCs are
included for testing; use Alchemy/Infura for production.

Examples:
  python3 wallet_commands.py addresses
  python3 wallet_commands.py balance sol
  python3 wallet_commands.py send sol 0.01 5xK2...abc
  python3 wallet_commands.py send icp 1.0 aaaaa-aa
  python3 wallet_commands.py send eth 0.01 0x7f3d...
  python3 wallet_commands.py swap So111...112 EPjFW...1v 500000000 150
""")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)

    command = sys.argv[1].lower()

    if command == "addresses":
        get_addresses()
    elif command == "balance":
        if len(sys.argv) < 3:
            print("Usage: wallet_commands.py balance <chain>")
            sys.exit(1)
        get_balance(sys.argv[2])
    elif command == "send":
        if len(sys.argv) < 5:
            print("Usage: wallet_commands.py send <chain> <amount> <address>")
            sys.exit(1)
        send_tokens(sys.argv[2], sys.argv[3], sys.argv[4])
    elif command == "swap":
        if len(sys.argv) < 6:
            print("Usage: wallet_commands.py swap <input_mint> <output_mint> <amount> <slippage_bps>")
            sys.exit(1)
        swap_raydium(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
    else:
        print(f"Unknown command: {command}")
        print_usage()
        sys.exit(1)
