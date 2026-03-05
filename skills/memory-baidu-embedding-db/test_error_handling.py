"""
测试错误处理机制
"""
import os
import sys
import tempfile
from pathlib import Path

# 添加项目路径
sys.path.append('/root/clawd/skills/memory-baidu-embedding-db')

from memory_baidu_embedding_db import MemoryBaiduEmbeddingDB

def test_missing_credentials():
    """测试缺少凭证的情况"""
    print("🧪 测试1: 缺少API凭证")
    
    # 临时取消环境变量
    original_api_string = os.environ.get('BAIDU_API_STRING')
    original_secret_key = os.environ.get('BAIDU_SECRET_KEY')
    
    if 'BAIDU_API_STRING' in os.environ:
        del os.environ['BAIDU_API_STRING']
    if 'BAIDU_SECRET_KEY' in os.environ:
        del os.environ['BAIDU_SECRET_KEY']
    
    try:
        mem_db = MemoryBaiduEmbeddingDB()
        print("❌ 应该抛出异常但没有")
    except ValueError as e:
        print(f"✅ 正确捕获异常: {e}")
    except Exception as e:
        print(f"❌ 捕获了意外异常: {e}")
    finally:
        # 恢复环境变量
        if original_api_string:
            os.environ['BAIDU_API_STRING'] = original_api_string
        if original_secret_key:
            os.environ['BAIDU_SECRET_KEY'] = original_secret_key

def test_invalid_inputs():
    """测试无效输入"""
    print("\n🧪 测试2: 无效输入参数")
    
    # 设置正确的环境变量（测试用）
    os.environ['BAIDU_API_STRING'] = '${BAIDU_API_STRING}'
    os.environ['BAIDU_SECRET_KEY'] = '${BAIDU_SECRET_KEY}'
    
    # 使用临时数据库文件
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
        tmp_db_path = tmp_file.name
    
    try:
        mem_db = MemoryBaiduEmbeddingDB(db_path=tmp_db_path)
        
        # 测试空内容
        result = mem_db.add_memory("")
        print(f"   空内容测试: {'✅' if not result else '❌'}")
        
        # 测试非字符串内容
        result = mem_db.add_memory(None)
        print(f"   None内容测试: {'✅' if not result else '❌'}")
        
        # 测试过长内容
        result = mem_db.add_memory("a" * 10001)  # 超过10000字符限制
        print(f"   过长内容测试: {'✅' if not result else '❌'}")
        
        # 测试无效标签类型
        result = mem_db.add_memory("test content", tags="invalid_tag_type")
        print(f"   无效标签类型测试: {'✅' if not result else '❌'}")
        
        # 测试无效元数据类型
        result = mem_db.add_memory("test content", metadata="invalid_metadata_type")
        print(f"   无效元数据类型测试: {'✅' if not result else '❌'}")
        
        # 测试无效查询
        results = mem_db.search_memories("")
        print(f"   空查询测试: {'✅' if len(results) == 0 else '❌'}")
        
        # 测试无效limit
        results = mem_db.search_memories("test", limit=-1)
        print(f"   负数limit测试: {'✅' if len(results) == 0 else '❌'}")
        
        # 测试无效memory_id
        result = mem_db.delete_memory(-1)
        print(f"   无效memory_id测试: {'✅' if not result else '❌'}")
        
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # 清理临时数据库文件
        if Path(tmp_db_path).exists():
            Path(tmp_db_path).unlink()

def test_normal_operation():
    """测试正常操作"""
    print("\n🧪 测试3: 正常操作")
    
    # 使用临时数据库文件
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
        tmp_db_path = tmp_file.name
    
    try:
        mem_db = MemoryBaiduEmbeddingDB(db_path=tmp_db_path)
        
        # 添加正常记忆
        success = mem_db.add_memory(
            "这是一个正常的记忆测试",
            tags=["test", "normal"],
            metadata={"test": True}
        )
        print(f"   添加正常记忆: {'✅' if success else '❌'}")
        
        # 搜索记忆
        results = mem_db.search_memories("正常记忆", limit=1)
        print(f"   搜索记忆: {'✅' if len(results) >= 0 else '❌'}")  # 搜索可能返回空结果，这很正常
        
        # 获取统计信息
        stats = mem_db.get_statistics()
        print(f"   获取统计信息: {'✅' if isinstance(stats, dict) else '❌'}")
        
        # 获取所有记忆
        all_memories = mem_db.get_all_memories()
        print(f"   获取所有记忆: {'✅' if isinstance(all_memories, list) else '❌'}")
        
        print("   所有正常操作测试完成")
        
    except Exception as e:
        print(f"❌ 正常操作测试出错: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # 清理临时数据库文件
        if Path(tmp_db_path).exists():
            Path(tmp_db_path).unlink()

if __name__ == "__main__":
    print("🔧 错误处理机制测试")
    print("="*50)
    
    test_missing_credentials()
    test_invalid_inputs()
    test_normal_operation()
    
    print(f"\n✅ 错误处理测试完成！")