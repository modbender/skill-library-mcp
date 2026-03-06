import { ethers } from "ethers";
import modAbi from "../abi-mod.json" with { type: "json" };
import notesAbi from "../abi-notes.json" with { type: "json" };

const rpc = process.env.AVAX_RPC_URL || "https://api.avax.network/ext/bc/C/rpc";
const username = process.env.BITNOTE_USERNAME || "example_username";

const provider = new ethers.JsonRpcProvider(rpc);
const mod = new ethers.Contract("0x225AFdEb639E4cB7A128e348898A02e4730F2F2A", modAbi, provider);
const notes = new ethers.Contract("0x3B0f15DAB71e3C609EcbB4c99e3AD7EA6532c8c9", notesAbi, provider);

const unameHash = ethers.keccak256(ethers.toUtf8Bytes(username));
const linkedAddress = await mod.getAddressLink(unameHash);

console.log("USERNAME", username);
console.log("LINKED_ADDRESS", linkedAddress);

if (linkedAddress !== ethers.ZeroAddress) {
  const idx = await notes.getUserIndex(linkedAddress);
  console.log("INDEX_COUNT", idx.length);

  if (idx.length > 0) {
    const blobs = await notes.getDataAtIndexArray(Array.from(idx));
    console.log("BLOB_COUNT", blobs.length);
  }
}
