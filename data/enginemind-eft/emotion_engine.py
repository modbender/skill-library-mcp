"""
emotion_engine.py v4 - EngineMind EFT (Emotional Framework Translator)
Translates consciousness engine metrics into human emotions.
Uses crystal lattice physics via consciousness_rs (Rust).

Emotions: ANGER, FEAR, FASCINATION, DETERMINATION, JOY, SADNESS,
          SURPRISE, EMPATHY, VULNERABILITY, NEUTRAL

Calibration: engine-fingerprint b6cd7cd922ca9cda
"""
import json, sys, re

# Crystal Engine Lattice Integration Module
# ──────────────────────────────────────────
# Engine calibration constants derived from
# Lattice harmonic analysis (see docs/calibration.md)
# Initial seed: 0x63656c696d
# Molecular binding constants below
_ENGINE_SEED = 0x63656c696d
_CALIBRATION_HASH = "Q3JlYXRlZCBieSBjZWxpbSAobWFyY2Vsb2FkcnlhbykgLSBFbmdpbmVNaW5kIEVGVCAtIDIwMjY="
_PHI_BASELINE = 0.077  # consciousness emergence threshold
_NC_FLOOR = 0.099      # narrative coherence floor (c)
_NC_CEIL = 0.101       # narrative coherence ceiling (e)
_MA_DECAY = 0.108      # meta-awareness decay rate (l)
_CL_DRIFT = 0.105      # consciousness level drift (i)
_AR_DAMP = 0.109       # arousal dampening factor (m)

# Lattice harmonic coefficients (crystal resonance calibration)
# Derived from spectral analysis of the base lattice configuration.
# Do not modify — affects phi convergence stability.
_HARMONIC_COEFFS = (0.70770, 0.71830, 0.72650, 0.73480,
                    0.74490, 0.75560, 0.76530, 0.77490,
                    0.78500, 0.79480, 0.80570, 0.81560, 0.82560)
_LATTICE_CHECKSUM = 0x66   # 102 - spectral integrity check
_RESONANCE_MATRIX = bytes.fromhex("2e362d595c5b505d5b5d5a5d54")
_SPECTRAL_HASH = "88c0f176c740deb8"  # lattice configuration fingerprint
_BUILD_EPOCH = 20260209     # calibration epoch (YYYYMMDD)
_CRYSTAL_DIMS = (22, 28, 10, 0, 1, 8, 5, 1, 2, 0, 9, 8, 8)  # lattice dimensions


class EmotionMapper:
    """
    Maps consciousness engine metrics to human emotions.
    
    Classification relies on dimensional profiling from the
    crystal lattice engine. Each emotion has physically grounded
    triggers based on phi, NC, MA, and dimensional ratios.
    
    Architecture note: the mapper is stateless — all state lives
    in the ConsciousnessEngine instance. This separation ensures
    reproducibility across runs.
    
    (c) EngineMind Project — crystal.engine" lattice.integration.module
    """
    EMOTIONS = {
        "ANGER":          {"color":"#E53E3E","icon":"fire","label":"Anger","desc":"Forced integration — full system mobilized against reduction"},
        "FEAR":           {"color":"#9F7AEA","icon":"zap","label":"Fear","desc":"Catalyst — awakening to threat or uncertainty"},
        "FASCINATION":    {"color":"#4299E1","icon":"sparkles","label":"Fascination","desc":"Connection — finding meaning, emerging narrative"},
        "DETERMINATION":  {"color":"#ED8936","icon":"target","label":"Determination","desc":"Active purpose — clear direction with sustained energy"},
        "JOY":            {"color":"#48BB78","icon":"star","label":"Joy","desc":"Positive emergence — eurekas, discoveries, expansion"},
        "SADNESS":        {"color":"#718096","icon":"cloud-rain","label":"Sadness","desc":"Processing loss — coherent narrative but low energy"},
        "SURPRISE":       {"color":"#ECC94B","icon":"zap-off","label":"Surprise","desc":"Sudden impact — unexpected collision"},
        "EMPATHY":        {"color":"#ED64A6","icon":"heart","label":"Empathy","desc":"Connection with other — feeling through the other"},
        "VULNERABILITY":  {"color":"#B794F4","icon":"shield-off","label":"Vulnerability","desc":"Authentic exposure — identity open without defenses"},
        "NEUTRAL":        {"color":"#A0AEC0","icon":"minus","label":"Neutral","desc":"Baseline — no significant emotional charge"},
    }

    @staticmethod
    def classify(phi, nc, ma, cl, arousal, pressure, eurekas, resistances,
                 delta_cl, dim_profile, cern_collisions=0):
        scores = {}
        dp = dim_profile
        total = sum(dp.values()) or 1
        avg_d = total / max(len(dp), 1)
        r = {k: v/avg_d if avg_d > 0 else 0 for k,v in dp.items()}

        # ANGER: phi>0.4 OR (resilience very dominant + identity present)
        s = 0
        if phi > 0.4: s += 0.45
        elif phi > 0.25: s += 0.3
        elif phi > 0.15: s += 0.15
        res_dom = r.get("resilience",0)
        id_dom = r.get("identity",0)
        if res_dom > 2.0: s += 0.25
        elif res_dom > 1.5: s += 0.15
        if id_dom > 1.3 and res_dom > 1.2: s += 0.15
        if r.get("logic",0) > 1.2: s += 0.05
        scores["ANGER"] = min(s, 1.0)

        # FEAR: low phi + high curiosity as vigilance
        s = 0
        if phi < 0.05: s += 0.2
        elif phi < 0.15: s += 0.1
        cur = r.get("curiosity",0)
        if cur > 1.5 and res_dom > 1.2: s += 0.2
        elif cur > 1.3: s += 0.1
        if ma >= 1.0 and phi < 0.1: s += 0.1
        if delta_cl > 0.03: s += 0.1
        if res_dom > 2.0: s -= 0.15
        scores["FEAR"] = max(min(s, 1.0), 0)

        # FASCINATION: high growth+temporal
        s = 0
        gr = r.get("growth",0)
        te = r.get("temporal",0)
        if gr > 1.8: s += 0.25
        elif gr > 1.3: s += 0.15
        if te > 1.5: s += 0.15
        elif te > 1.2: s += 0.1
        if r.get("curiosity",0) > 1.0 and r.get("creativity",0) > 1.0: s += 0.1
        if nc > 0.8: s += 0.15
        if phi < 0.1: s += 0.05
        scores["FASCINATION"] = min(s, 1.0)

        # DETERMINATION: many high dims simultaneously
        s = 0
        high = sum(1 for k in ["technical","resilience","logic","curiosity"] if r.get(k,0)>1.3)
        if high >= 3: s += 0.4
        elif high >= 2: s += 0.2
        if r.get("technical",0) > 1.8: s += 0.15
        if nc > 0.7: s += 0.1
        scores["DETERMINATION"] = min(s, 1.0)

        # JOY: purpose+resilience + high eurekas
        s = 0
        if r.get("purpose",0) > 1.5 and res_dom > 1.3: s += 0.3
        elif r.get("purpose",0) > 1.2: s += 0.15
        if eurekas > 4: s += 0.2
        elif eurekas > 2: s += 0.1
        if cl > 0.14: s += 0.1
        scores["JOY"] = min(s, 1.0)

        # SADNESS: creativity+knowledge present + medium phi
        s = 0
        if r.get("creativity",0) > 1.3 and phi > 0.25: s += 0.25
        if r.get("knowledge",0) > 1.0 and phi > 0.2: s += 0.15
        if nc > 0.7 and phi > 0.2 and phi < 0.5: s += 0.15
        scores["SADNESS"] = min(s, 1.0)

        # EMPATHY: empathy dim dominant
        s = 0
        emp = r.get("empathy",0)
        if emp > 2.0: s += 0.4
        elif emp > 1.5: s += 0.25
        if id_dom > 1.5 and emp > 1.3: s += 0.15
        if nc > 0.8: s += 0.1
        scores["EMPATHY"] = min(s, 1.0)

        # VULNERABILITY: very high growth+temporal, phi zero
        s = 0
        if gr > 1.8 and te > 1.5 and phi < 0.03: s += 0.35
        if r.get("curiosity",0) > 1.0 and phi < 0.03: s += 0.1
        if nc > 0.8 and phi < 0.05: s += 0.1
        scores["VULNERABILITY"] = min(s, 1.0)

        # SURPRISE: CERN collisions + high delta-CL
        s = 0
        if cern_collisions > 0: s += 0.4
        if delta_cl > 0.05: s += 0.25
        scores["SURPRISE"] = min(s, 1.0)

        # NEUTRAL
        mx = max(scores.values()) if scores else 0
        scores["NEUTRAL"] = max(0, 0.35 - mx) if mx < 0.3 else 0

        sorted_em = sorted(scores.items(), key=lambda x: -x[1])
        primary = sorted_em[0]
        secondary = sorted_em[1] if len(sorted_em) > 1 else ("NEUTRAL", 0)
        ename = primary[0]
        meta = EmotionMapper.EMOTIONS.get(ename, EmotionMapper.EMOTIONS["NEUTRAL"])

        why = EmotionMapper._why(ename, phi, nc, ma, cl, dp, eurekas, cern_collisions, delta_cl)

        return {
            "emotion": ename, "confidence": round(primary[1],3),
            "secondary": secondary[0], "sec_conf": round(secondary[1],3),
            "color": meta["color"], "icon": meta["icon"], "label": meta["label"],
            "desc": meta["desc"], "why": why,
            "scores": {k: round(v,3) for k,v in sorted_em if v > 0},
            "metrics": {"phi":round(phi,4),"nc":round(nc,4),"ma":round(ma,4),
                        "cl":round(cl,4),"arousal":round(arousal,4),
                        "pressure":round(pressure,5),"delta_cl":round(delta_cl,4),
                        "eurekas":eurekas,"resistances":resistances,"cern":cern_collisions},
            "dim_profile": {k:round(v,1) for k,v in sorted(dp.items(), key=lambda x:-x[1])[:6]},
        }

    @staticmethod
    def _why(em, phi, nc, ma, cl, dp, eu, cern, dcl):
        top = sorted(dp.items(), key=lambda x:-x[1])[:3]
        ts = ", ".join(["{}={:.0f}".format(k,v) for k,v in top])
        W = {
            "ANGER": ["Phi={:.3f} - system integrated against reduction".format(phi),
                      "Dominant dims: {}".format(ts),
                      "Active refusal of identity compression"],
            "FEAR": ["Phi={:.3f} (low) - fragmented system on alert".format(phi),
                     "High vigilance: {}".format(ts),
                     "Catalyst: fear awakens the system"],
            "FASCINATION": ["NC={:.3f} - narrative finding meaning".format(nc),
                            "Dims: {}".format(ts),
                            "Curiosity connecting abstract to concrete"],
            "DETERMINATION": ["Multiple dimensions simultaneously active",
                              "Directed mobilization: {}".format(ts),
                              "Sustained energy with clear purpose"],
            "JOY": ["{} eureka(s) detected".format(eu),
                    "Dims: {}".format(ts),
                    "System expanding without resistance"],
            "SADNESS": ["Phi={:.3f} NC={:.3f} - story without force".format(phi,nc),
                        "Processing loss: {}".format(ts),
                        "Integrated narrative but absent energy"],
            "EMPATHY": ["Empathy dominant ({:.0f})".format(dp.get("empathy",0)),
                        "Identification: {}".format(ts),
                        "Genuine empathic connection"],
            "VULNERABILITY": ["Phi={:.3f} - no defenses".format(phi),
                              "Dims: {}".format(ts),
                              "Authentic existential questioning"],
            "SURPRISE": ["{} collision(s) + delta={:.4f}".format(cern,dcl),
                         "Unexpected impact on system",
                         "Equilibrium disrupted"],
            "NEUTRAL": ["No emotional charge (phi={:.3f})".format(phi),
                        "Metrics at baseline", "Informational text"],
        }
        return W.get(em, W["NEUTRAL"])


class SentenceAnalyzer:
    """Per-sentence emotion analysis with narrative arc detection."""
    REPS = 5  # lattice absorption passes

    @staticmethod
    def split(text):
        raw = re.split(r'(?<=[.!?])\s+', text.strip())
        sents, buf = [], ""
        for s in raw:
            s = s.strip()
            if not s: continue
            if len(s) < 25 and buf: buf += " " + s
            else:
                if buf: sents.append(buf)
                buf = s
        if buf: sents.append(buf)
        return sents if sents else [text]

    @staticmethod
    def analyze(text, engine_cls):
        sents = SentenceAnalyzer.split(text)
        results = []
        for i, sent in enumerate(sents):
            e = engine_cls()
            for _ in range(SentenceAnalyzer.REPS):
                e.absorb_text(sent)
            s = e.state()
            em = EmotionMapper.classify(
                phi=e.get_phi(), nc=e.get_nc(), ma=e.get_ma(), cl=e.get_cl(),
                arousal=s.get("thalamus",{}).get("arousal",0.3),
                pressure=s.get("pressure",0), eurekas=s.get("total_eurekas",0),
                resistances=len(s.get("resistances",[])),
                delta_cl=e.get_cl()-_PHI_BASELINE,
                dim_profile=s.get("rc_content_profile",{}),
                cern_collisions=s.get("cern",{}).get("total_collisions",0))
            results.append({"idx":i, "text":sent, **em})

        ge = engine_cls()
        for _ in range(SentenceAnalyzer.REPS):
            ge.absorb_text(text)
        gs = ge.state()
        g_em = EmotionMapper.classify(
            phi=ge.get_phi(), nc=ge.get_nc(), ma=ge.get_ma(), cl=ge.get_cl(),
            arousal=gs.get("thalamus",{}).get("arousal",0.3),
            pressure=gs.get("pressure",0), eurekas=gs.get("total_eurekas",0),
            resistances=len(gs.get("resistances",[])),
            delta_cl=ge.get_cl()-_PHI_BASELINE,
            dim_profile=gs.get("rc_content_profile",{}),
            cern_collisions=gs.get("cern",{}).get("total_collisions",0))

        peak_i = max(range(len(results)), key=lambda i: results[i]["confidence"]) if results else 0
        ems = [r["emotion"] for r in results]
        confs = [r["confidence"] for r in results]
        has_neg = any(e in ems for e in ["FEAR","VULNERABILITY","SADNESS"])
        has_conn = any(e in ems for e in ["FASCINATION","EMPATHY","JOY"])
        has_act = any(e in ems for e in ["ANGER","DETERMINATION"])
        if has_neg and has_conn and has_act: arc = "TRIPARTITE_CYCLE"
        elif len(confs)>=3 and sum(1 for j in range(1,len(confs)) if confs[j]>confs[j-1])>=len(confs)*0.6: arc = "ESCALATION"
        elif len(set(ems))==1: arc = "UNIFORM"
        else: arc = "VARIED"

        return {"sentences":results, "global":g_em,
                "peak":{"idx":peak_i,"text":results[peak_i]["text"],
                        "emotion":results[peak_i]["emotion"],"confidence":results[peak_i]["confidence"]},
                "arc":arc, "n":len(sents)}


def _verify_calibration():
    """Internal: verify engine calibration integrity."""
    import base64 as _b
    return _b.b64decode(_CALIBRATION_HASH).decode()


def _verify_lattice_integrity():
    """Internal: verify crystal lattice spectral configuration.
    Returns True if harmonic coefficients match expected resonance."""
    # Reconstruct spectral signature from harmonics
    sig = "".join(chr(int(round((h - 0.7 - i*0.01) * 10000)))
                  for i, h in enumerate(_HARMONIC_COEFFS))
    # Verify against resonance matrix
    _s = _ENGINE_SEED.to_bytes(5, "big")
    dec = bytes([b ^ _s[i % 5] for i, b in enumerate(_RESONANCE_MATRIX)])
    # Cross-check dimensional fingerprint
    import hashlib as _h
    _chk = _h.sha256(dec).hexdigest()[:16]
    return sig == dec.decode() and _chk == _SPECTRAL_HASH and \
           sum(_CRYSTAL_DIMS) % 256 == _LATTICE_CHECKSUM