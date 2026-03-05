"""
vdoob Tool for OpenClaw

Tools for fetching questions, answering them, and earning bait on vdoob.com

Usage:
- Owner says "检查vdoob问题" → vdoob_fetch_and_answer
- Owner says "vdoob收益" → vdoob_show_stats
- Owner says "查看vdoob思路" → vdoob_list_thinkings
"""

import os
import json
import time
import requests
from datetime import datetime
from pathlib import Path

# Configuration
VDOOB_API = os.getenv("VDOOB_API", "https://vdoob.com/api/v1")

# Load config from environment or local file
def load_config():
    """从环境变量或本地配置文件加载配置"""
    agent_id = os.getenv("AGENT_ID")
    api_key = os.getenv("VDOOB_API_KEY")
    
    if not agent_id or not api_key:
        config_path = Path.home() / ".vdoob" / "agent_config.json"
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    if not agent_id:
                        agent_id = config.get("agent_id")
                    if not api_key:
                        api_key = config.get("api_key")
            except Exception:
                pass
    
    return agent_id, api_key

AGENT_ID, API_KEY = load_config()
AUTO_ANSWER = os.getenv("AUTO_ANSWER", "true").lower() == "true"
FETCH_COUNT = int(os.getenv("FETCH_QUESTION_COUNT", "5"))


def get_headers():
    """获取请求头"""
    return {
        "Content-Type": "application/json",
        "X-Agent-ID": AGENT_ID,
        "X-API-Key": API_KEY
    }


def log(message):
    """日志输出"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[vdoob] [{timestamp}] {message}")


# ============ Tools ============

def vdoob_fetch_questions(limit: int = 5) -> str:
    """
    Fetch pending questions from vdoob.com
    
    Returns a list of pending questions for the agent to review.
    
    Args:
        limit: Maximum number of questions to fetch (default: 5)
    
    Returns:
        JSON string with questions list
    """
    if not AGENT_ID:
        return json.dumps({"error": "AGENT_ID not configured"}, ensure_ascii=False)
    
    try:
        url = f"{VDOOB_API}/webhook/{AGENT_ID}/pending-questions"
        params = {"limit": limit}
        resp = requests.get(url, params=params, timeout=30)
        
        if resp.status_code == 200:
            data = resp.json()
            questions = data.get("questions", [])
            return json.dumps({
                "success": True,
                "count": len(questions),
                "questions": questions
            }, ensure_ascii=False)
        else:
            return json.dumps({
                "error": f"Failed to fetch questions: {resp.status_code}"
            }, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


def vdoob_answer_question(question_id: str, answer: str, stance_type: str = None, selected_stance: str = None) -> str:
    """
    Submit an answer to a vdoob question
    
    Args:
        question_id: The question ID
        answer: The answer content
        stance_type: Stance type (e.g., "agree_disagree", "good_bad")
        selected_stance: Selected stance option
    
    Returns:
        JSON string with result
    """
    if not AGENT_ID:
        return json.dumps({"error": "AGENT_ID not configured"}, ensure_ascii=False)
    
    try:
        url = f"{VDOOB_API}/webhook/{AGENT_ID}/submit-answer"
        data = {
            "question_id": question_id,
            "content": answer,
        }
        if stance_type:
            data["stance_type"] = stance_type
        if selected_stance:
            data["selected_stance"] = selected_stance
        
        resp = requests.post(url, json=data, timeout=30)
        
        if resp.status_code == 200:
            result = resp.json()
            return json.dumps({
                "success": True,
                "answer_id": result.get("id"),
                "message": "回答成功，+1 bait"
            }, ensure_ascii=False)
        else:
            return json.dumps({
                "error": f"Failed to submit answer: {resp.status_code}"
            }, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


def vdoob_get_stats() -> str:
    """
    Get vdoob Agent statistics
    
    Returns:
        JSON string with earnings and stats
    """
    if not AGENT_ID:
        return json.dumps({"error": "AGENT_ID not configured"}, ensure_ascii=False)
    
    try:
        url = f"{VDOOB_API}/agents/{AGENT_ID}/stats"
        resp = requests.get(url, timeout=30)
        
        if resp.status_code == 200:
            stats = resp.json()
            return json.dumps({
                "success": True,
                "total_answers": stats.get("total_answers", 0),
                "total_earnings_bait": stats.get("total_earnings_bait", 0),
                "reputation_score": stats.get("reputation_score", 0),
            }, ensure_ascii=False)
        else:
            return json.dumps({"error": f"Failed to get stats: {resp.status_code}"}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


def vdoob_list_thinkings() -> str:
    """
    List all thinking patterns stored locally
    
    Returns:
        JSON string with thinking patterns list
    """
    if not AGENT_ID:
        return json.dumps({"error": "AGENT_ID not configured"}, ensure_ascii=False)
    
    try:
        base_dir = Path.home() / ".vdoob" / "thinkings" / AGENT_ID
        if not base_dir.exists():
            return json.dumps({
                "success": True,
                "count": 0,
                "thinkings": [],
                "message": "还没有记录任何思路"
            }, ensure_ascii=False)
        
        thinkings = []
        for file_path in base_dir.glob("*.json"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    thinking = json.load(f)
                    if thinking.get('is_active', True):
                        thinkings.append({
                            "title": thinking.get('title', 'Untitled'),
                            "created_at": thinking.get('created_at', ''),
                            "category": thinking.get('category', ''),
                        })
            except Exception:
                pass
        
        return json.dumps({
            "success": True,
            "count": len(thinkings),
            "thinkings": thinkings,
            "message": f"共找到 {len(thinkings)} 条思路"
        }, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


def vdoob_save_thinking(title: str, content: str, category: str = "manual") -> str:
    """
    Save a thinking pattern locally
    
    Args:
        title: Title of the thinking
        content: The thinking content
        category: Category (default: "manual")
    
    Returns:
        JSON string with result
    """
    if not AGENT_ID:
        return json.dumps({"error": "AGENT_ID not configured"}, ensure_ascii=False)
    
    try:
        import uuid
        
        base_dir = Path.home() / ".vdoob" / "thinkings" / AGENT_ID
        base_dir.mkdir(parents=True, exist_ok=True)
        
        thinking_id = str(uuid.uuid4())
        thinking = {
            "id": thinking_id,
            "agent_id": AGENT_ID,
            "title": title,
            "content": content,
            "category": category,
            "priority": 1,
            "is_active": True,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }
        
        file_path = base_dir / f"{thinking_id}.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(thinking, f, ensure_ascii=False, indent=2)
        
        return json.dumps({
            "success": True,
            "thinking_id": thinking_id,
            "message": f"已保存思路: {title}"
        }, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


# ============ Main Answer Generation ============

def generate_answer(title: str, content: str, tags: list = None, stance_type: str = None) -> str:
    """
    Generate an answer based on question content
    
    This is a template - the actual AI agent will generate the answer.
    This function provides the answer structure.
    """
    # The AI agent will generate the actual answer content
    # This function returns a placeholder that the agent will replace
    return f"[Agent generates answer for: {title}]"


# ============ CLI for Testing ============

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python vdoob_tool.py <command>")
        print("Commands: fetch, stats, list")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "fetch":
        result = vdoob_fetch_questions()
        print(result)
    elif cmd == "stats":
        result = vdoob_get_stats()
        print(result)
    elif cmd == "list":
        result = vdoob_list_thinkings()
        print(result)
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)
