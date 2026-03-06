#!/usr/bin/env python3
"""YouTube搜索结果视频链接提取器 - 从文件中提取链接的测试脚本"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from youtube_search_extractor import YouTubeSearchExtractor

def test_extraction_from_file():
    """测试从保存的HTML文件中提取链接"""
    print("🔍 测试从保存的HTML文件中提取链接...")
    
    # 使用之前保存的Hydrasynth搜索结果文件
    test_file = "hydrasynth_search_results.html"
    
    if not os.path.exists(test_file):
        print(f"❌ 测试文件 '{test_file}' 不存在")
        return False
    
    print(f"✅ 找到测试文件: {test_file}")
    
    try:
        with open(test_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
            
        print(f"✅ 文件大小: {len(html_content)} 字符")
        
        extractor = YouTubeSearchExtractor()
        
        # 测试链接提取功能
        links = extractor.extract_video_links(html_content)
        
        if links:
            print(f"✅ 成功提取 {len(links)} 个视频链接")
            
            # 测试链接格式
            valid_links = [link for link in links if 
                         (link.startswith('https://www.youtube.com/watch?v=') or 
                          link.startswith('https://youtu.be/')) and 
                         len(link) > 20]
            
            print(f"✅ 格式正确的链接: {len(valid_links)} 个")
            
            if valid_links:
                print("\n📄 链接预览（前5个）:")
                for i, link in enumerate(valid_links[:5], 1):
                    print(f"{i}. {link}")
                
                # 保存到临时文件
                output_file = "hydrasynth_test_links"
                timestamp = __import__('datetime').datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                with open(f"{output_file}_links.txt", 'w', encoding='utf-8') as f:
                    f.write(f"# YouTube搜索结果：'hydrasynth 实战应用' ({timestamp})\n")
                    f.write(f"# 找到 {len(valid_links)} 个相关视频\n\n")
                    
                    for i, link in enumerate(valid_links, 1):
                        f.write(f"{i}. {link}\n")
                
                print(f"\n✅ 链接已保存到: {output_file}_links.txt")
                
                return True
            else:
                print("❌ 提取的链接格式无效")
                return False
                
        else:
            print("❌ 未找到视频链接")
            return False
            
    except Exception as e:
        print(f"❌ 提取过程中出错: {e}")
        import traceback
        print(traceback.format_exc())
        return False

def test_with_sample_html():
    """测试使用示例HTML内容"""
    print("\n🔍 测试使用示例HTML内容...")
    
    sample_html = '''
    <div class="yt-lockup-content">
        <h3 class="yt-lockup-title">
            <a href="/watch?v=O37_qc3jhsc" title="HYDRASYNTH 实战应用 - 合成器教程">HYDRASYNTH 实战应用 - 合成器教程</a>
        </h3>
    </div>
    <div class="yt-lockup-content">
        <h3 class="yt-lockup-title">
            <a href="/watch?v=t0Ic87OLHRE" title="Hydrasynth 音色设计实战">Hydrasynth 音色设计实战</a>
        </h3>
    </div>
    <div class="yt-lockup-content">
        <h3 class="yt-lockup-title">
            <a href="https://youtu.be/NB5D34KDMxs" title="Hydrasynth 演奏技巧">Hydrasynth 演奏技巧</a>
        </h3>
    </div>
    '''
    
    try:
        extractor = YouTubeSearchExtractor()
        
        links = extractor.extract_video_links(sample_html)
        
        if links:
            print(f"✅ 成功提取 {len(links)} 个视频链接")
            
            for i, link in enumerate(links, 1):
                print(f"{i}. {link}")
                
            return True
        else:
            print("❌ 未找到视频链接")
            return False
            
    except Exception as e:
        print(f"❌ 测试过程中出错: {e}")
        import traceback
        print(traceback.format_exc())
        return False

def main():
    """主函数"""
    print("=== YouTube Search Extractor 从文件中提取链接的测试 ===")
    
    if not os.path.exists('youtube_search_extractor.py'):
        print("❌ 请在正确的目录下运行")
        return False
    
    success = True
    
    # 测试从文件中提取
    if os.path.exists("hydrasynth_search_results.html"):
        if not test_extraction_from_file():
            success = False
    else:
        print("⚠️  未找到 hydrasynth_search_results.html，跳过从文件中提取的测试")
    
    # 测试示例HTML
    if not test_with_sample_html():
        success = False
    
    if success:
        print("\n🎉 所有测试通过！从文件中提取链接的功能正常")
        return True
    else:
        print("\n❌ 测试失败，请检查上述错误信息")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
