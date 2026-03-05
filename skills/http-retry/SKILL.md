# HTTP 重试技能

**触发词**: timeouterror, econnreset, econnrefused, 429, retry, http error, 网络超时

## 问题
网络请求失败（超时、连接重置、限流）导致服务不稳定

## 解决方案
指数退避 + 超时控制 + 连接池复用

```javascript
async function fetchWithRetry(url, options = {}, maxRetries = 3) {
  const { retryDelay = 1000, timeout = 30000 } = options;
  
  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), timeout);
      const response = await fetch(url, { ...options, signal: controller.signal });
      clearTimeout(timeoutId);
      
      if (response.status === 429 || response.status >= 500) {
        await new Promise(r => setTimeout(r, retryDelay * Math.pow(2, attempt)));
        continue;
      }
      return response;
    } catch (err) {
      if (attempt === maxRetries) throw err;
      await new Promise(r => setTimeout(r, retryDelay * Math.pow(2, attempt)));
    }
  }
}
```
