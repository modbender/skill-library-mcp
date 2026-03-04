const EventEmitter = require('events');
const { randomUUID: uuid } = require('crypto');

/**
 * Message - 消息结构
 */
class Message {
  constructor({ type = 'direct', from, to, payload, metadata = {} }) {
    this.id = `msg:${uuid()}`;
    this.timestamp = Date.now();
    this.type = type; // direct | broadcast | rpc | event
    this.from = from;
    this.to = to;
    this.payload = payload;
    this.metadata = {
      priority: metadata.priority || 0,
      ttl: metadata.ttl || 300000, // 5分钟超时
      ...metadata
    };
  }

  toJSON() {
    return {
      id: this.id,
      timestamp: this.timestamp,
      type: this.type,
      from: this.from,
      to: this.to,
      payload: this.payload,
      metadata: this.metadata
    };
  }
}

/**
 * Knot - 安全边界验证
 */
class Knot {
  constructor(registry) {
    this.registry = registry;
  }

  /**
   * 验证通信权限
   */
  canCommunicate(senderId, receiverId) {
    const sender = this.registry.get(senderId);
    const receiver = this.registry.get(receiverId);

    if (!sender || !receiver) {
      return { allowed: false, reason: 'Agent not found' };
    }

    // 规则1: 同父兄弟（Worker之间）
    if (sender.parentId && sender.parentId === receiver.parentId) {
      return { allowed: true, rule: 'sibling' };
    }

    // 规则2: 父子双向
    if (sender.id === receiver.parentId) {
      return { allowed: true, rule: 'parent-to-child' };
    }
    if (receiver.id === sender.parentId) {
      return { allowed: true, rule: 'child-to-parent' };
    }

    // 规则3: Master之间（Kimi Swarm）
    if (sender.type === 'master' && receiver.type === 'master') {
      return { allowed: true, rule: 'master-to-master' };
    }

    // 拒绝
    return {
      allowed: false,
      reason: 'Agents are not in the same trust boundary',
      sender: { id: sender.id, parent: sender.parentId, type: sender.type },
      receiver: { id: receiver.id, parent: receiver.parentId, type: receiver.type }
    };
  }
}

/**
 * Thread - 通信层
 */
class Thread extends EventEmitter {
  constructor(registry, options = {}) {
    super();
    this.registry = registry;
    this.knot = new Knot(registry);
    this.messages = new Map();
    this.subscriptions = new Map();
    this.options = {
      defaultTimeout: options.defaultTimeout || 30000,
      maxRetries: options.maxRetries || 3,
      ...options
    };
  }

  /**
   * 发送消息（带安全验证）
   */
  async send(message) {
    // 验证通信权限
    const permission = this.knot.canCommunicate(message.from, message.to);
    
    if (!permission.allowed) {
      const error = new Error(`Communication denied: ${permission.reason}`);
      error.permission = permission;
      throw error;
    }

    // 存储消息
    this.messages.set(message.id, message);
    
    // 触发发送事件
    this.emit('message:send', message, permission);
    
    return message;
  }

  /**
   * 广播（同父兄弟）
   */
  async broadcast(from, payload, options = {}) {
    const sender = this.registry.get(from);
    if (!sender || !sender.parentId) {
      throw new Error('Only agents with parent can broadcast');
    }

    // 获取同父兄弟
    const siblings = this.registry.getByParent ? 
      this.registry.getByParent(sender.parentId).filter(a => a.id !== from) :
      [];

    const messages = [];
    for (const sibling of siblings) {
      const msg = new Message({
        type: 'broadcast',
        from,
        to: sibling.id,
        payload,
        metadata: options.metadata || {}
      });
      messages.push(this.send(msg));
    }

    return Promise.all(messages);
  }

  /**
   * RPC 调用（请求-响应）
   */
  async rpc(from, to, method, params, options = {}) {
    const timeout = options.timeout || this.options.defaultTimeout;
    const correlationId = `rpc:${uuid()}`;

    // 发送请求
    const request = new Message({
      type: 'rpc',
      from,
      to,
      payload: { method, params, correlationId },
      metadata: { timeout, ...options.metadata }
    });

    await this.send(request);

    // 等待响应
    return new Promise((resolve, reject) => {
      const timer = setTimeout(() => {
        this.off('message:rpc-response', handler);
        reject(new Error(`RPC timeout after ${timeout}ms`));
      }, timeout);

      const handler = (msg) => {
        if (msg.payload?.correlationId === correlationId) {
          clearTimeout(timer);
          this.off('message:rpc-response', handler);
          
          if (msg.payload.error) {
            reject(new Error(msg.payload.error));
          } else {
            resolve(msg.payload.result);
          }
        }
      };

      this.on('message:rpc-response', handler);
    });
  }

  /**
   * 订阅消息
   */
  subscribe(agentId, filter, handler) {
    const subscription = {
      id: `sub:${uuid()}`,
      agentId,
      filter,
      handler
    };

    this.subscriptions.set(subscription.id, subscription);

    // 监听所有消息，过滤后分发
    const listener = (msg, permission) => {
      if (msg.to === agentId || this.matchesFilter(msg, filter)) {
        handler(msg, permission);
      }
    };

    this.on('message:send', listener);

    // 返回取消订阅函数
    return () => {
      this.subscriptions.delete(subscription.id);
      this.off('message:send', listener);
    };
  }

  matchesFilter(msg, filter) {
    if (!filter) return false;
    if (filter.type && msg.type !== filter.type) return false;
    if (filter.from && msg.from !== filter.from) return false;
    if (filter.to && msg.to !== filter.to) return false;
    return true;
  }
}

module.exports = {
  Thread,
  Message,
  Knot
};
