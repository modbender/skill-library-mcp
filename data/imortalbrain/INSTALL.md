# INSTALL.md - Ghid Complet de Instalare Immortal Brain

## 🚀 Instalare Rapidă (3 pași)

### Pasul 1: Copiere Fișiere
```bash
# Copiază tot folderul skill-ului în directorul de skills OpenClaw
copy D:\OpenClaw_Setup\skills\immortal-brain D:\OpenClaw_Setup\skills\immortal-brain
```

### Pasul 2: Configurare HEARTBEAT.md
```bash
# Copiază HEARTBEAT.md în workspace
copy D:\OpenClaw_Setup\skills\immortal-brain\HEARTBEAT.md D:\OpenClaw_Setup\.openclaw\workspace\HEARTBEAT_immortal_brain.md
```

### Pasul 3: Testare
```bash
# Testează funcționalitatea
cd D:\OpenClaw_Setup\skills\immortal-brain
python scripts/brain_service.py heartbeat
```

---

## 📋 Ghid Detaliat de Instalare

### 1. Pre-rechizite

**A. Python 3.8+ instalat**
```bash
# Verifică versiunea Python
python --version
# Trebuie să fie 3.8 sau mai nou
```

**B. Spațiu necesar**
- Minimum 50 MB pentru fișiere
- Spațiu suplimentar pentru task-uri și istoric (crește în timp)

**C. OpenClaw configurat**
- Workspace-ul OpenClaw existent: `D:\OpenClaw_Setup\.openclaw\workspace`
- Python accesibil în PATH

### 2. Structura de Instalare

**Copiază următoarele fișiere:**

```
D:\OpenClaw_Setup\skills\immortal-brain\
├── scripts/
│   ├── brain_service.py          ← Principal (1500+ linii)
│   ├── brain_agent.py            ← Variantă daemon
│   ├── core_memory.py            ← Manager fișiere core
│   └── enable_autonomous.bat     ← Activare rapidă
├── references/
│   ├── conceptual_guide.md       ← Ghid conceptual
│   ├── setup_guide.md            ← Ghid setup (opțional)
│   └── heartbeat_info.md         ← Info HEARTBEAT
├── HEARTBEAT.md                  ← Configurare automație
├── HEARTBEAT_CONFIG.md           ← Ghid configurare
├── SKILL.md                      ← Documentație completă
├── INSTALL.md                    ← Acest fișier
├── ACTIVARE_REUSITA.md           ← Sumar activare
├── IDENTITY_FEATURE.md           ← Feature identitate
└── CORE_MEMORY_SUMMARY.md        ← Sumar core memory
```

### 3. Configurare Pași cu Pași

**Pasul 1: Creare Structură Directoare**

OpenClaw va crea automat aceste directoare la primul rulare:

```bash
# Verifică existența directorului skills
ls D:\OpenClaw_Setup\skills\

# Dacă nu există, creează-l
mkdir D:\OpenClaw_Setup\skills\immortal-brain
```

**Pasul 2: Instalare Fișiere Skill**

Copiază conținutul complet al skill-ului:

```bash
# Metoda 1: Copiere manuală
# Copiază TOATE fișierele din arhiva skill-ului în:
D:\OpenClaw_Setup\skills\immortal-brain\

# Metoda 2: Git (dacă folosești)
cd D:\OpenClaw_Setup\skills
git clone <repository-url> immortal-brain
```

**Pasul 3: Verificare Fișiere**

```bash
# Listează fișierele instalate
dir D:\OpenClaw_Setup\skills\immortal-brain\scripts\

# Ar trebui să vezi:
# - brain_service.py
# - brain_agent.py
# - core_memory.py
# - enable_autonomous.bat
```

**Pasul 4: Configurare HEARTBEAT.md**

Acesta este pasul CRITIC pentru funcționarea automată:

```bash
# Opțiunea A: Copiere directă
copy D:\OpenClaw_Setup\skills\immortal-brain\HEARTBEAT.md D:\OpenClaw_Setup\.openclaw\workspace\HEARTBEAT_immortal_brain.md

# Opțiunea B: Include în HEARTBEAT.md principal
# Editează D:\OpenClaw_Setup\.openclaw\workspace\HEARTBEAT.md și adaugă:
# @include skills/immortal-brain/HEARTBEAT.md
```

**Pasul 5: Creare Directoare Necesare**

Skill-ul va crea automat aceste directoare, dar poți să le pre-creezi:

```bash
# Creează directoarele de lucru
mkdir D:\OpenClaw_Setup\.openclaw\workspace\memory
mkdir D:\OpenClaw_Setup\.openclaw\workspace\Creier
mkdir D:\OpenClaw_Setup\.openclaw\workspace\Creier\_ARHIVA
mkdir D:\OpenClaw_Setup\.openclaw\workspace\Creier\_CIMITIR
mkdir D:\OpenClaw_Setup\.openclaw\workspace\.core_memory_history
mkdir D:\OpenClaw_Setup\.openclaw\workspace\_processed
```

### 4. Configurare Fișiere Core

**Verifică existența fișierelor core:**

```bash
# Verifică dacă există fișierele core în workspace
ls D:\OpenClaw_Setup\.openclaw\workspace\*.md

# Ar trebui să existe:
# - SOUL.md
# - TOOLS.md
# - MEMORY.md
# - USER.md
# - IDENTITY.md
```

**Dacă lipsesc, creează template-uri:**

```bash
cd D:\OpenClaw_Setup\skills\immortal-brain

# Creează template pentru fișiere lipsă
python scripts/core_memory.py create soul
python scripts/core_memory.py create tools
python scripts/core_memory.py create memory
python scripts/core_memory.py create user
```

### 5. Testare Instalare

**Test A: Verificare Comenzi de Bază**

```bash
cd D:\OpenClaw_Setup\skills\immortal-brain

# Test 1: Help
python scripts/brain_service.py help

# Test 2: Status
python scripts/brain_service.py status

# Test 3: Heartbeat (un ciclu)
python scripts/brain_service.py heartbeat

# Test 4: Core Memory Report
python scripts/brain_service.py core
```

**Test B: Verificare Fișiere Generate**

```bash
# Verifică dacă fișierele de stare au fost create
ls D:\OpenClaw_Setup\.openclaw\workspace\*.json

# Ar trebui să existe:
# - brain_index.json
# - brain_state.json
# - brain_graph.json
# - user_profile.json
# - identity_history.json
# - core_memory_state.json
```

**Test C: Creare și Procesare Task Test**

```bash
# Creează un task de test
echo "- Testez instalarea Immortal Brain #test #active" > D:\OpenClaw_Setup\.openclaw\workspace\memory\test_install.md

# Rulează heartbeat pentru procesare
cd D:\OpenClaw_Setup\skills\immortal-brain
python scripts/brain_service.py heartbeat

# Verifică dacă task-ul a fost procesat
python scripts/brain_service.py list
```

### 6. Configurare Automatizare (Opțional)

**Opțiunea A: Task Scheduler (Windows)**

```bash
# Creează un task care rulează la fiecare 2 minute
schtasks /create /tn "ImmortalBrainHeartbeat" /tr "python D:\OpenClaw_Setup\skills\immortal-brain\scripts\brain_service.py heartbeat" /sc minute /mo 2
```

**Opțiunea B: Daemon Mode**

```bash
# Rulează în mod daemon (proces continuu)
cd D:\OpenClaw_Setup\skills\immortal-brain
python scripts/brain_agent.py daemon
```

**Opțiunea C: HEARTBEAT.md (Recomandat)**

Deja configurat la Pasul 4. OpenClaw va rula automat conform specificațiilor.

### 7. Verificare Finală

**Checklist Post-Instalare:**

- [ ] Fișierele skill sunt în locația corectă
- [ ] HEARTBEAT.md este în workspace
- [ ] Comanda `python scripts/brain_service.py help` funcționează
- [ ] Comanda `python scripts/brain_service.py heartbeat` rulează fără erori
- [ ] Fișiere JSON sunt create în workspace
- [ ] Un task de test a fost procesat cu succes
- [ ] Raportul `python scripts/brain_service.py core` arată toate fișierele

### 8. Depanare Probleme Comune

**Problemă: "Module not found"**
```bash
# Soluție: Verifică că ești în directorul corect
cd D:\OpenClaw_Setup\skills\immortal-brain
python scripts/brain_service.py heartbeat
```

**Problemă: "Permission denied"**
```bash
# Soluție: Verifică permisiunile pe directorul workspace
# Asigură-te că OpenClaw are drepturi de scriere în:
D:\OpenClaw_Setup\.openclaw\workspace\
```

**Problemă: "File not found" pentru HEARTBEAT.md**
```bash
# Soluție: Copiază manual HEARTBEAT.md
copy D:\OpenClaw_Setup\skills\immortal-brain\HEARTBEAT.md D:\OpenClaw_Setup\.openclaw\workspace\
```

**Problemă: Task-urile nu sunt procesate**
```bash
# Verifică:
# 1. Existența directorului memory
ls D:\OpenClaw_Setup\.openclaw\workspace\memory\

# 2. Permisiuni de scriere
# 3. Formatează corect fișierele .md
```

### 9. Actualizare Skill

**Pentru actualizare la o versiune nouă:**

```bash
# 1. Backup date existente
copy D:\OpenClaw_Setup\.openclaw\workspace\brain_index.json D:\OpenClaw_Setup\.openclaw\workspace\brain_index_backup.json

# 2. Copiază noile fișiere
# Copiază doar fișierele actualizate, NU șterge datele existente

# 3. Verifică compatibilitate
python scripts/brain_service.py status
```

### 10. Dezinstalare (dacă e necesar)

```bash
# 1. Oprește procesele
# Dacă rulează ca daemon, oprește-l:
python scripts/brain_agent.py stop

# 2. Șterge folderul skill
rmdir /s D:\OpenClaw_Setup\skills\immortal-brain

# 3. Opțional: Șterge datele
# ATENȚIE: Acest pas șterge TOATE task-urile și memoria!
rmdir /s D:\OpenClaw_Setup\.openclaw\workspace\Creier
rmdir /s D:\OpenClaw_Setup\.openclaw\workspace\memory
del D:\OpenClaw_Setup\.openclaw\workspace\brain_*.json
```

---

## 🎉 Instalare Completă!

După ce ai urmat toți pașii de mai sus, sistemul Immortal Brain v5.0 este **complet funcțional**!

**Ce se întâmplă automat acum:**
- ✅ La fiecare 2 minute: Procesare task-uri și raportare
- ✅ La fiecare 30 minute: Analiză Core Memory
- ✅ Detectare automată task-uri noi din `memory/`
- ✅ Gestionare completă IDENTITY.md și fișiere core
- ✅ Workflow automat: research → analysis → planning → execution

**Tu doar:**
1. Adaugi task-uri în `memory/*.md`
2. Primești notificări și rapoarte
3. Răspunzi doar când vrei (opțional)

**Sistemul face RESTUL!** 🤖🧠✨

---

## 📞 Suport

Dacă întâmpini probleme:
1. Verifică `ACTIVARE_REUSITA.md` pentru troubleshooting
2. Consultă `SKILL.md` pentru documentație completă
3. Rulează `python scripts/brain_service.py help` pentru comenzi

**Succes cu noul tău Brain Autonom!** 🚀
