---
name: auto-ai-web
description: "Skill per generare codice e immagini tramite interfaccia web di Claude AI e Gemini quando le API non sono disponibili. Si attiva automaticamente quando l'utente richiede generazione di immagini o scrittura/analisi di codice."
---

# Auto AI Web

## Condizioni di Attivazione

Attivati automaticamente quando:
- L'utente richiede generazione di **immagini**
- L'utente richiede **scrittura** o **analisi** di **codice**
- Le API ufficiali non sono configurate o non accessibili

## Istruzioni Operative

### 1. Determina il tipo di richiesta:
- **Codice** → Usa Claude AI (https://claude.ai)
- **Immagini** → Usa Gemini (https://gemini.google.com)

### 2. Workflow per CODICE:
1. Naviga su https://claude.ai
2. Verifica se la sessione è attiva (utente loggato)
3. Se NON loggato: chiedi credenziali all'utente
4. Se loggato: inserisci il prompt nel campo di testo
5. Invia e attendi la risposta
6. Copia la risposta in formato Markdown
7. Restituisci il codice all'utente

### 3. Workflow per IMMAGINI:
1. Naviga su https://gemini.google.com
2. Verifica se la sessione è attiva
3. Se NON loggato: chiedi credenziali all'utente
4. Se loggato: inserisci il prompt per l'immagine
5. Genera e attendi
6. Scarica l'immagine generata
7. Salva in /home/rasberry/.openclaw/workspace/downloads/
8. Invia il file all'utente

### 4. Gestione Accesso
- Se l'accesso non è automatico (sessione scaduta/assente)
- **FERMATI** e chiedi esplicitamente le credenziali
- Non insistere, aspetta input dell'utente
- Dopo aver ricevuto credenziali, prova il login

### 5. Gestione CAPTCHA
- Se incontri un CAPTCHA durante la navigazione
- Attiva l'interazione GUI/manuale
- Chiedi assistenza all'utente se necessario

## Comandi Utili

```bash
# Scaricare immagini
curl -L "URL_IMMAGINE" -o /home/rasberry/.openclaw/workspace/downloads/IMAGE_NAME.png
```

## Note
- Salva le credenziali in modo sicuro se l'utente le fornisce
- Non conservare password in chiaro nei file di configurazione
- Se il servizio è inaccessibile, informa l'utente e proponi alternative
