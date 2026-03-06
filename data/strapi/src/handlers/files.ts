import { readFileSync, existsSync } from 'node:fs';
import { basename } from 'node:path';
import type { StrapiClient } from '../client.js';
import { fetchJson } from '../client.js';

const MIME_MAP: Record<string, string> = {
  jpg: 'image/jpeg', jpeg: 'image/jpeg', png: 'image/png',
  gif: 'image/gif', webp: 'image/webp', svg: 'image/svg+xml',
  pdf: 'application/pdf', doc: 'application/msword',
  docx: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
  xls: 'application/vnd.ms-excel',
  xlsx: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
  mp4: 'video/mp4', webm: 'video/webm', mp3: 'audio/mpeg',
  json: 'application/json', txt: 'text/plain', csv: 'text/csv',
  zip: 'application/zip',
};

function getMimeType(name: string): string {
  const ext = name.split('.').pop()?.toLowerCase() ?? '';
  return MIME_MAP[ext] ?? 'application/octet-stream';
}

function isUrl(source: string): boolean {
  return /^https?:\/\//i.test(source);
}

function extractFileName(source: string): string {
  if (isUrl(source)) {
    const urlPath = new URL(source).pathname;
    const name = basename(urlPath);
    return name || 'download';
  }
  return basename(source);
}

async function fetchFileFromUrl(url: string): Promise<{ buffer: ArrayBuffer; mimeType: string; fileName: string }> {
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`Failed to download file from ${url}: HTTP ${response.status} ${response.statusText}`);
  }
  const contentType = response.headers.get('content-type');
  const fileName = extractFileName(url);
  const mimeType = contentType?.split(';')[0]?.trim() || getMimeType(fileName);
  const buffer = await response.arrayBuffer();
  return { buffer, mimeType, fileName };
}

export async function handleFiles(
  client: StrapiClient,
  action: string,
  args: string[]
): Promise<unknown> {
  const files = client.files;

  switch (action) {
    case 'find': {
      const params = args[0] ? JSON.parse(args[0]) : undefined;
      return files.find(params);
    }

    case 'findOne': {
      const fileId = args[0];
      if (!fileId) {
        throw new Error('File ID is required for findOne');
      }
      return files.findOne(Number(fileId));
    }

    case 'upload': {
      const source = args[0];
      if (!source) {
        throw new Error(
          'Usage: files upload <source> [fileInfo] [linkInfo]\n' +
          'source: local file path OR URL (http:// or https://)\n' +
          'fileInfo (optional): JSON with name, alternativeText, caption\n' +
          '  e.g. \'{"name":"hero","alternativeText":"Hero image","caption":"Main banner"}\'\n' +
          'linkInfo (optional): JSON to link file to an entry\n' +
          '  e.g. \'{"ref":"api::article.article","refId":"abc123","field":"cover"}\''
        );
      }

      let fileData: ArrayBuffer;
      let fileName: string;
      let mimeType: string;

      if (isUrl(source)) {
        const downloaded = await fetchFileFromUrl(source);
        fileData = downloaded.buffer;
        fileName = downloaded.fileName;
        mimeType = downloaded.mimeType;
      } else {
        if (!existsSync(source)) {
          throw new Error(`File not found: ${source}`);
        }
        const buffer = readFileSync(source);
        fileData = buffer.buffer.slice(buffer.byteOffset, buffer.byteOffset + buffer.byteLength);
        fileName = basename(source);
        mimeType = getMimeType(source);
      }

      const blob = new Blob([fileData], { type: mimeType });
      const formData = new FormData();
      formData.append('files', blob, fileName);

      if (args[1]) {
        const fileInfo = JSON.parse(args[1]) as Record<string, string>;
        formData.append('fileInfo', JSON.stringify(fileInfo));
      }

      if (args[2]) {
        const linkInfo = JSON.parse(args[2]) as Record<string, string>;
        if (linkInfo.ref) formData.append('ref', linkInfo.ref);
        if (linkInfo.refId) formData.append('refId', linkInfo.refId);
        if (linkInfo.field) formData.append('field', linkInfo.field);
      }

      return fetchJson(client, '/upload', {
        method: 'POST',
        body: formData as unknown as RequestInit['body'],
      });
    }

    case 'update': {
      const fileId = args[0];
      const fileInfo = args[1];
      if (!fileId || !fileInfo) {
        throw new Error('File ID and fileInfo JSON are required for update');
      }
      return files.update(Number(fileId), JSON.parse(fileInfo));
    }

    case 'delete': {
      const fileId = args[0];
      if (!fileId) {
        throw new Error('File ID is required for delete');
      }
      return files.delete(Number(fileId));
    }

    default:
      throw new Error(
        `Unknown files action: "${action}". Use: find, findOne, upload, update, delete`
      );
  }
}
