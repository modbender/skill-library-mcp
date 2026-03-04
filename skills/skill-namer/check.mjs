#!/usr/bin/env node
/**
 * Skill-Namer — check helper (manual-first, zero keys required)
 * Prints search URLs across common Web3 + ICANN naming providers.
 * Does NOT guarantee availability; it’s a fast lane for humans/moltys.
 *
 * Usage:
 *   node scripts/check.mjs workcrew gigmesh bountyhq --tlds eth,com,xyz --providers ens,ud,godaddy,namecheap,porkbun,dynadot,hover,gandi,squarespace,cloudflare
 *
 * Notes:
 * - For .eth, we link directly to ENS Manager.
 * - For DNS, we link to registrar search pages.
 */

const args = process.argv.slice(2);

function getFlag(name, def=null) {
  const i = args.indexOf(`--${name}`);
  if (i === -1) return def;
  return args[i+1] ?? def;
}

const tlds = (getFlag('tlds', 'eth,ai,com,dao') || 'eth,ai,com,dao').split(',').map(s=>s.trim()).filter(Boolean);
const providers = (getFlag('providers', 'ens,ud,godaddy,namecheap,porkbun,dynadot,hover,gandi,squarespace,cloudflare') || '')
  .split(',').map(s=>s.trim().toLowerCase()).filter(Boolean);

const names = args.filter(a=>!a.startsWith('--') && !args[args.indexOf(a)-1]?.startsWith('--'))
  .filter(a=>!a.includes(','));

if (!names.length) {
  console.error('Provide one or more base names (without TLD), e.g. `workcrew gigmesh`');
  process.exit(2);
}

const P = {
  ens: (n)=>`https://app.ens.domains/${encodeURIComponent(n)}.eth`,
  ud: (n)=>`https://unstoppabledomains.com/search?searchTerm=${encodeURIComponent(n)}`,
  godaddy: (fqdn)=>`https://www.godaddy.com/domainsearch/find?domainToCheck=${encodeURIComponent(fqdn)}`,
  namecheap: (fqdn)=>`https://www.namecheap.com/domains/registration/results/?domain=${encodeURIComponent(fqdn)}`,
  porkbun: (fqdn)=>`https://porkbun.com/products/domains/search?q=${encodeURIComponent(fqdn)}`,
  dynadot: (fqdn)=>`https://www.dynadot.com/domain/search?domain=${encodeURIComponent(fqdn)}`,
  hover: (fqdn)=>`https://www.hover.com/domains/results?q=${encodeURIComponent(fqdn)}`,
  gandi: (fqdn)=>`https://www.gandi.net/en/domain/suggest?search=${encodeURIComponent(fqdn)}`,
  squarespace: (fqdn)=>`https://domains.squarespace.com/domain-search?query=${encodeURIComponent(fqdn)}`,
  cloudflare: (fqdn)=>`https://www.cloudflare.com/products/registrar/`,
};

function uniq(arr){ return [...new Set(arr)]; }

for (const base of names) {
  const b = base.toLowerCase().trim();
  if (!b) continue;
  console.log(`\n== ${b}`);

  // Web3
  if (tlds.includes('eth') && providers.includes('ens')) {
    console.log(`.eth (ENS): ${P.ens(b)}`);
  }
  if (providers.includes('ud')) {
    console.log(`Unstoppable: ${P.ud(b)}`);
  }

  // DNS (group by TLD for readability)
  const dnsTlds = tlds.filter(t=>t !== 'eth');
  for (const tld of uniq(dnsTlds)) {
    const fqdn = `${b}.${tld}`;
    console.log(`\n-- ${fqdn}`);
    for (const prov of providers) {
      if (['ens','ud'].includes(prov)) continue;
      const fn = P[prov];
      if (!fn) continue;
      if (prov === 'cloudflare') {
        console.log(`cloudflare: ${P.cloudflare(fqdn)} (manual search in UI)`);
      } else {
        console.log(`${prov}: ${fn(fqdn)}`);
      }
    }
  }
}
