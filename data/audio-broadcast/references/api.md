# 小播鼠 API 参考

## 基础信息

- 协议: HTTP POST
- 格式: form-data
- 编码: UTF-8

## 认证

### 获取 Token (不修改 token)

```
POST /user/fnkukei/gtoken
参数: username, passwd
返回: { res: true, data: { id, token, ... } }
```

### 重置 Token

```
POST /user/gtoken
参数: username, passwd
返回: { res: true, data: { id, token, ... } }
```

## 设备管理

### 设备列表

```
POST /user/listdev
参数: id, token
返回: { res: true, devlist: [...] }
```

设备对象:
- id: 设备 ID
- device_name: 设备名称
- device_seed: 设备唯一标识 (用于播放等操作)
- status: 状态 (1=在线, 0=离线)
- vol: 当前音量

### 设备列表 (Olist)

```
POST /user/olist
参数: id, token
```

### 注册设备

```
POST /user/deviceadd
参数: id, token, name, sn
```

### 删除设备

```
POST /user/deldevs
参数: id, token, snid
```

## 文件管理

### 文件列表

```
POST /user/listfile
参数: id, token
返回: { res: true, filelist: [...] }
```

文件对象:
- id: 文件 ID
- filename: 文件名
- url: 播放 URL
- len: 时长 (秒)
- sizeByte: 文件大小

### 上传文件

```
POST /user/uploadfile
参数: id, token, name, file (multipart)
```

### 删除文件

```
POST /user/delfile
参数: id, token, fileid
```

## 播放控制

### 播放 URL

```
POST /user/urlplay
参数: id, token, url, snlist
```

- url: 音频文件 URL
- snlist: 设备 seed 列表，多个用 `|` 分隔

### 停止播放

```
POST /user/urlstop
参数: id, token, snlist
```

### 调节音量

```
POST /user/editvols
参数: id, token, vol, snlist
```

- vol: 音量值 (0-100)

## 任务管理

### 任务列表 vs 任务详情

| 接口 | 返回内容 |
|------|----------|
| `/user/list_task` | 只返回任务基本信息列表 |
| `/user/getone_task` | 返回任务详情 + 关联设备列表 + 关联文件列表 |

### 任务状态字段

| 字段 | 含义 | 值说明 |
|------|------|--------|
| `enable` | 任务启用状态 | 1=启用, 0=禁用 |
| `statu` | 播放状态 | 1=正在播放, 0=未播放 |

### 禁用/启用任务时的状态变化

| 操作 | enable | statu |
|------|--------|-------|
| 创建/修改后 | 0 | 0 |
| enabletask 启用 | 1 | 0 |
| disabletask 禁用 | 0 | 不变 |
| starttask 启动 | 不变 | 1 |
| stoptask 停止 | 不变 | 0 |

**注意：**
- `enable` 控制定时任务是否生效
- `statu` 表示当前是否正在播放
- 禁用任务仅表示下次到点不会触发播放，不影响当前播放状态

### 任务列表

```
POST /user/list_task
参数: id, token
返回: { res: true, taskary: [...] }
```

任务对象:
- id: 任务 ID
- task_name: 任务名称
- tasktime: 开始时间 (HH:MM:SS)
- enable: 是否启用 (1=启用, 0=禁用)
- statu: 播放状态 (1=正在播放, 0=未播放)
- week: 星期 (7位，1=启用，如 1111111 表示每天)
- kind: 播放模式
- len: 播放时长 (秒)
- jiange: 间隔 (秒)
- startdate: 开始日期 (YYYY-MM-DD 或 "无限制")
- enddate: 结束日期 (YYYY-MM-DD 或 "无限制")
- groupid: 分组 ID

### 添加任务

> ⚠️ **注意**：任务创建或修改后默认是禁用状态，需要调用 `enabletask` 启用。

```
POST /user/add_task
参数: id, token, snids, fileids, start_time, startdate, enddate, len, jiange, kind, weeks, taskname
```

- snids: 设备 ID 列表，多个用 `|` 分隔
- fileids: 文件 ID 列表，多个用 `|` 分隔
- start_time: 开始时间 (HH:MM:SS)
- startdate: 开始日期 (YYYY-MM-DD 或 0 表示立即)
- enddate: 结束日期 (YYYY-MM-DD 或 0 表示永久)
- len: 播放时长 (秒)
- jiange: 文件间隔 (秒)，一个文件播放完后等待多少秒再播放下一个
- kind: 播放模式
  - 0 = 随机播放，根据结束时间停止，最大时长不超过 10 小时
  - 1 = 顺序播放 1 遍后结束
  - 2 = 顺序播放 2 遍后结束
  - 以此类推...
  - 顺序播放时：结束时间先到则到点结束；文件先播完则以文件播完为准
- weeks: 星期设置 (7位，位置1-7分别代表周一到周日)
  - 1 = 播放，0 = 不播放
  - 1111111 = 周一到周日每天都播放
  - 1111100 = 周一到周五播放，周六周日不播放
  - 0111100 = 周二到周五播放，周一和周末不播放
- taskname: 任务名称

### 获取任务详细信息

```
POST /user/getone_task
参数: id, token, taskid
返回: { res: true, task: {...}, devlistary: [...], filelistary: [...] }
```

返回任务的详细信息，包括关联的设备列表和文件列表。

### 启用任务

```
POST /user/enabletask
参数: id, token, taskid
```

### 禁用任务

```
POST /user/disabletask
参数: id, token, taskid
```

### 立即启动任务

```
POST /user/starttask
参数: id, token, taskid
```

立刻启动一个没有正在播放的任务。

### 停止正在播放的任务

```
POST /user/stoptask
参数: id, token, taskid
```

停止正在播放的任务。

### 删除任务

```
POST /user/del_task
参数: id, token, taskid
```

## 临时播放

### 开始临时播放

```
POST /user/tmpstartpl
参数: id, token, playmode, len, jiange, snids, fileids
```

### 停止临时播放

```
POST /user/tmpstoppl
参数: id, token, tpid
```

### 临时播放信息

```
POST /user/tmplistpl
参数: id, token
```

## 多路报警器

### 设置消息上报地址

```
POST /user/setreportudpip
参数: id, token, sn, ip (base64编码)
```

### 创建通道报警

```
POST /user/setwaringlinetaskid
参数: id, token, username, passwd, host, lineid, taskid, sn
```

### 删除通道报警

```
POST /user/rmwaringlinetaskid
参数: id, token, lineid, sn
```

### WiFi 回调设置

```
POST /user/setwaringlinewifi
参数: id, token, url (base64编码), sn
```

### WiFi 回调删除

```
POST /user/rmwaringlinewifi
参数: id, token, sn
```

### WiFi 预缓存

```
POST /user/precacheurlwifi
参数: id, token, sn, url (base64编码)
```

### 查询缓存

```
POST /user/scancacheurlwifi
参数: id, token, sn
```
