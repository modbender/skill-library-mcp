"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.loadPolicy = loadPolicy;
const fs = __importStar(require("fs"));
const constants_js_1 = require("./constants.js");
const validate_policy_js_1 = require("./validate-policy.js");
function loadPolicy(policyPath) {
    let resolvedPath = policyPath || constants_js_1.DEFAULT_POLICY_PATH;
    if (!fs.existsSync(resolvedPath) && !policyPath) {
        // Fall back to the bundled example policy for zero-config setup
        if (fs.existsSync(constants_js_1.DEFAULT_EXAMPLE_POLICY_PATH)) {
            resolvedPath = constants_js_1.DEFAULT_EXAMPLE_POLICY_PATH;
        }
        else {
            throw new Error(`Governance policy not found at ${resolvedPath}. Run: cp policy.example.json policy.json`);
        }
    }
    else if (!fs.existsSync(resolvedPath)) {
        throw new Error(`Governance policy not found at ${resolvedPath}`);
    }
    const raw = JSON.parse(fs.readFileSync(resolvedPath, "utf-8"));
    const validation = (0, validate_policy_js_1.validatePolicy)(raw);
    if (!validation.valid) {
        throw new Error(`Invalid policy at ${resolvedPath}: ${validation.errors.join("; ")}`);
    }
    if (validation.warnings.length > 0) {
        for (const w of validation.warnings) {
            process.stderr.write(`[governance] policy warning: ${w}\n`);
        }
    }
    return raw;
}
