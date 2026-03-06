import axios from 'axios';
import FormData from 'form-data';
import { createReadStream, statSync } from 'fs';
import { basename } from 'path';
import { loadConfig } from './config.js';

let client = null;

// Custom error class for GraphQL errors
class GraphQLError extends Error {
  constructor(errors) {
    const messages = errors.map(e => e.message).join('; ');
    super(messages);
    this.name = 'GraphQLError';
    this.errors = errors;
  }
}

// Sanitize string for safe GraphQL interpolation
// Escapes quotes and backslashes to prevent injection
function sanitizeString(str) {
  if (str === null || str === undefined) return '';
  return String(str)
    .replace(/\\/g, '\\\\')
    .replace(/"/g, '\\"')
    .replace(/\n/g, '\\n')
    .replace(/\r/g, '\\r')
    .replace(/\t/g, '\\t');
}

// Validate ID is a positive integer
function validateId(id) {
  const num = parseInt(id, 10);
  if (isNaN(num) || num < 1) {
    throw new Error(`Invalid ID: ${id}`);
  }
  return num;
}

// Validate path format
function validatePath(path) {
  if (!path || typeof path !== 'string') {
    throw new Error('Path is required');
  }
  // Remove leading slash if present for consistency
  const cleanPath = path.startsWith('/') ? path.slice(1) : path;
  // Check for invalid characters
  if (/[<>:"|?*]/.test(cleanPath)) {
    throw new Error(`Invalid characters in path: ${path}`);
  }
  return cleanPath;
}

// Helper to execute GraphQL and handle errors
async function graphql(query) {
  const response = await getClient().post('/graphql', { query });

  // Check for GraphQL errors
  if (response.data?.errors && response.data.errors.length > 0) {
    throw new GraphQLError(response.data.errors);
  }

  return response.data?.data;
}

function getClient() {
  if (client) return client;

  const config = loadConfig();
  client = axios.create({
    baseURL: config.url,
    headers: {
      'Authorization': `Bearer ${config.apiToken}`,
      'Content-Type': 'application/json'
    },
    timeout: 30000
  });

  // Interceptor to provide better error messages
  client.interceptors.response.use(
    response => response,
    error => {
      if (error.response?.data?.errors) {
        throw new GraphQLError(error.response.data.errors);
      }
      throw error;
    }
  );

  return client;
}

// ============ PAGES ============

export async function listPages(options = {}) {
  const { tag, author, locale, limit = 50 } = options;

  // Wiki.js 2.x GraphQL - list doesn't accept parameters
  const query = `
    query {
      pages {
        list {
          id
          path
          title
          description
          locale
          createdAt
          updatedAt
          tags
          isPublished
        }
      }
    }
  `;

  const data = await graphql(query);
  let pages = data?.pages?.list || [];

  // Client-side filtering
  if (locale) {
    pages = pages.filter(p => p.locale === locale);
  }
  if (tag) {
    pages = pages.filter(p => p.tags && p.tags.includes(tag));
  }
  if (author) {
    // Note: authorName not available in list query, would need to fetch each page
    pages = pages.filter(p => p.authorName && p.authorName.toLowerCase().includes(author.toLowerCase()));
  }

  // Apply limit
  return pages.slice(0, limit);
}

export async function searchPages(searchQuery, options = {}) {
  const { limit = 50 } = options;

  const query = `
    query {
      pages {
        search(query: "${sanitizeString(searchQuery)}") {
          results {
            id
            path
            title
            description
            locale
          }
          suggestions
          totalHits
        }
      }
    }
  `;

  const data = await graphql(query);
  const result = data?.pages?.search || { results: [], totalHits: 0 };

  return {
    results: result.results.slice(0, limit),
    totalHits: result.totalHits,
    suggestions: result.suggestions
  };
}

export async function getPage(idOrPath, options = {}) {
  const config = loadConfig();
  const { withChildren = false, locale = config.defaultLocale || 'en' } = options;

  let page;

  if (typeof idOrPath === 'number') {
    // Get by ID
    const validId = validateId(idOrPath);
    const query = `
      query {
        pages {
          single(id: ${validId}) {
            id
            path
            title
            description
            content
            render
            locale
            createdAt
            updatedAt
            authorName
            tags { tag }
            isPublished
            isPrivate
          }
        }
      }
    `;
    const data = await graphql(query);
    page = data?.pages?.single;
    // Flatten tags
    if (page && page.tags) {
      page.tags = page.tags.map(t => t.tag);
    }
  } else {
    // Get by path with configurable locale
    const safePath = sanitizeString(idOrPath);
    const safeLocale = sanitizeString(locale);
    const query = `
      query {
        pages {
          singleByPath(path: "${safePath}", locale: "${safeLocale}") {
            id
            path
            title
            description
            content
            render
            locale
            createdAt
            updatedAt
            authorName
            tags { tag }
            isPublished
            isPrivate
          }
        }
      }
    `;
    const data = await graphql(query);
    page = data?.pages?.singleByPath;
    // Flatten tags
    if (page && page.tags) {
      page.tags = page.tags.map(t => t.tag);
    }
  }

  if (!page) {
    throw new Error(`Page not found: ${idOrPath}`);
  }

  // Get children if requested
  if (withChildren) {
    const childQuery = `
      query {
        pages {
          list {
            id
            path
            title
          }
        }
      }
    `;
    const childData = await graphql(childQuery);
    const allPages = childData?.pages?.list || [];
    page.children = allPages.filter(p =>
      p.path.startsWith(page.path + '/') && p.id !== page.id
    );
  }

  return page;
}

export async function createPage(path, title, options = {}) {
  const config = loadConfig();
  const {
    content = '',
    description = '',
    tags = [],
    locale = config.defaultLocale || 'en',
    editor = config.defaultEditor || 'markdown',
    isPublished = true,
    isPrivate = false
  } = options;

  // Validate and sanitize inputs
  const safePath = sanitizeString(validatePath(path));
  const safeEditor = sanitizeString(editor);
  const safeLocale = sanitizeString(locale);

  const mutation = `
    mutation {
      pages {
        create(
          content: ${JSON.stringify(content)}
          description: ${JSON.stringify(description)}
          editor: "${safeEditor}"
          isPrivate: ${isPrivate}
          isPublished: ${isPublished}
          locale: "${safeLocale}"
          path: "${safePath}"
          tags: ${JSON.stringify(tags)}
          title: ${JSON.stringify(title)}
        ) {
          responseResult {
            succeeded
            errorCode
            message
          }
          page {
            id
            path
            title
          }
        }
      }
    }
  `;

  const data = await graphql(mutation);
  const result = data?.pages?.create;

  if (!result?.responseResult?.succeeded) {
    throw new Error(result?.responseResult?.message || 'Failed to create page');
  }

  return result.page;
}

export async function updatePage(id, options = {}) {
  const {
    content,
    title,
    description,
    tags,
    isPublished
  } = options;

  // Validate ID
  const validId = validateId(id);

  // First get current page data
  const currentPage = await getPage(validId);

  const mutation = `
    mutation {
      pages {
        update(
          id: ${validId}
          content: ${JSON.stringify(content ?? currentPage.content)}
          description: ${JSON.stringify(description ?? currentPage.description ?? '')}
          isPublished: ${isPublished ?? currentPage.isPublished}
          tags: ${JSON.stringify(tags ?? currentPage.tags ?? [])}
          title: ${JSON.stringify(title ?? currentPage.title)}
        ) {
          responseResult {
            succeeded
            errorCode
            message
          }
          page {
            id
            path
            title
            updatedAt
          }
        }
      }
    }
  `;

  const data = await graphql(mutation);
  const result = data?.pages?.update;

  if (!result?.responseResult?.succeeded) {
    throw new Error(result?.responseResult?.message || 'Failed to update page');
  }

  return result.page;
}

export async function movePage(id, newPath, options = {}) {
  const config = loadConfig();
  const { locale = config.defaultLocale || 'en' } = options;

  // Validate and sanitize inputs
  const validId = validateId(id);
  const safePath = sanitizeString(validatePath(newPath));
  const safeLocale = sanitizeString(locale);

  const mutation = `
    mutation {
      pages {
        move(
          id: ${validId}
          destinationPath: "${safePath}"
          destinationLocale: "${safeLocale}"
        ) {
          responseResult {
            succeeded
            errorCode
            message
          }
        }
      }
    }
  `;

  const data = await graphql(mutation);
  const result = data?.pages?.move;

  if (!result?.responseResult?.succeeded) {
    throw new Error(result?.responseResult?.message || 'Failed to move page');
  }

  return { success: true, newPath };
}

export async function deletePage(id, options = {}) {
  const validId = validateId(id);

  const mutation = `
    mutation {
      pages {
        delete(id: ${validId}) {
          responseResult {
            succeeded
            errorCode
            message
          }
        }
      }
    }
  `;

  const data = await graphql(mutation);
  const result = data?.pages?.delete;

  if (!result?.responseResult?.succeeded) {
    throw new Error(result?.responseResult?.message || 'Failed to delete page');
  }

  return { success: true, id };
}

// ============ TAGS ============

export async function listTags() {
  const query = `
    query {
      pages {
        tags {
          id
          tag
          title
          createdAt
          updatedAt
        }
      }
    }
  `;

  const data = await graphql(query);
  return data?.pages?.tags || [];
}

// ============ ASSETS ============

export async function listAssets(options = {}) {
  const { folder = '', limit = 50 } = options;

  const query = `
    query {
      assets {
        list(folderId: 0, kind: ALL) {
          id
          filename
          ext
          kind
          mime
          fileSize
          createdAt
          updatedAt
        }
      }
    }
  `;

  const data = await graphql(query);
  let assets = data?.assets?.list || [];

  // Filter by folder path if specified
  if (folder) {
    assets = assets.filter(a => a.filename.startsWith(folder));
  }

  return assets.slice(0, limit);
}

export async function uploadAsset(filePath, options = {}) {
  const { folder = '', rename } = options;

  const filename = rename || basename(filePath);
  const stats = statSync(filePath);

  const form = new FormData();
  form.append('mediaUpload', createReadStream(filePath), {
    filename,
    contentType: 'application/octet-stream'
  });

  const config = loadConfig();
  const response = await axios.post(
    `${config.url}/u`,
    form,
    {
      headers: {
        ...form.getHeaders(),
        'Authorization': `Bearer ${config.apiToken}`
      }
    }
  );

  return response.data;
}

export async function deleteAsset(id) {
  const validId = validateId(id);

  const mutation = `
    mutation {
      assets {
        deleteAsset(id: ${validId}) {
          responseResult {
            succeeded
            errorCode
            message
          }
        }
      }
    }
  `;

  const data = await graphql(mutation);
  const result = data?.assets?.deleteAsset;

  if (!result?.responseResult?.succeeded) {
    throw new Error(result?.responseResult?.message || 'Failed to delete asset');
  }

  return { success: true, id };
}

// ============ SYSTEM ============

export async function getHealth() {
  const query = `
    query {
      system {
        info {
          configFile
          currentVersion
          latestVersion
          operatingSystem
          hostname
          platform
        }
      }
    }
  `;

  const data = await graphql(query);
  return data?.system?.info;
}

export async function getStats() {
  const query = `
    query {
      pages {
        list {
          id
          locale
          isPublished
          tags
        }
      }
    }
  `;

  const data = await graphql(query);
  const pages = data?.pages?.list || [];

  // Calculate stats
  const stats = {
    totalPages: pages.length,
    publishedPages: pages.filter(p => p.isPublished).length,
    draftPages: pages.filter(p => !p.isPublished).length,
    locales: {},
    topTags: {}
  };

  pages.forEach(p => {
    // Count by locale
    stats.locales[p.locale] = (stats.locales[p.locale] || 0) + 1;

    // Count tags
    (p.tags || []).forEach(tag => {
      stats.topTags[tag] = (stats.topTags[tag] || 0) + 1;
    });
  });

  return stats;
}

// ============ VERSIONS ============

export async function getPageVersions(id) {
  const validId = validateId(id);

  const query = `
    query {
      pages {
        history(id: ${validId}) {
          versionId
          versionDate
          authorName
          actionType
        }
      }
    }
  `;

  const data = await graphql(query);
  return data?.pages?.history || [];
}

export async function revertPage(pageId, versionId) {
  const validPageId = validateId(pageId);
  const validVersionId = validateId(versionId);

  const mutation = `
    mutation {
      pages {
        restore(pageId: ${validPageId}, versionId: ${validVersionId}) {
          responseResult {
            succeeded
            errorCode
            message
          }
        }
      }
    }
  `;

  const data = await graphql(mutation);
  const result = data?.pages?.restore;

  if (!result?.responseResult?.succeeded) {
    throw new Error(result?.responseResult?.message || 'Failed to revert page');
  }

  return { success: true, pageId, versionId };
}

export { GraphQLError };

export default {
  listPages,
  searchPages,
  getPage,
  createPage,
  updatePage,
  movePage,
  deletePage,
  listTags,
  listAssets,
  uploadAsset,
  deleteAsset,
  getHealth,
  getStats,
  getPageVersions,
  revertPage
};
