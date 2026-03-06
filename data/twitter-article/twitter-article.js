#!/usr/bin/env node
/**
 * Twitter/X Article CLI
 * 
 * 通过 cookies 认证调用 Twitter GraphQL API 创建/管理 Articles (Premium+ 长文功能)
 * 
 * Usage:
 *   node twitter-article.js list                              # 列出草稿
 *   node twitter-article.js create-draft --title "xxx"        # 创建草稿（含空内容）
 *   node twitter-article.js create --title "xxx" --file a.md  # 创建 + 写入内容
 *   node twitter-article.js update-title --id <id> --title    # 更新标题
 *   node twitter-article.js update-content --id <id> --file   # 更新内容（.md 或 .json）
 *   node twitter-article.js upload-media --file image.png     # 上传图片拿 media_id
 *   node twitter-article.js update-cover --id <id> --media-id # 设封面
 *   node twitter-article.js publish --id <id>                 # 发布
 *   node twitter-article.js delete --id <id>                  # 删除
 *   node twitter-article.js get --id <id>                     # 查看
 * 
 * Env: AUTH_TOKEN, CT0, HTTPS_PROXY (default http://127.0.0.1:7897)
 */

const fs = require('fs');
const crypto = require('crypto');
const http = require('http');
const https = require('https');
const tls = require('tls');
const { URL } = require('url');

const BEARER = 'AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA';
const PROXY = process.env.HTTPS_PROXY || process.env.HTTP_PROXY || 'http://127.0.0.1:7897';

const ENDPOINTS = {
  ArticleEntityDraftCreate:      { queryId: 't5-e2kJcCqqJ_MsZ0c07Rg', method: 'POST' },
  ArticleEntityUpdateContent:    { queryId: 'IzVdegTuct9uoXRK5L93Qg', method: 'POST' },
  ArticleEntityUpdateTitle:      { queryId: '5wp_YbfxSfYJTiLWb4tYnA', method: 'POST' },
  ArticleEntityUpdateCoverMedia: { queryId: 'ImdpGnpk1xo9yYJBIwHsvw', method: 'POST' },
  ArticleEntityPublish:          { queryId: 'D7SXoTdAoDmYacGzp9KQQw', method: 'POST' },
  ArticleEntityUnpublish:        { queryId: 'hQGA3NRU9IkosCbkAJQLjA', method: 'POST' },
  ArticleEntityDelete:           { queryId: 'e4lWqB6m2TA8Fn_j9L9xEA', method: 'POST' },
  ArticleEntityResultByRestId:   { queryId: 'id8pHQbQi7eZ6P9mA1th1Q', method: 'GET' },
  ArticleEntitiesSlice:          { queryId: 'cMMcpaRIk_-FJKdQ08HiDQ', method: 'GET' },
};

const FEATURES = {
  profile_label_improvements_pcf_label_in_post_enabled: true,
  responsive_web_profile_redirect_enabled: false,
  rweb_tipjar_consumption_enabled: false,
  verified_phone_label_enabled: false,
  responsive_web_graphql_skip_user_profile_image_extensions_enabled: false,
  responsive_web_graphql_timeline_navigation_enabled: true,
};

function getAuth() {
  const authToken = process.env.AUTH_TOKEN;
  const ct0 = process.env.CT0;
  if (!authToken || !ct0) { console.error('Error: AUTH_TOKEN and CT0 env vars required'); process.exit(1); }
  return { authToken, ct0 };
}

function proxyRequest(url, opts = {}) {
  return new Promise((resolve, reject) => {
    const { authToken, ct0 } = getAuth();
    const parsed = new URL(url);
    const proxy = new URL(PROXY);
    
    const proxyReq = http.request({
      host: proxy.hostname, port: proxy.port,
      method: 'CONNECT', path: `${parsed.hostname}:443`,
    });
    
    proxyReq.on('connect', (res, socket) => {
      if (res.statusCode !== 200) { reject(new Error(`Proxy CONNECT failed: ${res.statusCode}`)); return; }
      const tlsSocket = tls.connect({ socket, servername: parsed.hostname });
      const req = https.request({
        socket: tlsSocket, hostname: parsed.hostname,
        path: parsed.pathname + parsed.search,
        method: opts.method || 'POST',
        headers: {
          'authorization': `Bearer ${BEARER}`,
          'x-csrf-token': ct0,
          'cookie': `auth_token=${authToken}; ct0=${ct0}`,
          'content-type': opts.contentType || 'application/json',
          'x-twitter-active-user': 'yes',
          'x-twitter-auth-type': 'OAuth2Session',
          'x-twitter-client-language': 'en',
          'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
          'referer': 'https://x.com/',
          'origin': 'https://x.com',
          ...opts.headers,
        },
      }, (response) => {
        const chunks = [];
        response.on('data', c => chunks.push(c));
        response.on('end', () => {
          const buf = Buffer.concat(chunks);
          const str = buf.toString('utf-8');
          try { resolve({ status: response.statusCode, data: JSON.parse(str), raw: str }); }
          catch { resolve({ status: response.statusCode, data: null, raw: str, buffer: buf }); }
        });
      });
      req.on('error', reject);
      if (opts.body) {
        if (Buffer.isBuffer(opts.body)) req.write(opts.body);
        else req.write(opts.body);
      }
      req.end();
    });
    proxyReq.on('error', reject);
    proxyReq.end();
  });
}

async function graphql(name, variables = {}) {
  const ep = ENDPOINTS[name];
  if (!ep) throw new Error(`Unknown endpoint: ${name}`);
  const url = `https://x.com/i/api/graphql/${ep.queryId}/${name}`;
  
  if (ep.method === 'GET') {
    const params = new URLSearchParams({
      variables: JSON.stringify(variables),
      features: JSON.stringify(FEATURES),
    });
    return proxyRequest(`${url}?${params}`, { method: 'GET' });
  }
  
  return proxyRequest(url, {
    body: JSON.stringify({ variables, features: FEATURES, queryId: ep.queryId }),
  });
}

// --- Content Format ---
// Twitter Article uses a modified Draft.js format:
// Block: { key, text, type, data: {}, entity_ranges: [], inline_style_ranges: [] }
// EntityMap: array of { key: "N", value: { type, mutability, data } }
//
// Supported block types: unstyled, header-one, header-two, blockquote,
//   unordered-list-item, ordered-list-item, atomic
// NOT supported: header-three, header-four, code-block (server error)
//
// Image entity format (type "MEDIA"):
//   data: { entity_key: "<uuid>", media_items: [{ local_media_id: N, media_category: "DraftTweetImage", media_id: "<id>" }] }
// Atomic block must reference entity via entity_ranges: [{ key: N, offset: 0, length: 1 }]

function genKey() { return crypto.randomBytes(3).toString('hex').slice(0, 5); }
function genUUID() { return crypto.randomUUID(); }

function makeBlock(text, type, entityRanges = []) {
  return { data: {}, text, key: genKey(), type, entity_ranges: entityRanges, inline_style_ranges: [] };
}

function markdownToTwitterContent(markdown, imageMediaIds = []) {
  const lines = markdown.split('\n');
  const blocks = [];
  const entity_map = [];
  let mediaIdx = 0;
  let entityIdx = 0;
  let skippedFirstH1 = false;  // Skip first h1 — it becomes the article title

  for (const line of lines) {
    if (line.trim() === '') continue;

    const h1 = line.match(/^# (.+)/);
    const h2 = line.match(/^## (.+)/);
    const h3 = line.match(/^###+ (.+)/);
    const img = line.match(/^!\[.*?\]\((.+?)\)/);
    const quote = line.match(/^> (.+)/);
    const ul = line.match(/^[-*] (.+)/);
    const ol = line.match(/^\d+\. (.+)/);

    if (h1 && !skippedFirstH1) {
      skippedFirstH1 = true;  // First h1 is the title, skip it in body
      continue;
    } else if (h1) {
      blocks.push(makeBlock(h1[1], 'header-one'));
    } else if (h2) {
      blocks.push(makeBlock(h2[1], 'header-two'));
    } else if (h3) {
      // header-three not supported, promote to header-two
      blocks.push(makeBlock(h3[1], 'header-two'));
    } else if (img && mediaIdx < imageMediaIds.length) {
      const mid = imageMediaIds[mediaIdx++];
      const eidx = entityIdx++;
      entity_map.push({
        key: String(eidx),
        value: {
          type: 'MEDIA',
          mutability: 'Immutable',
          data: {
            entity_key: genUUID(),
            media_items: [{ local_media_id: mediaIdx, media_category: 'DraftTweetImage', media_id: mid }],
          },
        },
      });
      blocks.push(makeBlock(' ', 'atomic', [{ key: eidx, offset: 0, length: 1 }]));
    } else if (quote) {
      blocks.push(makeBlock(quote[1], 'blockquote'));
    } else if (ul) {
      blocks.push(makeBlock(ul[1], 'unordered-list-item'));
    } else if (ol) {
      blocks.push(makeBlock(ol[1], 'ordered-list-item'));
    } else {
      let text = line.replace(/\*\*(.+?)\*\*/g, '$1').replace(/\*(.+?)\*/g, '$1');
      blocks.push(makeBlock(text, 'unstyled'));
    }
  }

  if (blocks.length === 0) {
    blocks.push(makeBlock('', 'unstyled'));
  }

  return { blocks, entity_map };
}

// --- Upload Media ---
async function uploadMedia(filePath) {
  const fileData = fs.readFileSync(filePath);
  const ext = filePath.split('.').pop().toLowerCase();
  const mimeType = { png: 'image/png', gif: 'image/gif', webp: 'image/webp', jpg: 'image/jpeg', jpeg: 'image/jpeg' }[ext] || 'image/jpeg';

  // INIT
  const initRes = await proxyRequest('https://upload.twitter.com/i/media/upload.json', {
    contentType: 'application/x-www-form-urlencoded',
    body: `command=INIT&total_bytes=${fileData.length}&media_type=${encodeURIComponent(mimeType)}&media_category=tweet_image`,
  });
  if (!initRes.data?.media_id_string) { console.error('Upload INIT failed:', initRes.raw); process.exit(1); }
  const mediaId = initRes.data.media_id_string;

  // APPEND
  const chunkSize = 5 * 1024 * 1024;
  for (let i = 0; i * chunkSize < fileData.length; i++) {
    const chunk = fileData.slice(i * chunkSize, (i + 1) * chunkSize);
    await proxyRequest('https://upload.twitter.com/i/media/upload.json', {
      contentType: 'application/x-www-form-urlencoded',
      body: `command=APPEND&media_id=${mediaId}&segment_index=${i}&media_data=${encodeURIComponent(chunk.toString('base64'))}`,
    });
  }

  // FINALIZE
  const finalRes = await proxyRequest('https://upload.twitter.com/i/media/upload.json', {
    contentType: 'application/x-www-form-urlencoded',
    body: `command=FINALIZE&media_id=${mediaId}`,
  });
  // Always use string media_id to avoid JS number precision loss
  return { ...finalRes.data, media_id: mediaId, media_id_string: mediaId };
}

// --- Download image from URL ---
async function downloadImage(url, destPath) {
  return new Promise((resolve, reject) => {
    const parsed = new URL(url);
    const proxy = new URL(PROXY);
    const proxyReq = http.request({ host: proxy.hostname, port: proxy.port, method: 'CONNECT', path: `${parsed.hostname}:443` });
    proxyReq.on('connect', (res, socket) => {
      const tlsSocket = tls.connect({ socket, servername: parsed.hostname });
      const req = https.request({ socket: tlsSocket, hostname: parsed.hostname, path: parsed.pathname + parsed.search, method: 'GET' }, (response) => {
        if (response.statusCode >= 300 && response.statusCode < 400 && response.headers.location) {
          // Follow redirect
          downloadImage(response.headers.location, destPath).then(resolve).catch(reject);
          return;
        }
        const chunks = [];
        response.on('data', c => chunks.push(c));
        response.on('end', () => { fs.writeFileSync(destPath, Buffer.concat(chunks)); resolve(destPath); });
      });
      req.on('error', reject);
      req.end();
    });
    proxyReq.on('error', reject);
    proxyReq.end();
  });
}

// --- Commands ---

async function cmdCreateDraft(title, contentFile) {
  let content_state;
  let plaintext = '';
  
  if (contentFile) {
    if (contentFile.endsWith('.md')) {
      const md = fs.readFileSync(contentFile, 'utf-8');
      content_state = markdownToTwitterContent(md);
      plaintext = md.replace(/[#*>\-\[\]!()]/g, '').trim();
    } else {
      content_state = JSON.parse(fs.readFileSync(contentFile, 'utf-8'));
      plaintext = content_state.blocks.map(b => b.text).join('\n');
    }
  } else {
    content_state = { blocks: [{ key: genKey(), text: '', type: 'unstyled' }], entity_map: [] };
  }

  const res = await graphql('ArticleEntityDraftCreate', {
    content_state,
    title: title || 'Untitled',
    plaintext,
    word_count: plaintext.split(/\s+/).filter(Boolean).length,
  });

  const result = res.data?.data?.articleentity_create_draft?.article_entity_results?.result;
  if (result) {
    console.log(`✅ Draft created!`);
    console.log(`   Article ID: ${result.rest_id}`);
    console.log(`   Title: ${result.title}`);
    console.log(`   Preview: ${result.preview_text?.substring(0, 80)}...`);
    return result;
  } else {
    console.error('❌ Failed:', JSON.stringify(res.data, null, 2));
    process.exit(1);
  }
}

async function cmdUpdateTitle(articleId, title) {
  const res = await graphql('ArticleEntityUpdateTitle', { articleEntityId: articleId, title });
  if (res.data?.errors) { console.error('❌', JSON.stringify(res.data.errors)); } 
  else { console.log(`✅ Title updated: ${title}`); }
}

async function cmdUpdateContent(articleId, contentFile) {
  let content_state;
  if (contentFile.endsWith('.md')) {
    content_state = markdownToTwitterContent(fs.readFileSync(contentFile, 'utf-8'));
  } else {
    content_state = JSON.parse(fs.readFileSync(contentFile, 'utf-8'));
  }
  const plaintext = content_state.blocks.map(b => b.text).join('\n');

  const res = await graphql('ArticleEntityUpdateContent', {
    article_entity: articleId,
    content_state,
    plaintext,
    word_count: plaintext.split(/\s+/).filter(Boolean).length,
  });
  if (res.data?.errors) { console.error('❌', JSON.stringify(res.data.errors)); }
  else { console.log('✅ Content updated!'); }
}

async function cmdUpdateCover(articleId, mediaId) {
  const res = await graphql('ArticleEntityUpdateCoverMedia', {
    articleEntityId: articleId,
    coverMedia: { media_id: mediaId, media_category: 'DraftTweetImage' },
  });
  if (res.data?.errors) { console.error('❌', JSON.stringify(res.data.errors)); }
  else { console.log('✅ Cover updated!'); }
}

async function cmdPublish(articleId) {
  const res = await graphql('ArticleEntityPublish', { articleEntityId: articleId });
  if (res.data?.errors) { console.error('❌', JSON.stringify(res.data.errors)); }
  else { console.log('✅ Published!'); console.log(JSON.stringify(res.data, null, 2)); }
}

async function cmdDelete(articleId) {
  const res = await graphql('ArticleEntityDelete', { articleEntityId: articleId });
  if (res.data?.errors) { console.error('❌', JSON.stringify(res.data.errors)); }
  else { console.log('✅ Deleted!'); }
}

async function cmdGet(articleId) {
  const res = await graphql('ArticleEntityResultByRestId', { articleEntityId: articleId });
  console.log(JSON.stringify(res.data, null, 2));
}

async function cmdList() {
  const res = await graphql('ArticleEntitiesSlice', { count: 20 });
  console.log(JSON.stringify(res.data, null, 2));
}

async function cmdUploadMedia(filePath) {
  const result = await uploadMedia(filePath);
  console.log(`✅ Media uploaded! ID: ${result.media_id}`);
  return result;
}

// --- Notion → Twitter Article (end-to-end) ---

async function fetchNotionBlocks(notionKey, blockId) {
  const blocks = [];
  let cursor;
  do {
    const url = `https://api.notion.com/v1/blocks/${blockId}/children?page_size=100${cursor ? '&start_cursor=' + cursor : ''}`;
    const res = await fetch(url, {
      headers: { 'Authorization': `Bearer ${notionKey}`, 'Notion-Version': '2022-06-28' },
    });
    const data = await res.json();
    blocks.push(...(data.results || []));
    cursor = data.has_more ? data.next_cursor : null;
  } while (cursor);
  return blocks;
}

function notionBlocksToMarkdown(blocks) {
  const lines = [];
  const images = [];
  for (const b of blocks) {
    const richToText = (rt) => (rt || []).map(r => r.plain_text).join('');
    switch (b.type) {
      case 'heading_1': lines.push(`# ${richToText(b.heading_1.rich_text)}`); break;
      case 'heading_2': lines.push(`## ${richToText(b.heading_2.rich_text)}`); break;
      case 'heading_3': lines.push(`### ${richToText(b.heading_3.rich_text)}`); break;
      case 'paragraph': lines.push(richToText(b.paragraph.rich_text)); break;
      case 'bulleted_list_item': lines.push(`- ${richToText(b.bulleted_list_item.rich_text)}`); break;
      case 'numbered_list_item': lines.push(`1. ${richToText(b.numbered_list_item.rich_text)}`); break;
      case 'quote': lines.push(`> ${richToText(b.quote.rich_text)}`); break;
      case 'code': lines.push(`> ${richToText(b.code.rich_text)}`); break;
      case 'divider': lines.push('---'); break;
      case 'image': {
        const url = b.image.file?.url || b.image.external?.url || '';
        if (url) {
          images.push(url);
          const caption = richToText(b.image.caption) || `image${images.length}`;
          lines.push(`![${caption}](${url})`);
        }
        break;
      }
      case 'callout': lines.push(`> ${richToText(b.callout.rich_text)}`); break;
      case 'toggle': lines.push(richToText(b.toggle.rich_text)); break;
      default: break;
    }
  }
  return { markdown: lines.join('\n\n'), images };
}

async function cmdNotionToArticle(notionKey, pageId, opts = {}) {
  if (!notionKey || !pageId) {
    console.error('Usage: notion-to-article --notion-key <key> --page-id <id> [--publish]');
    process.exit(1);
  }

  // 1. Fetch page title
  console.log('📖 Fetching Notion page...');
  const pageRes = await fetch(`https://api.notion.com/v1/pages/${pageId}`, {
    headers: { 'Authorization': `Bearer ${notionKey}`, 'Notion-Version': '2022-06-28' },
  });
  const pageData = await pageRes.json();
  const titleProp = Object.values(pageData.properties || {}).find(p => p.type === 'title');
  const title = titleProp?.title?.[0]?.plain_text || 'Untitled';
  console.log(`   Title: ${title}`);

  // 2. Fetch blocks
  const blocks = await fetchNotionBlocks(notionKey, pageId);
  console.log(`   Blocks: ${blocks.length}`);

  // 3. Convert to markdown + extract images
  const { markdown, images } = notionBlocksToMarkdown(blocks);
  console.log(`   Images: ${images.length}`);

  // 4. Download & upload images
  const mediaIds = [];
  const tmpDir = '/tmp/twitter-article-imgs';
  fs.mkdirSync(tmpDir, { recursive: true });

  for (let i = 0; i < images.length; i++) {
    const imgUrl = images[i];
    const ext = imgUrl.match(/\.(png|jpg|jpeg|gif|webp)/i)?.[1] || 'jpg';
    const localPath = `${tmpDir}/img${i}.${ext}`;
    console.log(`   📤 [${i + 1}/${images.length}] Downloading & uploading...`);
    try {
      await downloadImage(imgUrl, localPath);
      const upload = await uploadMedia(localPath);
      mediaIds.push(upload.media_id);
    } catch (e) {
      console.error(`   ⚠️ Image ${i + 1} failed: ${e.message}`);
    }
  }
  console.log(`   Uploaded: ${mediaIds.length}/${images.length}`);

  // 5. Convert to Twitter format
  const content = markdownToTwitterContent(markdown, mediaIds);
  const contentFile = '/tmp/twitter-article-content.json';
  fs.writeFileSync(contentFile, JSON.stringify(content));
  console.log(`   Content: ${content.blocks.length} blocks, ${content.entity_map.length} entities`);

  // 6. Create draft
  console.log('📝 Creating draft...');
  const result = await cmdCreateDraft(title, contentFile);
  if (!result) { console.error('❌ Failed to create draft'); process.exit(1); }

  // 7. Set cover (first image)
  if (mediaIds.length > 0) {
    console.log('🖼️  Setting cover image...');
    await cmdUpdateCover(result.rest_id, mediaIds[0]);
  }

  console.log(`\n🎉 Done!`);
  console.log(`   Article ID: ${result.rest_id}`);
  console.log(`   Title: ${title}`);
  console.log(`   Images: ${mediaIds.length} inline + cover`);
  console.log(`   Status: Draft (go to x.com/compose/articles to preview & publish)`);

  // 8. Optionally publish
  if (opts.publish) {
    console.log('🚀 Publishing...');
    await cmdPublish(result.rest_id);
  }

  return result;
}

// --- CLI ---
async function main() {
  const args = process.argv.slice(2);
  const cmd = args[0];
  const getArg = (name) => { const i = args.indexOf(`--${name}`); return i >= 0 ? args[i + 1] : null; };

  try {
    switch (cmd) {
      case 'list': await cmdList(); break;
      case 'create-draft': await cmdCreateDraft(getArg('title'), getArg('file')); break;
      case 'create': await cmdCreateDraft(getArg('title'), getArg('file')); break;
      case 'update-title': await cmdUpdateTitle(getArg('id'), getArg('title')); break;
      case 'update-content': await cmdUpdateContent(getArg('id'), getArg('file')); break;
      case 'upload-media': await cmdUploadMedia(getArg('file')); break;
      case 'update-cover': await cmdUpdateCover(getArg('id'), getArg('media-id')); break;
      case 'publish': await cmdPublish(getArg('id')); break;
      case 'delete': await cmdDelete(getArg('id')); break;
      case 'get': await cmdGet(getArg('id')); break;
      case 'notion-to-article':
        await cmdNotionToArticle(getArg('notion-key'), getArg('page-id'), { publish: args.includes('--publish') });
        break;
      default:
        console.log(`Twitter Article CLI - X Premium+ 长文管理

Commands:
  list                                              列出文章草稿
  create-draft --title "xxx"                        创建空草稿
  create --title "xxx" --file article.md            创建并写入内容
  update-title --id <id> --title "xxx"              更新标题
  update-content --id <id> --file a.md              更新内容(.md/.json)
  upload-media --file image.png                     上传图片→media_id
  update-cover --id <id> --media-id <mid>           设置封面图
  publish --id <id>                                 发布
  delete --id <id>                                  删除
  get --id <id>                                     查看详情
  notion-to-article --notion-key <k> --page-id <p>  Notion→Twitter一键同步
    [--publish]                                     直接发布（默认仅草稿）

Env: AUTH_TOKEN, CT0, HTTPS_PROXY`);
    }
  } catch (err) {
    console.error('Error:', err.message);
    process.exit(1);
  }
}

// Export for programmatic use
module.exports = { 
  cmdCreateDraft, cmdUpdateTitle, cmdUpdateContent, cmdUploadMedia,
  cmdUpdateCover, cmdPublish, cmdDelete, cmdGet, cmdList,
  cmdNotionToArticle, markdownToTwitterContent, uploadMedia, downloadImage,
  fetchNotionBlocks, notionBlocksToMarkdown,
};

if (require.main === module) main();
