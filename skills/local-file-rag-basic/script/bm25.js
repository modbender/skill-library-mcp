const fs = require('node:fs');
const path = require('node:path');

/**
 * 纯手写无依赖的高性能 BM25 检索内核
 */
class BM25SearchEngine {
    constructor(db) {
        this.db = db;
        // BM25 默认超参数
        this.k1 = 1.2;
        this.b = 0.4; // 调低 B 值，减弱对代码长块的长度惩罚
        this.avgDr = 0;
        this.totalDocs = 0; // 文档总数
        this.docLengths = {}; // id -> 分词数量
        this.df = {}; // term -> 出现过的文档数量
        this.tf = {}; // id -> { term -> freq }
        this.documents = {}; // id -> 真实文件结构对象，用于内存打分加速
    }

    /**
     * 高级分词器：支持多语言（中英文混合）、驼峰、蛇形切分
     * @param {string} text - 待分词源码或文档内容
     * @returns {string[]} - 词元数组
     */
    static tokenize(text) {
        if (!text) return [];

        // 1. 中文处理：在每个中文字符周围加空格，以便后续按空格切分（中文字符作为独立词元）
        let processedText = text.replace(/([\u4e00-\u9fa5])/g, ' $1 ');

        // 2. 清洗：保留字母、数字、下划线及中文字符，其余变空格
        const cleanText = processedText.replace(/[^\w\u4e00-\u9fa5]/g, ' ');

        // 3. 处理驼峰 (ComponentName) -> (Component Name)
        const splitText = cleanText.replace(/([a-z])([A-Z])/g, '$1 $2').replace(/_/g, ' ');

        // 4. 转小写并切分成数组
        const tokens = splitText.toLowerCase().split(/\s+/).filter(t => t.length > 0);

        // 5. N-gram 融合
        const ngrams = [];
        for (let i = 0; i < tokens.length - 1; i++) {
            ngrams.push(tokens[i] + tokens[i + 1]); // 中文连字 N-gram (如 "设" + "计" -> "设计")
        }
        return tokens.concat(ngrams);
    }

    /**
     * 构建索引层
     * 提取 SQLite 数据进行内存化 TF-IDF 运算，确保 100ms 检索红线
     */
    buildIndex() {
        const startTime = Date.now();

        // 重置状态
        this.totalDocs = 0;
        this.docLengths = {};
        this.df = {};
        this.tf = {};
        this.documents = {};
        let totalTermsCount = 0;

        // 获取全部有效的逻辑块（包含头部、签名及普通分分片）
        const chunks = this.db.prepare('SELECT * FROM chunks').all();
        this.totalDocs = chunks.length;

        for (const chunk of chunks) {
            const tokens = BM25SearchEngine.tokenize(chunk.content);
            const docId = chunk.id;

            this.documents[docId] = chunk;
            this.docLengths[docId] = tokens.length;
            totalTermsCount += tokens.length;

            this.tf[docId] = {};

            // 统计词频和文档频率
            const uniqueTerms = new Set();
            for (const token of tokens) {
                // TF
                this.tf[docId][token] = (this.tf[docId][token] || 0) + 1;
                // 用 Set 保证同一份文件同一词语只计入一遍 DF 计数
                uniqueTerms.add(token);
            }

            for (const term of uniqueTerms) {
                this.df[term] = (this.df[term] || 0) + 1;
            }
        }

        // 计算平均文件长度
        this.avgDr = this.totalDocs > 0 ? totalTermsCount / this.totalDocs : 0;
    }

    /**
     * 核心评分算法 (计算逆文档文档频率 IDF 并与 TF 结合)
     */
    calculateBM25Score(queryTokens, docId) {
        let score = 0;
        const docLength = this.docLengths[docId] || 0;

        // 空块防御
        if (docLength === 0) return 0;

        const tfDoc = this.tf[docId];

        for (const token of queryTokens) {
            if (!this.df[token]) continue; // 词库里根本没有的词不参与评分

            // 1. IDF 惩罚值（逆总文档频率），用平滑函数避免负数或者极大值
            const idf = Math.log(1 + (this.totalDocs - this.df[token] + 0.5) / (this.df[token] + 0.5));

            // 2. TF 词频
            const baseTf = tfDoc[token] || 0;

            if (baseTf > 0) {
                // 3. 将两者融合，做文档长度惩罚 (过长的文段中重复提及的权重更低)
                // 优化：增加语义密度权重，长词的分量通常比单字更重
                const termWeight = token.length > 1 ? 2.0 : 0.5;

                const numerator = baseTf * (this.k1 + 1) * termWeight;
                const denominator = baseTf + this.k1 * (1 - this.b + this.b * (docLength / this.avgDr));
                score += idf * (numerator / denominator);
            }
        }

        // 4. 结构权重：如果是签名或头部，给予显著加成
        if (this.documents[docId].is_signature) score *= 5.0;
        else if (this.documents[docId].is_header) score *= 3.0;

        return score;
    }

    /**
     * 高性能查询接口
     * @param {string} query - 大模型或是用户的结构化提问
     * @param {number} topK - 限定取出的分片数目
     * @returns {Array} - 按分值倒序排序返回最匹配的代码分片
     */
    search(query, topK = 5) {
        const queryTokens = BM25SearchEngine.tokenize(query);
        if (queryTokens.length === 0) return [];

        const startTime = Date.now();
        const results = [];

        for (let docId in this.documents) {
            const score = this.calculateBM25Score(queryTokens, docId);
            if (score > 0) {
                results.push({
                    score: score,
                    chunk: this.documents[docId]
                });
            }
        }

        // 依据评分倒序输出并裁剪
        results.sort((a, b) => b.score - a.score);
        return results.slice(0, topK);
    }
}

module.exports = { BM25SearchEngine };
