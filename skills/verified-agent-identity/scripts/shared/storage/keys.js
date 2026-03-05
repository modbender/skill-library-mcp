const { FileStorage } = require("./base");

/**
 * File-based storage for cryptographic keys.
 * Implements AbstractPrivateKeyStore interface from js-sdk.
 * Stores keys in JSON format as an array of {alias, privateKeyHex} objects.
 */
class KeysFileStorage extends FileStorage {
  constructor(filename = "kms.json") {
    super(filename);
  }

  async importKey(args) {
    const keys = await this.readFile();
    const index = keys.findIndex((entry) => entry.alias === args.alias);

    if (index >= 0) {
      keys[index].privateKeyHex = args.key;
    } else {
      keys.push({ alias: args.alias, privateKeyHex: args.key });
    }

    await this.writeFile(keys);
  }

  async get(args) {
    const keys = await this.readFile();
    const entry = keys.find((entry) => entry.alias === args.alias);
    return entry ? entry.privateKeyHex : "";
  }

  async list() {
    const keys = await this.readFile();
    return keys.map((entry) => ({
      alias: entry.alias,
      key: entry.privateKeyHex,
    }));
  }
}

module.exports = { KeysFileStorage };
