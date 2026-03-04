import fs from "node:fs/promises";

const addresses = {
  mod: "0x225AFdEb639E4cB7A128e348898A02e4730F2F2A",
  notes: "0x3B0f15DAB71e3C609EcbB4c99e3AD7EA6532c8c9",
  keys: "0x78D35C5341f9625f6eC7C497Ed875E0dEE0Ef3Ac",
};

for (const [name, address] of Object.entries(addresses)) {
  const u = new URL("https://api.snowtrace.io/api");
  u.searchParams.set("module", "contract");
  u.searchParams.set("action", "getabi");
  u.searchParams.set("address", address);
  u.searchParams.set("apikey", "YourApiKeyToken");

  const r = await fetch(u);
  const j = await r.json();
  if (j.status !== "1") throw new Error(`${name} abi failed: ${j.message}`);

  await fs.writeFile(`abi-${name}.json`, JSON.stringify(JSON.parse(j.result), null, 2));
  console.log("saved", `abi-${name}.json`);
}
