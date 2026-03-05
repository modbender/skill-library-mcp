#!/usr/bin/env python3
import argparse
import json
import os
import sys
import requests
from requests.auth import HTTPBasicAuth
from urllib.parse import quote

# ---------- Error Class ----------

class OpenKMError(RuntimeError):
    pass

# ---------- Client ----------

class OpenKMClient:
    def __init__(self, base_url, username, password, debug=False):
        if base_url.rstrip("/").endswith("/OpenKM"):
            raise OpenKMError("OPENKM_BASE_URL must NOT end with /OpenKM")
        self.base_url = base_url.rstrip("/")
        self.auth = HTTPBasicAuth(username, password)
        self.debug = debug

    def _dbg(self, msg):
        if self.debug:
            print(f"[DEBUG] {msg}", file=sys.stderr)

    def _req(self, method, endpoint, **kw):
        url = self.base_url + endpoint
        self._dbg(f"{method} {url}")
        r = requests.request(method, url, auth=self.auth, timeout=30, **kw)
        self._dbg(f"→ {r.status_code} {r.text[:200]}")
        return r

    # ---------- Folder ----------

    def get_folder(self, path):
        r = self._req("GET", f"/OpenKM/services/rest/folder/getPath/{quote(path, safe='')}")
        if r.status_code == 200:
            return r.json()
        if r.status_code == 404:
            return None
        raise OpenKMError(r.text)

    def create_folder(self, path):
        # API expects Content-Type: application/xml with path as raw string body
        r = self._req(
            "POST",
            "/OpenKM/services/rest/folder/createSimple",
            data=path,
            headers={"Content-Type": "application/xml", "Accept": "application/json"},
        )
        if r.status_code in (200, 201):
            return r.json()
        if r.status_code == 409 or "ItemExistsException" in r.text:
            return self.get_folder(path)
        raise OpenKMError(f"{r.status_code}: {r.text}")

    def ensure_structure(self, parts, root="/okm:root"):
        path = root
        for p in parts:
            path += f"/{p}"
            if not self.get_folder(path):
                self.create_folder(path)
        return path

    def list_children(self, path):
        r = self._req(
            "GET",
            f"/OpenKM/services/rest/folder/getChildren?fldId={quote(path, safe='')}",
            headers={"Accept": "application/json"},
        )
        if r.status_code == 200:
            data = r.json()
            # API returns {"folder": [...]} or {"folder": {...}} for single item
            if isinstance(data, dict) and "folder" in data:
                folder_data = data["folder"]
                if isinstance(folder_data, list):
                    return folder_data
                else:
                    return [folder_data]
            return data
        if r.status_code == 404:
            return []
        raise OpenKMError(r.text)

    # ---------- Document ----------

    def upload(self, okm_path, local_path):
        # API expects multipart/form-data with docPath and content fields
        with open(local_path, "rb") as f:
            files = {
                "docPath": (None, okm_path),
                "content": (os.path.basename(local_path), f, "application/pdf"),
            }
            r = self._req(
                "POST",
                "/OpenKM/services/rest/document/createSimple",
                files=files,
                headers={"Accept": "application/json"},
            )
        if r.status_code in (200, 201):
            return r.json()
        if r.status_code == 500 and "ItemExistsException" in r.text:
            raise OpenKMError(f"Document already exists: {okm_path}")
        raise OpenKMError(f"{r.status_code}: {r.text}")

    def download(self, doc_id, local_path):
        r = self._req(
            "GET",
            f"/OpenKM/services/rest/document/getContent/{quote(doc_id, safe='')}",
            stream=True,
        )
        if r.status_code == 200:
            with open(local_path, "wb") as f:
                for c in r.iter_content(8192):
                    f.write(c)
            return True
        if r.status_code == 404:
            return False
        raise OpenKMError(r.text)

    def move(self, doc_id, target):
        # API uses query parameters for docId and dstId
        r = self._req(
            "PUT",
            f"/OpenKM/services/rest/document/move?docId={quote(doc_id, safe='')}&dstId={quote(target, safe='')}",
            headers={"Accept": "application/json"},
        )
        if r.status_code in (200, 201, 204):
            return {"moved": True, "docId": doc_id, "to": target}
        raise OpenKMError(f"{r.status_code}: {r.text}")

    def rename(self, doc_id, new_name):
        # API uses query parameters for docId and newName
        r = self._req(
            "PUT",
            f"/OpenKM/services/rest/document/rename?docId={quote(doc_id, safe='')}&newName={quote(new_name, safe='')}",
            headers={"Accept": "application/json"},
        )
        if r.status_code in (200, 201):
            return r.json()
        raise OpenKMError(f"{r.status_code}: {r.text}")

    def delete(self, doc_id):
        r = self._req(
            "DELETE",
            f"/OpenKM/services/rest/document/delete?docId={quote(doc_id, safe='')}",
        )
        return r.status_code in (200, 204)

    # ---------- Metadata & Organization ----------

    def get_properties(self, doc_id):
        """Get document properties (title, description, keywords, categories)"""
        r = self._req(
            "GET",
            f"/OpenKM/services/rest/document/getProperties?docId={quote(doc_id, safe='')}",
            headers={"Accept": "application/json"},
        )
        if r.status_code == 200:
            return r.json()
        raise OpenKMError(f"{r.status_code}: {r.text}")

    def add_keyword(self, doc_id, keyword):
        """Add a keyword to a document"""
        r = self._req(
            "POST",
            f"/OpenKM/services/rest/property/addKeyword?nodeId={quote(doc_id, safe='')}&keyword={quote(keyword, safe='')}",
            headers={"Accept": "application/json"},
        )
        if r.status_code in (200, 201, 204):
            return {"added": True, "keyword": keyword}
        raise OpenKMError(f"{r.status_code}: {r.text}")

    def remove_keyword(self, doc_id, keyword):
        """Remove a keyword from a document"""
        r = self._req(
            "DELETE",
            f"/OpenKM/services/rest/property/removeKeyword?nodeId={quote(doc_id, safe='')}&keyword={quote(keyword, safe='')}",
            headers={"Accept": "application/json"},
        )
        if r.status_code in (200, 204):
            return {"removed": True, "keyword": keyword}
        raise OpenKMError(f"{r.status_code}: {r.text}")

    def add_category(self, doc_id, category_id):
        """Add a category to a document (category_id is a UUID or path)"""
        r = self._req(
            "POST",
            f"/OpenKM/services/rest/property/addCategory?nodeId={quote(doc_id, safe='')}&catId={quote(category_id, safe='')}",
            headers={"Accept": "application/json"},
        )
        if r.status_code in (200, 201, 204):
            return {"added": True, "category": category_id}
        raise OpenKMError(f"{r.status_code}: {r.text}")

    def remove_category(self, doc_id, category_id):
        """Remove a category from a document"""
        r = self._req(
            "DELETE",
            f"/OpenKM/services/rest/property/removeCategory?nodeId={quote(doc_id, safe='')}&catId={quote(category_id, safe='')}",
            headers={"Accept": "application/json"},
        )
        if r.status_code in (200, 204):
            return {"removed": True, "category": category_id}
        raise OpenKMError(f"{r.status_code}: {r.text}")

    def set_properties(self, doc_id, title=None, description=None):
        """Update document title and/or description"""
        # First get current properties
        props = self.get_properties(doc_id)
        
        # Update fields
        if title is not None:
            props["title"] = title
        if description is not None:
            props["description"] = description
        
        # Send back
        r = self._req(
            "PUT",
            "/OpenKM/services/rest/document/setProperties",
            json=props,
            headers={"Content-Type": "application/json", "Accept": "application/json"},
        )
        if r.status_code in (200, 201, 204):
            return {"updated": True, "title": title, "description": description}
        raise OpenKMError(f"{r.status_code}: {r.text}")

    # ---------- Versioning ----------

    def get_version_history(self, doc_id):
        """Get document version history"""
        r = self._req(
            "GET",
            f"/OpenKM/services/rest/document/getVersionHistory?docId={quote(doc_id, safe='')}",
            headers={"Accept": "application/json"},
        )
        if r.status_code == 200:
            data = r.json()
            # API returns {"version": [...]} or single version object
            if isinstance(data, dict) and "version" in data:
                versions = data["version"]
                return versions if isinstance(versions, list) else [versions]
            return data
        raise OpenKMError(f"{r.status_code}: {r.text}")

    def checkout(self, doc_id):
        """Checkout a document for editing (creates a new version draft)"""
        r = self._req(
            "GET",
            f"/OpenKM/services/rest/document/checkout?docId={quote(doc_id, safe='')}",
        )
        if r.status_code in (200, 204):
            return {"checkedOut": True, "docId": doc_id}
        raise OpenKMError(f"{r.status_code}: {r.text}")

    def cancel_checkout(self, doc_id):
        """Cancel checkout and discard changes"""
        r = self._req(
            "PUT",
            f"/OpenKM/services/rest/document/cancelCheckout?docId={quote(doc_id, safe='')}",
            headers={"Accept": "application/json"},
        )
        if r.status_code in (200, 201, 204):
            return {"cancelled": True, "docId": doc_id}
        raise OpenKMError(f"{r.status_code}: {r.text}")

    def checkin(self, doc_id, local_path, comment=""):
        """Checkin a document with new content (creates a new version)
        
        Args:
            doc_id: Document UUID
            local_path: Path to local file with new content
            comment: Optional version comment
        """
        with open(local_path, "rb") as f:
            files = {
                "content": (os.path.basename(local_path), f, "application/octet-stream"),
            }
            data = {"docId": doc_id, "comment": comment}
            r = self._req(
                "POST",
                "/OpenKM/services/rest/document/checkin",
                files=files,
                data=data,
                headers={"Accept": "application/json"},
            )
        if r.status_code in (200, 201):
            return r.json()
        raise OpenKMError(f"{r.status_code}: {r.text}")

    def set_content(self, doc_id, local_path):
        """Update document content (creates new version in OpenKM)"""
        with open(local_path, "rb") as f:
            r = self._req(
                "PUT",
                f"/OpenKM/services/rest/document/setContent?docId={quote(doc_id, safe='')}",
                data=f,
                headers={"Accept": "application/json"},
            )
        if r.status_code in (200, 201, 204):
            return {"updated": True, "docId": doc_id}
        raise OpenKMError(f"{r.status_code}: {r.text}")

    def upload_version(self, doc_path, local_path, comment=""):
        """Upload a new version of an existing document
        
        Performs: checkout → checkin workflow
        """
        # First get document ID from path
        doc = self.get_document_by_path(doc_path)
        if not doc:
            raise OpenKMError(f"Document not found: {doc_path}")
        
        doc_id = doc.get("uuid") or doc.get("docId")
        
        # Checkout
        self.checkout(doc_id)
        
        try:
            # Checkin with new content
            result = self.checkin(doc_id, local_path, comment)
            return result
        except Exception as e:
            # Cancel checkout on error
            try:
                self.cancel_checkout(doc_id)
            except:
                pass
            raise e

    def get_document_by_path(self, path):
        """Get document info by path using search"""
        # Use search to find document by exact path
        r = self._req(
            "GET",
            f"/OpenKM/services/rest/search/findByName?name={quote(os.path.basename(path), safe='')}",
            headers={"Accept": "application/json"},
        )
        if r.status_code == 200:
            data = r.json()
            if isinstance(data, dict) and "queryResult" in data:
                results = data["queryResult"]
                if not isinstance(results, list):
                    results = [results]
                # Find exact path match
                for result in results:
                    node = result.get("node", {})
                    if node.get("path") == path:
                        return node
        return None

    def restore_version(self, doc_id, version_name):
        """Restore document to a specific version"""
        r = self._req(
            "PUT",
            f"/OpenKM/services/rest/document/restoreVersion?docId={quote(doc_id, safe='')}&versionId={quote(version_name, safe='')}",
            headers={"Accept": "application/json"},
        )
        if r.status_code in (200, 201, 204):
            return {"restored": True, "docId": doc_id, "version": version_name}
        raise OpenKMError(f"{r.status_code}: {r.text}")

    def download_version(self, doc_id, version_name, local_path):
        """Download a specific version of a document"""
        r = self._req(
            "GET",
            f"/OpenKM/services/rest/document/getContentByVersion?docId={quote(doc_id, safe='')}&versionId={quote(version_name, safe='')}",
            stream=True,
        )
        if r.status_code == 200:
            with open(local_path, "wb") as f:
                for c in r.iter_content(8192):
                    f.write(c)
            return True
        if r.status_code == 404:
            return False
        raise OpenKMError(r.text)

    # ---------- Search ----------

    def search_by_content(self, content):
        """Search documents by content (full-text search)"""
        r = self._req(
            "GET",
            f"/OpenKM/services/rest/search/findByContent?content={quote(content, safe='')}",
            headers={"Accept": "application/json"},
        )
        if r.status_code == 200:
            data = r.json()
            # API returns {"queryResult": [...]} or single result
            if isinstance(data, dict) and "queryResult" in data:
                results = data["queryResult"]
                return results if isinstance(results, list) else [results]
            return data
        raise OpenKMError(f"{r.status_code}: {r.text}")

    def search_by_name(self, name):
        """Search documents by name/filename"""
        r = self._req(
            "GET",
            f"/OpenKM/services/rest/search/findByName?name={quote(name, safe='')}",
            headers={"Accept": "application/json"},
        )
        if r.status_code == 200:
            data = r.json()
            if isinstance(data, dict) and "queryResult" in data:
                results = data["queryResult"]
                return results if isinstance(results, list) else [results]
            return data
        raise OpenKMError(f"{r.status_code}: {r.text}")

    def search_by_keywords(self, keywords):
        """Search documents by keywords (comma-separated)"""
        keyword_list = [k.strip() for k in keywords.split(",")]
        params = "".join([f"&keyword={quote(k, safe='')}" for k in keyword_list])
        r = self._req(
            "GET",
            f"/OpenKM/services/rest/search/findByKeywords?{params[1:]}",  # Remove leading &
            headers={"Accept": "application/json"},
        )
        if r.status_code == 200:
            data = r.json()
            if isinstance(data, dict) and "queryResult" in data:
                results = data["queryResult"]
                return results if isinstance(results, list) else [results]
            return data
        raise OpenKMError(f"{r.status_code}: {r.text}")

    def search(self, content=None, name=None, path=None, author=None):
        """General search with multiple filters"""
        params = []
        if content:
            params.append(f"content={quote(content, safe='')}")
        if name:
            params.append(f"name={quote(name, safe='')}")
        if path:
            params.append(f"path={quote(path, safe='')}")
        if author:
            params.append(f"author={quote(author, safe='')}")
        
        query_string = "&".join(params) if params else ""
        endpoint = f"/OpenKM/services/rest/search/find?{query_string}" if query_string else "/OpenKM/services/rest/search/find"
        
        r = self._req(
            "GET",
            endpoint,
            headers={"Accept": "application/json"},
        )
        if r.status_code == 200:
            data = r.json()
            if isinstance(data, dict) and "queryResult" in data:
                results = data["queryResult"]
                return results if isinstance(results, list) else [results]
            return data
        raise OpenKMError(f"{r.status_code}: {r.text}")

    # ---------- Workflows ----------

    def list_workflows(self):
        """List all available workflow process definitions"""
        r = self._req(
            "GET",
            "/OpenKM/services/rest/workflow/getAllProcessDefinitions",
            headers={"Accept": "application/json"},
        )
        if r.status_code == 200:
            data = r.json()
            # API returns {"processDefinition": [...]} or single object
            if isinstance(data, dict) and "processDefinition" in data:
                defs = data["processDefinition"]
                return defs if isinstance(defs, list) else [defs]
            return data
        raise OpenKMError(f"{r.status_code}: {r.text}")

    def find_workflows(self, name):
        """Find workflow process definitions by name"""
        r = self._req(
            "GET",
            f"/OpenKM/services/rest/workflow/getAllProcessDefinitionsByName?name={quote(name, safe='')}",
            headers={"Accept": "application/json"},
        )
        if r.status_code == 200:
            data = r.json()
            if isinstance(data, dict) and "processDefinition" in data:
                defs = data["processDefinition"]
                return defs if isinstance(defs, list) else [defs]
            return data
        raise OpenKMError(f"{r.status_code}: {r.text}")

    def start_workflow(self, workflow_uuid, doc_id=None, values=None):
        """Start a workflow instance
        
        Args:
            workflow_uuid: UUID of the process definition
            doc_id: Optional document UUID to associate
            values: Optional dict of workflow variable values
        """
        params = f"uuid={quote(workflow_uuid, safe='')}"
        if doc_id:
            params += f"&nodeId={quote(doc_id, safe='')}"
        
        # Prepare form data for values
        data = values or {}
        
        r = self._req(
            "POST",
            f"/OpenKM/services/rest/workflow/runProcessDefinition?{params}",
            data=data,
            headers={"Accept": "application/json"},
        )
        if r.status_code in (200, 201, 204):
            if r.text:
                return r.json()
            return {"started": True, "workflow": workflow_uuid, "document": doc_id}
        raise OpenKMError(f"{r.status_code}: {r.text}")

    def get_tasks(self, doc_id=None, actor_id=None):
        """Get workflow tasks for a document or actor"""
        if doc_id:
            endpoint = f"/OpenKM/services/rest/workflow/findTaskInstances?nodeId={quote(doc_id, safe='')}"
        elif actor_id:
            endpoint = f"/OpenKM/services/rest/workflow/findTaskInstancesByActor?actorId={quote(actor_id, safe='')}"
        else:
            raise OpenKMError("Either doc_id or actor_id must be provided")
        
        r = self._req(
            "GET",
            endpoint,
            headers={"Accept": "application/json"},
        )
        if r.status_code == 200:
            data = r.json()
            # API returns {"taskInstance": [...]} or single object
            if isinstance(data, dict) and "taskInstance" in data:
                tasks = data["taskInstance"]
                return tasks if isinstance(tasks, list) else [tasks]
            return data
        raise OpenKMError(f"{r.status_code}: {r.text}")

    def complete_task(self, task_id, values=None, transition=""):
        """Complete a workflow task
        
        Args:
            task_id: Task instance ID
            values: Optional dict of task variable values
            transition: Optional transition name
        """
        params = f"taskInstanceId={quote(task_id, safe='')}"
        if transition:
            params += f"&transitionName={quote(transition, safe='')}"
        
        data = values or {}
        
        r = self._req(
            "POST",
            f"/OpenKM/services/rest/workflow/setTaskInstanceValues?{params}",
            data=data,
            headers={"Accept": "application/json"},
        )
        if r.status_code in (200, 201, 204):
            return {"completed": True, "task": task_id}
        raise OpenKMError(f"{r.status_code}: {r.text}")

    def add_task_comment(self, task_id, message):
        """Add a comment to a workflow task"""
        r = self._req(
            "POST",
            f"/OpenKM/services/rest/workflow/addTaskInstanceComment?taskInstanceId={quote(task_id, safe='')}&message={quote(message, safe='')}",
            headers={"Accept": "application/json"},
        )
        if r.status_code in (200, 201, 204):
            return {"commented": True, "task": task_id}
        raise OpenKMError(f"{r.status_code}: {r.text}")

    def assign_task(self, task_id, actor_id):
        """Assign a task to an actor"""
        r = self._req(
            "POST",
            f"/OpenKM/services/rest/workflow/setTaskInstanceActor?taskInstanceId={quote(task_id, safe='')}&actorId={quote(actor_id, safe='')}",
            headers={"Accept": "application/json"},
        )
        if r.status_code in (200, 201, 204):
            return {"assigned": True, "task": task_id, "actor": actor_id}
        raise OpenKMError(f"{r.status_code}: {r.text}")

# ---------- CLI ----------

def env(name):
    v = os.getenv(name)
    if not v:
        raise OpenKMError(f"Missing environment variable: {name}")
    return v

def main():
    p = argparse.ArgumentParser()
    sp = p.add_subparsers(dest="cmd", required=True)

    sp.add_parser("list").add_argument("--folder-path", required=True)

    s = sp.add_parser("ensure-structure")
    s.add_argument("--parts", nargs="+", required=True)

    s = sp.add_parser("upload")
    s.add_argument("--okm-path", required=True)
    s.add_argument("--local-path", required=True)

    s = sp.add_parser("download")
    s.add_argument("--doc-id", required=True)
    s.add_argument("--local-path", required=True)

    s = sp.add_parser("move")
    s.add_argument("--doc-id", required=True)
    s.add_argument("--target-path", required=True)

    s = sp.add_parser("rename")
    s.add_argument("--doc-id", required=True)
    s.add_argument("--new-name", required=True)

    s = sp.add_parser("delete")
    s.add_argument("--doc-id", required=True)

    # Metadata commands
    s = sp.add_parser("properties")
    s.add_argument("--doc-id", required=True)

    s = sp.add_parser("add-keyword")
    s.add_argument("--doc-id", required=True)
    s.add_argument("--keyword", required=True)

    s = sp.add_parser("remove-keyword")
    s.add_argument("--doc-id", required=True)
    s.add_argument("--keyword", required=True)

    s = sp.add_parser("add-category")
    s.add_argument("--doc-id", required=True)
    s.add_argument("--category-id", required=True)

    s = sp.add_parser("remove-category")
    s.add_argument("--doc-id", required=True)
    s.add_argument("--category-id", required=True)

    s = sp.add_parser("set-properties")
    s.add_argument("--doc-id", required=True)
    s.add_argument("--title", default=None)
    s.add_argument("--description", default=None)

    # Versioning commands
    s = sp.add_parser("versions")
    s.add_argument("--doc-id", required=True)

    s = sp.add_parser("restore-version")
    s.add_argument("--doc-id", required=True)
    s.add_argument("--version", required=True, help="Version name (e.g., 1.0, 1.1)")

    s = sp.add_parser("download-version")
    s.add_argument("--doc-id", required=True)
    s.add_argument("--version", required=True, help="Version name")
    s.add_argument("--local-path", required=True)

    # Checkout/Checkin commands
    s = sp.add_parser("checkout")
    s.add_argument("--doc-id", required=True, help="Document UUID to checkout")

    s = sp.add_parser("cancel-checkout")
    s.add_argument("--doc-id", required=True, help="Document UUID to cancel checkout")

    s = sp.add_parser("checkin")
    s.add_argument("--doc-id", required=True, help="Document UUID to checkin")
    s.add_argument("--local-path", required=True, help="Path to file with new content")
    s.add_argument("--comment", default="", help="Version comment")

    s = sp.add_parser("upload-version")
    s.add_argument("--okm-path", required=True, help="Document path in OpenKM (e.g., /okm:root/file.pdf)")
    s.add_argument("--local-path", required=True, help="Path to local file with new content")
    s.add_argument("--comment", default="", help="Version comment")

    # Search commands
    s = sp.add_parser("search-content")
    s.add_argument("--content", required=True, help="Full-text search query")

    s = sp.add_parser("search-name")
    s.add_argument("--name", required=True, help="Filename pattern")

    s = sp.add_parser("search-keywords")
    s.add_argument("--keywords", required=True, help="Comma-separated keywords")

    s = sp.add_parser("search")
    s.add_argument("--content", default=None, help="Full-text search")
    s.add_argument("--name", default=None, help="Filename pattern")
    s.add_argument("--path", default=None, help="Path filter")
    s.add_argument("--author", default=None, help="Author filter")

    # Workflow commands
    s = sp.add_parser("workflows")
    s.add_argument("--name", default=None, help="Filter workflows by name")

    s = sp.add_parser("start-workflow")
    s.add_argument("--workflow-uuid", required=True, help="Workflow definition UUID")
    s.add_argument("--doc-id", default=None, help="Optional document UUID to associate")

    s = sp.add_parser("tasks")
    s.add_argument("--doc-id", default=None, help="Filter tasks by document")
    s.add_argument("--actor-id", default=None, help="Filter tasks by actor")

    s = sp.add_parser("complete-task")
    s.add_argument("--task-id", required=True, help="Task instance ID")
    s.add_argument("--transition", default="", help="Transition name")

    s = sp.add_parser("comment-task")
    s.add_argument("--task-id", required=True, help="Task instance ID")
    s.add_argument("--message", required=True, help="Comment text")

    s = sp.add_parser("assign-task")
    s.add_argument("--task-id", required=True, help="Task instance ID")
    s.add_argument("--actor-id", required=True, help="Actor to assign")

    args = p.parse_args()

    cli = OpenKMClient(
        env("OPENKM_BASE_URL"),
        env("OPENKM_USERNAME"),
        env("OPENKM_PASSWORD"),
        debug=os.getenv("OPENKM_DEBUG") == "1",
    )

    if args.cmd == "ensure-structure":
        print(json.dumps({"path": cli.ensure_structure(args.parts)}, indent=2))
    elif args.cmd == "list":
        print(json.dumps(cli.list_children(args.folder_path), indent=2))
    elif args.cmd == "upload":
        print(json.dumps(cli.upload(args.okm_path, args.local_path), indent=2))
    elif args.cmd == "download":
        print(json.dumps({"ok": cli.download(args.doc_id, args.local_path)}, indent=2))
    elif args.cmd == "move":
        print(json.dumps(cli.move(args.doc_id, args.target_path), indent=2))
    elif args.cmd == "rename":
        print(json.dumps(cli.rename(args.doc_id, args.new_name), indent=2))
    elif args.cmd == "delete":
        print(json.dumps({"ok": cli.delete(args.doc_id)}, indent=2))
    elif args.cmd == "properties":
        print(json.dumps(cli.get_properties(args.doc_id), indent=2))
    elif args.cmd == "add-keyword":
        print(json.dumps(cli.add_keyword(args.doc_id, args.keyword), indent=2))
    elif args.cmd == "remove-keyword":
        print(json.dumps(cli.remove_keyword(args.doc_id, args.keyword), indent=2))
    elif args.cmd == "add-category":
        print(json.dumps(cli.add_category(args.doc_id, args.category_id), indent=2))
    elif args.cmd == "remove-category":
        print(json.dumps(cli.remove_category(args.doc_id, args.category_id), indent=2))
    elif args.cmd == "set-properties":
        print(json.dumps(cli.set_properties(args.doc_id, args.title, args.description), indent=2))
    elif args.cmd == "versions":
        print(json.dumps(cli.get_version_history(args.doc_id), indent=2))
    elif args.cmd == "restore-version":
        print(json.dumps(cli.restore_version(args.doc_id, args.version), indent=2))
    elif args.cmd == "download-version":
        print(json.dumps({"ok": cli.download_version(args.doc_id, args.version, args.local_path)}, indent=2))
    elif args.cmd == "search-content":
        print(json.dumps(cli.search_by_content(args.content), indent=2))
    elif args.cmd == "search-name":
        print(json.dumps(cli.search_by_name(args.name), indent=2))
    elif args.cmd == "search-keywords":
        print(json.dumps(cli.search_by_keywords(args.keywords), indent=2))
    elif args.cmd == "search":
        print(json.dumps(cli.search(args.content, args.name, args.path, args.author), indent=2))
    elif args.cmd == "workflows":
        if args.name:
            print(json.dumps(cli.find_workflows(args.name), indent=2))
        else:
            print(json.dumps(cli.list_workflows(), indent=2))
    elif args.cmd == "start-workflow":
        print(json.dumps(cli.start_workflow(args.workflow_uuid, args.doc_id), indent=2))
    elif args.cmd == "tasks":
        print(json.dumps(cli.get_tasks(args.doc_id, args.actor_id), indent=2))
    elif args.cmd == "complete-task":
        print(json.dumps(cli.complete_task(args.task_id, transition=args.transition), indent=2))
    elif args.cmd == "comment-task":
        print(json.dumps(cli.add_task_comment(args.task_id, args.message), indent=2))
    elif args.cmd == "assign-task":
        print(json.dumps(cli.assign_task(args.task_id, args.actor_id), indent=2))
    elif args.cmd == "checkout":
        print(json.dumps(cli.checkout(args.doc_id), indent=2))
    elif args.cmd == "cancel-checkout":
        print(json.dumps(cli.cancel_checkout(args.doc_id), indent=2))
    elif args.cmd == "checkin":
        print(json.dumps(cli.checkin(args.doc_id, args.local_path, args.comment), indent=2))
    elif args.cmd == "upload-version":
        print(json.dumps(cli.upload_version(args.okm_path, args.local_path, args.comment), indent=2))

if __name__ == "__main__":
    main()
