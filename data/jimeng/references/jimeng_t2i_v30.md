<span id="J4BpYk0V"></span>
# 接口简介
文生图3.0是即梦同源的文生图能力，在**文字响应准确度、图文排版、层次美感和语义理解**能力上相较之前版本均有显著提升，人像质感更逼真，且支持输出高清大图。此外，在文字响应更精准的基础下，还支持响应大小字、各类艺术字体和不同字重。
<span id="AP4n0xvI"></span>
# 接入说明
<span id="IofNGsIT"></span>
## 请求说明

|名称 |内容 |
|---|---|
|接口地址 |[https://visual.volcengineapi.com](https://visual.volcengineapi.com/) |
|请求方式 |POST |
|Content\-Type |application/json |

<span id="1GqwxDet"></span>
## 提交任务
<span id="KY4VDDHq"></span>
### **提交任务请求参数**
<span id="YQbyxnGB"></span>
#### **Query参数**
:::tip 拼接到url后的参数，示例：[https://visual.volcengineapi.com?Action=CVSync2AsyncSubmitTask&Version=2022-08-31](https://visual.volcengineapi.com?Action=CVSync2AsyncSubmitTask&Version=2022-08-31)

:::
|参数 |类型 |**可选/必选** |说明 |
|---|---|---|---|
|Action |string |必选 |接口名，取值：**CVSync2AsyncSubmitTask** |
|Version |string |必选 |版本号，取值：2022\-08\-31 |

<span id="WYfvENGL"></span>
#### **Header参数**
:::warning
本服务固定值：**Region为cn\-north\-1，Service为cv**
:::
主要用于鉴权，详见 [公共参数](https://www.volcengine.com/docs/6369/67268) \- 签名参数 \- 在Header中的场景部分
<span id="JNMjMBYS"></span>
#### **Body参数**
:::warning
业务请求参数，放到request.body中，MIME\-Type为**application/json**

:::
|参数 |类型 |**可选/必选** |说明 |
|---|---|---|---|
|req_key |string |必选 |算法名称，取**固定值为jimeng_t2i_v30** |
|prompt |string |必选 |用于生成图像的提示词 ，中英文均可输入。建议长度<=120字符，最长不超过800字符，prompt过长有概率出图异常或不生效 |
|use_pre_llm |bool |可选 |开启文本扩写，会针对输入prompt进行扩写优化，如果输入prompt较短建议开启，如果输入prompt较长建议关闭|\
| | | |默认值：true |
|seed |int |可选 |随机种子，作为确定扩散初始状态的基础，默认\-1（随机）。若随机种子为相同正整数且其他参数均一致，则生成图片极大概率效果一致|\
| | | |默认值：\-1 |
|width |int |可选 |1、生成图像宽高，**系统默认生成1328 \* 1328的图像**；|\
| | | |2、支持自定义生成图像宽高，宽高比在1:3到3:1之间，宽高乘积在[512\*512, 2048\*2048]之间；推荐可选的宽高比为：|\
| | | ||\
| | | |* 标清1K|\
| | | |   * 1328 \* 1328（1:1）|\
| | | |   * 1472 \* 1104 （4:3）|\
| | | |   * 1584 \* 1056（3:2）|\
| | | |   * 1664 \* 936（16:9）|\
| | | |   * 2016 \* 864（21:9）|\
| | | |* 高清2K|\
| | | |   * 2048 \* 2048（1:1）|\
| | | |   * 2304 \* 1728 （4:3）|\
| | | |   * 2496 \* 1664（3:2）|\
| | | |   * 2560 \* 1440（16:9）|\
| | | |   * 3024 \* 1296（21:9）|\
| | | ||\
| | | |&nbsp;|\
| | | |注意：|\
| | | ||\
| | | |* 需同时传width和height才会生效； |
|height |int |可选 |^^|

<span id="RvySrFbR"></span>
### 提交任务返回参数
<span id="wmYUlFyr"></span>
#### **通用返回参数**
请参考[通用返回字段及错误码](https://www.volcengine.com/docs/6444/69728)
<span id="nb2IN0Jm"></span>
#### **业务返回参数**
:::tip 重点关注data中以下字段，其他字段为公共返回(可忽略或不做解析)

:::
|字段 |类型 |说明 |
|---|---|---|
|task_id |string |任务ID，用于查询结果 |

<span id="a1lccc7R"></span>
### 提交任务请求&返回完整示例
**请求示例：**
```JSON
{
    "req_key": "jimeng_t2i_v30",
    "prompt": "千军万马",
    "seed": -1,
    "width": 1024,
    "height": 1024
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

<span id="DGZ31nOc"></span>
## 查询任务
<span id="BvGUXoW9"></span>
### **查询任务请求参数**
<span id="2tr96Dk5"></span>
#### **Query参数**
:::tip 拼接到url后的参数，示例：[https://visual.volcengineapi.com](https://visual.volcengineapi.com/)[?Action=CVSync2AsyncGetResult&Version=2022-08-31](https://visual.volcengineapi.com?Action=CVGetResult&Version=2022-08-31)

:::
|参数 |类型 |**可选/必选** |说明 |
|---|---|---|---|
|Action |string |必选 |接口名，固定值：**CVSync2AsyncGetResult** |
|Version |string |必选 |版本号，固定值：**2022\-08\-31** |

<span id="PCwQDxEq"></span>
#### **Header参数**
:::warning
本服务固定值：**Region为cn\-north\-1，Service为cv**
:::
主要用于鉴权，详见 [公共参数](https://www.volcengine.com/docs/6369/67268) \- 签名参数 \- 在Header中的场景部分
<span id="Fk8sVH4F"></span>
#### **Body参数**
:::warning
业务请求参数，放到request.body中，MIME\-Type为**application/json**

:::
|参数 |类型 |**可选/必选** |说明 |
|---|---|---|---|
|req_key |string |必选 |服务标识|\
| | | |取固定值: **jimeng_t2i_v30** |
|task_id |string |必选 |任务ID，此字段的取值为**提交任务接口**的返回 |
|req_json |JSON string |可选 |json序列化后的字符串|\
| | | |目前支持水印配置和是否以图片链接形式返回，可在返回结果中添加|\
| | | |示例："{\"logo_info\":{\"add_logo\":true,\"position\":0,\"language\":0,\"opacity\":1,\"logo_text_content\":\"这里是明水印内容\"},\"return_url\":true}" |

<span id="XJgwkfOv"></span>
##### **ReqJson(序列化后的结果再赋值给req_json)**
配置信息

|**参数** |**类型** |**可选/必选** |**说明** | |
|---|---|---|---|---|
|return_url |bool |可选 |输出是否返回图片链接  **（链接有效期为24小时）**  | |
|logo_info |LogoInfo |可选 |水印信息 | |
|aigc_meta |AIGCMeta |可选 |隐式标识 |隐式标识验证方式：|\
| | | | ||\
| | | | |1. 查看【png】或【mp4】格式，人工智能生成合成内容表示服务平台（后续预计增加jpg）|\
| | | | |* [https://www.gcmark.com/web/index.html#/mark/check/image](https://www.gcmark.com/web/index.html#/mark/check/image)|\
| | | | |2. 查看【jpg】格式，使用app11 segment查看aigc元数据内容|\
| | | | |* 如 [https://cyber.meme.tips/jpdump/#](https://cyber.meme.tips/jpdump/#) |

<span id="IBIiY3sJ"></span>
##### **LogoInfo**
水印相关信息

|名称 |类型 |**可选/必选** |描述 |
|---|---|---|---|
|add_logo |bool |可选 |是否添加水印。True为添加，False不添加。默认不添加 |
|position |int |可选 |水印的位置，取值如下：|\
| | | |0\-右下角|\
| | | |1\-左下角|\
| | | |2\-左上角|\
| | | |3\-右上角|\
| | | |默认0 |
|language |int |可选 |水印的语言，取值如下：|\
| | | |0\-中文（AI生成）|\
| | | |1\-英文（Generated by AI）|\
| | | |默认0 |
|opacity |float |可选 |水印的不透明度，取值范围0\-1，1表示完全不透明，默认1 |
|logo_text_content |string |可选 |明水印自定义内容 |

<span id="CME4x9Ap"></span>
##### AIGCMeta
隐式标识，依据《人工智能生成合成内容标识办法》&《网络安全技术人工智能生成合成内容标识方法》

|名称 |类型 |**可选/必选** |描述 |
|---|---|---|---|
|content_producer |string |可选 |内容生成服务ID |
|producer_id |string |必选 |内容生成服务商给此图片数据的唯一ID |
|content_propagator |string |可选 |内容传播服务商ID |
|propagate_id |string |可选 |传播服务商给此图片数据的唯一ID |

<span id="tR5vn63j"></span>
### 查询任务返回参数
<span id="OPSUlRYY"></span>
#### **通用返回参数**
请参考[通用返回字段及错误码](https://www.volcengine.com/docs/6444/69728)
<span id="Cvax9L8s"></span>
#### **业务返回参数**
:::tip
重点关注data中以下字段，其他字段为公共返回(可忽略或不做解析)

:::
|参数名 |参数说明 |参数示例 |
|---|---|---|
|binary_data_base64 |array of string |返回图片的base64数组。 |
|image_urls |array of string |返回图片的url数组，输出图片格式为jpeg格式 |
|status |string |任务执行状态|\
| | ||\
| | |* in_queue：任务已提交|\
| | |* generating：任务已被消费，处理中|\
| | |* done：处理完成，成功或者失败，可根据外层code&message进行判断|\
| | |* not_found：任务未找到，可能原因是无此任务或任务已过期(12小时)|\
| | |* expired：任务已过期，请尝试重新提交任务请求 |

<span id="32oT2j1Y"></span>
### 查询任务请求&返回完整示例
**请求示例：**
```JSON
{
    "req_key": "jimeng_t2i_v30",
    "task_id": "<任务提交接口返回task_id>",
    "req_json": "{\"logo_info\":{\"add_logo\":false,\"position\":0,\"language\":0,\"opacity\":1,\"logo_text_content\":\"这里是明水印内容\"},\"return_url\":true,\"aigc_meta\":{\"content_producer\":\"xxx\",\"producer_id\":\"xxx\",\"logo_text_content\":\"xxx\",\"logo_text_content\":\"xxx\"}}"
    }
```

**返回示例：**
```JSON
{
    "code": 10000, //状态码，优先判断 code=10000, 然后再判断data.status，否则解析有可能会panic
    "data": {
        "binary_data_base64": null,
        "image_urls": [
            "https://xxxx",
            // ...
        ],
        "status": "done"  //任务状态
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

<span id="GZaKTGHp"></span>
## 错误码
<span id="Q2XOFEaJ"></span>
### **通用错误码**
请参考[通用返回字段及错误码](https://www.volcengine.com/docs/6444/69728)
<span id="xLjIjtjY"></span>
### **业务错误码**

|HttpCode |错误码 |错误消息 |描述 |是否需要重试 |
|---|---|---|---|---|
|200 |10000 |无 |请求成功 |不需要 |
|400 |50411 |Pre Img Risk Not Pass |输入图片前审核未通过 |不需要 |
|400 |50511 |Post Img Risk Not Pass |输出图片后审核未通过 |可重试 |
|400 |50412 |Text Risk Not Pass |输入文本前审核未通过 |不需要 |
|400 |50512 |Post Text Risk Not Pass |输出文本后审核未通过 |不需要 |
|400 |50413 |Post Text Risk Not Pass |输入文本含敏感词、版权词等审核不通过 |不需要 |
|400 |50518 |Pre Img Risk Not Pass: Copyright |输入版权图前审核未通过 |不需要 |
|400 |50519 |Post Img Risk Not Pass: Copyright |输出版权图后审核未通过 |可重试 |
|400 |50520 |Risk Internal Error |审核服务异常 |不需要 |
|400 |50521 |Antidirt Internal Error |版权词服务异常 |不需要 |
|400 |50522 |Image Copyright Internal Error |版权图服务异常 |不需要 |
|429 |50429 |Request Has Reached API Limit, Please Try Later |QPS超限 |可重试 |
|429 |50430 |Request Has Reached API Concurrent Limit, Please Try Later |并发超限 |可重试 |
|500 |50500 |Internal Error |内部错误 |不需要 |
|500 |50501 |Internal RPC Error |内部算法错误 |不需要 |

&nbsp;
<span id="15sxCUlu"></span>
## 接入说明
<span id="JLgy9o5U"></span>
### SDK使用说明
请参考[SDK使用说明](https://www.volcengine.com/docs/6444/1340578)
<span id="i5GpXrRj"></span>
### HTTP方式接入说明
请参考[HTTP请求示例](https://www.volcengine.com/docs/6444/1390583)
&nbsp;


