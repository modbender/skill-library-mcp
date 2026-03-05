/**
 * PMP-Agent Core Calculations
 * PMBOK 7th Edition Project Management Functions
 */

// EVM (Earned Value Management)
export {
  calculateEVM,
  calculateEAC,
  formatEVMJson,
  formatEVMMarkdown,
  DEFAULT_THRESHOLDS,
  type EVMInput,
  type EVMOutput,
  type EVMThresholds,
} from './evm';

// Risk Management
export {
  scoreRisk,
  scoreRisks,
  getRiskMatrixTable,
  calculateRiskStats,
  DEFAULT_RISK_MATRIX,
  type RiskInput,
  type RiskOutput,
  type RiskMatrix,
  type ProbabilityScore,
  type ImpactScore,
  type RiskZone,
} from './risk';

// Velocity & Agile
export {
  calculateVelocity,
  formatVelocityJson,
  formatVelocityMarkdown,
  type VelocityInput,
  type VelocityOutput,
} from './velocity';

// Health Check
export {
  checkHealth,
  formatHealthJson,
  formatHealthMarkdown,
  REQUIRED_DOCUMENTS,
  OPTIONAL_DOCUMENTS,
  type HealthCheckInput,
  type HealthCheckOutput,
} from './health';
