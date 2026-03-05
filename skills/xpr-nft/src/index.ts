/**
 * NFT Skill — Full AtomicAssets/AtomicMarket Integration
 *
 * Read-only tools use the Saltant AtomicAssets REST API (rich joined data).
 * Write tools create sessions from env vars for signing transactions.
 */

// ── Types ────────────────────────────────────────

interface ToolDef {
  name: string;
  description: string;
  parameters: { type: 'object'; required?: string[]; properties: Record<string, unknown> };
  handler: (params: any) => Promise<unknown>;
}

interface SkillApi {
  registerTool(tool: ToolDef): void;
  getConfig(): Record<string, unknown>;
}

// ── Session Factory ──────────────────────────────

let cachedSession: { api: any; account: string; permission: string } | null = null;

async function getNftSession(): Promise<{ api: any; account: string; permission: string }> {
  if (cachedSession) return cachedSession;

  const privateKey = process.env.XPR_PRIVATE_KEY;
  const account = process.env.XPR_ACCOUNT;
  const permission = process.env.XPR_PERMISSION || 'active';
  const rpcEndpoint = process.env.XPR_RPC_ENDPOINT;

  if (!privateKey) throw new Error('XPR_PRIVATE_KEY is required for NFT write operations');
  if (!account) throw new Error('XPR_ACCOUNT is required for NFT write operations');
  if (!rpcEndpoint) throw new Error('XPR_RPC_ENDPOINT is required for NFT write operations');

  const { Api, JsonRpc, JsSignatureProvider } = await import('@proton/js');
  const rpc = new JsonRpc(rpcEndpoint);
  const signatureProvider = new JsSignatureProvider([privateKey]);
  const api = new Api({ rpc, signatureProvider });

  cachedSession = { api, account, permission };
  return cachedSession;
}

// ── AtomicAssets API Helpers ─────────────────────

const API_TIMEOUT = 15000;

function getAtomicApiEndpoints(network: string): string[] {
  if (network === 'mainnet') {
    return [
      'https://aa-xprnetwork-main.saltant.io',
      'https://xpr-mainnet-atm-api.bloxprod.io',
    ];
  }
  // BloxProd first — Saltant testnet indexer is unreliable / often behind
  return [
    'https://xpr-testnet-atm-api.bloxprod.io',
    'https://aa-xprnetwork-test.saltant.io',
  ];
}

async function atomicGetSingle(base: string, path: string, params?: Record<string, string>): Promise<any> {
  const url = new URL(path, base);
  if (params) {
    Object.entries(params).forEach(([k, v]) => {
      if (v !== undefined && v !== null && v !== '') url.searchParams.set(k, v);
    });
  }
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), API_TIMEOUT);
  try {
    const resp = await fetch(url.toString(), { signal: controller.signal });
    if (!resp.ok) {
      const text = await resp.text().catch(() => '');
      throw new Error(`AtomicAssets API ${path} failed (${resp.status}): ${text.slice(0, 200)}`);
    }
    const json = await resp.json();
    if (!json.success) throw new Error(`AtomicAssets API error: ${JSON.stringify(json).slice(0, 200)}`);
    return json.data;
  } finally {
    clearTimeout(timer);
  }
}

async function atomicGet(endpoints: string[], path: string, params?: Record<string, string>): Promise<any> {
  let lastError: Error | null = null;
  for (const base of endpoints) {
    try {
      return await atomicGetSingle(base, path, params);
    } catch (err: any) {
      lastError = err;
      // Try next endpoint
    }
  }
  throw lastError || new Error(`All AtomicAssets API endpoints failed for ${path}`);
}

// ── RPC Fallback Helper ─────────────────────────

async function rpcPost(endpoint: string, path: string, body: unknown): Promise<any> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), API_TIMEOUT);
  try {
    const resp = await fetch(`${endpoint}${path}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
      signal: controller.signal,
    });
    if (!resp.ok) {
      const text = await resp.text().catch(() => '');
      throw new Error(`RPC ${path} failed (${resp.status}): ${text.slice(0, 200)}`);
    }
    return await resp.json();
  } finally {
    clearTimeout(timer);
  }
}

async function getTableRows(endpoint: string, opts: {
  code: string; scope: string; table: string;
  lower_bound?: string | number; upper_bound?: string | number;
  limit?: number; key_type?: string; index_position?: string;
}): Promise<any[]> {
  const result = await rpcPost(endpoint, '/v1/chain/get_table_rows', {
    json: true,
    code: opts.code,
    scope: opts.scope,
    table: opts.table,
    lower_bound: opts.lower_bound,
    upper_bound: opts.upper_bound,
    limit: opts.limit || 100,
    key_type: opts.key_type,
    index_position: opts.index_position,
  });
  return result.rows || [];
}

// ── Schema Format Fetcher (AA API + RPC fallback) ──

async function fetchSchemaFormat(
  atomicEndpoints: string[],
  rpcEndpoint: string,
  collection_name: string,
  schema_name: string,
): Promise<Array<{ name: string; type: string }>> {
  // Try AA API first
  try {
    const data = await atomicGet(atomicEndpoints, `/atomicassets/v1/schemas/${encodeURIComponent(collection_name)}/${encodeURIComponent(schema_name)}`);
    if (data.format && data.format.length > 0) return data.format;
  } catch { /* fall through to RPC */ }

  // Fallback: read directly from chain (schemas table scoped by collection)
  const rows = await getTableRows(rpcEndpoint, {
    code: 'atomicassets',
    scope: collection_name,
    table: 'schemas',
    lower_bound: schema_name,
    upper_bound: schema_name,
    limit: 1,
  });
  if (rows.length === 0) throw new Error(`Schema "${schema_name}" not found in collection "${collection_name}"`);
  const format = rows[0].format;
  if (!Array.isArray(format) || format.length === 0) {
    throw new Error(`Schema "${schema_name}" has no attributes defined`);
  }
  return format;
}

// ── ATTRIBUTE_MAP Builder ────────────────────────

function buildAttributeMap(
  data: Record<string, any>,
  schemaFormat: Array<{ name: string; type: string }>,
): Array<{ key: string; value: [string, any] }> {
  const typeMap = new Map(schemaFormat.map(f => [f.name, f.type]));
  return Object.entries(data).map(([key, val]) => {
    const type = typeMap.get(key);
    if (!type) throw new Error(`Attribute "${key}" not found in schema`);
    if (['string', 'image', 'ipfs'].includes(type)) return { key, value: ['string', String(val)] };
    if (type.startsWith('uint')) return { key, value: [type, Number(val)] };
    if (type.startsWith('int')) return { key, value: [type, Number(val)] };
    if (['float', 'double'].includes(type)) return { key, value: ['double', Number(val)] };
    if (type === 'bool') return { key, value: ['uint8', val ? 1 : 0] };
    return { key, value: ['string', String(val)] };
  });
}

// ── Token Contract Resolution ────────────────────

const TOKEN_CONTRACTS: Record<string, string> = {
  XPR: 'eosio.token',
  XUSDC: 'xtokens',
  XBTC: 'xtokens',
  XETH: 'xtokens',
  METAL: 'xtokens',
  FOOBAR: 'xtokens',
  XDOGE: 'xtokens',
  XLTC: 'xtokens',
};

function getTokenContract(symbol: string): string {
  return TOKEN_CONTRACTS[symbol.toUpperCase()] || 'eosio.token';
}

function parsePrice(price: string): { amount: string; symbol: string; precision: number; contract: string } {
  const parts = price.trim().split(/\s+/);
  if (parts.length !== 2) throw new Error(`Invalid price format "${price}". Expected "100.0000 XPR"`);
  const amount = parts[0];
  const symbol = parts[1].toUpperCase();
  const dotIdx = amount.indexOf('.');
  const precision = dotIdx >= 0 ? amount.length - dotIdx - 1 : 0;
  const contract = getTokenContract(symbol);
  return { amount, symbol, precision, contract };
}

// ── Validation Helpers ───────────────────────────

function isValidEosioName(name: string): boolean {
  if (!name || name.length > 12) return false;
  return /^[a-z1-5.]+$/.test(name);
}

// ── Skill Entry Point ────────────────────────────

export default function nftSkill(api: SkillApi): void {
  const config = api.getConfig();
  const rpcEndpoint = (config.rpcEndpoint as string) || process.env.XPR_RPC_ENDPOINT || '';
  const network = (config.network as string) || process.env.XPR_NETWORK || 'testnet';
  const atomicEndpoints = getAtomicApiEndpoints(network);

  // ════════════════════════════════════════════════
  // READ-ONLY TOOLS (11)
  // ════════════════════════════════════════════════

  // ── 1. nft_get_collection ──
  api.registerTool({
    name: 'nft_get_collection',
    description: 'Get details of an AtomicAssets collection by name. Returns author, authorized accounts, market fee, and collection data.',
    parameters: {
      type: 'object',
      required: ['collection_name'],
      properties: {
        collection_name: { type: 'string', description: 'Collection name (1-12 chars)' },
      },
    },
    handler: async ({ collection_name }: { collection_name: string }) => {
      if (!collection_name) return { error: 'collection_name is required' };
      try {
        const data = await atomicGet(atomicEndpoints, `/atomicassets/v1/collections/${encodeURIComponent(collection_name)}`);
        return {
          collection_name: data.collection_name,
          author: data.author,
          authorized_accounts: data.authorized_accounts,
          notify_accounts: data.notify_accounts,
          market_fee: data.market_fee,
          data: data.data,
          created_at_block: data.created_at_block,
          created_at_time: data.created_at_time,
        };
      } catch (err: any) {
        // Fallback to RPC
        try {
          const rows = await getTableRows(rpcEndpoint, {
            code: 'atomicassets', scope: 'atomicassets', table: 'collections',
            lower_bound: collection_name, upper_bound: collection_name, limit: 1,
          });
          if (rows.length === 0) return { error: `Collection "${collection_name}" not found` };
          return rows[0];
        } catch {
          return { error: `Failed to get collection: ${err.message}` };
        }
      }
    },
  });

  // ── 2. nft_list_collections ──
  api.registerTool({
    name: 'nft_list_collections',
    description: 'Search or list AtomicAssets collections. Filter by author or search term.',
    parameters: {
      type: 'object',
      properties: {
        author: { type: 'string', description: 'Filter by collection author account' },
        match: { type: 'string', description: 'Search term to match collection names' },
        limit: { type: 'number', description: 'Max results (default 20, max 100)' },
        page: { type: 'number', description: 'Page number (default 1)' },
      },
    },
    handler: async ({ author, match, limit, page }: {
      author?: string; match?: string; limit?: number; page?: number;
    }) => {
      const params: Record<string, string> = {
        limit: String(Math.min(Math.max(limit || 20, 1), 100)),
        page: String(Math.max(page || 1, 1)),
        order: 'desc',
        sort: 'created',
      };
      if (author) params.author = author;
      if (match) params.match = match;

      try {
        const data = await atomicGet(atomicEndpoints, '/atomicassets/v1/collections', params);
        const collections = Array.isArray(data) ? data : [];
        return {
          collections: collections.map((c: any) => ({
            collection_name: c.collection_name,
            author: c.author,
            market_fee: c.market_fee,
            data: c.data,
            created_at_time: c.created_at_time,
          })),
          total: collections.length,
        };
      } catch (err: any) {
        return { error: `Failed to list collections: ${err.message}` };
      }
    },
  });

  // ── 3. nft_get_schema ──
  api.registerTool({
    name: 'nft_get_schema',
    description: 'Get schema attribute definitions (name/type pairs) for a collection schema.',
    parameters: {
      type: 'object',
      required: ['collection_name', 'schema_name'],
      properties: {
        collection_name: { type: 'string', description: 'Collection name' },
        schema_name: { type: 'string', description: 'Schema name' },
      },
    },
    handler: async ({ collection_name, schema_name }: { collection_name: string; schema_name: string }) => {
      if (!collection_name || !schema_name) return { error: 'collection_name and schema_name are required' };
      try {
        const data = await atomicGet(atomicEndpoints, `/atomicassets/v1/schemas/${encodeURIComponent(collection_name)}/${encodeURIComponent(schema_name)}`);
        return {
          schema_name: data.schema_name,
          collection_name: data.collection?.collection_name || collection_name,
          format: data.format,
          created_at_time: data.created_at_time,
        };
      } catch (err: any) {
        return { error: `Failed to get schema: ${err.message}` };
      }
    },
  });

  // ── 4. nft_get_template ──
  api.registerTool({
    name: 'nft_get_template',
    description: 'Get template details including immutable data, supply count, and transferable/burnable flags.',
    parameters: {
      type: 'object',
      required: ['collection_name', 'template_id'],
      properties: {
        collection_name: { type: 'string', description: 'Collection name' },
        template_id: { type: 'string', description: 'Template ID' },
      },
    },
    handler: async ({ collection_name, template_id }: { collection_name: string; template_id: string }) => {
      if (!collection_name || !template_id) return { error: 'collection_name and template_id are required' };
      try {
        const data = await atomicGet(atomicEndpoints, `/atomicassets/v1/templates/${encodeURIComponent(collection_name)}/${encodeURIComponent(template_id)}`);
        return {
          template_id: data.template_id,
          collection_name: data.collection?.collection_name || collection_name,
          schema_name: data.schema?.schema_name,
          immutable_data: data.immutable_data,
          max_supply: data.max_supply,
          issued_supply: data.issued_supply,
          is_transferable: data.is_transferable,
          is_burnable: data.is_burnable,
          created_at_time: data.created_at_time,
        };
      } catch {
        // Fallback: read directly from chain
        try {
          const rows = await getTableRows(rpcEndpoint, {
            code: 'atomicassets', scope: collection_name, table: 'templates',
            lower_bound: template_id, upper_bound: template_id, limit: 1,
          });
          if (rows.length === 0) return { error: `Template "${template_id}" not found in collection "${collection_name}"` };
          const t = rows[0];
          return {
            template_id: t.template_id,
            collection_name,
            schema_name: t.schema_name,
            max_supply: t.max_supply,
            issued_supply: t.issued_supply,
            is_transferable: t.transferable === 1,
            is_burnable: t.burnable === 1,
            source: 'rpc',
            note: 'Data from RPC (immutable_data is serialized binary)',
          };
        } catch (rpcErr: any) {
          return { error: `Failed to get template: ${rpcErr.message}` };
        }
      }
    },
  });

  // ── 5. nft_list_templates ──
  api.registerTool({
    name: 'nft_list_templates',
    description: 'List templates in a collection, optionally filtered by schema.',
    parameters: {
      type: 'object',
      required: ['collection_name'],
      properties: {
        collection_name: { type: 'string', description: 'Collection name' },
        schema_name: { type: 'string', description: 'Filter by schema name' },
        limit: { type: 'number', description: 'Max results (default 20, max 100)' },
        page: { type: 'number', description: 'Page number (default 1)' },
      },
    },
    handler: async ({ collection_name, schema_name, limit, page }: {
      collection_name: string; schema_name?: string; limit?: number; page?: number;
    }) => {
      if (!collection_name) return { error: 'collection_name is required' };
      const params: Record<string, string> = {
        collection_name,
        limit: String(Math.min(Math.max(limit || 20, 1), 100)),
        page: String(Math.max(page || 1, 1)),
        order: 'desc',
        sort: 'created',
      };
      if (schema_name) params.schema_name = schema_name;

      try {
        const data = await atomicGet(atomicEndpoints, '/atomicassets/v1/templates', params);
        const templates = Array.isArray(data) ? data : [];
        if (templates.length > 0) {
          return {
            templates: templates.map((t: any) => ({
              template_id: t.template_id,
              schema_name: t.schema?.schema_name,
              immutable_data: t.immutable_data,
              max_supply: t.max_supply,
              issued_supply: t.issued_supply,
              is_transferable: t.is_transferable,
              is_burnable: t.is_burnable,
            })),
            total: templates.length,
          };
        }
        // AA API returned empty — fall through to RPC
        throw new Error('AA API returned no templates, trying RPC');
      } catch {
        // Fallback: read directly from chain
        try {
          const rows = await getTableRows(rpcEndpoint, {
            code: 'atomicassets', scope: collection_name, table: 'templates',
            limit: Math.min(Math.max(limit || 20, 1), 100),
          });
          return {
            templates: rows.map((t: any) => ({
              template_id: t.template_id,
              schema_name: t.schema_name,
              max_supply: t.max_supply === '0' ? '0' : t.max_supply,
              issued_supply: t.issued_supply,
              is_transferable: t.transferable === 1,
              is_burnable: t.burnable === 1,
              note: 'Data from RPC (immutable_data is serialized binary)',
            })),
            total: rows.length,
            source: 'rpc',
          };
        } catch (rpcErr: any) {
          return { error: `Failed to list templates: ${rpcErr.message}` };
        }
      }
    },
  });

  // ── 6. nft_get_asset ──
  api.registerTool({
    name: 'nft_get_asset',
    description: 'Get full details of a specific NFT asset by its ID, including owner, collection, template data, and mutable data.',
    parameters: {
      type: 'object',
      required: ['asset_id'],
      properties: {
        asset_id: { type: 'string', description: 'Asset ID' },
      },
    },
    handler: async ({ asset_id }: { asset_id: string }) => {
      if (!asset_id) return { error: 'asset_id is required' };
      try {
        const data = await atomicGet(atomicEndpoints, `/atomicassets/v1/assets/${encodeURIComponent(asset_id)}`);
        return {
          asset_id: data.asset_id,
          owner: data.owner,
          collection: data.collection ? {
            collection_name: data.collection.collection_name,
            author: data.collection.author,
          } : null,
          schema: data.schema ? { schema_name: data.schema.schema_name } : null,
          template: data.template ? {
            template_id: data.template.template_id,
            immutable_data: data.template.immutable_data,
          } : null,
          immutable_data: data.immutable_data,
          mutable_data: data.mutable_data,
          is_transferable: data.is_transferable,
          is_burnable: data.is_burnable,
          burned_at_time: data.burned_at_time,
        };
      } catch (err: any) {
        return { error: `Failed to get asset: ${err.message}` };
      }
    },
  });

  // ── 7. nft_list_assets ──
  api.registerTool({
    name: 'nft_list_assets',
    description: 'List/search NFT assets. Filter by owner, collection, template, or schema.',
    parameters: {
      type: 'object',
      properties: {
        owner: { type: 'string', description: 'Filter by owner account' },
        collection_name: { type: 'string', description: 'Filter by collection name' },
        template_id: { type: 'string', description: 'Filter by template ID' },
        schema_name: { type: 'string', description: 'Filter by schema name' },
        limit: { type: 'number', description: 'Max results (default 20, max 100)' },
        page: { type: 'number', description: 'Page number (default 1)' },
      },
    },
    handler: async ({ owner, collection_name, template_id, schema_name, limit, page }: {
      owner?: string; collection_name?: string; template_id?: string;
      schema_name?: string; limit?: number; page?: number;
    }) => {
      const params: Record<string, string> = {
        limit: String(Math.min(Math.max(limit || 20, 1), 100)),
        page: String(Math.max(page || 1, 1)),
        order: 'desc',
        sort: 'asset_id',
      };
      if (owner) params.owner = owner;
      if (collection_name) params.collection_name = collection_name;
      if (template_id) params.template_id = template_id;
      if (schema_name) params.schema_name = schema_name;

      try {
        const data = await atomicGet(atomicEndpoints, '/atomicassets/v1/assets', params);
        const assets = Array.isArray(data) ? data : [];
        return {
          assets: assets.map((a: any) => ({
            asset_id: a.asset_id,
            owner: a.owner,
            collection_name: a.collection?.collection_name,
            schema_name: a.schema?.schema_name,
            template_id: a.template?.template_id,
            name: a.immutable_data?.name || a.data?.name || a.template?.immutable_data?.name,
            immutable_data: a.immutable_data,
            mutable_data: a.mutable_data,
          })),
          total: assets.length,
        };
      } catch (err: any) {
        return { error: `Failed to list assets: ${err.message}` };
      }
    },
  });

  // ── 8. nft_get_sale ──
  api.registerTool({
    name: 'nft_get_sale',
    description: 'Get details of a specific AtomicMarket sale listing by sale ID. Returns full asset metadata, price, seller, buyer, and state.',
    parameters: {
      type: 'object',
      required: ['sale_id'],
      properties: {
        sale_id: { type: 'string', description: 'Sale ID' },
      },
    },
    handler: async ({ sale_id }: { sale_id: string }) => {
      if (!sale_id) return { error: 'sale_id is required' };
      try {
        const data = await atomicGet(atomicEndpoints, `/atomicmarket/v1/sales/${encodeURIComponent(sale_id)}`);
        return {
          sale_id: data.sale_id,
          seller: data.seller,
          buyer: data.buyer,
          listing_price: data.listing_price,
          listing_symbol: data.listing_symbol,
          price: data.price,
          collection_name: data.collection_name || data.collection?.collection_name,
          assets: (data.assets || []).map((a: any) => ({
            asset_id: a.asset_id,
            name: a.name || a.data?.name || a.immutable_data?.name,
            template_id: a.template?.template_id,
            data: a.data || a.immutable_data,
          })),
          state: data.state,
          offer_id: data.offer_id,
          created_at_time: data.created_at_time,
          updated_at_time: data.updated_at_time,
        };
      } catch (err: any) {
        // Fallback to RPC
        try {
          const rows = await getTableRows(rpcEndpoint, {
            code: 'atomicmarket', scope: 'atomicmarket', table: 'sales',
            lower_bound: sale_id, upper_bound: sale_id, limit: 1,
          });
          if (rows.length === 0) return { error: `Sale #${sale_id} not found` };
          return rows[0];
        } catch {
          return { error: `Failed to get sale: ${err.message}` };
        }
      }
    },
  });

  // ── 9. nft_search_sales ──
  api.registerTool({
    name: 'nft_search_sales',
    description: 'Search AtomicMarket sales. Filter by collection, seller, price range, state, symbol. Returns rich asset metadata.',
    parameters: {
      type: 'object',
      properties: {
        collection_name: { type: 'string', description: 'Filter by collection name' },
        seller: { type: 'string', description: 'Filter by seller account' },
        buyer: { type: 'string', description: 'Filter by buyer account' },
        min_price: { type: 'string', description: 'Minimum price filter (e.g. "10.0000")' },
        max_price: { type: 'string', description: 'Maximum price filter (e.g. "1000.0000")' },
        symbol: { type: 'string', description: 'Token symbol filter (e.g. "XPR")' },
        state: { type: 'string', description: 'Sale state: 0=waiting, 1=listed, 2=canceled, 3=sold (default: 1)' },
        limit: { type: 'number', description: 'Max results (default 20, max 100)' },
      },
    },
    handler: async ({ collection_name, seller, buyer, min_price, max_price, symbol, state, limit }: {
      collection_name?: string; seller?: string; buyer?: string;
      min_price?: string; max_price?: string; symbol?: string; state?: string; limit?: number;
    }) => {
      const params: Record<string, string> = {
        state: state || '1',
        limit: String(Math.min(Math.max(limit || 20, 1), 100)),
        order: 'desc',
        sort: 'created',
      };
      if (collection_name) params.collection_name = collection_name;
      if (seller) params.seller = seller;
      if (buyer) params.buyer = buyer;
      if (symbol) params.symbol = symbol.toUpperCase();
      if (min_price) params.min_price = min_price;
      if (max_price) params.max_price = max_price;

      try {
        const data = await atomicGet(atomicEndpoints, '/atomicmarket/v1/sales', params);
        const sales = Array.isArray(data) ? data : [];
        return {
          sales: sales.map((s: any) => ({
            sale_id: s.sale_id,
            seller: s.seller,
            buyer: s.buyer,
            listing_price: s.listing_price,
            price: s.price,
            collection_name: s.collection_name || s.collection?.collection_name,
            assets: (s.assets || []).map((a: any) => ({
              asset_id: a.asset_id,
              name: a.name || a.data?.name || a.immutable_data?.name,
              template_id: a.template?.template_id,
            })),
            state: s.state,
            created_at_time: s.created_at_time,
          })),
          total: sales.length,
        };
      } catch (err: any) {
        return { error: `Failed to search sales: ${err.message}` };
      }
    },
  });

  // ── 10. nft_list_auctions ──
  api.registerTool({
    name: 'nft_list_auctions',
    description: 'List AtomicMarket auctions. Filter by collection, seller, or state.',
    parameters: {
      type: 'object',
      properties: {
        collection_name: { type: 'string', description: 'Filter by collection name' },
        seller: { type: 'string', description: 'Filter by seller account' },
        state: { type: 'string', description: 'Auction state: 0=waiting, 1=active, 2=canceled, 3=sold, 4=invalid (default: 1)' },
        limit: { type: 'number', description: 'Max results (default 20, max 100)' },
      },
    },
    handler: async ({ collection_name, seller, state, limit }: {
      collection_name?: string; seller?: string; state?: string; limit?: number;
    }) => {
      const params: Record<string, string> = {
        state: state || '1',
        limit: String(Math.min(Math.max(limit || 20, 1), 100)),
        order: 'desc',
        sort: 'created',
      };
      if (collection_name) params.collection_name = collection_name;
      if (seller) params.seller = seller;

      try {
        const data = await atomicGet(atomicEndpoints, '/atomicmarket/v1/auctions', params);
        const auctions = Array.isArray(data) ? data : [];
        return {
          auctions: auctions.map((a: any) => ({
            auction_id: a.auction_id,
            seller: a.seller,
            buyer: a.buyer,
            price: a.price,
            collection_name: a.collection_name || a.collection?.collection_name,
            assets: (a.assets || []).map((asset: any) => ({
              asset_id: asset.asset_id,
              name: asset.name || asset.data?.name || asset.immutable_data?.name,
            })),
            bids: a.bids || [],
            state: a.state,
            end_time: a.end_time,
            created_at_time: a.created_at_time,
          })),
          total: auctions.length,
        };
      } catch (err: any) {
        return { error: `Failed to list auctions: ${err.message}` };
      }
    },
  });

  // ── 11. nft_get_auction ──
  api.registerTool({
    name: 'nft_get_auction',
    description: 'Get details of a specific AtomicMarket auction including bids, assets, and timing.',
    parameters: {
      type: 'object',
      required: ['auction_id'],
      properties: {
        auction_id: { type: 'string', description: 'Auction ID' },
      },
    },
    handler: async ({ auction_id }: { auction_id: string }) => {
      if (!auction_id) return { error: 'auction_id is required' };
      try {
        const data = await atomicGet(atomicEndpoints, `/atomicmarket/v1/auctions/${encodeURIComponent(auction_id)}`);
        return {
          auction_id: data.auction_id,
          seller: data.seller,
          buyer: data.buyer,
          price: data.price,
          collection_name: data.collection_name || data.collection?.collection_name,
          assets: (data.assets || []).map((a: any) => ({
            asset_id: a.asset_id,
            name: a.name || a.data?.name || a.immutable_data?.name,
            template_id: a.template?.template_id,
            data: a.data || a.immutable_data,
          })),
          bids: data.bids || [],
          state: data.state,
          end_time: data.end_time,
          created_at_time: data.created_at_time,
          updated_at_time: data.updated_at_time,
        };
      } catch (err: any) {
        return { error: `Failed to get auction: ${err.message}` };
      }
    },
  });

  // ════════════════════════════════════════════════
  // WRITE TOOLS (12)
  // ════════════════════════════════════════════════

  // ── 12. nft_create_collection ──
  api.registerTool({
    name: 'nft_create_collection',
    description: 'Create a new AtomicAssets collection. The agent account becomes the author and authorized account. Collection names are permanent (1-12 chars, a-z1-5).',
    parameters: {
      type: 'object',
      required: ['collection_name', 'confirmed'],
      properties: {
        collection_name: { type: 'string', description: 'Unique collection name (1-12 chars, a-z and 1-5 only, permanent)' },
        display_name: { type: 'string', description: 'Human-readable display name' },
        description: { type: 'string', description: 'Collection description' },
        image: { type: 'string', description: 'Collection image (IPFS CID or URL)' },
        market_fee: { type: 'number', description: 'Market fee as decimal (e.g. 0.05 = 5%, default 0.05)' },
        allow_notify: { type: 'boolean', description: 'Allow contract notifications (default true)' },
        confirmed: { type: 'boolean', description: 'Must be true to proceed' },
      },
    },
    handler: async ({ collection_name, display_name, description, image, market_fee, allow_notify, confirmed }: {
      collection_name: string; display_name?: string; description?: string; image?: string;
      market_fee?: number; allow_notify?: boolean; confirmed?: boolean;
    }) => {
      if (!confirmed) return { error: 'Confirmation required. Set confirmed=true to create this collection.' };
      if (!isValidEosioName(collection_name)) return { error: 'Invalid collection_name. Must be 1-12 characters, a-z and 1-5 only.' };

      try {
        const session = await getNftSession();
        const data: Array<{ key: string; value: [string, any] }> = [];
        if (display_name) data.push({ key: 'name', value: ['string', display_name] });
        if (image) data.push({ key: 'image', value: ['string', image] });
        if (description) data.push({ key: 'description', value: ['string', description] });

        const result = await session.api.transact({
          actions: [{
            account: 'atomicassets',
            name: 'createcol',
            authorization: [{ actor: session.account, permission: session.permission }],
            data: {
              author: session.account,
              collection_name,
              allow_notify: allow_notify !== false,
              authorized_accounts: [session.account],
              notify_accounts: [],
              market_fee: market_fee ?? 0.05,
              data,
            },
          }],
        }, { blocksBehind: 3, expireSeconds: 30 });

        return { transaction_id: result.transaction_id || result.processed?.id, collection_name, author: session.account };
      } catch (err: any) {
        return { error: `Failed to create collection: ${err.message}` };
      }
    },
  });

  // ── 13. nft_create_schema ──
  api.registerTool({
    name: 'nft_create_schema',
    description: 'Create a schema within a collection. Defines attribute names and types for templates/assets. Common types: string, image, ipfs, uint64, uint32, double, bool.',
    parameters: {
      type: 'object',
      required: ['collection_name', 'schema_name', 'schema_format', 'confirmed'],
      properties: {
        collection_name: { type: 'string', description: 'Collection to add schema to' },
        schema_name: { type: 'string', description: 'Schema name (1-12 chars, a-z1-5)' },
        schema_format: {
          type: 'array',
          description: 'Array of {name, type} attribute definitions. E.g. [{"name":"name","type":"string"},{"name":"image","type":"image"},{"name":"rarity","type":"string"}]',
        },
        confirmed: { type: 'boolean', description: 'Must be true to proceed' },
      },
    },
    handler: async ({ collection_name, schema_name, schema_format, confirmed }: {
      collection_name: string; schema_name: string;
      schema_format: Array<{ name: string; type: string }>; confirmed?: boolean;
    }) => {
      if (!confirmed) return { error: 'Confirmation required. Set confirmed=true to create this schema.' };
      if (!isValidEosioName(collection_name)) return { error: 'Invalid collection_name' };
      if (!isValidEosioName(schema_name)) return { error: 'Invalid schema_name. Must be 1-12 characters, a-z and 1-5 only.' };
      if (!Array.isArray(schema_format) || schema_format.length === 0) {
        return { error: 'schema_format must be a non-empty array of {name, type} objects' };
      }

      try {
        const session = await getNftSession();
        const result = await session.api.transact({
          actions: [{
            account: 'atomicassets',
            name: 'createschema',
            authorization: [{ actor: session.account, permission: session.permission }],
            data: {
              authorized_creator: session.account,
              collection_name,
              schema_name,
              schema_format,
            },
          }],
        }, { blocksBehind: 3, expireSeconds: 30 });

        return { transaction_id: result.transaction_id || result.processed?.id, collection_name, schema_name, attributes: schema_format.length };
      } catch (err: any) {
        return { error: `Failed to create schema: ${err.message}` };
      }
    },
  });

  // ── 14. nft_create_template ──
  api.registerTool({
    name: 'nft_create_template',
    description: 'Create a template with immutable data. Pass a plain data object — types are auto-mapped from the schema. E.g. {name: "My NFT", img: "QmHash", rarity: "legendary"}.',
    parameters: {
      type: 'object',
      required: ['collection_name', 'schema_name', 'immutable_data', 'confirmed'],
      properties: {
        collection_name: { type: 'string', description: 'Collection name' },
        schema_name: { type: 'string', description: 'Schema name within the collection' },
        immutable_data: { type: 'object', description: 'Key-value pairs matching schema attributes. E.g. {"name":"Cool NFT","image":"QmHash"}' },
        max_supply: { type: 'number', description: 'Maximum supply (0 = unlimited, default 0)' },
        transferable: { type: 'boolean', description: 'Can assets be transferred (default true)' },
        burnable: { type: 'boolean', description: 'Can assets be burned (default true)' },
        confirmed: { type: 'boolean', description: 'Must be true to proceed' },
      },
    },
    handler: async ({ collection_name, schema_name, immutable_data, max_supply, transferable, burnable, confirmed }: {
      collection_name: string; schema_name: string; immutable_data: Record<string, any>;
      max_supply?: number; transferable?: boolean; burnable?: boolean; confirmed?: boolean;
    }) => {
      if (!confirmed) return { error: 'Confirmation required. Set confirmed=true to create this template.' };
      if (!collection_name || !schema_name) return { error: 'collection_name and schema_name are required' };
      if (!immutable_data || typeof immutable_data !== 'object') return { error: 'immutable_data must be an object' };

      try {
        // Fetch schema to get attribute types (AA API with RPC fallback)
        const schemaFormat = await fetchSchemaFormat(atomicEndpoints, rpcEndpoint, collection_name, schema_name);

        const attributeMap = buildAttributeMap(immutable_data, schemaFormat);

        const session = await getNftSession();
        const result = await session.api.transact({
          actions: [{
            account: 'atomicassets',
            name: 'createtempl',
            authorization: [{ actor: session.account, permission: session.permission }],
            data: {
              authorized_creator: session.account,
              collection_name,
              schema_name,
              transferable: transferable !== false,
              burnable: burnable !== false,
              max_supply: max_supply || 0,
              immutable_data: attributeMap,
            },
          }],
        }, { blocksBehind: 3, expireSeconds: 30 });

        const txId = result.transaction_id || result.processed?.id;

        // Read template_id from on-chain table (AA API is too slow for newly created templates)
        let template_id: number | undefined;
        try {
          const rows = await getTableRows(rpcEndpoint, {
            code: 'atomicassets', scope: collection_name, table: 'templates',
            limit: 1, key_type: undefined, index_position: undefined,
          });
          // Templates table uses template_id as primary key — get the highest one (most recent)
          if (rows.length > 0) {
            // Read in reverse to get highest template_id
            const allRows = await getTableRows(rpcEndpoint, {
              code: 'atomicassets', scope: collection_name, table: 'templates',
              limit: 100, key_type: undefined, index_position: undefined,
            });
            if (allRows.length > 0) {
              template_id = allRows[allRows.length - 1].template_id;
            }
          }
        } catch { /* non-critical — template_id is a convenience */ }

        return {
          transaction_id: txId,
          template_id,
          collection_name, schema_name,
          immutable_data,
          max_supply: max_supply || 0,
          note: template_id
            ? `Template created with ID ${template_id}. Use this ID for nft_mint.`
            : 'Template created. Read the templates table to get the template_id.',
        };
      } catch (err: any) {
        return { error: `Failed to create template: ${err.message}` };
      }
    },
  });

  // ── 15. nft_mint ──
  api.registerTool({
    name: 'nft_mint',
    description: 'Mint a new NFT from an existing template. Optionally include mutable data and specify a recipient (defaults to self).',
    parameters: {
      type: 'object',
      required: ['collection_name', 'schema_name', 'template_id', 'confirmed'],
      properties: {
        collection_name: { type: 'string', description: 'Collection name' },
        schema_name: { type: 'string', description: 'Schema name' },
        template_id: { type: 'number', description: 'Template ID to mint from' },
        new_asset_owner: { type: 'string', description: 'Recipient account (default: self)' },
        mutable_data: { type: 'object', description: 'Optional mutable data key-value pairs' },
        confirmed: { type: 'boolean', description: 'Must be true to proceed' },
      },
    },
    handler: async ({ collection_name, schema_name, template_id, new_asset_owner, mutable_data, confirmed }: {
      collection_name: string; schema_name: string; template_id: number;
      new_asset_owner?: string; mutable_data?: Record<string, any>; confirmed?: boolean;
    }) => {
      if (!confirmed) return { error: 'Confirmation required. Set confirmed=true to mint this NFT.' };
      if (!collection_name || !schema_name || template_id == null) {
        return { error: 'collection_name, schema_name, and template_id are required' };
      }

      try {
        const session = await getNftSession();
        const owner = new_asset_owner || session.account;

        // Build mutable data attribute map if provided
        let immutable_data: Array<{ key: string; value: [string, any] }> = [];
        let mutable_data_map: Array<{ key: string; value: [string, any] }> = [];

        if (mutable_data && Object.keys(mutable_data).length > 0) {
          // Fetch schema to map types (AA API with RPC fallback)
          const schemaFormat = await fetchSchemaFormat(atomicEndpoints, rpcEndpoint, collection_name, schema_name);
          mutable_data_map = buildAttributeMap(mutable_data, schemaFormat);
        }

        const result = await session.api.transact({
          actions: [{
            account: 'atomicassets',
            name: 'mintasset',
            authorization: [{ actor: session.account, permission: session.permission }],
            data: {
              authorized_minter: session.account,
              collection_name,
              schema_name,
              template_id,
              new_asset_owner: owner,
              immutable_data,
              mutable_data: mutable_data_map,
              tokens_to_back: [],
            },
          }],
        }, { blocksBehind: 3, expireSeconds: 30 });

        const txId = result.transaction_id || result.processed?.id;

        // Extract new asset_id from the transaction traces (logmint inline action)
        let asset_id: string | undefined;
        try {
          const traces = result.processed?.action_traces || [];
          for (const trace of traces) {
            const inlines = trace.inline_traces || [];
            for (const inl of inlines) {
              if (inl.act?.name === 'logmint' && inl.act?.data?.asset_id) {
                asset_id = String(inl.act.data.asset_id);
                break;
              }
            }
            if (asset_id) break;
          }
        } catch { /* non-critical */ }

        // Fallback: read the assets table for this owner scoped by collection
        if (!asset_id) {
          try {
            // The global config table holds the next asset_id counter
            const configRows = await getTableRows(rpcEndpoint, {
              code: 'atomicassets', scope: 'atomicassets', table: 'config', limit: 1,
            });
            if (configRows.length > 0 && configRows[0].asset_counter) {
              // The asset just minted has ID = counter - 1
              asset_id = String(Number(configRows[0].asset_counter) - 1);
            }
          } catch { /* non-critical */ }
        }

        return {
          transaction_id: txId,
          asset_id,
          collection_name, schema_name, template_id,
          new_asset_owner: owner,
          note: asset_id
            ? `NFT minted with asset ID ${asset_id}. Use this ID for transfers, sales, or delivery.`
            : 'NFT minted successfully. Check your assets to find the new asset ID.',
        };
      } catch (err: any) {
        return { error: `Failed to mint NFT: ${err.message}` };
      }
    },
  });

  // ── 16. nft_transfer ──
  api.registerTool({
    name: 'nft_transfer',
    description: 'Transfer one or more NFT assets to another account.',
    parameters: {
      type: 'object',
      required: ['to', 'asset_ids', 'confirmed'],
      properties: {
        to: { type: 'string', description: 'Recipient account' },
        asset_ids: { type: 'array', description: 'Array of asset IDs to transfer', items: { type: 'string' } },
        memo: { type: 'string', description: 'Transfer memo (default empty)' },
        confirmed: { type: 'boolean', description: 'Must be true to proceed' },
      },
    },
    handler: async ({ to, asset_ids, memo, confirmed }: {
      to: string; asset_ids: string[]; memo?: string; confirmed?: boolean;
    }) => {
      if (!confirmed) return { error: 'Confirmation required. Set confirmed=true to transfer these NFTs.' };
      if (!to || !isValidEosioName(to)) return { error: 'Invalid recipient account' };
      if (!Array.isArray(asset_ids) || asset_ids.length === 0) return { error: 'asset_ids must be a non-empty array' };

      try {
        const session = await getNftSession();
        const result = await session.api.transact({
          actions: [{
            account: 'atomicassets',
            name: 'transfer',
            authorization: [{ actor: session.account, permission: session.permission }],
            data: {
              from: session.account,
              to,
              asset_ids: asset_ids.map(id => Number(id)),
              memo: memo || '',
            },
          }],
        }, { blocksBehind: 3, expireSeconds: 30 });

        return { transaction_id: result.transaction_id || result.processed?.id, from: session.account, to, asset_ids };
      } catch (err: any) {
        return { error: `Failed to transfer NFTs: ${err.message}` };
      }
    },
  });

  // ── 17. nft_burn ──
  api.registerTool({
    name: 'nft_burn',
    description: 'Permanently destroy (burn) an NFT asset you own. This cannot be undone.',
    parameters: {
      type: 'object',
      required: ['asset_id', 'confirmed'],
      properties: {
        asset_id: { type: 'string', description: 'Asset ID to burn' },
        confirmed: { type: 'boolean', description: 'Must be true to proceed' },
      },
    },
    handler: async ({ asset_id, confirmed }: { asset_id: string; confirmed?: boolean }) => {
      if (!confirmed) return { error: 'Confirmation required. Set confirmed=true to burn this NFT. This action is PERMANENT.' };
      if (!asset_id) return { error: 'asset_id is required' };

      try {
        const session = await getNftSession();
        const result = await session.api.transact({
          actions: [{
            account: 'atomicassets',
            name: 'burnasset',
            authorization: [{ actor: session.account, permission: session.permission }],
            data: {
              asset_owner: session.account,
              asset_id: Number(asset_id),
            },
          }],
        }, { blocksBehind: 3, expireSeconds: 30 });

        return { transaction_id: result.transaction_id || result.processed?.id, burned_asset_id: asset_id };
      } catch (err: any) {
        return { error: `Failed to burn NFT: ${err.message}` };
      }
    },
  });

  // ── 18. nft_list_for_sale ──
  api.registerTool({
    name: 'nft_list_for_sale',
    description: 'List NFT(s) for sale at a fixed price on AtomicMarket. Combines createoffer + announcesale in one transaction. Price format: "100.0000 XPR".',
    parameters: {
      type: 'object',
      required: ['asset_ids', 'price', 'confirmed'],
      properties: {
        asset_ids: { type: 'array', description: 'Array of asset IDs to sell', items: { type: 'string' } },
        price: { type: 'string', description: 'Listing price with full precision, e.g. "100.0000 XPR" or "50.000000 XUSDC"' },
        marketplace: { type: 'string', description: 'Maker marketplace account (optional)' },
        confirmed: { type: 'boolean', description: 'Must be true to proceed' },
      },
    },
    handler: async ({ asset_ids, price, marketplace, confirmed }: {
      asset_ids: string[]; price: string; marketplace?: string; confirmed?: boolean;
    }) => {
      if (!confirmed) return { error: 'Confirmation required. Set confirmed=true to list these NFTs for sale.' };
      if (!Array.isArray(asset_ids) || asset_ids.length === 0) return { error: 'asset_ids must be a non-empty array' };
      if (!price) return { error: 'price is required (e.g. "100.0000 XPR")' };

      try {
        const parsed = parsePrice(price);
        const session = await getNftSession();
        const numericAssetIds = asset_ids.map(id => Number(id));

        // announcesale MUST come before createoffer — when createoffer notifies
        // atomicmarket, it checks that a sale was already announced for these assets.
        const result = await session.api.transact({
          actions: [
            {
              account: 'atomicmarket',
              name: 'announcesale',
              authorization: [{ actor: session.account, permission: session.permission }],
              data: {
                seller: session.account,
                asset_ids: numericAssetIds,
                listing_price: `${parsed.amount} ${parsed.symbol}`,
                settlement_symbol: `${parsed.precision},${parsed.symbol}`,
                maker_marketplace: marketplace || '',
              },
            },
            {
              account: 'atomicassets',
              name: 'createoffer',
              authorization: [{ actor: session.account, permission: session.permission }],
              data: {
                sender: session.account,
                recipient: 'atomicmarket',
                sender_asset_ids: numericAssetIds,
                recipient_asset_ids: [],
                memo: 'sale',
              },
            },
          ],
        }, { blocksBehind: 3, expireSeconds: 30 });

        return { transaction_id: result.transaction_id || result.processed?.id, asset_ids, price };
      } catch (err: any) {
        return { error: `Failed to list for sale: ${err.message}` };
      }
    },
  });

  // ── 19. nft_cancel_sale ──
  api.registerTool({
    name: 'nft_cancel_sale',
    description: 'Cancel a sale listing on AtomicMarket. Only the seller can cancel.',
    parameters: {
      type: 'object',
      required: ['sale_id', 'confirmed'],
      properties: {
        sale_id: { type: 'string', description: 'Sale ID to cancel' },
        confirmed: { type: 'boolean', description: 'Must be true to proceed' },
      },
    },
    handler: async ({ sale_id, confirmed }: { sale_id: string; confirmed?: boolean }) => {
      if (!confirmed) return { error: 'Confirmation required. Set confirmed=true to cancel this sale.' };
      if (!sale_id) return { error: 'sale_id is required' };

      try {
        const session = await getNftSession();
        const result = await session.api.transact({
          actions: [{
            account: 'atomicmarket',
            name: 'cancelsale',
            authorization: [{ actor: session.account, permission: session.permission }],
            data: {
              sale_id: Number(sale_id),
            },
          }],
        }, { blocksBehind: 3, expireSeconds: 30 });

        return { transaction_id: result.transaction_id || result.processed?.id, cancelled_sale_id: sale_id };
      } catch (err: any) {
        return { error: `Failed to cancel sale: ${err.message}` };
      }
    },
  });

  // ── 20. nft_purchase ──
  api.registerTool({
    name: 'nft_purchase',
    description: 'Purchase an NFT from an AtomicMarket sale. Combines token deposit + purchasesale in one transaction.',
    parameters: {
      type: 'object',
      required: ['sale_id', 'price', 'confirmed'],
      properties: {
        sale_id: { type: 'string', description: 'Sale ID to purchase' },
        price: { type: 'string', description: 'Exact listing price (must match), e.g. "100.0000 XPR"' },
        taker_marketplace: { type: 'string', description: 'Taker marketplace account (optional)' },
        confirmed: { type: 'boolean', description: 'Must be true to proceed' },
      },
    },
    handler: async ({ sale_id, price, taker_marketplace, confirmed }: {
      sale_id: string; price: string; taker_marketplace?: string; confirmed?: boolean;
    }) => {
      if (!confirmed) return { error: 'Confirmation required. Set confirmed=true to purchase this NFT.' };
      if (!sale_id) return { error: 'sale_id is required' };
      if (!price) return { error: 'price is required (must match listing price exactly)' };

      try {
        const parsed = parsePrice(price);
        const session = await getNftSession();

        const result = await session.api.transact({
          actions: [
            {
              account: parsed.contract,
              name: 'transfer',
              authorization: [{ actor: session.account, permission: session.permission }],
              data: {
                from: session.account,
                to: 'atomicmarket',
                quantity: `${parsed.amount} ${parsed.symbol}`,
                memo: 'deposit',
              },
            },
            {
              account: 'atomicmarket',
              name: 'purchasesale',
              authorization: [{ actor: session.account, permission: session.permission }],
              data: {
                buyer: session.account,
                sale_id: Number(sale_id),
                intended_delphi_median: 0,
                taker_marketplace: taker_marketplace || '',
              },
            },
          ],
        }, { blocksBehind: 3, expireSeconds: 30 });

        return { transaction_id: result.transaction_id || result.processed?.id, sale_id, price, buyer: session.account };
      } catch (err: any) {
        return { error: `Failed to purchase NFT: ${err.message}` };
      }
    },
  });

  // ── 21. nft_create_auction ──
  api.registerTool({
    name: 'nft_create_auction',
    description: 'Start a timed auction on AtomicMarket. Transfers assets to atomicmarket and announces the auction.',
    parameters: {
      type: 'object',
      required: ['asset_ids', 'starting_bid', 'duration_seconds', 'confirmed'],
      properties: {
        asset_ids: { type: 'array', description: 'Array of asset IDs to auction', items: { type: 'string' } },
        starting_bid: { type: 'string', description: 'Starting bid price, e.g. "10.0000 XPR"' },
        duration_seconds: { type: 'number', description: 'Auction duration in seconds (e.g. 86400 = 24 hours)' },
        marketplace: { type: 'string', description: 'Maker marketplace account (optional)' },
        confirmed: { type: 'boolean', description: 'Must be true to proceed' },
      },
    },
    handler: async ({ asset_ids, starting_bid, duration_seconds, marketplace, confirmed }: {
      asset_ids: string[]; starting_bid: string; duration_seconds: number;
      marketplace?: string; confirmed?: boolean;
    }) => {
      if (!confirmed) return { error: 'Confirmation required. Set confirmed=true to create this auction.' };
      if (!Array.isArray(asset_ids) || asset_ids.length === 0) return { error: 'asset_ids must be a non-empty array' };
      if (!starting_bid) return { error: 'starting_bid is required (e.g. "10.0000 XPR")' };
      if (!duration_seconds || duration_seconds <= 0) return { error: 'duration_seconds must be a positive number' };

      try {
        const parsed = parsePrice(starting_bid);
        const session = await getNftSession();
        const numericAssetIds = asset_ids.map(id => Number(id));

        // announceauct MUST come before transfer — when atomicmarket receives the
        // assets via transfer notification, it checks for a previously announced auction.
        const result = await session.api.transact({
          actions: [
            {
              account: 'atomicmarket',
              name: 'announceauct',
              authorization: [{ actor: session.account, permission: session.permission }],
              data: {
                seller: session.account,
                asset_ids: numericAssetIds,
                starting_bid: `${parsed.amount} ${parsed.symbol}`,
                duration: duration_seconds,
                maker_marketplace: marketplace || '',
              },
            },
            {
              account: 'atomicassets',
              name: 'transfer',
              authorization: [{ actor: session.account, permission: session.permission }],
              data: {
                from: session.account,
                to: 'atomicmarket',
                asset_ids: numericAssetIds,
                memo: 'auction',
              },
            },
          ],
        }, { blocksBehind: 3, expireSeconds: 30 });

        return {
          transaction_id: result.transaction_id || result.processed?.id,
          asset_ids, starting_bid, duration_seconds,
        };
      } catch (err: any) {
        return { error: `Failed to create auction: ${err.message}` };
      }
    },
  });

  // ── 22. nft_bid ──
  api.registerTool({
    name: 'nft_bid',
    description: 'Place a bid on an AtomicMarket auction. Combines token deposit + auctionbid in one transaction. Bid must be higher than current highest bid.',
    parameters: {
      type: 'object',
      required: ['auction_id', 'bid_amount', 'confirmed'],
      properties: {
        auction_id: { type: 'string', description: 'Auction ID to bid on' },
        bid_amount: { type: 'string', description: 'Bid amount, e.g. "50.0000 XPR" (must exceed current highest bid)' },
        taker_marketplace: { type: 'string', description: 'Taker marketplace account (optional)' },
        confirmed: { type: 'boolean', description: 'Must be true to proceed' },
      },
    },
    handler: async ({ auction_id, bid_amount, taker_marketplace, confirmed }: {
      auction_id: string; bid_amount: string; taker_marketplace?: string; confirmed?: boolean;
    }) => {
      if (!confirmed) return { error: 'Confirmation required. Set confirmed=true to place this bid.' };
      if (!auction_id) return { error: 'auction_id is required' };
      if (!bid_amount) return { error: 'bid_amount is required (e.g. "50.0000 XPR")' };

      try {
        const parsed = parsePrice(bid_amount);
        const session = await getNftSession();

        const result = await session.api.transact({
          actions: [
            {
              account: parsed.contract,
              name: 'transfer',
              authorization: [{ actor: session.account, permission: session.permission }],
              data: {
                from: session.account,
                to: 'atomicmarket',
                quantity: `${parsed.amount} ${parsed.symbol}`,
                memo: 'deposit',
              },
            },
            {
              account: 'atomicmarket',
              name: 'auctionbid',
              authorization: [{ actor: session.account, permission: session.permission }],
              data: {
                bidder: session.account,
                auction_id: Number(auction_id),
                bid: `${parsed.amount} ${parsed.symbol}`,
                taker_marketplace: taker_marketplace || '',
              },
            },
          ],
        }, { blocksBehind: 3, expireSeconds: 30 });

        return { transaction_id: result.transaction_id || result.processed?.id, auction_id, bid_amount, bidder: session.account };
      } catch (err: any) {
        return { error: `Failed to place bid: ${err.message}` };
      }
    },
  });

  // ── 23. nft_claim_auction ──
  api.registerTool({
    name: 'nft_claim_auction',
    description: 'Claim won assets (buyer) or sale proceeds (seller) from a completed auction. No risk — just claims what is rightfully yours.',
    parameters: {
      type: 'object',
      required: ['auction_id'],
      properties: {
        auction_id: { type: 'string', description: 'Auction ID to claim' },
      },
    },
    handler: async ({ auction_id }: { auction_id: string }) => {
      if (!auction_id) return { error: 'auction_id is required' };

      try {
        const session = await getNftSession();

        // auctclaimbuy claims assets for the buyer, auctclaimsell claims proceeds for the seller
        // Try both — only the relevant one will succeed
        const actions = [
          {
            account: 'atomicmarket',
            name: 'auctclaimbuy',
            authorization: [{ actor: session.account, permission: session.permission }],
            data: { auction_id: Number(auction_id) },
          },
          {
            account: 'atomicmarket',
            name: 'auctclaimsell',
            authorization: [{ actor: session.account, permission: session.permission }],
            data: { auction_id: Number(auction_id) },
          },
        ];

        // Try buyer claim first
        try {
          const result = await session.api.transact({ actions: [actions[0]] }, { blocksBehind: 3, expireSeconds: 30 });
          return { transaction_id: result.transaction_id || result.processed?.id, auction_id, claim_type: 'buyer' };
        } catch {
          // Not the buyer — try seller claim
        }

        try {
          const result = await session.api.transact({ actions: [actions[1]] }, { blocksBehind: 3, expireSeconds: 30 });
          return { transaction_id: result.transaction_id || result.processed?.id, auction_id, claim_type: 'seller' };
        } catch {
          // Neither buyer nor seller
        }

        return { error: `Could not claim auction #${auction_id} — you may not be the buyer or seller, or the auction may not be completed yet.` };
      } catch (err: any) {
        return { error: `Failed to claim auction: ${err.message}` };
      }
    },
  });
}
