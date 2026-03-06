const { encodeFunctionData } = require('viem');

const DIAMOND_ADDRESS = '0xA99c4B08201F2913Db8D28e71d020c4298F29dBF';
const CHAIN_ID = 8453; // Base mainnet

// Slot position mapping
const SLOTS = {
  BODY: 0,
  FACE: 1,
  EYES: 2,
  HEAD: 3,
  LEFT_HAND: 4,
  RIGHT_HAND: 5,
  PET: 6,
  BACKGROUND: 7
};

const SLOT_NAMES = ['body', 'face', 'eyes', 'head', 'left-hand', 'right-hand', 'pet', 'background'];

// ABI for equipWearables
const EQUIP_ABI = {
  name: 'equipWearables',
  type: 'function',
  stateMutability: 'nonpayable',
  inputs: [
    { name: '_tokenId', type: 'uint256' },
    { name: '_wearablesToEquip', type: 'uint16[16]' }
  ],
  outputs: []
};

/**
 * Build equip transaction
 * @param {number} gotchiId - Gotchi token ID
 * @param {Object} wearables - Wearable configuration { slotName: wearableId }
 * @returns {Object} Transaction object for Bankr
 */
function buildEquipTransaction(gotchiId, wearables) {
  // Initialize empty slots (0 = unequip/no change based on current state)
  const slots = new Array(16).fill(0);
  
  // Fill in wearables
  for (const [slotName, wearableId] of Object.entries(wearables)) {
    const slotIndex = SLOT_NAMES.indexOf(slotName.toLowerCase());
    if (slotIndex === -1) {
      throw new Error(`Invalid slot name: ${slotName}. Valid slots: ${SLOT_NAMES.join(', ')}`);
    }
    slots[slotIndex] = parseInt(wearableId);
  }
  
  const calldata = encodeFunctionData({
    abi: [EQUIP_ABI],
    functionName: 'equipWearables',
    args: [BigInt(gotchiId), slots]
  });
  
  return {
    transaction: {
      to: DIAMOND_ADDRESS,
      chainId: CHAIN_ID,
      value: '0',
      data: calldata
    },
    description: `Equip wearables on Gotchi #${gotchiId}`,
    waitForConfirmation: true
  };
}

/**
 * Build unequip-all transaction
 * @param {number} gotchiId - Gotchi token ID
 * @returns {Object} Transaction object for Bankr
 */
function buildUnequipAllTransaction(gotchiId) {
  // All zeros = unequip everything
  const slots = new Array(16).fill(0);
  
  const calldata = encodeFunctionData({
    abi: [EQUIP_ABI],
    functionName: 'equipWearables',
    args: [BigInt(gotchiId), slots]
  });
  
  return {
    transaction: {
      to: DIAMOND_ADDRESS,
      chainId: CHAIN_ID,
      value: '0',
      data: calldata
    },
    description: `Unequip all wearables from Gotchi #${gotchiId}`,
    waitForConfirmation: true
  };
}

module.exports = {
  DIAMOND_ADDRESS,
  CHAIN_ID,
  SLOTS,
  SLOT_NAMES,
  buildEquipTransaction,
  buildUnequipAllTransaction
};
