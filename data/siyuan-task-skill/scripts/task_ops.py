#!/usr/bin/env python3
"""Task management operations for SiYuan Note (database/Attribute View mode)."""

import json
import sys
import time
import random
import string
from datetime import datetime
from siyuan_api import SiYuanClient, load_config


class TaskManager:
    """Manage tasks stored as database rows in the 任务清单 document of SiYuan Note."""

    TASK_DOC_NAME = "任务清单"

    STATUS_NOT_STARTED = "未开始"
    STATUS_IN_PROGRESS = "进行中"
    STATUS_COMPLETED = "结束"
    STATUS_SUSPENDED = "挂起"

    IMPORTANCE_HIGH = "高"
    IMPORTANCE_MEDIUM = "中"
    IMPORTANCE_LOW = "低"

    # Status colors (SiYuan select color: 1=red, 3=blue, 4=green, 5=gray)
    STATUS_COLORS = {"未开始": "5", "进行中": "4", "结束": "1", "挂起": "3"}
    IMPORTANCE_COLORS = {"高": "1", "中": "4", "低": "5"}
    URGENCY_COLORS = {"高": "1", "中": "4", "低": "5"}

    def __init__(self, skip_av=False):
        cfg = load_config()
        self.client = SiYuanClient(cfg)
        self._task_doc_id = None
        self._cfg = cfg
        if skip_av:
            self.AV_ID = None
            self.AV_BLOCK_ID = None
            self.COLUMN_IDS = {}
            return
        self.AV_ID = cfg["AV_ID"]
        self.AV_BLOCK_ID = cfg["AV_BLOCK_ID"]
        self.COLUMN_IDS = {
            "block":        cfg["COL_BLOCK"],
            "content":      cfg["COL_CONTENT"],
            "importance":   cfg["COL_IMPORTANCE"],
            "urgency":      cfg["COL_URGENCY"],
            "status":       cfg["COL_STATUS"],
            "notes":        cfg["COL_NOTES"],
            "stakeholders": cfg["COL_STAKEHOLDERS"],
            "start_time":   cfg["COL_START_TIME"],
            "end_time":     cfg["COL_END_TIME"],
            "created":      cfg["COL_CREATED"],
            "updated":      cfg["COL_UPDATED"],
        }

    @staticmethod
    def _gen_id():
        now = datetime.now().strftime("%Y%m%d%H%M%S")
        rand = "".join(random.choices(string.ascii_lowercase + string.digits, k=7))
        return f"{now}-{rand}"

    @staticmethod
    def _now_ms():
        return int(time.time() * 1000)

    def get_task_doc_id(self):
        """Find or create the 任务清单 document, return its block ID."""
        if self._task_doc_id:
            return self._task_doc_id
        r = self.client._post("/api/filetree/getIDsByHPath", {
            "path": f"/{self.TASK_DOC_NAME}",
            "notebook": self.client.notebook_id,
        })
        if r["code"] == 0 and r["data"]:
            self._task_doc_id = r["data"][0]
            return self._task_doc_id
        r = self.client.create_doc(f"/{self.TASK_DOC_NAME}", "")
        if r["code"] == 0:
            self._task_doc_id = r["data"]
            return self._task_doc_id
        raise RuntimeError(f"Failed to get/create TASK doc: {r['msg']}")

    # ── Init ──

    def _find_existing_av(self, doc_id):
        """Find an existing AV block inside the 任务清单 document.

        Returns (av_id, av_block_id) or (None, None).
        """
        r = self.client.get_child_blocks(doc_id)
        if r["code"] != 0 or not r.get("data"):
            return None, None
        for block in r["data"]:
            if block.get("type") == "av":
                av_block_id = block["id"]
                kr = self.client._post("/api/block/getBlockDOM", {"id": av_block_id})
                if kr["code"] == 0 and kr.get("data"):
                    dom = kr["data"].get("dom", "")
                    import re
                    m = re.search(r'data-av-id="([^"]+)"', dom)
                    if m:
                        return m.group(1), av_block_id
        return None, None

    def _read_existing_columns(self, av_id):
        """Read column IDs from an existing AV. Returns col_ids dict or None."""
        keys_r = self.client._post(
            "/api/av/getAttributeViewKeysByAvID", {"avID": av_id})
        if keys_r.get("code") != 0 or not keys_r.get("data"):
            return None

        name_to_key = {
            "任务内容": "content", "相关方": "stakeholders",
            "重要程度": "importance", "紧急程度": "urgency",
            "开始时间": "start_time", "结束时间": "end_time",
            "创建时间": "created", "更新时间": "updated",
            "状态": "status", "备注": "notes",
        }
        col_ids = {}
        for k in keys_r["data"]:
            if k["type"] == "block":
                col_ids["block"] = k["id"]
            elif k["name"] in name_to_key:
                col_ids[name_to_key[k["name"]]] = k["id"]

        expected = {"block", "content", "stakeholders", "importance",
                    "urgency", "start_time", "end_time", "created",
                    "updated", "status", "notes"}
        if col_ids.keys() >= expected:
            return col_ids
        return None

    def init_database(self):
        """Create or reuse 任务清单 doc and TASK database. Write IDs to config.env."""
        from pathlib import Path

        doc_id = self.get_task_doc_id()

        # Check for existing AV block in the document
        av_id, av_block_id = self._find_existing_av(doc_id)
        reused = False

        if av_id and av_block_id:
            col_ids = self._read_existing_columns(av_id)
            if col_ids:
                reused = True

        if not reused:
            # Create new AV block
            av_id = self._gen_id()
            dom = (f'<div data-av-id="{av_id}" data-av-type="table" '
                   f'data-node-id="" data-type="NodeAttributeView"></div>')
            r = self.client._post("/api/block/appendBlock", {
                "dataType": "dom", "data": dom, "parentID": doc_id,
            })
            if r["code"] != 0:
                raise RuntimeError(f"Failed to create AV block: {r['msg']}")
            av_block_id = r["data"][0]["doOperations"][0]["id"]

            # Initialize AV JSON by rendering
            self.client._post("/api/av/renderAttributeView", {
                "id": av_id, "blockID": av_block_id,
            })

            # Remove default select column
            keys_r = self.client._post(
                "/api/av/getAttributeViewKeysByAvID", {"avID": av_id})
            for k in (keys_r.get("data") or []):
                if k["type"] == "select":
                    self.client._post("/api/av/removeAttributeViewKey", {
                        "avID": av_id, "keyID": k["id"],
                    })

            # Define columns to add
            col_defs = [
                ("content",      "任务内容",  "text"),
                ("stakeholders", "相关方",    "text"),
                ("importance",   "重要程度",  "select"),
                ("urgency",      "紧急程度",  "select"),
                ("start_time",   "开始时间",  "date"),
                ("end_time",     "结束时间",  "date"),
                ("created",      "创建时间",  "created"),
                ("updated",      "更新时间",  "updated"),
                ("status",       "状态",      "select"),
                ("notes",        "备注",      "text"),
            ]

            col_ids = {}
            for key, name, ktype in col_defs:
                kid = self._gen_id()
                self.client._post("/api/av/addAttributeViewKey", {
                    "avID": av_id, "keyID": kid, "keyName": name,
                    "keyType": ktype, "keyIcon": "", "previousKeyID": "",
                })
                col_ids[key] = kid

            # Get block column ID (primary key, auto-created)
            keys_r = self.client._post(
                "/api/av/getAttributeViewKeysByAvID", {"avID": av_id})
            for k in (keys_r.get("data") or []):
                if k["type"] == "block":
                    col_ids["block"] = k["id"]
                    break

        # Write back to config.env
        config_path = Path(__file__).parent.parent / "config.env"
        lines = config_path.read_text().splitlines()

        # Remove old AV/COL lines
        lines = [l for l in lines if not l.startswith(("AV_", "COL_"))
                 and l.strip() != "# Task Database (Attribute View) Configuration"
                 and l.strip() != "# Column IDs"]

        # Remove trailing blank lines
        while lines and lines[-1].strip() == "":
            lines.pop()

        # Append new config
        lines.append("")
        lines.append("# Task Database (Attribute View) Configuration")
        lines.append(f"AV_ID={av_id}")
        lines.append(f"AV_BLOCK_ID={av_block_id}")
        lines.append("")
        lines.append("# Column IDs")
        col_map = {
            "block": "COL_BLOCK", "content": "COL_CONTENT",
            "importance": "COL_IMPORTANCE", "urgency": "COL_URGENCY",
            "status": "COL_STATUS", "notes": "COL_NOTES",
            "stakeholders": "COL_STAKEHOLDERS",
            "start_time": "COL_START_TIME", "end_time": "COL_END_TIME",
            "created": "COL_CREATED", "updated": "COL_UPDATED",
        }
        for key, env_name in col_map.items():
            lines.append(f"{env_name}={col_ids[key]}")
        lines.append("")

        config_path.write_text("\n".join(lines))

        return {"ok": True, "av_id": av_id, "av_block_id": av_block_id,
                "reused": reused}

    # ── Binding ──

    def _bind_row_to_doc(self, row_id, doc_id):
        """Convert a detached AV row to non-detached by modifying the AV JSON.

        Sets block.id to the sub-document's doc_id so the primary key shows
        a document icon linked to the sub-document.
        """
        av_path = f"/data/storage/av/{self.AV_ID}.json"
        av_data = self.client.get_file(av_path)
        if isinstance(av_data, dict) and av_data.get("code", 0) != 0:
            return False
        for kv in av_data.get("keyValues", []):
            if kv["key"]["type"] != "block":
                continue
            for v in kv["values"]:
                if v["blockID"] != row_id:
                    continue
                v.pop("isDetached", None)
                v["block"]["id"] = doc_id
                break
            break
        r = self.client.put_file(av_path, av_data)
        return r.get("code") == 0

    # ── Create ──

    def create_task(self, name, content="", notes="", stakeholders="",
                    importance="中", urgency="中", status="未开始"):
        """Create a new task row in the database with a linked sub-document."""
        row_id = self._gen_id()
        row_values = [
            {
                "keyID": self.COLUMN_IDS["block"],
                "id": self._gen_id(),
                "blockID": row_id,
                "type": "block",
                "isDetached": True,
                "block": {"content": name},
            },
            {
                "keyID": self.COLUMN_IDS["content"],
                "id": self._gen_id(),
                "blockID": row_id,
                "type": "text",
                "text": {"content": content},
            },
            {
                "keyID": self.COLUMN_IDS["importance"],
                "id": self._gen_id(),
                "blockID": row_id,
                "type": "select",
                "mSelect": [{"content": importance,
                             "color": self.IMPORTANCE_COLORS.get(importance, "5")}],
            },
            {
                "keyID": self.COLUMN_IDS["urgency"],
                "id": self._gen_id(),
                "blockID": row_id,
                "type": "select",
                "mSelect": [{"content": urgency,
                             "color": self.URGENCY_COLORS.get(urgency, "5")}],
            },
            {
                "keyID": self.COLUMN_IDS["status"],
                "id": self._gen_id(),
                "blockID": row_id,
                "type": "select",
                "mSelect": [{"content": status,
                             "color": self.STATUS_COLORS.get(status, "5")}],
            },
            {
                "keyID": self.COLUMN_IDS["notes"],
                "id": self._gen_id(),
                "blockID": row_id,
                "type": "text",
                "text": {"content": notes},
            },
            {
                "keyID": self.COLUMN_IDS["stakeholders"],
                "id": self._gen_id(),
                "blockID": row_id,
                "type": "text",
                "text": {"content": stakeholders},
            },
        ]
        r = self.client._post("/api/av/appendAttributeViewDetachedBlocksWithValues", {
            "avID": self.AV_ID,
            "blocksValues": [row_values],
        })
        if r["code"] != 0:
            return {"ok": False, "msg": r.get("msg", "")}

        # Auto-create sub-document with template
        doc_md = "# 任务描述\n\n\n# 任务附件\n\n\n# 下一步\n"
        doc_r = self.client.create_doc(f"/{self.TASK_DOC_NAME}/{name}", doc_md)
        doc_id = doc_r["data"] if doc_r["code"] == 0 else None

        # Bind the row to the sub-document (non-detached primary key)
        if doc_id:
            self._bind_row_to_doc(row_id, doc_id)

        return {"ok": True, "row_id": row_id, "name": name, "doc_id": doc_id}

    # ── Query ──

    def _render_av(self):
        """Render the attribute view and return all rows with parsed fields."""
        r = self.client._post("/api/av/renderAttributeView", {
            "id": self.AV_ID,
            "blockID": self.AV_BLOCK_ID,
        })
        if r["code"] != 0 or not r.get("data"):
            return []
        return r["data"]["view"].get("rows", [])

    @staticmethod
    def _extract_cell(cell):
        """Extract display value from a single cell."""
        v = cell.get("value", {})
        t = v.get("type", "")
        if t == "block":
            return v.get("block", {}).get("content", "")
        if t == "text":
            return v.get("text", {}).get("content", "")
        if t == "select":
            items = v.get("mSelect") or []
            return items[0]["content"] if items else ""
        if t in ("date", "created", "updated"):
            sub = v.get(t, {})
            fc = sub.get("formattedContent", "")
            if fc:
                return fc
            ts = sub.get("content", 0)
            if ts and sub.get("isNotEmpty"):
                return datetime.fromtimestamp(ts / 1000).strftime("%Y-%m-%d %H:%M")
            return ""
        return ""

    def _row_to_task(self, row, columns):
        """Convert a rendered row into a task dict."""
        task = {"row_id": row["id"]}
        col_map = {c["id"]: c["name"] for c in columns}
        for cell in row.get("cells", []):
            key_id = cell.get("value", {}).get("keyID", "")
            col_name = col_map.get(key_id, key_id)
            task[col_name] = self._extract_cell(cell)
        return task

    def list_tasks(self):
        """List all tasks from the database."""
        r = self.client._post("/api/av/renderAttributeView", {
            "id": self.AV_ID,
            "blockID": self.AV_BLOCK_ID,
        })
        if r["code"] != 0 or not r.get("data"):
            return []
        view = r["data"]["view"]
        columns = view.get("columns", [])
        rows = view.get("rows", [])
        return [self._row_to_task(row, columns) for row in rows]

    def find_tasks_by_status(self, status):
        """Find tasks filtered by status value."""
        tasks = self.list_tasks()
        return [t for t in tasks if t.get("状态") == status]

    # ── Update ──

    def _set_cell(self, row_id, col_key, value_obj):
        """Update a single cell in the database."""
        key_id = self.COLUMN_IDS[col_key]
        return self.client._post("/api/av/setAttributeViewBlockAttr", {
            "avID": self.AV_ID,
            "keyID": key_id,
            "rowID": row_id,
            "value": value_obj,
        })

    def update_task_status(self, row_id, status):
        """Update the status select cell for a task row."""
        color = self.STATUS_COLORS.get(status, "5")
        return self._set_cell(row_id, "status", {
            "type": "select",
            "mSelect": [{"content": status, "color": color}],
        })

    def update_task_text(self, row_id, col_key, text):
        """Update a text cell for a task row."""
        return self._set_cell(row_id, col_key, {
            "type": "text",
            "text": {"content": text},
        })

    def update_task_date(self, row_id, col_key, timestamp_ms):
        """Update a date cell for a task row."""
        return self._set_cell(row_id, col_key, {
            "type": "date",
            "date": {"content": timestamp_ms, "isNotEmpty": True},
        })

    def start_task(self, row_id):
        """Set task status to in-progress and record start time."""
        self.update_task_status(row_id, "进行中")
        self.update_task_date(row_id, "start_time", self._now_ms())
        return {"ok": True}

    def complete_task(self, row_id):
        """Set task status to completed and record end time."""
        self.update_task_status(row_id, "结束")
        self.update_task_date(row_id, "end_time", self._now_ms())
        return {"ok": True}

    def suspend_task(self, row_id):
        """Set task status to suspended."""
        self.update_task_status(row_id, "挂起")
        return {"ok": True}

    def _get_task_name(self, row_id):
        """Get the task name (primary key) for a given row_id."""
        tasks = self.list_tasks()
        for t in tasks:
            if t["row_id"] == row_id:
                return t.get("主键", "")
        return ""

    def _find_sub_doc_id(self, task_name):
        """Find the sub-document ID by task name."""
        r = self.client._post("/api/filetree/getIDsByHPath", {
            "path": f"/{self.TASK_DOC_NAME}/{task_name}",
            "notebook": self.client.notebook_id,
        })
        if r["code"] == 0 and r["data"]:
            return r["data"][0]
        return None

    def rename_task(self, row_id, new_name):
        """Rename a task and its associated sub-document."""
        old_name = self._get_task_name(row_id)
        if not old_name:
            return {"ok": False, "msg": f"Task {row_id} not found"}

        # Update the block primary key in the AV
        self._set_cell(row_id, "block", {
            "type": "block",
            "block": {"content": new_name},
        })

        # Rename the associated sub-document
        doc_id = self._find_sub_doc_id(old_name)
        if doc_id:
            self.client.rename_doc_by_id(doc_id, new_name)

        return {"ok": True, "old_name": old_name, "new_name": new_name}

    # ── Attachments ──

    def _find_heading_block(self, doc_id, heading_text):
        """Find a heading block by text within a document."""
        r = self.client.get_child_blocks(doc_id)
        if r["code"] != 0 or not r.get("data"):
            return None
        for block in r["data"]:
            if block.get("type") == "h" and block.get("content") == heading_text:
                return block["id"]
        return None

    def attach_image_to_task(self, row_id, file_path, section="任务附件"):
        """Upload an image and insert it into a task's sub-document section."""
        task_name = self._get_task_name(row_id)
        if not task_name:
            return {"ok": False, "msg": f"Task {row_id} not found"}

        doc_id = self._find_sub_doc_id(task_name)
        if not doc_id:
            return {"ok": False, "msg": f"Sub-document for '{task_name}' not found"}

        # Upload asset
        r = self.client.upload_asset(file_path)
        if r["code"] != 0 or not r.get("data", {}).get("succMap"):
            return {"ok": False, "msg": r.get("msg", "Upload failed")}

        filename = list(r["data"]["succMap"].keys())[0]
        asset_path = r["data"]["succMap"][filename]

        # Find the target heading block
        heading_id = self._find_heading_block(doc_id, section)
        if not heading_id:
            return {"ok": False, "msg": f"Heading '{section}' not found in sub-document"}

        # Insert image after the heading
        md = f"![{filename}]({asset_path})"
        ir = self.client.insert_block(md, previous_id=heading_id)
        if ir["code"] != 0:
            return {"ok": False, "msg": ir.get("msg", "Insert failed")}

        block_id = ir["data"][0]["doOperations"][0]["id"]
        return {"ok": True, "asset_path": asset_path, "block_id": block_id}

    # ── Sub-documents ──

    def list_sub_docs(self):
        """List all sub-documents under 任务清单."""
        r = self.client.sql_query(
            f"SELECT id, content, hpath FROM blocks "
            f"WHERE type = 'd' AND hpath LIKE '/{self.TASK_DOC_NAME}/%' "
            f"AND box = '{self.client.notebook_id}'"
        )
        if r["code"] != 0 or not r["data"]:
            return []
        return [{"doc_id": d["id"], "title": d["content"], "path": d["hpath"]}
                for d in r["data"]]

    # ── Delete ──

    def delete_task(self, row_id):
        """Delete a task row and its associated sub-document."""
        # Find task name to locate sub-document
        task_name = self._get_task_name(row_id)
        if task_name:
            doc_id = self._find_sub_doc_id(task_name)
            if doc_id:
                self.client.remove_doc_by_id(doc_id)

        # Delete the AV row
        r = self.client._post("/api/av/removeAttributeViewBlocks", {
            "avID": self.AV_ID,
            "srcIDs": [row_id],
        })
        return {"ok": r["code"] == 0, "msg": r.get("msg", "")}

    # ── Migration ──

    def reorder_columns(self):
        """Reorder columns in the view to the desired display order."""
        desired_order = [
            "block", "content", "stakeholders", "importance", "urgency",
            "status", "notes", "created", "start_time", "end_time", "updated",
        ]
        prev_id = ""
        for col_key in desired_order:
            key_id = self.COLUMN_IDS.get(col_key)
            if not key_id:
                continue
            self.client._post("/api/av/sortAttributeViewViewKey", {
                "avID": self.AV_ID,
                "keyID": key_id,
                "previousKeyID": prev_id,
            })
            prev_id = key_id
        return {"ok": True}

    def migrate(self):
        """Apply schema changes to existing database: remove 相关文档, reorder columns, bind rows."""
        results = {}

        # Remove 相关文档 column if it exists
        old_col_id = self._cfg.get("COL_RELATED_DOCS")
        if old_col_id:
            r = self.client._post("/api/av/removeAttributeViewKey", {
                "avID": self.AV_ID,
                "keyID": old_col_id,
            })
            results["remove_related_docs"] = r["code"] == 0

        # Bind detached rows that have sub-documents
        bound = self.bind_all_detached()
        results["bound_rows"] = bound

        # Reorder columns
        self.reorder_columns()
        results["reorder"] = True

        return {"ok": True, **results}

    def bind_all_detached(self):
        """Find rows needing binding and bind them to their sub-documents."""
        tasks = self.list_tasks()
        av_path = f"/data/storage/av/{self.AV_ID}.json"
        av_data = self.client.get_file(av_path)
        if isinstance(av_data, dict) and av_data.get("code", 0) != 0:
            return []

        # Build lookup: row_id -> block value from AV JSON
        block_vals = {}
        for kv in av_data.get("keyValues", []):
            if kv["key"]["type"] == "block":
                for v in kv["values"]:
                    block_vals[v["blockID"]] = v
                break

        bound = []
        for t in tasks:
            row_id = t["row_id"]
            name = t.get("主键", "")
            if not name:
                continue
            doc_id = self._find_sub_doc_id(name)
            if not doc_id:
                continue
            bv = block_vals.get(row_id)
            if not bv:
                continue
            # Bind if detached or if block.id doesn't match doc_id
            needs_bind = bv.get("isDetached") or bv["block"].get("id") != doc_id
            if needs_bind and self._bind_row_to_doc(row_id, doc_id):
                bound.append(name)
        return bound


# ── CLI entry point ──

def main():
    if len(sys.argv) < 2:
        print("Usage: task_ops.py <command> [args...]")
        print("Commands: init, create, list, find, start, complete, suspend,")
        print("          rename, attach-image, list-docs, delete, migrate")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "init":
        tm = TaskManager(skip_av=True)
        result = tm.init_database()
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    tm = TaskManager()

    if cmd == "create":
        name = sys.argv[2] if len(sys.argv) > 2 else "Untitled Task"
        opts = {}
        for arg in sys.argv[3:]:
            if "=" in arg:
                k, v = arg.split("=", 1)
                opts[k] = v
        result = tm.create_task(name, **opts)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif cmd == "list":
        tasks = tm.list_tasks()
        print(json.dumps(tasks, ensure_ascii=False, indent=2))

    elif cmd == "find":
        status = sys.argv[2] if len(sys.argv) > 2 else "进行中"
        tasks = tm.find_tasks_by_status(status)
        print(json.dumps(tasks, ensure_ascii=False, indent=2))

    elif cmd == "start":
        result = tm.start_task(sys.argv[2])
        print(json.dumps(result, ensure_ascii=False))

    elif cmd == "complete":
        result = tm.complete_task(sys.argv[2])
        print(json.dumps(result, ensure_ascii=False))

    elif cmd == "suspend":
        result = tm.suspend_task(sys.argv[2])
        print(json.dumps(result, ensure_ascii=False))

    elif cmd == "rename":
        result = tm.rename_task(sys.argv[2], sys.argv[3])
        print(json.dumps(result, ensure_ascii=False))

    elif cmd == "list-docs":
        docs = tm.list_sub_docs()
        print(json.dumps(docs, ensure_ascii=False, indent=2))

    elif cmd == "attach-image":
        section = "任务附件"
        for arg in sys.argv[4:]:
            if arg.startswith("section="):
                section = arg.split("=", 1)[1]
        result = tm.attach_image_to_task(sys.argv[2], sys.argv[3], section)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif cmd == "delete":
        result = tm.delete_task(sys.argv[2])
        print(json.dumps(result, ensure_ascii=False))

    elif cmd == "migrate":
        result = tm.migrate()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)


if __name__ == "__main__":
    main()
