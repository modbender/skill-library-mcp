#!/usr/bin/env node

const { Command } = require('commander');
const fs = require('fs');
const path = require('path');
const FeishuDocsAPI = require('../src/api.js');

// 加载环境变量
require('dotenv').config();

const program = new Command();

program
  .name('feishu-docs')
  .description('飞书文档(Docx)命令行工具')
  .version(require('../package.json').version);

// 初始化API客户端
function initAPI() {
  const appId = process.env.FEISHU_APP_ID;
  const appSecret = process.env.FEISHU_APP_SECRET;
  
  if (!appId || !appSecret) {
    console.error('错误: 请设置环境变量 FEISHU_APP_ID 和 FEISHU_APP_SECRET');
    console.error('或使用 --app-id 和 --app-secret 参数');
    process.exit(1);
  }
  
  return new FeishuDocsAPI(appId, appSecret);
}

// 创建文档命令
program
  .command('create')
  .description('创建新文档')
  .requiredOption('-f, --folder-token <token>', '文件夹token')
  .requiredOption('-t, --title <title>', '文档标题')
  .option('-c, --content <content>', '文档内容（Markdown格式）')
  .option('--content-file <file>', '从文件读取文档内容')
  .option('--app-id <id>', '飞书应用ID（覆盖环境变量）')
  .option('--app-secret <secret>', '飞书应用密钥（覆盖环境变量）')
  .action(async (options) => {
    try {
      if (options.appId) process.env.FEISHU_APP_ID = options.appId;
      if (options.appSecret) process.env.FEISHU_APP_SECRET = options.appSecret;
      
      const api = initAPI();
      
      let content = options.content || '';
      if (options.contentFile) {
        content = fs.readFileSync(options.contentFile, 'utf8');
      }
      
      console.log('正在创建文档...');
      let result;
      if (content) {
        result = await api.createDocumentWithContent(options.folderToken, options.title, content);
      } else {
        result = await api.createDocument(options.folderToken, options.title);
      }
      
      console.log('✅ 文档创建成功！');
      console.log(`文档ID: ${result.document.document_id}`);
      console.log(`文档标题: ${result.document.title}`);
      console.log(`文档URL: https://example.feishu.cn/docx/${result.document.document_id}`);
      
    } catch (error) {
      console.error('❌ 创建文档失败:', error.message);
      process.exit(1);
    }
  });

// 获取文档命令
program
  .command('get')
  .description('获取文档信息')
  .requiredOption('-d, --document-id <id>', '文档ID')
  .option('--format <format>', '输出格式（json, markdown, text）', 'json')
  .option('--include-content', '包含文档内容')
  .option('--app-id <id>', '飞书应用ID（覆盖环境变量）')
  .option('--app-secret <secret>', '飞书应用密钥（覆盖环境变量）')
  .action(async (options) => {
    try {
      if (options.appId) process.env.FEISHU_APP_ID = options.appId;
      if (options.appSecret) process.env.FEISHU_APP_SECRET = options.appSecret;
      
      const api = initAPI();
      
      console.log('正在获取文档信息...');
      const document = await api.getDocument(options.documentId);
      
      if (options.format === 'json') {
        console.log(JSON.stringify(document, null, 2));
      } else {
        console.log(`文档ID: ${document.document_id}`);
        console.log(`文档标题: ${document.title}`);
        if (document.create_time) {
          console.log(`创建时间: ${new Date(document.create_time * 1000).toLocaleString('zh-CN')}`);
        }
        if (document.edit_time) {
          console.log(`更新时间: ${new Date(document.edit_time * 1000).toLocaleString('zh-CN')}`);
        }
        if (document.creator_id) {
          console.log(`创建者: ${document.creator_id}`);
        }
        
        if (options.includeContent) {
          console.log('\n正在获取文档内容...');
          const blocks = await api.getDocumentBlocks(options.documentId);
          const markdown = api.blocksToMarkdown(blocks.items || []);
          
          if (options.format === 'markdown') {
            console.log('\n文档内容（Markdown格式）:');
            console.log('---');
            console.log(markdown);
            console.log('---');
          } else if (options.format === 'text') {
            console.log('\n文档内容:');
            console.log(markdown);
          }
        }
      }
      
    } catch (error) {
      console.error('❌ 获取文档失败:', error.message);
      process.exit(1);
    }
  });

// 更新文档命令
program
  .command('update')
  .description('更新文档内容')
  .requiredOption('-d, --document-id <id>', '文档ID')
  .option('-c, --content <content>', '新的文档内容（Markdown格式）')
  .option('--content-file <file>', '从文件读取新的文档内容')
  .option('--append', '追加内容而不是替换')
  .option('--app-id <id>', '飞书应用ID（覆盖环境变量）')
  .option('--app-secret <secret>', '飞书应用密钥（覆盖环境变量）')
  .action(async (options) => {
    try {
      if (options.appId) process.env.FEISHU_APP_ID = options.appId;
      if (options.appSecret) process.env.FEISHU_APP_SECRET = options.appSecret;
      
      const api = initAPI();
      
      let newContent = options.content || '';
      if (options.contentFile) {
        newContent = fs.readFileSync(options.contentFile, 'utf8');
      }
      
      if (!newContent) {
        console.error('错误: 请提供要更新的内容');
        process.exit(1);
      }
      
      console.log('正在更新文档...');
      
      if (options.append) {
        await api.appendToDocument(options.documentId, newContent);
        console.log('✅ 内容追加成功！');
      } else {
        await api.replaceDocumentContent(options.documentId, newContent);
        console.log('✅ 文档更新成功！');
      }
      
    } catch (error) {
      console.error('❌ 更新文档失败:', error.message);
      process.exit(1);
    }
  });

// 删除文档命令
program
  .command('delete')
  .description('删除文档')
  .requiredOption('-d, --document-id <id>', '文档ID')
  .option('--app-id <id>', '飞书应用ID（覆盖环境变量）')
  .option('--app-secret <secret>', '飞书应用密钥（覆盖环境变量）')
  .action(async (options) => {
    try {
      if (options.appId) process.env.FEISHU_APP_ID = options.appId;
      if (options.appSecret) process.env.FEISHU_APP_SECRET = options.appSecret;
      
      const api = initAPI();
      
      console.log('正在删除文档...');
      await api.deleteDocument(options.documentId);
      
      console.log('✅ 文档删除成功！');
      
    } catch (error) {
      console.error('❌ 删除文档失败:', error.message);
      process.exit(1);
    }
  });

// 搜索文档命令
program
  .command('search')
  .description('搜索文档')
  .requiredOption('-q, --query <query>', '搜索关键词')
  .option('-f, --folder-token <token>', '在指定文件夹内搜索')
  .option('--limit <number>', '返回结果数量', '10')
  .option('--app-id <id>', '飞书应用ID（覆盖环境变量）')
  .option('--app-secret <secret>', '飞书应用密钥（覆盖环境变量）')
  .action(async (options) => {
    try {
      if (options.appId) process.env.FEISHU_APP_ID = options.appId;
      if (options.appSecret) process.env.FEISHU_APP_SECRET = options.appSecret;
      
      const api = initAPI();
      
      console.log(`正在搜索 "${options.query}"...`);
      const results = await api.searchDocuments(options.query, options.folderToken);
      
      console.log(`找到 ${results.files?.length || 0} 个结果:`);
      console.log('');
      
      if (results.files && results.files.length > 0) {
        results.files.slice(0, parseInt(options.limit)).forEach((file, index) => {
          console.log(`${index + 1}. ${file.name}`);
          console.log(`   类型: ${file.type}`);
          console.log(`   Token: ${file.token}`);
          if (file.created_time) {
            console.log(`   创建时间: ${new Date(parseInt(file.created_time) * 1000).toLocaleString('zh-CN')}`);
          }
          console.log('');
        });
      } else {
        console.log('没有找到匹配的文档。');
      }
      
    } catch (error) {
      console.error('❌ 搜索文档失败:', error.message);
      process.exit(1);
    }
  });

// 列出文件夹文件命令
program
  .command('list')
  .description('列出文件夹中的文件')
  .requiredOption('-f, --folder-token <token>', '文件夹token')
  .option('--type <type>', '文件类型（doc, docx, sheet, bitable, file）', 'docx')
  .option('--limit <number>', '返回结果数量', '50')
  .option('--app-id <id>', '飞书应用ID（覆盖环境变量）')
  .option('--app-secret <secret>', '飞书应用密钥（覆盖环境变量）')
  .action(async (options) => {
    try {
      if (options.appId) process.env.FEISHU_APP_ID = options.appId;
      if (options.appSecret) process.env.FEISHU_APP_SECRET = options.appSecret;
      
      const api = initAPI();
      
      console.log(`正在列出文件夹中的 ${options.type} 文件...`);
      const files = await api.listFolderFiles(options.folderToken, options.type);
      
      console.log(`找到 ${files.files?.length || 0} 个文件:`);
      console.log('');
      
      if (files.files && files.files.length > 0) {
        files.files.slice(0, parseInt(options.limit)).forEach((file, index) => {
          console.log(`${index + 1}. ${file.name}`);
          console.log(`   类型: ${file.type}`);
          console.log(`   Token: ${file.token}`);
          if (file.created_time) {
            console.log(`   创建时间: ${new Date(parseInt(file.created_time) * 1000).toLocaleString('zh-CN')}`);
          }
          console.log('');
        });
      } else {
        console.log('文件夹为空。');
      }
      
    } catch (error) {
      console.error('❌ 列出文件失败:', error.message);
      process.exit(1);
    }
  });

// 分享文档命令
program
  .command('share')
  .description('分享文档给用户')
  .requiredOption('-d, --document-id <id>', '文档ID')
  .requiredOption('-u, --user-id <id>', '用户ID')
  .option('--perm <perm>', '权限类型（view, edit, comment）', 'view')
  .option('--app-id <id>', '飞书应用ID（覆盖环境变量）')
  .option('--app-secret <secret>', '飞书应用密钥（覆盖环境变量）')
  .action(async (options) => {
    try {
      if (options.appId) process.env.FEISHU_APP_ID = options.appId;
      if (options.appSecret) process.env.FEISHU_APP_SECRET = options.appSecret;
      
      const api = initAPI();
      
      console.log('正在分享文档...');
      const result = await api.addPermissionMember(options.documentId, options.userId, 'user', options.perm);
      
      console.log('✅ 文档分享成功！');
      console.log(`权限: ${options.perm}`);
      console.log(`用户ID: ${options.userId}`);
      
    } catch (error) {
      console.error('❌ 分享文档失败:', error.message);
      process.exit(1);
    }
  });

// 获取权限成员命令
program
  .command('permissions')
  .description('获取文档权限成员列表')
  .requiredOption('-d, --document-id <id>', '文档ID')
  .option('--app-id <id>', '飞书应用ID（覆盖环境变量）')
  .option('--app-secret <secret>', '飞书应用密钥（覆盖环境变量）')
  .action(async (options) => {
    try {
      if (options.appId) process.env.FEISHU_APP_ID = options.appId;
      if (options.appSecret) process.env.FEISHU_APP_SECRET = options.appSecret;
      
      const api = initAPI();
      
      console.log('正在获取权限成员列表...');
      const members = await api.getPermissionMembers(options.documentId);
      
      console.log(`文档有 ${members.members?.length || 0} 个权限成员:`);
      console.log('');
      
      if (members.members && members.members.length > 0) {
        members.members.forEach((member, index) => {
          console.log(`${index + 1}. ${member.member_type}: ${member.member_id}`);
          console.log(`   权限: ${member.perm}`);
          console.log(`   类型: ${member.type}`);
          console.log('');
        });
      } else {
        console.log('文档没有设置权限成员。');
      }
      
    } catch (error) {
      console.error('❌ 获取权限成员失败:', error.message);
      process.exit(1);
    }
  });

// 转换内容命令
program
  .command('convert')
  .description('将Markdown/HTML内容转换为文档块')
  .requiredOption('-t, --content-type <type>', '内容类型：markdown 或 html')
  .option('-c, --content <content>', '要转换的内容')
  .option('--content-file <file>', '从文件读取内容')
  .option('--user-id-type <type>', '用户ID类型：open_id, union_id, user_id', 'open_id')
  .option('--app-id <id>', '飞书应用ID（覆盖环境变量）')
  .option('--app-secret <secret>', '飞书应用密钥（覆盖环境变量）')
  .action(async (options) => {
    try {
      if (options.appId) process.env.FEISHU_APP_ID = options.appId;
      if (options.appSecret) process.env.FEISHU_APP_SECRET = options.appSecret;
      
      const api = initAPI();
      
      let content = options.content || '';
      if (options.contentFile) {
        content = fs.readFileSync(options.contentFile, 'utf8');
      }
      
      if (!content) {
        console.error('错误: 请使用 --content 或 --content-file 提供要转换的内容');
        process.exit(1);
      }

      console.log(`正在将${options.contentType}内容转换为文档块...`);
      const result = await api.convertContent(options.contentType, content, options.userIdType);
      
      console.log('✅ 内容转换成功！');
      console.log(`生成块数量: ${result.blocks?.length || 0}`);
      console.log(`一级块ID: ${result.first_level_block_ids?.join(', ') || '无'}`);
      
      if (result.blocks && result.blocks.length > 0) {
        console.log('\n前5个块类型:');
        result.blocks.slice(0, 5).forEach((block, index) => {
          console.log(`${index + 1}. ${block.block_type}`);
        });
      }
      
    } catch (error) {
      console.error('❌ 内容转换失败:', error.message);
      process.exit(1);
    }
  });

// 创建文档（使用正确流程）命令
program
  .command('create-with-content')
  .description('创建文档并正确插入Markdown/HTML内容')
  .requiredOption('-f, --folder-token <token>', '文件夹token')
  .requiredOption('-t, --title <title>', '文档标题')
  .option('-c, --content <content>', '文档内容（Markdown格式）')
  .option('--content-file <file>', '从文件读取文档内容')
  .option('--content-type <type>', '内容类型：markdown 或 html', 'markdown')
  .option('--app-id <id>', '飞书应用ID（覆盖环境变量）')
  .option('--app-secret <secret>', '飞书应用密钥（覆盖环境变量）')
  .action(async (options) => {
    try {
      if (options.appId) process.env.FEISHU_APP_ID = options.appId;
      if (options.appSecret) process.env.FEISHU_APP_SECRET = options.appSecret;
      
      const api = initAPI();
      
      let content = options.content || '';
      if (options.contentFile) {
        content = fs.readFileSync(options.contentFile, 'utf8');
      }
      
      console.log('正在创建文档并插入内容...');
      const result = await api.createDocumentWithContent(
        options.folderToken, 
        options.title, 
        content,
        options.contentType
      );
      
      console.log('✅ 文档创建成功！');
      console.log(`文档ID: ${result.document.document_id}`);
      console.log(`文档标题: ${result.document.title}`);
      console.log(`文档URL: https://feishu.cn/docx/${result.document.document_id}`);
      
      if (content) {
        console.log(`内容已正确插入到文档中（使用${options.contentType}转换）`);
      }
      
    } catch (error) {
      console.error('❌ 创建文档失败:', error.message);
      process.exit(1);
    }
  });

// 解析命令行参数
program.parse(process.argv);

// 如果没有提供命令，显示帮助
if (!process.argv.slice(2).length) {
  program.outputHelp();
}