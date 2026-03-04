# Index T-codes SAP FI/CO — Référence rapide

## FI-GL (General Ledger)
| T-code | Description | S/4HANA |
|--------|-------------|---------|
| FB01 | Saisie pièce comptable | Remplacé par FB50 / Fiori F0717 |
| FB50 | Saisie écriture GL | ✅ Fiori F0717 |
| F-02 | Saisie écriture (écran classique) | Disponible mais FB50 préféré |
| FB03 | Affichage pièce comptable | ✅ Fiori F0718 |
| FB08 | Contre-passation pièce | ✅ |
| FBRA | Annulation compensation | ✅ |
| FBL3N | Postes individuels comptes GL | ✅ Fiori F0996 |
| FAGLB03 | Affichage soldes GL (New GL) | ✅ Fiori F1653 |
| FAGLL03 | Postes individuels GL (New GL) | ✅ |
| FAGL_FC_VALUATION | Réévaluation devises | ✅ |

## FI-AP (Accounts Payable)
| T-code | Description | S/4HANA |
|--------|-------------|---------|
| FB60 | Saisie facture fournisseur | ✅ Fiori F0859 |
| FB65 | Avoir fournisseur | ✅ |
| F-53 | Règlement fournisseur (manuel) | ✅ |
| F-44 | Compensation fournisseur | ✅ |
| F110 | Programme paiement automatique | ✅ Fiori F0765 |
| FBL1N | Postes individuels fournisseurs | ✅ Fiori F0997 |
| FK01/02/03 | Création/modif/affichage fournisseur | → BP (Business Partner) en S/4 |

## FI-AR (Accounts Receivable)
| T-code | Description | S/4HANA |
|--------|-------------|---------|
| FB70 | Saisie facture client | ✅ Fiori F2501 |
| F-28 | Encaissement client | ✅ |
| F-32 | Compensation client | ✅ |
| FBL5N | Postes individuels clients | ✅ Fiori F0998 |
| F150 | Programme relance (dunning) | ✅ Fiori F2166 |
| FD01/02/03 | Création/modif/affichage client | → BP en S/4 |

## FI-AA (Asset Accounting)
| T-code | Description | S/4HANA |
|--------|-------------|---------|
| AS01/02/03 | Création/modif/affichage immobilisation | ✅ Fiori F2217 |
| AW01N | Asset Explorer | ✅ |
| AFAB | Lancement amortissements | ✅ Fiori F4572 |
| AJAB | Changement exercice fiscal AA | ✅ |
| AJRW | Clôture exercice AA | ✅ |
| ABST2 | Réconciliation FI-AA ↔ FI-GL | Obsolète en S/4 (real-time posting) |
| ABAVN | Sortie d'immobilisation | ✅ |
| AIAB/AIBU | Immobilisation en cours (AuC) | ✅ |

## CO-CCA (Cost Center Accounting)
| T-code | Description | S/4HANA |
|--------|-------------|---------|
| KS01/02/03 | Création/modif/affichage centre de coûts | ✅ Fiori F1612 |
| KSB1 | Postes réels centres de coûts | ✅ Fiori F2425 |
| KSBT | Postes réels tous CdC | ✅ |
| KSS2 | Schéma de déversement de coûts | ✅ |
| KSU5 | Exécution assessment | ✅ Fiori F2712 |
| KSV5 | Exécution distribution | ✅ Fiori F2712 |
| KP06 | Planification coûts par nature | ✅ |
| KP26 | Planification coûts par type d'activité | ✅ |
| KSH1/2/3 | Hiérarchie centres de coûts | ✅ |

## CO-OPA (Internal Orders)
| T-code | Description | S/4HANA |
|--------|-------------|---------|
| KO01/02/03 | Création/modif/affichage ordre interne | ✅ |
| KO88 | Settlement ordre interne | ✅ |
| KOB1 | Postes réels ordres internes | ✅ |

## CO-PA (Profitability Analysis)
| T-code | Description | S/4HANA |
|--------|-------------|---------|
| KE30 | Reporting CO-PA | ✅ |
| KEA0 | Gestion operating concern | ✅ |
| KE21N | Saisie manuelle CO-PA | ✅ |
| KE4I | Maintenance champs de valeurs | ✅ |

## CO-PC (Product Costing)
| T-code | Description | S/4HANA |
|--------|-------------|---------|
| CK11N | Calcul coût de revient | ✅ |
| CK40N | Calcul de coûts en masse | ✅ |
| KKBC_ORD | Postes ordres de fabrication | ✅ |
| KKBC_PHA | Postes phases de production | ✅ |
| KKS1 | Calcul WIP (Work in Process) | ✅ |

## Configuration principales
| T-code | Domaine | Description |
|--------|---------|-------------|
| OB52 | FI | Ouverture/fermeture périodes comptables |
| OB58 | FI | Tolérance pour salariés |
| OBA7 | FI | Document types par société |
| OBC4 | FI | Tolérance pour comptes GL |
| OBBH | FI | Domiciliation bancaire |
| OBBW | FI | Define document type for parking |
| OBCR | FI | Assign default chart of accounts |
| OBYC | FI-MM | Account determination matières |
| VKOA | FI-SD | Account determination revenus |
| OKKP | CO | Activation composants CO |
| OKB9 | CO | Default account assignments |
| OKC6 | CO | Cycles assessment |
| OKES | CO-PA | Operating concern structure |
| AO90 | FI-AA | Activation New Asset Accounting |
