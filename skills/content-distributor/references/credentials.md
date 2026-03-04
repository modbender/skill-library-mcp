# 凭据配置指南

## 平台限制

### 知乎
- **图片上传**: ⚠️ 知乎图片上传 API 有严格的防爬机制，目前无法通过脚本上传图片。如需发布带图想法，请手动在知乎 App/网页编辑添加。
- **审核**: 发布后通常会显示"待审核·仅自己可见"，审核通过后自动公开。

### 豆瓣
- ⚠️ **仅支持国内 IP**，海外服务器无法直接访问 API
- 需要国内代理或在本地浏览器操作

### 微博
- 待测试

---

## 凭据文件位置

所有敏感信息存储在 `~/clawd/secrets/content-distributor.json`

**安全提醒：**
- 此文件已在 .gitignore 中排除
- 请勿手动提交此文件
- 定期更新过期的 Cookie

## 凭据结构

```json
{
  "zhihu": {
    "cookies": {
      "z_c0": "your_z_c0_cookie",
      "_xsrf": "your_xsrf_token"
    },
    "user_agent": "Mozilla/5.0 ..."
  },
  "douban": {
    "cookies": {
      "dbcl2": "your_dbcl2_cookie",
      "ck": "your_ck_token"
    },
    "user_agent": "Mozilla/5.0 ..."
  },
  "weibo": {
    "cookies": {
      "SUB": "your_sub_cookie"
    },
    "user_agent": "Mozilla/5.0 ..."
  }
}
```

## 验证凭据

发帖前可以先验证凭据是否有效：

**知乎：**
```bash
curl -s "https://www.zhihu.com/api/v4/me" \
  -H "Cookie: z_c0=YOUR_Z_C0; _xsrf=YOUR_XSRF"
```
返回用户信息 = 有效，返回 401 = 过期

**豆瓣：**
```bash
curl -s -I "https://www.douban.com/mine/" \
  -H "Cookie: dbcl2=YOUR_DBCL2; ck=YOUR_CK"
```
返回 200 = 有效，返回 302 重定向到登录 = 过期
（注意：豆瓣对海外 IP 有限制，即使凭据有效也可能失败）

## 获取 Cookie 的步骤

### 知乎

1. 在浏览器中登录 zhihu.com
2. 打开开发者工具 (F12) → Application → Cookies
3. 复制 `z_c0` 和 `_xsrf` 的值
4. 运行 `python3 scripts/configure.py --platform zhihu`
5. 按提示输入 Cookie 值

### 豆瓣

⚠️ **注意：豆瓣仅支持国内 IP 访问，海外服务器无法直接调用 API**

1. 在浏览器中登录 douban.com
2. 打开开发者工具 (F12) → Application → Cookies
3. 复制 `dbcl2` 和 `ck` 的值
4. 运行 `python3 scripts/configure.py --platform douban`
5. 按提示输入 Cookie 值

如果你的服务器在海外，需要通过国内代理或在本地浏览器中操作。

### 微博

1. 在浏览器中登录 weibo.com
2. 打开开发者工具 (F12) → Application → Cookies
3. 复制 `SUB` 的值
4. 运行 `python3 scripts/configure.py --platform weibo`
5. 按提示输入 Cookie 值

## Cookie 有效期

- **知乎**: 
  - `z_c0`: 约 1-3 个月（主要登录凭证）
  - `_xsrf`: 跟随 session，可能更短
  - 如果浏览器保持登录，会自动续期
- **豆瓣**: 约 1 个月
  - ⚠️ **仅支持国内 IP**，海外服务器无法直接访问
  - 需要国内代理或在本地浏览器操作
- **微博**: 约 1-2 周

当脚本报告认证失败时，请重新配置凭据。

## 安全最佳实践

1. 使用专用账号进行自动化发布
2. 不要使用主账号的 Cookie
3. 定期轮换凭据
4. 监控账号异常登录提醒
