import pytest
from read_wechat_article import read_wechat_article, WeChatArticleError, clean_wechat_url


def test_clean_wechat_url():
    """测试URL清理"""
    test_urls = [
        (
            "https://mp.weixin.qq.com/s/ijZyuHyubiX7Dp1tJrxZOw?from=groupmessage&isappinstalled=0",
            "https://mp.weixin.qq.com/s/ijZyuHyubiX7Dp1tJrxZOw"
        ),
        (
            "https://mp.weixin.qq.com/s/abc123?utm_source=github&utm_medium=readme",
            "https://mp.weixin.qq.com/s/abc123"
        ),
        (
            "https://mp.weixin.qq.com/s/abc_def-123",
            "https://mp.weixin.qq.com/s/abc_def-123"
        ),
    ]
    
    for original, expected in test_urls:
        assert clean_wechat_url(original) == expected


def test_invalid_url():
    """测试无效URL"""
    with pytest.raises(ValueError):
        read_wechat_article("https://example.com")
        
    with pytest.raises(ValueError):
        read_wechat_article("https://mp.weixin.qq.com/xxx/abc123")


def test_url_validation():
    """测试URL格式验证"""
    valid_urls = [
        "https://mp.weixin.qq.com/s/ijZyuHyubiX7Dp1tJrxZOw",
        "https://mp.weixin.qq.com/s/ABC-DEF_123",
        "https://mp.weixin.qq.com/s/a",
    ]
    
    for url in valid_urls:
        try:
            # 不实际执行网络请求，只验证格式
            result = read_wechat_article(url)
            # 如果成功，断言应该返回结果
            assert result is not None
        except ValueError:
            pytest.fail(f"Valid URL rejected: {url}")
        except WeChatArticleError:
            # 网络请求失败是预期的，只要不抛ValueError
            pass


def test_result_structure():
    """测试结果结构"""
    # 使用一个已知的文章URL进行测试
    url = "https://mp.weixin.qq.com/s/ijZyuHyubiX7Dp1tJrxZOw"
    
    try:
        result = read_wechat_article(url)
        
        # 验证结果结构
        assert isinstance(result, dict)
        assert "title" in result
        assert isinstance(result["title"], str)
        
        assert "author" in result
        assert isinstance(result["author"], str)
        
        assert "content_markdown" in result
        assert isinstance(result["content_markdown"], str)
        
        assert "content_text" in result
        assert isinstance(result["content_text"], str)
        
        assert "images" in result
        assert isinstance(result["images"], list)
        
        assert "word_count" in result
        assert isinstance(result["word_count"], int)
        assert result["word_count"] >= 0
        
        assert "read_time_minutes" in result
        assert isinstance(result["read_time_minutes"], int)
        assert result["read_time_minutes"] >= 1
        
    except WeChatArticleError as e:
        print(f"网络请求失败，跳过结构测试: {e}")
        pytest.skip("网络请求失败，跳过结构测试")


def test_empty_result_handling():
    """测试空结果处理"""
    # 这个测试需要模拟网络请求
    pass


if __name__ == "__main__":
    pytest.main([__file__])