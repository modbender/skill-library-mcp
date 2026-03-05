# CONFIGURARE HEARTBEAT.md - Ghid Rapid

## 🎯 Ce face acest fișier?

Transformă Immortal Brain dintr-un skill **pasiv** (care așteaptă comenzi) într-un sistem **autonom** (care acționează singur).

## 🚀 Cum să îl activezi în OpenClaw:

### Opțiunea 1: Copiază în workspace-ul principal
```bash
# Copiază fișierul HEARTBEAT.md din skill în workspace:
copy D:\OpenClaw_Setup\skills\immortal-brain\HEARTBEAT.md D:\OpenClaw_Setup\.openclaw\workspace\HEARTBEAT.md
```

Sau direct:
```
D:\OpenClaw_Setup\.openclaw\workspace\HEARTBEAT.md  ← Pune fișierul aici
```

### Opțiunea 2: Include din skill (recomandat)
```markdown
# În HEARTBEAT.md principal al OpenClaw adaugă:

@include skills/immortal-brain/HEARTBEAT.md
```

## ⏰ Ce se întâmplă automat:

### Fără să faci nimic, sistemul va:

**La fiecare 30 minute:**
- ✅ Procesează notițe noi din `memory/`
- ✅ Organizează în `Creier/`
- ✅ Trimite notificare cu rezultatele

**Zilnic la 09:00:**
- ✨ Generează o curiozitate nouă
- ✨ Te întreabă dacă vrei să o explorezi

**La fiecare oră:**
- 🔥 Caută task-uri urgente
- 🔥 Te alertează dacă există

**Zilnic la 20:00:**
- 📊 Trimite raport zilnic
- 📊 Statistici complete

**Când salvezi un fișier în `memory/`:**
- 📁 Detectează automat
- 📁 Procesează imediat
- 📁 Confirmă integrarea

## 📝 Exemplu Flow Complet:

### Tu faci (doar atât):
```bash
# Crezi un fișier în memory/
echo "- [ ] Implementare API #dev #urgent" >> memory/idei.md
```

### Sistemul face (automat):
1. **În 0-30 minute**: OpenClaw detectează fișierul nou
2. Rulează `brain_service.py pulse`
3. Procesează neuronul
4. Organizează în `Creier/DEV.md`
5. **Notificare**: "🧠 1 neuron nou integrat"

6. **La următoarea oră**: Caută `#urgent`
7. Găsește task-ul tău
8. **Notificare**: "🔥 1 task urgent în așteptare!"

9. **Seara la 20:00**: 
10. **Notificare raport**: "📊 Total: 150 neuroni..."

### Tu primești notificări precum:
- "🧠 3 neuroni noi integrați în Creier"
- "🔥 ATENȚIE: 2 task-uri URGENTE!"
- "✨ Curiozitatea zilei: teoria haosului"
- "📊 Raport zilnic: 150 neuroni total"

## 🎮 Tu doar:
1. **Adaugi notițe** în `memory/*.md`
2. **Primești notificări** despre ce se întâmplă
3. **Acționezi** doar când vrei (opțional)

## 🔧 Personalizare:

### Schimbă frecvența:
```markdown
### La fiecare 10 minute  ← în loc de 30
```

### Adaugă noi acțiuni:
```markdown
### La fiecare 6 ore
- **Acțiune**: `python brain_service.py search "#hold"`
```

### Modifică notificările:
Editează textele între ghilimele în HEARTBEAT.md

## ✅ Verificare:

După ce activezi HEARTBEAT.md:
1. Așteaptă 30 minute
2. Ar trebui să primești prima notificare: "🧠 0 neuroni noi..."
3. Adaugă o notiță în `memory/test.md`
4. Așteaptă încă 30 minute
5. Primești: "🧠 X neuroni noi integrați"

**Succes! Sistemul are acum INIȚIATIVE!** 🎉
