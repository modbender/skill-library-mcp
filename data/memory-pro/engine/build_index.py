from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import os
from preprocess import preprocess_directory

def build_index():
    """
    構建 FAISS 索引並保存到指定路徑
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    index_dir = os.getenv("MEMORY_PRO_INDEX_DIR", base_dir)
    output_path = os.getenv("MEMORY_PRO_INDEX_PATH", os.path.join(index_dir, "memory.index"))
    sentences_path = os.path.join(index_dir, "sentences.txt")
    
    print("🔍 開始構建索引...")
    
    model = SentenceTransformer('all-MiniLM-L6-v2')
    sentences = preprocess_directory()
    print(f"📊 找到 {len(sentences)} 個有效句子")
    embeddings = model.encode(sentences)
    index = faiss.IndexFlatL2(embeddings.shape[1])
    faiss.normalize_L2(embeddings)
    index.add(embeddings)
    
    print(f"💾 保存索引到 {output_path}...")
    faiss.write_index(index, output_path)
    with open(sentences_path, "w", encoding="utf-8") as f:
        f.write("\n".join(sentences))
    print(f"✅ 索引構建完成！包含 {len(sentences)} 個句子")
    return sentences, index

if __name__ == "__main__":
    sentences, index = build_index()
