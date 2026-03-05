---
name: addtocartfrombitable
description: 从飞书Bitable表格获取商品信息（链接、规格、数量），然后通过浏览器自动化将其加入天猫/淘宝购物车。触发词：加购物车、Bitable商品、批量加购、采购表格。
tags: [feishu, bitable, shopping, taobao, tmall, browser-automation, add-to-cart]
---

# 从 Bitable 加入购物车

从飞书多维表格读取商品信息，自动添加到淘宝/天猫购物车。

## Bitable 表格要求

默认表格：`https://somo-tech.feishu.cn/base/UIdIbPe2RaOQ1tsNIhlcB5ilngc`
- **app_token:** `UIdIbPe2RaOQ1tsNIhlcB5ilngc`
- **table_id:** `tblwMnggn0CuboHs`

必需字段：
| 字段名 | 类型 | 说明 |
|--------|------|------|
| 链接 | URL | 商品链接（从 `field.link` 取值） |
| 采购规格 | Text | 要选择的规格文本，必须与页面上的规格选项完全匹配 |
| 数量 | Number | 购买数量 |

## 操作流程

### 1. 获取待处理记录

```
feishu_bitable_list_records(app_token, table_id, page_size=20)
```

筛选出有完整 `链接`、`采购规格`、`数量` 的记录。

### 2. 逐个处理商品

对每条记录执行：

#### 2.1 提取信息
- `productUrl` = record.fields.链接.link
- `productSpec` = record.fields.采购规格
- `productQuantity` = record.fields.数量

#### 2.2 打开商品页面
```
browser.open(profile='openclaw', targetUrl=productUrl)
```
等待页面加载完成（约 3-5 秒）。

#### 2.3 使用 evaluate 查找并点击规格
由于页面元素可能动态加载，直接使用 snapshot 可能无法找到。建议优先使用 `evaluate` 查找包含规格文本的元素并点击。

```javascript
browser.act(profile='openclaw', request={
    kind: 'evaluate',
    fn: `(specText) => {
        // XPath 查找包含文本的元素
        const xpath = "//*[contains(text(), '" + specText + "')]";
        const result = document.evaluate(xpath, document, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null);
        for (let i = 0; i < result.snapshotLength; i++) {
            const node = result.snapshotItem(i);
            // 尝试点击，如果失败则向上找 clickable 的父元素
            let target = node;
            while (target && target !== document.body) {
                // 检查常见的可点击标签或属性
                if (['A', 'BUTTON', 'LI'].includes(target.tagName) || target.getAttribute('role') === 'button' || target.className.includes('sku')) {
                    target.click();
                    return true;
                }
                target = target.parentElement;
            }
            // 实在不行点击节点本身
            node.click();
            return true;
        }
        return false;
    }`,
    args: [productSpec]
})
```

#### 2.4 设置数量
同理，使用 evaluate 找到输入框并修改值：
```javascript
browser.act(profile='openclaw', request={
    kind: 'evaluate',
    fn: `(qty) => {
        const inputs = document.querySelectorAll('input.text-amount, input.mui-amount-input, input[type=number]');
        for (let input of inputs) {
             // 简单的启发式规则：value 是 1 或不为空
             if (input.value) {
                input.value = qty;
                input.dispatchEvent(new Event('input', { bubbles: true }));
                input.dispatchEvent(new Event('change', { bubbles: true }));
                return true;
            }
        }
        return false;
    }`,
    args: [productQuantity]
})
```

#### 2.5 点击加入购物车
找到"加入购物车"按钮并点击：
```javascript
browser.act(profile='openclaw', request={
    kind: 'evaluate',
    fn: `() => {
        const buttons = document.querySelectorAll('a, button, div[role=button]');
        for (let btn of buttons) {
            const text = btn.innerText || btn.textContent;
            if (text && (text.includes('加入购物车') || text.includes('加入购物袋'))) {
                btn.click();
                return true;
            }
        }
        return false;
    }`
})
```

#### 2.6 确认添加
等待 2-3 秒，检查是否出现成功提示或购物车数量变化。

### 3. 汇报结果

完成后通过 message 工具发送 Telegram 通知：
```
message(action='send', channel='telegram', to='telegram:1642489086', message='采购商品已加入购物车：\n- 商品1: ✅\n- 商品2: ✅\n...')
```

**改进点：**
- 不再仅依赖 `browser.snapshot` 返回的静态文本 ref，而是利用 `evaluate` 在浏览器上下文中直接执行 DOM 操作，提高对动态页面和复杂结构的适应性。
- 增加了针对规格选择、数量设置和加购按钮的具体 DOM 查找策略。

## 示例调用

用户说："帮我把采购表格里的商品加入购物车"

1. 读取 Bitable 记录
2. 对每个有效记录执行加购流程 (优先使用 evaluate 策略)
3. 汇报结果
