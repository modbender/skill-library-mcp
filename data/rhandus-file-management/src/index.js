import { exec } from 'child_process';
import { promisify } from 'util';
import fs from 'fs';
import path from 'path';

const execAsync = promisify(exec);

// Configuración
const DEFAULT_ACCOUNT = process.env.GOOGLE_ACCOUNT || 'TU_EMAIL_GOOGLE';
const WORKSPACE_ROOT = '/workspace';

/**
 * Sube un archivo a Google Drive
 */
export async function uploadFile(filePath, options = {}) {
  const {
    folder = 'root',
    customName = null,
    account = DEFAULT_ACCOUNT
  } = options;
  
  if (!fs.existsSync(filePath)) {
    throw new Error(`Archivo no encontrado: ${filePath}`);
  }
  
  const fileName = customName || path.basename(filePath);
  const mimeType = getMimeType(filePath);
  
  try {
    const command = `gog drive files upload --account ${account} --file "${filePath}" --name "${fileName}" --parents "${folder}" --mime-type "${mimeType}" --json`;
    const { stdout } = await execAsync(command, { shell: true });
    
    const result = JSON.parse(stdout);
    return {
      id: result.id,
      name: result.name,
      webViewLink: result.webViewLink,
      size: parseInt(result.size || '0'),
      mimeType: result.mimeType,
      status: 'uploaded'
    };
    
  } catch (error) {
    if (error.stderr && error.stderr.includes('insufficientPermissions')) {
      throw new Error('No hay permisos para Google Drive. Asegúrate que gog tiene acceso a Drive.');
    }
    throw new Error(`Error subiendo archivo: ${error.message}`);
  }
}

/**
 * Lista archivos en Google Drive
 */
export async function listFiles(options = {}) {
  const {
    folder = 'root',
    limit = 20,
    query = '',
    account = DEFAULT_ACCOUNT
  } = options;
  
  try {
    let command = `gog drive files list --account ${account} --max ${limit} --json`;
    
    if (folder !== 'root') {
      command += ` --parents "${folder}"`;
    }
    
    if (query) {
      command += ` --query "name contains '${query}'"`;
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
      parents: file.parents || []
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
    fileType = '',
    limit = 20,
    account = DEFAULT_ACCOUNT
  } = options;
  
  try {
    let searchQuery = `fullText contains '${query}' or name contains '${query}'`;
    
    if (fileType) {
      searchQuery += ` and mimeType contains '${fileType}'`;
    }
    
    const command = `gog drive files list --account ${account} --max ${limit} --query "${searchQuery}" --json`;
    const { stdout } = await execAsync(command, { shell: true });
    
    const files = JSON.parse(stdout);
    return files.map(file => ({
      id: file.id,
      name: file.name,
      mimeType: file.mimeType,
      snippet: file.description || '',
      webViewLink: file.webViewLink
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
    const infoCommand = `gog drive files get --account ${account} --file ${fileId} --json`;
    const { stdout: infoStdout } = await execAsync(infoCommand, { shell: true });
    const fileInfo = JSON.parse(infoStdout);
    
    const fileName = fileInfo.name;
    const destination = path.join(outputPath, fileName);
    
    // Descargar el archivo
    const downloadCommand = `gog drive files download --account ${account} --file ${fileId} --output "${destination}"`;
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

/**
 * Comparte un archivo
 */
export async function shareFile(fileId, options = {}) {
  const {
    email,
    role = 'reader',
    account = DEFAULT_ACCOUNT
  } = options;
  
  if (!email) {
    throw new Error('Email requerido para compartir');
  }
  
  try {
    const command = `gog drive permissions create --account ${account} --file ${fileId} --role ${role} --type user --email-address "${email}" --json`;
    const { stdout } = await execAsync(command, { shell: true });
    
    const result = JSON.parse(stdout);
    return {
      fileId,
      email,
      role,
      permissionId: result.id,
      status: 'shared'
    };
    
  } catch (error) {
    throw new Error(`Error compartiendo archivo: ${error.message}`);
  }
}

/**
 * Obtiene el MIME type de un archivo
 */
function getMimeType(filePath) {
  const ext = path.extname(filePath).toLowerCase();
  
  const mimeTypes = {
    '.txt': 'text/plain',
    '.md': 'text/markdown',
    '.json': 'application/json',
    '.js': 'application/javascript',
    '.py': 'text/x-python',
    '.php': 'application/x-httpd-php',
    '.html': 'text/html',
    '.css': 'text/css',
    '.pdf': 'application/pdf',
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.png': 'image/png',
    '.csv': 'text/csv',
    '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
  };
  
  return mimeTypes[ext] || 'application/octet-stream';
}

// CLI handler para pruebas
if (process.argv[2] === 'list') {
  const limit = process.argv[3] || 10;
  listFiles({ limit: parseInt(limit) })
    .then(files => {
      console.log(JSON.stringify(files, null, 2));
    })
    .catch(console.error);
}

if (process.argv[2] === 'search') {
  const query = process.argv.slice(3).join(' ');
  searchFiles(query, { limit: 10 })
    .then(results => {
      console.log(JSON.stringify(results, null, 2));
    })
    .catch(console.error);
}