import * as fs from 'fs';
import * as path from 'path';
import { createClient } from '@openclaw-feishu/feishu-client';

function getAuth() {
  const appId = process.env.FEISHU_APP_ID;
  const appSecret = process.env.FEISHU_APP_SECRET;
  if (!appId || !appSecret) throw new Error('Missing FEISHU_APP_ID or FEISHU_APP_SECRET');
  return { appId, appSecret };
}

/**
 * 创建新版文档 (Docx)
 * @param title - 文档标题
 * @param folderToken - 所在文件夹 token（可选）
 */
export async function createDocument(title: string, folderToken?: string) {
  const { appId, appSecret } = getAuth();
  const client = createClient({ appId, appSecret });

  return await client.call(() => client.getClient().docx.document.create({
    data: {
      title: title,
      folder_token: folderToken,
    }
  }));
}

/**
 * 获取文档基本信息
 */
export async function getDocument(documentId: string) {
  const { appId, appSecret } = getAuth();
  const client = createClient({ appId, appSecret });

  return await client.call(() => client.getClient().docx.document.get({
    path: { document_id: documentId }
  }));
}

/**
 * 获取文档纯文本内容
 */
export async function getDocumentRawContent(documentId: string) {
  const { appId, appSecret } = getAuth();
  const client = createClient({ appId, appSecret });

  return await client.call(() => client.getClient().docx.document.rawContent({
    path: { document_id: documentId }
  }));
}

/**
 * 列出文档所有块 (Blocks)
 */
export async function listDocumentBlocks(documentId: string, pageToken?: string, pageSize?: number) {
  const { appId, appSecret } = getAuth();
  const client = createClient({ appId, appSecret });

  return await client.call(() => client.getClient().docx.documentBlock.list({
    path: { document_id: documentId },
    params: {
      page_token: pageToken,
      page_size: pageSize || 500,
    }
  }));
}

/**
 * 向文档追加文本块
 * @param documentId - 文档 Token
 * @param text - 要追加的文本
 * @param targetBlockId - 目标块 ID（默认为文档本身，即 documentId）
 */
export async function appendText(documentId: string, text: string, targetBlockId?: string) {
  const { appId, appSecret } = getAuth();
  const client = createClient({ appId, appSecret });

  const blockId = targetBlockId || documentId;

  return await client.call(() => client.getClient().docx.documentBlockChildren.create({
    path: {
      document_id: documentId,
      block_id: blockId,
    },
    data: {
      children: [
        {
          block_type: 2, // Text block
          text: {
            elements: [
              {
                text_run: {
                  content: text,
                }
              }
            ]
          }
        }
      ]
    }
  }));
}

/**
 * 批量追加块
 */
export async function appendBlocks(documentId: string, blocks: any[], targetBlockId?: string) {
  const { appId, appSecret } = getAuth();
  const client = createClient({ appId, appSecret });

  const blockId = targetBlockId || documentId;

  return await client.call(() => client.getClient().docx.documentBlockChildren.create({
    path: {
      document_id: documentId,
      block_id: blockId,
    },
    data: {
      children: blocks,
    }
  }));
}

type DocType = "doc" | "sheet" | "file" | "wiki" | "bitable" | "docx" | "mindnote" | "minutes" | "slides";
type MemberType = "email" | "openid" | "unionid" | "openchat" | "opendepartmentid" | "userid" | "groupid" | "wikispaceid";

/**
 * 获取公开权限设置
 */
export async function getPublicPermission(token: string, type: DocType = 'docx') {
  const { appId, appSecret } = getAuth();
  const client = createClient({ appId, appSecret });

  return await client.call(() => client.getClient().drive.permissionPublic.get({
    path: { token: token },
    params: { type: type }
  }));
}

/**
 * 更新公开权限设置
 */
export async function updatePublicPermission(token: string, type: DocType, data: any) {
  const { appId, appSecret } = getAuth();
  const client = createClient({ appId, appSecret });

  return await client.call(() => client.getClient().drive.permissionPublic.patch({
    path: { token: token },
    params: { type: type },
    data: data,
  }));
}

/**
 * 添加协作者权限
 */
export async function addMemberPermission(token: string, type: DocType, memberId: string, memberType: MemberType, role: 'view' | 'edit' | 'full_access') {
  const { appId, appSecret } = getAuth();
  const client = createClient({ appId, appSecret });

  return await client.call(() => client.getClient().drive.permissionMember.create({
    path: { token: token },
    params: { type: type as any },
    data: {
      member_type: memberType,
      member_id: memberId,
      perm: role,
    }
  }));
}

/**
 * 列出云空间文件
 */
export async function listFiles(folderToken?: string, pageToken?: string, pageSize?: number) {
  const { appId, appSecret } = getAuth();
  const client = createClient({ appId, appSecret });

  return await client.call(() => client.getClient().drive.file.list({
    params: {
      folder_token: folderToken,
      page_token: pageToken,
      page_size: pageSize || 20,
    }
  }));
}

/**
 * 上传文件到云空间
 */
export async function uploadFile(filePath: string, parentNode: string, fileName?: string) {
  const { appId, appSecret } = getAuth();
  const client = createClient({ appId, appSecret });

  if (!fs.existsSync(filePath)) {
    return { ok: false, error: `文件不存在: ${filePath}` };
  }

  const finalFileName = fileName || path.basename(filePath);
  const size = fs.statSync(filePath).size;

  return await client.call(() => client.getClient().drive.file.uploadAll({
    data: {
      file_name: finalFileName,
      parent_type: 'explorer',
      parent_node: parentNode,
      size: size,
      file: fs.createReadStream(filePath),
    }
  }));
}

/**
 * 创建文件夹
 */
export async function createFolder(name: string, folderToken: string) {
  const { appId, appSecret } = getAuth();
  const client = createClient({ appId, appSecret });

  return await client.call(() => client.getClient().drive.file.createFolder({
    data: {
      name: name,
      folder_token: folderToken,
    }
  }));
}

/**
 * 列出知识库空间
 */
export async function listWikiSpaces(pageToken?: string, pageSize?: number) {
  const { appId, appSecret } = getAuth();
  const client = createClient({ appId, appSecret });

  return await client.call(() => client.getClient().wiki.space.list({
    params: {
      page_token: pageToken,
      page_size: pageSize || 20,
    }
  }));
}

/**
 * 获取知识库空间信息
 */
export async function getWikiSpace(spaceId: string) {
  const { appId, appSecret } = getAuth();
  const client = createClient({ appId, appSecret });

  return await client.call(() => client.getClient().wiki.space.get({
    path: { space_id: spaceId }
  }));
}

/**
 * 列出知识库节点
 */
export async function listWikiNodes(spaceId: string, parentNodeToken?: string, pageToken?: string, pageSize?: number) {
  const { appId, appSecret } = getAuth();
  const client = createClient({ appId, appSecret });

  return await client.call(() => client.getClient().wiki.spaceNode.list({
    path: { space_id: spaceId },
    params: {
      parent_node_token: parentNodeToken,
      page_token: pageToken,
      page_size: pageSize || 20,
    }
  }));
}

/**
 * 获取节点信息
 */
export async function getNodeInfo(token: string) {
  const { appId, appSecret } = getAuth();
  const client = createClient({ appId, appSecret });

  return await client.call(() => client.getClient().wiki.space.getNode({
    params: {
      token: token,
    }
  }));
}
