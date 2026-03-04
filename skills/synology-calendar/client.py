#!/usr/bin/env python3
"""
Synology Calendar API - 使用新版 Office Suite API

基于: https://office-suite-api.synology.com/Synology-Calendar/v1

认证: POST /api/Calendar/default/v1/login
事件: POST /api/Calendar/default/v1/event
"""

import os, sys, json, requests

# 默认配置 ({username}_dsm)
URL = os.environ.get("SYNOLOGY_URL", "http://{nas_ip}:5000")
USER = os.environ.get("SYNOLOGY_USER", "{username}")
PWD = os.environ.get("SYNOLOGY_PASSWORD", "{password}")


class SynologyCalendar:
    """Synology Calendar API (新版 Office Suite API)"""
    
    def __init__(self, url=None, user=None, password=None):
        self.url = (url or URL).rstrip('/')
        self.user = user or USER
        self.password = password or PWD
        self.s = requests.Session()
        self.did = None
        self.sid = None
    
    def login(self):
        """新版登录: POST /api/Calendar/default/v1/login"""
        login_url = f"{self.url}/api/Calendar/default/v1/login"
        
        data = {
            "account": self.user,
            "passwd": self.password,
            "format": "sid"  # 必须设为 "sid"
        }
        
        try:
            r = self.s.post(login_url, json=data, timeout=10)
            result = r.json()
            
            if result.get("success"):
                self.did = result["data"]["did"]
                self.sid = result["data"]["sid"]
                print(f"✓ 登录成功 (did: {self.did[:10]}...)")
                return True
            else:
                print(f"✗ 登录失败: {result}")
                return False
        except Exception as e:
            print(f"✗ 登录异常: {e}")
            return False
    
    def logout(self):
        """登出"""
        if not self.sid:
            return
        
        logout_url = f"{self.url}/api/Calendar/default/v1/logout"
        
        try:
            self.s.post(logout_url, json={"did": self.did, "sid": self.sid}, timeout=10)
            print("✓ 已登出")
        except Exception as e:
            print(f"登出异常: {e}")
    
    def _request(self, method, endpoint, **kwargs):
        """发送 API 请求
        
        ⚠️ 重要: SID 必须在 URL 参数中传递，不是 JSON body
        API 文档: https://office-suite-api.synology.com/Calendar/v1
        """
        # SID 必须放在 URL 参数中
        url = f"{self.url}{endpoint}"
        if "?" in url:
            url += f"&_sid={self.sid}"
        else:
            url += f"?_sid={self.sid}"
        
        # JSON body 中不需要包含 did/sid
        r = self.s.request(method, url, **kwargs)
        return r.json()
    
    def create_event(self, title, dtstart, dtend, cal_id="/{username}/home/", 
                    all_day=False, description="", notify_minutes=-15,
                    location=None, participant=None):
        """创建事件
        
        Args:
            title: 事件标题
            dtstart: 开始时间 (格式: "20190606" 或 "TZID=Asia/Tokyo:20190628T090000")
            dtend: 结束时间
            cal_id: 日历 ID
            all_day: 是否全天事件
            description: 事件描述
            notify_minutes: 提前多少分钟提醒 (负数表示提前)
            location: 地点
            participant: 参与者列表
        """
        # 构建必填参数 (根据新版 OpenAPI 文档)
        data = {
            "cal_id": cal_id,
            "original_cal_id": cal_id,
            "summary": title,
            "is_all_day": all_day,
            "is_repeat_evt": False,
            "color": "#0082D5",  # 默认蓝色
            "notify_setting": [{
                "action": "display",
                "description": "Event reminder",
                "type": "duration",
                "duration": {
                    "related": "start",
                    "minutes": notify_minutes
                }
            }],
            "description": description,
            "participant": participant if participant else [],
        }
        
        # 非全天事件需要时区
        if not all_day:
            data["tz_id"] = "Asia/Shanghai"
        
        # dtstart/dtend 需要是 Unix 时间戳整数
        try:
            if isinstance(dtstart, str):
                # 尝试解析字符串格式
                if 'T' in dtstart:
                    # 格式: 20260227T150000
                    from datetime import datetime
                    dt = datetime.strptime(dtstart, "%Y%m%dT%H%M%S")
                    data["dtstart"] = int(dt.timestamp())
                elif len(dtstart) == 8:
                    # 格式: 20260227 (全天)
                    data["dtstart"] = int(dtstart)
                else:
                    data["dtstart"] = int(dtstart)
            else:
                data["dtstart"] = int(dtstart)
                
            if isinstance(dtend, str):
                if 'T' in dtend:
                    from datetime import datetime
                    dt = datetime.strptime(dtend, "%Y%m%dT%H%M%S")
                    data["dtend"] = int(dt.timestamp())
                elif len(dtend) == 8:
                    data["dtend"] = int(dtend)
                else:
                    data["dtend"] = int(dtend)
            else:
                data["dtend"] = int(dtend)
        except Exception as e:
            print(f"时间解析错误: {e}, 使用原始值")
            data["dtstart"] = dtstart
            data["dtend"] = dtend
        
        # 地点信息
        if location:
            data["location_info"] = {
                "map_type": "",
                "name": location,
                "address": "",
                "place_id": "",
                "gps": {"lat": 0, "lng": 0}
            }
        
        # 发送请求
        result = self._request("POST", "/api/Calendar/default/v1/event", json=data)
        
        if result.get("success"):
            evt_id = result["data"]["evt_id"]
            print(f"✓ 事件创建成功: {evt_id}")
            return evt_id
        else:
            error = result.get("error", {})
            print(f"✗ 事件创建失败: {error}")
            raise Exception(f"Failed: {error}")
    
    def get_event(self, evt_id):
        """获取事件详情"""
        result = self._request("GET", "/api/Calendar/default/v1/event", json={"evt_id": evt_id})
        return result.get("data", {})
    
    def list_events(self, cal_id="/{username}/home/"):
        """列出事件"""
        result = self._request("POST", "/api/Calendar/default/v1/event/list", json={
            "cal_id_list": [cal_id]
        })
        return result.get("data", {}).get("events", [])
    
    def delete_event(self, evt_id):
        """删除事件"""
        result = self._request("DELETE", "/api/Calendar/default/v1/event", json={"evt_id": evt_id})
        if result.get("success"):
            print(f"✓ 事件 {evt_id} 已删除")
            return True
        print(f"✗ 删除失败: {result}")
        return False
    
    def get_calendars(self):
        """获取日历列表"""
        result = self._request("GET", "/api/Calendar/default/v1/cal/list")
        return result.get("data", {}).get("calendars", [])
    
    def get_timezones(self):
        """获取时区列表"""
        result = self._request("GET", "/api/Calendar/default/v1/timezone")
        return result.get("data", {}).get("timezones", [])
    
    # ========== 任务 (Todo) ==========
    
    def create_task(self, title, due, cal_id="/{username}/home_todo/", description=""):
        """创建任务"""
        from datetime import datetime
        import time
        
        # 解析截止日期
        if isinstance(due, str):
            if 'T' in due:
                dt = datetime.strptime(due, "%Y%m%dT%H%M%S")
                due_timestamp = int(dt.timestamp())
                is_all_day = False
                tz_id = "Asia/Shanghai"
                has_start_time = False
                has_end_time = False
            else:
                due_timestamp = int(due) if due.isdigit() else int(datetime.strptime(due, "%Y%m%d").timestamp())
                is_all_day = True
                tz_id = None
                has_start_time = False
                has_end_time = False
        else:
            due_timestamp = int(due)
            is_all_day = False
            tz_id = "Asia/Shanghai"
            has_start_time = False
            has_end_time = False
        
        data = {
            "cal_id": cal_id,
            "original_cal_id": cal_id,
            "summary": title,
            "description": description,
            "due": due_timestamp,
            "is_all_day": is_all_day,
            "tz_id": tz_id,
            "has_start_time": has_start_time,
            "has_end_time": has_end_time,
            "percent_complete": 0,
            "priority_order": 0,
            "notify_setting": [],
        }
        
        result = self._request("POST", "/api/Calendar/default/v1/task", json=data)
        
        if result.get("success"):
            task_id = result["data"]["evt_id"]
            print(f"✓ 任务创建成功: {task_id}")
            return task_id
        print(f"✗ 任务创建失败: {result}")
        return None
    
    def list_tasks(self, cal_id="/{username}/home_todo/"):
        """列出任务"""
        result = self._request("POST", "/api/Calendar/default/v1/task/list", json={"cal_id": cal_id})
        return result.get("data", {}).get("tasks", [])


# ========== CLI ==========
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Synology Calendar API (新版)")
    parser.add_argument("--url", default=URL, help="NAS URL")
    parser.add_argument("--user", default=USER, help="用户名")
    parser.add_argument("--password", default=PWD, help="密码")
    
    subparsers = parser.add_subparsers(dest="command")
    
    # login
    subparsers.add_parser("login", help="登录")
    
    # list-calendars
    subparsers.add_parser("list-calendars", help="列出日历")
    
    # list-events
    p_events = subparsers.add_parser("list-events", help="列出事件")
    p_events.add_argument("--cal-id", default="/{username}/home/", help="日历 ID")
    
    # create-event
    p_create = subparsers.add_parser("create-event", help="创建事件")
    p_create.add_argument("title", help="事件标题")
    p_create.add_argument("dtstart", help="开始时间 (如: 20260210T100000)")
    p_create.add_argument("dtend", help="结束时间")
    p_create.add_argument("--cal-id", default="/{username}/home/", help="日历 ID")
    p_create.add_argument("--all-day", action="store_true", help="全天事件")
    p_create.add_argument("--desc", default="", help="事件描述")
    
    # delete-event
    p_delete = subparsers.add_parser("delete-event", help="删除事件")
    p_delete.add_argument("evt_id", help="事件 ID")
    
    # list-tasks
    p_tasks = subparsers.add_parser("list-tasks", help="列出任务")
    
    # create-task
    p_task = subparsers.add_parser("create-task", help="创建任务")
    p_task.add_argument("title", help="任务标题")
    p_task.add_argument("due", help="截止日期 (如: 20260210)")
    p_task.add_argument("--cal-id", default="/{username}/home_todo/", help="日历 ID")
    p_task.add_argument("--desc", default="", help="任务描述")
    
    # timezones
    subparsers.add_parser("timezones", help="获取时区列表")
    
    args = parser.parse_args()
    
    cal = SynologyCalendar(args.url, args.user, args.password)
    
    if not cal.login():
        sys.exit(1)
    
    try:
        if args.command == "login":
            print("✓ 登录成功")
        
        elif args.command == "list-calendars":
            print("\n日历列表:")
            for c in cal.get_calendars():
                print(f"  [{c['cal_id']}] {c.get('name', 'Unknown')}")
        
        elif args.command == "list-events":
            print(f"\n事件列表 ({args.cal_id}):")
            for e in cal.list_events(args.cal_id):
                t = e.get("dtstart_string", "-")
                d = "全天" if e.get("is_all_day") else ""
                print(f"  [{e['evt_id']}] {e['summary']} - {t} {d}")
        
        elif args.command == "create-event":
            cal.create_event(
                args.title, args.dtstart, args.dtend,
                cal_id=args.cal_id, all_day=args.all_day, description=args.desc
            )
        
        elif args.command == "delete-event":
            cal.delete_event(args.evt_id)
        
        elif args.command == "list-tasks":
            print(f"\n任务列表:")
            for t in cal.list_tasks():
                print(f"  [{t['task_id']}] {t['summary']} - {t.get('due', '-')}")
        
        elif args.command == "create-task":
            cal.create_task(args.title, args.due, args.cal_id, args.desc)
        
        elif args.command == "timezones":
            print("\n时区列表:")
            for tz in cal.get_timezones()[:10]:
                print(f"  {tz}")
        
        else:
            print("可用命令:")
            print("  login           - 登录")
            print("  list-calendars  - 列出日历")
            print("  list-events    - 列出事件")
            print("  create-event    - 创建事件")
            print("  delete-event    - 删除事件")
            print("  list-tasks      - 列出任务")
            print("  create-task     - 创建任务")
            print("  timezones       - 获取时区")
    
    finally:
        cal.logout()
