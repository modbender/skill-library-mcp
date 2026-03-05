// OpenClaw plugin loader expects a CommonJS entry point at the plugin root.
// Re-export the compiled OpenClaw entry point.
module.exports = require("./dist/openclaw-entry.js");
