#!/usr/bin/env node
// AiCoin Newsflash (OpenData) CLI
import { apiGet, cli } from '../lib/aicoin-api.mjs';

cli({
  search: ({ word, page, size } = {}) => {
    const p = { word };
    if (page) p.page = page;
    if (size) p.size = size;
    return apiGet('/api/upgrade/v2/content/newsflash/search', p);
  },
  list: ({ last_id, pagesize, tab, only_important, lan, platform_show, date_mode, jump_to_date, start_date, end_date } = {}) => {
    const p = {};
    if (last_id) p.last_id = last_id;
    if (pagesize) p.pagesize = pagesize;
    if (tab) p.tab = tab;
    if (only_important) p.only_important = only_important;
    if (lan) p.lan = lan;
    if (platform_show) p.platform_show = platform_show;
    if (date_mode) p.date_mode = date_mode;
    if (jump_to_date) p.jump_to_date = jump_to_date;
    if (start_date) p.start_date = start_date;
    if (end_date) p.end_date = end_date;
    return apiGet('/api/upgrade/v2/content/newsflash/list', p);
  },
  detail: ({ flash_id } = {}) => {
    return apiGet('/api/upgrade/v2/content/newsflash/detail', { flash_id });
  },
});
