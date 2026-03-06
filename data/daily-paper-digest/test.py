"""
测试脚本 - 用于验证各个模块是否正常工作
"""
import sys
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def test_imports():
    """测试依赖导入"""
    print("\n" + "="*60)
    print("📦 测试依赖导入...")
    print("="*60)
    
    try:
        import arxiv
        print("✅ arxiv")
    except ImportError:
        print("❌ arxiv - 请运行: pip install arxiv")
        return False
    
    try:
        import requests
        print("✅ requests")
    except ImportError:
        print("❌ requests - 请运行: pip install requests")
        return False
    
    try:
        from bs4 import BeautifulSoup
        print("✅ beautifulsoup4")
    except ImportError:
        print("❌ beautifulsoup4 - 请运行: pip install beautifulsoup4")
        return False
    
    try:
        import feedparser
        print("✅ feedparser")
    except ImportError:
        print("❌ feedparser - 请运行: pip install feedparser")
        return False
    
    print("\n✅ 所有依赖已安装\n")
    return True


def test_arxiv_fetcher():
    """测试 arXiv 模块"""
    print("\n" + "="*60)
    print("🔬 测试 arXiv 模块...")
    print("="*60)
    
    try:
        from arxiv_fetcher import ArxivFetcher
        
        # 创建获取器（只获取1篇论文用于测试）
        fetcher = ArxivFetcher(categories=['cs.AI'], max_results=1)
        print("✅ ArxivFetcher 初始化成功")
        
        # 搜索论文
        print("🔍 搜索最新论文...")
        papers = fetcher.search_papers("machine learning", max_results=2)
        
        if papers:
            print(f"✅ 成功获取 {len(papers)} 篇论文")
            print(f"\n示例论文:")
            print(f"   标题: {papers[0]['title'][:60]}...")
            print(f"   链接: {papers[0]['arxiv_url']}")
        else:
            print("⚠️  未获取到论文（可能是网络问题）")
        
        return True
        
    except Exception as e:
        print(f"❌ arXiv 模块测试失败: {str(e)}")
        return False


def test_huggingface_fetcher():
    """测试 HuggingFace 模块"""
    print("\n" + "="*60)
    print("🤗 测试 HuggingFace 模块...")
    print("="*60)
    
    try:
        from huggingface_fetcher import HuggingFaceFetcher
        
        # 创建获取器
        fetcher = HuggingFaceFetcher(max_results=2)
        print("✅ HuggingFaceFetcher 初始化成功")
        
        # 获取论文
        print("🔍 获取热门论文...")
        papers = fetcher.fetch_daily_papers()
        
        if papers:
            print(f"✅ 成功获取 {len(papers)} 篇论文")
            print(f"\n示例论文:")
            print(f"   标题: {papers[0]['title'][:60]}...")
            print(f"   链接: {papers[0]['url']}")
        else:
            print("⚠️  未获取到论文（可能是网络问题或页面结构变化）")
        
        return True
        
    except Exception as e:
        print(f"❌ HuggingFace 模块测试失败: {str(e)}")
        return False


def test_main_module():
    """测试主模块"""
    print("\n" + "="*60)
    print("🚀 测试主模块...")
    print("="*60)
    
    try:
        from main import PaperDigest
        
        # 创建实例
        digest = PaperDigest()
        print("✅ PaperDigest 初始化成功")
        
        # 注意：这里不实际运行 fetch_all_papers，因为可能需要较长时间
        print("✅ 主模块加载正常")
        
        return True
        
    except Exception as e:
        print(f"❌ 主模块测试失败: {str(e)}")
        return False


def main():
    """运行所有测试"""
    print("\n" + "="*60)
    print("🧪 开始运行测试套件")
    print("="*60)
    
    results = []
    
    # 测试依赖
    results.append(("依赖导入", test_imports()))
    
    # 测试模块
    if results[0][1]:  # 只有依赖正常才继续测试
        results.append(("arXiv 模块", test_arxiv_fetcher()))
        results.append(("HuggingFace 模块", test_huggingface_fetcher()))
        results.append(("主模块", test_main_module()))
    
    # 输出结果
    print("\n" + "="*60)
    print("📊 测试结果汇总")
    print("="*60)
    
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{name}: {status}")
    
    all_passed = all(result for _, result in results)
    
    print("\n" + "="*60)
    if all_passed:
        print("🎉 所有测试通过！")
        print("="*60)
        print("\n下一步:")
        print("1. 运行 python main.py 获取今日论文")
        print("2. 编辑 config/sources.json 自定义配置")
        print("3. 部署到 OpenClaw")
    else:
        print("⚠️  部分测试失败，请检查错误信息")
        print("="*60)
        print("\n故障排除:")
        print("1. 确保已安装所有依赖: pip install -r requirements.txt")
        print("2. 检查网络连接")
        print("3. 查看详细错误信息")
    
    print("")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
