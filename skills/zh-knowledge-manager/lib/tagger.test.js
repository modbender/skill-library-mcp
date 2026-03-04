const { describe, it } = require('node:test');
const assert = require('node:assert/strict');
const { suggestTags, autoTag, fallbackExtract } = require('./tagger');

describe('suggestTags', () => {
    it('从中文文本提取标签', () => {
        const tags = suggestTags('使用 pandas 读取大数据集时需要设置 chunksize 避免内存溢出', 5);
        assert.ok(tags.length > 0);
        assert.ok(tags.length <= 5);
    });

    it('从英文技术文本提取标签', () => {
        const tags = suggestTags('Docker container deployment with Kubernetes orchestration on AWS EC2', 5);
        assert.ok(tags.length > 0);
    });

    it('混合中英文文本', () => {
        const tags = suggestTags('使用 Docker 部署 Python Flask 服务到生产环境服务器', 3);
        assert.ok(tags.length > 0);
        assert.ok(tags.length <= 3);
    });

    it('topN 参数限制结果数量', () => {
        const tags3 = suggestTags('多个关键词的文本 数据库 缓存 消息队列 容器 部署 监控 报表', 3);
        assert.ok(tags3.length <= 3);
    });

    it('空文本返回空数组', () => {
        const tags = suggestTags('', 5);
        assert.equal(tags.length, 0);
    });

    it('纯停用词文本返回空或极少结果', () => {
        const tags = suggestTags('的了在是我有和就不人都一上', 5);
        assert.ok(tags.length <= 1);
    });

    it('短文本也能提取', () => {
        const tags = suggestTags('Nginx 反向代理', 3);
        assert.ok(tags.length > 0);
    });
});

describe('fallbackExtract', () => {
    it('无 jieba 时降级正则提取中文词', () => {
        const tags = fallbackExtract('数据库连接池配置优化', 3);
        assert.ok(tags.length > 0);
    });

    it('提取英文单词', () => {
        const tags = fallbackExtract('Deploy Docker containers with Kubernetes', 3);
        assert.ok(tags.some(t => /[A-Za-z]/.test(t)));
    });
});

describe('autoTag', () => {
    it('补充标签到已有标签列表', () => {
        const entry = {
            title: '使用 Docker 部署微服务',
            body: '通过 Docker Compose 编排多个服务，使用 Nginx 做反向代理。每个服务独立容器。',
            tags: ['部署'],
        };
        const config = { autoTag: { topN: 5 } };
        const result = autoTag(entry, config);
        assert.ok(result.length > 1);
        assert.ok(result.includes('部署'));
    });

    it('不产生与已有标签重复的建议', () => {
        const entry = {
            title: '数据库优化',
            body: '数据库索引优化，减少全表扫描。数据库连接池调整。',
            tags: ['数据库'],
        };
        const config = { autoTag: { topN: 5 } };
        const result = autoTag(entry, config);
        const dbCount = result.filter(t => t === '数据库').length;
        assert.equal(dbCount, 1);
    });

    it('空标签列表时正常工作', () => {
        const entry = {
            title: '测试标题',
            body: '测试正文内容，包含多个关键词如服务器部署和容器编排',
            tags: [],
        };
        const config = { autoTag: { topN: 3 } };
        const result = autoTag(entry, config);
        assert.ok(result.length > 0);
    });

    it('同义词归一化生效', () => {
        const entry = {
            title: 'Docker 容器化部署',
            body: '使用 docker compose 部署，配置 container 网络',
            tags: [],
        };
        const config = { autoTag: { topN: 5 } };
        const result = autoTag(entry, config);
        const allLower = result.map(t => t.toLowerCase());
        const hasDuplicate = allLower.length !== new Set(allLower).size;
        assert.ok(!hasDuplicate, '不应有语义重复标签');
    });

    it('config.autoTag 不存在时使用默认值', () => {
        const entry = { title: '测试', body: '数据库查询优化', tags: [] };
        const config = {};
        const result = autoTag(entry, config);
        assert.ok(Array.isArray(result));
    });
});
