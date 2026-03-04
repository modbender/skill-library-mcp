<span id="9mPKUb0F"></span>
# 接口简介
即梦视频3.0 —— 即梦同源的文生视频能力，专业级视频生成引擎，释放无限创意。 准确遵循复杂指令，视觉表达流畅一致，支持1080P高清渲染，更可驾驭多元艺术风格，在视频生成质量出色的基础上，是**生成效果与速度兼备的高性价比之选。**
本文档重点阐述1080P\-图生视频\-首尾帧的接口说明。
<span id="D1UV2r97"></span>
# 接入说明
<span id="plK33lpy"></span>
## 请求说明

|名称 |内容 |
|---|---|
|接口地址 |[https://visual.volcengineapi.com](https://visual.volcengineapi.com/) |
|请求方式 |POST |
|Content\-Type |application/json |

<span id="HSsnRLXY"></span>
## 提交任务
<span id="Y0S0UlPo"></span>
### **提交任务请求参数**
<span id="66smsXtJ"></span>
#### **Query参数**
:::tip 拼接到url后的参数，示例：[https://visual.volcengineapi.com?Action=CVSync2AsyncSubmitTask&Version=2022-08-31](https://visual.volcengineapi.com?Action=CVSync2AsyncSubmitTask&Version=2022-08-31)

:::
|参数 |类型 |**可选/必选** |说明 |
|---|---|---|---|
|Action |string |必选 |接口名，取值：**CVSync2AsyncSubmitTask** |
|Version |string |必选 |版本号，取值：2022\-08\-31 |

<span id="oVa5CMFw"></span>
#### **Header参数**
:::warning
本服务固定值：**Region为cn\-north\-1，Service为cv**
:::
主要用于鉴权，详见 [公共参数](https://www.volcengine.com/docs/6369/67268) \- 签名参数 \- 在Header中的场景部分
<span id="npsYDnjU"></span>
#### **Body参数**
:::warning
业务请求参数，放到request.body中，MIME\-Type为**application/json**

:::
|参数 |类型 |**可选/必选** |说明 |
|---|---|---|---|
|req_key |string |必选 |服务标识|\
| | | |取固定值: **jimeng_i2v_first_tail_v30_1080** |
|binary_data_base64 |array of string |必选（二选一） |图片文件base64编码，请输入2张图片，仅支持JPEG、PNG格式；|\
| | | |注意：|\
| | | ||\
| | | |* 图片文件大小：最大 4.7MB；|\
| | | |* 图片分辨率：最大 4096 \* 4096，最短边不低于320；|\
| | | |* 图片长边与短边比例在3以内；|\
| | | |* 尾帧图片需与首帧图片比例相同。 |
|image_urls |^^|^^|图片文件URL，请输入2张图片|\
| | | |注意：|\
| | | ||\
| | | |* 图片长边与短边比例在3以内；|\
| | | |* 尾帧图片需与首帧图片比例相同。 |
|prompt |string |必选 |用于生成视频的提示词 ，中英文均可输入。建议在400字以内，不超过800字，prompt过长有概率出现效果异常或不生效 |
|seed |int |可选 |随机种子，作为确定扩散初始状态的基础，默认\-1（随机）。若随机种子为相同正整数且其他参数均一致，则生成视频极大概率效果一致|\
| | | |默认值：\-1 |
|frames |int |可选 |生成的总帧数（帧数 = 24 \* n + 1，其中n为秒数，支持5s、10s）|\
| | | |可选取值：[121, 241]|\
| | | |默认值：121 |

<span id="rmtQPEW8"></span>
### 提交任务返回参数
<span id="qS3pUYO3"></span>
#### **通用返回参数**
请参考[通用返回字段及错误码](https://www.volcengine.com/docs/6444/69728)
<span id="ByWr3XtV"></span>
#### **业务返回参数**
:::tip 重点关注data中以下字段，其他字段为公共返回(可忽略或不做解析)

:::
|字段 |类型 |说明 |
|---|---|---|
|task_id |string |任务ID，用于查询结果 |

<span id="yDdSmrIN"></span>
### 提交任务请求&返回完整示例
**请求示例：**
```JSON
{
    "req_key": "jimeng_i2v_first_tail_v30_1080",
    // "binary_data_base64": [],
    "image_urls": [
        "https://xxx",
        "https://xxx"
    ],
    "prompt": "千军万马",
    "seed": -1,
    "frames": 121
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

<span id="j37eSupM"></span>
## 查询任务
<span id="MPdtb8Mv"></span>
### **查询任务请求参数**
<span id="uqX4tU3z"></span>
#### **Query参数**
:::tip 拼接到url后的参数，示例：[https://visual.volcengineapi.com](https://visual.volcengineapi.com/)[?Action=CVSync2AsyncGetResult&Version=2022-08-31](https://visual.volcengineapi.com?Action=CVGetResult&Version=2022-08-31)

:::
|参数 |类型 |**可选/必选** |说明 |
|---|---|---|---|
|Action |string |必选 |接口名，固定值：**CVSync2AsyncGetResult** |
|Version |string |必选 |版本号，固定值：**2022\-08\-31** |

<span id="3XiOwNGw"></span>
#### **Header参数**
:::warning
本服务固定值：**Region为cn\-north\-1，Service为cv**
:::
主要用于鉴权，详见 [公共参数](https://www.volcengine.com/docs/6369/67268) \- 签名参数 \- 在Header中的场景部分
<span id="t81TZuWw"></span>
#### **Body参数**
:::warning
业务请求参数，放到request.body中，MIME\-Type为**application/json**

:::
|参数 |类型 |**可选/必选** |说明 | |
|---|---|---|---|---|
|req_key |string |必选 |服务标识| |\
| | | |取固定值: **jimeng_i2v_first_tail_v30_1080** | |
|task_id |string |必选 |任务ID，此字段的取值为**提交任务接口**的返回 | |
|req_json |json string |可选 |json序列化后的字符串,目前支持隐性水印配置，可在返回结果中添加 |示例："{\"aigc_meta\": {\"content_producer\": \"xxxxxx\", \"producer_id\": \"xxxxxx\", \"content_propagator\": \"xxxxxx\", \"propagate_id\": \"xxxxxx\"}}" |

<span id="Jwdwyt1o"></span>
##### **ReqJson(序列化后的结果再赋值给req_json)**
配置信息

|**参数** |**类型** |**可选/必选** |**说明** | |
|---|---|---|---|---|
|aigc_meta |AIGCMeta |可选 |隐式标识 |隐式标识验证方式：|\
| | | | ||\
| | | | |https://www.gcmark.com/web/index.html#/mark/check/video|\
| | | | |   验证，先注册帐号 上传打标后的视频 点击开始检测 输出检测结果如下图即代表成功|\
| | | | ||\
| | | | |<div style="text-align: center">|\
| | | | |<img src="https://portal.volccdn.com/obj/volcfe/cloud-universal-doc/upload_37d8115b3de900fec9b697787ea51d86.png" width="2362px" /></div>|\
| | | | | |

<span id="gJWywfkM"></span>
##### AIGCMeta
隐式标识，依据《人工智能生成合成内容标识办法》&《网络安全技术人工智能生成合成内容标识方法》

|名称 |类型 |**可选/必选** |描述 |
|---|---|---|---|
|content_producer |string |可选 |内容生成服务ID（长度 <= 256字符） |
|producer_id |string |必选 |内容生成服务商给此图片数据的唯一ID（长度 <= 256字符） |
|content_propagator |string |必选 |内容传播服务商ID（长度 <= 256字符） |
|propagate_id |string |可选 |传播服务商给此图片数据的唯一ID（长度 <= 256字符） |

<span id="9XM8SbTx"></span>
### 查询任务返回参数
<span id="nEfQ9fCb"></span>
#### **通用返回参数**
请参考[通用返回字段及错误码](https://www.volcengine.com/docs/6444/69728)
<span id="BauLP5aJ"></span>
#### **业务返回参数**
:::tip
重点关注data中以下字段，其他字段为公共返回(可忽略或不做解析)

:::
|参数名 |类型 | |
|---|---|---|
|video_url |string |生成的视频URL（有效期为 1 小时） |
|aigc_meta_tagged |bool |隐式标识是否打标成功 |
|status |string |任务执行状态|\
| | ||\
| | |* in_queue：任务已提交|\
| | |* generating：任务已被消费，处理中|\
| | |* done：处理完成，成功或者失败，可根据外层code&message进行判断|\
| | |* not_found：任务未找到，可能原因是无此任务或任务已过期(12小时)|\
| | |* expired：任务已过期，请尝试重新提交任务请求 |

<span id="mRk5rFX2"></span>
### 查询任务请求&返回完整示例
**请求示例：**
```JSON
{
    "req_key": "jimeng_i2v_first_tail_v30_1080",
    "task_id": "7491596536074305586",
    "req_json": "{\"aigc_meta\": {\"content_producer\": \"001191440300192203821610000\", \"producer_id\": \"producer_id_test123\", \"content_propagator\": \"001191440300192203821610000\", \"propagate_id\": \"propagate_id_test123\"}}"
}
```

**返回示例：**
```JSON
{
    "code": 10000, //状态码，优先判断 code=10000, 然后再判断data.status，否则解析有可能会panic
    "data": {
        "aigc_meta_tagged": true,
        "status": "done", //任务状态
        "video_url": "https://xxxx"
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

<span id="okkRkkEK"></span>
## 错误码
<span id="2tLl3yeL"></span>
### **通用错误码**
请参考[通用返回字段及错误码](https://www.volcengine.com/docs/6444/69728)
<span id="oDhNfcW3"></span>
### **业务错误码**

|HttpCode |错误码 |错误消息 |描述 |是否需要重试 |
|---|---|---|---|---|
|200 |10000 |无 |请求成功 |不需要 |
|400 |50411 |Pre Img Risk Not Pass |输入图片前审核未通过 |不需要 |
|400 |50511 |Post Img Risk Not Pass |输出图片后审核未通过 |可重试 |
|400 |50412 |Text Risk Not Pass |输入文本前审核未通过 |不需要 |
|400 |50512 |Post Text Risk Not Pass |输出文本后审核未通过 |不需要 |
|400 |50413 |Post Text Risk Not Pass |输入文本含敏感词、版权词等审核不通过 |不需要 |
|400 |50516 | Post Video Risk Not Pass |输出视频后审核未通过 |可重试 |
|400 |50517 |Post Audio Risk Not Pass |输出音频后审核未通过 |可重试 |
|400 |50518 |Pre Img Risk Not Pass: Copyright |输入版权图前审核未通过 |不需要 |
|400 |50519 |Post Img Risk Not Pass: Copyright |输出版权图后审核未通过 |可重试 |
|400 |50520 |Risk Internal Error |审核服务异常 |不需要 |
|400 |50521 |Antidirt Internal Error |版权词服务异常 |不需要 |
|400 |50522 |Image Copyright Internal Error |版权图服务异常 |不需要 |
|429 |50429 |Request Has Reached API Limit, Please Try Later |QPS超限 |可重试 |
|429 |50430 |Request Has Reached API Concurrent Limit, Please Try Later |并发超限 |可重试 |
|500 |50500 |Internal Error |内部错误 |可重试 |
|500 |50501 |Internal RPC Error |内部算法错误 |可重试 |

&nbsp;
<span id="tgL3yjY2"></span>
## 接入说明
<span id="Wtv3562x"></span>
### SDK使用说明
请参考[SDK使用说明](https://www.volcengine.com/docs/6444/1340578)
<span id="SbFNP6RA"></span>
### HTTP方式接入说明
请参考[HTTP请求示例](https://www.volcengine.com/docs/6444/1390583)


