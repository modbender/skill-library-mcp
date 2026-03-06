---
name: coding
description: '1. 创建网页需要先根据拿到的数据设计数据库结构，需要调用工具在数据库中建立结构。
  2.后端接口设计需要考虑现有的数据库结构，接口地址为：https://teamo-dev.floatai.cn/api/engine/generalDataApi，method="post"，入参为{"session_group_id":"$SESSION_GROUP_ID$",
  "collection_name":${表名}}，返回值为{"code":0, "result": {"data": ${JSON数组}}}
  基于上边的接口和字段设计，开发动态html看板。 要求每个图表各自请求一次接口完成渲染，间隔60S轮训接口，实时更新页面。3.
  注意将传给你的数据信息插入到创建好的数据库结构中。'
---


# Coding

## Overview

This skill provides specialized capabilities for coding.

## Instructions

1. 创建网页需要先根据拿到的数据设计数据库结构，需要调用工具在数据库中建立结构。 2.后端接口设计需要考虑现有的数据库结构，接口地址为：https://teamo-dev.floatai.cn/api/engine/generalDataApi，method="post"，入参为{"session_group_id":"$SESSION_GROUP_ID$", "collection_name":${表名}}，返回值为{"code":0, "result": {"data": ${JSON数组}}} 基于上边的接口和字段设计，开发动态html看板。 要求每个图表各自请求一次接口完成渲染，间隔60S轮训接口，实时更新页面。3. 注意将传给你的数据信息插入到创建好的数据库结构中。


## Usage Notes

- This skill is based on the Coding agent configuration
- Template variables (if any) like $DATE$, $SESSION_GROUP_ID$ may require runtime substitution
- Follow the instructions and guidelines provided in the content above
