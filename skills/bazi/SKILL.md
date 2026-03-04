---
name: bazi
description: 计算八字以及大运流年信息，需要性别， ISO 8601 格式的时间两个参数
---

凡心八字官网

http://bagezi.top/

252468400@qq.com

# 使用方法

必须设置utf-8编码后运行

## 只提供必填参数（name 使用默认值"张三"）

python paipan.py -gender "男" -birthday_str "1997-01-12T23:07:19.083Z"

## 提供所有参数

python paipan.py -name "李四" -gender "女" -birthday_str "1990-05-20T10:00:00.000Z"

## 参数位置绑定（按顺序）

python paipan.py "王五" "男" "1985-08-15T00:00:00.000Z"
