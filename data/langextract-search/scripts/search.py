#!/usr/bin/env python3
"""
LangExtract Search - Zhipu + DuckDuckGo + langextract Workflow
集成智谱 MCP 搜索、DuckDuckGo 搜索和 langextract 结构化提取
"""

import json
import os
import sys
import argparse
import subprocess
import requests
from datetime import datetime
from pathlib import Path


PROJECT_ROOT = Path(__file__).parent.parent
SCRIPTS_DIR = Path(__file__).parent


def add_project_path():
    """将 scripts 目录添加到 Python 路径，以便导入 langextract。"""
    if str(SCRIPTS_DIR) not in sys.path:
        sys.path.append(str(SCRIPTS_DIR))



def resolve_api_key(value):
    if value is None:
        return None
    if not isinstance(value, str):
        return value
    key = value.strip()
    if not key:
        return None
    env_value = os.getenv(key)
    if env_value:
        return env_value
    if key.startswith("${") and key.endswith("}") and len(key) > 3:
        env_value = os.getenv(key[2:-1])
        if env_value:
            return env_value
    if key.startswith("$") and len(key) > 1:
        env_value = os.getenv(key[1:])
        if env_value:
            return env_value
    return key


def map_timelimit(value: str, target: str) -> str:
    """
    将统一的时间过滤值映射到目标搜索引擎的格式。
    
    Args:
        value: 统一值 (day/week/month/year/null/none/None)
        target: 目标引擎 (ddgs/zai)
    
    Returns:
        映射后的值
    """
    if value is None or str(value).lower() in ('null', 'none', ''):
        return None if target == 'ddgs' else 'noLimit'
    
    mapping = {
        'ddgs': {'day': 'd', 'week': 'w', 'month': 'm', 'year': 'y'},
        'zai': {'day': 'oneDay', 'week': 'oneWeek', 'month': 'oneMonth', 'year': 'oneYear'}
    }
    
    return mapping.get(target, {}).get(str(value).lower(), value)


def get_langextract_config(conf: dict = None) -> dict:
    """
    获取 langextract 配置。
    
    Returns:
        dict: {provider, model, baseUrl, apiKey}
    
    Raises:
        ValueError: 配置缺失时抛出
    """
    if conf is None:
        conf = load_project_conf()
    
    task_conf = conf.get('langextract', {})
    
    if not task_conf:
        raise ValueError("langextract 配置缺失。请在 conf.json 中配置 langextract 节点，参考 conf.json.example")
    
    provider = task_conf.get('provider')
    model = task_conf.get('model')
    base_url = task_conf.get('baseUrl')
    api_key = resolve_api_key(task_conf.get('apiKey'))
    
    missing = []
    if not model:
        missing.append('model')
    if not base_url:
        missing.append('baseUrl')
    if not api_key:
        missing.append('apiKey')
    
    if missing:
        raise ValueError(f"langextract 配置不完整，缺少: {', '.join(missing)}。请参考 conf.json.example")
    
    return {
        'provider': provider,
        'model': model,
        'baseUrl': base_url,
        'apiKey': api_key
    }


def get_zhipu_search_config(conf: dict = None) -> dict:
    """
    获取智谱搜索配置。
    
    配置项:
        enabled: 是否启用智谱搜索，默认 True
        apiKey: API Key（支持环境变量引用）
        search_engine: 搜索引擎 search_std/search_pro/search_pro_sogou/search_pro_quark，默认 search_pro
        count: 返回结果数 1-50，默认 15
        timelimit: 时间过滤 day/week/month/year/null，默认 null（不限）
        content_size: 内容长度 medium/high，默认 high
        search_domain_filter: 限定搜索域名，默认 null
    """
    if conf is None:
        conf = load_project_conf()
    
    search_conf = conf.get('zhipu_search', {})
    
    api_key = resolve_api_key(search_conf.get('apiKey'))
    timelimit = search_conf.get('timelimit')
    
    return {
        'enabled': search_conf.get('enabled', True),
        'apiKey': api_key,
        'search_engine': search_conf.get('search_engine', 'search_pro'),
        'count': search_conf.get('count', 15),
        'timelimit': timelimit,
        'timelimit_mapped': map_timelimit(timelimit, 'zai'),
        'content_size': search_conf.get('content_size', 'high'),
        'search_domain_filter': search_conf.get('search_domain_filter')
    }


def get_duckduckgo_search_config(conf: dict = None) -> dict:
    """
    获取 DuckDuckGo 搜索配置。
    
    配置项:
        enabled: 是否启用 DuckDuckGo 搜索，默认 True
        maxResults: 返回结果数，默认 20
        region: 地区代码 cn-zh/us-en/wt-wt 等，默认 wt-wt（无限制）
        safesearch: 安全搜索 on/moderate/off，默认 moderate
        timelimit: 时间过滤 day/week/month/year/null，默认 null（不限）
        backend: 搜索后端 auto/bing/google/duckduckgo/brave/yandex/yahoo，默认 auto
        proxy: 代理地址，默认 null
        timeout: 请求超时（秒），默认 10
    """
    if conf is None:
        conf = load_project_conf()
    
    search_conf = conf.get('duckduckgo_search', {})
    timelimit = search_conf.get('timelimit')
    
    return {
        'enabled': search_conf.get('enabled', True),
        'maxResults': search_conf.get('maxResults', 20),
        'region': search_conf.get('region', 'wt-wt'),
        'safesearch': search_conf.get('safesearch', 'moderate'),
        'timelimit': timelimit,
        'timelimit_mapped': map_timelimit(timelimit, 'ddgs'),
        'backend': search_conf.get('backend', 'auto'),
        'proxy': search_conf.get('proxy'),
        'timeout': search_conf.get('timeout', 10)
    }


def get_volcengine_search_config(conf: dict = None) -> dict:
    """获取火山引擎联网问答配置。"""
    if conf is None:
        conf = load_project_conf()
    
    search_conf = conf.get('volcengine_search', {})
    
    api_key = resolve_api_key(search_conf.get('apiKey'))
    bot_id = resolve_api_key(search_conf.get('botId'))
    
    return {
        'enabled': search_conf.get('enabled', False),
        'apiKey': api_key,
        'botId': bot_id
    }


def get_extraction_config(conf: dict = None) -> dict:
    """获取结构化提取配置。"""
    if conf is None:
        conf = load_project_conf()
    
    extraction_conf = conf.get('extraction', {})
    
    return {
        'max_content_length': extraction_conf.get('max_content_length', 70000)
    }


def get_project_conf_path():
    """获取项目配置文件路径"""
    return PROJECT_ROOT / "conf.json"


def load_project_conf():
    """加载项目配置"""
    conf_path = get_project_conf_path()
    if conf_path.exists():
        try:
            with open(conf_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            print(f"⚠️ conf.json 格式错误: {e}")
            print(f"   请修复或删除 {conf_path} 后重试")
            raise
    return {}


def parse_mcp_output(output: str):
    """Parse MCP output - handle double-quoted JSON."""
    try:
        # First parse: get the string
        first_parse = json.loads(output.strip())
        if isinstance(first_parse, str):
            # Second parse: parse the string to get the array
            return json.loads(first_parse)
        elif isinstance(first_parse, list):
            # Already an array
            return first_parse
        else:
            raise ValueError(f"Unexpected type: {type(first_parse)}")
    except Exception as e:
        print(f"   解析调试: {e}")
        print(f"   原始输出: {repr(output[:200])}")
        raise


def search_with_zhipu_mcp(query: str, verbose: bool = False):
    """
    Step 1a: Search using Zhipu AI's official zai-sdk (web_search API).
    
    配置参数从 conf.json 的 zhipu_search 节点读取:
        search_engine: 搜索引擎
        count: 返回结果数
        timelimit: 时间过滤
        content_size: 内容长度
        search_domain_filter: 域名过滤
    """
    search_conf = get_zhipu_search_config()
    
    if verbose:
        print("\n" + "=" * 60)
        print("🔍 步骤 1a: 智谱 AI 网络搜索")
        print("=" * 60)
        print(f"\n📥 输入:")
        print(f"   搜索查询: {query}")
        print(f"   搜索引擎: {search_conf['search_engine']}")
        print(f"   结果数量: {search_conf['count']}")
        print(f"   时间过滤: {search_conf['timelimit']} -> {search_conf['timelimit_mapped']}")
        print(f"   内容长度: {search_conf['content_size']}")
        if search_conf['search_domain_filter']:
            print(f"   域名过滤: {search_conf['search_domain_filter']}")
    
    try:
        try:
            from zai import ZhipuAiClient
            has_zai = True
        except ImportError:
            has_zai = False
        
        api_key = search_conf.get('apiKey')
        
        if not api_key:
            raise ValueError("智谱搜索 API Key 未配置。请在 conf.json 的 zhipu_search.apiKey 中设置")
        
        if verbose:
            print(f"\n🤖 正在调用智谱搜索 API...")
            print(f"   使用 zai-sdk: {has_zai}")
        
        search_results = []
        
        if has_zai:
            client = ZhipuAiClient(api_key=api_key)
            
            search_params = {
                'search_engine': search_conf['search_engine'],
                'search_query': query,
                'count': search_conf['count'],
                'search_recency_filter': search_conf['timelimit_mapped'],
                'content_size': search_conf['content_size']
            }
            if search_conf['search_domain_filter']:
                search_params['search_domain_filter'] = search_conf['search_domain_filter']
            
            response = client.web_search.web_search(**search_params)
            
            # Parse search results from the response
            if hasattr(response, 'search_result') and response.search_result:
                for item in response.search_result:
                    search_results.append({
                        "title": getattr(item, "title", ""),
                        "link": getattr(item, "link", ""),
                        "content": getattr(item, "content", ""),
                        "publish_date": getattr(item, "publish_date", ""),
                        "site_name": getattr(item, "media", "")
                    })
            # Also check if response is a dict-like object
            elif isinstance(response, dict) and 'search_result' in response:
                for item in response['search_result']:
                    search_results.append({
                        "title": item.get("title", ""),
                        "link": item.get("link", ""),
                        "content": item.get("content", ""),
                        "publish_date": item.get("publish_date", ""),
                        "site_name": item.get("media", "")
                    })
        
        # If no results from SDK, fall back to DuckDuckGo
        if not search_results:
            if verbose:
                print(f"   智谱搜索未获取到结果，将使用 DuckDuckGo...")
            
            # Return empty result so the workflow can use DuckDuckGo instead
            return {
                "success": False,
                "error": "Zhipu search did not return results, will use DuckDuckGo",
                "query": query,
                "source": "zhipu"
            }
        
        if verbose:
            print(f"\n📤 输出:")
            print(f"   智谱搜索成功: ✅")
            print(f"   找到结果: {len(search_results)} 条")
            
            for i, item in enumerate(search_results[:3], 1):
                print(f"\n   {i}. {item.get('title', 'No title')}")
                print(f"      URL: {item.get('link', 'No link')}")
                print(f"      日期: {item.get('publish_date', 'No date')}")
                content = item.get('content', '')
                print(f"      摘要: {content[:100]}...")
        
        # Combine search results into a single text
        combined_content = ""
        for item in search_results:
            title = item.get('title', '')
            link = item.get('link', '')
            content = item.get('content', '')
            date = item.get('publish_date', '')
            
            combined_content += f"# [智谱] {title}\n"
            if date:
                combined_content += f"日期: {date}\n"
            if link:
                combined_content += f"链接: {link}\n"
            combined_content += f"\n{content}\n\n"
        
        return {
            "success": True,
            "query": query,
            "search_results": search_results,
            "combined_content": combined_content,
            "source": "zhipu"
        }
        
    except Exception as e:
        if verbose:
            print(f"\n❌ 智谱搜索失败: {e}")
            print(f"   将使用 DuckDuckGo 作为替代...")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e),
            "query": query,
            "source": "zhipu"
        }


def search_with_volcengine(query: str, verbose: bool = False):
    """
    Step 1c: Search using Volcengine (火山引擎联网问答Agent API).
    
    文档: https://www.volcengine.com/docs/85508/1510834
    接入方式: APIKey接入
    URL: https://open.feedcoopapi.com/agent_api/agent/chat/completion
    """
    if verbose:
        print("\n" + "=" * 60)
        print("🔍 步骤 1c: 火山引擎联网问答搜索")
        print("=" * 60)
        print(f"\n📥 输入:")
        print(f"   搜索查询: {query}")
    
    try:
        search_conf = get_volcengine_search_config()
        api_key = search_conf.get('apiKey')
        bot_id = search_conf.get('botId')
        
        if not api_key:
            raise ValueError("火山引擎搜索 API Key 未配置。请在 conf.json 的 volcengine_search.apiKey 中设置")
        if not bot_id:
            raise ValueError("火山引擎 Bot ID 未配置。请在 conf.json 的 volcengine_search.botId 中设置")
        
        if verbose:
            print(f"\n🤖 正在调用火山引擎联网问答 API...")
            print(f"   Bot ID: {bot_id}")
        
        url = "https://open.feedcoopapi.com/agent_api/agent/chat/completion"
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "bot_id": bot_id,
            "messages": [
                {"role": "user", "content": query}
            ],
            "stream": False
        }
        
        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=60
        )
        response.raise_for_status()
        
        result = response.json()
        
        search_results = []
        combined_content = ""
        answer_content = ""
        
        if result.get("code") == 0 and result.get("data"):
            data = result["data"]
            
            if "answer" in data:
                answer_content = data["answer"]
                combined_content += f"# [火山引擎] 联网问答结果\n\n{answer_content}\n\n"
            
            if "references" in data and data["references"]:
                for ref in data["references"]:
                    search_results.append({
                        "title": ref.get("title", ""),
                        "link": ref.get("url", ""),
                        "content": ref.get("content", ref.get("summary", "")),
                        "site_name": ref.get("site_name", "")
                    })
                    combined_content += f"## [{ref.get('site_name', '参考')}] {ref.get('title', '')}\n"
                    combined_content += f"链接: {ref.get('url', '')}\n"
                    combined_content += f"{ref.get('content', ref.get('summary', ''))}\n\n"
            
            if "search_results" in data and data["search_results"]:
                for item in data["search_results"]:
                    search_results.append({
                        "title": item.get("title", ""),
                        "link": item.get("url", item.get("link", "")),
                        "content": item.get("content", item.get("snippet", "")),
                        "site_name": item.get("site_name", "")
                    })
        
        if verbose:
            print(f"\n📤 输出:")
            print(f"   火山引擎搜索成功: ✅")
            print(f"   找到参考结果: {len(search_results)} 条")
            if answer_content:
                print(f"   回答内容长度: {len(answer_content)} 字符")
                print(f"   回答预览: {answer_content[:200]}...")
            
            for i, item in enumerate(search_results[:3], 1):
                print(f"\n   {i}. {item.get('title', 'No title')}")
                print(f"      URL: {item.get('link', 'No link')}")
                content = item.get('content', '')
                if content:
                    print(f"      摘要: {content[:100]}...")
        
        return {
            "success": True,
            "query": query,
            "search_results": search_results,
            "combined_content": combined_content,
            "answer": answer_content,
            "source": "volcengine"
        }
        
    except Exception as e:
        if verbose:
            print(f"\n❌ 火山引擎搜索失败: {e}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e),
            "query": query,
            "source": "volcengine"
        }


def search_with_duckduckgo(query: str, verbose: bool = False, max_results: int = None):
    """
    Step 1b: Search using DuckDuckGo (ddgs).
    
    配置参数从 conf.json 的 duckduckgo_search 节点读取:
        maxResults: 返回结果数
        region: 地区代码
        safesearch: 安全搜索
        timelimit: 时间过滤
        backend: 搜索后端
        proxy: 代理地址
        timeout: 请求超时
    
    Args:
        query: 搜索查询
        verbose: 显示详细信息
        max_results: 覆盖配置的结果数（可选）
    """
    search_conf = get_duckduckgo_search_config()
    actual_max_results = max_results if max_results is not None else search_conf['maxResults']
    
    if verbose:
        print("\n" + "=" * 60)
        print("🔍 步骤 1b: DuckDuckGo 搜索")
        print("=" * 60)
        print(f"\n📥 输入:")
        print(f"   搜索查询: {query}")
        print(f"   结果数量: {actual_max_results}")
        print(f"   地区代码: {search_conf['region']}")
        print(f"   安全搜索: {search_conf['safesearch']}")
        print(f"   时间过滤: {search_conf['timelimit']} -> {search_conf['timelimit_mapped']}")
        print(f"   搜索后端: {search_conf['backend']}")
        if search_conf['proxy']:
            print(f"   代理地址: {search_conf['proxy']}")
        print(f"   超时设置: {search_conf['timeout']}s")
    
    try:
        from ddgs import DDGS
        
        if verbose:
            print(f"\n🤖 正在调用 DuckDuckGo...")
        
        ddgs_kwargs = {'timeout': search_conf['timeout']}
        if search_conf['proxy']:
            ddgs_kwargs['proxy'] = search_conf['proxy']
        
        with DDGS(**ddgs_kwargs) as ddgs:
            search_params = {
                'query': query,
                'max_results': actual_max_results,
                'region': search_conf['region'],
                'safesearch': search_conf['safesearch'],
                'backend': search_conf['backend']
            }
            if search_conf['timelimit_mapped']:
                search_params['timelimit'] = search_conf['timelimit_mapped']
            
            search_results = list(ddgs.text(**search_params))
        
        if verbose:
            print(f"\n📤 输出:")
            print(f"   DuckDuckGo 搜索成功: ✅")
            print(f"   找到结果: {len(search_results)} 条")
            
            for i, item in enumerate(search_results[:3], 1):
                print(f"\n   {i}. {item.get('title', 'No title')}")
                print(f"      URL: {item.get('href', 'No link')}")
                content = item.get('body', '')
                print(f"      摘要: {content[:100]}...")
        
        # Combine search results into a single text
        combined_content = ""
        for item in search_results:
            title = item.get('title', '')
            link = item.get('href', '')
            content = item.get('body', '')
            
            combined_content += f"# [DuckDuckGo] {title}\n"
            if link:
                combined_content += f"链接: {link}\n"
            combined_content += f"\n{content}\n\n"
        
        return {
            "success": True,
            "query": query,
            "search_results": search_results,
            "combined_content": combined_content,
            "source": "duckduckgo"
        }
        
    except Exception as e:
        if verbose:
            print(f"\n❌ DuckDuckGo 搜索失败: {e}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e),
            "query": query,
            "source": "duckduckgo"
        }


def extract_with_langextract(zhipu_data, ddg_data, volcengine_data=None, verbose: bool = False):
    """
    Step 2: Extract structured information using configured model (doubao/glm/zhipu).
    """
    if verbose:
        print("\n" + "=" * 60)
        print("📝 步骤 2: 结构化提取")
        print("=" * 60)
    
    volcengine_data = volcengine_data or {}
    
    combined_content = ""
    if zhipu_data.get("success"):
        combined_content += zhipu_data["combined_content"]
    if ddg_data.get("success"):
        combined_content += ddg_data["combined_content"]
    if volcengine_data.get("success"):
        combined_content += volcengine_data["combined_content"]
    
    extraction_config = get_extraction_config()
    max_content_length = extraction_config['max_content_length']
    if len(combined_content) > max_content_length:
        if verbose:
            print(f"⚠️ 内容过长 ({len(combined_content)} 字符)，截断至 {max_content_length} 字符")
        combined_content = combined_content[:max_content_length]
    
    if not combined_content:
        if verbose:
            print("❌ 所有搜索都失败，无法提取信息")
        return {
            "success": False,
            "error": "All searches failed",
            "zhipu_data": zhipu_data,
            "ddg_data": ddg_data,
            "volcengine_data": volcengine_data
        }
    
    try:
        model_config = get_langextract_config()
        model_provider = model_config['provider']
        model_name = model_config['model']
        base_url = model_config['baseUrl']
        api_key = model_config['apiKey']
        
        if not api_key:
            raise ValueError("langextract API Key 未配置。请在 conf.json 的 langextract.apiKey 中设置")
        
        if verbose:
            print(f"\n📥 输入:")
            print(f"   总搜索内容长度: {len(combined_content)} 字符")
            print(f"   模型提供商: {model_provider}")
            print(f"   模型名称: {model_name}")
            print(f"   Base URL: {base_url}")
        
        extraction_prompt = f"""基于以下网络搜索结果（包含智谱、DuckDuckGo、火山引擎的结果），请提取结构化信息：

搜索结果：
{combined_content}

请提取以下信息：
1. 主要内容摘要
2. 关键点列表（3-5个）
3. 相关事实或数据
4. 来源或参考信息（如果有）

请用清晰的格式输出。"""
        
        if verbose:
            print(f"\n🤖 正在调用 {model_provider} API...")
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model_name,
            "messages": [
                {
                    "role": "user",
                    "content": extraction_prompt
                }
            ],
            "temperature": 0.7,
            "max_tokens": 2000,
            "top_p": 0.9
        }
        
        response = requests.post(
            f"{base_url}/chat/completions",
            headers=headers,
            json=payload,
            timeout=120
        )
        response.raise_for_status()
        
        result = response.json()
        extracted_info = result["choices"][0]["message"]["content"]
        
        if verbose:
            print(f"\n📤 输出:")
            print(f"   提取成功: ✅")
            print(f"   提取内容长度: {len(extracted_info)} 字符")
            print(f"\n   提取内容（前500字符）:")
            print(f"   {extracted_info[:500]}...")
        
        return {
            "success": True,
            "zhipu_data": zhipu_data,
            "ddg_data": ddg_data,
            "volcengine_data": volcengine_data,
            "combined_content": combined_content,
            "extracted_info": extracted_info,
            "model_provider": model_provider,
            "model_name": model_name,
            "input": {
                "total_content_length": len(combined_content),
                "extraction_prompt": extraction_prompt[:200] + "..."
            }
        }
        
    except Exception as e:
        if verbose:
            print(f"\n❌ 提取失败: {e}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e),
            "zhipu_data": zhipu_data,
            "ddg_data": ddg_data,
            "volcengine_data": volcengine_data
        }


def save_results(final_result, output_dir: str, save_json: bool = False, verbose: bool = False):
    """Save results to files."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if verbose:
        print("\n" + "=" * 60)
        print("💾 保存结果")
        print("=" * 60)
        print(f"\n输出目录: {output_dir}")
    
    saved_files = []
    
    # Save Zhipu search result
    if final_result.get("zhipu_data", {}).get("success"):
        zhipu_file = output_path / f"zhipu_search_result_{timestamp}.md"
        with open(zhipu_file, "w", encoding="utf-8") as f:
            f.write(f"# 智谱 MCP 搜索结果\n\n")
            f.write(f"**查询**: {final_result['zhipu_data']['query']}\n\n")
            f.write(f"**时间**: {datetime.now().isoformat()}\n\n")
            f.write("---\n\n")
            f.write(final_result['zhipu_data']['combined_content'])
        saved_files.append(str(zhipu_file))
        if verbose:
            print(f"✅ 已保存: {zhipu_file.name}")
    
    # Save DuckDuckGo search result
    if final_result.get("ddg_data", {}).get("success"):
        ddg_file = output_path / f"duckduckgo_search_result_{timestamp}.md"
        with open(ddg_file, "w", encoding="utf-8") as f:
            f.write(f"# DuckDuckGo 搜索结果\n\n")
            f.write(f"**查询**: {final_result['ddg_data']['query']}\n\n")
            f.write(f"**时间**: {datetime.now().isoformat()}\n\n")
            f.write("---\n\n")
            f.write(final_result['ddg_data']['combined_content'])
        saved_files.append(str(ddg_file))
        if verbose:
            print(f"✅ 已保存: {ddg_file.name}")
    
    # Save Volcengine search result
    if final_result.get("volcengine_data", {}).get("success"):
        volcengine_file = output_path / f"volcengine_search_result_{timestamp}.md"
        with open(volcengine_file, "w", encoding="utf-8") as f:
            f.write(f"# 火山引擎联网问答搜索结果\n\n")
            f.write(f"**查询**: {final_result['volcengine_data']['query']}\n\n")
            f.write(f"**时间**: {datetime.now().isoformat()}\n\n")
            f.write("---\n\n")
            f.write(final_result['volcengine_data']['combined_content'])
        saved_files.append(str(volcengine_file))
        if verbose:
            print(f"✅ 已保存: {volcengine_file.name}")
    
    # Save extracted info
    if final_result.get("success") and final_result.get("extracted_info"):
        extract_file = output_path / f"extracted_info_{timestamp}.md"
        with open(extract_file, "w", encoding="utf-8") as f:
            f.write(f"# 提取的结构化信息\n\n")
            f.write(f"**源查询**: {final_result['zhipu_data']['query'] if final_result.get('zhipu_data') else final_result['ddg_data']['query']}\n\n")
            f.write(f"**时间**: {datetime.now().isoformat()}\n\n")
            f.write("---\n\n")
            f.write(final_result['extracted_info'])
        saved_files.append(str(extract_file))
        if verbose:
            print(f"✅ 已保存: {extract_file.name}")
    
    # Save workflow summary
    summary_file = output_path / f"workflow_summary_{timestamp}.md"
    with open(summary_file, "w", encoding="utf-8") as f:
        f.write(f"# 工作流摘要\n\n")
        f.write(f"**时间**: {datetime.now().isoformat()}\n\n")
        f.write(f"**状态**: {'✅ 成功' if final_result.get('success') else '❌ 失败'}\n\n")
        
        if final_result.get("success"):
            query = (
                final_result.get('zhipu_data', {}).get('query') or 
                final_result.get('ddg_data', {}).get('query') or
                final_result.get('volcengine_data', {}).get('query') or
                ''
            )
            f.write(f"**查询**: {query}\n\n")
            if final_result.get("zhipu_data", {}).get("success"):
                f.write(f"**智谱搜索结果数**: {len(final_result['zhipu_data'].get('search_results', []))} 条\n\n")
            if final_result.get("ddg_data", {}).get("success"):
                f.write(f"**DuckDuckGo 搜索结果数**: {len(final_result['ddg_data'].get('search_results', []))} 条\n\n")
            if final_result.get("volcengine_data", {}).get("success"):
                f.write(f"**火山引擎搜索结果数**: {len(final_result['volcengine_data'].get('search_results', []))} 条\n\n")
            f.write(f"**总搜索内容长度**: {len(final_result['combined_content'])} 字符\n\n")
            if final_result.get("extracted_info"):
                f.write(f"**提取内容长度**: {len(final_result['extracted_info'])} 字符\n\n")
        
        if final_result.get("error"):
            f.write(f"**错误**: {final_result['error']}\n\n")
        
        if final_result.get("warning"):
            f.write(f"**警告**: {final_result['warning']}\n\n")
    
    saved_files.append(str(summary_file))
    if verbose:
        print(f"✅ 已保存: {summary_file.name}")
    
    # Save full JSON
    if save_json:
        json_file = output_path / f"full_results_{timestamp}.json"
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(final_result, f, ensure_ascii=False, indent=2)
        saved_files.append(str(json_file))
        if verbose:
            print(f"✅ 已保存: {json_file.name}")
    
    return saved_files


def main():
    add_project_path()
    
    parser = argparse.ArgumentParser(
        description="智谱 MCP + DuckDuckGo + 火山引擎 + 豆包 搜索提取工作流"
    )
    parser.add_argument(
        "query",
        nargs="?",
        help="搜索关键词（也可以用 --query 指定）"
    )
    parser.add_argument(
        "--query",
        help="搜索关键词"
    )
    parser.add_argument(
        "--save-json",
        action="store_true",
        help="保存完整的 JSON 结果"
    )
    parser.add_argument(
        "--output-dir",
        default=str(PROJECT_ROOT / "output"),
        help="输出目录"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="显示详细的输入和输出信息（验证用）"
    )
    parser.add_argument(
        "--ddg-max-results",
        type=int,
        default=None,
        help="DuckDuckGo 最大搜索结果数（覆盖配置文件，默认使用 conf.json 中的 maxResults）"
    )
    parser.add_argument(
        "--volcengine",
        action="store_true",
        help="启用火山引擎联网问答搜索（需在 conf.json 中配置 volcengine_search）"
    )
    parser.add_argument(
        "--volcengine-only",
        action="store_true",
        help="仅使用火山引擎搜索（不使用智谱和DuckDuckGo）"
    )
    
    args = parser.parse_args()
    
    # 获取查询关键词：位置参数或 --query 参数二选一
    search_query = args.query
    
    if not search_query:
        print("❌ 请提供搜索关键词！")
        parser.print_help()
        sys.exit(1)
    
    print("=" * 60)
    print("🔄 智谱 MCP + DuckDuckGo + 火山引擎 + 豆包 工作流")
    print("=" * 60)
    
    zhipu_result = {}
    ddg_result = {}
    volcengine_result = {}
    
    if args.volcengine_only:
        volcengine_result = search_with_volcengine(search_query, verbose=args.verbose)
    else:
        zhipu_search_conf = get_zhipu_search_config()
        if zhipu_search_conf.get('enabled', True):
            zhipu_result = search_with_zhipu_mcp(search_query, verbose=args.verbose)
        else:
            if args.verbose:
                print("\n⏭️ 智谱搜索已禁用，跳过...")
        ddg_result = search_with_duckduckgo(search_query, verbose=args.verbose, max_results=args.ddg_max_results)
        
        if args.volcengine:
            volcengine_result = search_with_volcengine(search_query, verbose=args.verbose)
    
    final_result = extract_with_langextract(
        zhipu_result, ddg_result, volcengine_result, verbose=args.verbose
    )
    
    # Save results
    saved_files = save_results(
        final_result,
        args.output_dir,
        save_json=args.save_json,
        verbose=args.verbose
    )
    
    # Final summary
    print("\n" + "=" * 60)
    print("📋 工作流完成")
    print("=" * 60)
    
    if final_result.get("success"):
        print(f"\n✅ 工作流成功！")
        print(f"   查询: {search_query}")
        if final_result.get("zhipu_data", {}).get("success"):
            print(f"   智谱搜索结果: {len(zhipu_result.get('search_results', []))} 条")
        if final_result.get("ddg_data", {}).get("success"):
            print(f"   DuckDuckGo 搜索结果: {len(ddg_result.get('search_results', []))} 条")
        if final_result.get("volcengine_data", {}).get("success"):
            print(f"   火山引擎搜索结果: {len(volcengine_result.get('search_results', []))} 条")
        print(f"   保存文件: {len(saved_files)} 个")
        for f in saved_files:
            print(f"   - {Path(f).name}")
        
        print("\n" + "=" * 60)
        print("📝 提取的信息")
        print("=" * 60)
        print("\n" + final_result["extracted_info"])
    else:
        print(f"\n❌ 工作流失败: {final_result.get('error', 'Unknown error')}")
    
    print("\n" + "=" * 60)


if __name__ == '__main__':
    main()
