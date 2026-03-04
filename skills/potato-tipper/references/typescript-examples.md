# TypeScript examples — setup PotatoTipper for a 🆙

## Prerequisites

```bash
npm install @erc725/erc725.js @lukso/lsp-smart-contracts viem wagmi
```

## 1) Encode LSP1 delegate data keys + values (using erc725.js)

This is the core encoding logic used by the dApp. It produces the data keys and values to call `setDataBatch` on the 🆙.

```ts
import { ERC725, type ERC725JSONSchema } from '@erc725/erc725.js';
import LSP1Schema from '@erc725/erc725.js/schemas/LSP1UniversalReceiverDelegate.json';

// LSP26 type IDs (from @lukso/lsp26-contracts)
const LSP26_FOLLOW_TYPE_ID =
  '0x71e02f9f05bcd5816ec4f3134aa2e5a916669537b41f96eb8c5d7a5514904590';
const LSP26_UNFOLLOW_TYPE_ID =
  '0x9d3c0b4012b69658977b099bdaa51eff0f0460f4a204bfed99e554c1eab4b7c1';

// PotatoTipper:Settings custom schema
const POTATO_SETTINGS_SCHEMA: ERC725JSONSchema = {
  name: 'PotatoTipper:Settings',
  key: '0xd1d57abed02d4c2d7ce00000e8211998bb257be214c7b0997830cd295066cc6a',
  keyType: 'Mapping',
  valueType: '(uint256,uint256,uint256)',
  valueContent: '(Number,Number,Number)',
};

const erc725 = new ERC725([...LSP1Schema, POTATO_SETTINGS_SCHEMA]);

// --- Encode LSP1 delegate keys (connect PotatoTipper) ---
export function encodeLSP1DelegateKeys(potatoTipperAddress: string) {
  const { keys, values } = erc725.encodeData([
    {
      keyName: 'LSP1UniversalReceiverDelegate:<bytes32>',
      dynamicKeyParts: [LSP26_FOLLOW_TYPE_ID],
      value: potatoTipperAddress,
    },
    {
      keyName: 'LSP1UniversalReceiverDelegate:<bytes32>',
      dynamicKeyParts: [LSP26_UNFOLLOW_TYPE_ID],
      value: potatoTipperAddress,
    },
  ]);
  return { keys: keys as `0x${string}`[], values: values as `0x${string}`[] };
}

// --- Encode tip settings ---
export function encodeTipSettings(
  tipAmountWei: string,      // e.g. "42000000000000000000" for 42 🥔
  minFollowers: string,       // e.g. "5"
  minPotatoBalanceWei: string // e.g. "100000000000000000000" for 100 🥔
) {
  const { keys: [key], values: [value] } = erc725.encodeData({
    keyName: 'PotatoTipper:Settings',
    value: [tipAmountWei, minFollowers, minPotatoBalanceWei],
  });
  return { key: key as `0x${string}`, value: value as `0x${string}` };
}

// --- Decode tip settings from raw bytes ---
export function decodeTipSettings(rawValue: string) {
  const decoded = erc725.decodeData([{
    keyName: POTATO_SETTINGS_SCHEMA.name,
    value: rawValue,
  }]);
  const [tipAmount, minFollowers, minPotatoBalance] = decoded[0].value as [bigint, number, bigint];
  return { tipAmount, minFollowers, minPotatoBalance };
}
```

## 2) Connect PotatoTipper from a dApp (wagmi + viem)

```ts
import { useAccount, useWriteContract } from 'wagmi';
import { universalProfileAbi } from '@lukso/lsp-smart-contracts/abi';
import { parseUnits } from 'viem';
import { encodeLSP1DelegateKeys, encodeTipSettings } from './erc725-helpers';

const POTATO_TIPPER_MAINNET = '0x5eed04004c2D46C12Fe30C639A90AD5d6F5D573d';

function useConnectPotatoTipper() {
  const { address } = useAccount();
  const { writeContract } = useWriteContract();

  // Step 1: Set LSP1 delegate data keys (connect)
  function connect() {
    const { keys, values } = encodeLSP1DelegateKeys(POTATO_TIPPER_MAINNET);
    writeContract({
      abi: universalProfileAbi,
      address: address!,
      functionName: 'setDataBatch',
      args: [keys, values],
    });
  }

  // Step 2: Set tip settings
  function setSettings(tipAmount: string, minFollowers: string, minBalance: string) {
    const { key, value } = encodeTipSettings(
      parseUnits(tipAmount, 18).toString(),
      minFollowers,
      parseUnits(minBalance, 18).toString()
    );
    writeContract({
      abi: universalProfileAbi,
      address: address!,
      functionName: 'setData',
      args: [key, value],
    });
  }

  // Step 3: Authorize PotatoTipper as operator on $POTATO token
  function authorizeTippingBudget(budgetAmount: string) {
    const POTATO_TOKEN_MAINNET = '0x80D898C5A3A0B118a0c8C8aDcdBB260FC687F1ce';
    writeContract({
      abi: [
        {
          name: 'authorizeOperator',
          type: 'function',
          inputs: [
            { name: 'operator', type: 'address' },
            { name: 'amount', type: 'uint256' },
            { name: 'operatorNotificationData', type: 'bytes' },
          ],
          outputs: [],
          stateMutability: 'nonpayable',
        },
      ],
      address: POTATO_TOKEN_MAINNET,
      functionName: 'authorizeOperator',
      args: [
        POTATO_TIPPER_MAINNET,
        parseUnits(budgetAmount, 18),
        '0x',
      ],
    });
  }

  // Disconnect: clear the LSP1 delegate keys
  function disconnect() {
    const { keys } = encodeLSP1DelegateKeys(POTATO_TIPPER_MAINNET);
    writeContract({
      abi: universalProfileAbi,
      address: address!,
      functionName: 'setDataBatch',
      args: [keys, ['0x', '0x']],
    });
  }

  return { connect, setSettings, authorizeTippingBudget, disconnect };
}
```

## 3) Pure ethers.js example (no wagmi)

```ts
import { ethers } from 'ethers';
import { encodeLSP1DelegateKeys, encodeTipSettings } from './erc725-helpers';

const UP_ABI = [
  'function setDataBatch(bytes32[] keys, bytes[] values)',
  'function setData(bytes32 key, bytes value)',
];

async function connectPotatoTipper(
  signer: ethers.Signer,
  upAddress: string,
  potatoTipperAddress: string
) {
  const up = new ethers.Contract(upAddress, UP_ABI, signer);

  // 1. Connect LSP1 delegates
  const { keys, values } = encodeLSP1DelegateKeys(potatoTipperAddress);
  await up.setDataBatch(keys, values);

  // 2. Set settings (42 🥔 tip, min 5 followers, min 100 🥔 balance)
  const settings = encodeTipSettings(
    ethers.parseUnits('42', 18).toString(),
    '5',
    ethers.parseUnits('100', 18).toString()
  );
  await up.setData(settings.key, settings.value);

  console.log('PotatoTipper connected + settings configured');
}
```

## Important: permissions

The calling address (controller) MUST have:
- **`ADDUNIVERSALRECEIVERDELEGATE`** to connect (set new LSP1 delegate)
- **`CHANGEUNIVERSALRECEIVERDELEGATE`** to disconnect (clear existing LSP1 delegate)

See `references/permissions.md` for troubleshooting.

