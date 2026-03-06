<span id="CqWmhbOT"></span>
# 接口简介
OmniHuman1.5（即梦同源数字人模型），该模型可根据用户上传的**单张图片+音频**，生成与图片对应的**视频效果**。支持输入任意画幅包含人物或其他主体（宠物、动漫等）的图片，结合音频，生成高质量的视频。
人物的情绪、动作与音频具有强关联性，支持通过提示词（prompt）对画面、动作、运镜进行调整。同时OmniHuman1.5对动漫、宠物等形象支持较好，允许指定讲话人/主体，可广泛应用于内容表达、唱歌和表演等场景。
相较于上一代模型，OmniHuman1.5 在**运动自然度和结构稳定性**提升明显，在**人物/主体的运动表现力和画面质量上更优。** 可以广泛应用于制作剧情对话、多人对话/对唱、商品交互、漫剧等内容。对比其他视频通用模型，OmniHuman 数字人大模型在**人物/主体的剧情演绎效果**上极具优势。
<span id="Vmnn1XrW"></span>
# 接入说明
<span id="slvinWHY"></span>
## 请求说明

|名称 |内容 |
|---|---|
|接口地址 |[https://visual.volcengineapi.com](https://visual.volcengineapi.com/) |
|请求方式 |POST |
|Content\-Type |application/json |

<span id="L0IW2Ncc"></span>
## 提交任务
<span id="Xfkmq42L"></span>
### **提交任务请求参数**
**Query参数**
:::tip 拼接到url后的参数，示例：[https://visual.volcengineapi.com?Action=CVSubmitTask&Version=2022-08-31](https://visual.volcengineapi.com?Action=CVSubmitTask&Version=2022-08-31)

:::
|参数 |类型 |**可选/必选** |说明 |
|---|---|---|---|
|Action |string |必选 |接口名，取值：**CVSubmitTask** |
|Version |string |必选 |版本号，取值：2022\-08\-31 |

<span id="9bD7KCSs"></span>
#### **Header参数**
:::warning
本服务固定值：**Region为cn\-north\-1，Service为cv**
:::
主要用于鉴权，详见 [公共参数](https://www.volcengine.com/docs/6369/67268) \- 签名参数 \- 在Header中的场景部分
<span id="HpYkrYBl"></span>
#### **Body参数**
:::warning
业务请求参数，放到request.body中，MIME\-Type为**application/json**

:::
|名称 |类型 |必选 |描述 |
|---|---|---|---|
|req_key |string |必选 |服务标识|\
| | | |取固定值: **jimeng_realman_avatar_picture_omni_v15** |
|image_url |string |必选 |人像图片URL链接 |
|mask_url |array of string |可选 |mask图URL列表|\
| | | |如果需要指定图片中的某个主体说话，可通过**调用步骤2：主体检测**获取对应主体的mask图传入 |
|audio_url |string |必选 |音频URL|\
| | | |音频时长必须小于60秒，过长情况下提交任务正常，查询任务会报错如下：|\
| | | |```JSON|\
| | | |{|\
| | | |    "code": 50215,|\
| | | |    "data": null,|\
| | | |    "message": "Input invalid for this service.",|\
| | | |    "request_id": "2025092517155016D925474BBC35F63896",|\
| | | |    "status": 50215,|\
| | | |    "time_elapsed": "28.911171ms"|\
| | | |}|\
| | | |```|\
| | | | |
|seed |int |可选 |随机种子，作为确定扩散初始状态的基础，默认\-1（随机）。若随机种子为相同正整数且其他参数均一致，则生成内容极大概率效果一致|\
| | | |默认值：\-1 |
|prompt |string |可选 |提示词，仅限中文、英语、日语、韩语、墨西哥语、印尼语，建议长度≤300字符 |
|output_resolution |int |可选 |输出视频分辨率|\
| | | |可选值（二选一）：[720, 1080]|\
| | | |默认值：1080 |
|pe_fast_mode |bool |可选 |是否启用快速模式|\
| | | ||\
| | | |* 开启后会通过牺牲部分效果加快生成速度|\
| | | |* 如果希望与即梦客户端的效果保持较高的一致性，建议遵循如下传参规则：|\
| | | |   * 当输出视频分辨率（output_resolution）取值为720时，pe_fast_mode传true|\
| | | |   * 当输出视频分辨率（output_resolution）取值为1080时，pe_fast_mode传false|\
| | | ||\
| | | |默认值：false |

<span id="SxBqueIQ"></span>
### 提交任务返回参数
<span id="RW88LZnH"></span>
#### **通用返回参数**
请参考[通用返回字段及错误码](https://www.volcengine.com/docs/6444/69728)
<span id="kwqPevIu"></span>
#### **业务返回参数**
:::tip 重点关注data中以下字段，其他字段为公共返回(可忽略或不做解析)

:::
|字段 |类型 |说明 |
|---|---|---|
|task_id |string |任务ID，用于查询结果 |

<span id="MV5sBjJT"></span>
### 提交任务请求&返回完整示例
**请求示例：**
```JSON
{
    "req_key": "jimeng_realman_avatar_picture_omni_v15",
    "image_url": "https://xxxxx",
    // "mask_url": ["https://xxxxx", ...]
    "audio_url": "https://xxxxx"
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

<span id="XkRzLbBF"></span>
## 查询任务
<span id="meJwcf0W"></span>
### **查询任务请求参数**
<span id="Mtw2N4GZ"></span>
#### **Query参数**
:::tip 拼接到url后的参数，示例：[https://visual.volcengineapi.com](https://visual.volcengineapi.com/)[?Action=CVGetResult&Version=2022-08-31](https://visual.volcengineapi.com?Action=CVGetResult&Version=2022-08-31)

:::
|参数 |类型 |**可选/必选** |说明 |
|---|---|---|---|
|Action |string |必选 |接口名，固定值：**CVGetResult** |
|Version |string |必选 |版本号，固定值：**2022\-08\-31** |

<span id="Cij1pwoF"></span>
#### **Header参数**
:::warning
本服务固定值：**Region为cn\-north\-1，Service为cv**
:::
主要用于鉴权，详见 [公共参数](https://www.volcengine.com/docs/6369/67268) \- 签名参数 \- 在Header中的场景部分
<span id="QtbA9YpR"></span>
#### **Body参数**
:::warning
业务请求参数，放到request.body中，MIME\-Type为**application/json**

:::
|参数 |类型 |可选/必选 |说明 | |
|---|---|---|---|---|
|req_key |string |必选 |服务标识| |\
| | | |取固定值: **jimeng_realman_avatar_picture_omni_v15** | |
|task_id |string |必选 |任务ID，此字段的取值为**提交任务接口**的返回 | |
|req_json |json string |可选 |json序列化后的字符串,目前支持隐性水印配置，可在返回结果中添加 |示例："{\"aigc_meta\": {\"content_producer\": \"xxxxxx\", \"producer_id\": \"xxxxxx\", \"content_propagator\": \"xxxxxx\", \"propagate_id\": \"xxxxxx\"}}" |

<span id="6fFSWsdl"></span>
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

<span id="8zhlsx33"></span>
##### AIGCMeta
隐式标识，依据《人工智能生成合成内容标识办法》&《网络安全技术人工智能生成合成内容标识方法》

|名称 |类型 |**可选/必选** |描述 |
|---|---|---|---|
|content_producer |string |可选 |内容生成服务ID（长度 <= 256字符） |
|producer_id |string |必选 |内容生成服务商给此图片数据的唯一ID（长度 <= 256字符） |
|content_propagator |string |必选 |内容传播服务商ID（长度 <= 256字符） |
|propagate_id |string |可选 |传播服务商给此图片数据的唯一ID（长度 <= 256字符） |

<span id="PtWWIA8z"></span>
### 查询任务返回参数
<span id="l8fdebjW"></span>
#### **通用返回参数**
请参考[通用返回字段及错误码](https://www.volcengine.com/docs/6444/69728)
<span id="CI0dYiql"></span>
#### **业务返回参数**
:::tip
重点关注data中以下字段，其他字段为公共返回(可忽略或不做解析)

:::
|参数名 |类型 |参数说明 |
|---|---|---|
|video_url |string |视频链接（**有效期为 1 小时**） |
|aigc_meta_tagged |bool |隐式标识是否打标成功 |
|status |string |任务执行状态|\
| | ||\
| | |* processing：任务前置处理|\
| | |* in_queue：任务已提交|\
| | |* generating：任务已被消费，处理中|\
| | |* done：处理完成，成功或者失败，可根据外层code&message进行判断|\
| | |* not_found：任务未找到，可能原因是无此任务或任务已过期(12小时)|\
| | |* expired：任务已过期，请尝试重新提交任务请求 |

<span id="E0xSZUkA"></span>
### 查询任务请求&返回完整示例
**请求示例：**
```JSON
{
    "req_key": "jimeng_realman_avatar_picture_omni_v15",
    "task_id": "<任务提交接口返回task_id>",
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

<span id="WAE8NxIC"></span>
## 错误码
<span id="guKxoBDI"></span>
### **通用错误码**
请参考[通用返回字段及错误码](https://www.volcengine.com/docs/6444/69728)
<span id="hFJhfPZT"></span>
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

&nbsp;
<span id="npp6rpqr"></span>
## 接入说明
<span id="9GgCcR8x"></span>
### SDK使用说明
请参考[SDK使用说明](https://www.volcengine.com/docs/6444/1340578)
<span id="iDIaPTft"></span>
### HTTP方式接入说明
请参考[HTTP请求示例](https://www.volcengine.com/docs/6444/1390583)
&nbsp;


