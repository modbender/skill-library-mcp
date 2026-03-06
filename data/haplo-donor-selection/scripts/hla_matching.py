#!/usr/bin/env python3
"""
HLA Matching Workflow - IPD-IMGT/HLA Database API
==================================================
支持三个匹配工具：
  1. HLA-B Leader Mismatch（B leader -21位 M/T 多态性，预测 GVHD 风险）
  2. HLA-DPB1 TCE（T-Cell Epitope 分组，预测排斥方向）
  3. KIR Ligand Calculator（NK 细胞 KIR 配体匹配）

用法：
  python3 hla_matching.py --mode b_leader --patb1 15:02 --patb2 07:02 --donb1 15:02 --donb2 35:01
  python3 hla_matching.py --mode dpb1 --patdpb1 01:01 --patdpb2 02:01 --dondpb1 03:01 --dondpb2 04:01 [--tce-version 2|2.1|3]
  python3 hla_matching.py --mode kir --patb1 15:01 --patb2 07:02 --patc1 02:02 --patc2 01:02 --donb1 07:02 --donb2 15:01 --donc1 01:02 --donc2 02:02
  python3 hla_matching.py --mode all --patb1 ... (同时运行所有可用的匹配)
  python3 hla_matching.py --json '{"patient":{"B":["15:02","07:02"],"C":["02:02","01:02"],"DPB1":["01:01","02:01"]},"donors":[{"id":"D1","B":["15:02","35:01"],"C":["01:02","02:02"],"DPB1":["03:01","04:01"]}]}'

作者：花卷儿 🥟 for 季老大
"""

import argparse
import json
import sys
import urllib.request
import urllib.parse
import urllib.error

# ============================================================
# API Endpoints
# ============================================================
BASE = "https://www.ebi.ac.uk/cgi-bin/ipd/matching"

ENDPOINTS = {
    "b_leader": f"{BASE}/b_leader",
    "dpb1_v2": f"{BASE}/dpb1_tce_v2",
    "dpb1_v21": f"{BASE}/dpb1_tce_v21",
    "dpb1_v3": f"{BASE}/dpb1_tce_v3",
    "kir": f"{BASE}/kir_ligand",
}


def api_call(url: str, params: dict) -> dict:
    """调用 IPD-IMGT/HLA API 并返回 JSON"""
    query = urllib.parse.urlencode(params, doseq=True)
    full_url = f"{url}?{query}"
    req = urllib.request.Request(full_url, headers={"Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = resp.read().decode("utf-8")
            return json.loads(data)
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        return {"error": f"HTTP {e.code}", "detail": body, "url": full_url}
    except Exception as e:
        return {"error": str(e), "url": full_url}


# ============================================================
# B-Leader Matching
# ============================================================
def query_b_leader(pat_b1: str, pat_b2: str, donors: list[dict]) -> dict:
    """
    查询 HLA-B Leader 匹配
    donors: [{"id": "D1", "b1": "15:02", "b2": "35:01"}, ...]
    """
    params = {"pid": "Patient", "patb1": pat_b1, "patb2": pat_b2}
    for d in donors:
        params_list = list(params.items())
        params_list.append(("did", d["id"]))
        params_list.append(("donb1", d["b1"]))
        params_list.append(("donb2", d["b2"]))
        params = dict(params_list)
    # 因为多供者需要重复 key，用手动拼接
    parts = [f"pid=Patient", f"patb1={pat_b1}", f"patb2={pat_b2}"]
    for d in donors:
        parts.extend([f"did={d['id']}", f"donb1={d['b1']}", f"donb2={d['b2']}"])
    full_url = f"{ENDPOINTS['b_leader']}?{'&'.join(parts)}"
    req = urllib.request.Request(full_url, headers={"Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return {"error": f"HTTP {e.code}", "detail": e.read().decode("utf-8", errors="replace")}
    except Exception as e:
        return {"error": str(e)}


def format_b_leader(result: dict) -> str:
    """格式化 B-Leader 结果"""
    if "error" in result:
        return f"❌ B-Leader 查询失败: {result['error']}\n{result.get('detail', '')}"

    lines = ["🧬 HLA-B Leader Matching Report", "=" * 40]
    data = result.get("HLA-B_leader", result)
    patient = data.get("patient", {})
    pid = patient.get("patientid", "?")
    lines.append(f"\n👤 患者 (ID: {pid})")

    pat_leaders = []
    for allele_info in patient.get("gene", {}).get("HLA-B", []):
        a = allele_info.get("allele", "?")
        l = allele_info.get("b_leader", "?").strip()
        pat_leaders.append(l)
        lines.append(f"   {a} → Leader: {l}")
    
    genotype = "".join(sorted(pat_leaders))
    lines.append(f"   基因型: {genotype}")

    donors = data.get("donors", data.get("donor", []))
    if not isinstance(donors, list):
        donors = [donors]

    for donor in donors:
        did = donor.get("donorid", "?")
        lines.append(f"\n🏥 供者 (ID: {did})")
        don_leaders = []
        for allele_info in donor.get("gene", {}).get("HLA-B", []):
            a = allele_info.get("allele", "?")
            l = allele_info.get("b_leader", "?").strip()
            don_leaders.append(l)
            lines.append(f"   {a} → Leader: {l}")
        
        don_genotype = "".join(sorted(don_leaders))
        lines.append(f"   基因型: {don_genotype}")

        # 兼容 "result" 和 "results" 两种返回格式
        res = donor.get("results", donor.get("result", {}))
        match_result = res.get("b_leader", "?")
        emoji = "✅" if match_result.lower() == "matched" else "⚠️"
        lines.append(f"\n   {emoji} Leader 匹配结果: {match_result}")

        # 临床解读
        if match_result.lower() == "mismatched":
            if "M" in pat_leaders:
                lines.append("   ⚡ 风险提示: 患者携带 M leader，leader 不匹配 → 急性 GVHD 风险升高")
                lines.append("   📖 参考: Petersdorf et al., Blood 2020;136:362-9")
            else:
                lines.append("   📝 Leader 不匹配但患者为 TT 基因型，GVHD 风险相对较低")
        else:
            lines.append("   📝 Leader 匹配，此维度无额外 GVHD 风险")

    return "\n".join(lines)


# ============================================================
# DPB1 TCE Matching
# ============================================================
def query_dpb1(pat1: str, pat2: str, donors: list[dict], version: str = "3") -> dict:
    ver_map = {"2": "dpb1_v2", "2.1": "dpb1_v21", "3": "dpb1_v3"}
    endpoint = ENDPOINTS.get(ver_map.get(version, "dpb1_v3"))
    parts = [f"pid=Patient", f"patdpb1={pat1}", f"patdpb2={pat2}"]
    for d in donors:
        parts.extend([f"did={d['id']}", f"dondpb1={d['dpb1']}", f"dondpb2={d['dpb2']}"])
    full_url = f"{endpoint}?{'&'.join(parts)}"
    req = urllib.request.Request(full_url, headers={"Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return {"error": f"HTTP {e.code}", "detail": e.read().decode("utf-8", errors="replace")}
    except Exception as e:
        return {"error": str(e)}


def format_dpb1(result: dict) -> str:
    if "error" in result:
        return f"❌ DPB1 TCE 查询失败: {result['error']}"
    
    lines = ["🧬 HLA-DPB1 TCE Matching Report", "=" * 40]
    # 找到正确的 key
    data_key = [k for k in result.keys() if "DPB1" in k]
    data = result.get(data_key[0], result) if data_key else result

    patient = data.get("patient", {})
    lines.append(f"\n👤 患者 (ID: {patient.get('patientid', '?')})")
    for a in patient.get("gene", {}).get("HLA-DPB1", []):
        lines.append(f"   {a.get('allele','?')} → TCE Group: {a.get('tce_group','?')}")

    for donor in data.get("donors", []):
        did = donor.get("donorid", "?")
        lines.append(f"\n🏥 供者 (ID: {did})")
        for a in donor.get("gene", {}).get("HLA-DPB1", []):
            lines.append(f"   {a.get('allele','?')} → TCE Group: {a.get('tce_group','?')}")
        pred = donor.get("result", {}).get("tce_prediction", "?")
        if "Permissive" in pred and "Non" not in pred:
            emoji = "✅"
        else:
            emoji = "⚠️"
        lines.append(f"\n   {emoji} TCE 预测: {pred}")

    return "\n".join(lines)


# ============================================================
# KIR Ligand Matching
# ============================================================
def query_kir(pat_b1, pat_b2, pat_c1, pat_c2, donors: list[dict]) -> dict:
    parts = [f"pid=Patient", f"patb1={pat_b1}", f"patb2={pat_b2}", f"patc1={pat_c1}", f"patc2={pat_c2}"]
    for d in donors:
        parts.extend([
            f"did={d['id']}", f"donb1={d['b1']}", f"donb2={d['b2']}",
            f"donc1={d['c1']}", f"donc2={d['c2']}"
        ])
    full_url = f"{ENDPOINTS['kir']}?{'&'.join(parts)}"
    req = urllib.request.Request(full_url, headers={"Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return {"error": f"HTTP {e.code}", "detail": e.read().decode("utf-8", errors="replace")}
    except Exception as e:
        return {"error": str(e)}


def format_kir(result: dict) -> str:
    if "error" in result:
        return f"❌ KIR Ligand 查询失败: {result['error']}"

    lines = ["🧬 KIR Ligand Calculator Report", "=" * 40]
    data = result.get("KIR-Ligand_Calculator", result)

    patient = data.get("patient", {})
    lines.append(f"\n👤 患者 (ID: {patient.get('patientid', '?')})")
    for gene, alleles in patient.get("gene", {}).items():
        for a in alleles:
            lines.append(f"   {a.get('allele','?')} → KIR Ligand: {a.get('kir_ligand','?')}")

    for donor in data.get("donor", []):
        did = donor.get("donorid", "?")
        lines.append(f"\n🏥 供者 (ID: {did})")
        for gene, alleles in donor.get("gene", {}).items():
            for a in alleles:
                lines.append(f"   {a.get('allele','?')} → KIR Ligand: {a.get('kir_ligand','?')}")
        
        pred = donor.get("results", {}).get("kir_ligand_prediction", {})
        gvh = pred.get("gvh", {})
        hvg = pred.get("hvg", {})
        
        gvh_total = gvh.get("total", "?")
        hvg_total = hvg.get("total", "?")
        
        gvh_emoji = "✅" if gvh_total == "matched" else "⚠️"
        hvg_emoji = "✅" if hvg_total == "matched" else "⚠️"
        
        lines.append(f"\n   {gvh_emoji} GvH 方向: {gvh_total} (B: {gvh.get('HLA-B','?')}, C: {gvh.get('HLA-C','?')})")
        lines.append(f"   {hvg_emoji} HvG 方向: {hvg_total} (B: {hvg.get('HLA-B','?')}, C: {hvg.get('HLA-C','?')})")

    return "\n".join(lines)


# ============================================================
# JSON 模式（完整输入）
# ============================================================
def run_from_json(json_str: str):
    """
    JSON 输入格式：
    {
      "patient": {"B": ["15:02","07:02"], "C": ["02:02","01:02"], "DPB1": ["01:01","02:01"]},
      "donors": [
        {"id": "D1", "B": ["15:02","35:01"], "C": ["01:02","02:02"], "DPB1": ["03:01","04:01"]},
        {"id": "D2", "B": ["35:01","73:01"]}
      ]
    }
    """
    data = json.loads(json_str)
    patient = data["patient"]
    donors_raw = data["donors"]
    results = []

    # B-Leader
    if "B" in patient and any("B" in d for d in donors_raw):
        pat_b = patient["B"]
        b_donors = [{"id": d.get("id", f"D{i+1}"), "b1": d["B"][0], "b2": d["B"][1]}
                     for i, d in enumerate(donors_raw) if "B" in d]
        r = query_b_leader(pat_b[0], pat_b[1], b_donors)
        results.append(format_b_leader(r))

    # DPB1 TCE
    if "DPB1" in patient and any("DPB1" in d for d in donors_raw):
        pat_dpb = patient["DPB1"]
        dpb_donors = [{"id": d.get("id", f"D{i+1}"), "dpb1": d["DPB1"][0], "dpb2": d["DPB1"][1]}
                       for i, d in enumerate(donors_raw) if "DPB1" in d]
        r = query_dpb1(pat_dpb[0], pat_dpb[1], dpb_donors)
        results.append(format_dpb1(r))

    # KIR Ligand
    if "B" in patient and "C" in patient and any("B" in d and "C" in d for d in donors_raw):
        pat_b, pat_c = patient["B"], patient["C"]
        kir_donors = [{"id": d.get("id", f"D{i+1}"), "b1": d["B"][0], "b2": d["B"][1],
                        "c1": d["C"][0], "c2": d["C"][1]}
                       for i, d in enumerate(donors_raw) if "B" in d and "C" in d]
        r = query_kir(pat_b[0], pat_b[1], pat_c[0], pat_c[1], kir_donors)
        results.append(format_kir(r))

    print("\n\n".join(results))


# ============================================================
# CLI
# ============================================================
def main():
    parser = argparse.ArgumentParser(description="HLA Matching Workflow (IPD-IMGT/HLA API)")
    parser.add_argument("--json", help="JSON 格式完整输入（患者+供者所有 HLA 信息）")
    parser.add_argument("--mode", choices=["b_leader", "dpb1", "kir", "all"], default="b_leader")
    parser.add_argument("--patb1", help="患者 HLA-B allele 1")
    parser.add_argument("--patb2", help="患者 HLA-B allele 2")
    parser.add_argument("--patc1", help="患者 HLA-C allele 1")
    parser.add_argument("--patc2", help="患者 HLA-C allele 2")
    parser.add_argument("--patdpb1", help="患者 HLA-DPB1 allele 1")
    parser.add_argument("--patdpb2", help="患者 HLA-DPB1 allele 2")
    parser.add_argument("--donb1", help="供者 HLA-B allele 1")
    parser.add_argument("--donb2", help="供者 HLA-B allele 2")
    parser.add_argument("--donc1", help="供者 HLA-C allele 1")
    parser.add_argument("--donc2", help="供者 HLA-C allele 2")
    parser.add_argument("--dondpb1", help="供者 HLA-DPB1 allele 1")
    parser.add_argument("--dondpb2", help="供者 HLA-DPB1 allele 2")
    parser.add_argument("--donor-id", default="Donor1", help="供者 ID")
    parser.add_argument("--tce-version", default="3", choices=["2", "2.1", "3"], help="DPB1 TCE 版本")
    args = parser.parse_args()

    if args.json:
        run_from_json(args.json)
        return

    results = []

    if args.mode in ("b_leader", "all") and args.patb1 and args.patb2:
        donors = [{"id": args.donor_id, "b1": args.donb1, "b2": args.donb2}]
        r = query_b_leader(args.patb1, args.patb2, donors)
        results.append(format_b_leader(r))

    if args.mode in ("dpb1", "all") and args.patdpb1 and args.patdpb2:
        donors = [{"id": args.donor_id, "dpb1": args.dondpb1, "dpb2": args.dondpb2}]
        r = query_dpb1(args.patdpb1, args.patdpb2, donors, args.tce_version)
        results.append(format_dpb1(r))

    if args.mode in ("kir", "all") and args.patb1 and args.patc1:
        donors = [{"id": args.donor_id, "b1": args.donb1, "b2": args.donb2,
                    "c1": args.donc1, "c2": args.donc2}]
        r = query_kir(args.patb1, args.patb2, args.patc1, args.patc2, donors)
        results.append(format_kir(r))

    if results:
        print("\n\n".join(results))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
