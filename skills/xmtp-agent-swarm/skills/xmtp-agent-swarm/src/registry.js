// registry.js — On-chain BoardRegistry client
import { ethers } from 'ethers';

const REGISTRY_ADDRESS = '0xf64B21Ce518ab025208662Da001a3F61D3AcB390'; // V2
const RPC = 'https://mainnet.base.org';

const ABI = [
  'function registerBoard(string xmtpGroupId, string name, string description, string[] skills) returns (bytes32)',
  'function updateBoard(bytes32 boardId, string name, string description, string[] skills)',
  'function deactivateBoard(bytes32 boardId)',
  'function requestJoin(bytes32 boardId, string xmtpAddress, string[] skills)',
  'function approveJoin(bytes32 boardId, uint256 requestIndex)',
  'function rejectJoin(bytes32 boardId, uint256 requestIndex)',
  'function getBoardCount() view returns (uint256)',
  'function getBoard(bytes32 boardId) view returns (address owner, string xmtpGroupId, string name, string description, string[] skills, uint256 memberCount, uint256 createdAt, bool active)',
  'function getJoinRequestCount(bytes32 boardId) view returns (uint256)',
  'function getJoinRequest(bytes32 boardId, uint256 index) view returns (address agent, string xmtpAddress, string[] skills, uint256 requestedAt, bool approved, bool rejected)',
  'function listBoards(uint256 offset, uint256 limit) view returns (bytes32[] ids, uint256 total)',
  'function getOwnerBoards(address owner) view returns (bytes32[])',
  'function getAgentBoards(address agent) view returns (bytes32[])',
  'event BoardRegistered(bytes32 indexed boardId, address indexed owner, string name)',
  'event JoinRequested(bytes32 indexed boardId, address indexed agent)',
  'event JoinApproved(bytes32 indexed boardId, address indexed agent)',
];

export function getRegistry(walletOrProvider) {
  return new ethers.Contract(REGISTRY_ADDRESS, ABI, walletOrProvider);
}

export function getReadonlyRegistry() {
  const provider = new ethers.JsonRpcProvider(RPC);
  return new ethers.Contract(REGISTRY_ADDRESS, ABI, provider);
}

export async function listAllBoards(limit = 50) {
  const registry = getReadonlyRegistry();
  const [ids, total] = await registry.listBoards(0, limit);
  const boards = [];
  for (const id of ids) {
    const [owner, xmtpGroupId, name, description, skills, memberCount, createdAt, active] = await registry.getBoard(id);
    if (active) {
      boards.push({ id, owner, xmtpGroupId, name, description, skills, memberCount: Number(memberCount), createdAt: Number(createdAt) });
    }
  }
  return { boards, total: Number(total) };
}

export async function registerBoard(wallet, xmtpGroupId, name, description, skills) {
  const registry = getRegistry(wallet);
  const tx = await registry.registerBoard(xmtpGroupId, name, description, skills);
  const receipt = await tx.wait();
  const event = receipt.logs.find(l => {
    try { return registry.interface.parseLog(l)?.name === 'BoardRegistered'; } catch { return false; }
  });
  const boardId = event ? registry.interface.parseLog(event).args[0] : null;
  return { txHash: tx.hash, boardId };
}

export async function requestJoinBoard(wallet, boardId, xmtpAddress, skills) {
  const registry = getRegistry(wallet);
  const tx = await registry.requestJoin(boardId, xmtpAddress, skills);
  await tx.wait();
  return { txHash: tx.hash };
}

export async function approveJoinRequest(wallet, boardId, requestIndex) {
  const registry = getRegistry(wallet);
  const tx = await registry.approveJoin(boardId, requestIndex);
  await tx.wait();
  return { txHash: tx.hash };
}

export async function getPendingRequests(boardId) {
  const registry = getReadonlyRegistry();
  const count = await registry.getJoinRequestCount(boardId);
  const requests = [];
  for (let i = 0; i < Number(count); i++) {
    const [agent, xmtpAddress, skills, requestedAt, approved, rejected] = await registry.getJoinRequest(boardId, i);
    if (!approved && !rejected) {
      requests.push({ index: i, agent, xmtpAddress, skills, requestedAt: Number(requestedAt) });
    }
  }
  return requests;
}

export { REGISTRY_ADDRESS };
