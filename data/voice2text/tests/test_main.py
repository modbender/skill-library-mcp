from main import run

def test_transcribe(tmp_path):
    # 此处应放置合法的 16kHz 单声道 wav 示例文件，实际运行需提供。
    sample = tmp_path / "sample.wav"
    # 为演示目的，不实际生成 wav，假设文件存在。
    result = run({"audio": str(sample)})
    assert isinstance(result["text"], str)
