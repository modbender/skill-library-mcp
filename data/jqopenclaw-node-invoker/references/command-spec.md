# JQOpenClawNode 调用规范

## 1. 通用调用骨架

统一走 `node.invoke`：

```json
{
  "method": "node.invoke",
  "params": {
    "nodeId": "<node-id>",
    "command": "<command-name>",
    "params": {},
    "timeoutMs": 30000,
    "idempotencyKey": "<uuid>"
  }
}
```

约束：
- `nodeId`、`command`、`idempotencyKey` 必填。
- `params` 可省略，省略时等价空对象。
- 每次请求使用新 UUID 作为 `idempotencyKey`。
- 节点侧接收 `node.invoke.request` 时仅解析 `paramsJSON`，且 `paramsJSON` 必须为对象 JSON。
- `paramsJSON` 缺失或 `null` 时按空对象处理；若存在但不是字符串、为空字符串、或解析后不是对象，返回 `INVALID_PARAMS`。
- `node.invoke.params.timeoutMs` 可省略；若传入，必须为非负整数（毫秒），否则返回 `INVALID_PARAMS`。其中 `0` 视为立即超时。
- `node.invoke.params.timeoutMs` 会参与请求预算裁剪。节点内部会将 `process.exec.params.timeoutMs` 与 `file.read(operation=rg)` 的内部执行超时裁剪到该预算内（取更小值）。
- 即便省略 `node.invoke.params.timeoutMs`，网关/调用端仍存在等待超时（当前 OpenClaw 侧常见默认约 `30000ms`，CLI `openclaw nodes invoke` 默认 `15000ms`）。
- 实际可用执行时长取决于最先触发的超时层：调用端/网关等待超时、`node.invoke.params.timeoutMs`（若传入）、能力内部超时。

## 2. file.read

用途：读取文件内容、按行区间、目录遍历、元信息，或执行 `rg` 搜索。

`params`：
- `path`：字符串，必填。
- `operation`：字符串，可选，默认 `read`。可选值：`read` / `lines` / `list` / `rg` / `stat`。
- `read` 模式参数：
  - `encoding`：字符串，可选，`utf8`（默认）或 `base64`。
  - `maxBytes`：整数，可选，默认 `1048576`，范围 `[1, 20971520]`。
  - `offsetBytes`（或 `offset`）：整数，可选，默认 `0`。用于分块读取起始偏移量，范围 `[0, sizeBytes]`。
- `lines` 模式参数：
  - `startLine`（或 `fromLine`）：整数，必填，1-based 起始行号。
  - `endLine`（或 `toLine`）：整数，必填，1-based 结束行号（含）。
  - `encoding`：仅支持 `utf8`（默认）。
  - 行区间跨度限制：`endLine - startLine + 1` 需在 `[1, 50000]`。
- `list` 模式参数：
  - `includeEntries`：布尔，可选，默认 `true`。是否返回目录项列表。
  - `maxEntries`：整数，可选，默认 `200`，范围 `[1, 5000]`。仅在 `includeEntries=true` 时生效。
  - `recursive`：布尔，可选，默认 `false`。是否递归遍历子目录。
  - `includeHidden`：布尔，可选，默认 `true`。是否包含隐藏/系统项。
  - `glob`：字符串或字符串数组，可选。按文件名或相对路径通配过滤（支持 `*`、`?`）。
- `rg` 模式参数：
  - `pattern`：字符串，必填。
  - `maxMatches`：整数，可选，默认 `200`，范围 `[1, 5000]`。
  - `caseSensitive`：布尔，可选，默认 `false`。
  - `includeHidden`：布尔，可选，默认 `false`。
  - `literal`：布尔，可选，默认 `false`（固定字符串匹配）。
  - 内部执行超时：默认 `60000ms`，若设置了 `node.invoke.timeoutMs`（含 `0`），实际超时为二者较小值。
- `stat` 模式参数：
  - 无额外必填参数。

示例：

```json
{
  "method": "node.invoke",
  "params": {
    "nodeId": "<node-id>",
    "command": "file.read",
    "params": {
      "operation": "read",
      "path": "C:/Windows/win.ini",
      "encoding": "utf8",
      "offsetBytes": 0,
      "maxBytes": 8192
    },
    "timeoutMs": 15000,
    "idempotencyKey": "<uuid>"
  }
}
```

示例（list 模式）：

```json
{
  "method": "node.invoke",
  "params": {
    "nodeId": "<node-id>",
    "command": "file.read",
    "params": {
      "operation": "list",
      "path": "C:/Temp",
      "recursive": true,
      "glob": ["*.log", "logs/*"],
      "includeHidden": false,
      "includeEntries": true,
      "maxEntries": 200
    },
    "timeoutMs": 15000,
    "idempotencyKey": "<uuid>"
  }
}
```

示例（lines 模式）：

```json
{
  "method": "node.invoke",
  "params": {
    "nodeId": "<node-id>",
    "command": "file.read",
    "params": {
      "operation": "lines",
      "path": "C:/Repos/project/src/main.cpp",
      "startLine": 120,
      "endLine": 160
    },
    "timeoutMs": 15000,
    "idempotencyKey": "<uuid>"
  }
}
```

示例（rg 模式）：

```json
{
  "method": "node.invoke",
  "params": {
    "nodeId": "<node-id>",
    "command": "file.read",
    "params": {
      "operation": "rg",
      "path": "C:/Repos/project",
      "pattern": "TODO",
      "maxMatches": 200
    },
    "timeoutMs": 30000,
    "idempotencyKey": "<uuid>"
  }
}
```

示例（stat 模式）：

```json
{
  "method": "node.invoke",
  "params": {
    "nodeId": "<node-id>",
    "command": "file.read",
    "params": {
      "operation": "stat",
      "path": "C:/Temp/app.log"
    },
    "timeoutMs": 15000,
    "idempotencyKey": "<uuid>"
  }
}
```

返回重点（payload）：
- 公共字段：
  - `path`
  - `operation`
  - `targetType`：`file` 或 `directory`
- `read` 模式字段：
  - `encoding`
  - `sizeBytes`
  - `offsetBytes`
  - `nextOffsetBytes`
  - `readBytes`
  - `hasMore`
  - `eof`
  - `truncated`
  - `content`
- `lines` 模式字段：
  - `encoding`（固定 `utf8`）
  - `startLine`
  - `endLine`
  - `returnedLineCount`
  - `hasMore`
  - `eof`
  - `content`（按 `\n` 拼接）
  - `lines`（数组元素字段：`lineNumber`、`text`）
- `list` 模式字段：
  - `recursive`
  - `includeHidden`
  - `glob`（可选，数组）
  - `directoryCount`
  - `fileCount`
  - `otherCount`
  - `totalCount`
  - `includeEntries`
  - `maxEntries`（仅 `includeEntries=true` 返回）
  - `truncated`（仅 `includeEntries=true` 返回）
  - `entries`（仅 `includeEntries=true` 返回，元素字段：`name`、`path`、`relativePath`、`type`、`isSymLink`、`sizeBytes`[文件项才有]）
- `rg` 模式字段：
  - `pattern`
  - `caseSensitive`
  - `includeHidden`
  - `literal`
  - `maxMatches`
  - `matchCount`
  - `fileCount`
  - `truncated`
  - `rgExitCode`
  - `stderr`（可选）
  - `matches`（数组元素字段：`path`、`lineNumber`、`columnStart`、`columnEnd`、`lineText`、`matchText`）
- `stat` 模式字段：
  - `name`
  - `isFile` / `isDir` / `isSymLink` / `isHidden`
  - `isReadable` / `isWritable` / `isExecutable`
  - `sizeBytes`（文件时返回）
  - `owner`（`name`、`id`、`group`、`groupId`）
  - `permissions`（owner/group/other 的 read/write/execute）
  - `timestamps`（`accessTime`、`birthTime`、`modificationTime`、`metadataChangeTime`，各含 `iso8601`、`epochMs`）

## 3. file.write

用途：写入文件内容，或执行移动（剪切）与删除操作。

`params`：
- `path`：字符串，必填。
- `allowWrite`：布尔，可选，默认 `false`。必须显式传 `true` 才允许执行 `file.write`。
- `operation`：字符串，可选，默认 `write`。可选值：`write` / `move`（或 `cut`）/ `delete`（或 `remove`）。
- `write` 模式参数：
  - `content`：字符串，必填。
  - `encoding`：字符串，可选，`utf8`（默认）或 `base64`。
  - `append`：布尔，可选，默认 `false`。
  - `createDirs`：布尔，可选，默认 `true`。
- `move` 模式参数：
  - `destinationPath` 或 `toPath`：字符串，必填（目标路径）。
  - `overwrite`：布尔，可选，默认 `false`（目标存在时是否覆盖）。
  - `createDirs`：布尔，可选，默认 `true`（自动创建目标父目录）。
- `delete` 模式参数：
  - 无额外必填参数。删除行为固定为移动到回收站（`QFile::moveToTrash`）。

示例：

```json
{
  "method": "node.invoke",
  "params": {
    "nodeId": "<node-id>",
    "command": "file.write",
    "params": {
      "allowWrite": true,
      "operation": "write",
      "path": "C:/Temp/jqopenclaw-output.txt",
      "content": "hello from node",
      "encoding": "utf8",
      "append": false,
      "createDirs": true
    },
    "timeoutMs": 15000,
    "idempotencyKey": "<uuid>"
  }
}
```

示例（move 模式）：

```json
{
  "method": "node.invoke",
  "params": {
    "nodeId": "<node-id>",
    "command": "file.write",
    "params": {
      "allowWrite": true,
      "operation": "move",
      "path": "C:/Temp/a.txt",
      "destinationPath": "C:/Temp/archive/a.txt",
      "overwrite": true
    },
    "timeoutMs": 15000,
    "idempotencyKey": "<uuid>"
  }
}
```

示例（delete 模式）：

```json
{
  "method": "node.invoke",
  "params": {
    "nodeId": "<node-id>",
    "command": "file.write",
    "params": {
      "allowWrite": true,
      "operation": "delete",
      "path": "C:/Temp/old-data"
    },
    "timeoutMs": 15000,
    "idempotencyKey": "<uuid>"
  }
}
```

返回重点（payload）：
- 公共字段：
  - `operation`
  - `path`
- `write` 模式字段：
  - `encoding`
  - `appended`
  - `bytesWritten`
  - `sizeBytes`
- `move` 模式字段：
  - `fromPath`
  - `toPath`
  - `targetType`：`file` 或 `directory`
  - `overwritten`
  - `moved`
- `delete` 模式字段：
  - `targetType`：`file` 或 `directory`
  - `deleted`
  - `deleteMode`：固定 `trash`

## 4. process.exec

用途：远程执行进程命令（QProcess）。

`params`：
- `command`：字符串，不支持；传入会返回 `INVALID_PARAMS`。
- `program`：字符串，必填。
- `arguments`：字符串数组，可选。
- `workingDirectory`：字符串，可选。
- `stdin`：字符串，可选。
- `timeoutMs`：数字，可选，默认 `30000`，范围 `[100, 300000]`。
- `inheritEnvironment`：布尔，可选，默认 `true`。
- `environment`：对象，可选，键和值都必须是字符串。
- `mergeChannels`：布尔，可选，默认 `false`。
- 超时裁剪：若设置了 `node.invoke.timeoutMs`（含 `0`），实际执行超时为 `min(process.exec.params.timeoutMs, node.invoke.timeoutMs)`。

示例（program 模式）：

```json
{
  "method": "node.invoke",
  "params": {
    "nodeId": "<node-id>",
    "command": "process.exec",
    "params": {
      "program": "ping",
      "arguments": ["127.0.0.1", "-n", "2"],
      "timeoutMs": 15000
    },
    "timeoutMs": 20000,
    "idempotencyKey": "<uuid>"
  }
}
```

返回重点（payload）：
- `program`
- `arguments`
- `workingDirectory`
- `timeoutMs`
- `elapsedMs`
- `timedOut`
- `exitCode`
- `exitStatus`
- `stdout`
- `stderr`
- `ok`：布尔。是否为正常完成且 `exitCode == 0`。
- `resultClass`：字符串。`ok` / `non_zero_exit` / `crash` / `timeout`。
- `processError`：数字，可选。仅在存在进程级错误时返回。
- `processErrorName`：字符串，可选。仅在存在进程级错误时返回，取值：`failed_to_start` / `crashed` / `timed_out` / `read_error` / `write_error`。
- `processErrorString`：字符串，可选。仅在存在进程级错误时返回。

判定建议：
- 优先使用 `ok` 与 `resultClass` 判断执行结果。
- `resultClass=timeout`（或 `timedOut=true`）时，`node.invoke` 仍返回成功结构，调用方应按业务将其视为超时失败。
- 无进程级错误时，不返回 `processError*` 字段。

## 5. system.screenshot

用途：采集全部屏幕截图并返回上传后的 URL 信息。

返回重点（payload 数组元素）：
- `format`
- `mimeType`
- `url`
- `width`
- `height`
- `screenIndex`
- `screenName`（可选）

## 6. system.info

用途：采集系统基础信息。

返回重点（payload）：
- `cpuName`
- `cpuCores`
- `cpuThreads`
- `computerName`
- `hostName`
- `osName`
- `osVersion`
- `userName`
- `memory`
- `gpuNames`
- `ip`
- `disks`

## 7. 常见错误与处理

- `INVALID_PARAMS`
  - 参数缺失、类型不匹配或超出范围（含 `file.read` / `file.write` / `process.exec` 参数校验失败）。
  - 修正字段后重试。

- `FILE_READ_FAILED` / `FILE_WRITE_FAILED`
  - 常见原因：路径错误、权限不足、父目录不存在、移动目标已存在、系统回收站不可用或拒绝接收目标。
  - 优先检查路径、权限、目录状态、回收站状态等执行环境问题。

- `PROCESS_EXEC_FAILED`
  - 常见原因：程序不存在、权限不足、启动失败等无法产出结构化执行结果。
  - 优先检查 `program`、`workingDirectory`、权限、运行环境。

- `SYSTEM_INFO_FAILED`
  - 系统信息采集失败。

- `SCREENSHOT_CAPTURE_FAILED`
  - 截图采集阶段失败（未进入上传）。

- `SCREENSHOT_UPLOAD_FAILED`
  - 截图已采集但全部上传失败。

- `TIMEOUT`
  - `node.invoke` 请求级超时（网关等待节点结果超时），或显式传入 `timeoutMs=0` 导致立即超时。
  - 增大 `timeoutMs` 或缩小执行范围。

- `COMMAND_NOT_SUPPORTED`
  - 节点未实现该命令。
  - 检查 `node.describe.commands`。

- `command not allowlisted`
  - 网关策略拦截。
  - 在网关配置 `gateway.nodes.allowCommands` 增加目标命令（如 `file.read`、`file.write`）。
