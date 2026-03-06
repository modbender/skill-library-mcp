const {
  normalizeStringArray,
  parseJsonInput,
  parsePageOptions,
  parseRequiredInt,
  printObject,
  requireNonEmptyString,
  requirePlainObject,
  toBoolean,
} = require('./common');

function toCloudPhoneNumericId(idValue) {
  const n = Number(idValue);
  return Number.isNaN(n) ? idValue : n;
}

function validateCloudPhoneCreatePayload(body, fail) {
  try {
    requirePlainObject(body, 'cloudphone create payload');
    requireNonEmptyString(body.skuId, 'skuId');
    body.quantity = parseRequiredInt(body.quantity, 'quantity', { min: 1, max: 10 });
  } catch (error) {
    fail(error.message);
  }
}

function createCloudPhoneHandler({ callApi, fail }) {
  async function findCloudPhoneById(id) {
    const targetId = String(id);
    const first = await callApi('/api/cloudphone/page', {
      body: { keyword: targetId, pageNo: 1, pageSize: 20 },
    });
    const fromFirst = (first.dataList || []).find((item) => String(item.id) === targetId);
    if (fromFirst) return fromFirst;

    const fallback = await callApi('/api/cloudphone/page', { body: { pageNo: 1, pageSize: 100 } });
    const fromFallback = (fallback.dataList || []).find((item) => String(item.id) === targetId);
    if (!fromFallback) {
      throw new Error(`Cloud phone not found: ${targetId}`);
    }
    return fromFallback;
  }

  async function getCloudPhoneInfoById(id) {
    return callApi('/api/cloudphone/info', {
      body: { id: toCloudPhoneNumericId(id) },
    });
  }

  return async function handleCloudPhone(command, options) {
    const payload = parseJsonInput(options.payload, '--payload');

    switch (command) {
      case 'help':
        console.log(`
CloudPhone subcommands:
  list --page 1 --page-size 20
  create --payload '{"skuId":"10002", ...}'
  start --id <cloudPhoneId>
  stop --id <cloudPhoneId>
  info --id <cloudPhoneId>
  adb-info --id <cloudPhoneId>
  update-adb --id <cloudPhoneId> --enable true
  new-machine --id <cloudPhoneId>
  app-installed --id <cloudPhoneId>
  app-start --id <cloudPhoneId> --package-name com.example.app
  app-stop --id <cloudPhoneId> --package-name com.example.app
  app-restart --id <cloudPhoneId> --package-name com.example.app
  app-uninstall --id <cloudPhoneId> --package-name com.example.app
`);
        return;
      case 'list': {
        let body;
        if (payload) {
          requirePlainObject(payload, 'cloudphone list payload');
          body = {
            ...payload,
            pageNo: payload.pageNo === undefined ? 1 : parseRequiredInt(payload.pageNo, 'pageNo', { min: 1 }),
            pageSize: payload.pageSize === undefined ? 20 : parseRequiredInt(payload.pageSize, 'pageSize', { min: 1, max: 200 }),
          };
        } else {
          body = parsePageOptions(options);
        }
        const data = await callApi('/api/cloudphone/page', { body });
        printObject(data);
        return;
      }
      case 'create': {
        if (!payload) fail('create: use --payload to pass full parameters');
        validateCloudPhoneCreatePayload(payload, fail);
        const data = await callApi('/api/cloudphone/create', { body: payload });
        console.log('✅ Cloud phone created successfully');
        printObject(data);
        return;
      }
      case 'start': {
        const body = payload || { id: options.id };
        requirePlainObject(body, 'start payload');
        body.id = requireNonEmptyString(body.id, 'id');
        const data = await callApi('/api/cloudphone/powerOn', { body });
        console.log('✅ Cloud phone started');
        printObject(data);
        return;
      }
      case 'stop': {
        const body = payload || { id: options.id };
        requirePlainObject(body, 'stop payload');
        body.id = requireNonEmptyString(body.id, 'id');
        const data = await callApi('/api/cloudphone/powerOff', { body });
        console.log('✅ Cloud phone stopped');
        printObject(data);
        return;
      }
      case 'info': {
        const body = payload || { id: options.id };
        requirePlainObject(body, 'info payload');
        body.id = requireNonEmptyString(body.id, 'id');
        const data = await callApi('/api/cloudphone/info', { body });
        printObject(data);
        return;
      }
      case 'adb-info': {
        const cloudphoneId = payload?.id || options.id;
        requireNonEmptyString(cloudphoneId, 'id');
        const phone = await findCloudPhoneById(cloudphoneId);
        const info = await getCloudPhoneInfoById(cloudphoneId);
        printObject({
          id: String(phone.id),
          osVersion: info?.device?.osVersion || phone.osVersion || '',
          supportAdb: phone.supportAdb,
          enableAdb: phone.enableAdb,
          adbInfo: phone.adbInfo || null,
        });
        return;
      }
      case 'update-adb': {
        const body = payload || {
          ids: [toCloudPhoneNumericId(options.id)],
          enableAdb: toBoolean(options.enable, true),
        };
        requirePlainObject(body, 'update-adb payload');
        body.ids = normalizeStringArray(body.ids, 'ids').map(toCloudPhoneNumericId);
        body.enableAdb = toBoolean(body.enableAdb, true);
        const data = await callApi('/api/cloudphone/updateAdb', { body });
        printObject(data);
        return;
      }
      case 'new-machine': {
        const body = payload || { id: options.id };
        requirePlainObject(body, 'new-machine payload');
        body.id = requireNonEmptyString(body.id, 'id');
        const data = await callApi('/api/cloudphone/newMachine', { body });
        printObject(data);
        return;
      }
      case 'app-installed': {
        const body = payload || { id: options.id };
        requirePlainObject(body, 'app-installed payload');
        body.id = requireNonEmptyString(body.id, 'id');
        const data = await callApi('/api/cloudphone/app/installedList', { body });
        printObject(data);
        return;
      }
      case 'app-start':
      case 'app-stop':
      case 'app-restart':
      case 'app-uninstall': {
        const endpointMap = {
          'app-start': '/api/cloudphone/app/start',
          'app-stop': '/api/cloudphone/app/stop',
          'app-restart': '/api/cloudphone/app/restart',
          'app-uninstall': '/api/cloudphone/app/uninstall',
        };
        const body = payload || { id: options.id, packageName: options['package-name'] };
        requirePlainObject(body, `${command} payload`);
        body.id = requireNonEmptyString(body.id, 'id');
        body.packageName = requireNonEmptyString(body.packageName, 'packageName');
        if (!/^[A-Za-z0-9._-]+$/.test(body.packageName)) {
          fail('packageName contains unsupported characters');
        }
        const data = await callApi(endpointMap[command], { body });
        printObject(data);
        return;
      }
      default:
        fail(`Unknown cloudphone command: ${command}`);
    }
  };
}

module.exports = { createCloudPhoneHandler };
