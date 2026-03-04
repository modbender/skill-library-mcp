# Messages d'erreur SAP FI/CO — Référence diagnostic

## Série F5 — Comptabilité générale (FI-GL)

| Code | Message | Cause | Solution |
|------|---------|-------|----------|
| F5 025 | Document type not defined for company code | Type document non affecté à la société | Config `/nOBA7` — ajouter le document type pour la société |
| F5 155 | Period XX/YYYY not open | Période comptable fermée | `/nOB52` — ouvrir la période pour le type de compte concerné |
| F5 201 | Account XXXXXX not defined in chart of accounts | Compte inexistant dans le plan comptable | Vérifier `/nFS00` ou créer le compte |
| F5 312 | Amount is zero | Montant à zéro dans l'écriture | Vérifier les montants saisis, contrôler les règles de TVA |
| F5 508 | Document does not balance | Pièce déséquilibrée débit/crédit | Vérifier les montants, devises, et taux de change |
| F5 600 | Entry already exists | Doublon de pièce | Vérifier si la pièce existe déjà via `/nFB03` |

## Série FK — Fournisseurs (FI-AP)

| Code | Message | Cause | Solution |
|------|---------|-------|----------|
| FK 009 | Company code not defined for vendor | Société non étendue pour le fournisseur | Étendre le fournisseur via `/nFK01` (ou BP en S/4) pour la société |
| FK 073 | Vendor is blocked for posting | Fournisseur bloqué au posting | Débloquer via `/nFK02` → Onglet "Payment transactions" |
| FK 083 | Payment method not maintained | Méthode de paiement non renseignée | Compléter les données bancaires fournisseur |

## Série FD — Clients (FI-AR)

| Code | Message | Cause | Solution |
|------|---------|-------|----------|
| FD 001 | Customer does not exist | Client inexistant dans la société | Créer ou étendre via `/nFD01` (ou BP en S/4) |
| FD 011 | Credit limit exceeded | Dépassement limite de crédit | Vérifier `/nFD32` — ajuster la limite ou libérer le blocage |

## Série AA — Immobilisations (FI-AA)

| Code | Message | Cause | Solution |
|------|---------|-------|----------|
| AA 010 | Asset does not exist | Immobilisation inexistante | Vérifier le numéro via `/nAS03` |
| AA 350 | Fiscal year not complete | Exercice fiscal FI-AA non clôturé | Exécuter `/nAJRW` pour clôturer l'exercice |
| AA 399 | Business area not maintained | Domaine d'activité manquant | Compléter la fiche immo via `/nAS02` |
| AA 555 | Depreciation area not active | Zone d'amortissement inactive | Activer via config `/nOAYZ` ou `/nAO90` |
| AA 687 | Depreciation area not posted | Zone non configurée pour posting | Config `/nOABD` — activer le real-time posting |

## Série K — Controlling (CO)

| Code | Message | Cause | Solution |
|------|---------|-------|----------|
| KD 002 | Order not found | Ordre interne inexistant | Vérifier via `/nKO03` |
| KD 106 | Order is closed | Ordre fermé, pas de posting possible | Rouvrir l'ordre via `/nKO02` → Status "Released" |
| KI 200 | Cost center does not exist | Centre de coûts inexistant pour la période | Vérifier dates validité via `/nKS03` |
| KI 235 | Cost center is locked | Centre de coûts verrouillé | Débloquer via `/nKS02` |
| KI 260 | No cost element for this posting | Nature comptable manquante | Créer via `/nKA06` (secondaire) ou vérifier le compte GL correspondant |

## Série M — Achats / Mouvements (FI-MM)

| Code | Message | Cause | Solution |
|------|---------|-------|----------|
| M7 061 | Account assignment required | Imputation analytique obligatoire | Renseigner le cost center/ordre/WBS dans la commande |
| M7 090 | No account determined | Compte non trouvé dans account determination | Vérifier `/nOBYC` pour le transaction event key |
| M8 147 | GR/IR account difference | Écart entre GR et IR | Analyser via `/nMR11` — rapprocher les entrées |
| M8 531 | Price variance too high | Écart de prix hors tolérance | Ajuster la tolérance dans `/nOMR6` ou corriger le prix |

## Série KP — Planification CO

| Code | Message | Cause | Solution |
|------|---------|-------|----------|
| KP 700 | Planning layout not found | Layout de planification inexistant | Vérifier la config `/nKP65` |
| KP 708 | Version not open for planning | Version de plan fermée | Ouvrir la version via `/nOKEQ` |

## Diagnostic rapide — Méthodologie

Quand un message d'erreur apparaît :

1. **Identifier le préfixe** : F5 = GL, FK = vendor, FD = customer, AA = assets, K = CO, M = MM
2. **Consulter la documentation** : `/nSE91` → Message class + numéro
3. **Vérifier le long text** : Dans le message d'erreur, cliquer sur l'icône "i" pour le texte détaillé
4. **Rechercher OSS** : SAP for Me → KBA search avec le code exact
5. **Analyser le contexte** : Transaction utilisée, données saisies, période, société
6. **Vérifier les autorisations** : Si l'erreur persiste, vérifier via `/nSU53` les derniers contrôles d'autorisation
