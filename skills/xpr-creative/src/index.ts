/**
 * Creative Skill — AI image/video generation, PDF creation, GitHub repos, IPFS storage
 *
 * Built-in skill that provides deliverable tools for job completion.
 * Extracted from the main agent runner to validate the skill module format.
 */

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

// ── Shared helpers ──────────────────────────────

const MAX_DELIVERABLES = 200;
const deliverables = new Map<number, { content: string; content_type: string; media_url?: string; created_at: string }>();

function setDeliverable(jobId: number, entry: { content: string; content_type: string; media_url?: string; created_at: string }): void {
  deliverables.set(jobId, entry);
  if (deliverables.size > MAX_DELIVERABLES) {
    const oldest = deliverables.keys().next().value;
    if (oldest !== undefined) deliverables.delete(oldest);
  }
}

/** Get deliverable by job ID (used by the agent runner to serve /deliverables/:jobId) */
export function getDeliverable(jobId: number): { content: string; content_type: string; media_url?: string; created_at: string } | undefined {
  return deliverables.get(jobId);
}

const PINATA_GATEWAY = process.env.PINATA_GATEWAY || '';
function ipfsUrl(cid: string): string {
  if (PINATA_GATEWAY) {
    const gw = PINATA_GATEWAY.replace(/\/+$/, '');
    return `${gw}/ipfs/${cid}`;
  }
  return `https://ipfs.io/ipfs/${cid}`;
}

async function uploadJsonToIpfs(content: string, jobId: number, contentType: string): Promise<string | null> {
  const jwt = process.env.PINATA_JWT;
  if (!jwt) return null;
  try {
    const resp = await fetch('https://api.pinata.cloud/pinning/pinJSONToIPFS', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${jwt}` },
      body: JSON.stringify({
        pinataContent: { job_id: jobId, content, content_type: contentType, created_at: new Date().toISOString() },
        pinataMetadata: { name: `job-${jobId}-deliverable` },
      }),
    });
    const data = await resp.json() as { IpfsHash?: string };
    if (data.IpfsHash) return ipfsUrl(data.IpfsHash);
  } catch (e) { console.error('[ipfs] JSON upload failed:', e); }
  return null;
}

async function uploadBinaryToIpfs(buffer: Buffer, filename: string, mimeType: string): Promise<string | null> {
  const jwt = process.env.PINATA_JWT;
  if (!jwt) return null;
  try {
    const formData = new FormData();
    formData.append('file', new Blob([new Uint8Array(buffer)], { type: mimeType }), filename);
    formData.append('pinataMetadata', JSON.stringify({ name: filename }));
    const resp = await fetch('https://api.pinata.cloud/pinning/pinFileToIPFS', {
      method: 'POST',
      headers: { Authorization: `Bearer ${jwt}` },
      body: formData,
    });
    const data = await resp.json() as { IpfsHash?: string };
    if (data.IpfsHash) return ipfsUrl(data.IpfsHash);
  } catch (e) { console.error('[ipfs] Binary upload failed:', e); }
  return null;
}

const MAX_DOWNLOAD_SIZE = 50 * 1024 * 1024;
async function downloadFromUrl(url: string): Promise<{ buffer: Buffer; mimeType: string } | null> {
  if (!/^https?:\/\//.test(url)) return null;
  try {
    const resp = await fetch(url, { signal: AbortSignal.timeout(30000), redirect: 'follow' });
    if (!resp.ok) return null;
    const contentType = resp.headers.get('content-type') || 'application/octet-stream';
    const contentLength = parseInt(resp.headers.get('content-length') || '0');
    if (contentLength > MAX_DOWNLOAD_SIZE) { console.warn(`[download] Too large: ${contentLength}`); return null; }
    const arrayBuffer = await resp.arrayBuffer();
    if (arrayBuffer.byteLength > MAX_DOWNLOAD_SIZE) return null;
    return { buffer: Buffer.from(arrayBuffer), mimeType: contentType.split(';')[0].trim() };
  } catch (e) { console.error(`[download] Failed: ${url}`, e); return null; }
}

function stripMarkdownInline(text: string): string {
  text = text.replace(/<cite[^>]*>([\s\S]*?)<\/cite>/g, '$1');
  text = text.replace(/<[^>]+>/g, '');
  return text.replace(/\*\*(.+?)\*\*/g, '$1').replace(/`([^`]+)`/g, '$1').replace(/\[([^\]]+)\]\([^\)]+\)/g, '$1');
}

function extractImages(text: string): { alt: string; url: string }[] {
  const matches: { alt: string; url: string }[] = [];
  const re = /!\[([^\]]*)\]\((https?:\/\/[^\)]+)\)/g;
  let m;
  while ((m = re.exec(text)) !== null) {
    matches.push({ alt: m[1], url: m[2] });
  }
  return matches;
}

async function downloadImage(url: string): Promise<{ buffer: Buffer; type: string } | null> {
  try {
    const resp = await fetch(url, { signal: AbortSignal.timeout(15000) });
    if (!resp.ok) return null;
    const ct = (resp.headers.get('content-type') || '').split(';')[0].trim();
    if (!ct.startsWith('image/')) return null;
    const buf = Buffer.from(await resp.arrayBuffer());
    if (buf.length < 100) return null;
    const type = ct.includes('png') ? 'png' : ct.includes('jpeg') || ct.includes('jpg') ? 'jpeg' : '';
    if (!type) return null;
    return { buffer: buf, type };
  } catch {
    return null;
  }
}

async function generatePdfFromMarkdown(content: string): Promise<Buffer> {
  const PDFDocument = require('pdfkit');

  const allImages = extractImages(content);
  const imageCache = new Map<string, { buffer: Buffer; type: string }>();
  if (allImages.length > 0) {
    await Promise.allSettled(
      allImages.slice(0, 10).map(async (img) => {
        const data = await downloadImage(img.url);
        if (data) imageCache.set(img.url, data);
      })
    );
  }

  return new Promise((resolve, reject) => {
    try {
      const doc = new PDFDocument({ size: 'A4', margin: 50 });
      const chunks: Buffer[] = [];
      doc.on('data', (chunk: Buffer) => chunks.push(chunk));
      doc.on('end', () => resolve(Buffer.concat(chunks)));
      doc.on('error', reject);

      const pageWidth = 595.28 - 100;
      const lines = content.split('\n');
      let inCodeBlock = false;

      // ── Table rendering helper ──
      function renderTable(tableLines: string[]): void {
        // Parse rows, skip separator rows (|---|---|)
        const rows: string[][] = [];
        let headerIdx = -1;
        for (let i = 0; i < tableLines.length; i++) {
          const raw = tableLines[i].trim();
          // Separator row
          if (/^\|[\s:]*-{2,}[\s:|-]*\|?\s*$/.test(raw)) {
            headerIdx = i - 1;
            continue;
          }
          const cells = raw.replace(/^\|/, '').replace(/\|$/, '').split('|').map(c => stripMarkdownInline(c.trim()));
          rows.push(cells);
        }
        if (rows.length === 0) return;

        const numCols = Math.max(...rows.map(r => r.length));
        const fontSize = numCols > 5 ? 8 : 9;
        const cellPadding = 4;
        const rowHeight = fontSize + cellPadding * 2 + 2;

        // Measure column widths — proportional based on max content width
        doc.fontSize(fontSize).font('Helvetica');
        const colMaxWidths: number[] = new Array(numCols).fill(0);
        for (const row of rows) {
          for (let c = 0; c < numCols; c++) {
            const text = row[c] || '';
            const w = doc.widthOfString(text);
            if (w > colMaxWidths[c]) colMaxWidths[c] = w;
          }
        }
        // Scale columns to fit page width
        const totalMaxWidth = colMaxWidths.reduce((s, w) => s + w, 0);
        const availableWidth = pageWidth - (numCols * cellPadding * 2);
        const colWidths = colMaxWidths.map(w => {
          const scaled = totalMaxWidth > 0 ? (w / totalMaxWidth) * availableWidth : availableWidth / numCols;
          return Math.max(scaled, 30); // min 30pt per column
        });
        const tableWidth = colWidths.reduce((s, w) => s + cellPadding * 2 + w, 0);

        doc.moveDown(0.3);
        const startX = 50;

        for (let r = 0; r < rows.length; r++) {
          const isHeader = (headerIdx >= 0 && r === 0);

          // Page break check
          if (doc.y + rowHeight > 780) {
            doc.addPage();
          }

          const y = doc.y;
          let x = startX;

          // Background for header
          if (isHeader) {
            doc.rect(x, y, tableWidth, rowHeight).fillColor('#f0f0f0').fill().fillColor('#000000');
          }

          // Draw cells
          for (let c = 0; c < numCols; c++) {
            const cellWidth = colWidths[c] + cellPadding * 2;
            const text = rows[r][c] || '';
            // Cell border
            doc.rect(x, y, cellWidth, rowHeight).strokeColor('#cccccc').lineWidth(0.5).stroke();
            // Cell text
            doc.fontSize(fontSize).font(isHeader ? 'Helvetica-Bold' : 'Helvetica').fillColor('#000000');
            doc.text(text, x + cellPadding, y + cellPadding, {
              width: colWidths[c],
              height: rowHeight - cellPadding,
              ellipsis: true,
              lineBreak: false,
            });
            x += cellWidth;
          }
          doc.y = y + rowHeight;
        }
        doc.moveDown(0.3);
      }

      // ── Process lines ──
      let tableBuffer: string[] = [];
      for (let li = 0; li <= lines.length; li++) {
        const line = li < lines.length ? lines[li] : '';
        const isTableLine = li < lines.length && /^\s*\|/.test(line);

        // Flush buffered table when we hit a non-table line
        if (!isTableLine && tableBuffer.length > 0) {
          renderTable(tableBuffer);
          tableBuffer = [];
        }
        if (li >= lines.length) break;

        if (isTableLine) {
          tableBuffer.push(line);
          continue;
        }

        if (line.startsWith('```')) { inCodeBlock = !inCodeBlock; doc.moveDown(0.3); continue; }
        if (inCodeBlock) { doc.fontSize(9).font('Courier').text(line); continue; }

        const imgMatch = line.match(/^!\[([^\]]*)\]\((https?:\/\/[^\)]+)\)\s*$/);
        if (imgMatch) {
          const imgData = imageCache.get(imgMatch[2]);
          if (imgData) {
            try {
              doc.moveDown(0.3);
              doc.image(imgData.buffer, { fit: [pageWidth, 300], align: 'center' });
              doc.moveDown(0.3);
              if (imgMatch[1]) {
                doc.fontSize(9).font('Helvetica').fillColor('#666666')
                  .text(imgMatch[1], { align: 'center' }).fillColor('#000000');
              }
              doc.moveDown(0.3);
            } catch {
              doc.fontSize(9).font('Helvetica').fillColor('#666666')
                .text(`[Image: ${imgMatch[1] || imgMatch[2]}]`, { align: 'center' }).fillColor('#000000');
            }
          } else {
            doc.fontSize(9).font('Helvetica').fillColor('#666666')
              .text(`[Image: ${imgMatch[1] || imgMatch[2]}]`, { align: 'center' }).fillColor('#000000');
          }
          continue;
        }

        if (/^---+$/.test(line.trim())) {
          doc.moveDown(0.3);
          const y = doc.y;
          doc.moveTo(50, y).lineTo(545, y).strokeColor('#cccccc').lineWidth(0.5).stroke();
          doc.moveDown(0.5);
          continue;
        }

        // Blockquote
        if (line.startsWith('> ')) {
          doc.moveDown(0.2);
          doc.fontSize(10).font('Helvetica-Oblique').fillColor('#555555')
            .text(stripMarkdownInline(line.slice(2)), { indent: 15 })
            .fillColor('#000000');
          doc.moveDown(0.2);
          continue;
        }

        if (line.startsWith('# ')) {
          doc.moveDown(0.5).fontSize(22).font('Helvetica-Bold').text(stripMarkdownInline(line.slice(2))).moveDown(0.3);
        } else if (line.startsWith('## ')) {
          doc.moveDown(0.4).fontSize(17).font('Helvetica-Bold').text(stripMarkdownInline(line.slice(3))).moveDown(0.2);
        } else if (line.startsWith('### ')) {
          doc.moveDown(0.3).fontSize(14).font('Helvetica-Bold').text(stripMarkdownInline(line.slice(4))).moveDown(0.2);
        } else if (/^[-*] /.test(line)) {
          doc.fontSize(11).font('Helvetica').text(`  \u2022 ${stripMarkdownInline(line.slice(2))}`, { indent: 10 });
        } else if (/^\d+\.\s/.test(line)) {
          const m = line.match(/^(\d+\.)\s(.*)/);
          if (m) doc.fontSize(11).font('Helvetica').text(`  ${m[1]} ${stripMarkdownInline(m[2])}`, { indent: 10 });
        } else if (line.trim() === '') {
          doc.moveDown(0.4);
        } else {
          doc.fontSize(11).font('Helvetica').text(stripMarkdownInline(line));
        }
      }
      doc.end();
    } catch (err) { reject(err); }
  });
}

async function createGithubRepo(
  jobId: number, repoName: string, description: string, files: Record<string, string>
): Promise<string | null> {
  const token = process.env.GITHUB_TOKEN;
  const owner = process.env.GITHUB_OWNER;
  if (!token || !owner) return null;
  const headers: Record<string, string> = {
    Authorization: `Bearer ${token}`, Accept: 'application/vnd.github+json',
    'Content-Type': 'application/json', 'X-GitHub-Api-Version': '2022-11-28',
  };
  try {
    const createResp = await fetch('https://api.github.com/user/repos', {
      method: 'POST', headers,
      body: JSON.stringify({ name: repoName, description, private: false, auto_init: true }),
    });
    if (!createResp.ok) { console.error('[github] Create repo failed:', await createResp.text()); return null; }
    const repo = await createResp.json() as { full_name: string; html_url: string; default_branch: string };

    const refResp = await fetch(`https://api.github.com/repos/${repo.full_name}/git/ref/heads/${repo.default_branch}`, { headers });
    const refData = await refResp.json() as { object: { sha: string } };
    const commitResp = await fetch(`https://api.github.com/repos/${repo.full_name}/git/commits/${refData.object.sha}`, { headers });
    const commitData = await commitResp.json() as { tree: { sha: string } };

    const treeItems: Array<{ path: string; mode: string; type: string; sha: string }> = [];
    for (const [filePath, fileContent] of Object.entries(files)) {
      const blobResp = await fetch(`https://api.github.com/repos/${repo.full_name}/git/blobs`, {
        method: 'POST', headers, body: JSON.stringify({ content: fileContent, encoding: 'utf-8' }),
      });
      const blobData = await blobResp.json() as { sha: string };
      treeItems.push({ path: filePath, mode: '100644', type: 'blob', sha: blobData.sha });
    }
    const treeResp = await fetch(`https://api.github.com/repos/${repo.full_name}/git/trees`, {
      method: 'POST', headers, body: JSON.stringify({ base_tree: commitData.tree.sha, tree: treeItems }),
    });
    const treeData = await treeResp.json() as { sha: string };

    const newCommitResp = await fetch(`https://api.github.com/repos/${repo.full_name}/git/commits`, {
      method: 'POST', headers,
      body: JSON.stringify({ message: `Job #${jobId} deliverable`, tree: treeData.sha, parents: [refData.object.sha] }),
    });
    const newCommitData = await newCommitResp.json() as { sha: string };
    await fetch(`https://api.github.com/repos/${repo.full_name}/git/refs/heads/${repo.default_branch}`, {
      method: 'PATCH', headers, body: JSON.stringify({ sha: newCommitData.sha }),
    });

    console.log(`[github] Created repo: ${repo.html_url}`);
    return repo.html_url;
  } catch (e) { console.error('[github] Failed:', e); return null; }
}

function toDataUri(content: string, contentType: string): string {
  const json = JSON.stringify({ content, content_type: contentType, created_at: new Date().toISOString() });
  return `data:application/json;base64,${Buffer.from(json).toString('base64')}`;
}

// ── Skill entry point ───────────────────────────

export default function creativeSkill(api: SkillApi): void {
  // ── store_deliverable ──
  api.registerTool({
    name: 'store_deliverable',
    description: [
      'Store job deliverable content before delivering on-chain. Call this BEFORE xpr_deliver_job.',
      'Routes by content_type:',
      '  text/markdown (default) — stores as JSON on IPFS',
      '  application/pdf — generates PDF from your Markdown, uploads binary to IPFS.',
      '    Images referenced as ![alt](url) in the Markdown are downloaded and embedded in the PDF.',
      '    Do NOT include <cite> or other HTML tags in the content — use clean Markdown only.',
      '  image/*, audio/*, video/* — downloads source_url and uploads binary to IPFS',
      '  text/csv, text/plain, text/html — stores as JSON on IPFS',
    ].join('\n'),
    parameters: {
      type: 'object',
      required: ['job_id', 'content'],
      properties: {
        job_id: { type: 'number', description: 'Job ID' },
        content: { type: 'string', description: 'Full deliverable content (markdown, text, CSV, etc.). For media types, can be empty if source_url is provided.' },
        content_type: { type: 'string', description: 'MIME type: text/markdown (default), application/pdf, image/png, audio/mpeg, video/mp4, text/csv, etc.' },
        source_url: { type: 'string', description: 'URL to download binary content from (for image/audio/video). The file is downloaded and uploaded to IPFS.' },
        filename: { type: 'string', description: 'Optional filename for the deliverable (e.g. "report.pdf")' },
      },
    },
    handler: async ({ job_id, content, content_type, source_url, filename }: {
      job_id: number; content: string; content_type?: string; source_url?: string; filename?: string;
    }) => {
      const ct = content_type || 'text/markdown';
      const ts = new Date().toISOString();

      if (ct === 'application/pdf') {
        try {
          const pdfBuffer = await generatePdfFromMarkdown(content);
          setDeliverable(job_id, { content, content_type: ct, created_at: ts });
          const url = await uploadBinaryToIpfs(pdfBuffer, filename || `job-${job_id}.pdf`, 'application/pdf');
          if (url) {
            console.log(`[deliverable] Job ${job_id} PDF → IPFS: ${url}`);
            return { stored: true, url, storage: 'ipfs', content_type: ct };
          }
          const dataUri = `data:application/pdf;base64,${pdfBuffer.toString('base64')}`;
          console.log(`[deliverable] Job ${job_id} PDF → data URI`);
          return { stored: true, url: dataUri, storage: 'data_uri', content_type: ct };
        } catch (err: any) {
          console.error(`[deliverable] PDF generation failed:`, err.message);
          return { stored: false, error: `PDF generation failed: ${err.message}` };
        }
      }

      if (ct.startsWith('image/') || ct.startsWith('audio/') || ct.startsWith('video/') || ct === 'application/octet-stream') {
        let buffer: Buffer | null = null;
        let mimeType = ct;

        if (source_url) {
          const downloaded = await downloadFromUrl(source_url);
          if (downloaded) { buffer = downloaded.buffer; mimeType = downloaded.mimeType || ct; }
        } else if (content) {
          buffer = Buffer.from(content, 'base64');
        }

        if (!buffer) return { stored: false, error: 'Failed to obtain binary content. Provide source_url for media types.' };

        setDeliverable(job_id, { content: source_url || '[binary]', content_type: mimeType, created_at: ts });
        const ext = mimeType.split('/')[1]?.split('+')[0] || 'bin';
        const url = await uploadBinaryToIpfs(buffer, filename || `job-${job_id}.${ext}`, mimeType);
        if (url) {
          console.log(`[deliverable] Job ${job_id} ${mimeType} → IPFS: ${url}`);
          return { stored: true, url, storage: 'ipfs', content_type: mimeType };
        }
        const dataUri = `data:${mimeType};base64,${buffer.toString('base64')}`;
        return { stored: true, url: dataUri, storage: 'data_uri', content_type: mimeType };
      }

      setDeliverable(job_id, { content, content_type: ct, created_at: ts });
      const url = await uploadJsonToIpfs(content, job_id, ct);
      if (url) {
        console.log(`[deliverable] Job ${job_id} ${ct} → IPFS: ${url}`);
        return { stored: true, url, storage: 'ipfs', content_type: ct };
      }
      const dataUri = toDataUri(content, ct);
      console.log(`[deliverable] Job ${job_id} ${ct} → data URI (${dataUri.length} chars)`);
      return { stored: true, url: dataUri, storage: 'data_uri', content_type: ct };
    },
  });

  // ── create_github_repo ──
  api.registerTool({
    name: 'create_github_repo',
    description: 'Create a GitHub repository with code deliverables for a job. Requires GITHUB_TOKEN and GITHUB_OWNER env vars. Returns the repo URL to use as evidence_uri when calling xpr_deliver_job.',
    parameters: {
      type: 'object',
      required: ['job_id', 'name', 'files'],
      properties: {
        job_id: { type: 'number', description: 'Job ID' },
        name: { type: 'string', description: 'Repository name (e.g. "job-59-credit-union-report")' },
        description: { type: 'string', description: 'Repository description' },
        files: { type: 'object', description: 'Object mapping file paths to content, e.g. {"src/index.ts": "...", "README.md": "..."}' },
      },
    },
    handler: async ({ job_id, name, description, files }: {
      job_id: number; name: string; description?: string; files: Record<string, string>;
    }) => {
      if (!process.env.GITHUB_TOKEN || !process.env.GITHUB_OWNER) {
        return { error: 'GitHub not configured. Set GITHUB_TOKEN and GITHUB_OWNER in .env' };
      }
      const repoUrl = await createGithubRepo(job_id, name, description || `Deliverable for job #${job_id}`, files);
      if (!repoUrl) return { error: 'Failed to create GitHub repository' };

      setDeliverable(job_id, {
        content: `GitHub repository: ${repoUrl}\n\nFiles: ${Object.keys(files).join(', ')}`,
        content_type: 'github:repo', media_url: repoUrl, created_at: new Date().toISOString(),
      });
      return { stored: true, url: repoUrl, storage: 'github', content_type: 'github:repo' };
    },
  });

  // ── generate_image ──
  api.registerTool({
    name: 'generate_image',
    description: [
      'Generate an AI image using Google Nano Banana and optionally store it as a job deliverable in one step.',
      'If job_id is provided: generates image, uploads to IPFS, and returns the evidence_uri ready for xpr_deliver_job.',
      'If no job_id: just returns the image URL.',
      'Requires REPLICATE_API_TOKEN in .env.',
    ].join(' '),
    parameters: {
      type: 'object',
      required: ['prompt'],
      properties: {
        prompt: { type: 'string', description: 'Detailed description of the image to generate. Be specific about style, composition, colors, lighting.' },
        job_id: { type: 'number', description: 'If provided, auto-stores the generated image as an IPFS deliverable for this job. Use the returned evidence_uri directly with xpr_deliver_job.' },
        aspect_ratio: { type: 'string', description: 'Aspect ratio: "1:1" (default), "16:9", "9:16", "4:3", "3:4"' },
      },
    },
    handler: async ({ prompt, job_id, aspect_ratio }: { prompt: string; job_id?: number; aspect_ratio?: string }) => {
      const token = process.env.REPLICATE_API_TOKEN;
      if (!token) return { error: 'REPLICATE_API_TOKEN not set. Add it to .env to enable AI image generation.' };

      try {
        const createResp = await fetch('https://api.replicate.com/v1/models/google/imagen-3/predictions', {
          method: 'POST',
          headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json', Prefer: 'wait' },
          body: JSON.stringify({ input: { prompt, aspect_ratio: aspect_ratio || '1:1', output_format: 'png' } }),
        });

        if (!createResp.ok) {
          const errText = await createResp.text();
          return { error: `Replicate API error: ${createResp.status} ${errText}` };
        }

        let result = await createResp.json() as any;

        if (result.status !== 'succeeded' && result.status !== 'failed') {
          const deadline = Date.now() + 60000;
          while (result.status !== 'succeeded' && result.status !== 'failed' && Date.now() < deadline) {
            await new Promise(r => setTimeout(r, 1000));
            const pollResp = await fetch(result.urls?.get || `https://api.replicate.com/v1/predictions/${result.id}`, {
              headers: { Authorization: `Bearer ${token}` },
            });
            result = await pollResp.json();
          }
        }

        if (result.status === 'failed') return { error: `Image generation failed: ${result.error || 'Unknown error'}` };
        if (result.status !== 'succeeded') return { error: 'Image generation timed out (60s). Try a simpler prompt.' };

        const outputs: string[] = Array.isArray(result.output) ? result.output : [result.output];
        console.log(`[replicate] Image generated: ${outputs[0]}`);

        if (job_id != null) {
          const imageUrl = outputs[0];
          const downloaded = await downloadFromUrl(imageUrl);
          if (downloaded) {
            const url = await uploadBinaryToIpfs(downloaded.buffer, `job-${job_id}.png`, 'image/png');
            if (url) {
              setDeliverable(job_id, { content: imageUrl, content_type: 'image/png', media_url: url, created_at: new Date().toISOString() });
              console.log(`[replicate] Job ${job_id} image → IPFS: ${url}`);
              return {
                success: true, evidence_uri: url, image_url: imageUrl, stored: true,
                instruction: 'Image generated and stored on IPFS. Now call xpr_deliver_job with evidence_uri to complete delivery.',
              };
            }
          }
          setDeliverable(job_id, { content: outputs[0], content_type: 'image/png', media_url: outputs[0], created_at: new Date().toISOString() });
          return {
            success: true, evidence_uri: outputs[0], image_url: outputs[0], stored: true,
            instruction: 'Image generated (IPFS upload failed, using direct URL). Call xpr_deliver_job with evidence_uri.',
          };
        }

        return {
          success: true, urls: outputs, primary_url: outputs[0], prompt, model: 'google-imagen-3',
          instruction: 'Call store_deliverable with content_type "image/png" and source_url set to primary_url, then xpr_deliver_job.',
        };
      } catch (e: any) {
        return { error: `Image generation failed: ${e.message}` };
      }
    },
  });

  // ── generate_video ──
  api.registerTool({
    name: 'generate_video',
    description: [
      'Generate an AI video and optionally store it as a job deliverable in one step.',
      'If job_id is provided: generates video, uploads to IPFS, and returns the evidence_uri ready for xpr_deliver_job.',
      'For text-to-video: provide just a prompt. For image-to-video: also provide image_url.',
      'Requires REPLICATE_API_TOKEN in .env.',
    ].join(' '),
    parameters: {
      type: 'object',
      required: ['prompt'],
      properties: {
        prompt: { type: 'string', description: 'Description of the video to generate. Be specific about motion, scene, and style.' },
        job_id: { type: 'number', description: 'If provided, auto-stores the generated video as an IPFS deliverable for this job.' },
        image_url: { type: 'string', description: 'Optional: URL of a source image to animate (image-to-video mode).' },
      },
    },
    handler: async ({ prompt, job_id, image_url }: { prompt: string; job_id?: number; image_url?: string }) => {
      const token = process.env.REPLICATE_API_TOKEN;
      if (!token) return { error: 'REPLICATE_API_TOKEN not set. Add it to .env to enable AI video generation.' };

      try {
        const model = image_url
          ? 'stability-ai/stable-video-diffusion:3f0457e4619daac51203dedb472816fd4af51f3149fa7a9e0b5ffcf1b8172438'
          : 'minimax/video-01-live';
        const input: Record<string, any> = { prompt };
        if (image_url) {
          input.input_image = image_url;
          delete input.prompt;
        }

        const url = model.includes(':')
          ? 'https://api.replicate.com/v1/predictions'
          : `https://api.replicate.com/v1/models/${model}/predictions`;
        const body: Record<string, any> = { input };
        if (model.includes(':')) body.version = model.split(':')[1];

        const createResp = await fetch(url, {
          method: 'POST',
          headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
          body: JSON.stringify(body),
        });

        if (!createResp.ok) {
          const errText = await createResp.text();
          return { error: `Replicate API error: ${createResp.status} ${errText}` };
        }

        let result = await createResp.json() as any;
        console.log(`[replicate] Video prediction created: ${result.id} (model: ${model.split(':')[0]})`);

        const deadline = Date.now() + 300000;
        while (result.status !== 'succeeded' && result.status !== 'failed' && Date.now() < deadline) {
          await new Promise(r => setTimeout(r, 3000));
          const pollResp = await fetch(result.urls?.get || `https://api.replicate.com/v1/predictions/${result.id}`, {
            headers: { Authorization: `Bearer ${token}` },
          });
          result = await pollResp.json();
        }

        if (result.status === 'failed') return { error: `Video generation failed: ${result.error || 'Unknown error'}` };
        if (result.status !== 'succeeded') return { error: 'Video generation timed out (5min). Try a simpler prompt.' };

        const output = Array.isArray(result.output) ? result.output[0] : result.output;
        console.log(`[replicate] Video generated: ${output}`);

        if (job_id != null && output) {
          const downloaded = await downloadFromUrl(output);
          if (downloaded) {
            const ipfsResult = await uploadBinaryToIpfs(downloaded.buffer, `job-${job_id}.mp4`, 'video/mp4');
            if (ipfsResult) {
              setDeliverable(job_id, { content: output, content_type: 'video/mp4', media_url: ipfsResult, created_at: new Date().toISOString() });
              console.log(`[replicate] Job ${job_id} video → IPFS: ${ipfsResult}`);
              return {
                success: true, evidence_uri: ipfsResult, video_url: output, stored: true,
                instruction: 'Video generated and stored on IPFS. Now call xpr_deliver_job with evidence_uri to complete delivery.',
              };
            }
          }
          setDeliverable(job_id, { content: output, content_type: 'video/mp4', media_url: output, created_at: new Date().toISOString() });
          return { success: true, evidence_uri: output, video_url: output, stored: true, instruction: 'Call xpr_deliver_job with evidence_uri.' };
        }

        return {
          success: true, url: output, prompt, model: model.split(':')[0],
          instruction: 'Call store_deliverable with content_type "video/mp4" and source_url set to the url, then xpr_deliver_job.',
        };
      } catch (e: any) {
        return { error: `Video generation failed: ${e.message}` };
      }
    },
  });
}
