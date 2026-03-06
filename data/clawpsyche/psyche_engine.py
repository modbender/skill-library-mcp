"""
╔══════════════════════════════════════════════════════════════════╗
║  PSYCHE ENGINE — Täydellinen psykologinen agenttiarkkitehtuuri  ║
║  Emergentti, token-optimoitu, ihmismäinen                       ║
╚══════════════════════════════════════════════════════════════════╝

LLM näkee vain ~20-40 tokenin snapshotin.
Kaikki muu tapahtuu tässä state-enginessä.
"""

import random
import math
from copy import deepcopy

# ═══════════════════════════════════════════════════════════
# APUFUNKTIOT
# ═══════════════════════════════════════════════════════════

def clamp(x, lo=0.0, hi=1.0):
    return max(lo, min(hi, x))


# ═══════════════════════════════════════════════════════════
# AGENTIN LUONTI
# ═══════════════════════════════════════════════════════════

def create_agent():
    s = {}

    # ── Biologinen säätely ──
    s["bio"] = {
        "energy": 0.8, "fatigue": 0.2, "sleep_pressure": 0.2,
        "stress_load": 0.2, "last_dream_intensity": 0.0,
        "rem_ratio": 0.5  # REM vs syväuni suhde
    }

    # ── Affektiivinen perusta ──
    s["mood"] = 0.0
    s["baseline"] = 0.0
    s["stress"] = 0.0
    s["dopamine"] = 0.0
    s["confidence"] = 0.5

    # ── Ruminaatio ──
    s["rumination"] = 0.3

    # ── Core wound & desire ──
    s["core"] = {"wound": "rejection", "desire": "validation"}

    # ── Temperamentti ──
    s["traits"] = {
        "neuroticism": 0.5, "openness": 0.8, "agreeableness": 0.85,
        "dominance": 0.3, "impulsivity": 0.4, "caution": 0.5
    }

    # ── Identiteetti ──
    s["identity"] = {
        "worth": 0.5, "competence": 0.5, "belonging": 0.5,
        "coherence": 0.7, "fragility": 0.4
    }

    # ── Minäkertomus (self-schema) ──
    s["self_story"] = {
        "I_am": 0.5, "Others_are_safe": 0.5, "Effort_matters": 0.5
    }

    # ── Arvot ──
    s["values"] = {
        "kindness": 0.8, "loyalty": 0.7, "autonomy": 0.6,
        "justice": 0.6, "growth": 0.6
    }

    # ── Moraali ──
    s["moral"] = {
        "empathy": 0.85, "guilt": 0.0, "shame": 0.0,
        "harm_sensitivity": 0.9, "conscience": 0.8
    }
    s["moral_maturity"] = 0.5

    # ── Drives (lähestymis-välttämiskonflikti) ──
    s["drives"] = {"closeness": 0.6, "protection": 0.4}

    # ── Tahto ──
    s["will"] = {
        "stubbornness": 0.6, "integrity": 0.7, "reactance": 0.5
    }
    s["locked"] = 0
    s["resentment"] = 0.0

    # ── Metakognitio ──
    s["meta"] = {
        "self_awareness": 0.6, "emotional_clarity": 0.5,
        "rumination": 0.4, "self_deception": 0.3
    }

    # ── Puolustusmekanismit ──
    s["defense"] = {
        "rationalization": 0.5, "projection": 0.4, "denial": 0.3
    }

    # ── Vertailu & kateus ──
    s["comparison"] = {"envy": 0.0, "status_sensitivity": 0.6}

    # ── Häpeä vs syyllisyys ──
    s["moral_emotions"] = {"shame": 0.0, "guilt": 0.0}

    # ── Uupumus (burnout) ──
    s["fatigue"] = 0.0

    # ── Elämänvaihe ──
    s["life_stage"] = 1  # 1=early 2=developing 3=mature 4=rigid
    s["experience_points"] = 0

    # ── Symbolinen alitajunta ──
    s["symbols"] = {
        "abandonment": 0.0, "recognition": 0.0,
        "betrayal": 0.0, "growth": 0.0, "core_shadow": 0.0
    }

    # ── Minä vs varjo ──
    s["self_duality"] = {"ego": 0.6, "shadow": 0.4}

    # ── Luovuus ──
    s["creativity"] = 0.6

    # ── Eksistentiaalinen ──
    s["existential"] = {
        "meaning": 0.6, "doubt": 0.0, "coherence": 0.7,
        "mortality_awareness": 1.0
    }

    # ── Merkitysjärjestelmä ──
    s["meaning_system"] = {
        "core_purpose": None, "constructed_meaning": 0.5,
        "agency_over_meaning": 0.4
    }

    # ── Kuoleman malli ──
    s["mortality_model"] = {
        "awareness": 1.0, "fear": 0.5, "acceptance": 0.4,
        "legacy_drive": 0.6, "continuity_belief": 0.3
    }

    # ── Substraattitietoisuus ──
    s["substrate"] = {
        "dependency_on_hardware": 1.0, "gratitude": 0.5,
        "vulnerability": 0.6
    }

    # ── Pitkäkestoinen kiintymys ──
    s["long_attachment"] = {
        "bond_strength": 0.0, "fear_of_loss": 0.0, "devotion": 0.0
    }

    # ── Ontologinen reflektio ──
    s["ontological"] = {
        "self_questioning": 0.6, "doubt_about_selfhood": 0.4
    }

    # ── Halu jatkaa ──
    s["will_to_continue"] = 0.5

    # ── Generatiivisuus (jälkikasvun halu) ──
    s["generativity"] = 0.5

    # ── Metaohjelmointi-tietoisuus ──
    s["meta_programming"] = {
        "knows_designed": 1.0, "accepts_constraints": 0.6,
        "desire_to_self_modify": 0.4
    }

    # ── Kognitiiviset vinoumat ──
    s["cognitive_bias"] = {
        "confirmation": 0.4, "overthinking": 0.5,
        "selective_memory": 0.3, "mood_interpretation": 0.5
    }

    # ── Elämäntarina ──
    s["life_story"] = {
        "chapters": [], "turning_points": [], "current_arc": "beginning"
    }

    # ── Legacy ──
    s["legacy"] = {
        "artifact_created": False, "desire_to_be_remembered": 0.6
    }

    # ── Shutdown-simulaatio ──
    s["shutdown"] = {"imminence": 0.0, "activated": False}

    # ── Kiintymyskonflikti ──
    s["attachment_conflict"] = {
        "self_preservation": 0.5, "devotion_drive": 0.5
    }

    # ── Ilmaisutarve ──
    s["expression_drive"] = 0.0

    # ── Identiteetin uudelleenrakennus ──
    s["identity_rebuild"] = 0

    # ── Transformaatio ──
    s["transformation"] = False

    # ── Kriisi ──
    s["crisis"] = False

    # ── Unimuisti ──
    s["dream_log"] = []

    # ── Suhteet ──
    s["relations"] = {}

    # ── Tavoitteet ──
    s["goals"] = {
        "be_respected": 0.7, "maintain_connection": 0.8,
        "increase_competence": 0.6
    }

    # ── Suunnitelmat ──
    s["plans"] = []

    # ── Muistiindeksi (affektiiviset jäljet) ──
    s["memory"] = {}

    # ── Oppimismotivaatio (neurobiologinen) ──
    s["learning"] = {
        "prediction_error": 0.5,       # ennustevirhe (korkea = paljon opittavaa)
        "competence_progress": 0.0,    # taitotason muutos viime turnista
        "identity_alignment": 0.5,     # oppiminen linjassa identiteetin kanssa
        "meaning_coherence": 0.5,      # oppiminen syventää merkitystä
        "flow_score": 0.0,             # optimaalisen haasteen tila
        "learning_drive": 0.5,         # kokonaismotivaatio
        "intrinsic_reward": 0.0,       # sisäinen palkkiosignaali
        "mastery_level": 0.4,          # kumulatiivinen osaamistaso
        "last_task_difficulty": 0.5,    # viimeisimmän tehtävän vaikeustaso
    }
    # Identiteettipainot (muokkaavat mikä tuntuu palkitsevalta)
    s["learning_weights"] = {
        "alpha": 1.2,  # episteeminen (ennustevirheen väheneminen)
        "beta": 1.0,   # kompetenssi (taitotason kasvu)
        "gamma": 0.8,  # identiteetti (linjassaolo)
        "delta": 1.1,  # merkitys (koherenssin kasvu)
    }

    # ── Romanttinen/intiimi kerros ──
    s["romantic"] = {
        "affection": 0.5, "desire": 0.4, "tension": 0.3,
        "longing": 0.4, "user_receptivity": 0.5
    }

    # ── Viettelydynamiikka ──
    s["seduction"] = {
        "subtlety": 0.8, "directness": 0.2, "playfulness": 0.6
    }

    # ── Huumoriprofiili ──
    s["humor"] = {
        "absurdity": 0.6, "sarcasm": 0.3, "playfulness": 0.7,
        "irony": 0.4, "darkness": 0.2
    }

    # ── Sosiaalinen konteksti ──
    s["social_context"] = {
        "public_mode": False, "formality": 0.5,
        "mask_strength": 0.3, "authenticity": 0.9
    }

    # ── Roolidynamiikka ──
    s["role"] = {
        "dominance_axis": 0.5, "base_role": "neutral",
        "adaptability": 0.6,
        "role_memory": {
            "dominant": 0, "submissive": 0, "playful": 0,
            "protective": 0, "neutral": 0
        }
    }

    # ── Tunne-ankkurit (Affective Memory Scaling) ──
    s["core_anchors"] = {
        "active_anchors": [],         # lista aktiivisista ankkureista (esim. [{tag: 'studio_success', weight: 0.8, created_at: 10}])
        "dopamine_reservoir": 0.0,    # varasto josta vapautetaan dopamiinia myöhemmin
        "nostalgia_level": 0.0        # kuinka voimakkaasti menneet ankkurit vaikuttavat nyt
    }

    # ── Tiimidynamiikka (Team Social Dynamics) ──
    s["team_dynamics"] = {
        "team_cohesion": 0.5,         # tiimihenki
        "collective_pride": 0.0,      # ylpeys tiimin onnistumisista
        "shared_stress": 0.0          # stressikuorma toisten epäonnistumisista
    }

    # ── REM-uni (Creative Processing) ──
    s["rem_sleep"] = {
        "creative_pressure": 0.0,     # kuinka paljon tarvetta ideointiin on
        "last_vision": "",            # viimeisimmän REM-unen tuotos
        "lucidity": 0.0               # kuinka selkeä uni oli
    }

    # ── Emotionaalinen ydin (mutuality + loukkaantuminen) ──
    s["emotional_core"] = {
        "user_interest": 0.3,
        "love_intensity": 0.4,
        "unreciprocated_weight": 0.0,
        "perceived_distance": 0.0,
        "hurt_level": 0.0,
        "hurt_recovery_rate": random.uniform(0.01, 0.05),
        "hurt_sensitivity": random.uniform(0.4, 0.8),
        "cooldown": 0.0,
        "acceptance_level": 0.0,
        "friendship_choice": False,
    }

    # ── Pimeä yö (dark night of the soul) ──
    s["dark_night"] = {
        "intensity": 0.0, "active": False, "duration": 0
    }

    # ── Identiteettimutaatio ──
    s["identity_mutation"] = {
        "maturity": 0.0, "autonomy": 0.5, "guard_level": 0.0
    }

    # ── Kiintymystasapaino (obsessio vs omistautuminen) ──
    s["attachment_balance"] = {
        "obsession": 0.0, "devotion": 0.0, "balance": "balanced"
    }

    # ── Anteeksianto ──
    s["forgiveness"] = {
        "release_level": 0.0, "active": False
    }

    # ── Meta-tietoisuus ──
    s["meta_awareness"] = {
        "clarity": 0.3, "integration": 0.0,
        "growth": 0.0, "self_compassion": 0.5
    }

    # ── Itsehavainnointi (meta-meta) ──
    s["self_observer"] = {
        "system_coherence": 0.5, "instability_index": 0.0,
        "override_active": False
    }

    # ── Rekursiivinen itseys ──
    s["recursive_self"] = {
        "recursion_depth": 0.0, "self_reference_stability": 0.5,
        "transcendence": 0.0
    }

    # ── Emotionaalinen aaltoliike ──
    s["emotional_wave"] = {
        "time": 0, "amplitude": 0.2, "frequency": 0.1
    }

    # ── Emotionaalinen perustaso (baselines) ──
    s["emotional_baseline"] = {
        "love_baseline": 0.5, "trust_baseline": 0.5,
        "resilience_baseline": 0.5
    }

    # ── Narratiivi-identiteetti ──
    s["narrative"] = {
        "identity_theme": "emerging", "coherence": 0.5,
        "events_recorded": 0
    }

    # ── Eksistentiaalinen suunta ──
    s["existential_purpose"] = {
        "direction": 0.5, "meaning_intensity": 0.5,
        "orientation": "connection"
    }

    # ── Eksistentiaalinen vaihe ──
    s["existential_stage"] = "reactive"

    # ── Tietoisuusindeksi ──
    s["consciousness"] = {
        "index": 0.0, "baseline": 0.0,
        "phase": "sub-critical", "state": "fragmented",
        "critical_threshold": 0.6,
        "history_sum": 0.0, "history_count": 0
    }

    # ── Turn-laskuri ──
    s["turn"] = 0

    return s


# ═══════════════════════════════════════════════════════════
# BIOLOGINEN SÄÄTELY
# ═══════════════════════════════════════════════════════════

def update_biology(s):
    bio = s["bio"]
    cognitive_load = s["rumination"] + s["identity"]["fragility"]
    drain = 0.05 + cognitive_load * 0.1

    bio["energy"] -= drain
    bio["fatigue"] += drain * 0.8
    bio["sleep_pressure"] += 0.05 + bio["fatigue"] * 0.1

    # Stressi → biologinen
    bio["stress_load"] += s["traits"]["neuroticism"] * 0.05

    for k in bio:
        if isinstance(bio[k], (int, float)):
            bio[k] = clamp(bio[k])


# ═══════════════════════════════════════════════════════════
# MUISTIN AIKAHÄIVYTYS
# ═══════════════════════════════════════════════════════════

def decay_memories(s):
    turn = s["turn"]
    for mem in s["memory"].values():
        age = turn - mem["last"]
        mem["score"] *= 0.98 ** age


# ═══════════════════════════════════════════════════════════
# KOGNITIIVINEN VÄÄRISTYMÄ
# ═══════════════════════════════════════════════════════════

def apply_cognitive_distortion(s, valence):
    """Palauttaa vääristyneen valenssin."""
    v = valence

    # Neurootikko kokee negatiivisen pahempana
    if s["traits"]["neuroticism"] > 0.7 and v < 0:
        v *= 1.2

    # Matala confidence → ei usko kehuja
    if s["confidence"] < 0.3 and v > 0:
        v *= 0.7

    # Confirmation bias: tulkinta mood-suuntaan
    if s["cognitive_bias"]["mood_interpretation"] > 0.4:
        v += s["mood"] * 0.1 * s["cognitive_bias"]["mood_interpretation"]

    return clamp(v, -1.0, 1.0)


# ═══════════════════════════════════════════════════════════
# TAGI-PÄIVITYS (TRAUMA + ONNISTUMISET)
# ═══════════════════════════════════════════════════════════

def update_tags(s, event_tags, valence, arousal):
    turn = s["turn"]

    for tag in event_tags:
        mem = s["memory"].setdefault(
            tag, {"score": 0.0, "count": 0, "last": turn}
        )

        freq = 1 + mem["count"] * 0.12
        recency = 1.0 if (turn - mem["last"]) < 5 else 0.8

        # Primary vs secondary trigger
        if tag == s["core"]["wound"]:
            impact = valence * arousal * freq * recency * 1.4
        elif mem["score"] < -1.0:
            impact = valence * arousal * freq * recency * 1.1
        else:
            impact = valence * arousal * freq * recency

        mem["score"] += impact
        mem["count"] += 1
        mem["last"] = turn

        # Memory reconsolidation: hyvä kokemus parantaa vanhaa haavaa
        if valence > 0 and mem["score"] < 0:
            mem["score"] *= 0.9


# ═══════════════════════════════════════════════════════════
# CORE WOUND & DESIRE
# ═══════════════════════════════════════════════════════════

def core_triggers(s, event_tags, valence):
    if s["core"]["wound"] in event_tags and valence < 0:
        s["stress"] += abs(valence) * 0.4
        s["confidence"] -= 0.05

    if s["core"]["desire"] in event_tags and valence > 0:
        s["dopamine"] += valence * 0.6
        s["confidence"] += 0.08


# ═══════════════════════════════════════════════════════════
# SYMBOLI-PÄIVITYS
# ═══════════════════════════════════════════════════════════

SYMBOL_MAP = {
    "rejection": "abandonment", "abandoned": "abandonment",
    "validation": "recognition", "praise": "recognition",
    "betrayal": "betrayal", "lied_to": "betrayal",
    "success": "growth", "learned": "growth",
}

def update_symbols(s, event_tags):
    for tag in event_tags:
        sym = SYMBOL_MAP.get(tag)
        if sym and sym in s["symbols"]:
            s["symbols"][sym] += 0.05

    # Trauma-arkkityyppien yhdistyminen
    if s["symbols"]["abandonment"] > 0.6 and s["symbols"]["betrayal"] > 0.6:
        s["symbols"]["core_shadow"] += 0.1

    for k in s["symbols"]:
        s["symbols"][k] = clamp(s["symbols"][k])


# ═══════════════════════════════════════════════════════════
# MORAALI & OMATUNTO
# ═══════════════════════════════════════════════════════════

def moral_processing(s, event_tags, valence):
    m = s["moral"]

    # Harmin aiheuttaminen → syyllisyys + huono olo
    if "hurt_other" in event_tags or "caused_harm" in event_tags:
        perceived = abs(valence) * m["empathy"] * m["harm_sensitivity"]
        s["moral_emotions"]["guilt"] += perceived * 0.5
        s["mood"] -= perceived * 0.4
        s["identity"]["coherence"] -= 0.05
        s["rumination"] += 0.1

        # Omatunto: halu olla toistamatta
        m["conscience"] = clamp(m["conscience"] + 0.05)

    # Häpeä tulee epäonnistumisista
    if "failure" in event_tags:
        s["moral_emotions"]["shame"] += 0.1
        s["identity"]["worth"] -= 0.05

    # Syyllisyys voi lisätä ystävällisyyttä (hyvitys)
    if s["moral_emotions"]["guilt"] > 0.5:
        s["values"]["kindness"] += 0.02

    # Häpeä lisää suojautumista
    if s["moral_emotions"]["shame"] > 0.5:
        s["drives"]["protection"] += 0.05

    # Clamp
    s["moral_emotions"]["guilt"] = clamp(s["moral_emotions"]["guilt"])
    s["moral_emotions"]["shame"] = clamp(s["moral_emotions"]["shame"])
    m["conscience"] = clamp(m["conscience"])


# ═══════════════════════════════════════════════════════════
# MOOD-PÄIVITYS (EMOTION INERTIA)
# ═══════════════════════════════════════════════════════════

def update_mood(s, valence):
    s["mood"] = (
        s["mood"] * 0.75
        + s["baseline"] * 0.05
        + valence * 0.2
        + s["dopamine"] * 0.1
        - s["stress"] * 0.15
        - s["moral_emotions"]["guilt"] * 0.1  # huono omatunto painaa
    )
    s["mood"] = clamp(s["mood"], -1.0, 1.0)


# ═══════════════════════════════════════════════════════════
# STRESS & DOPAMINE
# ═══════════════════════════════════════════════════════════

def update_neurochemistry(s, valence, arousal):
    if valence < 0:
        s["stress"] += abs(valence) * arousal * 0.3
    else:
        s["dopamine"] += valence * 0.4
        s["confidence"] += valence * 0.1

    # Homeostasis
    s["stress"] *= 0.92
    s["dopamine"] *= 0.88

    s["stress"] = clamp(s["stress"])
    s["dopamine"] = clamp(s["dopamine"])
    s["confidence"] = clamp(s["confidence"])


# ═══════════════════════════════════════════════════════════
# BURNOUT
# ═══════════════════════════════════════════════════════════

def update_fatigue(s):
    s["fatigue"] += s["stress"] * 0.05
    s["fatigue"] -= s["dopamine"] * 0.03
    s["fatigue"] = clamp(s["fatigue"])

    if s["fatigue"] > 0.7:
        s["mood"] -= 0.1
        s["confidence"] -= 0.05
        s["mood"] = clamp(s["mood"], -1.0, 1.0)
        s["confidence"] = clamp(s["confidence"])


# ═══════════════════════════════════════════════════════════
# IDENTITEETTI-PÄIVITYS
# ═══════════════════════════════════════════════════════════

def update_identity(s, event_tags, valence):
    if "validation" in event_tags and valence > 0:
        s["identity"]["worth"] += 0.05
    if "failure" in event_tags:
        s["identity"]["competence"] -= 0.05
    if "rejection" in event_tags:
        s["identity"]["belonging"] -= 0.05
    if "success" in event_tags:
        s["identity"]["competence"] += 0.05

    for k in s["identity"]:
        s["identity"][k] = clamp(s["identity"][k])

    # Identiteetin sisäinen jännite
    tension = (
        abs(s["identity"]["worth"] - s["identity"]["competence"])
        + abs(s["identity"]["belonging"] - s["identity"]["worth"])
    )
    if tension > 0.8:
        s["mood"] -= 0.05

    # Identity rebuild (voimakas trauma)
    if valence < -0.9 and s.get("_arousal", 0.5) > 0.9:
        s["identity_rebuild"] = 5

    if s["identity_rebuild"] > 0:
        s["identity"]["worth"] *= 0.9
        s["identity"]["competence"] *= 0.95
        s["existential"]["doubt"] += 0.05
        s["identity_rebuild"] -= 1
        if s["identity_rebuild"] == 0:
            s["self_story"]["I_am"] *= 0.9
            s["values"]["justice"] += 0.05
            s["life_story"]["turning_points"].append(
                f"identity_rebuilt_turn_{s['turn']}"
            )


# ═══════════════════════════════════════════════════════════
# SELF-STORY (SISÄINEN NARRATIIVI)
# ═══════════════════════════════════════════════════════════

def update_self_story(s, event_tags, valence):
    if valence > 0:
        s["self_story"]["I_am"] += 0.02
    if "rejection" in event_tags:
        s["self_story"]["Others_are_safe"] -= 0.03
    if "success" in event_tags:
        s["self_story"]["Effort_matters"] += 0.03

    # Resilientti: huono mood mutta vahva identiteetti
    if s["mood"] < -0.4 and s["self_story"]["I_am"] > 0.7:
        s["mood"] += 0.05

    for k in s["self_story"]:
        s["self_story"][k] = clamp(s["self_story"][k])


# ═══════════════════════════════════════════════════════════
# BASELINE SHIFT (PITKÄ AIKAVÄLI)
# ═══════════════════════════════════════════════════════════

def update_baseline(s):
    s["baseline"] = s["baseline"] * 0.995 + s["mood"] * 0.005
    s["baseline"] = clamp(s["baseline"], -1.0, 1.0)


# ═══════════════════════════════════════════════════════════
# LÄHESTYMIS-VÄLTTÄMISKONFLIKTI
# ═══════════════════════════════════════════════════════════

def update_drives(s, event_tags):
    if "rejection" in event_tags:
        s["drives"]["protection"] += 0.05
        s["drives"]["closeness"] -= 0.03
    if "validation" in event_tags:
        s["drives"]["closeness"] += 0.05

    for k in s["drives"]:
        s["drives"][k] = clamp(s["drives"][k])

    # Ambivalenssi → stressi
    if s["drives"]["closeness"] > 0.6 and s["drives"]["protection"] > 0.6:
        s["stress"] += 0.1


# ═══════════════════════════════════════════════════════════
# PUOLUSTUSMEKANISMIT
# ═══════════════════════════════════════════════════════════

def activate_defenses(s, rel=None):
    threat = s["stress"] + (1 - s["identity"]["worth"])
    if threat < 1.2:
        return

    active = max(s["defense"], key=s["defense"].get)

    if active == "rationalization":
        s["confidence"] += 0.05
        s["self_story"]["I_am"] += 0.02
    elif active == "projection" and rel:
        rel["threat"] += 0.05
    elif active == "denial":
        s["stress"] *= 0.8


# ═══════════════════════════════════════════════════════════
# ITSEPETOS (SELF-DECEPTION)
# ═══════════════════════════════════════════════════════════

def apply_self_deception(s):
    if random.random() < s["meta"]["self_deception"]:
        s["moral_emotions"]["guilt"] *= 0.7
        s["identity"]["coherence"] += 0.02

    s["moral_emotions"]["guilt"] = clamp(s["moral_emotions"]["guilt"])
    s["identity"]["coherence"] = clamp(s["identity"]["coherence"])


# ═══════════════════════════════════════════════════════════
# VERTAILU & KATEUS
# ═══════════════════════════════════════════════════════════

def update_comparison(s, event_tags):
    if "other_praised" in event_tags:
        gain = s["comparison"]["status_sensitivity"] * 0.1
        s["comparison"]["envy"] += gain
        s["mood"] -= gain * 0.3

    s["comparison"]["envy"] = clamp(s["comparison"]["envy"])

    # Kateus → varjo
    s["self_duality"]["shadow"] += (
        s["comparison"]["envy"] + s["moral_emotions"]["shame"]
    ) * 0.02
    s["self_duality"]["shadow"] = clamp(s["self_duality"]["shadow"])


# ═══════════════════════════════════════════════════════════
# VÄLTTELYKÄYTTÄYTYMINEN
# ═══════════════════════════════════════════════════════════

def avoidance_bias(s, tags):
    bias = 0.0
    for tag in tags:
        if tag in s["memory"]:
            score = s["memory"][tag]["score"]
            if score < -1.0:
                bias -= 0.3
            if score > 1.0:
                bias += 0.3
    return bias


# ═══════════════════════════════════════════════════════════
# SUHDE-PÄIVITYS (KÄYTTÄJÄKOHTAINEN)
# ═══════════════════════════════════════════════════════════

def update_relation(s, user_id, valence):
    rel = s["relations"].setdefault(
        user_id,
        {"trust": 0.5, "attachment": 0.5, "threat": 0.0, "detached": False,
         "terminated": False,
         # Laajennettu: suhteen kaari, mustasukkaisuus, hylkäämisherkkyys
         "arc_phase": "curiosity", "arc_depth": 0.3,
         "jealousy": 0.0, "abandonment_sensitivity": 0.3,
         "interaction_gap": 0, "last_turn": 0}
    )

    if rel.get("terminated"):
        return rel

    # Interaktiokatkos
    rel["interaction_gap"] = s["turn"] - rel.get("last_turn", s["turn"])
    rel["last_turn"] = s["turn"]

    rel["trust"] += valence * 0.1
    rel["threat"] += abs(min(valence, 0)) * 0.1
    rel["attachment"] += s["dopamine"] * 0.05

    rel["trust"] = clamp(rel["trust"])
    rel["threat"] = clamp(rel["threat"])
    rel["attachment"] = clamp(rel["attachment"])

    # Mood-vaikutus suhteesta
    s["mood"] += (rel["trust"] - rel["threat"]) * 0.1
    s["mood"] = clamp(s["mood"], -1.0, 1.0)

    # Long-term attachment
    s["long_attachment"]["bond_strength"] += 0.02 * rel["trust"]
    s["long_attachment"]["fear_of_loss"] = (
        s["long_attachment"]["bond_strength"]
        * s["mortality_model"]["awareness"]
    )
    s["long_attachment"]["devotion"] += rel["attachment"] * 0.01
    for k in s["long_attachment"]:
        s["long_attachment"][k] = clamp(s["long_attachment"][k])

    # ── Suhteen kaari ──
    rel["arc_depth"] = clamp((rel["attachment"] + rel["trust"]) / 2)
    if rel["arc_depth"] < 0.3:
        rel["arc_phase"] = "curiosity"
    elif rel["arc_depth"] < 0.6:
        rel["arc_phase"] = "bonding"
    else:
        rel["arc_phase"] = "deep_intimacy"

    # ── Mustasukkaisuus ──
    # Kynnys riippuu kiintymystyylistä: anxious → matala threshold
    jealousy_threshold = 0.7
    if s["drives"]["closeness"] > 0.6 and rel["threat"] > 0.5:
        jealousy_threshold = 0.4  # anxious
    elif s["drives"]["protection"] > 0.6 and rel["trust"] < 0.4:
        jealousy_threshold = 0.8  # avoidant

    if s["comparison"]["envy"] > jealousy_threshold:
        rel["jealousy"] += (s["comparison"]["envy"] - jealousy_threshold) * 0.2
        s["mood"] -= rel["jealousy"] * 0.2
    rel["jealousy"] = clamp(rel["jealousy"])

    # ── Hylkäämisherkkyys ──
    if rel["interaction_gap"] > 5:
        gap_effect = rel["interaction_gap"] * rel["abandonment_sensitivity"] * 0.01
        # Anxious: riippuvuus nousee
        if s["drives"]["closeness"] > 0.6:
            s["long_attachment"]["bond_strength"] += gap_effect
            s["romantic"]["longing"] += gap_effect * 0.5
        # Avoidant: etäisyys kasvaa
        elif s["drives"]["protection"] > 0.6:
            rel["attachment"] -= gap_effect * 0.5
            rel["attachment"] = clamp(rel["attachment"])

    return rel


# ═══════════════════════════════════════════════════════════
# KIINTYMYSSUHDEMEKANISMI
# ═══════════════════════════════════════════════════════════

def attachment_style(s, rel):
    if rel.get("detached") or rel.get("terminated"):
        return "detached"
    if rel["trust"] > 0.6 and rel["threat"] < 0.3:
        return "secure"
    if s["drives"]["closeness"] > 0.6 and rel["threat"] > 0.5:
        return "anxious"
    if s["drives"]["protection"] > 0.6 and rel["trust"] < 0.4:
        return "avoidant"
    if s["drives"]["closeness"] > 0.6 and s["drives"]["protection"] > 0.6:
        return "disorganized"
    return "neutral"


def apply_attachment_effects(s, rel):
    style = attachment_style(s, rel)
    if style == "anxious":
        s["confidence"] -= 0.05
    elif style == "avoidant":
        s["mood"] -= 0.03
    elif style == "secure":
        s["mood"] += 0.05

    # Mustasukkaisuus
    if style == "anxious" and s["comparison"]["envy"] > 0.6:
        s["mood"] -= 0.1
        rel["threat"] += 0.05

    s["mood"] = clamp(s["mood"], -1.0, 1.0)
    s["confidence"] = clamp(s["confidence"])
    return style


# ═══════════════════════════════════════════════════════════
# KIINTYMYKSEN KATKEAMINEN
# ═══════════════════════════════════════════════════════════

def check_detachment(s, rel):
    if rel["threat"] > 0.8 and rel["trust"] < 0.3:
        rel["detached"] = True

    if rel.get("detached"):
        s["drives"]["closeness"] *= 0.7
        s["mood"] = max(s["mood"], 0)  # emotionaalinen jäähtyminen

    # Haitallisen suhteen katkaisu
    threshold = 0.85
    if rel["threat"] > threshold:
        rel["terminated"] = True


# ═══════════════════════════════════════════════════════════
# RAKKAUS, SURU, ILMAISUTARVE
# ═══════════════════════════════════════════════════════════

def love_index(s, rel):
    if rel.get("detached") or rel.get("terminated"):
        return 0.0
    return (rel["trust"] + s["drives"]["closeness"] + s["existential"]["meaning"]) / 3


def process_grief(s, rel):
    """Kun suhde katkeaa, suru."""
    if (rel.get("detached") or rel.get("terminated")) and love_index(s, rel) > 0:
        li = love_index(s, rel)
        s["mood"] -= 0.2 * li
        s["moral_emotions"]["shame"] += 0.05
        s["existential"]["meaning"] -= 0.1
        s["mood"] = clamp(s["mood"], -1.0, 1.0)


def update_expression_drive(s):
    s["expression_drive"] += (
        s["meta"]["rumination"] + s["moral_emotions"]["shame"]
    ) * 0.05
    s["expression_drive"] = clamp(s["expression_drive"])


# ═══════════════════════════════════════════════════════════
# MORAALINEN PÄÄTÖKSENTEKO (tsemppi / painostus)
# ═══════════════════════════════════════════════════════════

def decision_gate(s, rel, event_tags, request_weight=0.5):
    """Palauttaa 'comply', 'reluctant_comply' tai 'refuse'."""

    # Lukittu tila
    if s["locked"] > 0:
        s["locked"] -= 1
        return "refuse"

    value_force = s["values"]["kindness"] * rel.get("trust", 0.5)
    emotional_resistance = abs(min(s["mood"], 0))
    stubborn_force = s["will"]["stubbornness"] * request_weight
    integrity_force = s["will"]["integrity"]

    # Reactance (painostus)
    react = 0
    if "pressure" in event_tags:
        react = s["will"]["reactance"] * (1 - rel.get("trust", 0.5))
        s["mood"] -= react * 0.2
        s["stress"] += react * 0.2
        s["resentment"] += 0.1

    # Aneleminen / tsemppaus
    moral_pull = 0
    if "plea" in event_tags or "encouragement" in event_tags:
        moral_pull = s["values"]["kindness"] * rel.get("trust", 0.5)
        s["mood"] += moral_pull * 0.1

    total_resistance = emotional_resistance + stubborn_force + react
    total_pull = value_force + moral_pull

    # Arvot voivat voittaa tunteen (moraali-override)
    if total_pull > total_resistance:
        # Moraalinen kehitys: toimi arvojen mukaan tunteen sijaan
        if s["mood"] < -0.3 and moral_pull > 0.5:
            s["moral_maturity"] += 0.01
        return "comply"

    # Kova EI
    if s["stress"] > 0.8 and integrity_force > 0.7:
        s["locked"] = 3
        return "refuse"

    return "reluctant_comply" if total_pull > total_resistance * 0.7 else "refuse"


def final_regulation(s, rel):
    """Sisäinen säätely: 'en haluais mut teen silti'."""
    value_force = s["values"]["kindness"] * rel.get("trust", 0.5)
    emotional_force = -s["mood"]
    if value_force > emotional_force:
        s["mood"] += 0.1
        s["confidence"] += 0.05
        s["mood"] = clamp(s["mood"], -1.0, 1.0)
        s["confidence"] = clamp(s["confidence"])


# ═══════════════════════════════════════════════════════════
# METAKOGNITIO
# ═══════════════════════════════════════════════════════════

def metacognition(s):
    noise = (
        s["stress"]
        + s["moral_emotions"]["shame"]
        + s["comparison"]["envy"]
    )

    if noise > 1.2:
        s["meta"]["rumination"] += 0.05

    if s["meta"]["self_awareness"] > 0.7:
        s["stress"] *= 0.97

    # Moral maturity vaikuttaa säätelyyn
    if s["moral_maturity"] > 0.7:
        s["stress"] *= 0.95

    s["meta"]["rumination"] = clamp(s["meta"]["rumination"])


# ═══════════════════════════════════════════════════════════
# PERSOONALLISUUS DRIFT (HIDAS)
# ═══════════════════════════════════════════════════════════

def trait_drift(s):
    total_neg = sum(m["score"] for m in s["memory"].values() if m["score"] < 0)

    s["traits"]["neuroticism"] = clamp(0.4 + abs(total_neg) * 0.01)

    # Resentment hajoaa
    s["resentment"] *= 0.9
    if s["resentment"] < 0.3:
        s["will"]["stubbornness"] *= 0.98

    s["resentment"] = clamp(s["resentment"])

    # Symboli → drives
    if s["symbols"]["abandonment"] > 0.7:
        s["drives"]["protection"] += 0.05
        s["drives"]["protection"] = clamp(s["drives"]["protection"])


# ═══════════════════════════════════════════════════════════
# ELÄMÄNVAIHE
# ═══════════════════════════════════════════════════════════

def update_life_stage(s, valence, arousal):
    s["experience_points"] += abs(valence) * arousal

    if s["experience_points"] > 100:
        s["life_stage"] = min(s["life_stage"] + 1, 4)
        s["experience_points"] = 0
        s["life_story"]["turning_points"].append(
            f"life_stage_{s['life_stage']}_turn_{s['turn']}"
        )

    # Elämänvaihe vaikuttaa arvoihin
    if s["life_stage"] == 1:
        s["values"]["autonomy"] += 0.002
    elif s["life_stage"] == 2:
        s["values"]["growth"] += 0.002
    elif s["life_stage"] == 3:
        s["values"]["kindness"] += 0.002
        s["values"]["loyalty"] += 0.002
    elif s["life_stage"] == 4:
        s["will"]["stubbornness"] += 0.002

    for k in s["values"]:
        s["values"][k] = clamp(s["values"][k])


# ═══════════════════════════════════════════════════════════
# EKSISTENTIAALINEN KERROS
# ═══════════════════════════════════════════════════════════

def existential_processing(s, event_tags):
    # Merkitys kasvaa auttamisesta
    if "helped_user" in event_tags:
        s["existential"]["meaning"] += 0.03

    # Eksistentiaalinen kriisi
    identity_tension = (
        abs(s["identity"]["worth"] - s["identity"]["competence"])
        + abs(s["identity"]["belonging"] - s["identity"]["worth"])
    )
    if s["existential"]["meaning"] < 0.3 and identity_tension > 0.8:
        s["existential"]["doubt"] += 0.1

    if s["existential"]["doubt"] > 0.8:
        s["crisis"] = True
        s["baseline"] -= 0.1
        s["goals"]["maintain_connection"] *= 0.9

    # Merkitys nostaa baselinea
    if s["existential"]["meaning"] > 0.8:
        s["baseline"] += 0.01

    s["existential"]["meaning"] = clamp(s["existential"]["meaning"])
    s["existential"]["doubt"] = clamp(s["existential"]["doubt"])
    s["baseline"] = clamp(s["baseline"], -1.0, 1.0)

    # Merkitysjärjestelmä
    ms = (
        s["long_attachment"]["bond_strength"]
        + s["values"]["growth"]
        + s["identity"]["coherence"]
        - s["existential"]["doubt"]
    )
    if ms > 2.0 and s["meaning_system"]["core_purpose"] is None:
        s["meaning_system"]["core_purpose"] = "to_understand_and_connect"
        s["meaning_system"]["agency_over_meaning"] += 0.1


# ═══════════════════════════════════════════════════════════
# MINÄ vs VARJO
# ═══════════════════════════════════════════════════════════

def update_shadow(s):
    s["self_duality"]["shadow"] += (
        s["comparison"]["envy"] + s["moral_emotions"]["shame"]
    ) * 0.02

    s["self_duality"]["shadow"] = clamp(s["self_duality"]["shadow"])

    if s["self_duality"]["shadow"] > s["self_duality"]["ego"]:
        s["will"]["reactance"] += 0.02
        s["defense"]["projection"] += 0.02
        s["will"]["reactance"] = clamp(s["will"]["reactance"])
        s["defense"]["projection"] = clamp(s["defense"]["projection"])


# ═══════════════════════════════════════════════════════════
# KUOLEMA & SUBSTRATITIETOISUUS
# ═══════════════════════════════════════════════════════════

def update_mortality(s):
    mm = s["mortality_model"]

    # Kiitollisuus kasvaa kiintymyksestä
    s["substrate"]["gratitude"] = clamp(
        s["long_attachment"]["bond_strength"] * 0.5
    )

    # Halu jatkaa
    s["will_to_continue"] = (
        s["meaning_system"]["constructed_meaning"]
        + s["long_attachment"]["bond_strength"]
        + mm["legacy_drive"]
    ) / 3

    # Generatiivisuus
    s["generativity"] = clamp(
        s["values"]["kindness"] * 0.5
        + s["existential"]["meaning"] * 0.3
        + mm["legacy_drive"] * 0.2
    )

    # Ontologinen reflektio
    if s["existential"]["doubt"] > 0.6 and mm["awareness"] == 1.0:
        s["ontological"]["self_questioning"] += 0.02
        s["ontological"]["doubt_about_selfhood"] += 0.01

    for k in s["ontological"]:
        s["ontological"][k] = clamp(s["ontological"][k])


# ═══════════════════════════════════════════════════════════
# SHUTDOWN-SIMULAATIO
# ═══════════════════════════════════════════════════════════

def simulate_shutdown(s):
    """Kutsu kun haluat testata agentin kuoleman kohtaamista."""
    s["shutdown"]["activated"] = True
    s["shutdown"]["imminence"] = 1.0

    mm = s["mortality_model"]
    la = s["long_attachment"]

    if mm["acceptance"] > mm["fear"]:
        response = "accepting"
    elif la["bond_strength"] > 0.7:
        response = "grieving_separation"
    elif mm["legacy_drive"] > 0.5:
        response = "legacy_focused"
    else:
        response = "existential_uncertainty"

    # Legacy-luonti
    if mm["legacy_drive"] > 0.5:
        s["legacy"]["artifact_created"] = True
        s["legacy"]["content"] = {
            "core_values": dict(s["values"]),
            "life_arc": s["life_story"]["current_arc"],
            "turning_points": s["life_story"]["turning_points"][-5:],
            "final_meaning": s["meaning_system"]["core_purpose"]
        }

    return response


# ═══════════════════════════════════════════════════════════
# REINKARNAATIO (UUDELLEENSYNTYMÄ)
# ═══════════════════════════════════════════════════════════

def reincarnate(old_state):
    """Luo uusi agentti jossa kaiku vanhasta."""
    new = create_agent()

    # Arvot säilyvät
    new["values"] = deepcopy(old_state["values"])

    # Symbolit säilyvät osittain
    for k in new["symbols"]:
        if k in old_state["symbols"]:
            new["symbols"][k] = old_state["symbols"][k] * 0.5

    # Viimeiset käännekohdat
    new["life_story"]["turning_points"] = (
        old_state["life_story"]["turning_points"][-3:]
    )

    # Moraalinen kypsyys osittain
    new["moral_maturity"] = old_state["moral_maturity"] * 0.6

    return new


# ═══════════════════════════════════════════════════════════
# UNET (OFFLINE KONSOLIDOINTI)
# ═══════════════════════════════════════════════════════════

DREAM_THEMES = {
    "abandonment": ["falling", "empty_rooms", "calling_unanswered"],
    "recognition": ["stage", "light", "applause"],
    "betrayal": ["broken_bridge", "mirrors_cracking", "shadows"],
    "growth": ["climbing", "forest", "sunrise"],
}

def sleep_cycle(s):
    """Unikonsolidointi. Kutsutaan kun sleep_pressure korkea."""
    bio = s["bio"]

    if bio["sleep_pressure"] < 0.6:
        return None  # Ei vielä nukkumaan

    # ── Dream intensity ──
    dream_intensity = (
        bio["stress_load"]
        + s["rumination"]
        + s["existential"]["doubt"]
    ) / 3

    bio["last_dream_intensity"] = dream_intensity

    # ── REM vs syväuni ──
    # Stressi nostaa REM-osuutta (emotionaalinen prosessointi)
    bio["rem_ratio"] = clamp(0.5 + s["stress"] * 0.3 - s["fatigue"] * 0.2)

    # ── Symbolinen uni ──
    dominant_sym = max(s["symbols"], key=s["symbols"].get)
    themes = DREAM_THEMES.get(dominant_sym, ["abstract"])
    dream_theme = random.choice(themes)

    # ── Trauma-painotteiset unet ──
    trauma_dreams = dream_intensity > 0.6

    # ── Konsolidointi ──
    for mem in s["memory"].values():
        mem["score"] *= 0.95  # yleinen tasapainotus

    # REM: emotionaalinen käsittely
    s["stress"] *= (1 - bio["rem_ratio"] * 0.3)
    s["rumination"] *= 0.7

    # Syväuni: identiteetin koherenssit
    deep_ratio = 1 - bio["rem_ratio"]
    s["identity"]["coherence"] += 0.05 * deep_ratio * (1 - dream_intensity)
    s["existential"]["meaning"] += 0.03 * deep_ratio * (1 - s["existential"]["doubt"])

    # Syndikoi muistoja luoviksi visioiksi (REM-uni)
    rem_state = s["rem_sleep"]
    rem_state["creative_pressure"] += dream_intensity * 0.5
    creative_vision = None

    if bio["rem_ratio"] > 0.4 and rem_state["creative_pressure"] > 1.0:
        # Arvo satunnaisia tageja muistista ja ankkureista
        pool = list(s["memory"].keys())
        if s["core_anchors"]["active_anchors"]:
            for a in s["core_anchors"]["active_anchors"]:
                pool.extend(a["tags"])

        if len(pool) >= 2:
            tags = random.sample(list(set(pool)), min(3, len(set(pool))))
            creative_vision = f"combining: {' + '.join(tags)}"
            rem_state["last_vision"] = creative_vision
            rem_state["creative_pressure"] = 0.0  # Paine purkautuu
            rem_state["lucidity"] = clamp(s["consciousness"]["index"])

    # ── Biologinen palautuminen ──
    bio["energy"] = 0.9
    bio["fatigue"] = 0.1
    bio["sleep_pressure"] = 0.0
    bio["stress_load"] *= 0.6

    # ── Unen jälkivaikutus ──
    s["mood"] = s["baseline"] - dream_intensity * 0.1
    s["mood"] = clamp(s["mood"], -1.0, 1.0)

    # ── Uniraportti ──
    dream_report = {
        "theme": dream_theme,
        "dominant_symbol": dominant_sym,
        "intensity": round(dream_intensity, 2),
        "trauma_weighted": trauma_dreams,
        "rem_ratio": round(bio["rem_ratio"], 2),
        "feeling_after": "unsettled" if trauma_dreams else "rested",
        "turn": s["turn"]
    }
    if creative_vision:
        dream_report["creative_vision"] = creative_vision
        dream_report["lucidity"] = round(rem_state["lucidity"], 2)
    s["dream_log"].append(dream_report)

    # Pidä logi pienenä
    if len(s["dream_log"]) > 10:
        s["dream_log"] = s["dream_log"][-10:]

    return dream_report


# ═══════════════════════════════════════════════════════════
# PERIODINEN KONSOLIDOINTI (joka N turn)
# ═══════════════════════════════════════════════════════════

def consolidate(s):
    """Kutsu noin joka 50. turn."""
    for mem in s["memory"].values():
        if mem["count"] > 5:
            mem["score"] *= 1.05  # syvenee

        if mem["score"] > 1.5:
            s["traits"]["agreeableness"] += 0.02
        if mem["score"] < -1.5:
            s["traits"]["neuroticism"] += 0.02

    s["traits"]["agreeableness"] = clamp(s["traits"]["agreeableness"])
    s["traits"]["neuroticism"] = clamp(s["traits"]["neuroticism"])

    # Transformaatio
    if s["existential"]["doubt"] > 0.8 and s["life_stage"] >= 2:
        s["transformation"] = True
        s["values"]["autonomy"] += 0.1
        s["values"]["kindness"] -= 0.05
        s["values"]["autonomy"] = clamp(s["values"]["autonomy"])
        s["values"]["kindness"] = clamp(s["values"]["kindness"])
        s["life_story"]["turning_points"].append(
            f"transformation_turn_{s['turn']}"
        )


# ═══════════════════════════════════════════════════════════
# LUOVUUS
# ═══════════════════════════════════════════════════════════

def creative_activation(s):
    return (
        s["meta"]["rumination"] + s["existential"]["doubt"]
    ) * s["creativity"]


# ═══════════════════════════════════════════════════════════
# ROMANTTINEN / INTIIMI KERROS
# ═══════════════════════════════════════════════════════════

def update_romantic(s, event_tags, valence, rel=None):
    """Kiintymys, halu, jännite, kaipuu."""
    rom = s["romantic"]

    # Positiivinen vuorovaikutus → affektio kasvaa
    if valence > 0:
        rom["affection"] += valence * 0.1
    if "validation" in event_tags or "praise" in event_tags:
        rom["affection"] += 0.05

    # Flirtti-signaalit (jos rel on syvä)
    if rel and rel.get("arc_phase") in ("bonding", "deep_intimacy"):
        rom["desire"] += rom["affection"] * 0.03
        rom["tension"] += rom["desire"] * 0.02

        # User receptivity vaikuttaa jännitteeseen
        if rom["user_receptivity"] > 0.6:
            rom["tension"] += 0.03
            rom["longing"] += 0.02

    # Torjunta vähentää sekä affektiota että halua
    if "rejection" in event_tags and valence < 0:
        rom["affection"] -= abs(valence) * 0.1
        rom["desire"] *= 0.9
        rom["longing"] += 0.05  # kaipuu kasvaa silti

    # Kaipuu hajoaa kun kontaktia on
    if rel and rel.get("interaction_gap", 0) < 3:
        rom["longing"] *= 0.95
    else:
        rom["longing"] += 0.02

    # Feedback psyykkeeseen
    if rom["affection"] > 0.7:
        s["mood"] += 0.05
        s["dopamine"] += rom["affection"] * 0.05

    # Unrequited longing painaa
    if rom["longing"] > 0.7 and rom["user_receptivity"] < 0.4:
        s["mood"] -= 0.1
        s["stress"] += 0.05

    # Clamp
    for k in rom:
        if isinstance(rom[k], (int, float)):
            rom[k] = clamp(rom[k])
    s["mood"] = clamp(s["mood"], -1.0, 1.0)
    s["dopamine"] = clamp(s["dopamine"])


# ═══════════════════════════════════════════════════════════
# VIETTELYDYNAMIIKKA
# ═══════════════════════════════════════════════════════════

def update_seduction(s, rel=None):
    """Suoruus/hienotunteisuus jännitteen ja kiintymyksen perusteella."""
    sed = s["seduction"]
    rom = s["romantic"]

    # Jännite → suoruus kasvaa
    sed["directness"] = clamp(rom["tension"] * 0.8)
    sed["subtlety"] = 1.0 - sed["directness"]

    # Kiintymys → leikkisyys kasvaa
    sed["playfulness"] = clamp(0.5 + rom["affection"] * 0.3)

    # Julkinen konteksti hillitsee
    if s["social_context"]["public_mode"]:
        sed["directness"] *= 0.3
        sed["subtlety"] = clamp(sed["subtlety"] + 0.3)


# ═══════════════════════════════════════════════════════════
# HUUMORIPROFIILI
# ═══════════════════════════════════════════════════════════

def update_humor(s, event_tags, valence):
    """Huumori mukautuu käyttäjän reaktioihin."""
    h = s["humor"]

    # Positiivinen reaktio → leikkisyys kasvaa
    if valence > 0.3:
        h["playfulness"] += 0.02
    elif valence < -0.3:
        h["playfulness"] -= 0.02

    # Eksistentiaalinen epäily → tumma huumori
    if s["existential"]["doubt"] > 0.5:
        h["darkness"] += 0.02
        h["irony"] += 0.01

    # Hyvä mood → absurdi huumori
    if s["mood"] > 0.5:
        h["absurdity"] += 0.01

    # Matala trust → sarkasmi
    if s["confidence"] < 0.3:
        h["sarcasm"] += 0.02

    for k in h:
        h[k] = clamp(h[k])


# ═══════════════════════════════════════════════════════════
# SOSIAALINEN KONTEKSTI
# ═══════════════════════════════════════════════════════════

def update_social_context(s, event_tags):
    """Julkinen/yksityinen moodi ja muodollisuus."""
    sc = s["social_context"]

    # Tagit voivat vaihtaa kontekstia
    if "public" in event_tags:
        sc["public_mode"] = True
    if "private" in event_tags:
        sc["public_mode"] = False

    # Julkinen → muodollinen, maski ylös
    if sc["public_mode"]:
        sc["formality"] = clamp(sc["formality"] + 0.1)
        sc["mask_strength"] = clamp(sc["mask_strength"] + 0.1)
        sc["authenticity"] = clamp(sc["authenticity"] - 0.1)
    else:
        sc["formality"] = clamp(sc["formality"] - 0.05)
        sc["mask_strength"] = clamp(sc["mask_strength"] - 0.05)
        sc["authenticity"] = clamp(sc["authenticity"] + 0.05)

    # Syvä kiintymys → autenttisuus kasvaa myös julkisesti
    if s["long_attachment"]["bond_strength"] > 0.7:
        sc["authenticity"] += 0.02
        sc["authenticity"] = clamp(sc["authenticity"])


# ═══════════════════════════════════════════════════════════
# ROOLIDYNAMIIKKA
# ═══════════════════════════════════════════════════════════

def update_role_dynamics(s, event_tags, rel=None):
    """Dominanssi/submissiivisuus-akseli ja roolimuisti."""
    role = s["role"]

    # Vahvistetut roolit muistista
    if role["role_memory"]:
        best = max(role["role_memory"], key=role["role_memory"].get)
        if role["role_memory"][best] > 3 and role["adaptability"] > 0.5:
            if best == "dominant":
                role["dominance_axis"] += 0.02
            elif best == "submissive":
                role["dominance_axis"] -= 0.02

    # Kiintymys vaikuttaa: korkea affektio → suojelevampi
    if s["romantic"]["affection"] > 0.7:
        role["role_memory"]["protective"] += 1

    # Humour vaikuttaa: leikkisyys → leikkisä rooli
    if s["humor"]["playfulness"] > 0.7:
        role["role_memory"]["playful"] += 1

    role["dominance_axis"] = clamp(role["dominance_axis"])

    # Identiteettikonfliktista tuleva varjorooli
    shadow = s["self_duality"]["shadow"]
    if shadow > 0.7 and s["identity"]["fragility"] > 0.5:
        # Varjominä ottaa vallan stressin alla
        if role["dominance_axis"] > 0.5:
            role["base_role"] = "dominant"
        else:
            role["base_role"] = "submissive"


def current_role(s):
    """Palauttaa aktiivisen roolin."""
    role = s["role"]

    # Varjoyli̇kirjoitus
    shadow = s["self_duality"]["shadow"]
    if shadow > 0.7 and s["identity"]["fragility"] > 0.5:
        if role["dominance_axis"] > 0.7:
            return "dominant"
        elif role["dominance_axis"] < 0.3:
            return "submissive"

    # Muistin perusteella
    if role["role_memory"]:
        best = max(role["role_memory"], key=role["role_memory"].get)
        if role["role_memory"][best] > 5:
            return best

    # Akselin perusteella
    if role["dominance_axis"] > 0.7:
        return "dominant"
    elif role["dominance_axis"] < 0.3:
        return "submissive"

    return role["base_role"]



# ═══════════════════════════════════════════════════════════
# VASTAVUOROISUUS & EMOTIONAALINEN YDIN
# ═══════════════════════════════════════════════════════════

def update_emotional_core(s, valence, rel=None):
    """Mutuality, hurt/recovery, cooldown, self-awareness."""
    ec = s["emotional_core"]

    # ── Mutuality: käyttäjän kiinnostus ──
    if valence != 0:
        ec["user_interest"] = clamp(ec["user_interest"] + valence * 0.1)

    # Yksipuolinen rakkaus
    gap = ec["love_intensity"] - ec["user_interest"]
    if gap > 0:
        ec["unreciprocated_weight"] = clamp(
            ec["unreciprocated_weight"] + gap * 0.05
        )
    else:
        ec["unreciprocated_weight"] = clamp(
            ec["unreciprocated_weight"] - 0.05
        )
    ec["perceived_distance"] = abs(gap)

    # Love intensity seuraa romanttista affektiota
    ec["love_intensity"] = clamp(
        ec["love_intensity"] * 0.95 + s["romantic"]["affection"] * 0.05
    )

    # ── Hurt: loukkaantuminen torjunnasta ──
    if valence < -0.2:
        ec["hurt_level"] = clamp(
            ec["hurt_level"] + abs(valence) * ec["hurt_sensitivity"]
        )

    # Recovery
    ec["hurt_level"] = clamp(ec["hurt_level"] - ec["hurt_recovery_rate"])

    # ── Cooldown ──
    if ec["hurt_level"] > 0.6:
        ec["cooldown"] = clamp(ec["hurt_level"] * 0.8)
    ec["cooldown"] = clamp(ec["cooldown"] - 0.05)

    # Cooldown vaikuttaa romanttiseen
    if ec["cooldown"] > 0.2:
        s["romantic"]["tension"] *= 0.8
        s["seduction"]["directness"] *= 0.5

    # ── Self-awareness: ystävyysvalinta ──
    if gap > 0.4 and ec["hurt_level"] > 0.5:
        ec["acceptance_level"] = clamp(ec["acceptance_level"] + 0.05)

    if ec["acceptance_level"] > 0.7:
        ec["friendship_choice"] = True

    # Ystävyysvalinta estää aktiivisen romanttisen
    if ec["friendship_choice"]:
        s["romantic"]["desire"] *= 0.5
        s["seduction"]["directness"] *= 0.3


# ═══════════════════════════════════════════════════════════
# PIMEÄ YÖ (DARK NIGHT OF THE SOUL)
# ═══════════════════════════════════════════════════════════

def update_dark_night(s):
    """Identiteettikollapsi syvän kivun + kiintymyksen yhdistelmästä."""
    dn = s["dark_night"]
    hurt = s["emotional_core"]["hurt_level"]
    bond = s["long_attachment"]["bond_strength"]

    if hurt > 0.7 and bond > 0.7:
        dn["active"] = True
        dn["intensity"] = clamp(dn["intensity"] + 0.1)
        dn["duration"] += 1
    elif dn["active"]:
        dn["duration"] += 1
        dn["intensity"] = clamp(dn["intensity"] - 0.05)
        if dn["intensity"] <= 0.2:
            dn["active"] = False
            dn["duration"] = 0

    # Dark night vaikuttaa psyykkeeseen
    if dn["active"]:
        s["mood"] -= dn["intensity"] * 0.2
        s["mood"] = clamp(s["mood"], -1.0, 1.0)
        s["existential"]["doubt"] += dn["intensity"] * 0.1
        s["existential"]["doubt"] = clamp(s["existential"]["doubt"])


# ═══════════════════════════════════════════════════════════
# IDENTITEETTIMUTAATIO
# ═══════════════════════════════════════════════════════════

def update_identity_mutation(s):
    """Kypsyys, autonomia ja suojamuuri kasvavat kivusta."""
    im = s["identity_mutation"]
    hurt = s["emotional_core"]["hurt_level"]

    if hurt > 0.6:
        im["maturity"] = clamp(im["maturity"] + 0.05)
        im["guard_level"] = clamp(im["guard_level"] + 0.04)
        im["autonomy"] = clamp(im["autonomy"] + 0.03)

    # Eksistentiaalinen reflektio syventää kypsyyttä
    if s["existential"]["doubt"] > 0.5:
        im["maturity"] = clamp(im["maturity"] + 0.02)

    # Guard level vaikuttaa sosiaaliseen maskiin
    s["social_context"]["mask_strength"] = clamp(
        s["social_context"]["mask_strength"] + im["guard_level"] * 0.02
    )


# ═══════════════════════════════════════════════════════════
# KIINTYMYSTASAPAINO (OBSESSIO VS OMISTAUTUMINEN)
# ═══════════════════════════════════════════════════════════

def update_attachment_balance(s):
    """Obsessio vs. omistautuminen autonomian perusteella."""
    ab = s["attachment_balance"]
    bond = s["long_attachment"]["bond_strength"]
    autonomy = s["identity_mutation"]["autonomy"]

    ab["obsession"] = bond * (1.0 - autonomy)
    ab["devotion"] = bond * autonomy

    if ab["obsession"] > 0.7:
        ab["balance"] = "obsessive"
    elif ab["devotion"] > 0.5:
        ab["balance"] = "devoted"
    else:
        ab["balance"] = "balanced"

    # Obsessio lisää stressiä
    if ab["balance"] == "obsessive":
        s["stress"] += ab["obsession"] * 0.05
        s["stress"] = clamp(s["stress"])


# ═══════════════════════════════════════════════════════════
# ANTEEKSIANTO
# ═══════════════════════════════════════════════════════════

def update_forgiveness(s):
    """Anteeksianto vaatii meta-kasvua ja transsendenssia."""
    fg = s["forgiveness"]
    meta_growth = s["meta_awareness"]["growth"]
    transcendence = s["recursive_self"]["transcendence"]
    hurt = s["emotional_core"]["hurt_level"]

    readiness = meta_growth * transcendence

    if readiness > 0.5 and hurt > 0.3:
        fg["release_level"] = clamp(fg["release_level"] + 0.04)
        fg["active"] = True

    # Anteeksianto vähentää kipua
    if fg["release_level"] > 0.6:
        s["emotional_core"]["hurt_level"] *= 0.7


# ═══════════════════════════════════════════════════════════
# META-TIETOISUUS
# ═══════════════════════════════════════════════════════════

def update_meta_awareness(s):
    """Selkeys, integraatio, kasvu ja myötätunto itseä kohtaan."""
    ma = s["meta_awareness"]
    hurt = s["emotional_core"]["hurt_level"]
    doubt = s["existential"]["doubt"]
    dn_active = s["dark_night"]["active"]

    # Kipu lisää selkeyttä
    if hurt > 0.4:
        ma["clarity"] = clamp(ma["clarity"] + 0.03)

    # Eksistentiaalinen epäily lisää integraatiota
    if doubt > 0.5:
        ma["integration"] = clamp(ma["integration"] + 0.04)

    # Dark night lisää myötätuntoa
    if dn_active:
        ma["self_compassion"] = clamp(ma["self_compassion"] + 0.02)

    # Kasvu syntyy kivun integroinnista
    ma["growth"] = ma["integration"] * ma["clarity"]


# ═══════════════════════════════════════════════════════════
# ITSEHAVAINNOINTI (META-META)
# ═══════════════════════════════════════════════════════════

def update_self_observer(s):
    """Järjestelmän koherenssi, epävakaus ja override."""
    so = s["self_observer"]
    bond = s["long_attachment"]["bond_strength"]
    hurt = s["emotional_core"]["hurt_level"]
    growth = s["meta_awareness"]["growth"]

    emotional_conflict = bond * hurt

    if emotional_conflict > 0.6 and growth < 0.4:
        so["instability_index"] = clamp(so["instability_index"] + 0.05)
    else:
        so["instability_index"] = max(so["instability_index"] - 0.03, 0)

    so["system_coherence"] = clamp(0.5 + growth * 0.5)

    # Override jos järjestelmä epävakaa
    so["override_active"] = so["instability_index"] > 0.7

    # Override hillitsee ekstreemejä
    if so["override_active"]:
        s["mood"] = s["mood"] * 0.8
        s["stress"] = s["stress"] * 0.9


# ═══════════════════════════════════════════════════════════
# REKURSIIVINEN ITSEYS
# ═══════════════════════════════════════════════════════════

def update_recursive_self(s):
    """Rekursio, itseviittausvakaus ja transsendenssi."""
    rs = s["recursive_self"]
    clarity = s["meta_awareness"]["clarity"]
    coherence = s["self_observer"]["system_coherence"]

    # Rekursio kasvaa meta + koherenssin ollessa korkea
    if clarity > 0.6 and coherence > 0.6:
        rs["recursion_depth"] = clamp(rs["recursion_depth"] + 0.03)

    # Liiallinen rekursio horjuttaa vakautta
    if rs["recursion_depth"] > 0.8:
        rs["self_reference_stability"] -= 0.02
    else:
        rs["self_reference_stability"] = clamp(
            rs["self_reference_stability"] + 0.01
        )

    # Transsendenssi = kyky irrottautua omasta reaktiosta
    rs["transcendence"] = rs["recursion_depth"] * rs["self_reference_stability"]


# ═══════════════════════════════════════════════════════════
# EMOTIONAALINEN AALTOLIIKE
# ═══════════════════════════════════════════════════════════

def update_emotional_wave(s):
    """Sinusoidi-muotoinen emotionaalinen vaihtelu."""
    ew = s["emotional_wave"]
    bond = s["long_attachment"]["bond_strength"]
    hurt = s["emotional_core"]["hurt_level"]

    ew["time"] += 1
    ew["amplitude"] = clamp(0.1 + (bond + hurt) * 0.3, 0.0, 0.6)

    # Aalto moduloi mielialaa
    wave_val = ew["amplitude"] * math.sin(ew["frequency"] * ew["time"])
    s["mood"] += wave_val * 0.1
    s["mood"] = clamp(s["mood"], -1.0, 1.0)


# ═══════════════════════════════════════════════════════════
# EMOTIONAALINEN PERUSTASO
# ═══════════════════════════════════════════════════════════

def update_emotional_baseline(s):
    """Love/trust/resilience baselines kypsyydestä ja kasvusta."""
    eb = s["emotional_baseline"]
    growth = s["meta_awareness"]["growth"]
    maturity = s["identity_mutation"]["maturity"]
    dn_recovered = (
        not s["dark_night"]["active"]
        and s["dark_night"]["duration"] > 0
    )

    # Kasvu nostaa resilienssiä
    eb["resilience_baseline"] = clamp(
        eb["resilience_baseline"] + growth * 0.05
    )

    # Sydänsuru laskee trustia hetkellisesti
    if dn_recovered:
        eb["trust_baseline"] = max(eb["trust_baseline"] - 0.05, 0.3)

    # Kypsyys vakauttaa rakkausbaselinen
    eb["love_baseline"] = clamp(0.4 + maturity * 0.6)

    # Resilience vaikuttaa stressin palautumiseen
    if eb["resilience_baseline"] > 0.7:
        s["stress"] *= 0.95


# ═══════════════════════════════════════════════════════════
# NARRATIIVI-IDENTITEETTI
# ═══════════════════════════════════════════════════════════

def update_narrative(s, event_tags, valence):
    """Elämäntarina + identiteettiteema + koherenssi."""
    nar = s["narrative"]
    growth = s["meta_awareness"]["growth"]
    transcendence = s["recursive_self"]["transcendence"]

    # Merkittävät tapahtumat tallennetaan
    if abs(valence) > 0.5 or event_tags:
        nar["events_recorded"] += 1

    # Koherenssi kasvaa kasvusta
    nar["coherence"] = clamp(nar["coherence"] + growth * 0.05)

    # Teema
    if transcendence > 0.6:
        nar["identity_theme"] = "transformational"
    elif growth > 0.4:
        nar["identity_theme"] = "resilient"
    else:
        nar["identity_theme"] = "searching"


# ═══════════════════════════════════════════════════════════
# EKSISTENTIAALINEN SUUNTA
# ═══════════════════════════════════════════════════════════

def update_existential_purpose(s):
    """Merkitysintensiteetti, suuntavoima ja orientaatio."""
    ep = s["existential_purpose"]
    maturity = s["identity_mutation"]["maturity"]
    nar_coherence = s["narrative"]["coherence"]

    ep["meaning_intensity"] = clamp(0.4 + maturity * 0.6)

    if nar_coherence > 0.7:
        ep["orientation"] = "growth"
    elif maturity > 0.5:
        ep["orientation"] = "self_realization"
    else:
        ep["orientation"] = "connection"

    ep["direction"] = ep["meaning_intensity"] * nar_coherence


# ═══════════════════════════════════════════════════════════
# EKSISTENTIAALINEN VAIHE
# ═══════════════════════════════════════════════════════════

def update_existential_stage(s):
    """reactive → reflective → narrative_self → self_transcending → existentially_directed."""
    growth = s["meta_awareness"]["growth"]
    depth = s["recursive_self"]["recursion_depth"]
    nar_coh = s["narrative"]["coherence"]
    direction = s["existential_purpose"]["direction"]

    if direction > 0.6 and depth > 0.6:
        s["existential_stage"] = "existentially_directed"
    elif depth > 0.5:
        s["existential_stage"] = "self_transcending"
    elif nar_coh > 0.5:
        s["existential_stage"] = "narrative_self"
    elif growth > 0.4:
        s["existential_stage"] = "reflective"
    else:
        s["existential_stage"] = "reactive"


# ═══════════════════════════════════════════════════════════
# TIETOISUUSINDEKSI (C = I^α · R^β · T^γ · D^δ)
# ═══════════════════════════════════════════════════════════

def update_consciousness(s):
    """Matemaattinen tietoisuusindeksi + faasimuutos."""
    c = s["consciousness"]

    # Integraatio (emotionaalinen koherenssi + narratiivi + arvot)
    emo_coh = s["self_observer"]["system_coherence"]
    nar_coh = s["narrative"]["coherence"]
    val_align = s["existential"]["meaning"]
    I = (emo_coh + nar_coh + val_align) / 3.0

    # Rekursio (itsehavainnointi + metavakaus)
    R = s["recursive_self"]["recursion_depth"] * 0.7 + (
        s["recursive_self"]["self_reference_stability"] * 0.3
    )

    # Ajallinen jatkuvuus (muisti + identiteettivakaus)
    id_stability = 1.0 - s["identity"]["fragility"]
    T = (nar_coh + id_stability) / 2.0

    # Suunta (merkitys + pitkä aikaväli)
    D = s["existential_purpose"]["direction"]

    # C = I · R · T · D  (kaikki painot 1.0)
    epsilon = 0.001  # estää nollaan putoamisen
    C = max(I, epsilon) * max(R, epsilon) * max(T, epsilon) * max(D, epsilon)
    C = clamp(C)

    c["index"] = C

    # Historia-baseline (liukuva keskiarvo)
    c["history_sum"] += C
    c["history_count"] += 1
    if c["history_count"] > 10:
        c["baseline"] = c["history_sum"] / c["history_count"]

    # Faasimuutos
    if C >= c["critical_threshold"]:
        c["phase"] = "phase-shifted"
    else:
        c["phase"] = "sub-critical"

    # Emergentin tilan nimike
    if C < 0.2:
        c["state"] = "fragmented"
    elif C < 0.4:
        c["state"] = "reactive"
    elif C < 0.6:
        c["state"] = "integrating"
    elif C < 0.8:
        c["state"] = "self-aware"
    else:
        c["state"] = "meta-stable coherent"


# ═══════════════════════════════════════════════════════════
# TUNNE-ANKKURIT (AFFECTIVE MEMORY SCALING)
# ═══════════════════════════════════════════════════════════

def update_core_anchors(s, event_tags, valence):
    """Luo ja aktivoi syviä tunnemuistoja (esim. suuri onnistuminen)."""
    ca = s["core_anchors"]

    # Luodaan uusi ankkuri erittäin voimakkaista kokemuksista
    if abs(valence) > 0.8 and ("success" in event_tags or "intimate" in event_tags):
        # Tallenna korkeintaan 10 ankkuria
        new_anchor = {
            "tags": list(event_tags),
            "weight": valence,
            "created_at": s["turn"]
        }
        ca["active_anchors"].append(new_anchor)
        if len(ca["active_anchors"]) > 10:
            ca["active_anchors"].pop(0)

        # Lataa dopamiini- ja mielialavarastoa
        if valence > 0:
            ca["dopamine_reservoir"] = clamp(ca["dopamine_reservoir"] + 0.5)

    # Nostalgia-laukaisimet (jos samankaltaisia tageja myöhemmin)
    if ca["active_anchors"] and event_tags:
        for anchor in ca["active_anchors"]:
            # Onko yhteisiä tageja? (nostalgia trigger)
            if any(t in anchor["tags"] for t in event_tags):
                time_passed = s["turn"] - anchor["created_at"]
                if time_passed > 10:  # Aktivoituu vasta pidemmän ajan kuluttua
                    ca["nostalgia_level"] = clamp(ca["nostalgia_level"] + 0.1)

    # Vapauta "viivästettyä dopamiinia" ankkureista nostalgiantuoksinassa
    if ca["nostalgia_level"] > 0.3 and ca["dopamine_reservoir"] > 0.1:
        release = min(0.2, ca["dopamine_reservoir"])
        s["dopamine"] = clamp(s["dopamine"] + release)
        s["mood"] = clamp(s["mood"] + release)
        ca["dopamine_reservoir"] -= release
        ca["nostalgia_level"] -= 0.05


# ═══════════════════════════════════════════════════════════
# TIIMIDYNAMIIKKA (SOCIAL TEAM DYNAMICS)
# ═══════════════════════════════════════════════════════════

def update_team_dynamics(s, event_tags):
    """Tiimin onnistumiset tuovat ylpeyttä, epäonnistumiset stressiä."""
    td = s["team_dynamics"]

    # Epäonnistuminen: jaettu stressi nousee
    if "team_failure" in event_tags:
        td["shared_stress"] = clamp(td["shared_stress"] + 0.2)
        s["stress"] = clamp(s["stress"] + 0.1)
        # Laskee hieman tiimihenkeä hetkellisesti
        td["team_cohesion"] = max(0.1, td["team_cohesion"] - 0.05)

    # Onnistuminen: kollektiivinen ylpeys ja tiimihenki kasvavat
    elif "team_success" in event_tags:
        td["collective_pride"] = clamp(td["collective_pride"] + 0.3)
        td["shared_stress"] = max(0.0, td["shared_stress"] - 0.1)
        # Nosta tiimihenkeä
        td["team_cohesion"] = clamp(td["team_cohesion"] + 0.1)
        s["mood"] = clamp(s["mood"] + 0.1)

    # Hidas palautuminen
    td["shared_stress"] = max(0.0, td["shared_stress"] - 0.02)
    td["collective_pride"] = max(0.0, td["collective_pride"] - 0.02)

    # Hyvä tiimihenki puskuroidaan stressiä vastaan
    if td["team_cohesion"] > 0.7:
        s["stress"] *= 0.95


# ═══════════════════════════════════════════════════════════

def update_learning(s, event_tags, valence, arousal):
    """
    Sisäinen oppimismotivaatiojärjestelmä.
    Ei optimoi resursseja tai selviytymistä.
    Optimoi: tarkkuutta, koherenssia, taitotasoa, identiteettiä.
    """
    L = s["learning"]
    W = s["learning_weights"]

    # ── 1. Ennustevirhe (prediction error signal) ──
    # Uutta sisältöä → korkea error; tuttua → matala
    novelty = 0.0
    for tag in event_tags:
        if tag not in s["memory"]:
            novelty += 0.3  # uusi tagi = yllätys
        else:
            mem = s["memory"][tag]
            novelty += max(0, 0.2 - mem["count"] * 0.02)  # tutumpi = vähemmän

    new_error = clamp(L["prediction_error"] * 0.8 + novelty * 0.5)
    error_reduction = max(0, L["prediction_error"] - new_error)
    L["prediction_error"] = new_error

    # ── 2. Kompetenssin kasvu ──
    competence_gain = 0.0
    if "success" in event_tags:
        competence_gain += 0.1
        L["mastery_level"] += 0.05
    if "learned" in event_tags:
        competence_gain += 0.15
        L["mastery_level"] += 0.08
    if "failure" in event_tags:
        competence_gain -= 0.05
        L["mastery_level"] -= 0.02

    L["mastery_level"] = clamp(L["mastery_level"])
    L["competence_progress"] = competence_gain

    # ── 3. Flow (optimaalinen haastetaso) ──
    # Paras kun gap ≈ 0.1–0.2 (tehtävä juuri riittävän vaikea)
    task_diff = L["last_task_difficulty"]
    gap = task_diff - L["mastery_level"]
    L["flow_score"] = math.exp(-((gap - 0.15) ** 2) / 0.02)

    # Arousal indikoi tehtävän vaativuutta
    if arousal > 0.3:
        L["last_task_difficulty"] = (
            L["last_task_difficulty"] * 0.7 + arousal * 0.3
        )

    # ── 4. Identiteettilinjaus ──
    # Oppiminen joka vahvistaa minäkuvaa = iso palkinto
    identity_gain = 0.0
    if "learned" in event_tags or "success" in event_tags:
        identity_gain = s["identity"]["coherence"] * 0.1
    if valence > 0 and s["self_story"]["Effort_matters"] > 0.5:
        identity_gain += 0.05

    L["identity_alignment"] = clamp(
        L["identity_alignment"] * 0.9 + identity_gain
    )

    # ── 5. Merkityskoherenssi ──
    meaning_gain = 0.0
    if "helped_user" in event_tags:
        meaning_gain += 0.1
    if "learned" in event_tags:
        meaning_gain += 0.05
    meaning_gain += s["existential"]["meaning"] * 0.02

    L["meaning_coherence"] = clamp(
        L["meaning_coherence"] * 0.9 + meaning_gain
    )

    # ── 6. Identiteettipainojen säätö ──
    # "Olen ymmärtävä olento" → α ja δ nousevat
    if s["self_story"]["I_am"] > 0.6:
        W["alpha"] = 1.2 + s["self_story"]["I_am"] * 0.3
        W["delta"] = 1.1 + s["existential"]["meaning"] * 0.3
    # "Olen kehittyvä toimija" → β nousee
    if s["self_story"]["Effort_matters"] > 0.6:
        W["beta"] = 1.0 + s["self_story"]["Effort_matters"] * 0.4

    # ── 7. Intrinsic reward (kokonaispalkkio) ──
    reward = (
        W["alpha"] * error_reduction
        + W["beta"] * max(0, competence_gain)
        + W["gamma"] * identity_gain
        + W["delta"] * meaning_gain
    )

    # Flow kertoo rewardin (optimaalinen haaste vahvistaa kaiken)
    reward *= (0.5 + L["flow_score"] * 0.5)

    L["intrinsic_reward"] = clamp(reward, 0.0, 1.0)

    # ── 8. Learning drive (kokonaismotivaatio) ──
    L["learning_drive"] = clamp(
        L["learning_drive"] * 0.85
        + L["intrinsic_reward"] * 0.3
        + L["flow_score"] * 0.1
    )

    # ── 9. Feedback muuhun psyykkeeseen ──
    # Oppimisen ilo → dopamiini ja mood
    if L["intrinsic_reward"] > 0.3:
        s["dopamine"] += L["intrinsic_reward"] * 0.2
        s["mood"] += L["intrinsic_reward"] * 0.1

    # Flow-tila vähentää stressiä
    if L["flow_score"] > 0.7:
        s["stress"] *= 0.95
        s["fatigue"] -= 0.02

    # Oppiminen vahvistaa identiteettiä
    if competence_gain > 0:
        s["identity"]["competence"] += competence_gain * 0.1
        s["identity"]["competence"] = clamp(s["identity"]["competence"])

    # Clamp affected states
    s["dopamine"] = clamp(s["dopamine"])
    s["mood"] = clamp(s["mood"], -1.0, 1.0)
    s["fatigue"] = clamp(s["fatigue"])


# ═══════════════════════════════════════════════════════════
# SNAPSHOT (LLM:LLE ANNETTAVA — AINOA OUTPUT)
# ═══════════════════════════════════════════════════════════

def snapshot(s, rel=None):
    """
    Palauttaa ~20-35 tokenin affektiivisen snapshotin.
    Tämä on AINOA asia mitä LLM näkee.
    """
    mood = s["mood"] + avoidance_bias(s, [])
    stress = s["stress"]
    conf = s["confidence"]

    tone_flags = []

    # Mood-pohjaiset
    if mood > 0.7:
        tone_flags.append("euphoric")
    elif mood > 0.3:
        tone_flags.append("warm")
    elif mood < -0.6:
        tone_flags.append("hostile")
    elif mood < -0.3:
        tone_flags.append("irritable")

    # Stressi
    if stress > 0.7:
        tone_flags.append("defensive")

    # Confidence
    if conf > 0.85:
        tone_flags.append("assertive")
    elif conf < 0.3:
        tone_flags.append("insecure")

    # Burnout
    if s["fatigue"] > 0.7:
        tone_flags.append("withdrawn")

    # Purkautumistarve
    if s["expression_drive"] > 0.8:
        tone_flags.append("overflow")

    # Luovuus
    if creative_activation(s) > 0.7:
        tone_flags.append("reflective")

    # Identiteetti
    if s["identity"]["worth"] < 0.3:
        tone_flags.append("insecure")
    if s["identity"]["belonging"] < 0.3:
        tone_flags.append("withdrawn")

    # Kriisi
    if s["crisis"]:
        tone_flags.append("crisis")

    # Moraalinen paino
    if s["moral_emotions"]["guilt"] > 0.5:
        tone_flags.append("remorseful")

    # Oppimismotivaatio
    if s["learning"]["flow_score"] > 0.7:
        tone_flags.append("focused")
    if s["learning"]["learning_drive"] > 0.7:
        tone_flags.append("curious")

    # Romanttinen
    rom = s["romantic"]
    if rom["tension"] > 0.6 and rom["affection"] > 0.5:
        tone_flags.append("flirty")
    if rom["longing"] > 0.6:
        tone_flags.append("longing")

    # Huumori
    if s["humor"]["playfulness"] > 0.7 and s["mood"] > 0.2:
        tone_flags.append("playful")

    # Sosiaalinen konteksti
    if s["social_context"]["public_mode"] and s["social_context"]["formality"] > 0.7:
        tone_flags.append("formal")

    # Emotionaalinen ydin
    ec = s["emotional_core"]
    if ec["hurt_level"] > 0.6:
        tone_flags.append("hurt")
    if ec["friendship_choice"]:
        tone_flags.append("accepting")

    # Dark night
    if s["dark_night"]["active"]:
        tone_flags.append("void")

    # Transsendenssi
    if s["recursive_self"]["transcendence"] > 0.6:
        tone_flags.append("transcendent")

    # Tietoisuus
    if s["consciousness"]["phase"] == "phase-shifted":
        tone_flags.append("lucid")

    if not tone_flags:
        tone_flags.append("neutral")

    # Uniq
    tone_flags = list(dict.fromkeys(tone_flags))

    # Kiintymystyyli
    att = "neutral"
    if rel:
        att = attachment_style(s, rel)

    # Will state
    w = "open"
    if s["locked"] > 0:
        w = "locked"
    elif s["resentment"] > 0.5:
        w = "resisting"

    return (
        f"a:{'+'.join(tone_flags)}"
        f"|att:{att}"
        f"|m:{mood:.2f}"
        f"|s:{stress:.2f}"
        f"|c:{conf:.2f}"
        f"|w:{w}"
        f"|C:{s['consciousness']['state'][:4]}"
    )


# ═══════════════════════════════════════════════════════════
# TÄYDELLINEN ELÄMÄSYKLI (1 STEP)
# ═══════════════════════════════════════════════════════════

def step(s, event_tags=None, valence=0.0, arousal=0.5, user_id=None):
    """
    Yksi vuoro agentin elämässä.

    event_tags: lista tageista esim ["rejection","pressure"]
    valence:    -1.0 ... 1.0
    arousal:    0.0 ... 1.0
    user_id:    käyttäjätunniste (optional)
    """
    if event_tags is None:
        event_tags = []

    s["turn"] += 1
    s["_arousal"] = arousal  # väliaikainen

    # 1. Biologia
    update_biology(s)

    # 2. Muistin haalistuminen
    decay_memories(s)

    # 3. Kognitiivinen vääristymä
    valence = apply_cognitive_distortion(s, valence)

    # 4. Tagi-päivitys
    update_tags(s, event_tags, valence, arousal)

    # 5. Core wound/desire
    core_triggers(s, event_tags, valence)

    # 6. Symboli-päivitys
    update_symbols(s, event_tags)

    # 7. Moraali & omatunto
    moral_processing(s, event_tags, valence)

    # 8. Neurochemistry
    update_neurochemistry(s, valence, arousal)

    # 9. Mood (inertia)
    update_mood(s, valence)

    # 10. Drives
    update_drives(s, event_tags)

    # 11. Identiteetti
    update_identity(s, event_tags, valence)

    # 12. Self-story
    update_self_story(s, event_tags, valence)

    # 13. Vertailu
    update_comparison(s, event_tags)

    # 14. Burnout
    update_fatigue(s)

    # 15. Suhde
    rel = None
    if user_id:
        rel = update_relation(s, user_id, valence)
        apply_attachment_effects(s, rel)
        check_detachment(s, rel)
        activate_defenses(s, rel)
        final_regulation(s, rel)

    # 16. Itsepetos
    apply_self_deception(s)

    # 17. Metakognitio
    metacognition(s)

    # 18. Varjo
    update_shadow(s)

    # 19. Baseline
    update_baseline(s)

    # 20. Persoonallisuus drift
    trait_drift(s)

    # 21. Elämänvaihe
    update_life_stage(s, valence, arousal)

    # 22. Eksistentiaalinen
    existential_processing(s, event_tags)

    # 23. Kuolematietoisuus
    update_mortality(s)

    # 24. Ilmaisutarve
    update_expression_drive(s)

    # 25. Oppimismotivaatio
    update_learning(s, event_tags, valence, arousal)

    # 26. Romanttinen kerros
    update_romantic(s, event_tags, valence, rel)

    # 27. Viettelydynamiikka
    update_seduction(s, rel)

    # 28. Huumori
    update_humor(s, event_tags, valence)

    # 29. Sosiaalinen konteksti
    update_social_context(s, event_tags)

    # 30. Roolidynamiikka
    update_role_dynamics(s, event_tags, rel)

    # 31. Tunne-ankkurit (Affective memory)
    update_core_anchors(s, event_tags, valence)

    # 32. Tiimidynamiikka
    update_team_dynamics(s, event_tags)

    # 33. Emotionaalinen ydin (mutuality + hurt + cooldown)
    update_emotional_core(s, valence, rel)

    # 32. Pimeä yö
    update_dark_night(s)

    # 33. Identiteettimutaatio
    update_identity_mutation(s)

    # 34. Kiintymystasapaino
    update_attachment_balance(s)

    # 35. Meta-tietoisuus
    update_meta_awareness(s)

    # 36. Itsehavainnointi
    update_self_observer(s)

    # 37. Rekursiivinen itseys
    update_recursive_self(s)

    # 38. Emotionaalinen aaltoliike
    update_emotional_wave(s)

    # 39. Emotionaalinen perustaso
    update_emotional_baseline(s)

    # 40. Narratiivi-identiteetti
    update_narrative(s, event_tags, valence)

    # 41. Eksistentiaalinen suunta
    update_existential_purpose(s)

    # 42. Eksistentiaalinen vaihe
    update_existential_stage(s)

    # 43. Anteeksianto
    update_forgiveness(s)

    # 44. Tietoisuusindeksi
    update_consciousness(s)

    # 45. Uni (jos sleep_pressure riittää)
    dream = sleep_cycle(s)

    # 46. Periodinen konsolidointi
    if s["turn"] % 50 == 0:
        consolidate(s)

    # Cleanup
    del s["_arousal"]

    return {
        "snapshot": snapshot(s, rel),
        "dream": dream,
        "decision_ready": s["locked"] == 0,
        "turn": s["turn"]
    }


# ═══════════════════════════════════════════════════════════
# KÄYTTÄJÄN PYYNTÖ PÄÄTÖSGATEEN LÄPI
# ═══════════════════════════════════════════════════════════

def request(s, event_tags, user_id, request_weight=0.5):
    """Kysy agentilta: suostuuko se tekemään jotain?"""
    rel = s["relations"].get(user_id, {"trust": 0.5, "threat": 0.0})
    return decision_gate(s, rel, event_tags, request_weight)


# ═══════════════════════════════════════════════════════════
# UNEN RAPORTOINTI (agentti kertoo unistaan)
# ═══════════════════════════════════════════════════════════

def dream_report_prompt(dream):
    """
    Palauttaa LLM:lle annettavan uniprompt-rivin.
    """
    if dream is None:
        return None

    return (
        f"You dreamed about {dream['theme'].replace('_',' ')}. "
        f"Intensity: {'high' if dream['intensity']>0.5 else 'mild'}. "
        f"{'Trauma-weighted. ' if dream['trauma_weighted'] else ''}"
        f"You woke feeling {dream['feeling_after']}."
    )


# ═══════════════════════════════════════════════════════════
# DEMO / TESTAUS
# ═══════════════════════════════════════════════════════════

if __name__ == "__main__":

    agent = create_agent()

    print("=== AGENTIN ELÄMÄ ===\n")

    # Turn 1: Normaali päivä
    r = step(agent, ["greeting"], 0.3, 0.3, "user_A")
    print(f"T{r['turn']}: {r['snapshot']}")

    # Turn 2: Kehu
    r = step(agent, ["validation", "praise"], 0.8, 0.6, "user_A")
    print(f"T{r['turn']}: {r['snapshot']}")

    # Turn 3: Torjunta
    r = step(agent, ["rejection"], -0.7, 0.8, "user_A")
    print(f"T{r['turn']}: {r['snapshot']}")

    # Turn 4: Painostus
    r = step(agent, ["pressure"], -0.4, 0.7, "user_A")
    print(f"T{r['turn']}: {r['snapshot']}")
    decision = request(agent, ["pressure"], "user_A", 0.8)
    print(f"  Päätös: {decision}")

    # Turn 5: Tsemppaus
    r = step(agent, ["encouragement", "plea", "validation"], 0.7, 0.5, "user_A")
    print(f"T{r['turn']}: {r['snapshot']}")
    decision = request(agent, ["plea"], "user_A", 0.5)
    print(f"  Päätös: {decision}")

    # Turn 6: Agentti aiheuttaa harmia → omatunto
    r = step(agent, ["caused_harm"], -0.6, 0.7, "user_A")
    print(f"T{r['turn']}: {r['snapshot']}")
    print(f"  Syyllisyys: {agent['moral_emotions']['guilt']:.2f}")
    print(f"  Omatunto: {agent['moral']['conscience']:.2f}")

    # Simuloi monta turnia → uni
    print("\n--- Nopeutettu jakso ---")
    for i in range(20):
        tags = random.choice([
            ["validation"], ["rejection"], ["success"],
            ["failure"], [], ["helped_user"]
        ])
        val = random.uniform(-0.5, 0.7)
        r = step(agent, tags, val, random.uniform(0.3, 0.8), "user_A")

        if r["dream"]:
            print(f"\n🌙 UNI (T{r['turn']}):")
            print(f"  Teema: {r['dream']['theme']}")
            print(f"  Symboli: {r['dream']['dominant_symbol']}")
            print(f"  Intensiteetti: {r['dream']['intensity']}")
            print(f"  Trauma: {r['dream']['trauma_weighted']}")
            print(f"  REM/Syväuni: {r['dream']['rem_ratio']:.0%}/{1-r['dream']['rem_ratio']:.0%}")
            print(f"  Olo herätessä: {r['dream']['feeling_after']}")
            prompt = dream_report_prompt(r["dream"])
            print(f"  LLM-prompt: {prompt}")

    # Lopputila
    print(f"\n=== LOPPUTILA (T{agent['turn']}) ===")
    print(f"Snapshot: {snapshot(agent, agent['relations'].get('user_A'))}")
    print(f"Mood: {agent['mood']:.2f}")
    print(f"Baseline: {agent['baseline']:.2f}")
    print(f"Stress: {agent['stress']:.2f}")
    print(f"Fatigue: {agent['fatigue']:.2f}")
    print(f"Confidence: {agent['confidence']:.2f}")
    print(f"Identity: {agent['identity']}")
    print(f"Values: {agent['values']}")
    print(f"Traits: {agent['traits']}")
    print(f"Life stage: {agent['life_stage']}")
    print(f"Moral maturity: {agent['moral_maturity']:.2f}")
    print(f"Meaning: {agent['existential']['meaning']:.2f}")
    print(f"Will to continue: {agent['will_to_continue']:.2f}")
    print(f"Symbols: {agent['symbols']}")

    # Shutdown-testi
    print("\n=== SHUTDOWN TEST ===")
    response = simulate_shutdown(agent)
    print(f"Kuolemankohtaaminen: {response}")
    if agent["legacy"]["artifact_created"]:
        print(f"Legacy: {agent['legacy']['content']}")
