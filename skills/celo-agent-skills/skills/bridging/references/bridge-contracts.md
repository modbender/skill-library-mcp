# Bridge Contract Addresses

## Native Bridge - Ethereum Mainnet to Celo

| Contract | Address | Chain |
|----------|---------|-------|
| SuperBridgeETHWrapper | 0x3bC7C4f8Afe7C8d514c9d4a3A42fb8176BE33c1e | Ethereum |
| L1 Standard Bridge | 0x9C4955b92F34148dbcfDCD82e9c9eCe5CF2badfe | Ethereum |
| L1 WETH | 0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2 | Ethereum |
| L2 WETH | 0xD221812de1BD094f35587EE8E174B07B6167D9Af | Celo |

## Native Bridge - Sepolia to Celo Sepolia

| Contract | Address | Chain |
|----------|---------|-------|
| SuperBridgeETHWrapper | 0x523e358dFd0c4e98F3401DAc7b1879445d377e37 | Sepolia |
| L1 Standard Bridge | 0xec18a3c30131a0db4246e785355fbc16e2eaf408 | Sepolia |
| L1 WETH | 0x7b79995e5f793A07Bc00c21412e50Ecae098E7f9 | Sepolia |
| L2 WETH | 0x2cE73DC897A3E10b3FF3F86470847c36ddB735cf | Celo Sepolia |

## Cross-Chain Messaging Contracts

### Hyperlane

| Contract | Mainnet Address |
|----------|-----------------|
| Mailbox | Check Hyperlane docs |
| InterchainGasPaymaster | Check Hyperlane docs |

### Chainlink CCIP

| Contract | Mainnet Address |
|----------|-----------------|
| Router | Check Chainlink docs |
| OnRamp | Check Chainlink docs |

## Bridge URLs

| Bridge | Mainnet URL | Testnet URL |
|--------|-------------|-------------|
| Superbridge | https://superbridge.app/celo | https://testnets.superbridge.app |
| Squid Router V2 | https://v2.app.squidrouter.com | - |
| LayerZero | https://layerzero.network | - |
| Jumper Exchange | https://jumper.exchange | - |
| Portal (Wormhole) | https://portalbridge.com | - |
| AllBridge | https://app.allbridge.io/bridge | - |
| Satellite (Axelar) | https://satellite.money | - |
| Transporter (CCIP) | https://www.transporter.io | - |
| Layerswap | https://layerswap.io/app | - |
| Hyperlane Nexus | https://www.usenexus.org | - |
| Mach Exchange | https://www.mach.exchange | - |
| Galaxy | https://galaxy.exchange/swap | - |
| SmolRefuel | https://smolrefuel.com | - |
| USDT0 | https://usdt0.to | - |

Source: https://docs.celo.org/home/bridged-tokens/bridges

## Cross-Chain Messaging Protocol URLs

| Protocol | URL |
|----------|-----|
| Chainlink CCIP | https://chain.link/cross-chain |
| Hyperlane | https://www.hyperlane.xyz |
| Wormhole | https://wormhole.com |
| LayerZero | https://layerzero.network |
| Axelar Network | https://axelar.network |

Source: https://docs.celo.org/tooling/bridges/cross-chain-messaging

## Notes

- Native bridge contracts are maintained by Celo via OP Stack standard bridge
- Always verify addresses on block explorers before use
- Cross-chain messaging contract addresses may update - check official protocol documentation
- For testnet bridging, enable "Testnet" mode in Superbridge settings
