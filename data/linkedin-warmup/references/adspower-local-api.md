# AdsPower Local API（本 skill 仅用到的部分）

Base URL（常见）：`http://127.0.0.1:50325`

鉴权：
- Header: `Authorization: Bearer API_KEY`（API_KEY 用实际值替换）

## 启动浏览器（Open Browser）

GET `/api/v1/browser/start?user_id=USER_ID`（USER_ID 用实际值替换）

常用可选参数：
- `open_tabs=0`：不打开历史 tab
- `ip_tab=0`：不打开 IP 检测页
- `headless=0`：可视化
- `launch_args=["--remote-debugging-port=30001"]`：指定 CDP/DevTools 端口（需 URL 编码）

返回（示例字段）：
- `data.debug_port`：实际调试端口
- `data.ws.puppeteer`：puppeteer ws 地址

## 关闭浏览器（Close Browser）

GET `/api/v1/browser/stop?user_id=USER_ID`（USER_ID 用实际值替换）

## 备注

- AdsPower 接口本身不一定提供单独的 `cdp_port` 参数；一般通过 `launch_args` 传 Chrome 启动参数来控制调试端口。
- 如果端口被占用，可能启动失败或端口被改写；以 `data.debug_port` 为准。
