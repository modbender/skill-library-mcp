#!/usr/bin/env node

import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const SPEC_PATH = path.join(__dirname, "..", "resources", "atlas-admin-api-v2-openapi-source.json");

function usage() {
  console.error(`Usage: atlas-api.mjs <command> [args]

Commands:
  catalog [category]     List all APIs, optionally filtered by category
  detail <operationId>   Get detailed info for a specific API
  schema <schemaName>    Get schema definition (e.g., ClusterDescription)

Examples:
  node atlas-api.mjs catalog
  node atlas-api.mjs catalog Clusters
  node atlas-api.mjs detail listClusterDetails
  node atlas-api.mjs schema "#/components/schemas/ApiError"
`);
  process.exit(2);
}

// Load OpenAPI spec
function loadSpec() {
  if (!fs.existsSync(SPEC_PATH)) {
    throw new Error(`OpenAPI spec not found: ${SPEC_PATH}`);
  }
  const raw = fs.readFileSync(SPEC_PATH, "utf-8");
  return JSON.parse(raw);
}

// Resolve $ref references
function resolveRef(spec, obj, maxDepth = 5, currentDepth = 0, shallow = false) {
  if (currentDepth >= maxDepth) return obj;
  
  if (typeof obj === "object" && obj !== null) {
    if (Array.isArray(obj)) {
      return obj.map(item => resolveRef(spec, item, maxDepth, currentDepth, shallow));
    }
    
    if (obj.$ref && typeof obj.$ref === "string") {
      const refPath = obj.$ref;
      if (refPath.startsWith("#/")) {
        const parts = refPath.slice(2).split("/");
        let resolved = spec;
        for (const part of parts) {
          resolved = resolved?.[part];
        }
        
        if (shallow && currentDepth > 0) {
          return obj;
        }
        
        return resolveRef(spec, resolved, maxDepth, currentDepth + 1, shallow);
      }
      return obj;
    }
    
    const result = {};
    for (const [key, value] of Object.entries(obj)) {
      result[key] = resolveRef(spec, value, maxDepth, currentDepth, shallow);
    }
    return result;
  }
  
  return obj;
}

// Smart trim - remove verbose fields
function smartTrim(obj) {
  if (typeof obj === "object" && obj !== null) {
    if (Array.isArray(obj)) {
      return obj.map(item => smartTrim(item));
    }
    
    const trimKeys = ["example", "examples", "default", "x-xgen-version"];
    const result = {};
    
    for (const [key, value] of Object.entries(obj)) {
      // Skip extension fields
      if (key.startsWith("x-") && key !== "x-enum-descriptions") {
        continue;
      }
      // Skip trim keys
      if (trimKeys.includes(key)) {
        continue;
      }
      // Truncate long descriptions
      if (key === "description" && typeof value === "string" && value.length > 300) {
        result[key] = value.slice(0, 300) + "...";
      } else {
        result[key] = smartTrim(value);
      }
    }
    return result;
  }
  return obj;
}

// YAML stringify (simple implementation)
function toYaml(obj, indent = 0) {
  const spaces = "  ".repeat(indent);
  let result = "";
  
  if (obj === null || obj === undefined) {
    return "null";
  }
  
  if (typeof obj === "string") {
    // Quote strings that need it
    if (obj.includes(":") || obj.includes("#") || obj.includes("'") || obj.includes('"') || obj.startsWith(" ") || obj.endsWith(" ")) {
      return `"${obj.replace(/"/g, '\\"')}"`;
    }
    return obj;
  }
  
  if (typeof obj === "number" || typeof obj === "boolean") {
    return String(obj);
  }
  
  if (Array.isArray(obj)) {
    if (obj.length === 0) return "[]";
    for (const item of obj) {
      const yamlItem = toYaml(item, indent + 1);
      if (typeof item === "object" && item !== null && !Array.isArray(item)) {
        result += `${spaces}-\n${yamlItem}\n`;
      } else {
        result += `${spaces}- ${yamlItem.replace(new RegExp(`^${" ".repeat(indent + 1)}`), "")}\n`;
      }
    }
    return result.trimEnd();
  }
  
  for (const [key, value] of Object.entries(obj)) {
    const yamlValue = toYaml(value, indent + 1);
    if (typeof value === "object" && value !== null && !Array.isArray(value) && Object.keys(value).length > 0) {
      result += `${spaces}${key}:\n${yamlValue}\n`;
    } else if (Array.isArray(value) && value.length > 0) {
      result += `${spaces}${key}:\n${yamlValue}\n`;
    } else {
      result += `${spaces}${key}: ${yamlValue}\n`;
    }
  }
  
  return result.trimEnd();
}

// Get list of unique categories from spec
function getCategories(spec) {
  const paths = spec.paths || {};
  const categories = new Set();
  
  for (const methods of Object.values(paths)) {
    for (const details of Object.values(methods)) {
      if (typeof details !== "object" || details === null) continue;
      const tags = details.tags || ["Uncategorized"];
      tags.forEach(tag => categories.add(tag));
    }
  }
  
  return Array.from(categories).sort();
}

// Get catalog of APIs
function getCatalog(spec, category = null) {
  // If no category specified, return list of categories
  if (!category) {
    const categories = getCategories(spec);
    const lines = categories.map(c => `- ${c}`);
    return `--- Atlas API Categories (${categories.length} total) ---\nUse: node atlas-api.mjs catalog <category> to list APIs in a category\n\n` + lines.join("\n");
  }
  
  const paths = spec.paths || {};
  const results = [];
  const targetCat = category.toLowerCase();
  
  for (const [pathStr, methods] of Object.entries(paths)) {
    for (const [method, details] of Object.entries(methods)) {
      if (typeof details !== "object" || details === null) continue;
      
      const tags = details.tags || ["Uncategorized"];
      
      if (tags.some(t => t.toLowerCase() === targetCat)) {
        const summary = details.summary || "N/A";
        const opId = details.operationId || "N/A";
        results.push(`- [${opId}] ${method.toUpperCase()} ${pathStr}\n  Summary: ${summary}`);
      }
    }
  }
  
  if (results.length === 0) {
    return `Category '${category}' not found.`;
  }
  
  return `--- Atlas API List (${category}) ---\n` + results.join("\n");
}

// Get API details by operationId
function getApiDetail(spec, operationId) {
  const paths = spec.paths || {};
  let targetOp = null;
  
  for (const [pathStr, methods] of Object.entries(paths)) {
    for (const [method, details] of Object.entries(methods)) {
      if (details?.operationId === operationId) {
        targetOp = { ...details, _path: pathStr, _method: method };
        break;
      }
    }
    if (targetOp) break;
  }
  
  if (!targetOp) {
    return `Error: API with operationId '${operationId}' not found.`;
  }
  
  const keysToKeep = ["summary", "description", "parameters", "requestBody", "responses"];
  const filteredOp = {};
  
  for (const key of keysToKeep) {
    if (key in targetOp) {
      filteredOp[key] = targetOp[key];
    }
  }
  
  // Add path and method for context
  filteredOp.path = targetOp._path;
  filteredOp.method = targetOp._method.toUpperCase();
  
  const resolvedOp = resolveRef(spec, filteredOp, 2, 0, true);
  const trimmedOp = smartTrim(resolvedOp);
  
  return toYaml(trimmedOp);
}

// Get schema details
function getSchemaDetail(spec, schemaRef) {
  // Handle shorthand form
  let fullRef = schemaRef;
  if (!schemaRef.startsWith("#/")) {
    fullRef = `#/components/schemas/${schemaRef}`;
  }
  
  if (!fullRef.startsWith("#/")) {
    return `Error: Invalid reference path '${schemaRef}', must start with '#/' or be a schema name.`;
  }
  
  const parts = fullRef.slice(2).split("/");
  let resolved = spec;
  
  for (const part of parts) {
    if (part in resolved) {
      resolved = resolved[part];
    } else {
      return `Error: Schema '${schemaRef}' not found.`;
    }
  }
  
  const resolvedSchema = resolveRef(spec, resolved, 3);
  const trimmedSchema = smartTrim(resolvedSchema);
  
  return toYaml({ [fullRef]: trimmedSchema });
}

// Main
async function main() {
  const args = process.argv.slice(2);
  
  if (args.length === 0 || args[0] === "-h" || args[0] === "--help") {
    usage();
  }
  
  const command = args[0];
  
  try {
    const spec = loadSpec();
    
    switch (command) {
      case "catalog": {
        const category = args[1] || null;
        console.log(getCatalog(spec, category));
        break;
      }
      
      case "detail": {
        if (!args[1]) {
          console.error("Error: operationId required");
          usage();
        }
        console.log(getApiDetail(spec, args[1]));
        break;
      }
      
      case "schema": {
        if (!args[1]) {
          console.error("Error: schemaName required");
          usage();
        }
        console.log(getSchemaDetail(spec, args[1]));
        break;
      }
      
      default:
        console.error(`Unknown command: ${command}`);
        usage();
    }
  } catch (err) {
    console.error(`Error: ${err.message}`);
    process.exit(1);
  }
}

main();
