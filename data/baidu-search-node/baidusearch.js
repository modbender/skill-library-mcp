#!/usr/bin/env node

const axios = require('axios');
const cheerio = require('cheerio');
const { program } = require('commander');

const ABSTRACT_MAX_LENGTH = 300; // abstract max length

const user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
    'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/49.0.2623.108 Chrome/49.0.2623.108 Safari/537.36',
    'Mozilla/5.0 (Windows; U; Windows NT 5.1; pt-BR) AppleWebKit/533.3 (KHTML, like Gecko) QtWeb Internet Browser/3.7 http://www.QtWeb.net',
    'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36',
    'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/532.2 (KHTML, like Gecko) ChromePlus/4.0.222.3 Chrome/4.0.222.3 Safari/532.2',
    'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.4pre) Gecko/20070404 K-Ninja/2.1.3',
    'Mozilla/5.0 (Future Star Technologies Corp.; Star-Blade OS; x86_64; U; en-US) iNet Browser 4.7',
    'Mozilla/5.0 (Windows; U; Windows NT 6.1; rv:2.2) Gecko/20110201',
    'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.13) Gecko/20080414 Firefox/2.0.0.13 Pogo/2.0.0.13.6866'
];

// 请求头信息
const HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "Content-Type": "application/x-www-form-urlencoded",
    "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
    "Referer": "https://www.baidu.com/",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "zh-CN,zh;q=0.9"
};

const baidu_host_url = "https://www.baidu.com";
const baidu_search_url = "https://www.baidu.com/s?ie=utf-8&tn=baidu&wd=";

// 创建axios实例
const axiosInstance = axios.create({
    headers: HEADERS,
    timeout: 10000
});

/**
 * 通过关键字进行搜索
 * @param {string} keyword - 关键字
 * @param {number} num_results - 指定返回的结果个数
 * @param {number} debug - 调试模式，0-关闭，1-打开
 * @returns {Promise<Array>} 结果列表
 */
async function search(keyword, num_results = 10, debug = 0) {
    if (!keyword) {
        return null;
    }

    const list_result = [];
    let page = 1;

    // 起始搜索的url
    let next_url = baidu_search_url + encodeURIComponent(keyword);

    // 循环遍历每一页的搜索结果，并返回下一页的url
    while (list_result.length < num_results) {
        const [data, next] = await parse_html(next_url, list_result.length, debug);
        if (data && data.length > 0) {
            list_result.push(...data);
            if (debug) {
                console.log(`---searching[${keyword}], finish parsing page ${page}, results number=${data.length}: `);
                for (const d of data) {
                    console.log(JSON.stringify(d));
                }
            }
        }

        if (!next) {
            if (debug) {
                console.log("already search the last page");
            }
            break;
        }
        next_url = next;
        page++;
    }

    if (debug) {
        console.log(`\n---search [${keyword}] finished. total results number=${list_result.length}！`);
    }
    return list_result.slice(0, num_results);
}

/**
 * 解析处理结果
 * @param {string} url - 需要抓取的 url
 * @param {number} rank_start - 排名起始值
 * @param {number} debug - 调试模式，0-关闭，1-打开
 * @returns {Promise<Array>} 结果列表，下一页的url
 */
async function parse_html(url, rank_start = 0, debug = 0) {
    try {
        const res = await axiosInstance.get(url);
        const $ = cheerio.load(res.data);

        const list_data = [];
        const div_contents = $('#content_left');
        
        div_contents.children().each((index, div) => {
            const class_list = $(div).attr('class') ? $(div).attr('class').split(' ') : [];
            if (!class_list.length) {
                return;
            }

            if (!class_list.includes('c-container')) {
                return;
            }

            let title = '';
            let url = '';
            let abstract = '';

            try {
                // 遍历所有找到的结果，取得标题和概要内容
                if (class_list.includes('xpath-log')) {
                    if ($(div).find('h3').length > 0) {
                        title = $(div).find('h3').text().trim();
                        url = $(div).find('h3 a').attr('href') ? $(div).find('h3 a').attr('href').trim() : '';
                    } else {
                        const text = $(div).text().trim();
                        title = text.split('\n')[0];
                        if ($(div).find('a').length > 0) {
                            url = $(div).find('a').first().attr('href') ? $(div).find('a').first().attr('href').trim() : '';
                        }
                    }

                    if ($(div).find('.c-abstract').length > 0) {
                        abstract = $(div).find('.c-abstract').text().trim();
                    } else if ($(div).find('div').length > 0) {
                        abstract = $(div).find('div').first().text().trim();
                    } else {
                        const text = $(div).text().trim();
                        const parts = text.split('\n');
                        if (parts.length > 1) {
                            abstract = parts[1].trim();
                        }
                    }
                } else if (class_list.includes('result-op')) {
                    if ($(div).find('h3').length > 0) {
                        title = $(div).find('h3').text().trim();
                        url = $(div).find('h3 a').attr('href') ? $(div).find('h3 a').attr('href').trim() : '';
                    } else {
                        const text = $(div).text().trim();
                        title = text.split('\n')[0];
                        if ($(div).find('a').length > 0) {
                            url = $(div).find('a').first().attr('href') ? $(div).find('a').first().attr('href').trim() : '';
                        }
                    }
                    if ($(div).find('.c-abstract').length > 0) {
                        abstract = $(div).find('.c-abstract').text().trim();
                    } else if ($(div).find('div').length > 0) {
                        abstract = $(div).find('div').first().text().trim();
                    } else {
                        const text = $(div).text().trim();
                        const parts = text.split('\n');
                        if (parts.length > 1) {
                            abstract = parts[1].trim();
                        }
                    }
                } else {
                    const tpl = $(div).attr('tpl') || '';
                    if (tpl !== 'se_com_default') {
                        if (tpl === 'se_st_com_abstract') {
                            if ($(div).children().length >= 1) {
                                if ($(div).find('h3').length > 0) {
                                    title = $(div).find('h3').text().trim();
                                }
                                if ($(div).find('.c-abstract').length > 0) {
                                    abstract = $(div).find('.c-abstract').text().trim();
                                } else if ($(div).find('div').length > 0) {
                                    abstract = $(div).find('div').first().text().trim();
                                } else {
                                    abstract = $(div).text().trim();
                                }
                            }
                        } else {
                            if ($(div).children().length >= 2) {
                                if ($(div).find('h3').length > 0) {
                                    title = $(div).find('h3').text().trim();
                                    url = $(div).find('h3 a').attr('href') ? $(div).find('h3 a').attr('href').trim() : '';
                                } else {
                                    title = $(div).children().first().text().trim();
                                    if ($(div).find('h3 a').length > 0) {
                                        url = $(div).find('h3 a').attr('href') ? $(div).find('h3 a').attr('href').trim() : '';
                                    }
                                }
                                if ($(div).find('.c-abstract').length > 0) {
                                    abstract = $(div).find('.c-abstract').text().trim();
                                } else if ($(div).find('div').length > 0) {
                                    abstract = $(div).find('div').first().text().trim();
                                } else {
                                    abstract = $(div).text().trim();
                                }
                            }
                        }
                    } else {
                        if ($(div).find('h3').length > 0) {
                            title = $(div).find('h3').text().trim();
                            url = $(div).find('h3 a').attr('href') ? $(div).find('h3 a').attr('href').trim() : '';
                        } else {
                            title = $(div).children().first().text().trim();
                            if ($(div).find('h3 a').length > 0) {
                                url = $(div).find('h3 a').attr('href') ? $(div).find('h3 a').attr('href').trim() : '';
                            }
                        }
                        if ($(div).find('.c-abstract').length > 0) {
                            abstract = $(div).find('.c-abstract').text().trim();
                        } else if ($(div).find('div').length > 0) {
                            abstract = $(div).find('div').first().text().trim();
                        } else {
                            abstract = $(div).text().trim();
                        }
                    }
                }
            } catch (e) {
                if (debug) {
                    console.log(`catch exception duration parsing page html, e=${e}`);
                }
                return;
            }

            if (ABSTRACT_MAX_LENGTH && abstract.length > ABSTRACT_MAX_LENGTH) {
                abstract = abstract.substring(0, ABSTRACT_MAX_LENGTH);
            }

            rank_start++;
            list_data.push({ title, abstract, url, rank: rank_start });
        });

        // 找到下一页按钮
        const next_btn = $('a.n');

        // 已经是最后一页了，没有下一页了，此时只返回数据不再获取下一页的链接
        if (next_btn.length <= 0 || next_btn.last().text().includes('上一页')) {
            return [list_data, null];
        }

        const next_url = baidu_host_url + next_btn.last().attr('href');
        return [list_data, next_url];
    } catch (e) {
        if (debug) {
            console.log(`catch exception duration parsing page html, e：${e}`);
        }
        return [null, null];
    }
}

/**
 * 主程序入口，支持命令行带参执行或者手动输入关键字
 */
async function run() {
    const default_keyword = "Amazing Coder";
    let num_results = 10;
    let debug = 0;

    program
        .name('baidusearch')
        .description('百度搜索命令行工具')
        .version('1.0.0')
        .argument('[keyword]', '搜索关键字')
        .option('-n, --num <number>', '结果数量', parseInt, 10)
        .option('-d, --debug <number>', '调试模式，0-关闭，1-打开', parseInt, 0)
        .action((keyword, options) => {
            if (keyword) {
                runSearch(keyword, options.num, options.debug);
            } else {
                // 没有提供关键字，使用默认值
                runSearch(default_keyword, options.num, options.debug);
            }
        });

    program.parse(process.argv);
}

async function runSearch(keyword, num_results, debug) {
    console.log(`---start search: [${keyword}], expected number of results:[${num_results}].`);
    const results = await search(keyword, num_results, debug);

    if (Array.isArray(results)) {
        console.log(`search results：(total[${results.length}]items.)`);
        for (const res of results) {
            console.log(`${res.rank}. ${res.title}\n   ${res.abstract}\n   ${res.url}`);
        }
    } else {
        console.log(`start search: [${keyword}] failed.`);
    }
}

// 导出函数
module.exports = {
    search,
    parse_html
};

// 如果直接运行此文件，则执行主程序
if (require.main === module) {
    run();
}
