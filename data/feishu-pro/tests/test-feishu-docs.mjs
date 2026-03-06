import {
  createDocument,
  getDocument,
  getDocumentRawContent,
  listDocumentBlocks,
  appendText,
  appendBlocks,
  getPublicPermission,
  updatePublicPermission,
  addMemberPermission,
  listFiles,
  uploadFile,
  createFolder,
  listWikiSpaces,
  getWikiSpace,
  listWikiNodes,
  getNodeInfo,
} from '../dist/index.js';
import { applyFeishuDefaults, createStats, logSuiteStart, logSuiteEnd, runCase } from './_utils.mjs';

applyFeishuDefaults();

const stats = createStats();
logSuiteStart('feishu/docs (文档/知识库/云空间)');

const getDocId = () => process.env.TEST_DOC_ID;
const getDocToken = () => process.env.TEST_DOC_TOKEN || process.env.TEST_DOC_ID;
const docFolderToken = process.env.TEST_DOC_FOLDER_TOKEN;
const driveFolderToken = process.env.TEST_DRIVE_FOLDER_TOKEN;
const driveParentNode = process.env.TEST_DRIVE_PARENT_NODE;
const uploadFilePath = process.env.TEST_UPLOAD_FILE_PATH;
const getWikiSpaceId = () => process.env.TEST_WIKI_SPACE_ID;
const getWikiNodeToken = () => process.env.TEST_WIKI_NODE_TOKEN;

function extractDocId(response) {
  return (
    response?.data?.document?.document_id ||
    response?.data?.document_id ||
    response?.document?.document_id ||
    response?.document_id ||
    response?.data?.document?.id
  );
}

function extractWikiSpaceId(response) {
  return (
    response?.data?.items?.[0]?.space_id ||
    response?.data?.space_list?.[0]?.space_id ||
    response?.data?.spaces?.[0]?.space_id
  );
}

function extractWikiNodeToken(response) {
  return (
    response?.data?.items?.[0]?.node_token ||
    response?.data?.node_list?.[0]?.node_token ||
    response?.data?.nodes?.[0]?.node_token
  );
}

await runCase(stats, {
  name: 'createDocument',
  sideEffect: true,
  fn: async () => {
    const res = await createDocument(process.env.TEST_DOC_TITLE || 'OpenClaw Test Doc', docFolderToken);
    const newId = extractDocId(res);
    if (newId) {
      if (!process.env.TEST_DOC_ID) process.env.TEST_DOC_ID = newId;
      if (!process.env.TEST_DOC_TOKEN) process.env.TEST_DOC_TOKEN = newId;
    }
    return res;
  },
});

await runCase(stats, {
  name: 'getDocument',
  requires: ['TEST_DOC_ID'],
  fn: () => getDocument(getDocId()),
});

await runCase(stats, {
  name: 'getDocumentRawContent',
  requires: ['TEST_DOC_ID'],
  fn: () => getDocumentRawContent(getDocId()),
});

await runCase(stats, {
  name: 'listDocumentBlocks',
  requires: ['TEST_DOC_ID'],
  fn: () => listDocumentBlocks(getDocId()),
});

await runCase(stats, {
  name: 'appendText',
  requires: ['TEST_DOC_ID'],
  sideEffect: true,
  fn: () => appendText(getDocId(), 'OpenClaw append test'),
});

await runCase(stats, {
  name: 'appendBlocks',
  requires: ['TEST_DOC_ID'],
  sideEffect: true,
  fn: () => appendBlocks(getDocId(), [
    {
      block_type: 2,
      text: { elements: [{ text_run: { content: 'OpenClaw block append' } }] }
    }
  ]),
});

await runCase(stats, {
  name: 'getPublicPermission',
  requires: ['TEST_DOC_TOKEN'],
  fn: () => getPublicPermission(getDocToken(), process.env.TEST_DOC_TYPE || 'docx'),
});

await runCase(stats, {
  name: 'updatePublicPermission',
  requires: ['TEST_DOC_TOKEN', 'TEST_PUBLIC_PERMISSION_JSON'],
  sideEffect: true,
  fn: () => updatePublicPermission(
    getDocToken(),
    process.env.TEST_DOC_TYPE || 'docx',
    JSON.parse(process.env.TEST_PUBLIC_PERMISSION_JSON)
  ),
});

await runCase(stats, {
  name: 'addMemberPermission',
  requires: ['TEST_DOC_TOKEN', 'TEST_DOC_MEMBER_ID', 'TEST_DOC_MEMBER_TYPE', 'TEST_DOC_MEMBER_ROLE'],
  sideEffect: true,
  fn: () => addMemberPermission(
    getDocToken(),
    process.env.TEST_DOC_TYPE || 'docx',
    process.env.TEST_DOC_MEMBER_ID,
    process.env.TEST_DOC_MEMBER_TYPE,
    process.env.TEST_DOC_MEMBER_ROLE
  ),
});

await runCase(stats, {
  name: 'listFiles',
  requires: ['TEST_DRIVE_FOLDER_TOKEN'],
  fn: () => listFiles(driveFolderToken),
});

await runCase(stats, {
  name: 'uploadFile',
  requires: ['TEST_UPLOAD_FILE_PATH', 'TEST_DRIVE_PARENT_NODE'],
  sideEffect: true,
  fn: () => uploadFile(uploadFilePath, driveParentNode),
});

await runCase(stats, {
  name: 'createFolder',
  requires: ['TEST_DRIVE_FOLDER_TOKEN'],
  sideEffect: true,
  fn: () => createFolder(process.env.TEST_DRIVE_NEW_FOLDER_NAME || 'OpenClaw Test Folder', driveFolderToken),
});

await runCase(stats, {
  name: 'listWikiSpaces',
  fn: async () => {
    const res = await listWikiSpaces();
    const spaceId = extractWikiSpaceId(res);
    if (spaceId && !process.env.TEST_WIKI_SPACE_ID) process.env.TEST_WIKI_SPACE_ID = spaceId;
    return res;
  },
});

await runCase(stats, {
  name: 'getWikiSpace',
  requires: ['TEST_WIKI_SPACE_ID'],
  fn: () => getWikiSpace(getWikiSpaceId()),
});

await runCase(stats, {
  name: 'listWikiNodes',
  requires: ['TEST_WIKI_SPACE_ID'],
  fn: async () => {
    const res = await listWikiNodes(getWikiSpaceId());
    const nodeToken = extractWikiNodeToken(res);
    if (nodeToken && !process.env.TEST_WIKI_NODE_TOKEN) process.env.TEST_WIKI_NODE_TOKEN = nodeToken;
    return res;
  },
});

await runCase(stats, {
  name: 'getNodeInfo',
  requires: ['TEST_WIKI_NODE_TOKEN'],
  fn: () => getNodeInfo(getWikiNodeToken()),
});

logSuiteEnd('feishu/docs', stats);
