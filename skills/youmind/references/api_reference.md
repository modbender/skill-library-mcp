# Youmind Skill API Reference (API-Only Runtime)

Browser is only for auth bootstrap/refresh (`auth_manager.py`).
All business operations use HTTP APIs.

## `board_manager.py`

```bash
python scripts/run.py board_manager.py list
python scripts/run.py board_manager.py find --query "keyword"
python scripts/run.py board_manager.py get --id BOARD_ID
python scripts/run.py board_manager.py create --name "Board Name" [--prompt "..."]
```

## `material_manager.py`

```bash
python scripts/run.py material_manager.py add-link --board-id BOARD_ID --url "https://..."
python scripts/run.py material_manager.py upload-file --board-id BOARD_ID --file /path/to/file
python scripts/run.py material_manager.py get-snips --ids "SNIP_ID_1,SNIP_ID_2"
python scripts/run.py material_manager.py list-picks --board-id BOARD_ID
```

## `chat_manager.py`

```bash
python scripts/run.py chat_manager.py create --board-id BOARD_ID --message "..."
python scripts/run.py chat_manager.py send --board-id BOARD_ID --chat-id CHAT_ID --message "..."
python scripts/run.py chat_manager.py history --board-id BOARD_ID
python scripts/run.py chat_manager.py detail --chat-id CHAT_ID
python scripts/run.py chat_manager.py detail-by-origin --board-id BOARD_ID
python scripts/run.py chat_manager.py mark-read --chat-id CHAT_ID
python scripts/run.py chat_manager.py generate-image --board-id BOARD_ID --prompt "..."
python scripts/run.py chat_manager.py generate-slides --board-id BOARD_ID --prompt "..."
```

## `artifact_manager.py`

```bash
python scripts/run.py artifact_manager.py extract --chat-id CHAT_ID
python scripts/run.py artifact_manager.py extract-latest --board-id BOARD_ID
python scripts/run.py artifact_manager.py extract --chat-id CHAT_ID --include-raw-content
```

## `ask_question.py` (compatibility wrapper)

```bash
python scripts/run.py ask_question.py --board-id BOARD_ID --question "..."
python scripts/run.py ask_question.py --board-id BOARD_ID --chat-id CHAT_ID --question "..."
```

## `auth_manager.py`

```bash
python scripts/run.py auth_manager.py setup
python scripts/run.py auth_manager.py status
python scripts/run.py auth_manager.py validate
python scripts/run.py auth_manager.py reauth
python scripts/run.py auth_manager.py clear
```

## Key Endpoints

- Boards: `/api/v1/listBoards`, `/api/v1/board/getBoardDetail`, `/api/v1/createBoard`
- Materials: `/api/v1/tryCreateSnipByUrl`, `/api/v1/genSignedPutUrlIfNotExist`, `/api/v1/createFileRecordFromCdnUrl`, `/api/v1/createTextFile`, `/api/v1/snip/getSnips`
- Chat: `/api/v2/chatAssistant/createChat`, `/api/v2/chatAssistant/sendMessage`, `/api/v2/chatAssistant/listChatHistory`, `/api/v2/chatAssistant/getChatDetail`, `/api/v2/chatAssistant/getChatDetailByOrigin`
