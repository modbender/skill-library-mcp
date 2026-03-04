<span id="EWtUCSbp"></span>
# 接口简介
动作模仿2.0 —— 新一代视频动作模仿大模型，输入一张图片和一段模版视频，可以将图片中的人物按照模版视频的动作/表情/口型驱动起来，主体及背景特征与输入图片保持一致。
相较于前一代模型，2.0支持了多人驱动，能够更好地保持图片画幅、原始姿态、特征等信息，具有更好的视觉表现，同时2.0也首次支持了非真人驱动视频。整体效果更好，适用场景更多。
<span id="H6Bt6Lbu"></span>
# 接入说明
<span id="VCIHbqCv"></span>
## 输入输出限制说明
<span id="jn2GYvP5"></span>
## 
|输入/输出 |文件类型 |限制说明 |
|---|---|---|
|入参 |图片+视频 |1. 输入的视频时长不可超过30s，支持mp4、mov、webm格式，视频分辨率须是200✖️200或以上，2K以内（2048✖️1440）|\
| | |2. 图片格式支持 jpeg 、jpg 、png ，分辨率需在 480✖️480 以上，1920✖️1080 以内（超出此大小会被等比例缩小），图片大小 4.7M 以下|\
| | |3. 同时支持人脸表情和肢体动作驱动，支持从全身、半身到肖像的全画幅驱动|\
| | |4. 驱动源：视频（支持真人、动漫、宠物）|\
| | |5. 驱动范围：全脸+肢体|\
| | |6. 图片支持真人、动漫、宠物等的驱动；过于抽象的主体可能会生成失败 |
|出参 |视频 |1. 输出视频为驱动后的图片视频，输出视频画面比例会尽量贴近输入图片，但不一定完全一致|\
| | |2. RTF约为18，即生成10秒钟的视频大约需要180秒左右，如遇到服务高峰耗时会增加|\
| | |3. 输出视频格式为mp4，视频分辨率为720P，25fps |

&nbsp;
<span id="mFhUhwJ0"></span>
## 请求说明

|名称 |内容 |
|---|---|
|接口地址 |[https://visual.volcengineapi.com](https://visual.volcengineapi.com/) |
|请求方式 |POST |
|Content\-Type |application/json |

<span id="6SmjCF9o"></span>
## 提交任务
<span id="kY4CgcU3"></span>
### **提交任务请求参数**
<span id="Pp0Pof2k"></span>
#### **Query参数**
:::tip 拼接到url后的参数，示例：[https://visual.volcengineapi.com?Action=CVSync2AsyncSubmitTask&Version=2022-08-31](https://visual.volcengineapi.com?Action=CVSync2AsyncSubmitTask&Version=2022-08-31)

:::
|参数 |类型 |**可选/必选** |说明 |
|---|---|---|---|
|Action |string |必选 |接口名，取值：**CVSync2AsyncSubmitTask** |
|Version |string |必选 |版本号，取值：2022\-08\-31 |

<span id="JBkRbI9Z"></span>
#### **Header参数**
:::warning
本服务固定值：**Region为cn\-north\-1，Service为cv**
:::
主要用于鉴权，详见 [公共参数](https://www.volcengine.com/docs/6369/67268) \- 签名参数 \- 在Header中的场景部分
<span id="7EMowymz"></span>
#### **Body参数**
:::warning
业务请求参数，放到request.body中，MIME\-Type为**application/json**

:::
|参数 |类型 |**可选/必选** |说明 |
|---|---|---|---|
|req_key |string |必选 |服务标识|\
| | | |取固定值: **jimeng_dreamactor_m20_gen_video** |
|binary_data_base64 |array of string |必选（二选一） |图片文件base64编码，需输入**1**张图片 |
|image_urls |array of string |^^|图片文件URL，需输入**1**张图片（需公网可访问） |
|video_url |string |必选 |视频URL（需公网可访问） |
|cut_result_first_second_switch |bool |可选 |是否裁剪结果视频的第1秒（结果视频的开头会存在1秒的过度视频，支持通过此参数进行裁剪）|\
| | | |默认值：true |
|callback_url |string |可选 |回调接口URL（需公网可访问） |

<span id="5gmcnUDX"></span>
### 提交任务返回参数
<span id="FFReGo8g"></span>
#### **通用返回参数**
请参考[通用返回字段及错误码](https://www.volcengine.com/docs/6444/69728)
<span id="mFPlGJ2R"></span>
#### **业务返回参数**
:::tip 重点关注data中以下字段，其他字段为公共返回(可忽略或不做解析)

:::
|字段 |类型 |说明 |
|---|---|---|
|task_id |string |任务ID，用于查询结果 |

<span id="8Y2fEV5K"></span>
### 提交任务请求&返回完整示例
**请求示例：**
```JSON
{
    "req_key": "jimeng_dreamactor_m20_gen_video",
    // "binary_data_base64": [],
    "image_urls": [
        "https://xxxx"
    ],
    "video_url": "https://xxxx"
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

<span id="3EwXjeDd"></span>
## 查询任务
<span id="xqMfgX1Z"></span>
### **查询任务请求参数**
<span id="YHwJ9zS9"></span>
#### **Query参数**
:::tip 拼接到url后的参数，示例：[https://visual.volcengineapi.com](https://visual.volcengineapi.com/)[?Action=CVSync2AsyncGetResult&Version=2022-08-31](https://visual.volcengineapi.com?Action=CVGetResult&Version=2022-08-31)

:::
|参数 |类型 |**可选/必选** |说明 |
|---|---|---|---|
|Action |string |必选 |接口名，固定值：**CVSync2AsyncGetResult** |
|Version |string |必选 |版本号，固定值：**2022\-08\-31** |

<span id="rmLP19yL"></span>
#### **Header参数**
:::warning
本服务固定值：**Region为cn\-north\-1，Service为cv**
:::
主要用于鉴权，详见 [公共参数](https://www.volcengine.com/docs/6369/67268) \- 签名参数 \- 在Header中的场景部分
<span id="qFSxDUnM"></span>
#### **Body参数**
:::warning
业务请求参数，放到request.body中，MIME\-Type为**application/json**

:::
|参数 |类型 |**可选/必选** |说明 | |
|---|---|---|---|---|
|req_key |string |必选 |服务标识| |\
| | | |取固定值: **jimeng_dreamactor_m20_gen_video** | |
|task_id |string |必选 |任务ID，此字段的取值为**提交任务接口**的返回 | |
|req_json |json string |可选 |json序列化后的字符串,目前支持隐性水印配置，可在返回结果中添加 |示例："{\"aigc_meta\": {\"content_producer\": \"xxxxxx\", \"producer_id\": \"xxxxxx\", \"content_propagator\": \"xxxxxx\", \"propagate_id\": \"xxxxxx\"}}" |

<span id="cVulQ4GW"></span>
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

<span id="wIHcZ4Qo"></span>
##### AIGCMeta
隐式标识，依据《人工智能生成合成内容标识办法》&《网络安全技术人工智能生成合成内容标识方法》

|名称 |类型 |**可选/必选** |描述 |
|---|---|---|---|
|content_producer |string |可选 |内容生成服务ID（长度 <= 256字符） |
|producer_id |string |必选 |内容生成服务商给此图片数据的唯一ID（长度 <= 256字符） |
|content_propagator |string |必选 |内容传播服务商ID（长度 <= 256字符） |
|propagate_id |string |可选 |传播服务商给此图片数据的唯一ID（长度 <= 256字符） |

<span id="X6CjrV3f"></span>
### 查询任务返回参数
<span id="yKRh67Lb"></span>
#### **通用返回参数**
请参考[通用返回字段及错误码](https://www.volcengine.com/docs/6444/69728)
<span id="1P9uIpCA"></span>
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

<span id="D1ZDQjnm"></span>
### 查询任务请求&返回完整示例
**请求示例：**
```JSON
{
    "req_key": "jimeng_dreamactor_m20_gen_video",
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

<span id="UAAkhqpL"></span>
## 回调返回说明
<span id="fLFYdFgU"></span>
#### **通用返回参数**
请参考[通用返回字段及错误码](https://www.volcengine.com/docs/6444/69728)
<span id="rSaIS8Ab"></span>
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

**返回示例：**
```JSON
{
        "code": 10000, //状态码，优先判断 code=10000, 然后再判断data.status，否则解析有可能会panic
        "task_id": "1016263xxxxx45545367",  // 任务ID
        "message": "Success",
        "data": {
                "video_url": "https://xxxx",
                "resp_data": "",
                "aigc_meta_tagged": false,
                "status": "done"//任务状态
        },
        "request_id": "202601221406585EE1349D09B",//排查错误的关键信息
        "time_elapsed": "131.518771ms",
        "status": 10000 //无需关注，请忽略
}
```

**返回报错示例：**
```JSON
{
        "code": 50215,  //状态码
        "task_id": "1016263xxxxx45545367",  // 任务ID
        "message": "Input invalid for this service.", //错误信息
        "data": {
                "resp_data": ""
        },
        "request_id": "20260122141710E69441A0883C66BBE1",//排查错误的关键信息
        "time_elapsed": "10.974197ms",//链路耗时
        "status": 50215 //无需关注，请忽略
}
```

<span id="A0ITGPnn"></span>
## 错误码
<span id="5VsyTURA"></span>
### **通用错误码**
请参考[通用返回字段及错误码](https://www.volcengine.com/docs/6444/69728)
<span id="7AyAbgdc"></span>
### **业务错误码**

|HttpCode |错误码 |错误消息 |描述 |是否需要重试 |
|---|---|---|---|---|
|200 |10000 |无 |请求成功 |不需要 |
|400 |50411 |Pre Img Risk Not Pass |输入图片前审核未通过 |不需要 |
|400 |50511 |Post Img Risk Not Pass |输出图片后审核未通过 |可重试 |
|400 |50412 |Text Risk Not Pass |输入文本前审核未通过 |不需要 |
|400 |50512 |Post Text Risk Not Pass |输出文本后审核未通过 |不需要 |
|400 |50513 |Pre Video Risk Not Pass |输入视频前审核未通过 |不需要 |
|400 |50514 |Pre Audio Risk Not Pass |输入音频前审核未通过 |不需要 |
|400 |50413 |Post Text Risk Not Pass |输入文本含敏感词、版权词等审核不通过 |不需要 |
|429 |50429 |Request Has Reached API Limit, Please Try Later |QPS超限 |可重试 |
|429 |50430 |Request Has Reached API Concurrent Limit, Please Try Later |并发超限 |可重试 |
|500 |50500 |Internal Error |内部错误 |可重试 |
|500 |50501 |Internal RPC Error |内部算法错误 |可重试 |

<span id="R5va1n8t"></span>
## 接入说明
<span id="inZmOrMd"></span>
### SDK使用说明
请参考[SDK使用说明](https://www.volcengine.com/docs/6444/1340578)
<span id="mXfppZ88"></span>
### HTTP方式接入说明
请参考[HTTP请求示例](https://www.volcengine.com/docs/6444/1390583)


