---
name: "feishu"
description: "飞书套件：文档/表格/多维表格/消息/群聊/通讯录/日程/任务/翻译/OCR/语音"
---

# Feishu Suite Skill

## 环境变量
- `FEISHU_APP_ID`
- `FEISHU_APP_SECRET`

## API 总览

### 文档/知识库/云空间 (Docs)
- `createDocument(title, folderToken?)`
- `getDocument(documentId)`
- `getDocumentRawContent(documentId)`
- `listDocumentBlocks(documentId, pageToken?, pageSize?)`
- `appendText(documentId, text, targetBlockId?)`
- `appendBlocks(documentId, blocks, targetBlockId?)`
- `getPublicPermission(token, type?)`
- `updatePublicPermission(token, type, data)`
- `addMemberPermission(token, type, memberId, memberType, role)`
- `listFiles(folderToken?, pageToken?, pageSize?)`
- `uploadFile(filePath, parentNode, fileName?)`
- `createFolder(name, folderToken)`
- `listWikiSpaces(pageToken?, pageSize?)`
- `getWikiSpace(spaceId)`
- `listWikiNodes(spaceId, parentNodeToken?, pageToken?, pageSize?)`
- `getNodeInfo(token)`

### 表格/多维表格 (Data)
- `createSpreadsheet(title, folderToken?)`
- `getSpreadsheet(spreadsheetToken)`
- `getSheetValues(spreadsheetToken, sheetId, range)`
- `updateSheetValues(spreadsheetToken, sheetId, range, values)`
- `appendSheetValues(spreadsheetToken, sheetId, range, values)`
- `prependSheetValues(spreadsheetToken, sheetId, range, values)`
- `listRecords(appToken, tableId, filter?, sort?, pageToken?, pageSize?)`
- `getRecord(appToken, tableId, recordId)`
- `createRecord(appToken, tableId, fields)`
- `batchCreateRecords(appToken, tableId, records)`
- `updateRecord(appToken, tableId, recordId, fields)`
- `batchUpdateRecords(appToken, tableId, records)`
- `deleteRecord(appToken, tableId, recordId)`
- `batchDeleteRecords(appToken, tableId, recordIds)`
- `copyBitable(appToken, name, folderToken?)`

### IM 消息/话题/群聊 (IM)
- `listMessages(params)`
- `recallMessage(messageId)`
- `updateMessage(messageId, content)`
- `pinMessage(messageId)`
- `unpinMessage(messageId)`
- `react(messageId, emoji)`
- `sendAttachment(receiveId, receiveIdType, filePath, fileName?)`
- `replyInThread(messageId, content, replyInThread?, msgType?)`
- `listThreadMessages(chatId, threadId)`
- `getChatInfo(chatId)`
- `listChats(pageToken?, pageSize?)`
- `getChatMembers(chatId, memberIdType?, pageToken?, pageSize?)`
- `isInChat(chatId)`
- `createChat(params)`
- `addChatMembers(chatId, idList, memberIdType?)`
- `removeChatMembers(chatId, idList, memberIdType?)`

### 组织/通讯录/日程/任务 (Org)
- `getUser(userId, userIdType?)`
- `getDepartment(departmentId, userIdType?)`
- `listDepartmentUsers(departmentId, pageToken?, pageSize?)`
- `getGroup(groupId, userIdType?)`
- `listCalendars(pageToken?, pageSize?)`
- `createCalendarEvent(calendarId, summary, startTime, endTime, description?)`
- `deleteCalendarEvent(calendarId, eventId)`
- `listTasks(pageToken?, pageSize?)`
- `createTask(summary, description?, dueTime?)`
- `completeTask(taskId)`

### AI 能力 (AI)
- `translateText(text, sourceLang, targetLang)`
- `detectLanguage(text)`
- `ocrImage(filePath)`
- `speechToText(filePath, format?)`

## 💡 飞书协作最佳实践 (Best Practices)

### 1. 文档权限与 Fallback 策略
- **预先授权**：在向他人发送飞书文档链接前，**必须**先通过 `updatePublicPermission` 或 `addMemberPermission` 开启可读权限。
- **权限不足时的 Fallback (重要)**：如果应用缺少 `docs:permission.setting:write_only` 权限（报错 99991672），请采用以下方案：
    - **方案 A (推荐)：父文件夹继承**。在一个已公开的文件夹内创建文档，文档会自动继承文件夹的权限，无需额外调用权限 API。
    - **方案 B：内容提取**。若无法授权且必须即时交付，先将文档内容提取并通过 IM 消息（如 `replyInThread`）直接发送原文。
    - **方案 C：知识库 (Wiki)**。在已公开的知识库空间创建页面，通常不需要二次授权。
- **避免尴尬**：严禁发送“对方无权查看”的文档，这会降低协作效率。

### 2. 沟通礼仪与情感
- **表情回复**：积极使用飞书表情（`react` API）回复他人消息。适时的表情符号能传达温暖和认可，让对方感到开心。
- **话题回复**：在群聊人数较多或讨论特定技术/细节时，优先使用 `replyInThread`。这样可以保持主聊天界面的整洁，避免刷屏打扰不相关的成员。
- **视情况而定**：对于需要全员关注的重要通知，可以直接发到主群。
