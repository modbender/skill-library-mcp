# Cue v1.0.4 Node.js 迁移计划

## 时间预算
- **总时间**: 4小时 (240分钟)
- **开始时间**: 2026-02-25 06:15
- **截止时间**: 2026-02-25 10:15

## 阶段划分

### 阶段 1: 架构设计 (30分钟)
- [ ] 设计 Node.js 项目结构
- [ ] 确定模块划分
- [ ] 设计配置系统

### 阶段 2: 核心功能迁移 (90分钟)
- [ ] 主入口 (src/index.js) - 替代 cue.sh
- [ ] 命令路由系统
- [ ] 研究任务管理
- [ ] 监控任务管理
- [ ] 通知系统

### 阶段 3: API 客户端迁移 (60分钟)
- [ ] 迁移 cuecue-client.js 到 ES Module
- [ ] 提示词生成系统
- [ ] 自动角色匹配

### 阶段 4: 执行器迁移 (30分钟)
- [ ] 监控执行引擎
- [ ] 搜索执行器
- [ ] 浏览器执行器

### 阶段 5: 测试验证 (30分钟)
- [ ] 单元测试
- [ ] 集成测试
- [ ] 全流程验证

## Node.js 项目结构

```
cue-v1.0.4/
├── package.json          # 更新主入口和依赖
├── src/
│   ├── index.js          # 主入口 (替代 cue.sh)
│   ├── commands/         # 命令处理器
│   │   ├── research.js   # /cue 命令
│   │   ├── tasks.js      # /ct 命令
│   │   ├── monitors.js   # /cm 命令
│   │   ├── notices.js    # /cn 命令
│   │   ├── config.js     # /config, /key 命令
│   │   └── help.js       # /ch 命令
│   ├── core/
│   │   ├── taskManager.js      # 任务管理
│   │   ├── monitorManager.js   # 监控管理
│   │   ├── userState.js        # 用户状态管理
│   │   └── logger.js           # 日志系统
│   ├── api/
│   │   ├── cuecueClient.js     # API 客户端
│   │   └── promptBuilder.js    # 提示词构建
│   ├── executors/
│   │   ├── monitorEngine.js    # 监控执行引擎
│   │   ├── searchExecutor.js   # 搜索执行器
│   │   └── browserExecutor.js  # 浏览器执行器
│   └── utils/
│       ├── fileUtils.js        # 文件操作
│       ├── envUtils.js         # 环境变量
│       └── validators.js       # 验证工具
├── scripts/              # 保留兼容性（软链接或包装）
└── tests/                # 测试文件
```

## 关键设计决策

### 1. 保持 CLI 接口兼容
- 所有 /command 格式保持不变
- 环境变量兼容
- 数据目录兼容 (~/.cuecue)

### 2. 进程管理
- 使用 child_process 替代 nohup
- 使用 EventEmitter 进行进程间通信
- 使用 fs.watch 监控文件变化

### 3. 通知系统改进
- 实现消息队列机制
- 支持多种通知渠道
- 失败重试机制

### 4. 错误处理
- 统一错误类
- 详细错误日志
- 自动恢复机制

## 依赖清单

```json
{
  "dependencies": {
    "commander": "^11.0.0",      // CLI 框架
    "chalk": "^5.3.0",           // 终端颜色
    "ora": "^7.0.1",             // 加载动画
    "inquirer": "^9.2.0",        // 交互式提示
    "node-cron": "^3.0.3",       // Cron 任务
    "fs-extra": "^11.1.0"        // 增强文件操作
  },
  "devDependencies": {
    "jest": "^29.7.0",           // 测试框架
    "nodemon": "^3.0.1"          // 开发热重载
  }
}
```

## 回滚机制

如果需要回滚到 v1.0.3:
```bash
cd /root/workspaces/feishu-feishu-ou_5facd87f11cb35d651c435a4c1c7c4bc/skills/cue
rm -rf src/ tests/ node_modules/
tar -xzf backups/cue-v1.0.3-backup-20260225-0611.tar.gz
```

## 成功标准

1. ✅ 所有 v1.0.3 功能完整迁移
2. ✅ 通过 comprehensive-test.js 测试
3. ✅ 至少一个完整研究任务跑通
4. ✅ 监控功能正常工作
5. ✅ 通知系统改进（解决后台进程通知问题）
