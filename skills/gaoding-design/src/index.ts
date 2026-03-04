/**
 * gaoding-design — 稿定设计对话式设计工具
 *
 * 每个 Tool 封装一个独立能力，由 OpenClaw Agent (LLM) 根据用户意图选择调用。
 */

// Tools
export * as searchTemplates from './tools/search-templates.js';
export * as selectTemplate from './tools/select-template.js';
export * as previewDesign from './tools/preview-design.js';
export * as editText from './tools/edit-text.js';
export * as exportDesign from './tools/export-design.js';

// Session management
export { getSession, clearSession } from './session/state.js';

// Types re-export
export type { TemplateInfo } from './browser/search.js';
export type { TextReplacement } from './browser/edit.js';
export type { ExportFormat } from './browser/export.js';
