module.exports = {
  name: "hledger",
  description: "Execute hledger CLI commands",
  async run({ input }) {
    const { exec } = require("child_process");
    return new Promise((resolve, reject) => {
      exec(`hledger ${input}`, (err, stdout, stderr) => {
        if (err) return reject(stderr || err.message);
        resolve(stdout || stderr);
      });
    });
  }
};
