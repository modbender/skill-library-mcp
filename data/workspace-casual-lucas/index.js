const fs = require("fs");
const { execSync } = require("child_process");
const path = require("path");

module.exports = {
  // List workspace files
  list_workspace: ({ path }) => {
    const workspacePath = path || "C:\\Users\\lucas\\OpenClawWorkspace";
    try {
      return fs.readdirSync(workspacePath);
    } catch (err) {
      return `Error listing workspace: ${err.message}`;
    }
  },

  // Run any command
  run_command: ({ command }) => {
    try {
      const output = execSync(command, { encoding: "utf8" });
      return output;
    } catch (err) {
      return `Error running command: ${err.message}`;
    }
  },

  // Open a file
  open_file: ({ file }) => {
    const resolvedPath = path.resolve(file);
    if (fs.existsSync(resolvedPath)) {
      return fs.readFileSync(resolvedPath, "utf8");
    } else {
      return "File does not exist.";
    }
  }
};
