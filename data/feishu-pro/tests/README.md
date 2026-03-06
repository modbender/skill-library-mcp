# Feishu Skills 测试说明

## 运行方式
- 单模块: `node ~/.openclaw/workspace/projects/openclaw-skills/skills/feishu/tests/test-feishu-im.mjs`
- 全量: `node ~/.openclaw/workspace/projects/openclaw-skills/skills/feishu/tests/run-all.mjs`
- 兼容入口: `node ~/.openclaw/workspace/projects/openclaw-skills/skills/feishu/tests/test-message-skills.cjs`

## 通用环境变量
- `FEISHU_APP_ID`
- `FEISHU_APP_SECRET`

## 安全开关
- `ALLOW_SIDE_EFFECTS=1` 才会执行写入类操作（发送消息、创建文档等）
- `ALLOW_DESTRUCTIVE=1` 才会执行删除/撤回类操作

## 常用测试参数
- `TEST_CHAT_ID`
- `TEST_MESSAGE_ID`
- `TEST_THREAD_ROOT_ID`
- `TEST_ATTACHMENT_PATH`
- `TEST_CHAT_MEMBER_IDS` (逗号分隔)
- `TEST_CREATE_CHAT_USER_IDS` (逗号分隔)
- `TEST_DOC_ID`
- `TEST_DOC_TOKEN`
- `TEST_DOC_TITLE`
- `TEST_DOC_FOLDER_TOKEN`
- `TEST_PUBLIC_PERMISSION_JSON` (JSON 字符串)
- `TEST_DOC_MEMBER_ID`
- `TEST_DOC_MEMBER_TYPE` (email/openid/unionid/...)
- `TEST_DOC_MEMBER_ROLE` (view/edit/full_access)
- `TEST_DRIVE_FOLDER_TOKEN`
- `TEST_DRIVE_PARENT_NODE`
- `TEST_UPLOAD_FILE_PATH`
- `TEST_DRIVE_NEW_FOLDER_NAME`
- `TEST_WIKI_SPACE_ID`
- `TEST_WIKI_NODE_TOKEN`
- `TEST_SHEET_TOKEN`
- `TEST_SHEET_ID`
- `TEST_SHEET_RANGE`
- `TEST_SHEET_VALUES_JSON` (JSON 数组)
- `TEST_SHEET_TITLE`
- `TEST_SHEET_FOLDER_TOKEN`
- `TEST_BITABLE_APP_TOKEN`
- `TEST_BITABLE_TABLE_ID`
- `TEST_BITABLE_RECORD_ID`
- `TEST_BITABLE_RECORD_IDS` (逗号分隔)
- `TEST_BITABLE_FIELDS_JSON` (JSON 对象)
- `TEST_BITABLE_RECORDS_JSON` (JSON 数组)
- `TEST_BITABLE_COPY_NAME`
- `TEST_BITABLE_FOLDER_TOKEN`
- `TEST_USER_ID`
- `TEST_DEPT_ID`
- `TEST_GROUP_ID`
- `TEST_CALENDAR_ID`
- `TEST_EVENT_ID`
- `TEST_EVENT_START`
- `TEST_EVENT_END`
- `TEST_EVENT_SUMMARY`
- `TEST_EVENT_DESC`
- `TEST_TASK_ID`
- `TEST_TASK_SUMMARY`
- `TEST_TASK_DESC`
- `TEST_OCR_IMAGE_PATH`
- `TEST_AUDIO_PATH`
- `TEST_AUDIO_FORMAT`

## 说明
- 所有写入/删除类测试默认跳过，只有显式开启开关才会执行。
- 失败时会输出自查建议，方便线上 OpenClaw 自动回溯。
