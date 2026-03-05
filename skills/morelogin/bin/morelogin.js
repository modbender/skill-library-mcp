#!/usr/bin/env node
const fs = require('fs');
const http = require('http');
const path = require('path');
const {
  DEFAULT_BASE_URL,
  normalizeStringArray,
  parseArgs,
  parseJsonInput,
  parsePageOptions,
  parseRequiredInt,
  printObject,
  requestApi,
  requireNonEmptyString,
  requirePlainObject,
  splitCsv,
  toBoolean,
  unwrapApiResult,
} = require('./common');


function fail(message, code = 1) {
  console.error(`❌ ${message}`);
  process.exit(code);
}

async function callApi(endpoint, { method = 'POST', body } = {}) {
  const response = await requestApi(endpoint, { method, body });
  const result = unwrapApiResult(response);
  if (!result.success) {
    throw new Error(result.message || 'API request failed');
  }
  return result.data;
}

function ensureProfileIdentity(options) {
  if (options['env-id']) return { envId: requireNonEmptyString(options['env-id'], '--env-id') };
  if (options['unique-id'] !== undefined) {
    return { uniqueId: parseRequiredInt(options['unique-id'], '--unique-id', { min: 1 }) };
  }
  fail('Please provide --env-id or --unique-id');
  return null;
}

function showHelp() {
  console.log(`
🌐 MoreLogin CLI (Official Local API)
Base URL: ${DEFAULT_BASE_URL}

Usage:
  morelogin browser <command> [options]
  morelogin cloudphone <command> [options]
  morelogin proxy <command> [options]
  morelogin group <command> [options]
  morelogin tag <command> [options]

Browser:
  list                    List profiles (/api/env/page)
  start                   Start profile (/api/env/start)
  close                   Close profile (/api/env/close)
  status                  Query run status (/api/env/status)
  detail                  Query details (/api/env/detail)
  create-quick            Quick create (/api/env/create/quick)
  refresh-fingerprint     Refresh fingerprint (/api/env/fingerprint/refresh)
  clear-cache             Clear local cache (/api/env/removeLocalCache)
  clean-cloud-cache       Clean cloud cache (/api/env/cache/cleanCloud)
  delete                  Batch delete to recycle bin (/api/env/removeToRecycleBin/batch)

CloudPhone:
  list                    List (/api/cloudphone/page)
  create                  Create (/api/cloudphone/create)
  start                   Power on (/api/cloudphone/powerOn)
  stop                    Power off (/api/cloudphone/powerOff)
  info                    Details (/api/cloudphone/info)
  adb-info                Get ADB params (device model)
  update-adb              Update ADB status (/api/cloudphone/updateAdb)
  new-machine             New machine one-click (/api/cloudphone/newMachine)
  app-installed           Installed apps list (/api/cloudphone/app/installedList)
  app-start|app-stop|app-restart|app-uninstall


Proxy:
  list                    Query proxy list (/api/proxyInfo/page)
  add                     Add proxy (/api/proxyInfo/add)
  update                  Update proxy (/api/proxyInfo/update)
  delete                  Delete proxy (/api/proxyInfo/delete)

Group:
  list                    Query groups (/api/envgroup/page)
  create                  Create group (/api/envgroup/create)
  edit                    Edit group (/api/envgroup/edit)
  delete                  Delete group (/api/envgroup/delete)

Tag:
  list                    Query tags (/api/envtag/all, GET)
  create                  Create tag (/api/envtag/create)
  edit                    Edit tag (/api/envtag/edit)
  delete                  Delete tag (/api/envtag/delete)

Legacy commands (backward compatible):
  morelogin list/start/stop/info/connect
  Equivalent to browser subcommands.

Security defaults:
  - cloudphone exec command is removed
`);
}

function showConnectTips(data) {
  const debugPort = data?.debugPort || data?.port;
  if (!debugPort) return;
  const browserUrl = `http://127.0.0.1:${debugPort}`;
  console.log(`\nCDP address: ${browserUrl}`);
  console.log(`Puppeteer: puppeteer.connect({ browserURL: "${browserUrl}" })`);
  console.log(`Playwright: chromium.connectOverCDP("${browserUrl}")`);
}

function validateProxyAddPayload(body) {
  requirePlainObject(body, 'proxy add payload');
  requireNonEmptyString(body.proxyIp, 'proxyIp');
  parseRequiredInt(body.proxyPort, 'proxyPort', { min: 1, max: 65535 });
  requireNonEmptyString(body.proxyProvider, 'proxyProvider');
}

function validateProxyUpdatePayload(body) {
  requirePlainObject(body, 'proxy update payload');
  requireNonEmptyString(body.id, 'id');
  requireNonEmptyString(body.proxyIp, 'proxyIp');
  parseRequiredInt(body.proxyPort, 'proxyPort', { min: 1, max: 65535 });
  requireNonEmptyString(body.proxyProvider, 'proxyProvider');
}

function validateGroupCreatePayload(body) {
  requirePlainObject(body, 'group create payload');
  requireNonEmptyString(body.groupName, 'groupName');
}

function validateTagCreatePayload(body) {
  requirePlainObject(body, 'tag create payload');
  requireNonEmptyString(body.tagName, 'tagName');
}




function buildLocalCachePayload(options) {
  const body = ensureProfileIdentity(options);
  const localStorage = toBoolean(options['local-storage'], false);
  const indexedDB = toBoolean(options['indexed-db'], false);
  const cookie = toBoolean(options.cookie, false);
  const extension = toBoolean(options.extension, false);
  const extensionFile = toBoolean(options['extension-file'], false);
  const hasAny = localStorage || indexedDB || cookie || extension || extensionFile;
  if (!hasAny) {
    fail(
      'clear-cache requires at least one cache flag, e.g. --cookie true or --local-storage true'
    );
  }
  return { ...body, localStorage, indexedDB, cookie, extension, extensionFile };
}

function buildCloudCachePayload(options) {
  const body = ensureProfileIdentity(options);
  const hasCookie = options.cookie !== undefined;
  const hasOthers = options.others !== undefined;
  if (!hasCookie && !hasOthers) {
    fail('clean-cloud-cache requires at least one flag: --cookie or --others');
  }
  return {
    ...body,
    cookie: toBoolean(options.cookie, false),
    others: toBoolean(options.others, false),
  };
}

function normalizeProfileIdentityPayload(payload, options, actionName) {
  const body = payload || ensureProfileIdentity(options);
  requirePlainObject(body, `${actionName} payload`);
  if (body.envId !== undefined) {
    body.envId = requireNonEmptyString(body.envId, 'envId');
    return body;
  }
  if (body.uniqueId !== undefined) {
    body.uniqueId = parseRequiredInt(body.uniqueId, 'uniqueId', { min: 1 });
    return body;
  }
  fail(`${actionName} requires envId or uniqueId`);
  return null;
}

function validateLocalCachePayload(payload) {
  requirePlainObject(payload, 'clear-cache payload');
  const localStorage = toBoolean(payload.localStorage, false);
  const indexedDB = toBoolean(payload.indexedDB, false);
  const cookie = toBoolean(payload.cookie, false);
  const extension = toBoolean(payload.extension, false);
  const extensionFile = toBoolean(payload.extensionFile, false);
  if (!localStorage && !indexedDB && !cookie && !extension && !extensionFile) {
    fail('clear-cache payload must include at least one cache flag');
  }
  const body = normalizeProfileIdentityPayload(payload, {}, 'clear-cache');
  return { ...body, localStorage, indexedDB, cookie, extension, extensionFile };
}

function validateCloudCachePayload(payload) {
  requirePlainObject(payload, 'clean-cloud-cache payload');
  if (payload.cookie === undefined && payload.others === undefined) {
    fail('clean-cloud-cache payload must include cookie or others');
  }
  const body = normalizeProfileIdentityPayload(payload, {}, 'clean-cloud-cache');
  return {
    ...body,
    cookie: toBoolean(payload.cookie, false),
    others: toBoolean(payload.others, false),
  };
}

function validatePagePayload(payload, { defaultPageNo = 1, defaultPageSize = 20 } = {}) {
  requirePlainObject(payload, 'payload');
  const pageNo = payload.pageNo === undefined
    ? defaultPageNo
    : parseRequiredInt(payload.pageNo, 'pageNo', { min: 1 });
  const pageSize = payload.pageSize === undefined
    ? defaultPageSize
    : parseRequiredInt(payload.pageSize, 'pageSize', { min: 1, max: 200 });
  return { ...payload, pageNo, pageSize };
}

async function handleBrowser(command, options) {
  switch (command) {
    case 'list': {
      const inputPayload = parseJsonInput(options.payload, '--payload');
      const payload = inputPayload
        ? validatePagePayload(inputPayload)
        : {
            ...parsePageOptions(options),
            envName: options.name ? String(options.name).trim() : '',
          };
      const data = await callApi('/api/env/page', { body: payload });
      printObject(data);
      return;
    }
    case 'start': {
      const payload = normalizeProfileIdentityPayload(parseJsonInput(options.payload, '--payload'), options, 'start');
      const data = await callApi('/api/env/start', { body: payload });
      console.log('✅ Profile started');
      printObject(data);
      showConnectTips(data);
      return;
    }
    case 'close': {
      const payload = normalizeProfileIdentityPayload(parseJsonInput(options.payload, '--payload'), options, 'close');
      const data = await callApi('/api/env/close', { body: payload });
      console.log('✅ Profile closed');
      printObject(data);
      return;
    }
    case 'status': {
      const payload = normalizeProfileIdentityPayload(parseJsonInput(options.payload, '--payload'), options, 'status');
      const data = await callApi('/api/env/status', { body: payload });
      printObject(data);
      showConnectTips(data);
      return;
    }
    case 'detail': {
      const body = normalizeProfileIdentityPayload(parseJsonInput(options.payload, '--payload'), options, 'detail');
      const data = await callApi('/api/env/detail', { body });
      printObject(data);
      return;
    }
    case 'create-quick': {
      const inputPayload = parseJsonInput(options.payload, '--payload');
      const payload = inputPayload || {
        browserTypeId: options['browser-type-id'] ?? 1,
        operatorSystemId: options['operator-system-id'] ?? 1,
        quantity: options.quantity ?? 1,
      };
      requirePlainObject(payload, 'create-quick payload');
      payload.browserTypeId = parseRequiredInt(payload.browserTypeId, 'browserTypeId', { min: 1 });
      payload.operatorSystemId = parseRequiredInt(payload.operatorSystemId, 'operatorSystemId', { min: 1 });
      payload.quantity = parseRequiredInt(payload.quantity, 'quantity', { min: 1, max: 100 });
      const data = await callApi('/api/env/create/quick', { body: payload });
      console.log('✅ Profile created successfully');
      printObject(data);
      return;
    }
    case 'refresh-fingerprint': {
      const payload = normalizeProfileIdentityPayload(parseJsonInput(options.payload, '--payload'), options, 'refresh-fingerprint');
      const data = await callApi('/api/env/fingerprint/refresh', { body: payload });
      console.log('✅ Fingerprint refresh completed');
      printObject(data);
      return;
    }
    case 'clear-cache': {
      const inputPayload = parseJsonInput(options.payload, '--payload');
      const payload = inputPayload ? validateLocalCachePayload(inputPayload) : buildLocalCachePayload(options);
      const data = await callApi('/api/env/removeLocalCache', { body: payload });
      console.log('✅ Cache cleared');
      printObject(data);
      return;
    }
    case 'clean-cloud-cache': {
      const inputPayload = parseJsonInput(options.payload, '--payload');
      const payload = inputPayload ? validateCloudCachePayload(inputPayload) : buildCloudCachePayload(options);
      const data = await callApi('/api/env/cache/cleanCloud', { body: payload });
      console.log('✅ Cloud cache cleared');
      printObject(data);
      return;
    }
    case 'delete': {
      const payload = parseJsonInput(options.payload, '--payload') || { envIds: splitCsv(options['env-ids']) };
      requirePlainObject(payload, 'delete payload');
      payload.envIds = normalizeStringArray(payload.envIds, 'envIds');
      if (!payload.envIds || payload.envIds.length === 0) {
        fail('delete requires --env-ids "<id1,id2>" or --payload');
      }
      const data = await callApi('/api/env/removeToRecycleBin/batch', { body: payload });
      console.log('✅ Delete request submitted');
      printObject(data);
      return;
    }
    default:
      fail(`Unknown browser command: ${command}`);
  }
}

async function handleProxy(command, options) {
  const payload = parseJsonInput(options.payload, '--payload');
  switch (command) {
    case 'list': {
      const body = payload
        ? validatePagePayload(payload)
        : parsePageOptions(options);
      const data = await callApi('/api/proxyInfo/page', { body });
      printObject(data);
      return;
    }
    case 'add': {
      if (!payload) fail('proxy add: use --payload to pass full parameters');
      validateProxyAddPayload(payload);
      const data = await callApi('/api/proxyInfo/add', { body: payload });
      printObject(data);
      return;
    }
    case 'update': {
      if (!payload) fail('proxy update: use --payload to pass full parameters');
      validateProxyUpdatePayload(payload);
      const data = await callApi('/api/proxyInfo/update', { body: payload });
      printObject(data);
      return;
    }
    case 'delete': {
      let body = payload;
      if (!body) {
        body = splitCsv(options.ids);
      } else if (!Array.isArray(body)) {
        if (Array.isArray(body.ids)) {
          body = body.ids;
        } else if (Array.isArray(body.proxyIds)) {
          body = body.proxyIds;
        }
      }
      if (!Array.isArray(body)) {
        fail('proxy delete requires --ids "<id1,id2>" or --payload');
      }
      body = normalizeStringArray(body, 'ids');
      const data = await callApi('/api/proxyInfo/delete', { body });
      printObject(data);
      return;
    }
    case 'help':
      console.log(`
Proxy subcommands:
  list --page 1 --page-size 20
  add --payload '{"proxyIp":"1.2.3.4",...}'
  update --payload '{"id":"...","proxyIp":"..."}'
  delete --ids "id1,id2" or --payload '["id1","id2"]'
`);
      return;
    default:
      fail(`Unknown proxy command: ${command}`);
  }
}

async function handleGroup(command, options) {
  const payload = parseJsonInput(options.payload, '--payload');
  switch (command) {
    case 'list': {
      const body = payload
        ? validatePagePayload(payload)
        : { ...parsePageOptions(options), groupName: options.name ? String(options.name).trim() : '' };
      const data = await callApi('/api/envgroup/page', { body });
      printObject(data);
      return;
    }
    case 'create': {
      const body = payload || (options.name ? { groupName: options.name } : null);
      if (!body) fail('group create requires --name or --payload');
      validateGroupCreatePayload(body);
      const data = await callApi('/api/envgroup/create', { body });
      printObject(data);
      return;
    }
    case 'edit': {
      const body = payload || { id: options.id, groupName: options.name };
      requirePlainObject(body, 'group edit payload');
      body.id = requireNonEmptyString(body.id, 'id');
      body.groupName = requireNonEmptyString(body.groupName, 'groupName');
      const data = await callApi('/api/envgroup/edit', { body });
      printObject(data);
      return;
    }
    case 'delete': {
      const body = payload || { ids: splitCsv(options.ids) };
      requirePlainObject(body, 'group delete payload');
      body.ids = normalizeStringArray(body.ids, 'ids');
      if (!Array.isArray(body.ids) || body.ids.length === 0) {
        fail('group delete requires --ids "<id1,id2>" or --payload');
      }
      const data = await callApi('/api/envgroup/delete', { body });
      printObject(data);
      return;
    }
    case 'help':
      console.log(`
Group subcommands:
  list --page 1 --page-size 20
  create --name "My Group" or --payload '{"groupName":"My Group"}'
  edit --id "<groupId>" --name "New Name" or --payload '{"id":"<groupId>","groupName":"New Name"}'
  delete --ids "id1,id2" or --payload '{"ids":["id1","id2"]}'
`);
      return;
    default:
      fail(`Unknown group command: ${command}`);
  }
}

async function handleTag(command, options) {
  const payload = parseJsonInput(options.payload, '--payload');
  switch (command) {
    case 'list': {
      const data = await callApi('/api/envtag/all', { method: 'GET' });
      printObject(data);
      return;
    }
    case 'create': {
      const body = payload || (options.name ? { tagName: options.name } : null);
      if (!body) fail('tag create requires --name or --payload');
      validateTagCreatePayload(body);
      const data = await callApi('/api/envtag/create', { body });
      printObject(data);
      return;
    }
    case 'edit': {
      const body = payload || { id: options.id, tagName: options.name };
      requirePlainObject(body, 'tag edit payload');
      body.id = requireNonEmptyString(body.id, 'id');
      body.tagName = requireNonEmptyString(body.tagName, 'tagName');
      const data = await callApi('/api/envtag/edit', { body });
      printObject(data);
      return;
    }
    case 'delete': {
      const body = payload || { ids: splitCsv(options.ids) };
      requirePlainObject(body, 'tag delete payload');
      body.ids = normalizeStringArray(body.ids, 'ids');
      if (!Array.isArray(body.ids) || body.ids.length === 0) {
        fail('tag delete requires --ids "<id1,id2>" or --payload');
      }
      const data = await callApi('/api/envtag/delete', { body });
      printObject(data);
      return;
    }
    case 'help':
      console.log(`
Tag subcommands:
  list
  create --name "tag-name" or --payload '{"tagName":"tag-name"}'
  edit --id "<tagId>" --name "new-tag-name" or --payload '{"id":"<tagId>","tagName":"new-tag-name"}'
  delete --ids "id1,id2" or --payload '{"ids":["id1","id2"]}'
`);
      return;
    default:
      fail(`Unknown tag command: ${command}`);
  }
}

async function main(argv = process.argv.slice(2)) {
  const [scope, command, ...rest] = argv;

  if (!scope || scope === 'help' || scope === '--help') {
    showHelp();
    return;
  }

  // Backward compatibility for legacy commands
  const legacyMap = {
    list: ['browser', 'list'],
    start: ['browser', 'start'],
    stop: ['browser', 'close'],
    info: ['browser', 'detail'],
    connect: ['browser', 'status'],
  };

  let effectiveScope = scope;
  let effectiveCommand = command;
  let optionsSource = rest;

  if (legacyMap[scope]) {
    [effectiveScope, effectiveCommand] = legacyMap[scope];
    optionsSource = [command, ...rest].filter((item) => item !== undefined);
  }
  const { options } = parseArgs(optionsSource);
  if (options['profile-id'] && !options['env-id']) {
    options['env-id'] = options['profile-id'];
  }
  if (options['instance-id'] && !options.id) {
    options.id = options['instance-id'];
  }

  try {
    if (effectiveScope === 'browser') {
      if (!effectiveCommand) fail('Missing browser subcommand');
      await handleBrowser(effectiveCommand, options);
      return;
    }
    if (effectiveScope === 'cloudphone') {
      if (!effectiveCommand) fail('Missing cloudphone subcommand');
      const { createCloudPhoneHandler } = require('./cloudphone-commands');
      const handleCloudPhone = createCloudPhoneHandler({ callApi, fail });
      await handleCloudPhone(effectiveCommand, options);
      return;
    }

    if (effectiveScope === 'proxy') {
      if (!effectiveCommand) fail('Missing proxy subcommand');
      await handleProxy(effectiveCommand, options);
      return;
    }
    if (effectiveScope === 'group') {
      if (!effectiveCommand) fail('Missing group subcommand');
      await handleGroup(effectiveCommand, options);
      return;
    }
    if (effectiveScope === 'tag') {
      if (!effectiveCommand) fail('Missing tag subcommand');
      await handleTag(effectiveCommand, options);
      return;
    }
    fail(`Unknown command scope: ${effectiveScope}`);
  } catch (error) {
    fail(error.message);
  }
}

if (require.main === module) {
  main();
}

module.exports = { main };
