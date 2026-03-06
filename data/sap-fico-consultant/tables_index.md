# Index Tables SAP FI/CO — Référence rapide

## FI — Tables de pièces comptables

| Table | Description | Clé | S/4HANA |
|-------|-------------|-----|---------|
| BKPF | En-tête pièce comptable | BUKRS + BELNR + GJAHR | → ACDOCA (en-tête intégré) |
| BSEG | Postes pièce comptable | BUKRS + BELNR + GJAHR + BUZEI | → ACDOCA |
| BSIS | Postes ouverts comptes GL | BUKRS + HKONT + AUGDT | Obsolète → ACDOCA |
| BSAS | Postes soldés comptes GL | BUKRS + HKONT + AUGDT | Obsolète → ACDOCA |
| BSID | Postes ouverts clients | BUKRS + KUNNR | Obsolète → ACDOCA |
| BSAD | Postes soldés clients | BUKRS + KUNNR | Obsolète → ACDOCA |
| BSIK | Postes ouverts fournisseurs | BUKRS + LIFNR | Obsolète → ACDOCA |
| BSAK | Postes soldés fournisseurs | BUKRS + LIFNR | Obsolète → ACDOCA |

> ⚠️ **S/4HANA** : Les tables BSIS, BSAS, BSID, BSAD, BSIK, BSAK sont des **vues de compatibilité** sur ACDOCA. Elles existent encore mais ne sont plus des tables physiques.

## FI — Tables de référence

| Table | Description |
|-------|-------------|
| SKA1 | Plan comptable (niveau chart of accounts) |
| SKAT | Textes plan comptable |
| SKB1 | Plan comptable (niveau société) |
| T001 | Sociétés (company codes) |
| T001K | Périmètres analytiques (controlling areas) |
| T003 | Types de documents |
| T030 | Account determination automatique |
| T012 | Banques sociétés |
| T012K | Comptes bancaires sociétés |

## FI-AA — Immobilisations

| Table | Description | S/4HANA |
|-------|-------------|---------|
| ANLA | Données de base immobilisation | ✅ (maintenue) |
| ANLB | Depreciation terms | ✅ → FAAT_DOC_IT |
| ANLC | Valeurs cumulées immo | ✅ → FAAT_PLAN_VALUES |
| ANLH | Historique immobilisation | ✅ |
| ANLP | Valeurs périodiques amortissement | → ACDOCA |
| ANEK | En-tête pièce immobilisation | → ACDOCA |
| ANEP | Postes pièce immobilisation | → ACDOCA |
| FAAT_DOC_IT | Postes document New AA | Nouvelle table S/4 |
| FAAT_PLAN_VALUES | Valeurs planifiées New AA | Nouvelle table S/4 |

## CO — Tables de totaux

| Table | Description | Clé |
|-------|-------------|-----|
| COSS | Totaux CO — coûts secondaires | OBJNR + GJAHR + WRTTP + VERSN + KSTAR |
| COSP | Totaux CO — coûts primaires | OBJNR + GJAHR + WRTTP + VERSN + KSTAR |
| COBK | En-tête document CO | KOKRS + BESSION |
| COEP | Postes individuels CO | OBJNR + GJAHR + BUZEI |
| COEJ | Postes individuels CO (exercice) | OBJNR + GJAHR |

> ⚠️ **S/4HANA** : COSS, COSP, COBK, COEP sont des **vues de compatibilité** sur ACDOCA.

## CO — Tables de référence

| Table | Description |
|-------|-------------|
| CSKS | Centres de coûts (données de base) |
| CSKT | Textes centres de coûts |
| CSLA | Types d'activité |
| CSKA | Natures comptables (cost elements) — niveau chart |
| CSKB | Natures comptables — niveau controlling area |
| SETNODE/SETHEADER | Groupes et hiérarchies |
| CEPC | Centres de profit (données de base) |
| AUFK | Ordres internes (données de base) |

## CO-PA — Profitability Analysis

| Table | Description |
|-------|-------------|
| CE1xxxx | Postes réels CO-PA (xxxx = operating concern) |
| CE2xxxx | Postes plan CO-PA |
| CE3xxxx | Structure segments CO-PA |
| CE4xxxx | Totaux CO-PA |

> Les "xxxx" correspondent au code de l'operating concern (ex: CE1S001 si OC = S001)

## S/4HANA — Nouvelles tables clés

| Table | Description | Remplace |
|-------|-------------|----------|
| ACDOCA | Universal Journal — postes réels | BSEG, BSIS/BSAS, BSID/BSAD, BSIK/BSAK, COEP, COSS, COSP, ANLP |
| ACDOCP | Universal Journal — postes plan | Données plan CO |
| ACDOCU | Universal Journal — données complémentaires | Extensions custom |
| FINSC_CFLEXA | Central Finance — postes réels | Réplication cross-system |
| FINSC_CFLED | Central Finance — totaux | Réplication agrégée |

## Intégration FI-MM

| Table | Description |
|-------|-------------|
| EKBE | Historique achats (GR, IR, retours) |
| MSEG | Mouvements matières |
| MKPF | En-tête mouvements matières |
| WRX | Soldes compte GR/IR |

## Intégration FI-SD

| Table | Description |
|-------|-------------|
| VBRK | En-tête facturation SD |
| VBRP | Postes facturation SD |
| VBAK | En-tête commande vente |
| VBAP | Postes commande vente |
