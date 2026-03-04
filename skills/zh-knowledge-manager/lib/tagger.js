/**
 * 中文自动标签推荐
 * 使用 @node-rs/jieba 分词 + TF-IDF 关键词提取
 * 纯本地计算，零 API 成本
 */
const { normalizeTags } = require('./synonyms');

let jiebaInstance = null;
let jiebaLoaded = false;

function ensureJieba() {
    if (jiebaLoaded) return !!jiebaInstance;
    try {
        const { Jieba } = require('@node-rs/jieba');
        jiebaInstance = new Jieba();
        jiebaLoaded = true;
        return true;
    } catch {
        jiebaLoaded = true;
        console.warn('[tagger] @node-rs/jieba 未安装，自动标签功能降级为正则提取。运行 npm install @node-rs/jieba');
        return false;
    }
}

const STOP_WORDS = new Set([
    '的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一',
    '一个', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着',
    '没有', '看', '好', '自己', '这', '他', '她', '它', '们', '那',
    '被', '从', '对', '把', '与', '还', '但', '但是', '然后', '所以',
    '因为', '如果', '虽然', '已经', '可以', '这个', '那个', '什么',
    '怎么', '为什么', '多少', '哪', '吧', '呢', '吗', '啊', '哦',
    '嗯', '呀', '哈', '嘿', '嗨', '用', '做', '让', '给', '比',
    '过', '下', '起', '来', '去', '出', '进', '回', '开', '关',
    '使用', '进行', '通过', '需要', '可能', '应该', '不是', '这样',
    '那样', '之后', '之前', '时候', '问题', '方法', '情况', '比较',
]);

const MIN_WORD_LENGTH = 2;

/**
 * 从文本中提取关键词并生成标签建议
 * @param {string} text - 输入文本
 * @param {number} [topN=5] - 返回前 N 个关键词
 * @returns {string[]} 推荐标签列表
 */
function suggestTags(text, topN = 5) {
    if (!ensureJieba()) {
        return fallbackExtract(text, topN);
    }

    const words = jiebaInstance.cutForSearch(text, true);
    return extractTopKeywords(words, topN);
}

function extractTopKeywords(words, topN) {
    const freq = new Map();
    const totalWords = words.length || 1;

    for (const word of words) {
        const w = word.trim();
        if (w.length < MIN_WORD_LENGTH) continue;
        if (STOP_WORDS.has(w)) continue;
        if (/^[\s\d.,;:!?，。；：！？、]+$/.test(w)) continue;
        if (/[时候里面上下中前后]$/.test(w) && w.length <= 3) continue;
        freq.set(w, (freq.get(w) || 0) + 1);
    }

    return Array.from(freq.entries())
        .map(([word, count]) => ({
            word,
            score: (count / totalWords) * Math.log(1 + word.length),
        }))
        .sort((a, b) => b.score - a.score)
        .slice(0, topN)
        .map(item => item.word);
}

/**
 * 降级提取：无 jieba 时用简单正则提取中文词组和英文单词
 */
function fallbackExtract(text, topN) {
    const chineseWords = text.match(/[\u4e00-\u9fff]{2,8}/g) || [];
    const englishWords = text.match(/[A-Za-z][\w-]{2,}/g) || [];
    const allWords = [...chineseWords, ...englishWords];
    return extractTopKeywords(allWords, topN);
}

/**
 * 为条目补充自动标签
 * @param {object} entry - 解析后的日志条目
 * @param {object} config - 配置
 * @returns {string[]} 合并后的标签列表（去重 + 归一化）
 */
function autoTag(entry, config) {
    const topN = config.autoTag?.topN || 5;
    const fullText = `${entry.title} ${entry.body}`;
    const suggested = suggestTags(fullText, topN);

    const existingLower = new Set(entry.tags.map(t => t.toLowerCase()));
    const filtered = suggested.filter(tag => {
        const tl = tag.toLowerCase();
        if (existingLower.has(tl)) return false;
        for (const existing of entry.tags) {
            if (existing.includes(tag) || tag.includes(existing)) return false;
        }
        return true;
    });

    const merged = [...entry.tags, ...filtered];
    return normalizeTags(merged);
}

module.exports = { suggestTags, autoTag, fallbackExtract };
