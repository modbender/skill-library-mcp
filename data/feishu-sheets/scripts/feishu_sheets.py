#!/usr/bin/env python3
"""
Feishu Sheets API Client
Supports: create, read, write, append, insert/delete rows/columns
"""

import os
import sys
import json
import requests
from typing import List, Dict, Any, Optional

# API Base URLs
BASE_URL = "https://open.feishu.cn/open-apis"
SHEETS_API = f"{BASE_URL}/sheets/v2/spreadsheets"
AUTH_API = f"{BASE_URL}/auth/v3/tenant_access_token/internal"

class FeishuSheetsClient:
    def __init__(self):
        self.app_id = os.getenv("FEISHU_APP_ID")
        self.app_secret = os.getenv("FEISHU_APP_SECRET")
        self._token = None
        
    def _get_token(self) -> str:
        """Get tenant access token"""
        if self._token:
            return self._token
            
        resp = requests.post(AUTH_API, json={
            "app_id": self.app_id,
            "app_secret": self.app_secret
        })
        resp.raise_for_status()
        data = resp.json()
        
        if data.get("code") != 0:
            raise Exception(f"Auth failed: {data}")
            
        self._token = data["tenant_access_token"]
        return self._token
        
    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self._get_token()}",
            "Content-Type": "application/json"
        }
        
    def create_spreadsheet(self, title: str, folder_token: Optional[str] = None) -> Dict:
        """Create a new spreadsheet"""
        url = f"{BASE_URL}/sheets/v3/spreadsheets"
        payload = {"title": title}
        if folder_token:
            payload["folder_token"] = folder_token
            
        resp = requests.post(url, headers=self._headers(), json=payload)
        resp.raise_for_status()
        return resp.json()
        
    def get_spreadsheet_info(self, spreadsheet_token: str) -> Dict:
        """Get spreadsheet metadata including sheets"""
        url = f"{SHEETS_API}/{spreadsheet_token}/metainfo"
        resp = requests.get(url, headers=self._headers())
        resp.raise_for_status()
        return resp.json()
        
    def read_values(self, spreadsheet_token: str, sheet_id: str, range_str: str) -> Dict:
        """Read values from a range"""
        range_param = f"{sheet_id}!{range_str}" if sheet_id else range_str
        url = f"{SHEETS_API}/{spreadsheet_token}/values/{range_param}"
        resp = requests.get(url, headers=self._headers())
        resp.raise_for_status()
        return resp.json()
        
    def write_values(self, spreadsheet_token: str, sheet_id: str, 
                     range_str: str, values: List[List[Any]]) -> Dict:
        """Write values to a range"""
        url = f"{SHEETS_API}/{spreadsheet_token}/values"
        range_param = f"{sheet_id}!{range_str}" if sheet_id else range_str
        payload = {
            "valueRange": {
                "range": range_param,
                "values": values
            }
        }
        resp = requests.put(url, headers=self._headers(), json=payload)
        resp.raise_for_status()
        return resp.json()
        
    def append_values(self, spreadsheet_token: str, sheet_id: str, 
                      values: List[List[Any]]) -> Dict:
        """Append values to the end of sheet"""
        url = f"{SHEETS_API}/{spreadsheet_token}/values_append"
        payload = {
            "valueRange": {
                "range": sheet_id,
                "values": values
            }
        }
        resp = requests.post(url, headers=self._headers(), json=payload)
        resp.raise_for_status()
        return resp.json()
        
    def insert_dimension(self, spreadsheet_token: str, sheet_id: str,
                        dimension: str, start_index: int, end_index: int) -> Dict:
        """Insert rows or columns"""
        url = f"{SHEETS_API}/{spreadsheet_token}/insert_dimension_range"
        payload = {
            "dimension": {
                "sheetId": sheet_id,
                "majorDimension": dimension,  # ROWS or COLUMNS
                "startIndex": start_index,
                "endIndex": end_index
            }
        }
        resp = requests.post(url, headers=self._headers(), json=payload)
        resp.raise_for_status()
        return resp.json()
        
    def delete_dimension(self, spreadsheet_token: str, sheet_id: str,
                        dimension: str, start_index: int, end_index: int) -> Dict:
        """Delete rows or columns"""
        url = f"{SHEETS_API}/{spreadsheet_token}/dimension_range"
        payload = {
            "dimension": {
                "sheetId": sheet_id,
                "majorDimension": dimension,
                "startIndex": start_index,
                "endIndex": end_index
            }
        }
        resp = requests.delete(url, headers=self._headers(), json=payload)
        resp.raise_for_status()
        return resp.json()
        
    def add_sheet(self, spreadsheet_token: str, title: str) -> Dict:
        """Add a new worksheet"""
        url = f"{SHEETS_API}/{spreadsheet_token}/sheets_batch_update"
        payload = {
            "requests": [{
                "addSheet": {
                    "properties": {"title": title}
                }
            }]
        }
        resp = requests.post(url, headers=self._headers(), json=payload)
        resp.raise_for_status()
        return resp.json()
        
    def delete_sheet(self, spreadsheet_token: str, sheet_id: str) -> Dict:
        """Delete a worksheet"""
        url = f"{SHEETS_API}/{spreadsheet_token}/sheets_batch_update"
        payload = {
            "requests": [{
                "deleteSheet": {"sheetId": sheet_id}
            }]
        }
        resp = requests.post(url, headers=self._headers(), json=payload)
        resp.raise_for_status()
        return resp.json()


def main():
    """CLI entry point for tool calls"""
    if len(sys.argv) < 2:
        print(json.dumps({"error": "No action specified"}))
        sys.exit(1)
        
    action = sys.argv[1]
    client = FeishuSheetsClient()
    
    try:
        if action == "create":
            title = sys.argv[2]
            folder = sys.argv[3] if len(sys.argv) > 3 else None
            result = client.create_spreadsheet(title, folder)
            
        elif action == "get_info":
            token = sys.argv[2]
            result = client.get_spreadsheet_info(token)
            
        elif action == "read":
            token = sys.argv[2]
            sheet_id = sys.argv[3]
            range_str = sys.argv[4]
            result = client.read_values(token, sheet_id, range_str)
            
        elif action == "write":
            token = sys.argv[2]
            sheet_id = sys.argv[3]
            range_str = sys.argv[4]
            values = json.loads(sys.argv[5])
            result = client.write_values(token, sheet_id, range_str, values)
            
        elif action == "append":
            token = sys.argv[2]
            sheet_id = sys.argv[3]
            values = json.loads(sys.argv[4])
            result = client.append_values(token, sheet_id, values)
            
        elif action == "insert_dimension":
            token = sys.argv[2]
            sheet_id = sys.argv[3]
            dimension = sys.argv[4]
            start = int(sys.argv[5])
            end = int(sys.argv[6])
            result = client.insert_dimension(token, sheet_id, dimension, start, end)
            
        elif action == "delete_dimension":
            token = sys.argv[2]
            sheet_id = sys.argv[3]
            dimension = sys.argv[4]
            start = int(sys.argv[5])
            end = int(sys.argv[6])
            result = client.delete_dimension(token, sheet_id, dimension, start, end)
            
        elif action == "add_sheet":
            token = sys.argv[2]
            title = sys.argv[3]
            result = client.add_sheet(token, title)
            
        elif action == "delete_sheet":
            token = sys.argv[2]
            sheet_id = sys.argv[3]
            result = client.delete_sheet(token, sheet_id)
            
        else:
            result = {"error": f"Unknown action: {action}"}
            
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
    except Exception as e:
        print(json.dumps({"error": str(e)}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
