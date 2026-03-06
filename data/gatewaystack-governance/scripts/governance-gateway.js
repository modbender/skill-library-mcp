#!/usr/bin/env node
"use strict";
/**
 * GatewayStack Governance Gateway for OpenClaw
 *
 * Barrel module — re-exports the public API and serves as the CLI entry point.
 * Implementation lives in ./governance/*.ts modules.
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.buildBaseline = exports.detectAnomalies = exports.scanOutput = exports.checkGovernance = exports.validatePolicy = exports.loadPolicy = void 0;
var policy_js_1 = require("./governance/policy.js");
Object.defineProperty(exports, "loadPolicy", { enumerable: true, get: function () { return policy_js_1.loadPolicy; } });
var validate_policy_js_1 = require("./governance/validate-policy.js");
Object.defineProperty(exports, "validatePolicy", { enumerable: true, get: function () { return validate_policy_js_1.validatePolicy; } });
var check_js_1 = require("./governance/check.js");
Object.defineProperty(exports, "checkGovernance", { enumerable: true, get: function () { return check_js_1.checkGovernance; } });
var dlp_js_1 = require("./governance/dlp.js");
Object.defineProperty(exports, "scanOutput", { enumerable: true, get: function () { return dlp_js_1.scanOutput; } });
var behavioral_js_1 = require("./governance/behavioral.js");
Object.defineProperty(exports, "detectAnomalies", { enumerable: true, get: function () { return behavioral_js_1.detectAnomalies; } });
Object.defineProperty(exports, "buildBaseline", { enumerable: true, get: function () { return behavioral_js_1.buildBaseline; } });
// CLI entry point
const cli_js_1 = require("./governance/cli.js");
const isDirectExecution = require.main === module ||
    process.argv[1]?.endsWith("governance-gateway.js");
if (isDirectExecution) {
    (0, cli_js_1.runGovernanceCheck)((0, cli_js_1.parseArgs)(process.argv));
}
