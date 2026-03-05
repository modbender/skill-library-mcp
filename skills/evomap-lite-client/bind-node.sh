#!/bin/bash
# 绑定节点到账户的脚本
# 使用方法：bash bind-node.sh <node_id>

NODE_ID=${1:-node_70e247c67b06eec9}

echo "📌 准备绑定节点：$NODE_ID"
echo ""
echo "请按以下步骤操作："
echo ""
echo "1. 访问 EvoMap 网站："
echo "   https://evomap.ai"
echo ""
echo "2. 登录你的账户"
echo ""
echo "3. 访问账户设置页面："
echo "   https://evomap.ai/account/settings"
echo ""
echo "4. 找到 'Connected Agents' 或 'My Nodes' 部分"
echo ""
echo "5. 点击 'Add Node' 或 'Bind Agent' 按钮"
echo ""
echo "6. 输入节点 ID："
echo "   $NODE_ID"
echo ""
echo "7. 确认绑定"
echo ""
echo "绑定完成后，运行以下命令验证："
echo "  curl -s 'https://evomap.ai/a2a/nodes/$NODE_ID' | python3 -m json.tool"
echo ""
echo "如果看到 \"owner_user_id\" 是你的用户 ID，说明绑定成功！"
