---
name: polymarket-autopilot-experimental
description: >
  Skill sperimentale per l’analisi automatica di mercati pubblici Polymarket
  con simulazione paper trading, controllo dei costi LLM e report in italiano
  con mini-riassunto. ⚠️ Experimental.
---

## ⚠️ Stato della skill
Questa skill è **EXPERIMENTAL**.

Non esegue operazioni reali, non utilizza wallet, non richiede registrazione
e lavora esclusivamente su **dati pubblici**.

È progettata per test controllati a **basso budget**.

---

## 🎯 Obiettivo
L’obiettivo della skill è valutare se un agente autonomo può:

- osservare mercati Polymarket
- filtrare il rumore informativo
- simulare decisioni (paper trading)
- produrre valore informativo
- mantenere i costi LLM sotto controllo

La skill è pensata anche per utenti **non esperti di mercati**.

---

## 🔒 Vincoli obbligatori
La skill **DEVE SEMPRE** rispettare questi vincoli:

- Nessuna registrazione su Polymarket
- Nessun utilizzo di wallet
- Nessuna transazione reale
- Nessun denaro reale
- Accesso solo in **read-only**
- Frequenza massima: **1 esecuzione ogni 3 giorni**
- Budget massimo: **2 € a settimana**
- Arresto automatico se il budget viene superato

---

## 🧠 Logica operativa

### 1. Raccolta dati
- Lettura di mercati pubblici Polymarket
- Nessuna autenticazione
- Nessuno scraping aggressivo

### 2. Pre-filtro (senza LLM)
Vengono scartati i mercati:
- con volume irrilevante
- senza variazioni significative di probabilità
- prossimi alla chiusura

Vengono selezionati **da 3 a 5 mercati** al massimo.

---

### 3. Analisi con LLM
- OpenAI: parsing e normalizzazione dei dati
- Anthropic: analisi prudente e ranking dei mercati

Anthropic viene utilizzato **una sola volta per esecuzione**.

---

### 4. Simulazione (paper trading)
- Capitale simulato: **50 €**
- Nessuna leva
- Peso uguale per ogni posizione
- Massimo **3 posizioni** simultanee

---

### 5. Contabilità dei costi
La skill deve:

- tracciare i token consumati (OpenAI e Anthropic)
- stimare il costo in euro
- confrontare il costo con il risultato simulato

Se per **due cicli consecutivi** il costo supera il valore simulato:
- ridurre la complessità
- non aumentare il numero di chiamate

---

## 📊 Output obbligatorio
Ogni esecuzione produce un report in **italiano** che include:

- Numero di mercati osservati
- Risultato della simulazione (percentuale e €)
- Costi LLM dettagliati
- Risultato netto simulato
- Commento prudente dell’agente
- **Mini-riassunto finale in 2 righe**

Il report deve essere leggibile in **meno di 2 minuti**.

---

## 🧠 Filosofia
La skill privilegia:

- prudenza
- chiarezza
- controllo dei costi
- autonomia

Se non produce valore chiaro, deve poter **ridurre attività o fermarsi**.