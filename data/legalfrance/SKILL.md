---
name: legalfrance
description: "Assistant juridique français RAG sur codes et lois consolidés (LEGI/DILA). Utiliser pour questions de droit français, recherche d'articles, explication de textes législatifs, synthèse juridique avec citations vérifiables."
---

# LegalFrance

Assistant juridique FR basé sur un retrieval hybride (FTS + vector) avec citations d'articles.

## Première utilisation — initialisation du référentiel

Si les index sont absents (`data/chroma_db` ou `data/fts_index.db` manquants), **demander confirmation à l'utilisateur avant d'exécuter** :

```bash
python scripts/ingest.py
```

⚠️ Cette étape télécharge le corpus LEGI (HuggingFace) et le modèle d'embeddings BGE-M3 (~2 Go au total) puis écrit les index sur disque. Durée estimée : 20–40 min selon la connexion.

Demander : *"L'initialisation va télécharger ~2 Go de données (corpus juridique + modèle). Confirmer ?"*

## Utilisation

Question juridique :

```bash
python scripts/one_shot.py "<question>"
```

Mode structuré JSON :

```bash
python scripts/one_shot.py "<question>" --json
```

Recherche brute dans les codes :

```bash
python scripts/search.py "<requête>" 5
```

## Règles de réponse

- Citer uniquement les sources retrouvées dans les index
- Ne jamais inventer d'article ou de décision
- Si sources insuffisantes : le dire explicitement
- Format recommandé : Principe → Application → Limites → Sources
- Disclaimer obligatoire en fin de réponse (information générale, pas conseil juridique personnalisé)

## Module jurisprudence (optionnel)

Le module `search_jurisprudence` (Cour de cassation / Conseil d'État) est optionnel.
S'il est absent, le skill fonctionne normalement sur les codes législatifs uniquement.
