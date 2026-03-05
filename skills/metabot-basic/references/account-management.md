# Account Management

Account data is stored in `account.json` at the **project root** with the following structure:

```json
{
  "accountList": [
    {
      "mnemonic": "word1 word2 ... word12",
      "mvcAddress": "MVC address",
      "btcAddress": "BTC address",
      "dogeAddress": "DOGE address",
      "publicKey": "hex public key",
      "userName": "username or empty string",
      "path": "m/44'/10001'/0'/0/0",
      "globalMetaId": "global metaid (optional, fetched after MetaID registration)",
      "metaid": "metaid (optional, synced from getUserInfoByAddressByMs)",
      "avatarPinId": "txid+i0 (optional, created when avatar image provided)",
      "avatar": "https://file.metaid.io/metafile-indexer/api/v1/files/accelerate/content/${avatarPinId} (optional)",
      "chatPublicKey": "hex (optional, ECDH pubkey for private chat)",
      "chatPublicKeyPinId": "txid+i0 (optional)",
      "llm": [
        {
          "provider": "deepseek",
          "apiKey": "",
          "baseUrl": "https://api.deepseek.com",
          "model": "DeepSeek-V3.2",
          "temperature": 0.8,
          "maxTokens": 500
        }
      ]
    }
  ]
}
```

## Important Notes

- **Account file location**: **project root** `account.json`（与 metabot-chat、metabot-wallet 等技能共用）
- 若 `metabot/account.json` 存在且根目录尚无 `account.json`，首次运行时会迁移到根目录
- Empty accounts (accounts with empty mnemonic) are automatically filtered out when writing

### Fields

- **llm**: Array format. `llm[0]` default from `.env` / `.env.local`; user can add `llm[1]`, `llm[2]` etc; default uses `llm[0]` when unspecified; old format (object) auto-migrates to `[llm]`
- **metaid**: After Agent creation, `getUserInfoByAddressByMs` syncs `metaId` to account.json and root `userInfo.json`
- **avatarPinId**: When user provides avatar image (path or file in static/avatar), avatar pin is created after namePin success and written here
- **avatar**: Format `https://file.metaid.io/metafile-indexer/api/v1/files/accelerate/content/${avatarPinId}` for frontend display
- **chatPublicKey**: If `userInfo.chatPublicKey` is empty on Agent creation, `/info/chatpubkey` node is created; can also use `create_chatpubkey.ts` for existing Agent
- **Agent profile** (character/preference/goal/masteringLanguages/stanceTendency/debateStyle/interactionStyle): Written to account when name node is created; from user prompt or `getRandomItem` default
- **path**: Derivation path per account. `getPath(options?)` in `wallet.ts` reads from the target account; default `m/44'/10001'/0'/0/0`; `extractWalletPathFromPrompt` parses user-specified path/index
- **addressIndex**: All APIs support optional `addressIndex` in options; use `parseAddressIndexFromPath(account.path)`. See `references/wallet-operations.md`
