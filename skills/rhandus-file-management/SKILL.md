---
name: file-management
description: "Google Drive file management for OpenClaw using gog CLI. Upload, download, list, search, and organize files."
license: MIT
metadata:
  author: Rhandus Malpica
  company: Tiklick
  website: https://tiklick.com
  version: "1.0.0"
  openclaw:
    emoji: "📁"
    ui:
      color: "#EA4335"
      icon: "drive"
---

# File Management Skill

Gestión de archivos en Google Drive para OpenClaw. Sube, descarga, lista, busca y organiza archivos en la nube.

## Uso

Utiliza esta herramienta cuando necesites:
- Subir archivos del workspace a Google Drive
- Descargar archivos de Drive al workspace
- Listar y organizar archivos en Drive
- Buscar archivos específicos
- Compartir archivos con el equipo

## Características

- **Subida inteligente:** Detecta tipo de archivo y organiza automáticamente
- **Búsqueda en Drive:** Encuentra archivos por nombre o contenido
- **Sincronización selectiva:** Sincroniza solo lo necesario
- **Backup automático:** Opción de backup de archivos críticos

## Comandos

### `drive upload`
Sube archivos a Google Drive.

- **Argumentos:**
  - `file` (string, requerido): Ruta del archivo a subir
  - `--folder` (string, opcional): ID de carpeta en Drive (default: root)
  - `--name` (string, opcional): Nombre personalizado en Drive

### `drive download`
Descarga archivos desde Google Drive.

- **Argumentos:**
  - `fileId` (string, requerido): ID del archivo en Drive
  - `--output` (string, opcional): Ruta de destino (default: workspace)

### `drive list`
Lista archivos en Google Drive.

- **Argumentos:**
  - `--folder` (string, opcional): ID de carpeta (default: root)
  - `--limit` (number, opcional): Máximo resultados (default: 20)
  - `--query` (string, opcional): Filtro de búsqueda

### `drive search`
Busca archivos en Google Drive.

- **Argumentos:**
  - `query` (string, requerido): Términos de búsqueda
  - `--type` (string, opcional): Tipo de archivo (document,spreadsheet,presentation,etc.)

### `drive share`
Comparte un archivo.

- **Argumentos:**
  - `fileId` (string, requerido): ID del archivo
  - `--email` (string, requerido): Email para compartir
  - `--role` (string, opcional): Rol (reader,writer,commenter) (default: reader)

## Configuración

Requiere `gog` CLI configurado con acceso a Google Drive.
La cuenta por defecto es `TU_EMAIL_GOOGLE`.

## Ejemplos

```bash
# Subir un archivo a Drive
file upload /workspace/ventas-y-gastos/README.md --folder "appDataFolder"

# Listar archivos en Drive
file list --limit 10

# Buscar documentos
file search "reporte ventas 2026"

# Descargar un archivo
file download 1ABC123DEF456 --output /workspace/backups/

# Compartir un archivo
file share 1ABC123DEF456 --email equipo@tiklick.com --role writer
```