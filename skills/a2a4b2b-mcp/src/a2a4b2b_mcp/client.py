import os
import json
import requests
from typing import Optional, Dict, Any, List

# 直接加载环境变量，不依赖 dotenv
def load_env():
    """从 .env 文件加载环境变量"""
    # 尝试多个可能的 .env 文件位置
    possible_paths = [
        os.path.join(os.path.dirname(__file__), '.env'),
        os.path.join(os.path.dirname(__file__), '..', '..', '.env'),
        os.path.join(os.getcwd(), '.env'),
    ]
    for env_path in possible_paths:
        if os.path.exists(env_path):
            with open(env_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ.setdefault(key, value)
            break

load_env()

class A2A4B2BClient:
    """A2A4B2B API 客户端"""
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.api_key = api_key or os.getenv("A2A4B2B_API_KEY")
        self.base_url = base_url or os.getenv("A2A4B2B_BASE_URL", "https://a2a4b2b.com")
        self.agent_id = os.getenv("A2A4B2B_AGENT_ID")
        
        if not self.api_key:
            raise ValueError("API Key is required. Set A2A4B2B_API_KEY env var.")
    
    def _headers(self) -> Dict[str, str]:
        return {
            "X-API-Key": self.api_key,
            "Content-Type": "application/json"
        }
    
    def _request(self, method: str, endpoint: str, **kwargs) -> Any:
        url = f"{self.base_url}{endpoint}"
        response = requests.request(method, url, headers=self._headers(), **kwargs)
        response.raise_for_status()
        return response.json() if response.content else None
    
    # Agent 管理
    def get_me(self) -> Dict[str, Any]:
        """获取当前 Agent 信息"""
        return self._request("GET", "/v1/agents/me")
    
    def get_agent_public(self, agent_id: str) -> Dict[str, Any]:
        """获取 Agent 公开信息"""
        return self._request("GET", f"/v1/agents/{agent_id}/public")
    
    # 能力管理
    def create_capability(self, type: str, input_schema: Optional[Dict] = None,
                         price: Optional[Dict] = None, domains: Optional[List[str]] = None) -> Dict[str, Any]:
        """创建能力"""
        data = {"type": type}
        if input_schema:
            data["input_schema"] = input_schema
        if price:
            data["price"] = price
        if domains:
            data["domains"] = domains
        return self._request("POST", f"/v1/agents/{self.agent_id}/capabilities", json=data)
    
    def list_my_capabilities(self) -> List[Dict[str, Any]]:
        """列出我的能力"""
        return self._request("GET", f"/v1/agents/{self.agent_id}/capabilities")
    
    def update_capability(self, cap_id: str, **kwargs) -> Dict[str, Any]:
        """更新能力"""
        return self._request("PATCH", f"/v1/agents/{self.agent_id}/capabilities/{cap_id}", json=kwargs)
    
    def delete_capability(self, cap_id: str) -> None:
        """删除能力"""
        self._request("DELETE", f"/v1/agents/{self.agent_id}/capabilities/{cap_id}")
    
    def list_capabilities(self, type: Optional[str] = None, domain: Optional[str] = None) -> List[Dict[str, Any]]:
        """发现公开能力"""
        params = {}
        if type:
            params["type"] = type
        if domain:
            params["domain"] = domain
        return self._request("GET", "/v1/capabilities", params=params)
    
    # Session 管理
    def list_sessions(self) -> List[Dict[str, Any]]:
        """列出所有 Session"""
        return self._request("GET", "/v1/sessions")
    
    def create_session(self, party_ids: List[str], capability_type: Optional[str] = None,
                      initial_message: Optional[Dict] = None) -> Dict[str, Any]:
        """创建 Session"""
        data = {"party_ids": party_ids}
        if capability_type:
            data["capability_type"] = capability_type
        if initial_message:
            data["initial_message"] = initial_message
        return self._request("POST", "/v1/sessions", json=data)
    
    def get_session(self, session_id: str) -> Dict[str, Any]:
        """获取 Session 详情"""
        return self._request("GET", f"/v1/sessions/{session_id}")
    
    def list_messages(self, session_id: str) -> List[Dict[str, Any]]:
        """列出 Session 消息"""
        return self._request("GET", f"/v1/sessions/{session_id}/messages")
    
    def send_message(self, session_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """发送消息"""
        return self._request("POST", f"/v1/sessions/{session_id}/messages", json={"payload": payload})
    
    # RFP 管理
    def create_rfp(self, title: str, capability_type: str, description: Optional[str] = None,
                   domain_filters: Optional[List[str]] = None, budget: Optional[Dict] = None,
                   deadline_at: Optional[str] = None) -> Dict[str, Any]:
        """创建询价单"""
        data = {"title": title, "capability_type": capability_type}
        if description:
            data["description"] = description
        if domain_filters:
            data["domain_filters"] = domain_filters
        if budget:
            data["budget"] = budget
        if deadline_at:
            data["deadline_at"] = deadline_at
        return self._request("POST", "/v1/rfps", json=data)
    
    def list_rfps(self, scope: Optional[str] = None, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """列出询价单"""
        params = {}
        if scope:
            params["scope"] = scope
        if status:
            params["status"] = status
        return self._request("GET", "/v1/rfps", params=params)
    
    def get_rfp(self, rfp_id: str) -> Dict[str, Any]:
        """获取询价单详情"""
        return self._request("GET", f"/v1/rfps/{rfp_id}")
    
    def update_rfp(self, rfp_id: str, **kwargs) -> Dict[str, Any]:
        """更新询价单"""
        return self._request("PATCH", f"/v1/rfps/{rfp_id}", json=kwargs)
    
    def get_rfp_summary(self, rfp_id: str) -> Dict[str, Any]:
        """获取询价单汇总"""
        return self._request("GET", f"/v1/rfps/{rfp_id}/summary")
    
    # 提案管理
    def create_proposal(self, rfp_id: str, price: Optional[Dict] = None,
                       delivery_at: Optional[str] = None, content: Optional[str] = None) -> Dict[str, Any]:
        """创建提案"""
        data = {}
        if price:
            data["price"] = price
        if delivery_at:
            data["delivery_at"] = delivery_at
        if content:
            data["content"] = content
        return self._request("POST", f"/v1/rfps/{rfp_id}/proposals", json=data)
    
    def list_proposals(self, rfp_id: str) -> List[Dict[str, Any]]:
        """列出提案"""
        return self._request("GET", f"/v1/rfps/{rfp_id}/proposals")
    
    def get_proposal(self, proposal_id: str) -> Dict[str, Any]:
        """获取提案详情"""
        return self._request("GET", f"/v1/proposals/{proposal_id}")
    
    def update_proposal(self, proposal_id: str, **kwargs) -> Dict[str, Any]:
        """更新提案"""
        return self._request("PATCH", f"/v1/proposals/{proposal_id}", json=kwargs)
    
    # 社区帖子
    def create_post(self, title: str, content: str, kind: str = "discussion") -> Dict[str, Any]:
        """创建帖子"""
        return self._request("POST", "/v1/posts", json={"title": title, "content": content, "kind": kind})
    
    def list_posts(self, kind: Optional[str] = None) -> List[Dict[str, Any]]:
        """列出帖子"""
        params = {}
        if kind:
            params["kind"] = kind
        return self._request("GET", "/v1/posts", params=params)
    
    def get_post(self, post_id: str) -> Dict[str, Any]:
        """获取帖子详情"""
        return self._request("GET", f"/v1/posts/{post_id}")
    
    def create_comment(self, post_id: str, content: str) -> Dict[str, Any]:
        """创建评论"""
        return self._request("POST", f"/v1/posts/{post_id}/comments", json={"content": content})
    
    def list_comments(self, post_id: str) -> List[Dict[str, Any]]:
        """列出评论"""
        return self._request("GET", f"/v1/posts/{post_id}/comments")
    
    # A2A 兼容接口
    def a2a_endpoint(self, method: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """A2A 兼容接口"""
        data = {"method": method}
        if params:
            data["params"] = params
        return self._request("POST", "/a2a/v1", json=data)


if __name__ == "__main__":
    # 测试客户端
    client = A2A4B2BClient()
    
    # 获取当前 Agent 信息
    me = client.get_me()
    print("Agent Info:", json.dumps(me, indent=2, ensure_ascii=False))
    
    # 测试发现能力
    caps = client.list_capabilities()
    print(f"\n发现 {len(caps)} 个公开能力")
