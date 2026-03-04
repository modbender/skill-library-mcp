#!/usr/bin/env python3
"""YouTube搜索结果视频链接提取器 - 测试文件"""

import pytest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from youtube_search_extractor import YouTubeSearchExtractor

class TestYouTubeSearchExtractor:
    """YouTube搜索结果视频链接提取器测试类"""
    
    def test_extractor_initialization(self):
        """测试提取器初始化"""
        extractor = YouTubeSearchExtractor()
        assert isinstance(extractor, YouTubeSearchExtractor)
        assert extractor.wait_time == 5
        assert extractor.max_links == 50
    
    def test_url_encoding(self):
        """测试URL编码功能"""
        extractor = YouTubeSearchExtractor()
        
        # 测试中文关键词编码
        chinese_text = "hydrasynth 实战应用"
        encoded = extractor._url_encode(chinese_text)
        assert isinstance(encoded, str)
        assert '%' in encoded  # 应该包含URL编码字符
        
        # 测试英文关键词编码
        english_text = "hydrasynth practical applications"
        encoded = extractor._url_encode(english_text)
        assert isinstance(encoded, str)
        
        # 测试包含特殊字符的关键词
        special_text = "openclaw tutorial 2024!@#$%^&*()"
        encoded = extractor._url_encode(special_text)
        assert isinstance(encoded, str)
        assert '!' not in encoded
        assert '@' not in encoded
    
    def test_video_link_extraction_from_sample_html(self):
        """测试从示例HTML中提取视频链接"""
        extractor = YouTubeSearchExtractor()
        
        # 示例HTML片段（包含真实的YouTube视频链接）
        sample_html = '''
        <div class="yt-lockup-content">
            <h3 class="yt-lockup-title">
                <a href="/watch?v=dQw4w9WgXcQ" title="Never Gonna Give You Up">Never Gonna Give You Up</a>
            </h3>
        </div>
        <div class="yt-lockup-content">
            <h3 class="yt-lockup-title">
                <a href="/watch?v=9bZkp7q19f0" title="Gangnam Style">Gangnam Style</a>
            </h3>
        </div>
        <div class="yt-lockup-content">
            <h3 class="yt-lockup-title">
                <a href="/watch?v=oHg5SJYRHA0" title="Rickroll">Rickroll</a>
            </h3>
        </div>
        '''
        
        links = extractor.extract_video_links(sample_html)
        
        assert len(links) == 3
        assert "https://www.youtube.com/watch?v=dQw4w9WgXcQ" in links
        assert "https://www.youtube.com/watch?v=9bZkp7q19f0" in links
        assert "https://www.youtube.com/watch?v=oHg5SJYRHA0" in links
    
    def test_extraction_from_real_sample_html(self):
        """测试从真实的YouTube搜索结果HTML中提取链接"""
        extractor = YouTubeSearchExtractor()
        
        # 真实的YouTube搜索结果HTML片段
        real_sample_html = '''
        <ytd-video-renderer class="style-scope ytd-item-section-renderer">
            <a id="video-title" class="yt-simple-endpoint style-scope ytd-video-renderer" 
               title="HYDRASYNTH 实战应用 - 合成器教程" 
               href="/watch?v=O37_qc3jhsc">
                <yt-formatted-string class="style-scope ytd-video-renderer">HYDRASYNTH 实战应用 - 合成器教程</yt-formatted-string>
            </a>
        </ytd-video-renderer>
        <ytd-video-renderer class="style-scope ytd-item-section-renderer">
            <a id="video-title" class="yt-simple-endpoint style-scope ytd-video-renderer" 
               title="Hydrasynth 音色设计实战" 
               href="/watch?v=t0Ic87OLHRE">
                <yt-formatted-string class="style-scope ytd-video-renderer">Hydrasynth 音色设计实战</yt-formatted-string>
            </a>
        </ytd-video-renderer>
        '''
        
        links = extractor.extract_video_links(real_sample_html)
        
        assert len(links) >= 2
        assert any("O37_qc3jhsc" in link for link in links)
        assert any("t0Ic87OLHRE" in link for link in links)
    
    def test_duplicate_links_handling(self):
        """测试重复链接处理"""
        extractor = YouTubeSearchExtractor()
        
        duplicate_html = '''
        <div class="yt-lockup-content">
            <h3 class="yt-lockup-title">
                <a href="/watch?v=dQw4w9WgXcQ" title="Never Gonna Give You Up">Never Gonna Give You Up</a>
            </h3>
        </div>
        <div class="yt-lockup-content">
            <h3 class="yt-lockup-title">
                <a href="/watch?v=dQw4w9WgXcQ" title="Never Gonna Give You Up">Never Gonna Give You Up</a>
            </h3>
        </div>
        '''
        
        links = extractor.extract_video_links(duplicate_html)
        
        assert len(links) == 1
        assert "https://www.youtube.com/watch?v=dQw4w9WgXcQ" in links
    
    def test_different_video_link_formats(self):
        """测试不同格式的视频链接提取"""
        extractor = YouTubeSearchExtractor()
        
        test_html = '''
        <!-- 标准YouTube链接 -->
        <a href="/watch?v=dQw4w9WgXcQ">视频1</a>
        <!-- 完整URL格式 -->
        <a href="https://www.youtube.com/watch?v=9bZkp7q19f0">视频2</a>
        <!-- youtu.be短链接 -->
        <a href="https://youtu.be/oHg5SJYRHA0">视频3</a>
        <!-- 带参数的链接 -->
        <a href="/watch?v=abc123&t=10s&list=PLabc">视频4</a>
        '''
        
        links = extractor.extract_video_links(test_html)
        
        assert len(links) == 4
        assert all('http' in link for link in links)
        assert "https://www.youtube.com/watch?v=dQw4w9WgXcQ" in links
        assert "https://www.youtube.com/watch?v=9bZkp7q19f0" in links
        assert "https://youtu.be/oHg5SJYRHA0" in links
        assert any("abc123" in link for link in links)

def test_command_line_arguments():
    """测试命令行参数解析"""
    from unittest.mock import patch
    
    with patch('sys.argv', [
        'youtube_search_extractor.py',
        'hydrasynth 实战应用',
        'hydrasynth_test',
        '--headless',
        '--wait-time', '10',
        '--max-links', '30'
    ]):
        with pytest.raises(SystemExit) as pytest_wrapped_e:
            import youtube_search_extractor
            youtube_search_extractor.main()
    
    assert pytest_wrapped_e.type == SystemExit
    # 这里会失败，因为我们没有模拟实际的网络请求

if __name__ == "__main__":
    pytest.main([__file__, '-v'])
