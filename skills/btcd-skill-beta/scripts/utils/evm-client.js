import { ethers } from 'ethers';
import { readFileSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';
import { logger } from './logger.js';
import { getEVMWallet } from './wallet-manager.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Load contract ABIs
const loadABI = filename => {
  const abiPath = join(__dirname, '../abi', filename);
  return JSON.parse(readFileSync(abiPath, 'utf8'));
};

const loanContractABI = loadABI('LoanContract.json');
const orderABI = loadABI('Order.json');
const issuerABI = loadABI('Issuer.json');
const erc20ABI = loadABI('ERC20.json');

export function getLoanContractInstance(address) {
  const wallet = getEVMWallet();
  return new ethers.Contract(address, loanContractABI.abi, wallet);
}

export function getOrderContractInstance(address) {
  const wallet = getEVMWallet();
  return new ethers.Contract(address, orderABI.abi, wallet);
}

export function getIssuerContractInstance(address) {
  const wallet = getEVMWallet();
  return new ethers.Contract(address, issuerABI.abi, wallet);
}

export function getERC20Instance(address) {
  const wallet = getEVMWallet();
  return new ethers.Contract(address, erc20ABI.abi, wallet);
}

export async function waitForTransaction(tx, confirmations = 1) {
  logger.info(`Waiting for transaction confirmation...`);
  logger.txHash(tx.hash);

  const receipt = await tx.wait(confirmations);

  if (receipt.status === 1) {
    logger.success('Transaction confirmed!');
  } else {
    throw new Error('Transaction failed');
  }

  return receipt;
}

export async function getOrderData(loanContractAddress, orderId) {
  // orderId is the address of the deployed order contract
  const orderContract = getOrderContractInstance(orderId);

  try {
    // Read order data from the specific order contract
    // Field names from Order.json ABI
    const orderType = await orderContract.orderType();
    const status = await orderContract.status();
    const token = await orderContract.token();
    const tokenAmount = await orderContract.tokenAmount();
    const collateralAmount = await orderContract.collateralAmount();
    const interestRate = await orderContract.interestRate();
    const limitedDays = await orderContract.limitedDays();
    const createTime = await orderContract.createTime();
    const takenTime = await orderContract.takenTime();
    const lender = await orderContract.lender();
    const borrower = await orderContract.borrower();
    const borrowerBtcAddress = await orderContract.borrowerBtcAddress();
    const borrowerPublicKey = await orderContract.borrowerPublicKey();
    const lenderBtcAddress = await orderContract.lenderBtcAddress();
    const preImageHash = await orderContract.preImageHash();
    const currentSelectedArbitrator = await orderContract.currentSelectedArbitrator();

    return {
      orderType,
      status,
      token,
      lendingAmount: tokenAmount, // Alias for compatibility
      tokenAmount,
      collateralAmount,
      interestRate,
      durationDays: limitedDays, // Alias for compatibility
      limitedDays,
      createdAt: createTime, // Alias for compatibility
      createTime,
      takenAt: takenTime, // Alias for compatibility
      takenTime,
      lender,
      borrower,
      borrowerBtcAddress,
      borrowerBtcPubKey: borrowerPublicKey, // Alias for compatibility
      borrowerPublicKey,
      lenderBtcAddress,
      preImageHash,
      arbiterAddress: currentSelectedArbitrator, // Alias for compatibility
      currentSelectedArbitrator
    };
  } catch (error) {
    logger.error('Failed to get order data:', error.message);
    throw error;
  }
}

export function parseUnits(value, decimals) {
  return ethers.utils.parseUnits(value.toString(), decimals);
}

export function formatUnits(value, decimals) {
  return ethers.utils.formatUnits(value, decimals);
}
