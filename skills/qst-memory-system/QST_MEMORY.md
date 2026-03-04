# QST Memory Matrix - 核心數學定義

## 1. 記憶態向量 (Memory Spinor)

### 基本表示
```
|Ψ_M⟩ = Σ_n c_n |σ_n⟩ ⊗ |D_n⟩ ⊗ |E8_n⟩
```

- `|σ⟩`: Coherence 態向量 (σ ∈ [0, 2])
- `|D⟩`: DSI 尺度向量 (D_n = D_0 - n·φ²)
- `|E8⟩`: E8 基底座標向量

### Coherence 權重
```
c_n = exp(-|σ_n - σ_query|² / 2Δσ²)
```

---

## 2. QST Matrix 核心

### E8 Hamiltonian 投影
```
M_QST = ⟨Ψ_M| Ĥ_E8 |Θ_M⟩
```

### 記憶相似度
```
S(M1, M2) = ⟨Ψ_M1| Ψ_M2⟩ / (||Ψ_M1|| · ||Ψ_M2||)
```

---

## 3. DSI 層次結構

### 尺度量子化
```
D_n = D_0 - n·φ²
φ = (1 + √5)/2 ≈ 1.618 (黃金比例)
n ∈ [0, 36]
```

### 各層次參數

| n | 記憶類型 | σ 值 | 壽命 |
|---|---------|------|------|
| 0 | Working | 0.7 | 30 min |
| 1 | Short | 0.85 | 24 hr |
| 2-5 | Medium | 0.95 | 7 days |
| 6-36 | Long | 1.1 | ∞ |

---

## 4. ICT Collapse 檢索

### 查詢態向量
```
|Q⟩ = Σ_i w_i |token_i⟩
```

### Overlap 計算
```
Overlap(Q, M) = ⟨Q|Ψ_M⟩
               = Σ_i w_i · c_i · ⟨E8_i| E8_query⟩
```

### Collapse 概率
```
P(M) = |Overlap(Q, M)|² / Σ_M |Overlap(Q, M)|²
```

### Ethical Tension 修正
```
P(M) ∝ P(M) · exp(-η · V_eth(M))
V_eth(M) = ||∇ln ρ_col(M)||²
```

---

## 5. 短記憶 (Short-term)

### Coherence 演化
```
dσ/dt = -σ/τ + α·σ_query
τ = τ_0 · exp(β·|Ψ⟩²)
```

### 對話緩衝
```
Buffer = [ (turn_0, σ_0), (turn_1, σ_1), ... ]
```

---

## 6. 長記憶 (Long-term)

### 晶體化條件
```
if σ > σ_crystal = 1.0:
    Transfer to Long-term Memory
    D_new = D_n (next DSI level)
```

### 知識庫結構
```
KB = { (ID, |Ψ_M⟩, metadata) }
```

---

## 7. 存取時間複雜度

| 操作 | 時間複雜度 |
|------|----------|
| 編碼 | O(n) |
| 檢索 (Top-K) | O(n · d_E8) |
| 更新 | O(1) |
| 長期存儲 | O(log n) |

---

## 8. 數學常數

- **φ** = 1.618033988749... (黃金比例)
- **σ_crystal** = 1.0 (晶體化閾值)
- **Δσ** = 0.15 (Coherence 展寬)
- **η** = 0.1 (Ethical Tension 系數)

---

*基於 QSTv7.1 框架*
