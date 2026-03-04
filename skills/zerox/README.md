## zerox skill
基于zerox项目，将各种格式的文档转换成markdown文档，包括扫描版的PDF。

### 安装依赖
CD到skill根目录
npm install zerox --ignore-scripts

### 修改zerox源码
由于直连zerox只支持国外的几个模型厂商，直连连不上，所以需要用中转商，这里用的是API易，需要把node_modules目录下的zerox源码的openAI.js文件中的API端点地址改为 https://api.apiyi.com/v1

### 配置apiKey
这里配置的是API易的apiKey
```sh
echo 'APIYI_API_KEY = sk-xxx' >> ~/.openclaw/.env
```
