<span id="iYs82pIr"></span>
# 接口简介
用于识别图片中是否包含人、类人、拟人等主体。
<span id="RggU0CpI"></span>
# 接入说明
<span id="m9jyyRCY"></span>
## 请求说明

|名称 |内容 |
|---|---|
|接口地址 |[https://visual.volcengineapi.com](https://visual.volcengineapi.com/) |
|请求方式 |POST |
|Content\-Type |application/json |

<span id="Wqosauyg"></span>
## 提交任务
<span id="UipBJfMe"></span>
### **提交任务请求参数**
**Query参数**
:::tip 拼接到url后的参数，示例：[https://visual.volcengineapi.com?Action=CVSubmitTask&Version=2022-08-31](https://visual.volcengineapi.com?Action=CVSubmitTask&Version=2022-08-31)

:::
|参数 |类型 |**可选/必选** |说明 |
|---|---|---|---|
|Action |string |必选 |接口名，取值：**CVSubmitTask** |
|Version |string |必选 |版本号，取值：2022\-08\-31 |

<span id="UL1JJkrl"></span>
#### **Header参数**
:::warning
本服务固定值：**Region为cn\-north\-1，Service为cv**
:::
主要用于鉴权，详见 [公共参数](https://www.volcengine.com/docs/6369/67268) \- 签名参数 \- 在Header中的场景部分
<span id="lKGawgyP"></span>
#### **Body参数**
:::warning
业务请求参数，放到request.body中，MIME\-Type为**application/json**

:::
|名称 |类型 |必选 |描述 |
|---|---|---|---|
|req_key |string |必选 |服务标识|\
| | | |取固定值: **jimeng_realman_avatar_picture_create_role_omni_v15** |
|image_url |string |必选 |人像图片URL链接 |

<span id="gLk9V4gc"></span>
### 提交任务返回参数
<span id="aCU4u8so"></span>
#### **通用返回参数**
请参考[通用返回字段及错误码](https://www.volcengine.com/docs/6444/69728)
<span id="hDOjda2V"></span>
#### **业务返回参数**
:::tip 重点关注data中以下字段，其他字段为公共返回(可忽略或不做解析)

:::
|字段 |类型 |说明 |
|---|---|---|
|task_id |string |任务ID，用于查询结果 |

<span id="EhE6lncW"></span>
### 提交任务请求&返回完整示例
**请求示例：**
```JSON
{
    "req_key": "jimeng_realman_avatar_picture_create_role_omni_v15",
    "image_url": "https://xxxxx"
}
```

**返回示例：**
```JSON
{
    "code": 10000, //状态码，判断状态，code!=10000的情况下，不会返回task_id
    "data": {
        "task_id": "7392616336519610409" //任务ID，查询接口使用
    },
    "message": "Success",
    "request_id": "20240720103939AF0029465CF6A74E51EC", //排查错误的关键信息
    "time_elapsed": "104.852309ms" //链路耗时
}
```

<span id="Kkpl7tcr"></span>
## 查询任务
<span id="2w0vDyP6"></span>
### **查询任务请求参数**
<span id="9T59GUSD"></span>
#### **Query参数**
:::tip 拼接到url后的参数，示例：[https://visual.volcengineapi.com](https://visual.volcengineapi.com/)[?Action=CVGetResult&Version=2022-08-31](https://visual.volcengineapi.com?Action=CVGetResult&Version=2022-08-31)

:::
|参数 |类型 |**可选/必选** |说明 |
|---|---|---|---|
|Action |string |必选 |接口名，固定值：**CVGetResult** |
|Version |string |必选 |版本号，固定值：**2022\-08\-31** |

<span id="2fbkyXAl"></span>
#### **Header参数**
:::warning
本服务固定值：**Region为cn\-north\-1，Service为cv**
:::
主要用于鉴权，详见 [公共参数](https://www.volcengine.com/docs/6369/67268) \- 签名参数 \- 在Header中的场景部分
<span id="5V2lUETO"></span>
#### **Body参数**
:::warning
业务请求参数，放到request.body中，MIME\-Type为**application/json**

:::
|参数 |类型 |可选/必选 |说明 |
|---|---|---|---|
|req_key |string |必选 |服务标识|\
| | | |取固定值: **jimeng_realman_avatar_picture_create_role_omni_v15** |
|task_id |string |必选 |任务ID，此字段的取值为**提交任务接口**的返回 |

<span id="nf5sT273"></span>
### 查询任务返回参数
<span id="XnVX9EJr"></span>
#### **通用返回参数**
请参考[通用返回字段及错误码](https://www.volcengine.com/docs/6444/69728)
<span id="oeCO0r2h"></span>
#### **业务返回参数**
:::tip
重点关注data中以下字段，其他字段为公共返回(可忽略或不做解析)

:::
|参数名 |参数说明 |参数示例 |
|---|---|---|
|resp_data |图片识别结果| |\
| |resp_data为序列化后的JSON字符串，其中的**status**参数为识别结果，取值为：| |\
| || |\
| |* 0：不包含人、类人、拟人等主体| |\
| |* 1：包含人、类人、拟人等主体 | |
|status |任务执行状态| |\
| || |\
| |* in_queue：任务已提交| |\
| |* generating：任务已被消费，处理中| |\
| |* done：处理完成，成功或者失败，可根据外层code&message进行判断| |\
| |* not_found：任务未找到，可能原因是无此任务或任务已过期(12小时)| |\
| |* expired：任务已过期，请尝试重新提交任务请求 | |

<span id="VrIpS7DD"></span>
### 查询任务请求&返回完整示例
**请求示例：**
```JSON
{
    "req_key": "jimeng_realman_avatar_picture_create_role_omni_v15",
    "task_id": "<任务提交接口返回task_id>"
}
```

**返回示例：**
```JSON
{
    "code": 10000, //状态码，优先判断 code=10000, 然后再判断data.status，否则解析有可能会panic
    "data": {
        "resp_data":"{\"status\":1}",
        "status": "done" //任务状态
    },
    "message": "Success",
    "status": 10000,  //无需关注，请忽略
    "request_id": "2025061718460554C9B78D23B0BAB45B2A",  //排查错误的关键信息
    "time_elapsed": "508.312154ms" //链路耗时
}
```

**返回报错示例：**
```JSON
{
    "code": 50413, //状态码，优先判断 code=10000, 然后再判断data.status，否则解析有可能会panic
    "data": null, //code!=10000的情况下，该字段返回为null
    "message": "Post Text Risk Not Pass", //错误信息
    "request_id": "202511281418218670D408837A9B0EB58F", //排查错误的关键信息
    "status": 50413, //无需关注，请忽略
    "time_elapsed": "36.799829ms" //链路耗时
}
```

<span id="tsSGEop2"></span>
## 错误码
<span id="NPBaYTGD"></span>
### **通用错误码**
请参考[通用返回字段及错误码](https://www.volcengine.com/docs/6444/69728)
<span id="yDjYXE2j"></span>
### **业务错误码**

|HttpCode |错误码 |错误消息 |描述 |是否需要重试 |
|---|---|---|---|---|
|200 |10000 |无 |请求成功 |不需要 |
|400 |50411 |Pre Img Risk Not Pass |输入图片前审核未通过 |不需要 |
|400 |50511 |Post Img Risk Not Pass |输出图片后审核未通过 |可重试 |
|400 |50412 |Text Risk Not Pass |输入文本前审核未通过 |不需要 |
|400 |50512 |Post Text Risk Not Pass |输出文本后审核未通过 |不需要 |
|400 |50413 |Post Text Risk Not Pass |输入文本含敏感词、版权词等审核不通过 |不需要 |
|429 |50429 |Request Has Reached API Limit, Please Try Later |QPS超限 |可重试 |
|429 |50430 |Request Has Reached API Concurrent Limit, Please Try Later |并发超限 |可重试 |
|500 |50500 |Internal Error |内部错误 |可重试 |
|500 |50501 |Internal RPC Error |内部算法错误 |可重试 |

&nbsp;
<span id="Cso1U6US"></span>
## 接入说明
<span id="ahROYmp4"></span>
### SDK使用说明
请参考[SDK使用说明](https://www.volcengine.com/docs/6444/1340578)
<span id="VmneJSlh"></span>
### HTTP方式接入说明
请参考[HTTP请求示例](https://www.volcengine.com/docs/6444/1390583)
&nbsp;


