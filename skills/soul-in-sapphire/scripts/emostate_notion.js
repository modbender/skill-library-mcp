#!/usr/bin/env node
import { httpJson } from './ltm_common.js';

function nowIso() { return new Date().toISOString(); }
const _rt = s => ({ rich_text: s ? [{ type: 'text', text: { content: String(s) } }] : [] });
const _title = s => ({ title: [{ type: 'text', text: { content: String(s) } }] });
const _select = n => ({ select: n ? { name: String(n) } : null });
const _multi = arr => ({ multi_select: (arr || []).filter(Boolean).map(n => ({ name: String(n) })) });
const _date = s => ({ date: s ? { start: String(s) } : null });
const _num = x => ({ number: (x === null || x === undefined || x === '') ? null : Number(x) });
const _url = u => ({ url: u ? String(u) : null });

function clamp010(x) { return Math.max(0, Math.min(10, Number(x))); }

function queryRecent(dsId, pageSize = 10) {
  const body = { page_size: pageSize, sorts: [{ timestamp: 'created_time', direction: 'descending' }] };
  const res = httpJson('POST', `/data_sources/${dsId}/query`, body);
  return res?.results || [];
}

function textOf(prop) {
  if (!prop) return '';
  const t = prop.type;
  if (t === 'title' || t === 'rich_text') return (prop[t] || []).map(x => x?.plain_text || '').join('').trim();
  if (t === 'select') return prop.select?.name || '';
  if (t === 'multi_select') return (prop.multi_select || []).map(x => x?.name).filter(Boolean);
  if (t === 'number') return prop.number;
  if (t === 'date') return prop.date?.start || '';
  if (t === 'url') return prop.url || '';
  if (t === 'relation') return (prop.relation || []).map(x => x?.id).filter(Boolean);
  return '';
}

function createPage(databaseId, properties) {
  return httpJson('POST', '/pages', { parent: { database_id: databaseId }, properties });
}
function patchPage(pageId, properties = undefined, archived = undefined) {
  const b = {};
  if (properties !== undefined) b.properties = properties;
  if (archived !== undefined) b.archived = !!archived;
  return httpJson('PATCH', `/pages/${pageId}`, b);
}

function buildEventProps(obj = {}) {
  const when = obj.when || nowIso();
  return {
    Name: _title(obj.title || obj.Name || '(event)'),
    when: _date(when),
    importance: _select(obj.importance != null ? String(obj.importance) : null),
    trigger: _select(obj.trigger),
    context: _rt(obj.context || ''),
    source: _select(obj.source || 'other'),
    link: _url(obj.link),
    uncertainty: _num(obj.uncertainty),
    control: _num(obj.control),
  };
}

function buildEmotionProps(obj = {}, eventPageId = null) {
  const props = {
    Name: _title(obj.title || `${obj.axis}=${obj.level}`),
    axis: _select(obj.axis),
    level: _num(obj.level),
    comment: _rt(obj.comment || ''),
    weight: _num(obj.weight),
    body_signal: _multi(obj.body_signal || []),
    need: _select(obj.need),
    coping: _select(obj.coping),
  };
  if (eventPageId) props.event = { relation: [{ id: eventPageId }] };
  return props;
}

function buildStateProps(obj = {}, eventPageId = null) {
  const when = obj.when || nowIso();
  const props = {
    Name: _title(obj.title || `state@${when}`),
    when: _date(when),
    state_json: _rt(JSON.stringify(obj.state_json || {})),
    reason: _rt(obj.reason || ''),
    source: _select(obj.source || 'manual'),
    mood_label: _select(obj.mood_label),
    intent: _select(obj.intent),
    need_stack: _select(obj.need_stack),
    need_level: _num(obj.need_level),
    avoid: _multi(obj.avoid || []),
  };
  if (eventPageId) props.event = { relation: [{ id: eventPageId }] };
  return props;
}

export { nowIso, clamp010, queryRecent, textOf, createPage, patchPage, buildEventProps, buildEmotionProps, buildStateProps };
