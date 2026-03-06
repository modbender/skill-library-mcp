import { ethers } from 'ethers';
import { EAS, SchemaEncoder } from '@ethereum-attestation-service/eas-sdk';
import { config } from '../config';
import { AttestationData } from '../types';

const BATCH_SIZE = config.attestationBatchSize;
const BATCH_INTERVAL_MS = 5 * 60 * 1000; // Flush batch every 5 minutes even if not full

// Astral location proof schema
const ASTRAL_SCHEMA_UID = '0xba4171c92572b1e4f241d044c32cdf083be9fd946b8766977558ca6378c824e2';

let attestationQueue: AttestationData[] = [];
let batchTimer: ReturnType<typeof setInterval> | null = null;
let isProcessing = false;
let totalAttestations = 0;

// EAS setup
const provider = new ethers.JsonRpcProvider(config.baseRpcUrl);
const wallet = new ethers.Wallet(config.walletPrivateKey, provider);
const eas = new EAS(config.easContract);
eas.connect(wallet);

const schemaEncoder = new SchemaEncoder(
  'uint256 eventTimestamp,string srs,string locationType,string location,string[] recipeType,bytes[] recipePayload,string[] mediaType,string[] mediaData,string memo'
);

export function queueAttestation(data: AttestationData): void {
  attestationQueue.push(data);

  if (attestationQueue.length >= BATCH_SIZE) {
    processBatch();
  }
}

async function processBatch(): Promise<void> {
  if (isProcessing || attestationQueue.length === 0) return;

  isProcessing = true;
  const batch = attestationQueue.splice(0, BATCH_SIZE);

  try {
    // Aggregate batch into a single attestation
    const aggregated = aggregateBatch(batch);

    // Build location string as GeoJSON Point
    const locationGeoJson = JSON.stringify({
      type: 'Point',
      coordinates: [aggregated.lon, aggregated.lat],
    });

    // Build memo with energy data
    const memo = JSON.stringify({
      gateway: 'windfall',
      version: '0.1.0',
      nodeId: aggregated.nodeId,
      requestCount: aggregated.requestCount,
      energyPricePerKwh: aggregated.energyPricePerKwh,
      carbonIntensityGCO2: aggregated.carbonIntensity,
      curtailmentActive: aggregated.curtailmentActive,
      model: aggregated.model,
      batchHash: aggregated.responseHash,
    });

    const encodedData = schemaEncoder.encodeData([
      { name: 'eventTimestamp', value: BigInt(aggregated.timestamp), type: 'uint256' },
      { name: 'srs', value: 'EPSG:4326', type: 'string' },
      { name: 'locationType', value: 'GeoJSON', type: 'string' },
      { name: 'location', value: locationGeoJson, type: 'string' },
      { name: 'recipeType', value: ['windfall-energy-proof'], type: 'string[]' },
      { name: 'recipePayload', value: [ethers.toUtf8Bytes(memo)], type: 'bytes[]' },
      { name: 'mediaType', value: [], type: 'string[]' },
      { name: 'mediaData', value: [], type: 'string[]' },
      { name: 'memo', value: memo, type: 'string' },
    ]);

    const tx = await eas.attest({
      schema: ASTRAL_SCHEMA_UID,
      data: {
        recipient: ethers.ZeroAddress,
        expirationTime: BigInt(0),
        revocable: false,
        refUID: ethers.ZeroHash,
        data: encodedData,
        value: BigInt(0),
      },
    });

    const uid = await tx.wait();
    totalAttestations++;

    console.log(
      `[eas] Attestation created: ${uid} | ` +
      `${aggregated.requestCount} requests | ` +
      `node=${aggregated.nodeId} | ` +
      `energy=$${aggregated.energyPricePerKwh.toFixed(4)}/kWh | ` +
      `carbon=${aggregated.carbonIntensity}g | ` +
      `https://base.easscan.org/attestation/view/${uid}`
    );

    return;
  } catch (err) {
    console.error('[eas] Attestation failed:', err);
    // Put items back in queue for retry
    attestationQueue.unshift(...batch);
  } finally {
    isProcessing = false;
  }
}

function aggregateBatch(batch: AttestationData[]): AttestationData {
  // Use the most recent entry as the representative
  const latest = batch[batch.length - 1];
  return {
    ...latest,
    requestCount: batch.length,
    // Hash all request IDs together
    responseHash: ethers.id(batch.map(b => b.responseHash).join(',')),
  };
}

export function startAttestationBatcher(): void {
  batchTimer = setInterval(() => {
    if (attestationQueue.length > 0) {
      console.log(`[eas] Flushing batch: ${attestationQueue.length} pending attestations`);
      processBatch();
    }
  }, BATCH_INTERVAL_MS);
}

export function stopAttestationBatcher(): void {
  if (batchTimer) {
    clearInterval(batchTimer);
    batchTimer = null;
  }
}

export function getAttestationStats() {
  return {
    totalAttestations,
    pendingInQueue: attestationQueue.length,
    batchSize: BATCH_SIZE,
  };
}

// Force flush — useful for testing or shutdown
export async function flushAttestations(): Promise<void> {
  while (attestationQueue.length > 0) {
    await processBatch();
  }
}
