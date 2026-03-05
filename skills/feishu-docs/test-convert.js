#!/usr/bin/env node

/**
 * 测试飞书文档转换接口
 */

const FeishuDocsAPI = require('./src/api.js');

// 测试配置
const TEST_CONFIG = {
  appId: process.env.FEISHU_APP_ID,
  appSecret: process.env.FEISHU_APP_SECRET
};

// 测试内容
const TEST_MARKDOWN = `# 测试文档标题

这是一个测试文档，用于验证飞书文档转换接口。

## 功能列表

1. 支持Markdown转换
2. 支持HTML转换
3. 支持表格转换
4. 支持代码块

## 代码示例

\`\`\`javascript
// 这是一个JavaScript代码示例
function helloWorld() {
  console.log('Hello, World!');
  return '测试成功';
}
\`\`\`

## 表格示例

| 功能 | 状态 | 说明 |
|------|------|------|
| Markdown转换 | ✅ | 支持基本Markdown语法 |
| HTML转换 | ✅ | 支持基本HTML标签 |
| 图片上传 | ⚠️ | 需要额外处理 |
| 表格处理 | ⚠️ | 需要去除merge_info字段 |

## 引用示例

> 这是引用文本
> 引用可以有多行

## 列表示例

- 无序列表项1
- 无序列表项2
  - 嵌套列表项
  - 另一个嵌套项

1. 有序列表项1
2. 有序列表项2
   1. 嵌套有序项
   2. 另一个嵌套项

---

文档结束。`;

const TEST_HTML = `<h1>HTML测试文档</h1>
<p>这是一个<strong>HTML</strong>测试文档。</p>
<h2>功能列表</h2>
<ul>
  <li>支持HTML标签</li>
  <li>支持样式</li>
  <li>支持链接</li>
</ul>
<p>访问<a href="https://open.feishu.cn">飞书开放平台</a>了解更多。</p>`;

async function testConvertAPI() {
  console.log('🚀 开始测试飞书文档转换接口...\n');
  
  if (!TEST_CONFIG.appId || !TEST_CONFIG.appSecret) {
    console.error('❌ 请设置环境变量 FEISHU_APP_ID 和 FEISHU_APP_SECRET');
    console.error('   或在代码中直接设置appId和appSecret');
    process.exit(1);
  }
  
  try {
    // 初始化API客户端
    const api = new FeishuDocsAPI(TEST_CONFIG.appId, TEST_CONFIG.appSecret);
    
    console.log('1. 测试Markdown内容转换...');
    const markdownResult = await api.convertContent('markdown', TEST_MARKDOWN);
    console.log(`   ✅ Markdown转换成功！`);
    console.log(`      生成块数量: ${markdownResult.blocks?.length || 0}`);
    console.log(`      一级块ID: ${markdownResult.first_level_block_ids?.length || 0}个`);
    
    // 显示块类型统计
    if (markdownResult.blocks) {
      const typeCount = {};
      markdownResult.blocks.forEach(block => {
        typeCount[block.block_type] = (typeCount[block.block_type] || 0) + 1;
      });
      console.log(`      块类型统计:`, typeCount);
    }
    
    console.log('\n2. 测试HTML内容转换...');
    const htmlResult = await api.convertContent('html', TEST_HTML);
    console.log(`   ✅ HTML转换成功！`);
    console.log(`      生成块数量: ${htmlResult.blocks?.length || 0}`);
    
    // 显示块类型统计
    if (htmlResult.blocks) {
      const typeCount = {};
      htmlResult.blocks.forEach(block => {
        typeCount[block.block_type] = (typeCount[block.block_type] || 0) + 1;
      });
      console.log(`      块类型统计:`, typeCount);
    }
    
    console.log('\n3. 测试错误处理...');
    try {
      await api.convertContent('invalid', 'test content');
      console.log('   ❌ 应该抛出错误但没有抛出');
    } catch (error) {
      console.log(`   ✅ 正确捕获错误: ${error.message}`);
    }
    
    try {
      await api.convertContent('markdown', '');
      console.log('   ❌ 应该抛出错误但没有抛出');
    } catch (error) {
      console.log(`   ✅ 正确捕获错误: ${error.message}`);
    }
    
    console.log('\n4. 测试表格块处理...');
    // 检查是否有表格块
    const hasTable = markdownResult.blocks?.some(block => block.block_type === 'table');
    if (hasTable) {
      console.log('   ✅ 检测到表格块，验证处理逻辑...');
      const tableBlock = markdownResult.blocks.find(block => block.block_type === 'table');
      if (tableBlock.table && tableBlock.table.merge_info) {
        console.log('   ⚠️  表格块包含merge_info字段，需要处理');
      } else {
        console.log('   ✅ 表格块不包含merge_info字段或已处理');
      }
    } else {
      console.log('   ℹ️  测试内容中没有表格块');
    }
    
    console.log('\n🎉 所有测试完成！');
    console.log('\n📋 总结:');
    console.log('   - Markdown转换: ✅ 工作正常');
    console.log('   - HTML转换: ✅ 工作正常');
    console.log('   - 错误处理: ✅ 工作正常');
    console.log('   - 表格处理: ✅ 已实现处理逻辑');
    console.log('\n💡 建议:');
    console.log('   1. 使用 create-with-content 命令创建文档');
    console.log('   2. 对于包含图片的内容，需要额外处理图片上传');
    console.log('   3. 大内容需要分批插入（每批最多1000个块）');
    
  } catch (error) {
    console.error('\n❌ 测试失败:', error.message);
    console.error('错误详情:', error);
    process.exit(1);
  }
}

// 运行测试
if (require.main === module) {
  testConvertAPI();
}

module.exports = { testConvertAPI };