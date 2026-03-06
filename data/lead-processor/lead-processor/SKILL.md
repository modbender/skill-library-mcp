# Lead Processing Agent

外贸 B2B 线索自动化清洗与分发代理。

## 功能
- 读取飞书多维表格中的客户 URL
- 访问客户官网进行深度分析
- 根据规则进行 A/B/C 分级
- 将结果写入飞书多维表格
- 发送分析报告到飞书群

## 配置
- `FEISHU_APP_ID`
- `FEISHU_APP_SECRET`
- 飞书群 ID (chat_id)
- 多维表格 App Token 和 Table ID

## 分级规则
- A级：终端工厂/制造商（OEM、production line、ISO9001、Request a Quote）
- B级：贸易商/经销商（Distributor、Wholesaler、Warehouse）
- C级：同行/铸件厂（Foundry services、Iron casting service）
