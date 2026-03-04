"""
feishu_api.py — 飞书 API 封装层
Token 管理 + 核心 API 调用封装
"""

import os
import time
import json
import requests
from typing import Optional, Dict, List, Any

# 飞书应用凭证（延迟检查，允许 demo 模式不配置凭证）
APP_ID = os.environ.get("FEISHU_APP_ID", "")
APP_SECRET = os.environ.get("FEISHU_APP_SECRET", "")

BASE_URL = "https://open.feishu.cn/open-apis"


def _check_creds():
    """调用 API 前检查凭证是否已配置"""
    global APP_ID, APP_SECRET
    APP_ID = os.environ.get("FEISHU_APP_ID", APP_ID)
    APP_SECRET = os.environ.get("FEISHU_APP_SECRET", APP_SECRET)
    if not APP_ID or not APP_SECRET:
        raise EnvironmentError(
            "请设置环境变量 FEISHU_APP_ID 和 FEISHU_APP_SECRET。\n"
            "export FEISHU_APP_ID=cli_xxx\n"
            "export FEISHU_APP_SECRET=xxx"
        )

# Token 缓存
_token_cache = {"token": None, "expires_at": 0}


def get_token() -> str:
    """获取 tenant_access_token，自动缓存和刷新"""
    _check_creds()
    now = time.time()
    if _token_cache["token"] and _token_cache["expires_at"] > now + 60:
        return _token_cache["token"]

    resp = requests.post(
        f"{BASE_URL}/auth/v3/tenant_access_token/internal",
        json={"app_id": APP_ID, "app_secret": APP_SECRET},
        timeout=10,
    )
    resp.raise_for_status()
    data = resp.json()
    if data.get("code") != 0:
        raise Exception(f"获取 token 失败: {data}")

    _token_cache["token"] = data["tenant_access_token"]
    _token_cache["expires_at"] = now + data.get("expire", 7200)
    return _token_cache["token"]


def _headers() -> Dict[str, str]:
    return {
        "Authorization": f"Bearer {get_token()}",
        "Content-Type": "application/json",
    }


def _get(path: str, params: Optional[Dict] = None) -> Dict:
    resp = requests.get(f"{BASE_URL}{path}", headers=_headers(), params=params, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    if data.get("code") != 0:
        raise Exception(f"API 错误 [{path}]: {data.get('msg', data)}")
    return data.get("data", {})


def _post(path: str, body: Optional[Dict] = None) -> Dict:
    resp = requests.post(f"{BASE_URL}{path}", headers=_headers(), json=body or {}, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    if data.get("code") != 0:
        raise Exception(f"API 错误 [{path}]: {data.get('msg', data)}")
    return data.get("data", {})


def _put(path: str, body: Optional[Dict] = None) -> Dict:
    resp = requests.put(f"{BASE_URL}{path}", headers=_headers(), json=body or {}, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    if data.get("code") != 0:
        raise Exception(f"API 错误 [{path}]: {data.get('msg', data)}")
    return data.get("data", {})


def _delete(path: str) -> Dict:
    resp = requests.delete(f"{BASE_URL}{path}", headers=_headers(), timeout=30)
    resp.raise_for_status()
    data = resp.json()
    if data.get("code") != 0:
        raise Exception(f"API 错误 [{path}]: {data.get('msg', data)}")
    return data.get("data", {})


# ============================================================
# Bitable API
# ============================================================

def bitable_list_tables(app_token: str) -> List[Dict]:
    """列出多维表格的所有数据表"""
    data = _get(f"/bitable/v1/apps/{app_token}/tables")
    return data.get("items", [])


def bitable_list_fields(app_token: str, table_id: str) -> List[Dict]:
    """列出数据表的所有字段"""
    data = _get(f"/bitable/v1/apps/{app_token}/tables/{table_id}/fields")
    return data.get("items", [])


def bitable_list_records(
    app_token: str,
    table_id: str,
    page_size: int = 100,
    page_token: Optional[str] = None,
    filter_str: Optional[str] = None,
    sort_str: Optional[str] = None,
) -> Dict:
    """列出记录，支持分页、过滤、排序"""
    params = {"page_size": page_size}
    if page_token:
        params["page_token"] = page_token
    if filter_str:
        params["filter"] = filter_str
    if sort_str:
        params["sort"] = sort_str
    return _get(f"/bitable/v1/apps/{app_token}/tables/{table_id}/records", params)


def bitable_list_all_records(
    app_token: str,
    table_id: str,
    filter_str: Optional[str] = None,
    sort_str: Optional[str] = None,
) -> List[Dict]:
    """列出所有记录（自动分页）"""
    all_records = []
    page_token = None
    while True:
        data = bitable_list_records(app_token, table_id, 500, page_token, filter_str, sort_str)
        items = data.get("items", [])
        all_records.extend(items)
        if not data.get("has_more"):
            break
        page_token = data.get("page_token")
    return all_records


def bitable_create_record(app_token: str, table_id: str, fields: Dict) -> Dict:
    """创建单条记录"""
    return _post(
        f"/bitable/v1/apps/{app_token}/tables/{table_id}/records",
        {"fields": fields},
    )


def bitable_batch_create_records(app_token: str, table_id: str, records: List[Dict]) -> Dict:
    """批量创建记录（单次最多 500 条）"""
    return _post(
        f"/bitable/v1/apps/{app_token}/tables/{table_id}/records/batch_create",
        {"records": [{"fields": r} for r in records]},
    )


def bitable_update_record(app_token: str, table_id: str, record_id: str, fields: Dict) -> Dict:
    """更新单条记录"""
    return _put(
        f"/bitable/v1/apps/{app_token}/tables/{table_id}/records/{record_id}",
        {"fields": fields},
    )


def bitable_batch_update_records(app_token: str, table_id: str, records: List[Dict]) -> Dict:
    """批量更新记录（单次最多 500 条）
    records: [{"record_id": "xxx", "fields": {...}}, ...]
    """
    return _post(
        f"/bitable/v1/apps/{app_token}/tables/{table_id}/records/batch_update",
        {"records": records},
    )


def bitable_delete_record(app_token: str, table_id: str, record_id: str) -> Dict:
    """删除单条记录"""
    return _delete(f"/bitable/v1/apps/{app_token}/tables/{table_id}/records/{record_id}")


def bitable_batch_delete_records(app_token: str, table_id: str, record_ids: List[str]) -> Dict:
    """批量删除记录（单次最多 500 条）"""
    return _post(
        f"/bitable/v1/apps/{app_token}/tables/{table_id}/records/batch_delete",
        {"records": record_ids},
    )


# ============================================================
# Docx API
# ============================================================

def docx_get_document(doc_token: str) -> Dict:
    """获取文档元信息"""
    return _get(f"/docx/v1/documents/{doc_token}")


def docx_get_content(doc_token: str) -> Dict:
    """获取文档全部内容（blocks）"""
    return _get(f"/docx/v1/documents/{doc_token}/raw_content")


def docx_list_blocks(doc_token: str) -> List[Dict]:
    """列出文档所有 blocks"""
    all_blocks = []
    page_token = None
    while True:
        params = {"page_size": 500}
        if page_token:
            params["page_token"] = page_token
        data = _get(f"/docx/v1/documents/{doc_token}/blocks", params)
        all_blocks.extend(data.get("items", []))
        if not data.get("has_more"):
            break
        page_token = data.get("page_token")
    return all_blocks


def docx_create_block(doc_token: str, parent_id: str, children: List[Dict], index: int = -1) -> Dict:
    """在指定位置插入 block"""
    body = {"children": children}
    if index >= 0:
        body["index"] = index
    return _post(f"/docx/v1/documents/{doc_token}/blocks/{parent_id}/children", body)


def docx_update_block(doc_token: str, block_id: str, update_body: Dict) -> Dict:
    """更新 block 内容"""
    return _put(f"/docx/v1/documents/{doc_token}/blocks/{block_id}", update_body)


def docx_delete_block(doc_token: str, parent_id: str, block_id: str) -> Dict:
    """删除 block"""
    return _delete(f"/docx/v1/documents/{doc_token}/blocks/{parent_id}/children/{block_id}")


def docx_create_document(title: str, folder_token: Optional[str] = None) -> Dict:
    """创建新文档"""
    body = {"title": title}
    if folder_token:
        body["folder_token"] = folder_token
    return _post("/docx/v1/documents", body)


# ============================================================
# Wiki API
# ============================================================

def wiki_list_spaces() -> List[Dict]:
    """列出所有知识库"""
    data = _get("/wiki/v2/spaces", {"page_size": 50})
    return data.get("items", [])


def wiki_get_node(token: str) -> Dict:
    """获取知识库节点信息"""
    return _get(f"/wiki/v2/spaces/get_node", {"token": token})


def wiki_list_nodes(space_id: str, parent_node_token: Optional[str] = None) -> List[Dict]:
    """列出知识库节点"""
    params = {"page_size": 50}
    if parent_node_token:
        params["parent_node_token"] = parent_node_token
    data = _get(f"/wiki/v2/spaces/{space_id}/nodes", params)
    return data.get("items", [])


# ============================================================
# Drive API
# ============================================================

def drive_list_files(folder_token: Optional[str] = None) -> List[Dict]:
    """列出文件夹内容"""
    params = {"page_size": 50}
    if folder_token:
        params["folder_token"] = folder_token
    data = _get("/drive/v1/files", params)
    return data.get("files", [])


def drive_create_folder(name: str, folder_token: Optional[str] = None) -> Dict:
    """创建文件夹"""
    body = {"name": name, "folder_token": folder_token or ""}
    return _post("/drive/v1/files/create_folder", body)
