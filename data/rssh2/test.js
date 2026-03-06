import { Rssh2 } from './index.js';

// 配置 - 请替换为你的实际配置
const config = {
  host: 'your-server.com',        // 服务器地址
  port: 22,                        // SSH 端口
  username: 'your-username',       // 用户名
  privateKey: '/path/to/key',      // 私钥路径（可选）
  password: 'your-password'        // 密码（可选，不推荐）
};

async function test() {
  console.log('🚀 Rssh2 测试开始...\n');

  const rssh2 = new Rssh2(config, { autoConnect: false });

  try {
    // 测试连接
    console.log('📡 测试连接...');
    await rssh2.connect();
    console.log('✅ 连接成功\n');

    // 测试执行命令
    console.log('📝 测试执行命令...');
    const result = await rssh2.exec('uptime');
    console.log('输出:', result.stdout);
    console.log('✅ 命令执行成功\n');

    // 测试会话管理器
    console.log('🔄 测试会话管理器...');
    const session = rssh2.getSessionManager();
    const results = await session.execMultiple([
      'uptime',
      'df -h | head -5',
      'free -m | head -5'
    ]);
    console.log('执行了', results.length, '个命令');
    console.log('✅ 会话管理器测试成功\n');

    // 测试SFTP
    console.log('📁 测试SFTP...');
    const sftp = rssh2.getSftpManager();
    const files = await sftp.list('/root');
    console.log('文件列表:', files.map(f => f.name).slice(0, 5));
    console.log('✅ SFTP测试成功\n');

    // 测试隧道
    console.log('🌉 测试隧道...');
    const tunnel = await rssh2.tunnelLocal({
      localPort: 18080,
      remoteHost: 'localhost',
      remotePort: 80
    });
    console.log('隧道ID:', tunnel.id);
    console.log('✅ 隧道测试成功\n');

    // 获取统计信息
    console.log('📊 统计信息:');
    console.log(JSON.stringify(rssh2.getStats(), null, 2));

    // 关闭隧道
    await rssh2.getTunnelManager().close(tunnel.id);

    // 关闭连接
    await rssh2.close();
    console.log('\n🎉 所有测试完成！');

  } catch (error) {
    console.error('❌ 测试失败:', error.message);
    await rssh2.close();
    process.exit(1);
  }
}

test();