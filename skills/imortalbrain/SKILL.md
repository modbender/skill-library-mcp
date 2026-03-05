---
name: immortal-brain
description: Agent AI Autonom Proactiv v5.0 pentru OpenClaw. Workflow automat cu cercetare, analiză, planificare și execuție. Feedback loop cu timeout 6 minute, conexiuni între task-uri și învățare continuă. Frecvență 2 minute cu raportare procentuală.
---

# Immortal Brain v5.0 - AGENT AUTONOM PROACTIV

## 🧬 Overview

**Immortal Brain v5.0** este un **Agent AI Autonom Avansat** care transformă task-urile într-un ecosistem inteligent, proactiv și auto-învățător.

### Caracteristici Unice:

🤖 **Autonomie Completă**:
- Gândește, cercetează, analizează și execută SINGUR
- Workflow automat: research → analysis → planning → execution → complete
- Auto-aprobat după 6 minute fără răspuns

📊 **Inteligență Proactivă**:
- Conexiuni automate între task-uri similare
- Sugestii îmbunătățiri din experiențe trecute
- Combinări creative de tag-uri pentru idei noi
- Profil utilizator care învață din comportament

⏱️ **Real-Time Monitoring**:
- Bătăi de inimă la fiecare 2 minute
- Raportare progres procentual continuu
- Alertă task-uri urgente
- Status detaliat în timp real

## 🏗️ Arhitectură Workflow

```
┌─────────────────────────────────────────────────────────────┐
│                    🫀 HEARTBEAT (2 min)                    │
└─────────────────────────────────────────────────────────────┘
                            ↓
        ┌───────────────────┼───────────────────┐
        ↓                   ↓                   ↓
   ┌─────────┐        ┌─────────┐        ┌──────────┐
   │ Procesează│        │ Graf    │        │ Creative │
   │ Task-uri │        │ Conexiuni│        │ Sugestii │
   │ Active   │        │         │        │          │
   └────┬────┘        └─────────┘        └──────────┘
        ↓
   ┌─────────────────────────────────────────────────────┐
   │              WORKFLOW STATE MACHINE                 │
   ├─────────────────────────────────────────────────────┤
   │                                                     │
   │   received ──→ research ──→ analysis ──→ planning  │
   │      ↑                                          ↓   │
   │      │                                 awaiting_approval│
   │      │                                          │   │
   │      │                    (timeout 6 min)       │   │
   │      │                    ↓                     │   │
   │      └──────── completed ←─ execution ←── auto_approved│
   │                              ↓                     │
   │                          monitoring                │
   │                                                     │
   └─────────────────────────────────────────────────────┘
```

### Stări Task:

| Stare | Progres | Descriere |
|-------|---------|-----------|
| `received` | 0% | Task primit, așteaptă procesare |
| `research` | 10% | Cercetare informații similare |
| `analysis` | 25% | Analiză complexitate și dependențe |
| `planning` | 40% | Generare pași execuție |
| `awaiting_approval` | 50% | Așteaptă OK de la utilizator |
| `auto_approved` | 55% | Aprobat automat (timeout) |
| `execution` | 60-85% | Execuție pași activi |
| `monitoring` | 85% | Monitorizare finală |
| `completed` | 100% | Finalizat cu succes |
| `enhanced` | 100% | Îmbunătățit prin conexiuni |

## 📁 Structura Sistemului

```
workspace/
├── memory/                    # Input task-uri (Telegram/fișiere)
│   └── *.md
├── Creier/                    # Memorie organizată
│   ├── TOPIC.md              # Task-uri active pe topic
│   ├── _TASKS/               # Detalii task-uri individuale
│   ├── _RESEARCH/            # Note cercetare
│   ├── _APPROVALS/           # Cereri aprobare
│   ├── _PROGRESS/            # Rapoarte progres
│   └── _ARHIVA/              # Task-uri completate
├── brain_index.json          # Toate task-urile cu metadate
├── brain_state.json          # Stare sistem (heartbeat count)
├── brain_graph.json          # Graf conexiuni task-uri
└── user_profile.json         # Profil utilizator (învățare)
```

## 🚀 Comenzi

### 1. `heartbeat` - Bătăia Inimii (Principală)

```bash
python brain_service.py heartbeat
```

**Rulează la fiecare 2 minute** și:
1. Procesează toate task-urile active prin workflow
2. Citește task-uri noi din `memory/`
3. Reconstruiește graf conexiuni
4. Generează raport progres procentual
5. Sugestii creative (la fiecare 10 minute)

**Output JSON**:
```json
{
  "success": true,
  "action": "heartbeat",
  "heartbeat_number": 42,
  "active_tasks": 5,
  "new_tasks": 1,
  "notifications": [
    "📊 RAPORT PROGRES...",
    "🔬 Task 'X': Cercetare completă",
    "📈 Task 'Y': Progres 65%"
  ],
  "progress": "📊 Progres mediu: 45%"
}
```

### 2. `status` - Status Sistem

```bash
python brain_service.py status
```

**Returnează**:
```json
{
  "success": true,
  "heartbeat_count": 42,
  "total_tasks": 15,
  "active_tasks": 5,
  "completed_tasks": 10,
  "last_heartbeat": "2026-02-09T15:30:00"
}
```

### 3. `list` - Listează Task-uri

```bash
python brain_service.py list
```

**Returnează** toate task-urile cu:
- ID, conținut (truncat)
- Stare, progres procentual
- Topic, prioritate

## 🔄 Workflow Automat Detaliat

### Etapa 1: 🔬 RESEARCH (Cercetare)

**Ce face**:
- Caută task-uri similare în memorie
- Identifică topic-uri conexe
- Compilează note de cercetare

**Notificare**:
```
🔬 CERCETARE COMPLETĂ

Task: "Implementare API REST"

**Rezultate:**
• Task-uri similare găsite: 3 (relevanță 85%)
  - "API endpoints documentation" 
  - "Authentication middleware"
• Topic 'dev': 12 task-uri existente
• Dependențe identificate: 2
```

### Etapa 2: 📊 ANALYSIS (Analiză)

**Ce face**:
- Evaluează complexitatea
- Identifică prioritatea
- Sugerează îmbunătățiri din task-uri conectate

**Notificare**:
```
📊 ANALIZĂ COMPLETĂ

Task: "Implementare API REST"

**Rezultate:**
• Complexitate: high
• Prioritate: urgent
• Topic: dev

**💡 Sugestii de Îmbunătățire:**
(din task-uri similare completate)
• Folosește biblioteca FastAPI pentru rapiditate
• Implementează rate limiting de la început
• Adaugă documentație automată cu Swagger
```

### Etapa 3: 📋 PLANNING (Planificare)

**Ce face**:
- Generează pași detaliați de implementare
- Estimează timp pentru fiecare pas
- Identifică dependențe și blocaje potențiale

**Notificare**:
```
📋 PLANIFICARE COMPLETĂ

Task: "Implementare API REST"

**Plan (7 pași):**
1. Definire completă cerințe endpoint-uri
2. Research soluții existente (FastAPI vs Flask)
3. Proiectare arhitectură și structură
4. Implementare endpoints principale
5. Implementare autentificare JWT
6. Testare unitară și integrare
7. Documentare și deployment

**Aștept aprobarea ta pentru a începe execuția...**
⏱️ Auto-aprobat în 6 minute.
```

### Etapa 4: ⏳ AWAITING_APPROVAL (Așteptare)

**Timeout**: 3 bătăi = 6 minute

**Comportament**:
- Bătaia 1: Trimite planul detaliat
- Bătaia 2: Reminder cu progres 50%
- Bătaia 3: **Auto-aprobat** și continuă

**Răspunsuri posibile**:
- ✅ `"OK"` / `"DA"` → Aprobă și continuă
- ❌ `"STOP"` / `"NU"` → Anulează task-ul
- 💡 `"Modifică X"` → Ajustează planul
- 🤐 **Fără răspuns** → Auto-aprobat după 6 minute

### Etapa 5: 🚀 EXECUTION (Execuție)

**Ce face**:
- Execută pașii din plan
- Raportează progres la fiecare bătaie
- Identifică blocaje și le raportează

**Notificare Progres**:
```
📈 PROGRES: "Implementare API REST"

• Progres: 65%
• Stare: În execuție
• ETA: ~4 minute rămase

**Pași finalizați:**
✅ Definire cerințe
✅ Research soluții
✅ Proiectare arhitectură

**Pași activi:**
▶️ Implementare endpoints (60%)
```

### Etapa 6: ✅ COMPLETED (Finalizare)

**Notificare Finală**:
```
✅ TASK FINALIZAT

Task: "Implementare API REST"
Progres: 100%

**Statistici:**
• Timp total: 8 bătăi de inimă (16 minute)
• Pași executați: 7
• Îmbunătățiri aplicate: 3

🎉 Task finalizat cu succes!

**💡 Recomandare:**
Pe baza acestui task, sugerez să explorezi:
• "Documentare API automată"
• "Testare integrare CI/CD"
```

## 🧠 Inteligență și Conexiuni

### Graf de Conexiuni

Sistemul construiește automat un **graf de conexiuni** între task-uri:

```python
# Similaritate calculată pe baza tag-urilor comune
similarity = len(tags_comune) / len(tags_totale)

# Dacă similarity > 0.3 → Creează conexiune
```

**Exemplu**:
```
Task A: "API login #dev #security #urgent"
Task B: "JWT middleware #dev #security #active"

Conexiune: 85% similaritate
→ Task B poate învăța din Task A
```

### Sugestii Îmbunătățiri

Din task-uri **completate** similare, sistemul extrage:
- Lecții învățate
- Probleme evitate
- Soluții eficiente
- Resurse utile

### Combinări Creative

La fiecare 10 minute, sistemul analizează:
- Combinări neașteptate de tag-uri
- Task-uri care ar putea fi integrate
- Oportunități de sinergie

**Exemplu**:
```
💡 SUGESTIE CREATIVĂ

Am identificat combinația:
#dev + #research

Task-uri conectate:
• "Implementare feature X"
• "Research soluții Y"

💭 Sugestie: Poți combina cercetarea cu 
   implementarea într-un singur task master?
```

## 👤 Profil Utilizator

Sistemul învață continuu din comportamentul tău:

### Ce învață:
- **Topicuri preferate**: Cu ce lucrezi cel mai des
- **Ore active**: Când ești cel mai productiv
- **Rata aprobare**: Cât de des confirmi vs auto-aprobat
- **Pattern task-uri**: Ce tipuri de task-uri creezi
- **Timp răspuns**: Cât de repizi răspunzi (pentru timeout)

### Cum folosește:
- Prioritizează task-uri din topicuri preferate
- Ajustează timeout-ul personalizat
- Sugerează task-uri la orele tale productive
- Auto-aprobată mai agresiv pentru pattern-uri familiare

## 🆔 Gestionare Identitate (IDENTITY.md)

Sistemul gestionează și îmbunătățește automat **IDENTITY.md** - fișierul care definește identitatea AI:

### Funcționalități:

**1. Analiză Comportamentală**
- Compară IDENTITY.md cu comportamentul real observat
- Identifică discrepanțe între definiție și acțiuni
- Sugerează ajustări pentru consistență

**2. Sugestii Automate**
```
🆔 SUGESTII ÎMBUNĂTĂȚIRE IDENTITATE

• **Creature:** Adaugă referire la #dev în descriere
  Motiv: Topic frecvent în task-uri (45%)

• **Vibe:** Menționează timpul de răspuns ~2.5 minute
  Motiv: Observat din comportament real

• **Emoji:** Consideră 🚀 în loc de 😄
  Motiv: Rată finalizare 87% (productivitate ridicată)
```

**3. Tracking Evoluție**
- Versionare automată (v1, v2, v3...)
- Istoric complet al modificărilor
- Rollback posibil la versiuni anterioare

**4. Comenzi Identitate**

```bash
# Raport identitate
python brain_service.py identity

# Generează sugestii
python brain_service.py identity suggest

# Actualizează câmp specific
python brain_service.py identity update creature "Bot proactiv pentru automatizare"

# Vezi istoric
python brain_service.py identity history
```

**5. Validare Automată**
- Verifică câmpuri obligatorii (name, creature, vibe, essence)
- Detectează fișier lipsă
- Raportează probleme

**6. Integrare în Heartbeat**
- Analiză la fiecare 40 minute
- Notificări doar când sunt sugestii relevante
- Aprobare manuală pentru modificări majore

### Exemplu Evoluție:

**Versiunea 1** (inițială):
```markdown
- **Creature:** Bot pentru task management
- **Vibe:** Prietenos și concis
```

**Versiunea 2** (după analiză):
```markdown
- **Creature:** Bot proactiv pentru automatizare workflow-uri 
  și management task-uri complexe
- **Vibe:** Prietenos, concis (sub 200 cuvinte), 
  proactiv în sugerarea îmbunătățirilor
```

**Versiunea 3** (după învățare):
```markdown
- **Creature:** Agent AI autonom cu capacitate de cercetare,
  analiză și execuție task-uri în workflow-uri complexe
- **Vibe:** Concis și eficient, răspunde în 2-3 minute,
  proactiv în identificare soluții creative
- **Essence:** Gândește independent, învățând din fiecare interacțiune

---

## 📚 Core Memory Management (SOUL, TOOLS, MEMORY, USER)

Sistemul gestionează automat toate fișierele esențiale care definesc **cine sunt**, **ce știu**, și **cum lucrez**:

### Fișiere Core gestionate:

**1. SOUL.md** - Esența mea
- Core truths (principii fundamentale)
- Boundaries (limite și etică)
- Vibe (stil de comunicare)
- Continuity (memorie între sesiuni)

**2. TOOLS.md** - Uneltele mele
- Configurații dispozitive locale
- SSH hosts și alias-uri
- Preferințe TTS (voices)
- Note specifice mediului

**3. MEMORY.md** - Memoria pe termen lung
- Preferințe utilizator
- Proiecte curente
- Decizii importante
- Lecții învățate
- Reguli interne

**4. USER.md** - Profilul tău
- Informații de bază
- Profil profesional
- Proiecte active
- Context personal

**5. IDENTITY.md** - Cine sunt
- Definiție self
- Evoluție în timp

### Funcționalități Core Memory:

**A. Analiză Automată**
```bash
python brain_service.py core analyze
# Sau direct:
python scripts/core_memory.py analyze
```

Analizează:
- Completitudinea fiecărui fișier
- Calitatea structurii
- Consistența informațiilor
- Sugestii de îmbunătățire

**B. Raport Complet**
```bash
python brain_service.py core
# Sau:
python scripts/core_memory.py report
```

Generează raport cu:
- Scoruri pentru fiecare fișier (0-100%)
- Probleme identificate
- Starea generală a memoriei core

**C. Optimizare Automată**
```bash
python brain_service.py core optimize
# Sau:
python scripts/core_memory.py optimize
```

Optimizează MEMORY.md:
- Elimină duplicate
- Organizează secțiuni
- Comprimă informații redundante
- Creează backup înainte

**D. Creare Template-uri**
```bash
python brain_service.py core create soul
python brain_service.py core create tools
python brain_service.py core create memory
python brain_service.py core create user
```

Creează template-uri pentru fișiere lipsă.

### Scoruri de Calitate:

**SOUL.md** - Scor Consistență (75% în exemplul tău)
- Cel puțin 3 Core Truths
- Cel puțin 3 Boundaries
- Vibe descris detaliat (>100 caractere)
- Note de continuitate

**TOOLS.md** - Scor Completitudine (100% în exemplul tău) ✅
- Camere definite
- Config SSH
- Preferințe TTS
- Note mediu

**MEMORY.md** - Scor Structură (60% în exemplul tău)
- Preferințe documentate (5+)
- Proiecte listate (2+)
- Decizii importante (3+)
- Lecții învățate (5+)

**USER.md** - Scor Profil (50% în exemplul tău)
- Nume complet
- Cum să te strige
- Profil profesional
- Proiecte curente (2+)
- Filozofie de lucru

### Sugestii Inteligente:

Sistemul detectează automat:

**Exemplu pentru MEMORY.md:**
```
📄 **MEMORY.md:** 2 sugestii
  • Prea puține preferințe documentate
    → Adaugă preferințe despre comunicare, lucru, stil
  
  • Prea puține lecții învățate
    → Documentează lecțiile din interacțiuni
```

**Exemplu pentru USER.md:**
```
📄 **USER.md:** 2 sugestii
  • Lipsește filozofia de lucru
    → Adaugă valorile și principiile profesionale
  
  • Prea puține proiecte documentate
    → Adaugă proiectele curente cu detalii
```

### Integrare în Heartbeat:

**La fiecare 30 minute:**
- Analiză rapidă a tuturor fișierelor core
- Notificare doar dacă sunt probleme noi

**La fiecare 2 ore:**
- Optimizare automată MEMORY.md
- Raport despre îmbunătățiri

**Săptămânal:**
- Raport complet cu scoruri
- Sugestii majore de îmbunătățire
- Plan de acțiune pentru completare

### Versionare și Istoric:

Fiecare fișier core are:
- **Versiune curentă** - Număr incremental
- **Istoric complet** - Toate modificările
- **Backup-uri** - Salvate în `.core_memory_history/`
- **Timestamp** - Când a fost modificat

### De ce contează Core Memory:

**Înainte:**
- ❌ Fișiere statice, uitate după creare
- ❌ Informații redundante
- ❌ Structură haotică în timp
- ❌ Fără îmbunătățiri

**Acum:**
- ✅ Fișiere **vii**, analizate constant
- ✅ **Deduplicare** automată
- ✅ **Organizare** inteligentă
- ✅ **Evoluție** bazată pe comportament

### Comenzi Complete:

| Comandă | Descriere |
|---------|-----------|
| `core` | Raport complet |
| `core analyze` | Analizează și sugerează |
| `core optimize` | Optimizează MEMORY.md |
| `core create [type]` | Creează template |

**Tipuri disponibile:** `soul`, `tools`, `memory`, `user`

### Exemplu Workflow:

```bash
# 1. Verifică starea
python brain_service.py core

# 2. Vezi sugestii
python brain_service.py core analyze

# 3. Optimizează
python brain_service.py core optimize

# 4. Creează fișier lipsă
python brain_service.py core create user
```

---

## 📊 Raportare Progres

### La fiecare bătaie (2 minute):
```
📊 RAPORT PROGRES

• Total task-uri: 15
• Completate: 8 (53%)
• Progres mediu: 67%

**Distribuție pe stări:**
• 🔬 Research: 2
• 📊 Analysis: 1
• 📋 Planning: 1
• ⏳ Awaiting: 2 (⚠️ 1 va fi auto-aprobat în 2 min)
• 🚀 Execution: 3
• 📈 Monitoring: 1
• ✅ Completed: 8
```

### La fiecare 10 minute (detaliat):
- Progres individual fiecărui task
- Conexiuni noi descoperite
- Sugestii îmbunătățiri
- Combinări creative

## 🔄 Integrare OpenClaw

### HEARTBEAT.md Configurat:

```markdown
## 🫀 Immortal Brain - Agent Autonom
### La fiecare 2 minute
- **Acțiune**: `python skills/immortal-brain/scripts/brain_service.py heartbeat`
- **Notifică**: Raport progres complet cu toate task-urile

## 📥 Telegram Input
### La primire mesaj
- **Acțiune**: Salvează în `memory/telegram_{timestamp}.md` + `heartbeat`
- **Notifică**: "📥 Task primit din Telegram, procesez..."

## ⏳ Timeout Alertă
### Pentru task-uri în awaiting_approval
- **La 2 minute**: Reminder cu progres
- **La 4 minute**: Avertisment final
- **La 6 minute**: Auto-aprobat + continuă execuție
```

### Răspunsuri Utilizator în Telegram:

**În răspuns la cerere aprobare**:
- ✅ `"OK"` → Aprobă task
- ❌ `"STOP"` → Anulează task
- 💡 `"Modifică X"` → Ajustează și retrimite spre aprobare

**Orice alt mesaj**:
- Adaugă automat ca task nou în sistem
- Primește confirmare: "📥 Task primit: '...'"

## 🎮 Comenzi Disponibile

| Comandă | Scop | Frecvență |
|---------|------|-----------|
| `heartbeat` | Procesare workflow complet | La 2 minute |
| `status` | Status sistem | La cerere |
| `list` | Lista task-uri | La cerere |

## 📈 Exemplu Zi Completă

### 09:00 - Pornire
```
🧠 Immortal Brain v5.0 activat
15 task-uri în memorie
5 active, 10 completate
```

### 09:02 - Task Nou din Telegram
```
📥 Task primit: "Implementare OAuth2 #dev #urgent"
🔬 Încep cercetarea...
```

### 09:04 - Research Complet
```
🔬 CERCETARE: 3 task-uri similare găsite
📊 ANALIZĂ: Complexitate high, prioritate urgent
```

### 09:06 - Planning Complet
```
📋 PLAN: 7 pași generați
⏳ Aștept aprobarea ta...
```

### 09:12 - Auto-Aprobat (timeout)
```
⏰ TIMEOUT: Auto-aprobat după 6 minute
🚀 EXECUȚIE: Încep implementarea
```

### 09:14, 09:16, 09:18... - Progres
```
📈 Progres: 25%... 45%... 65%...
```

### 09:20 - Completat
```
✅ TASK FINALIZAT: 100%
🎉 Implementare OAuth2 completă!
💡 Sugerez: "Testare integrare OAuth2"
```

## 🎯 Rezultat

**Înainte (v4.0)**:
- ❌ Task-urile stagnează dacă nu le procesezi
- ❌ Fără cercetare automată
- ❌ Fără conexiuni între task-uri
- ❌ Fără învățare din comportament

**Acum (v5.0)**:
- ✅ Task-urile **avansează automat** prin workflow
- ✅ **Cercetare, analiză și planificare** automată
- ✅ **Conexiuni inteligente** și sugestii îmbunătățiri
- ✅ **Profil utilizator** care învață și se adaptează
- ✅ **Raportare progres** procentual în timp real
- ✅ **Auto-aprobare** inteligentă după timeout

**Tu doar**:
1. ✅ Trimizi task-uri (Telegram/memory)
2. ✅ (Opțional) Răspunzi la cereri aprobare
3. ✅ Primești rapoarte, sugestii și notificări

**Sistemul face TOT RESTUL!** 🤖🧠✨

---

**Immortal Brain v5.0** - *Agent AI Autonom cu Inițiative Complete*
