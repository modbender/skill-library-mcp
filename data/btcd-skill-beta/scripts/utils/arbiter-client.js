import axios from 'axios';
import { ethers } from 'ethers';
import { readFileSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';
import { logger } from './logger.js';
import { getEVMWallet } from './wallet-manager.js';
import { config } from './config.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const arbitratorManagerABI = JSON.parse(
  readFileSync(join(__dirname, '../abi/ArbitratorManager.json'), 'utf8')
);

const SUBGRAPH_URL =
  process.env.ARBITRATION_SUBGRAPH_URL || 'https://graph.bel2.org/subgraphs/name/btcd-arbitrators-staging';

export async function fetchArbiters() {
  const query = `query FetchArbiters {
    arbiterInfos (where: { isActive: true }) {
      id
      address
      deadLine
      isActive
      paused
    }
  }`;

  try {
    const response = await axios.post(SUBGRAPH_URL, { query }, { headers: { 'Content-Type': 'application/json' } });

    return response.data?.data?.arbiterInfos || [];
  } catch (error) {
    logger.error('Failed to fetch arbiters from subgraph:', error.message);
    return [];
  }
}

export async function selectBestArbiter(orderDurationDays) {
  logger.info('Selecting best arbiter for order...');

  // Fetch arbiters from subgraph
  const arbiters = await fetchArbiters();

  if (arbiters.length === 0) {
    throw new Error('No active arbiters found');
  }

  logger.info(`Found ${arbiters.length} active arbiters`);

  // Calculate minimum deadline (order duration + buffer)
  const now = Math.floor(Date.now() / 1000);
  const orderDurationSeconds = orderDurationDays * 24 * 60 * 60;
  const bufferSeconds = 30 * 24 * 60 * 60; // 30 days buffer
  const minDeadline = now + orderDurationSeconds + bufferSeconds;

  logger.data('Min Arbiter Deadline', new Date(minDeadline * 1000).toISOString());

  // Filter arbiters with deadline after minDeadline
  const validArbiters = arbiters.filter(a => {
    const arbiterDeadline = Number(a.deadLine);
    const isValid = arbiterDeadline > minDeadline && !a.paused && a.isActive;

    if (isValid) {
      logger.data(`  ${a.address.substring(0, 10)}...`, `Deadline: ${new Date(arbiterDeadline * 1000).toISOString()}`);
    }

    return isValid;
  });

  if (validArbiters.length === 0) {
    throw new Error(
      `No arbiters found with deadline after ${new Date(minDeadline * 1000).toISOString()}. ` +
        `Try a shorter loan duration or wait for new arbiters.`
    );
  }

  // Select the first valid arbiter
  const selected = validArbiters[0];

  logger.success(`Selected arbiter: ${selected.address}`);
  logger.data('  Deadline', new Date(Number(selected.deadLine) * 1000).toISOString());

  return selected.address;
}

export async function getArbiterFeesFromOrderContract(orderContractInstance, arbiterAddress) {
  try {
    const fees = await orderContractInstance.getSelectedArbitratorFees(arbiterAddress);
    return {
      ethFee: fees.ethFee,
      btcFee: fees.btcFee
    };
  } catch (error) {
    logger.warning('Failed to get arbiter fees from order contract, using defaults:', error.message);
    return { ethFee: ethers.BigNumber.from(0), btcFee: ethers.BigNumber.from(0) };
  }
}

export async function getArbiterFeesFromManager(duration, arbiterAddress) {
  const wallet = getEVMWallet();
  const contract = new ethers.Contract(
    config.contracts.arbitratorManager || '0xcB8039A2D7A541F730B488dD85e2a91f116A95E2',
    arbitratorManagerABI.abi,
    wallet
  );

  try {
    const [ethFee, btcFee] = await Promise.all([
      contract.getFee(duration, arbiterAddress),
      contract.getBtcFee(duration, arbiterAddress)
    ]);

    return {
      ethFee,
      btcFee
    };
  } catch (error) {
    logger.warning('Failed to get arbiter fees from manager, using defaults:', error.message);
    return { ethFee: ethers.BigNumber.from(0), btcFee: ethers.BigNumber.from(0) };
  }
}
