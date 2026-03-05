#!/usr/bin/env python3
"""
Haplo Donor Selector - Disease-Free Survival (DFS) Calculator
==============================================================
基于 Fuchs E, McCurdy S, et al., Blood 2022; 139(10):1452-1468
Table 3: Multivariate Cox proportional hazards model for DFS

本地实现，无需访问 haplodonorselector.b12x.org

用法：
  python3 haplo_dfs.py --json '{...}'
  或在 hla_matching.py 工作流中自动调用

作者：花卷儿 🥟 for 季老大
"""

import argparse
import json
import math
import sys

# ============================================================
# Cox Model Coefficients (ln(HR)) from Table 3
# Reference groups have coefficient = 0
# ============================================================

# HLA-B Leader Match Status (global P = .01)
B_LEADER_COEFF = {
    "matched": 0.0,           # HR = 1.0 (reference)
    "mismatched": 0.1823,     # HR = 1.20 → ln(1.20) = 0.1823
}

# HLA-DRB1/DQB1 Match Status (global P = .003)
# Format: "DRB1_status/DQB1_status"
DRB1_DQB1_COEFF = {
    "mismatch/mismatch": 0.0,      # HR = 1.0 (reference)
    "mismatch/match": -0.2231,     # HR = 0.80 → ln(0.80)
    "match/mismatch": 0.2624,      # HR = 1.30 → ln(1.30)
    "match/match": 0.2776,         # HR = 1.32 → ln(1.32)
    "missing": 0.0,                # default to reference if unknown
}

# HLA-DPB1 TCE Status (global P = .04)
DPB1_TCE_COEFF = {
    "matched_or_permissive": 0.0,     # HR = 1.0 (reference: no nonpermissive GVH mismatch)
    "nonpermissive": -0.3285,          # HR = 0.72 → ln(0.72)
    "missing": -0.0305,               # HR = 0.97 → ln(0.97)
}

# Patient/Donor CMV Serostatus (global P = .005)
CMV_COEFF = {
    "pos/pos": 0.0,           # HR = 1.0 (reference)
    "pos/neg": 0.0,           # HR = 1.00
    "neg/pos": 0.0953,        # HR = 1.10 → ln(1.10)
    "neg/neg": -0.2357,       # HR = 0.79 → ln(0.79)
    "missing": 0.2624,        # HR = 1.30 → ln(1.30)
}

# Patient HCT Comorbidity Index (global P < .0001)
HCTCI_COEFF = {
    0: 0.0,       # HR = 1.0 (reference)
    1: 0.1906,    # HR = 1.21 → ln(1.21)
    2: 0.2151,    # HR = 1.24 → ln(1.24)
    3: 0.4318,    # HR = 1.54 → ln(1.54)  (≥3)
}

# Patient Age in years (global P = .0001)
AGE_COEFF = {
    "0-18": 0.0,       # HR = 1.0 (reference)
    "19-29": 0.0296,   # HR = 1.03 → ln(1.03)
    "30-39": -0.0101,  # HR = 0.99 → ln(0.99)
    "40-49": -0.1054,  # HR = 0.90 → ln(0.90)
    "50-59": 0.0677,   # HR = 1.07 → ln(1.07)
    ">=60": 0.3436,    # HR = 1.41 → ln(1.41)
}

# Disease type/stage coefficients (from Table 2 mortality model, used for stratification)
# Note: In the original model, disease/stage is used for stratification, not as a covariate
# The web tool includes it as an input, so we include approximate effects
DISEASE_STAGE_COEFF = {
    "AML/CR1": 0.0,
    "AML/CR2_CR3": 0.0953,    # HR ≈ 1.10
    "AML/Advanced": 0.7419,    # HR = 2.10
    "ALL/CR1": -0.5798,        # HR = 0.56
    "ALL/CR2": 0.4637,         # HR = 1.59
    "ALL/CR3+": 0.9203,        # HR = 2.51
    "MDS/Early": 0.1989,       # HR = 1.22
    "MDS/Advanced": 0.2852,    # HR = 1.33
}


def get_age_group(age: int) -> str:
    """将年龄转换为分组"""
    if age <= 18:
        return "0-18"
    elif age <= 29:
        return "19-29"
    elif age <= 39:
        return "30-39"
    elif age <= 49:
        return "40-49"
    elif age <= 59:
        return "50-59"
    else:
        return ">=60"


def get_hctci_group(score: int) -> int:
    """将 HCT-CI 评分转换为分组"""
    if score >= 3:
        return 3
    return score


def calculate_linear_predictor(params: dict) -> float:
    """
    计算 Cox 模型的线性预测值 (Xβ)
    
    params:
        b_leader: "matched" or "mismatched"
        drb1_dqb1: "mismatch/mismatch", "mismatch/match", "match/mismatch", "match/match"
        dpb1_tce: "matched_or_permissive", "nonpermissive", "missing"
        cmv: "pos/pos", "pos/neg", "neg/pos", "neg/neg", "missing"
        hctci: 0, 1, 2, or >=3
        age: patient age in years
        disease_stage: e.g., "AML/CR1"
    """
    xb = 0.0
    
    xb += B_LEADER_COEFF.get(params.get("b_leader", "matched"), 0.0)
    xb += DRB1_DQB1_COEFF.get(params.get("drb1_dqb1", "mismatch/mismatch"), 0.0)
    xb += DPB1_TCE_COEFF.get(params.get("dpb1_tce", "missing"), 0.0)
    xb += CMV_COEFF.get(params.get("cmv", "missing"), 0.0)
    
    hctci = get_hctci_group(params.get("hctci", 0))
    xb += HCTCI_COEFF.get(hctci, 0.0)
    
    age = params.get("age", 50)
    age_group = get_age_group(age)
    xb += AGE_COEFF.get(age_group, 0.0)
    
    xb += DISEASE_STAGE_COEFF.get(params.get("disease_stage", "AML/CR1"), 0.0)
    
    return xb


def estimate_dfs_probability(xb: float, time_years: float = 3.0) -> float:
    """
    估算 DFS 概率
    使用 S(t) = S0(t)^exp(Xβ)
    
    基于论文报告的 3年 DFS = 41.3% 作为基线（平均风险群体）
    S0(3) 为基线生存函数
    """
    # 论文报告的 3年 DFS 为 41.3%，这是整体人群的
    # 对于 Cox 模型，平均 Xβ ≈ 0 时的基线
    # 我们使用 S0(3) ≈ 0.413 作为近似基线生存率
    S0_3yr = 0.413
    
    # S(t) = S0(t)^exp(Xβ)
    dfs = S0_3yr ** math.exp(xb)
    
    return dfs


def determine_matching_status(patient_hla: dict, donor_hla: dict) -> dict:
    """
    根据患者和供者的 HLA 分型自动判断匹配状态
    """
    result = {}
    
    # DRB1 匹配判断
    pat_drb1 = set(patient_hla.get("DRB1", []))
    don_drb1 = set(donor_hla.get("DRB1", []))
    drb1_matched = bool(pat_drb1 & don_drb1) if pat_drb1 and don_drb1 else None
    
    # DQB1 匹配判断
    pat_dqb1 = set(patient_hla.get("DQB1", []))
    don_dqb1 = set(donor_hla.get("DQB1", []))
    dqb1_matched = bool(pat_dqb1 & don_dqb1) if pat_dqb1 and don_dqb1 else None
    
    # 组合 DRB1/DQB1 状态
    if drb1_matched is not None and dqb1_matched is not None:
        drb1_str = "match" if drb1_matched else "mismatch"
        dqb1_str = "match" if dqb1_matched else "mismatch"
        result["drb1_dqb1"] = f"{drb1_str}/{dqb1_str}"
    else:
        result["drb1_dqb1"] = "missing"
    
    return result


def format_dfs_report(patient_info: dict, donors_results: list) -> str:
    """格式化 DFS 报告"""
    lines = [
        "📊 Haplo Donor DFS Predictor Report",
        "=" * 50,
        f"📖 Based on: Fuchs et al., Blood 2022;139:1452-1468",
        f"   TCE-Core修正: Solomon et al., TCT 2024;30:608",
        f"   (n=1434, CIBMTR, Haplo+PTCy)",
        "",
        f"👤 患者信息:",
        f"   疾病: {patient_info.get('disease_stage', 'N/A')}",
        f"   年龄: {patient_info.get('age', 'N/A')} 岁 (分组: {get_age_group(patient_info.get('age', 50))})",
        f"   HCT-CI: {patient_info.get('hctci', 'N/A')}",
        f"   CMV: {patient_info.get('pat_cmv', 'N/A')}",
    ]
    
    # Sort donors by DFS (best first) — KIR does NOT affect ranking
    donors_results.sort(key=lambda x: x["dfs_3yr"], reverse=True)
    
    lines.append("")
    lines.append("🏆 供者排名 (按 3年 DFS 降序):")
    lines.append("   ⚠️ 排序依据: B-Leader + DRB1/DQB1 + DPB1 TCE-Core")
    lines.append("   ⚠️ KIR 信息仅供参考，不参与排序")
    lines.append("-" * 50)
    
    for rank, d in enumerate(donors_results, 1):
        medal = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else f"#{rank}"
        dfs_pct = d["dfs_3yr"] * 100
        
        lines.append(f"\n{medal} {d['donor_id']}")
        lines.append(f"   B-Leader: {d['b_leader']}")
        lines.append(f"   DRB1/DQB1: {d['drb1_dqb1']}")
        lines.append(f"   DPB1 TCE-Core: {d['dpb1_tce']}")
        lines.append(f"   CMV: {d['cmv']}")
        lines.append(f"   ──────────────────────")
        lines.append(f"   📈 预测 3年 DFS: {dfs_pct:.1f}%")
        lines.append(f"   📈 相对风险 (HR): {math.exp(d['xb']):.2f}")
        
        # KIR section — informational only
        kir = d.get("kir", {})
        if kir:
            lines.append(f"   ──────────────────────")
            lines.append(f"   🔬 KIR Ligand 信息 (仅供参考):")
            
            # Donor B/C KIR ligands
            don_b_kir = kir.get("donor_b_kir", [])
            don_c_kir = kir.get("donor_c_kir", [])
            if don_b_kir:
                lines.append(f"      供者 B: {', '.join(don_b_kir)}")
            if don_c_kir:
                lines.append(f"      供者 C: {', '.join(don_c_kir)}")
            
            # GvH / HvG
            gvh = kir.get("gvh", "N/A")
            hvg = kir.get("hvg", "N/A")
            gvh_emoji = "✅" if gvh == "matched" else "⚠️"
            hvg_emoji = "✅" if hvg == "matched" else "⚠️"
            lines.append(f"      GvH: {gvh_emoji} {gvh}")
            lines.append(f"      HvG: {hvg_emoji} {hvg}")
            
            # C1 directionality (Nikoloudis 2025)
            c1_status = kir.get("c1_direction", "")
            if c1_status:
                c1_emoji = "⚠️" if "inferior" in c1_status.lower() else "✅"
                lines.append(f"      C1方向: {c1_emoji} {c1_status}")
            
            # Missing ligand (Solomon 2022)
            ml = kir.get("missing_ligand", "")
            if ml:
                lines.append(f"      Missing Ligand: {ml}")
    
    # ============================================================
    # Section: Haplo vs MSD / MMUD Comparison
    # Based on Mehta et al., Blood Adv 2024 & TCT 2024
    # ============================================================
    lines.append("")
    lines.append("=" * 50)
    lines.append("")
    lines.append("🔄 优选供者 vs MSD/MUD/MMUD 比较分析")
    lines.append("   Based on: Mehta et al., Blood Adv 2024 & TCT 2024")
    lines.append("-" * 50)
    
    HAPLO_GROUPS = {
        "BL-M/DRB1-MM":  {"os": 56.1, "nrm": 16.9, "rel": 37.2, "pfs": 45.7,
                           "os_hr": 0.72, "os_p": ".0002"},
        "BL-M/DRB1-M":   {"os": 50.7, "nrm": 18.4, "rel": 49.1, "pfs": 32.2,
                           "os_hr": 0.80, "os_p": ".09"},
        "BL-MM/DRB1-MM": {"os": 48.4, "nrm": 23.7, "rel": 37.4, "pfs": 38.6,
                           "os_hr": 0.91, "os_p": ".33"},
        "BL-MM/DRB1-M":  {"os": 45.7, "nrm": 19.4, "rel": 50.9, "pfs": 29.5,
                           "os_hr": 0.95, "os_p": ".77"},
    }
    # Reference groups (Mehta Blood Adv 2024 & TCT 2024)
    REF_GROUPS = [
        {"label": "年轻MSD+PTCy (<50岁)",
         "os": "57.2*", "nrm": "19.9*", "rel": "38.5*", "pfs": "─",
         "os_hr_note": "HR 0.94 (P=.54) 🟰",
         "emoji": "🟢", "note": "与Haplo总体相当"},
        {"label": "老MSD+PTCy (≥50岁)",
         "os": "45.1*", "nrm": "23.7*", "rel": "44.7*", "pfs": "─",
         "os_hr_note": "年轻BL-M Haplo HR 0.65 (P=.009)",
         "emoji": "🟡", "note": "年轻BL-M Haplo显著更优"},
        {"label": "MMUD PBM-matched (CNI)",
         "os": "45.5", "nrm": "29.5", "rel": "29.3", "pfs": "41.1",
         "os_hr_note": "Ref (参照组)",
         "emoji": "🔵", "note": ""},
        {"label": "MMUD PBM-mismatched (CNI)",
         "os": "38.9", "nrm": "32.0", "rel": "32.1", "pfs": "35.7",
         "os_hr_note": "HR 1.21 (P=.005)",
         "emoji": "🟠", "note": "最差选项"},
    ]
    
    if donors_results:
        best = donors_results[0]
        bl = best.get("b_leader", "?")
        drb1_dqb1 = best.get("drb1_dqb1", "?")
        drb1_s = drb1_dqb1.split("/")[0] if "/" in drb1_dqb1 else "mismatch"
        
        if bl == "matched" and drb1_s == "mismatch":
            gk = "BL-M/DRB1-MM"
        elif bl == "matched":
            gk = "BL-M/DRB1-M"
        elif drb1_s == "mismatch":
            gk = "BL-MM/DRB1-MM"
        else:
            gk = "BL-MM/DRB1-M"
        
        h = HAPLO_GROUPS[gk]
        donor_age = best.get("donor_age")
        
        lines.append(f"")
        lines.append(f"   🏆 优选供者: {best['donor_id']}")
        lines.append(f"   📋 Haplo 分组: {gk}")
        if donor_age is not None:
            atag = "✅ <35" if donor_age < 35 else "35-45" if donor_age < 45 else "⚠️ ≥45"
            lines.append(f"   🎂 供者年龄: {donor_age} 岁 ({atag})")
        
        lines.append("")
        lines.append(f"   供者类型                            OS     NRM    复发   PFS")
        lines.append(f"   ──────────────────────────────── ─────  ─────  ─────  ─────")
        lines.append(f"   ⭐ 优选Haplo ({gk}){' '*(18-len(gk))} {h['os']:5.1f}% {h['nrm']:5.1f}% {h['rel']:5.1f}% {h['pfs']:5.1f}%")
        lines.append(f"   🟢 年轻MSD+PTCy (<50岁)          57.2%* 19.9%* 38.5%*  ─")
        lines.append(f"   🟡 老MSD+PTCy (≥50岁)            45.1%* 23.7%* 44.7%*  ─")
        lines.append(f"   🔵 MMUD PBM-matched (CNI)        45.5% 29.5% 29.3% 41.1%")
        lines.append(f"   🟠 MMUD PBM-mismatched (CNI)     38.9% 32.0% 32.1% 35.7%")
        lines.append(f"   (* MSD为2年估计值; 其余为3年; Mehta 2024)")
        
        # HR comparison section
        lines.append("")
        lines.append(f"   📊 OS 比较 (优选Haplo vs 各参照组):")
        lines.append(f"      vs 年轻MSD+PTCy:            HR 0.94 (P=.54) → 🟰 总体相当")
        if h['os_hr'] < 0.85:
            lines.append(f"      vs PBM-matched MMUD:        HR {h['os_hr']:.2f} (P={h['os_p']}) → ⭐ 显著更优")
        elif h['os_hr'] < 1.0:
            lines.append(f"      vs PBM-matched MMUD:        HR {h['os_hr']:.2f} (P={h['os_p']}) → ✅ 趋势更优")
        else:
            lines.append(f"      vs PBM-matched MMUD:        HR {h['os_hr']:.2f} (P={h['os_p']}) → 🟰 相当")
        lines.append(f"      vs PBM-mismatched MMUD:     HR ~{h['os_hr']/1.21:.2f} → ⭐ 显著更优")
        
        # Patient ≥50: young haplo vs old MSD
        pat_age = patient_info.get("age", 0)
        if pat_age >= 50:
            lines.append(f"")
            lines.append(f"   📌 患者≥50岁 年龄分层 (Mehta 2024):")
            if donor_age is not None and donor_age < 35 and bl == "matched":
                lines.append(f"      vs 老MSD(≥50): HR 0.65 (P=.009) → ⭐ 显著更优")
                lines.append(f"      vs 老MSD复发: HR 0.63 (P=.004) → ⭐ 显著降低复发")
            elif donor_age is not None and donor_age < 35:
                lines.append(f"      vs 老MSD(≥50): HR 0.76 (P=.06) → ✅ 趋势更优")
            else:
                lines.append(f"      供者≥35岁，年轻Haplo优势可能减弱")
        else:
            lines.append(f"")
            lines.append(f"   📌 患者<50岁，年龄分层数据有限")
            lines.append(f"      总体Haplo vs MSD: 无显著差异 (HR 0.94)")
        
        # Donor age impact
        if donor_age is not None:
            lines.append(f"")
            lines.append(f"   🎂 供者年龄效应:")
            lines.append(f"      每+1岁 → 死亡率+1% (HR 1.01/年)")
            if gk == "BL-M/DRB1-MM":
                if donor_age <= 45:
                    lines.append(f"      ✅ ≤45岁 BL-M/DRB1-MM → 优于30岁 PBM-matched MMUD")
                else:
                    lines.append(f"      ⚠️ >45岁 → vs年轻MMUD优势可能消失")
            if bl != "matched" and donor_age >= 55:
                lines.append(f"      ⚠️ BL-mismatch + ≥55岁 → 可能劣于30岁 PBM-matched MMUD")
        
        lines.append("")
        lines.append(f"   🛡️ GVHD 优势 (Haplo+PTCy vs MMUD+CNI):")
        lines.append(f"      aGVHD II-IV: MMUD 1.5-1.8x | cGVHD: MMUD 1.8-2.0x")
        lines.append(f"      → PTCy 大幅降低 GVHD 和 NRM")
        
        # ============================================================
        # 如有其他供者类型的选择推荐
        # ============================================================
        lines.append("")
        lines.append(f"   🧭 如有其他供者类型，应如何选择？")
        lines.append(f"   ─────────────────────────────────")
        
        # Determine haplo strength tier
        da = donor_age if donor_age is not None else 40
        is_young_haplo = da < 35
        is_mid_haplo = 35 <= da <= 45
        is_old_haplo = da > 45
        is_blm = (gk == "BL-M/DRB1-MM")
        is_drb1_mm = "mismatch" in drb1_s
        
        # vs 年轻 MSD (<50y)
        lines.append(f"")
        lines.append(f"   🟢 如有年轻MSD (<50岁)?")
        if is_blm and is_young_haplo:
            lines.append(f"      → 两者相当 (HR 0.94, P=.54)，均可选择")
            lines.append(f"      → 本Haplo年轻+BL-M，复发可能更低 (HR 0.87)")
            lines.append(f"      📌 推荐: 优选Haplo ≈ 年轻MSD，均为最优方案")
        elif is_blm:
            lines.append(f"      → Haplo与MSD总体相当 (HR 0.94)")
            if is_old_haplo:
                lines.append(f"      → 但本Haplo供者年龄偏大({da}岁)，年轻MSD可能更优")
                lines.append(f"      📌 推荐: 优先选年轻MSD ✅")
            else:
                lines.append(f"      📌 推荐: 两者相当，均可选择")
        else:
            lines.append(f"      → 本Haplo B-leader mismatched，DFS较低")
            lines.append(f"      📌 推荐: 优先选年轻MSD ✅")
        
        # vs 老 MSD (≥50y)
        lines.append(f"")
        lines.append(f"   🟡 如有老MSD (≥50岁)?")
        if pat_age >= 50:
            if is_blm and is_young_haplo:
                lines.append(f"      → 年轻BL-M Haplo 显著优于老MSD (OS HR 0.65, P=.009)")
                lines.append(f"      → 复发也显著更低 (HR 0.63, P=.004)")
                lines.append(f"      📌 推荐: 选本Haplo，不选老MSD ⭐")
            elif is_blm and is_mid_haplo:
                lines.append(f"      → BL-M Haplo vs 老MSD大致相当")
                lines.append(f"      → 年龄优势有限但BL-M提供NRM保护")
                lines.append(f"      📌 推荐: 优选Haplo ≈ 老MSD，略倾向Haplo")
            elif is_blm:
                lines.append(f"      → BL-M但供者年龄也偏大({da}岁)")
                lines.append(f"      → 年龄优势消失，两者相当")
                lines.append(f"      📌 推荐: 两者相当，结合其他因素决定")
            else:
                if is_young_haplo:
                    lines.append(f"      → 年轻Haplo但BL-mismatched vs 老MSD")
                    lines.append(f"      → HR 0.76 (P=.06)，趋势优于老MSD")
                    lines.append(f"      📌 推荐: 略倾向Haplo (年龄优势)")
                else:
                    lines.append(f"      → BL-mismatched + 供者偏大({da}岁)")
                    lines.append(f"      📌 推荐: 两者均非最优，结合其他因素决定")
        else:
            lines.append(f"      → 患者<50岁，总体Haplo vs MSD无差异 (HR 0.94)")
            if is_blm:
                lines.append(f"      📌 推荐: 优选Haplo BL-M ≈ MSD")
            else:
                lines.append(f"      📌 推荐: MSD略优于BL-mismatched Haplo")
        
        # vs MMUD
        lines.append(f"")
        lines.append(f"   🔵 如有MMUD (10/10 matched unrelated)?")
        if is_blm:
            if is_old_haplo:
                lines.append(f"      → BL-M/DRB1-MM Haplo总体OS HR 0.72 vs MMUD")
                lines.append(f"      → 但供者>45岁，Mehta探索性分析显示优势可能消失")
                lines.append(f"      → GVHD: Haplo+PTCy仍远低于MMUD+CNI")
                lines.append(f"      📌 推荐: 如MMUD年轻(<30岁)+PBM-matched → 可考虑MMUD")
                lines.append(f"             如MMUD也偏大或PBM-mismatched → 仍选Haplo")
            else:
                lines.append(f"      → BL-M/DRB1-MM Haplo 显著优于 MMUD (OS HR 0.72)")
                lines.append(f"      → NRM: Haplo 16.9% vs MMUD 29.5%")
                lines.append(f"      → GVHD风险: MMUD 约为Haplo的1.5-2倍")
                lines.append(f"      📌 推荐: 选Haplo，不选MMUD ⭐")
        elif is_drb1_mm:
            if is_young_haplo:
                lines.append(f"      → BL-mismatched但年轻Haplo，NRM仍低于MMUD")
                lines.append(f"      → GVHD保护明显")
                lines.append(f"      📌 推荐: 略倾向Haplo (NRM和GVHD优势)")
            elif da >= 55:
                lines.append(f"      → BL-mismatched + 供者≥55岁")
                lines.append(f"      → 死亡率可能高于年轻PBM-matched MMUD")
                lines.append(f"      📌 推荐: 如有年轻PBM-matched MMUD → 选MMUD ⚠️")
            else:
                lines.append(f"      → BL-mismatched Haplo vs MMUD 大致相当 (HR 0.91)")
                lines.append(f"      → GVHD/NRM仍有优势")
                lines.append(f"      📌 推荐: 略倾向Haplo，结合PBM状态综合判断")
        else:
            lines.append(f"      → DRB1 matched Haplo复发率高 (HR 1.56-1.86 vs MMUD)")
            lines.append(f"      → 虽然NRM/GVHD较低，但复发抵消了优势")
            lines.append(f"      📌 推荐: 优先选PBM-matched MMUD ⚠️")
        
        # Final summary
        lines.append("")
        lines.append(f"   💡 本例综合结论:")
        if is_blm and is_young_haplo:
            lines.append(f"      本Haplo (BL-M/DRB1-MM + <35岁) = 所有供者类型中最优")
            lines.append(f"      优于老MSD ⭐ | 相当于年轻MSD 🟰 | 优于MMUD ⭐")
        elif is_blm and is_mid_haplo:
            lines.append(f"      本Haplo (BL-M/DRB1-MM) = 优质选择")
            lines.append(f"      如有年轻MSD可考虑 | 优于MMUD ⭐ | 优于老MSD ✅")
        elif is_blm and is_old_haplo:
            lines.append(f"      本Haplo (BL-M/DRB1-MM) = HLA维度最优，但供者年龄偏大")
            lines.append(f"      如有年轻MSD → 优先MSD | vs MMUD需看MMUD年龄和PBM")
            lines.append(f"      如无更优选择 → 仍为可接受方案")
        elif is_drb1_mm and is_young_haplo:
            lines.append(f"      本Haplo年轻但BL-mismatched")
            lines.append(f"      如有年轻MSD → 优先MSD | 优于MMUD (NRM/GVHD优势)")
        elif is_drb1_mm:
            lines.append(f"      本Haplo BL-mismatched，年龄{da}岁")
            lines.append(f"      如有MSD → 优先MSD | vs MMUD大致相当")
        else:
            lines.append(f"      ⚠️ 本Haplo DRB1 matched → 复发风险高")
            lines.append(f"      如有MSD或PBM-matched MMUD → 应优先考虑")
    
    lines.append("")
    lines.append("=" * 50)
    lines.append("⚠️ 仅供研究参考，不作为临床决策的唯一依据")
    lines.append("   实际供者选择需综合考虑 ABO、CMV、年龄、性别等因素")
    lines.append("")
    lines.append("📖 参考文献:")
    lines.append("   [1] Fuchs et al., Blood 2022;139:1452-1468")
    lines.append("   [2] Solomon et al., TCT 2024;30:608.e1-e10 (TCE-Core)")
    lines.append("   [3] Solomon et al., TCT 2022;28:601.e1-e8 (KIR/B-leader)")
    lines.append("   [4] Nikoloudis et al., Cytotherapy 2025;27:457-464 (C1方向)")
    lines.append("   [5] Zou et al., Front Immunol 2022;13:1033871 (CF-iKIR)")
    lines.append("   [6] Mehta et al., Blood Adv 2024;8:5306-5314 (vs MSD)")
    lines.append("   [7] Mehta et al., TCT 2024;30:909.e1-e11 (vs MMUD)")
    
    return "\n".join(lines)


def run_dfs_analysis(json_input: dict) -> str:
    """
    运行 DFS 分析
    
    json_input 格式:
    {
        "patient": {
            "age": 40,
            "disease": "MDS",
            "disease_stage": "MDS/Early",  
            "hctci": 2,
            "cmv": "Positive"
        },
        "donors": [
            {
                "id": "D1",
                "b_leader": "matched",
                "drb1_dqb1": "mismatch/match",
                "dpb1_tce": "matched_or_permissive",
                "cmv": "Positive"
            }
        ]
    }
    """
    patient = json_input["patient"]
    age = patient.get("age", 50)
    disease_stage = patient.get("disease_stage", "AML/CR1")
    hctci = patient.get("hctci", 0)
    pat_cmv = patient.get("cmv", "Missing").lower()
    
    patient_info = {
        "age": age,
        "disease_stage": disease_stage,
        "hctci": hctci,
        "pat_cmv": patient.get("cmv", "Missing"),
    }
    
    donors_results = []
    
    for donor in json_input["donors"]:
        don_cmv = donor.get("cmv", "Missing").lower()
        
        # Determine CMV combination
        cmv_map = {
            ("positive", "positive"): "pos/pos",
            ("positive", "negative"): "pos/neg",
            ("negative", "positive"): "neg/pos",
            ("negative", "negative"): "neg/neg",
        }
        cmv_key = cmv_map.get((pat_cmv, don_cmv), "missing")
        
        params = {
            "b_leader": donor.get("b_leader", "matched"),
            "drb1_dqb1": donor.get("drb1_dqb1", "mismatch/mismatch"),
            "dpb1_tce": donor.get("dpb1_tce", "missing"),
            "cmv": cmv_key,
            "hctci": hctci,
            "age": age,
            "disease_stage": disease_stage,
        }
        
        xb = calculate_linear_predictor(params)
        dfs_3yr = estimate_dfs_probability(xb, 3.0)
        
        donors_results.append({
            "donor_id": donor.get("id", "Unknown"),
            "b_leader": donor.get("b_leader", "?"),
            "drb1_dqb1": donor.get("drb1_dqb1", "?"),
            "dpb1_tce": donor.get("dpb1_tce", "?"),
            "cmv": cmv_key,
            "xb": xb,
            "dfs_3yr": dfs_3yr,
            "hr": math.exp(xb),
            "kir": donor.get("kir", {}),
            "donor_age": donor.get("donor_age"),
        })
    
    return format_dfs_report(patient_info, donors_results)


def main():
    parser = argparse.ArgumentParser(description="Haplo Donor DFS Calculator (Fuchs et al. 2022)")
    parser.add_argument("--json", help="JSON input with patient and donor data")
    args = parser.parse_args()
    
    if args.json:
        data = json.loads(args.json)
        print(run_dfs_analysis(data))
    else:
        # Demo
        demo = {
            "patient": {
                "age": 40,
                "disease_stage": "MDS/Early",
                "hctci": 0,
                "cmv": "Positive"
            },
            "donors": [
                {"id": "D1-Demo", "b_leader": "matched", "drb1_dqb1": "mismatch/match",
                 "dpb1_tce": "matched_or_permissive", "cmv": "Positive"},
                {"id": "D2-Demo", "b_leader": "mismatched", "drb1_dqb1": "mismatch/mismatch",
                 "dpb1_tce": "nonpermissive", "cmv": "Negative"},
            ]
        }
        print(run_dfs_analysis(demo))


if __name__ == "__main__":
    main()
