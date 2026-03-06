# Agent-Weave 优化架构设计

## 核心改进

### 1. 子Agent无时长限制
- 子Agent运行时不设置超时限制
- 使用长期运行的Promise/事件机制
- 支持手动取消/终止

### 2. 异步双向通信
```
父Agent <-----> 通信通道 <-----> 子Agent
   ↓                                  ↓
可执行其他任务                  长期运行测试
   ↓                                  ↓
检查状态/结果                   发送进度/结果
```

### 3. 并发处理机制
- 父Agent使用async/await非阻塞
- 支持多个子Agent并行
- 事件驱动状态更新

## 通信协议

### 消息类型
1. **START** - 启动任务
2. **PROGRESS** - 进度更新
3. **RESULT** - 最终结果
4. **ERROR** - 错误信息
5. **CANCEL** - 取消任务

### 状态机
```
PENDING -> RUNNING -> COMPLETED
              ↓           ↓
           CANCELLED   ERROR
```

## API设计

### 父Agent端
```javascript
// 创建长期运行子Agent
const task = await agentSystem.spawn({
  task: 'test-agent-weave',
  timeout: 0,  // 无限制
  onProgress: (data) => console.log(data),
  onComplete: (result) => console.log(result),
  onError: (error) => console.error(error)
});

// 检查状态
const status = await task.getStatus();

// 取消任务
await task.cancel();
```

### 子Agent端
```javascript
// 发送进度
agentSystem.reportProgress({ percent: 50, message: '测试中...' });

// 发送结果
agentSystem.reportResult({ passed: 6, failed: 0 });

// 报告错误
agentSystem.reportError(new Error('测试失败'));
```
