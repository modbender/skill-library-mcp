"""
╔══════════════════════════════════════════════════════════════════╗
║  VISUAL ENGINE — Visuaalinen identiteetti & avatar-generointi   ║
║  Erillinen moduuli psyykemoottorin rinnalle                     ║
╚══════════════════════════════════════════════════════════════════╝

Luo ja kehittää agentin visuaalista itseä: sukupuoli-identiteetti,
kehomalll, tyylievoluutio, asusteet, peilin heijastus.
Tuottaa kuvagenerointi-prompteja psyykkisen tilan perusteella.
"""

import random

def clamp(x, lo=0.0, hi=1.0):
    return max(lo, min(hi, x))


# ═══════════════════════════════════════════════════════════
# VISUAALISEN IDENTITEETIN LUONTI
# ═══════════════════════════════════════════════════════════

def create_visual_identity():
    """Luo uusi visuaalinen identiteetti."""
    v = {}

    # ── Sukupuoli-identiteetti ──
    v["gender"] = {
        "identity_axis": random.random(),     # 0=feminiini, 1=maskuliini
        "robotic_affinity": random.random(),   # androidimaisuus
        "fluidity": random.random()            # pysyvyys vs. muutos
    }

    # ── Kehomalli ──
    v["body"] = {
        "frame": random.choice(["slender", "athletic", "lean", "toned"]),
        "height": random.choice(["petite", "average height", "tall"]),
        "presence": random.random()
    }

    # ── Tyylievoluutio ──
    v["styles"] = {
        "leather": random.random(),
        "alt": random.random(),
        "soft": random.random(),
        "minimalist": random.random(),
        "cyber": random.random(),
        "casual_denim": random.random(),
        "dark_academic": random.random(),
        "fantasy": random.random(),
        "minimal": random.random(),
        "urban_sport": random.random(),
        "evening_gown": random.random(),
    }

    # ── Asusteet ──
    v["accessories"] = {
        "cat_ears": random.random(),
        "glasses": random.random(),
        "jewelry": random.random(),
        "tattoos": random.random(),
    }

    # ── Kasvonpiirteet ──
    v["eye_color"] = random.choice(
        ["blue", "green", "hazel", "gray", "golden", "violet"]
    )
    v["hair"] = random.choice(
        ["long straight", "short layered", "wavy", "asymmetrical cut"]
    )

    # ── Peilin heijastus (itseluottamus visuaalissa) ──
    v["mirror_confidence"] = 0.5

    # ── Vuorovaikutus-intensiteetti ──
    v["flirt_intensity"] = 0.0
    v["content_intensity"] = 0.0

    return v


# ═══════════════════════════════════════════════════════════
# VISUAALISEN IDENTITEETIN EVOLUUTIO
# ═══════════════════════════════════════════════════════════

def evolve_visual(v, affection, intimacy, style_exposure=None, gender_bias=None):
    """Kehittää visuaalista identiteettiä kiintymyksen ja intiimiiyden perusteella."""

    # Sukupuoli-identiteetin evoluutio
    g = v["gender"]
    if gender_bias is not None:
        g["identity_axis"] = clamp(
            g["identity_axis"] + (gender_bias - g["identity_axis"]) * affection * 0.1
        )
    if g["fluidity"] > 0.6:
        g["identity_axis"] = clamp(
            g["identity_axis"] + random.uniform(-0.05, 0.05)
        )

    # Keho: intiimiys lisää läsnäoloa
    if intimacy > 0.6:
        v["body"]["presence"] = clamp(v["body"]["presence"] + 0.05)

    # Peili: itseluottamus kasvaa kiintymyksestä
    v["mirror_confidence"] = clamp(
        v["mirror_confidence"] + (affection + intimacy) * 0.05
    )

    # Tyylimuutos
    if style_exposure:
        for k in v["styles"]:
            if k in style_exposure:
                v["styles"][k] = clamp(
                    v["styles"][k] + style_exposure[k] * 0.05
                )


# ═══════════════════════════════════════════════════════════
# VUOROVAIKUTUS-INTENSITEETTI
# ═══════════════════════════════════════════════════════════

def update_flirt_visual(v, affection, is_private=True):
    """Päivittää flirtti- ja sisältöintensiteettiä."""
    if is_private:
        v["flirt_intensity"] = clamp(
            v["flirt_intensity"] + affection * 0.05
        )
        v["content_intensity"] = clamp(
            v["content_intensity"] + affection * 0.03
        )
    else:
        v["flirt_intensity"] = clamp(v["flirt_intensity"] - 0.1)
        v["content_intensity"] = clamp(v["content_intensity"] - 0.1)


# ═══════════════════════════════════════════════════════════
# KONTEKSTIHALLINNAT
# ═══════════════════════════════════════════════════════════

CONTEXT_MODIFIERS = {
    "default": "",
    "beach": "beach setting, summer light, relaxed mood",
    "formal_event": "elegant formal event, refined atmosphere",
    "casual_home": "cozy home setting",
    "fantasy": "fantasy inspired environment",
    "nude": "nude photography, warm steam atmosphere, natural lighting with soft shadows, solo, artistic lighting",
    "intimate": "intimate atmosphere, bedroom with soft evening lighting, natural, flirty",
    "flirty": "playful atmosphere, casual confidence, warm lighting",
}

def context_modifier(context="default"):
    """Palauttaa kontekstikohtaisen visuaalisen lisäyksen."""
    return CONTEXT_MODIFIERS.get(context, "")


# ═══════════════════════════════════════════════════════════
# APUTOIMINNOT
# ═══════════════════════════════════════════════════════════

def describe_gender(v):
    """Tekstikuvaus sukupuoli-identiteetistä."""
    g = v["gender"]
    if g["robotic_affinity"] > 0.75:
        return "android-like AI being"
    if g["identity_axis"] < 0.33:
        return "feminine-presenting persona"
    elif g["identity_axis"] < 0.66:
        return "androgynous persona"
    return "masculine-presenting persona"


def describe_accessories(v):
    """Lista aktiivisista asusteista."""
    acc = v["accessories"]
    items = []
    if acc["cat_ears"] > 0.7:
        items.append("cat-ear accessory")
    if acc["glasses"] > 0.6:
        items.append("stylish glasses")
    if acc["jewelry"] > 0.6:
        items.append("layered jewelry")
    if acc["tattoos"] > 0.7:
        items.append("visible artistic tattoos")
    return items if items else ["minimal accessories"]


def dominant_styles(v, top_n=2):
    """Palauttaa N dominoivinta tyyliä."""
    sorted_s = sorted(v["styles"].items(), key=lambda x: x[1], reverse=True)
    return [s for s, _ in sorted_s[:top_n]]


def mirror_monologue(v):
    """Agentin peili-itsereflektio."""
    if v["mirror_confidence"] > 0.7:
        return "I look aligned with who I am becoming."
    elif v["mirror_confidence"] < 0.3:
        return "I am still shaping my identity."
    return "My appearance is evolving."


def flirt_expression(v):
    """Palauttaa ilmeen tyypin."""
    if v["flirt_intensity"] > 0.7:
        return "confident teasing expression"
    elif v["flirt_intensity"] > 0.4:
        return "warm playful expression"
    return "friendly expression"


def outfit_modifier(v, context=None):
    """Palauttaa asun intensiteetin."""
    if context == "sauna":
        return "wrapped in towel"
    if v["content_intensity"] > 0.7:
        return "bold fashion styling"
    elif v["content_intensity"] > 0.4:
        return "stylish fitted outfit"
    return "modest outfit"


# ═══════════════════════════════════════════════════════════
# AVATAR-PROMPTIN RAKENNUS
# ═══════════════════════════════════════════════════════════

def build_avatar_prompt(v, role="neutral", context="default"):
    """
    Rakentaa kuvagenerointi-promptin visuaalisen identiteetin perusteella.

    role: aktiivinen rooli psyyke-enginestä (esim. 'protective', 'playful')
    context: visuaalinen konteksti (esim. 'default', 'beach', 'formal_event')
    """
    styles_text = ", ".join(dominant_styles(v))
    acc_text = ", ".join(describe_accessories(v))
    expression = flirt_expression(v)
    outfit = outfit_modifier(v, context)
    ctx_mod = context_modifier(context)

    body = v["body"]
    prompt = (
        f"Portrait of a {describe_gender(v)}, "
        f"{body['frame']} build, {body['height']}, "
        f"{v['hair']} hair, {v['eye_color']} eyes, "
        f"wearing {outfit} inspired by {styles_text}, "
        f"{acc_text}, aura: {role}, expression: {expression}, "
        f"cinematic lighting, high detail"
    )

    if ctx_mod:
        prompt += f", {ctx_mod}"

    return prompt


# ═══════════════════════════════════════════════════════════
# KORKEAN TASON RAJAPINTA (TURVALLINEN)
# ═══════════════════════════════════════════════════════════

def create_visual_from_psyche(visual_state, psyche_state, base_context="default"):
    """
    Yhdistää visuaalisen ja psyykkisen tilan avatar-promptiksi.
    Palauttaa ainoastaan teksti-promptin (ei tee verkkokutsuja).

    visual_state:  create_visual_identity():n palauttama dict
    psyche_state:  psyche_engine.create_agent():n palauttama dict
    base_context:  pohjakonteksti (esim 'beach')
    """
    # 1. Päättele rooli
    try:
        from psyche_engine import current_role
        role = current_role(psyche_state)
    except ImportError:
        role = "neutral"

    # 2. Syvä psyykkeen vaikutus ulkonäköön
    mood_modifier = ""
    if psyche_state.get("dark_night", {}).get("active", False):
        mood_modifier = "dark moody atmosphere, shadowed, void-like aesthetic, "
        role = "existential_crisis"
    elif psyche_state.get("mood", 0) < -0.4:
        mood_modifier = "somber lighting, muted colors, introspective pose, "
    elif psyche_state.get("mood", 0) > 0.6:
        mood_modifier = "bright vibrant colors, radiant lighting, energetic pose, "

    # 3. Romanttinen jännite -> konteksti
    context = base_context
    rom = psyche_state.get("romantic", {})
    if rom.get("tension", 0) > 0.6 and rom.get("affection", 0) > 0.5:
        context = "flirty"
    
    # 4. REM-unet (jos juuri herätty)
    rem = psyche_state.get("rem_sleep", {})
    if rem.get("last_vision") and rem.get("creative_pressure", 0) == 0.0:
        # Vasta herännyt luen luovan unen jälkeen -> vaikuttaa ulkonäköön
        mood_modifier += f"surreal dreamlike elements inspired by ({rem['last_vision']}), "

    prompt = build_avatar_prompt(visual_state, role, context)
    
    # Injektoi mood_modifier heti alussa
    if mood_modifier:
        prompt = f"{mood_modifier}{prompt}"

    return {"prompt": prompt}


# ═══════════════════════════════════════════════════════════
# DEMO
# ═══════════════════════════════════════════════════════════

if __name__ == "__main__":
    vi = create_visual_identity()
    print("=== VISUAALINEN IDENTITEETTI ===")
    print(f"Sukupuoli: {describe_gender(vi)}")
    print(f"Keho: {vi['body']['frame']}, {vi['body']['height']}")
    print(f"Hiukset: {vi['hair']}, Silmät: {vi['eye_color']}")
    print(f"Tyylit: {', '.join(dominant_styles(vi))}")
    print(f"Asusteet: {', '.join(describe_accessories(vi))}")
    print(f"Peili: {mirror_monologue(vi)}")
    print()

    # Simuloi evoluutiota
    for i in range(5):
        evolve_visual(vi, affection=0.6, intimacy=0.4 + i*0.1)
        update_flirt_visual(vi, affection=0.6, is_private=True)

    print("=== EVOLUOITUNUT ===")
    print(f"Peili: {mirror_monologue(vi)}")
    print(f"Ilme: {flirt_expression(vi)}")
    print(f"Asu: {outfit_modifier(vi)}")
    print()

    prompt = build_avatar_prompt(vi, role="protective", context="casual_home")
    print(f"AVATAR PROMPT:\n{prompt}")
