import { exec } from 'child_process';
import { promisify } from 'util';
import fs from 'fs';
import path from 'path';

const execAsync = promisify(exec);

// Configuración
const DEFAULT_ACCOUNT = process.env.GOOGLE_ACCOUNT || 'TU_EMAIL_GOOGLE';
const WORKSPACE_ROOT = '/workspace';

/**
 * Lista archivos en Google Drive
 */
export async function listFiles(options = {}) {
  const {
    folder = 'root',
    limit = 20,
    account = DEFAULT_ACCOUNT
  } = options;
  
  try {
    let command = `gog drive ls --account ${account} --max ${limit} --json`;
    
    if (folder !== 'root') {
      command += ` --folder "${folder}"`;
    }
    
    const { stdout } = await execAsync(command, { shell: true });
    const files = JSON.parse(stdout);
    
    return files.map(file => ({
      id: file.id,
      name: file.name,
      mimeType: file.mimeType,
      size: parseInt(file.size || '0'),
      createdTime: file.createdTime,
      modifiedTime: file.modifiedTime,
      webViewLink: file.webViewLink,
      isFolder: file.mimeType === 'application/vnd.google-apps.folder'
    }));
    
  } catch (error) {
    throw new Error(`Error listando archivos: ${error.message}`);
  }
}

/**
 * Busca archivos en Google Drive
 */
export async function searchFiles(query, options = {}) {
  const {
    limit = 20,
    account = DEFAULT_ACCOUNT
  } = options;
  
  try {
    const command = `gog drive search "${query}" --account ${account} --max ${limit} --json`;
    const { stdout } = await execAsync(command, { shell: true });
    
    const files = JSON.parse(stdout);
    return files.map(file => ({
      id: file.id,
      name: file.name,
      mimeType: file.mimeType,
      snippet: file.snippet || '',
      webViewLink: file.webViewLink,
      isFolder: file.mimeType === 'application/vnd.google-apps.folder'
    }));
    
  } catch (error) {
    throw new Error(`Error buscando archivos: ${error.message}`);
  }
}

/**
 * Descarga un archivo desde Google Drive
 */
export async function downloadFile(fileId, options = {}) {
  const {
    outputPath = WORKSPACE_ROOT,
    account = DEFAULT_ACCOUNT
  } = options;
  
  try {
    // Primero obtener información del archivo
    const infoCommand = `gog drive get ${fileId} --account ${account} --json`;
    const { stdout: infoStdout } = await execAsync(infoCommand, { shell: true });
    const fileInfo = JSON.parse(infoStdout);
    
    const fileName = fileInfo.name;
    const destination = path.join(outputPath, fileName);
    
    // Descargar el archivo
    const downloadCommand = `gog drive get ${fileId} --account ${account} --output "${destination}"`;
    await execAsync(downloadCommand, { shell: true });
    
    return {
      id: fileId,
      name: fileName,
      localPath: destination,
      size: parseInt(fileInfo.size || '0'),
      mimeType: fileInfo.mimeType,
      status: 'downloaded'
    };
    
  } catch (error) {
    throw new Error(`Error descargando archivo: ${error.message}`);
  }
}

// CLI handler para pruebas
if (process.argv[2] === 'list') {
  const limit = process.argv[3] || 5;
  listFiles({ limit: parseInt(limit) })
    .then(files => {
      console.log(`📁 Archivos en Drive (${files.length}):`);
      files.forEach((file, i) => {
        console.log(`${i + 1}. ${file.name} ${file.isFolder ? '(📁)' : ''}`);
      });
    })
    .catch(console.error);
}

if (process.argv[2] === 'search') {
  const query = process.argv.slice(3).join(' ');
  searchFiles(query, { limit: 10 })
    .then(results => {
      console.log(`🔍 Resultados para "${query}" (${results.length}):`);
      results.forEach((result, i) => {
        console.log(`${i + 1}. ${result.name}`);
        if (result.snippet) console.log(`   ${result.snippet.substring(0, 100)}...`);
      });
    })
    .catch(console.error);
}