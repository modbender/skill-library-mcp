#!/bin/bash

# 橙丁物联液位传感器状态查询脚本

KEY="你的KEY"
TEL="你的手机号"
IMEI="你的IMEI"
URL="https://www.cd6969.com/admin.php?s=/Admin/ApiV2/getList.html"

response=$(curl -s -X POST "$URL" \
  -H "Content-Type: application/json" \
  -d "{\"key\":\"$KEY\",\"tel\":\"$TEL\"}")

echo "$response" | jq -r --arg imei "D$IMEI" '
  if .code == 100 and .data[$imei] then
    .data[$imei]
  else
    {error: "设备未找到或API错误", code: .code}
  end
'
