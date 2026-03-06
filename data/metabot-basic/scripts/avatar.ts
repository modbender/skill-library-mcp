#!/usr/bin/env node

/**
 * 头像处理模块 - Node.js 环境
 * 支持从用户拖入对话框的文件路径读取图片，或从 static/avatar 读取，转为 base64 供链上创建
 */

import * as fs from 'fs'
import * as path from 'path'

const AVATAR_DIR = path.join(__dirname, '..', 'static', 'avatar')
const IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.avif']
const MAX_AVATAR_SIZE_BYTES = 1024 * 1024 // 1MB

export interface AttachmentItem {
  fileName: string
  fileType: string
  data: string
  encrypt: 0 | 1
  size: number
  url: string
}

/**
 * 从 static/avatar 获取第一个图片文件路径
 */
export function getAvatarImagePath(): string | null {
  if (!fs.existsSync(AVATAR_DIR)) {
    return null
  }
  const files = fs.readdirSync(AVATAR_DIR)
  for (const f of files) {
    const ext = path.extname(f).toLowerCase()
    if (IMAGE_EXTENSIONS.includes(ext)) {
      return path.join(AVATAR_DIR, f)
    }
  }
  return null
}

/**
 * 检查是否有头像文件（可指定文件名）
 */
export function hasAvatarFile(filename?: string): boolean {
  if (filename) {
    const p = path.join(AVATAR_DIR, filename)
    return fs.existsSync(p) && IMAGE_EXTENSIONS.includes(path.extname(filename).toLowerCase())
  }
  return getAvatarImagePath() !== null
}

/**
 * 根据文件名获取头像图片路径（文件名需在 static/avatar 下）
 */
export function getAvatarImagePathByFilename(filename: string): string | null {
  const p = path.join(AVATAR_DIR, filename)
  if (fs.existsSync(p) && IMAGE_EXTENSIONS.includes(path.extname(filename).toLowerCase())) {
    return p
  }
  return null
}

/**
 * 将图片文件转为 base64 字符串（Node 环境，与浏览器 fileToBase64/readAsDataURL 效果一致，返回纯 base64 部分）
 * 浏览器等价: reader.readAsDataURL(file) -> result.split(',')[1]
 */
export function fileToBase64(filePath: string): Promise<string> {
  return new Promise((resolve, reject) => {
    fs.readFile(filePath, (err, buffer) => {
      if (err) {
        reject(err)
        return
      }
      const base64 = buffer.toString('base64')
      resolve(base64)
    })
  })
}

/**
 * 将图片文件转为 AttachmentItem 格式（不压缩，data 为 base64）
 */
export async function imageFileToAttachmentItem(filePath: string): Promise<AttachmentItem> {
  const data = await fileToBase64(filePath)
  const ext = path.extname(filePath).toLowerCase()
  const stat = fs.statSync(filePath)

  const fileType =
    ext === '.png' ? 'image/png' : ext === '.gif' ? 'image/gif' : ext === '.webp' ? 'image/webp' : ext === '.avif' ? 'image/avif' : 'image/jpeg'

  return {
    data,
    fileName: path.basename(filePath),
    fileType,
    encrypt: 0,
    size: stat.size,
    url: `file://${filePath}`,
  }
}

/** 头像文件超过 1MB 时的提示信息 */
export const AVATAR_SIZE_EXCEEDED_MSG =
  '上传头像文件超过1 MB，请使用小于1MB图片文件设置头像'

/**
 * 判断是否为有效的头像图片路径（支持 jpg/png/gif/webp/avif）
 */
export function isValidAvatarFilePath(filePath: string): boolean {
  if (!filePath || !fs.existsSync(filePath)) return false
  const ext = path.extname(filePath).toLowerCase()
  return IMAGE_EXTENSIONS.includes(ext)
}

/**
 * 从任意文件路径加载头像（供用户拖入对话框的文件）
 * @param filePath 用户提供的完整文件路径（如拖入对话框的图片路径）
 * 若文件超过 1MB 则抛出错误（消息见 AVATAR_SIZE_EXCEEDED_MSG）
 */
export async function loadAvatarFromFilePath(filePath: string): Promise<{ avatar: string; contentType: string }> {
  const resolved = path.resolve(filePath)
  if (!isValidAvatarFilePath(resolved)) {
    throw new Error(`无效的头像文件路径或格式: ${filePath}（支持 jpg/png/gif/webp/avif）`)
  }
  const stat = fs.statSync(resolved)
  if (stat.size > MAX_AVATAR_SIZE_BYTES) {
    throw new Error(AVATAR_SIZE_EXCEEDED_MSG)
  }
  const attachment = await imageFileToAttachmentItem(resolved)
  const contentType =
    attachment.fileType === 'image/png'
      ? 'image/png;binary'
      : attachment.fileType === 'image/gif'
        ? 'image/gif;binary'
        : attachment.fileType === 'image/webp'
          ? 'image/webp;binary'
          : attachment.fileType === 'image/avif'
            ? 'image/avif;binary'
            : 'image/jpeg;binary'
  return { avatar: attachment.data, contentType }
}

/**
 * 从 static/avatar 读取图片并转为 base64（供 /info/avatar 上链）
 * @param filename 可选，指定 static/avatar 下的文件名（如 "images (2).jpeg"），不传则取目录下第一个图片
 * 若无可用的头像文件则返回 null
 * 若文件超过 1MB 则抛出错误（消息见 AVATAR_SIZE_EXCEEDED_MSG）
 */
export async function loadAvatarAsBase64(filename?: string): Promise<{ avatar: string; contentType: string } | null> {
  const imgPath = filename ? getAvatarImagePathByFilename(filename) : getAvatarImagePath()
  if (!imgPath) return null

  const stat = fs.statSync(imgPath)
  if (stat.size > MAX_AVATAR_SIZE_BYTES) {
    throw new Error(AVATAR_SIZE_EXCEEDED_MSG)
  }

  const attachment = await imageFileToAttachmentItem(imgPath)
  const avatar = attachment.data
  const contentType =
    attachment.fileType === 'image/png'
      ? 'image/png;binary'
      : attachment.fileType === 'image/gif'
        ? 'image/gif;binary'
        : attachment.fileType === 'image/webp'
          ? 'image/webp;binary'
          : attachment.fileType === 'image/avif'
            ? 'image/avif;binary'
            : 'image/jpeg;binary'
  return { avatar, contentType }
}
