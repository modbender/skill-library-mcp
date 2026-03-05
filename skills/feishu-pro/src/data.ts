import { createClient } from '@openclaw-feishu/feishu-client';

function getAuth() {
  const appId = process.env.FEISHU_APP_ID;
  const appSecret = process.env.FEISHU_APP_SECRET;
  if (!appId || !appSecret) throw new Error('Missing FEISHU_APP_ID or FEISHU_APP_SECRET');
  return { appId, appSecret };
}

/**
 * 创建电子表格
 */
export async function createSpreadsheet(title: string, folderToken?: string) {
  const { appId, appSecret } = getAuth();
  const client = createClient({ appId, appSecret });

  return await client.call(() => client.getClient().sheets.spreadsheet.create({
    data: {
      title: title,
      folder_token: folderToken,
    }
  }));
}

/**
 * 获取表格信息（元数据，包括子表列表）
 */
export async function getSpreadsheet(spreadsheetToken: string) {
  const { appId, appSecret } = getAuth();
  const client = createClient({ appId, appSecret });

  return await client.call(() => client.getClient().sheets.spreadsheet.get({
    path: { spreadsheet_token: spreadsheetToken }
  }));
}

/**
 * 读取单元格数据
 * @param spreadsheetToken - 表格 Token
 * @param sheetId - 子表 ID
 * @param range - 范围（如 A1:D10）
 */
export async function getSheetValues(spreadsheetToken: string, sheetId: string, range: string) {
  const { appId, appSecret } = getAuth();
  const client = createClient({ appId, appSecret });

  // 既然 SDK 没有直接的方法，我们使用 client.httpInstance 发起请求
  return await client.call(async () => {
    const response = await client.getClient().request({
      method: 'GET',
      url: `/open-apis/sheets/v3/spreadsheets/${spreadsheetToken}/sheets/${sheetId}/values/${range}`,
    });
    return response;
  });
}

/**
 * 更新单元格数据
 */
export async function updateSheetValues(spreadsheetToken: string, sheetId: string, range: string, values: any[][]) {
  const { appId, appSecret } = getAuth();
  const client = createClient({ appId, appSecret });

  return await client.call(async () => {
    return await client.getClient().request({
      method: 'PUT',
      url: `/open-apis/sheets/v3/spreadsheets/${spreadsheetToken}/sheets/${sheetId}/values/${range}`,
      data: {
        value_range: {
          values: values
        }
      }
    });
  });
}

/**
 * 追加单元格数据
 */
export async function appendSheetValues(spreadsheetToken: string, sheetId: string, range: string, values: any[][]) {
  const { appId, appSecret } = getAuth();
  const client = createClient({ appId, appSecret });

  return await client.call(async () => {
    return await client.getClient().request({
      method: 'POST',
      url: `/open-apis/sheets/v3/spreadsheets/${spreadsheetToken}/sheets/${sheetId}/values/append`,
      data: {
        value_range: {
          range: range,
          values: values
        }
      }
    });
  });
}

/**
 * 前插单元格数据
 */
export async function prependSheetValues(spreadsheetToken: string, sheetId: string, range: string, values: any[][]) {
  const { appId, appSecret } = getAuth();
  const client = createClient({ appId, appSecret });

  return await client.call(async () => {
    return await client.getClient().request({
      method: 'POST',
      url: `/open-apis/sheets/v3/spreadsheets/${spreadsheetToken}/sheets/${sheetId}/values/prepend`,
      data: {
        value_range: {
          range: range,
          values: values
        }
      }
    });
  });
}

/**
 * 列出记录
 */
export async function listRecords(appToken: string, tableId: string, filter?: string, sort?: string, pageToken?: string, pageSize?: number) {
  const { appId, appSecret } = getAuth();
  const client = createClient({ appId, appSecret });

  return await client.call(() => client.getClient().bitable.appTableRecord.list({
    path: {
      app_token: appToken,
      table_id: tableId,
    },
    params: {
      filter: filter,
      sort: sort,
      page_token: pageToken,
      page_size: pageSize || 20,
    }
  }));
}

/**
 * 获取单个记录
 */
export async function getRecord(appToken: string, tableId: string, recordId: string) {
  const { appId, appSecret } = getAuth();
  const client = createClient({ appId, appSecret });

  return await client.call(() => client.getClient().bitable.appTableRecord.get({
    path: {
      app_token: appToken,
      table_id: tableId,
      record_id: recordId,
    }
  }));
}

/**
 * 创建单条记录
 */
export async function createRecord(appToken: string, tableId: string, fields: Record<string, any>) {
  const { appId, appSecret } = getAuth();
  const client = createClient({ appId, appSecret });

  return await client.call(() => client.getClient().bitable.appTableRecord.create({
    path: {
      app_token: appToken,
      table_id: tableId,
    },
    data: {
      fields: fields
    }
  }));
}

/**
 * 批量创建记录
 */
export async function batchCreateRecords(appToken: string, tableId: string, records: Array<{ fields: Record<string, any> }>) {
  const { appId, appSecret } = getAuth();
  const client = createClient({ appId, appSecret });

  return await client.call(() => client.getClient().bitable.appTableRecord.batchCreate({
    path: {
      app_token: appToken,
      table_id: tableId,
    },
    data: {
      records: records
    }
  }));
}

/**
 * 更新单条记录
 */
export async function updateRecord(appToken: string, tableId: string, recordId: string, fields: Record<string, any>) {
  const { appId, appSecret } = getAuth();
  const client = createClient({ appId, appSecret });

  return await client.call(() => client.getClient().bitable.appTableRecord.update({
    path: {
      app_token: appToken,
      table_id: tableId,
      record_id: recordId,
    },
    data: {
      fields: fields
    }
  }));
}

/**
 * 批量更新记录
 */
export async function batchUpdateRecords(appToken: string, tableId: string, records: Array<{ record_id: string; fields: Record<string, any> }>) {
  const { appId, appSecret } = getAuth();
  const client = createClient({ appId, appSecret });

  return await client.call(() => client.getClient().bitable.appTableRecord.batchUpdate({
    path: {
      app_token: appToken,
      table_id: tableId,
    },
    data: {
      records: records
    }
  }));
}

/**
 * 删除单条记录
 */
export async function deleteRecord(appToken: string, tableId: string, recordId: string) {
  const { appId, appSecret } = getAuth();
  const client = createClient({ appId, appSecret });

  return await client.call(() => client.getClient().bitable.appTableRecord.delete({
    path: {
      app_token: appToken,
      table_id: tableId,
      record_id: recordId,
    }
  }));
}

/**
 * 批量删除记录
 */
export async function batchDeleteRecords(appToken: string, tableId: string, recordIds: string[]) {
  const { appId, appSecret } = getAuth();
  const client = createClient({ appId, appSecret });

  return await client.call(() => client.getClient().bitable.appTableRecord.batchDelete({
    path: {
      app_token: appToken,
      table_id: tableId,
    },
    data: {
      records: recordIds
    }
  }));
}

/**
 * 复制多维表格
 */
export async function copyBitable(appToken: string, name: string, folderToken?: string) {
  const { appId, appSecret } = getAuth();
  const client = createClient({ appId, appSecret });

  return await client.call(() => client.getClient().bitable.app.copy({
    path: { app_token: appToken },
    data: {
      name: name,
      folder_token: folderToken,
    }
  }));
}
