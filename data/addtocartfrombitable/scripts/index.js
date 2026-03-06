// 这是一个完整的逻辑脚本，尝试模拟整个加购流程，包括异常处理
// 目标：解决当前 snapshot 无法准确定位元素的问题
// 策略：优先使用 DOM 遍历和 CSS/XPath 查找，而不是依赖不稳定 snapshot

const { URL } = require('url');

async function process(bitableUrl, options = {}) {
    const { 
        dryRun = false, 
        verbose = true,
        headless = false,
        timeout = 30000 
    } = options;

    console.log(`开始处理: ${bitableUrl}`);

    // 1. 获取 Bitable 数据
    // 假设通过某种方式获取到了 records
    const records = [
        {
            url: "https://detail.tmall.com/item.htm?id=701699369447",
            spec: "62817【一字】3.0x100MM",
            qty: 2
        }
    ];

    for (const record of records) {
        console.log(`Processing: ${record.spec} x ${record.qty}`);
        try {
            await processSingleRecord(record, options);
            console.log(`Success: ${record.spec}`);
        } catch (err) {
            console.error(`Failed: ${record.spec}`, err);
        }
    }
}

async function processSingleRecord(record, options) {
    // 打开页面
    await browser.open({ profile: 'openclaw', targetUrl: record.url });
    await sleep(5000); // Wait for load

    // 尝试点击规格
    // 使用 evaluate 进行更精确的查找
    const clickedSpec = await browser.act({
        profile: 'openclaw',
        request: {
            kind: 'evaluate',
            fn: `(specText) => {
                // 1. 查找包含文本的所有元素
                const xpath = "//*[contains(text(), '" + specText + "')]";
                const result = document.evaluate(xpath, document, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null);
                
                for (let i = 0; i < result.snapshotLength; i++) {
                    const node = result.snapshotItem(i);
                    // 检查是否可见且可点击
                    if (node.offsetParent !== null) {
                        // 尝试向上找 clickable 的父元素 (例如 li, a, div[role=button])
                        let target = node;
                        while (target && target !== document.body) {
                            if (target.tagName === 'A' || target.tagName === 'BUTTON' || target.getAttribute('role') === 'button' || target.className.includes('sku')) {
                                target.click();
                                return true;
                            }
                            target = target.parentElement;
                        }
                        // 如果没找到明显的 clickable 父元素，直接点击文本节点本身
                        node.click();
                        return true;
                    }
                }
                return false;
            }`,
            args: [record.spec]
        }
    });

    if (!clickedSpec.result) {
        throw new Error(`无法找到规格: ${record.spec}`);
    }
    console.log(`规格已点击: ${record.spec}`);
    await sleep(2000);

    // 设置数量
    const setQty = await browser.act({
        profile: 'openclaw',
        request: {
            kind: 'evaluate',
            fn: `(qty) => {
                // 查找数量输入框
                const inputs = document.querySelectorAll('input.text-amount, input.mui-amount-input, input[type=number]');
                for (let input of inputs) {
                    if (input.value) { // 假设默认有值
                        input.value = qty;
                        input.dispatchEvent(new Event('input', { bubbles: true }));
                        input.dispatchEvent(new Event('change', { bubbles: true }));
                        return true;
                    }
                }
                return false;
            }`,
            args: [record.qty]
        }
    });
    
    if (!setQty.result) {
        console.warn("无法设置数量，尝试直接点击加号或忽略");
        // fallback logic...
    } else {
        console.log(`数量已设置为: ${record.qty}`);
    }
    await sleep(1000);

    // 点击加购
    const clickedCart = await browser.act({
        profile: 'openclaw',
        request: {
            kind: 'evaluate',
            fn: `() => {
                // 查找加购按钮
                // 常见类名：J_LinkAdd, add-cart-btn, btn-add-cart
                // 常见文本：加入购物车, 加入购物袋
                
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
        }
    });

    if (!clickedCart.result) {
        throw new Error("无法找到'加入购物车'按钮");
    }
    console.log("加购按钮已点击");
    await sleep(3000);
}

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

// Export for usage
module.exports = { process };
