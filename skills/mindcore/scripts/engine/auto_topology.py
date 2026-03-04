"""
auto_topology.py — 突触矩阵自动拓扑生成器
仿生情感心智引擎 (Biomimetic Mind Engine)

功能：
通过对 Layer 1 (感知开关) 和 Layer 2 (潜意识冲动) 的节点进行自然语言描述，
获取文本 Embedding，然后计算它们之间的余弦相似度。
生成的 50x50 相似度矩阵作为全连接层的突触权重 (Synapse Matrix)，
实现"无需硬编码的神经网络连接"。

例如：
"睡眠剥夺" (sleep_deprived) 和 "想睡觉" (impulse_sleep) 的相似度高，权重就大；
"下雨" (is_raining) 可能与 "想自闭" (impulse_withdraw) 产生中等连接。
"""

import os
import json
import numpy as np

# 为了避免强依赖 OpenAI 导致无法运行，这里支持 mock 模式
try:
    from sentence_transformers import SentenceTransformer
    HAS_LOCAL_MODEL = True
except ImportError:
    HAS_LOCAL_MODEL = False

from engine.config import DATA_DIR, TOTAL_LAYER1_NODES, TOTAL_LAYER2_NODES
from engine.layer1_sensors import ALL_KEYS as LAYER1_KEYS
from engine.layer2_impulses import IMPULSE_NAMES as LAYER2_KEYS

SYNAPSE_MATRIX_PATH = os.path.join(DATA_DIR, "Synapse_Matrix.npy")

def cosine_similarity(v1: np.ndarray, v2: np.ndarray) -> float:
    dot_product = np.dot(v1, v2)
    norm1 = np.linalg.norm(v1)
    norm2 = np.linalg.norm(v2)
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return float(dot_product / (norm1 * norm2))

class AutoTopologyBuilder:
    def __init__(self):
        self.use_mock = not HAS_LOCAL_MODEL
        
        if not self.use_mock:
            print("[AutoTopology] 正在加载本地小红书级的轻量 NLP 模型 (all-MiniLM-L6-v2)...")
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            print("[AutoTopology] 本地模型加载成功，无需网络和费用。")
        else:
            print("[AutoTopology] WARNING: sentence-transformers 未安装。退回至伪随机哈希布线 (Mock Embeddings)。")
            
    def get_embeddings_batch(self, texts: list) -> list:
        """批量获取文本的 Embedding 向量。"""
        if self.use_mock:
            # 伪造一组随机向量，但为了保持同一个单词的向量一致，用 hash 设定 seed
            embeddings = []
            for t in texts:
                np.random.seed(abs(hash(t)) % (2**32))
                embeddings.append(np.random.randn(384))
            return embeddings
            
        print(f"[AutoTopology] 正在批量本地嵌入 {len(texts)} 条语料...")
        embeddings = self.model.encode(texts)
        return embeddings

    def generate_descriptions(self) -> tuple:
        """为所有节点生成自然语言描述（提示词）。"""
        # Node 49 (最后一个) 是用于 ignored_long_time 的连续压力补充，或者是为了对齐 50 个。
        # 这里保证 L1 个数是 50
        l1_descriptions = []
        for key in LAYER1_KEYS:
            # 去除前缀和下划线，作为自然语言文本
            desc = key.replace("is_", "").replace("_", " ")
            l1_descriptions.append(f"The person is experiencing {desc}")
            
        # 补齐到 50 个
        while len(l1_descriptions) < TOTAL_LAYER1_NODES:
            l1_descriptions.append("The person feeling general need pressure and loneliness")

        l2_descriptions = []
        for key in LAYER2_KEYS:
            desc = key.replace("impulse_", "").replace("_", " ")
            l2_descriptions.append(f"The urge and impulse to {desc}")

        return l1_descriptions, l2_descriptions

    def build_matrix(self, threshold: float = 0.25) -> np.ndarray:
        """
        构建突触权重矩阵。
        
        Args:
            threshold: 相似度阈值，低于此值的突触权归零，实现稀疏化。
        """
        print("[AutoTopology] 正在构建突触连结矩阵...")
        l1_desc, l2_desc = self.generate_descriptions()
        
        print(f"[AutoTopology] 提取 Layer 1 感知节点 Embeddings ({len(l1_desc)} 个)...")
        l1_embeddings = self.get_embeddings_batch(l1_desc)
        
        print(f"[AutoTopology] 提取 Layer 2 冲动节点 Embeddings ({len(l2_desc)} 个)...")
        l2_embeddings = self.get_embeddings_batch(l2_desc)
        
        matrix = np.zeros((TOTAL_LAYER1_NODES, TOTAL_LAYER2_NODES), dtype=np.float64)
        print("[AutoTopology] 计算余弦相似度并织网...")
        for i in range(TOTAL_LAYER1_NODES):
            for j in range(TOTAL_LAYER2_NODES):
                sim = cosine_similarity(l1_embeddings[i], l2_embeddings[j])
                # 只保留正相关，且大于阈值的连接 (稀疏化)
                if sim > threshold:
                    # 指数放大差异，让强连接更强
                    matrix[i, j] = (sim - threshold) ** 0.5
                else:
                    matrix[i, j] = 0.0
                    
        # 归一化：为了适配 LIF 模型，将总权重限制在合理范围
        matrix = matrix / (np.max(matrix) + 1e-8) * 2.0  # 最大突触权重为 2.0
        
        print(f"[AutoTopology] 矩阵构建完成！稀疏度 (非零元素): {np.sum(matrix > 0)} / {matrix.size}")
        return matrix

    def save_matrix(self, matrix: np.ndarray, path: str = SYNAPSE_MATRIX_PATH):
        np.save(path, matrix)
        print(f"[AutoTopology] 突触矩阵已保存至 {path}")

if __name__ == "__main__":
    builder = AutoTopologyBuilder()
    matrix = builder.build_matrix()
    builder.save_matrix(matrix)
