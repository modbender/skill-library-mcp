const { describe, it, beforeEach, afterEach } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('fs');
const path = require('path');
const os = require('os');
const { parseLogFile, parseLogContent, findLogFiles, extractTags } = require('./parser');

let tmpDir;

beforeEach(() => {
    tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'km-parser-'));
});

afterEach(() => {
    fs.rmSync(tmpDir, { recursive: true, force: true });
});

describe('extractTags', () => {
    it('提取多个标签', () => {
        assert.deepEqual(extractTags('#报表 #自动化 #pandas'), ['报表', '自动化', 'pandas']);
    });

    it('处理无标签的行', () => {
        assert.deepEqual(extractTags('普通文本行'), []);
    });

    it('处理紧密排列的标签', () => {
        assert.deepEqual(extractTags('#标签1#标签2'), ['标签1', '标签2']);
    });

    it('处理带连字符的英文标签', () => {
        assert.deepEqual(extractTags('#data-pipeline #auto-tag'), ['data-pipeline', 'auto-tag']);
    });

    it('处理混合中英文标签', () => {
        assert.deepEqual(extractTags('#部署 #Docker #k8s #生产环境'), ['部署', 'Docker', 'k8s', '生产环境']);
    });
});

describe('parseLogContent - 基础解析', () => {
    it('解析标准 3 行格式', () => {
        const content = `### [PROJECT:数据报表] 自动化报表部署完成
crontab + Python 每日 8:00 推飞书。pandas 大表用 chunksize 避免 OOM。
#报表 #自动化 #pandas #飞书`;

        const entries = parseLogContent(content, '2026-02-24.md');
        assert.equal(entries.length, 1);
        assert.equal(entries[0].prefix, 'PROJECT');
        assert.equal(entries[0].name, '数据报表');
        assert.equal(entries[0].title, '自动化报表部署完成');
        assert.equal(entries[0].body, 'crontab + Python 每日 8:00 推飞书。pandas 大表用 chunksize 避免 OOM。');
        assert.deepEqual(entries[0].tags, ['报表', '自动化', 'pandas', '飞书']);
        assert.equal(entries[0].date, '2026-02-24');
    });

    it('解析无标签的条目', () => {
        const content = `### [INFRA:基础设施] 服务器迁移完成
新服务器 IP 192.168.1.100，已完成数据迁移。`;

        const entries = parseLogContent(content);
        assert.equal(entries.length, 1);
        assert.equal(entries[0].tags.length, 0);
        assert.ok(entries[0].body.includes('192.168.1.100'));
    });

    it('解析无正文只有标签的条目', () => {
        const content = `### [KB:知识] 测试条目
#测试`;

        const entries = parseLogContent(content);
        assert.equal(entries.length, 1);
        assert.equal(entries[0].body, '');
        assert.deepEqual(entries[0].tags, ['测试']);
    });

    it('解析多条日志', () => {
        const content = `### [PROJECT:报表] 第一条
内容一
#tag1

### [ISSUE:报表] 第二条
内容二
#tag2

### [INFRA:服务器] 第三条
内容三
#tag3`;

        const entries = parseLogContent(content, '2026-02-24.md');
        assert.equal(entries.length, 3);
        assert.equal(entries[0].title, '第一条');
        assert.equal(entries[1].title, '第二条');
        assert.equal(entries[2].title, '第三条');
    });

    it('解析多行正文', () => {
        const content = `### [RESEARCH:架构] 微服务调研
1. Spring Cloud 适合大型项目
2. 单体应用拆分需谨慎
3. 数据库拆分是最大挑战
考虑使用 Saga 模式处理分布式事务。
#微服务 #架构`;

        const entries = parseLogContent(content);
        assert.equal(entries.length, 1);
        assert.ok(entries[0].body.includes('Spring Cloud'));
        assert.ok(entries[0].body.includes('Saga 模式'));
        assert.equal(entries[0].body.split('\n').length, 4);
    });
});

describe('parseLogContent - 边界情况', () => {
    it('空文件', () => {
        assert.deepEqual(parseLogContent(''), []);
    });

    it('仅空白内容', () => {
        assert.deepEqual(parseLogContent('   \n\n  \n'), []);
    });

    it('没有 PREFIX 条目的内容（纯文本）', () => {
        const content = `# 日志标题
## 2026-02-24
今天做了一些事情`;
        assert.deepEqual(parseLogContent(content), []);
    });

    it('PREFIX 前有 ## Section 头', () => {
        const content = `## 开发日志

### [PROJECT:报表] 完成开发
开发完毕
#开发`;

        const entries = parseLogContent(content);
        assert.equal(entries.length, 1);
        assert.equal(entries[0].title, '完成开发');
    });

    it('标题包含特殊字符', () => {
        const content = `### [PROJECT:AI助手] 实现 v2.0-beta (含 LLM 增强)
升级到新版本
#AI`;

        const entries = parseLogContent(content);
        assert.equal(entries.length, 1);
        assert.equal(entries[0].title, '实现 v2.0-beta (含 LLM 增强)');
    });

    it('name 包含中文和空格', () => {
        const content = `### [PROJECT:数据 报表] 测试
内容
#test`;

        const entries = parseLogContent(content);
        assert.equal(entries.length, 1);
        assert.equal(entries[0].name, '数据 报表');
    });

    it('正文中包含 #### 四级标题', () => {
        const content = `### [KB:知识] 测试条目
正文开始
#### 子标题不应被吃掉
更多正文
#测试`;

        const entries = parseLogContent(content);
        assert.equal(entries.length, 1);
        assert.ok(entries[0].body.includes('####'));
    });

    it('正文中包含代码块带 #', () => {
        const content = `### [CONFIG:配置] Nginx 配置
配置 upstream：
server 192.168.1.1;
#nginx #配置`;

        const entries = parseLogContent(content);
        assert.equal(entries.length, 1);
        assert.deepEqual(entries[0].tags, ['nginx', '配置']);
    });

    it('连续两个条目之间无空行', () => {
        const content = `### [PROJECT:A] 第一条
内容一
#tag1
### [PROJECT:B] 第二条
内容二
#tag2`;

        const entries = parseLogContent(content);
        assert.equal(entries.length, 2);
        assert.equal(entries[0].title, '第一条');
        assert.equal(entries[1].title, '第二条');
    });

    it('超长正文（>1000 字符）', () => {
        const longBody = '这是一段很长的正文。'.repeat(200);
        const content = `### [KB:知识] 超长内容测试
${longBody}
#长文`;

        const entries = parseLogContent(content);
        assert.equal(entries.length, 1);
        assert.ok(entries[0].body.length > 1000);
    });

    it('无日期文件名时使用当天日期', () => {
        const content = `### [KB:知识] 测试
内容`;
        const entries = parseLogContent(content, 'random-note.md');
        assert.equal(entries.length, 1);
        assert.match(entries[0].date, /^\d{4}-\d{2}-\d{2}$/);
    });

    it('日期从文件名正确提取', () => {
        const entries = parseLogContent('### [KB:知识] 测试\n内容', '2026-01-15.md');
        assert.equal(entries[0].date, '2026-01-15');
    });

    it('多个标签行（正文中间和末尾各有标签行）', () => {
        const content = `### [PROJECT:报表] 测试
#中间标签
正文内容
#末尾标签`;

        const entries = parseLogContent(content);
        assert.equal(entries.length, 1);
        assert.ok(entries[0].tags.includes('中间标签'));
        assert.ok(entries[0].tags.includes('末尾标签'));
    });

    it('仅有标题行，无正文无标签', () => {
        const content = `### [PROJECT:报表] 只有标题`;
        const entries = parseLogContent(content);
        assert.equal(entries.length, 1);
        assert.equal(entries[0].body, '');
        assert.deepEqual(entries[0].tags, []);
    });

    it('raw 字段包含完整原文', () => {
        const content = `### [PROJECT:报表] 标题
正文
#标签`;
        const entries = parseLogContent(content);
        assert.ok(entries[0].raw.includes('### [PROJECT:报表] 标题'));
        assert.ok(entries[0].raw.includes('正文'));
        assert.ok(entries[0].raw.includes('#标签'));
    });
});

describe('parseLogFile', () => {
    it('读取并解析文件', () => {
        const filePath = path.join(tmpDir, '2026-02-24.md');
        fs.writeFileSync(filePath, `### [PROJECT:报表] 文件测试
内容
#测试`);

        const entries = parseLogFile(filePath);
        assert.equal(entries.length, 1);
        assert.equal(entries[0].date, '2026-02-24');
    });

    it('文件不存在时抛异常', () => {
        assert.throws(() => parseLogFile(path.join(tmpDir, 'nonexistent.md')));
    });
});

describe('findLogFiles', () => {
    it('找到指定天数内的日志文件', () => {
        const today = new Date().toISOString().slice(0, 10);
        fs.writeFileSync(path.join(tmpDir, `${today}.md`), '');
        fs.writeFileSync(path.join(tmpDir, '2020-01-01.md'), '');
        fs.writeFileSync(path.join(tmpDir, 'readme.txt'), '');

        const files = findLogFiles(tmpDir, 7);
        assert.equal(files.length, 1);
        assert.ok(files[0].endsWith(`${today}.md`));
    });

    it('目录不存在时返回空数组', () => {
        const files = findLogFiles(path.join(tmpDir, 'nonexistent'), 7);
        assert.deepEqual(files, []);
    });

    it('按日期排序返回', () => {
        const d1 = new Date();
        const d2 = new Date(d1);
        d2.setDate(d2.getDate() - 1);
        const s1 = d1.toISOString().slice(0, 10);
        const s2 = d2.toISOString().slice(0, 10);

        fs.writeFileSync(path.join(tmpDir, `${s1}.md`), '');
        fs.writeFileSync(path.join(tmpDir, `${s2}.md`), '');

        const files = findLogFiles(tmpDir, 7);
        assert.equal(files.length, 2);
        assert.ok(files[0].includes(s2));
        assert.ok(files[1].includes(s1));
    });

    it('忽略非 YYYY-MM-DD.md 格式的文件', () => {
        fs.writeFileSync(path.join(tmpDir, 'notes.md'), '');
        fs.writeFileSync(path.join(tmpDir, '2026-02-24.txt'), '');
        fs.writeFileSync(path.join(tmpDir, '20260224.md'), '');

        const files = findLogFiles(tmpDir, 365);
        assert.equal(files.length, 0);
    });
});
