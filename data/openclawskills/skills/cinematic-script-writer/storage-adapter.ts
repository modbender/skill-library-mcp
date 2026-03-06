/**
 * Storage Adapter System
 * Supports Google Drive, Local Filesystem, and other storage backends
 */

export interface StorageConfig {
  provider: 'google-drive' | 'local' | 'dropbox' | 'onedrive' | 'custom';
  credentials?: {
    accessToken?: string;
    refreshToken?: string;
    clientId?: string;
    clientSecret?: string;
    apiKey?: string;
  };
  basePath?: string;
  folderId?: string;  // For Google Drive parent folder
  options?: Record<string, any>;
}

export interface StorageFile {
  name: string;
  content: string;
  mimeType: string;
  path?: string;
  metadata?: Record<string, any>;
}

export interface StorageFolder {
  id: string;
  name: string;
  path: string;
  webViewLink?: string;
  created?: boolean;
}

export interface StorageAdapter {
  connect(config: StorageConfig): Promise<boolean>;
  disconnect(): Promise<void>;
  createFolder(name: string, parentPath?: string): Promise<StorageFolder>;
  createFile(folderId: string, file: StorageFile): Promise<{ id: string; webViewLink?: string }>;
  listFiles(folderId: string): Promise<StorageFile[]>;
  deleteFile(fileId: string): Promise<boolean>;
  getFile(fileId: string): Promise<StorageFile | null>;
  isConnected(): boolean;
}

// ============================================================================
// Google Drive Storage Adapter
// ============================================================================

export class GoogleDriveAdapter implements StorageAdapter {
  private config: StorageConfig | null = null;
  private connected = false;
  private accessToken: string | null = null;
  private baseUrl = 'https://www.googleapis.com/drive/v3';
  private uploadUrl = 'https://www.googleapis.com/upload/drive/v3';

  async connect(config: StorageConfig): Promise<boolean> {
    if (config.provider !== 'google-drive') {
      throw new Error('Invalid provider for GoogleDriveAdapter');
    }

    this.config = config;
    
    // Check if we have an access token
    if (config.credentials?.accessToken) {
      this.accessToken = config.credentials.accessToken;
      
      // Test connection
      try {
        const response = await fetch(`${this.baseUrl}/about?fields=user`, {
          headers: {
            'Authorization': `Bearer ${this.accessToken}`
          }
        });
        
        if (response.ok) {
          this.connected = true;
          return true;
        }
      } catch (error) {
        console.error('Failed to connect to Google Drive:', error);
      }
    }
    
    return false;
  }

  async disconnect(): Promise<void> {
    this.connected = false;
    this.accessToken = null;
    this.config = null;
  }

  isConnected(): boolean {
    return this.connected;
  }

  async createFolder(name: string, parentId?: string): Promise<StorageFolder> {
    if (!this.connected || !this.accessToken) {
      throw new Error('Not connected to Google Drive');
    }

    const metadata = {
      name: name,
      mimeType: 'application/vnd.google-apps.folder',
      parents: parentId ? [parentId] : undefined
    };

    const response = await fetch(`${this.baseUrl}/files`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.accessToken}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(metadata)
    });

    if (!response.ok) {
      const error = await response.text();
      throw new Error(`Failed to create folder: ${error}`);
    }

    const result = await response.json() as { id: string; webViewLink?: string };
    
    return {
      id: result.id,
      name: name,
      path: `/${name}`,
      webViewLink: result.webViewLink || `https://drive.google.com/drive/folders/${result.id}`,
      created: true
    };
  }

  async createFile(folderId: string, file: StorageFile): Promise<{ id: string; webViewLink?: string }> {
    if (!this.connected || !this.accessToken) {
      throw new Error('Not connected to Google Drive');
    }

    // Create multipart request
    const boundary = '-------314159265358979323846';
    const delimiter = "\r\n--" + boundary + "\r\n";
    const close_delim = "\r\n--" + boundary + "--";

    const metadata = {
      name: file.name,
      mimeType: file.mimeType,
      parents: [folderId]
    };

    const multipartRequestBody =
      delimiter +
      'Content-Type: application/json; charset=UTF-8\r\n\r\n' +
      JSON.stringify(metadata) +
      delimiter +
      `Content-Type: ${file.mimeType}\r\n\r\n` +
      file.content +
      close_delim;

    const response = await fetch(`${this.uploadUrl}/files?uploadType=multipart`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.accessToken}`,
        'Content-Type': `multipart/related; boundary="${boundary}"`
      },
      body: multipartRequestBody
    });

    if (!response.ok) {
      const error = await response.text();
      throw new Error(`Failed to create file: ${error}`);
    }

    const result = await response.json() as { id: string; webViewLink?: string };
    
    return {
      id: result.id,
      webViewLink: result.webViewLink || `https://drive.google.com/file/d/${result.id}/view`
    };
  }

  async listFiles(folderId: string): Promise<StorageFile[]> {
    if (!this.connected || !this.accessToken) {
      throw new Error('Not connected to Google Drive');
    }

    const response = await fetch(
      `${this.baseUrl}/files?q='${folderId}'+in+parents&fields=files(id,name,mimeType)`,
      {
        headers: {
          'Authorization': `Bearer ${this.accessToken}`
        }
      }
    );

    if (!response.ok) {
      throw new Error('Failed to list files');
    }

    const result = await response.json() as { files?: StorageFile[] };
    return result.files || [];
  }

  async deleteFile(fileId: string): Promise<boolean> {
    if (!this.connected || !this.accessToken) {
      throw new Error('Not connected to Google Drive');
    }

    const response = await fetch(`${this.baseUrl}/files/${fileId}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${this.accessToken}`
      }
    });

    return response.ok;
  }

  async getFile(fileId: string): Promise<StorageFile | null> {
    if (!this.connected || !this.accessToken) {
      throw new Error('Not connected to Google Drive');
    }

    // Get file metadata
    const metaResponse = await fetch(
      `${this.baseUrl}/files/${fileId}?fields=name,mimeType`,
      {
        headers: {
          'Authorization': `Bearer ${this.accessToken}`
        }
      }
    );

    if (!metaResponse.ok) {
      return null;
    }

    const metadata = await metaResponse.json() as { name: string; mimeType: string };

    // Download content
    const contentResponse = await fetch(
      `${this.baseUrl}/files/${fileId}/export?mimeType=text/plain`,
      {
        headers: {
          'Authorization': `Bearer ${this.accessToken}`
        }
      }
    );

    const content = contentResponse.ok ? await contentResponse.text() : '';

    return {
      name: metadata.name,
      content: content,
      mimeType: metadata.mimeType
    };
  }

  // Generate OAuth URL for user authorization
  static getAuthUrl(clientId: string, redirectUri: string, state?: string): string {
    const scope = encodeURIComponent('https://www.googleapis.com/auth/drive.file');
    const url = `https://accounts.google.com/o/oauth2/v2/auth?` +
      `client_id=${clientId}&` +
      `redirect_uri=${encodeURIComponent(redirectUri)}&` +
      `scope=${scope}&` +
      `response_type=code&` +
      `access_type=offline&` +
      `prompt=consent` +
      (state ? `&state=${encodeURIComponent(state)}` : '');
    return url;
  }

  // Exchange auth code for tokens
  static async exchangeCode(
    code: string,
    clientId: string,
    clientSecret: string,
    redirectUri: string
  ): Promise<{ access_token: string; refresh_token?: string }> {
    const response = await fetch('https://oauth2.googleapis.com/token', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      },
      body: new URLSearchParams({
        code,
        client_id: clientId,
        client_secret: clientSecret,
        redirect_uri: redirectUri,
        grant_type: 'authorization_code'
      })
    });

    if (!response.ok) {
      const error = await response.text();
      throw new Error(`Token exchange failed: ${error}`);
    }

    return await response.json() as { access_token: string; refresh_token?: string };
  }
}

// ============================================================================
// Local FileSystem Adapter
// ============================================================================

export class LocalStorageAdapter implements StorageAdapter {
  private config: StorageConfig | null = null;
  private connected = false;

  async connect(config: StorageConfig): Promise<boolean> {
    if (config.provider !== 'local') {
      throw new Error('Invalid provider for LocalStorageAdapter');
    }

    this.config = config;
    this.connected = true;
    return true;
  }

  async disconnect(): Promise<void> {
    this.connected = false;
    this.config = null;
  }

  isConnected(): boolean {
    return this.connected;
  }

  async createFolder(name: string, parentPath?: string): Promise<StorageFolder> {
    // In browser environment, this would use File System Access API
    // For now, return a mock folder
    return {
      id: `local-${Date.now()}`,
      name: name,
      path: parentPath ? `${parentPath}/${name}` : `/${name}`,
      created: true
    };
  }

  async createFile(folderId: string, file: StorageFile): Promise<{ id: string; webViewLink?: string }> {
    // In browser, trigger download
    // Note: This would need DOM APIs available in browser environment
    // For Node.js/OpenClaw runtime, this is a placeholder
    console.log(`[LocalStorage] Would download: ${file.name}`);

    return {
      id: `local-${Date.now()}`,
      webViewLink: undefined
    };
  }

  async listFiles(folderId: string): Promise<StorageFile[]> {
    return [];
  }

  async deleteFile(fileId: string): Promise<boolean> {
    return true;
  }

  async getFile(fileId: string): Promise<StorageFile | null> {
    return null;
  }
}

// ============================================================================
// Storage Factory
// ============================================================================

export class StorageFactory {
  static createAdapter(provider: string): StorageAdapter {
    switch (provider) {
      case 'google-drive':
        return new GoogleDriveAdapter();
      case 'local':
        return new LocalStorageAdapter();
      default:
        throw new Error(`Unknown storage provider: ${provider}`);
    }
  }
}

export default {
  GoogleDriveAdapter,
  LocalStorageAdapter,
  StorageFactory
};
