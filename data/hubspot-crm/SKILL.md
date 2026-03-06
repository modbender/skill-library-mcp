---
name: Skill HubSpot CRM — USC SYNERGY
description: Gestion complète du CRM HubSpot pour USC SYNERGY (centre de
  formation VAE). Permet de rechercher, créer, modifier des contacts et deals,
  gérer les associations, et suivre le pipeline commercial.
---

# Skill HubSpot CRM — USC SYNERGY
# Description
Gestion complète du CRM HubSpot pour USC SYNERGY (centre de formation VAE).
Permet de rechercher, créer, modifier des contacts et deals, gérer les associations, et suivre le pipeline commercial.

## Configuration requise
- Variable d'environnement : `HUBSPOT_ACCESS_TOKEN`
- Owner par défaut : Mark IBBOU (ID: 32587387)

## Pipelines
| Pipeline | ID | Usage |
|---|---|---|
| Sales Pipeline | default | Pipeline principal |
| Traitement des leads | 859619884 | Qualification prospects |

## Stages du Sales Pipeline (default)
| Stage | ID |
|---|---|
| Appointment Scheduled | appointmentscheduled |
| Qualified To Buy | qualifiedtobuy |
| Presentation Scheduled | presentationscheduled |
| Decision Maker Bought-In | decisionmakerboughtin |
| Contract Sent | contractsent |
| Closed Won | closedwon |
| Closed Lost | closedlost |

## Propriétés contact importantes
- `phone`, `mobilephone`, `hs_whatsapp_phone_number` — Téléphones
- `source` — Source du contact
- `ref` — Référence interne
- `objet` — Objet de la demande
- `fonction` — Fonction professionnelle

---

## Commandes disponibles

### 1. Rechercher un contact par téléphone
```bash
curl -s "https://api.hubapi.com/crm/v3/objects/contacts/search" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "filterGroups": [{
      "filters": [{
        "propertyName": "phone",
        "operator": "EQ",
        "value": "NUMERO_TEL"
      }]
    }],
    "properties": ["firstname","lastname","email","phone","mobilephone","hs_whatsapp_phone_number","source","ref","objet","fonction"]
  }'
```
> Remplacer `NUMERO_TEL` par le numéro au format international (+33...)
> Si aucun résultat, retenter avec `mobilephone` ou `hs_whatsapp_phone_number`

### 2. Rechercher un contact par email
```bash
curl -s "https://api.hubapi.com/crm/v3/objects/contacts/search" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "filterGroups": [{
      "filters": [{
        "propertyName": "email",
        "operator": "EQ",
        "value": "EMAIL_ADDRESS"
      }]
    }],
    "properties": ["firstname","lastname","email","phone","mobilephone","source","ref","objet"]
  }'
```

### 3. Rechercher un contact par nom
```bash
curl -s "https://api.hubapi.com/crm/v3/objects/contacts/search" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "filterGroups": [{
      "filters": [{
        "propertyName": "lastname",
        "operator": "EQ",
        "value": "NOM_FAMILLE"
      }]
    }],
    "properties": ["firstname","lastname","email","phone","mobilephone","source","ref","objet"]
  }'
```

### 4. Obtenir un contact par ID
```bash
curl -s "https://api.hubapi.com/crm/v3/objects/contacts/CONTACT_ID?properties=firstname,lastname,email,phone,mobilephone,hs_whatsapp_phone_number,source,ref,objet,fonction" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN"
```

### 5. Créer un nouveau contact
```bash
curl -s "https://api.hubapi.com/crm/v3/objects/contacts" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "properties": {
      "firstname": "PRENOM",
      "lastname": "NOM",
      "email": "EMAIL",
      "phone": "TELEPHONE",
      "source": "SOURCE",
      "hubspot_owner_id": "32587387"
    }
  }'
```

### 6. Mettre à jour un contact
```bash
curl -s -X PATCH "https://api.hubapi.com/crm/v3/objects/contacts/CONTACT_ID" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "properties": {
      "PROPRIETE": "VALEUR"
    }
  }'
```

### 7. Lister les deals d'un contact
```bash
curl -s "https://api.hubapi.com/crm/v4/objects/contacts/CONTACT_ID/associations/deals" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN"
```
> Récupère les IDs des deals, puis utiliser commande 9 pour les détails

### 8. Créer un deal
```bash
curl -s "https://api.hubapi.com/crm/v3/objects/deals" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "properties": {
      "dealname": "VAE - NOM_CANDIDAT - DIPLOME",
      "pipeline": "default",
      "dealstage": "appointmentscheduled",
      "amount": "MONTANT",
      "hubspot_owner_id": "32587387"
    }
  }'
```

### 9. Obtenir un deal par ID
```bash
curl -s "https://api.hubapi.com/crm/v3/objects/deals/DEAL_ID?properties=dealname,pipeline,dealstage,amount,closedate,hubspot_owner_id" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN"
```

### 10. Mettre à jour le stage d'un deal
```bash
curl -s -X PATCH "https://api.hubapi.com/crm/v3/objects/deals/DEAL_ID" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "properties": {
      "dealstage": "STAGE_ID"
    }
  }'
```

### 11. Associer un contact à un deal
```bash
curl -s -X PUT "https://api.hubapi.com/crm/v4/objects/deals/DEAL_ID/associations/contacts/CONTACT_ID" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '[{"associationCategory":"HUBSPOT_DEFINED","associationTypeId":3}]'
```

### 12. Créer une note sur un contact
```bash
curl -s "https://api.hubapi.com/crm/v3/objects/notes" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "properties": {
      "hs_note_body": "CONTENU_NOTE",
      "hs_timestamp": "'$(date -u +%Y-%m-%dT%H:%M:%S.000Z)'"
    }
  }'
```
> Après création, associer la note au contact avec commande 13

### 13. Associer une note à un contact
```bash
curl -s -X PUT "https://api.hubapi.com/crm/v4/objects/notes/NOTE_ID/associations/contacts/CONTACT_ID" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '[{"associationCategory":"HUBSPOT_DEFINED","associationTypeId":202}]'
```

### 14. Créer une tâche
```bash
curl -s "https://api.hubapi.com/crm/v3/objects/tasks" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "properties": {
      "hs_task_subject": "SUJET_TACHE",
      "hs_task_body": "DESCRIPTION",
      "hs_task_status": "NOT_STARTED",
      "hs_task_priority": "MEDIUM",
      "hs_timestamp": "'$(date -u +%Y-%m-%dT%H:%M:%S.000Z)'",
      "hubspot_owner_id": "32587387"
    }
  }'
```

### 15. Associer une tâche à un contact
```bash
curl -s -X PUT "https://api.hubapi.com/crm/v4/objects/tasks/TASK_ID/associations/contacts/CONTACT_ID" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '[{"associationCategory":"HUBSPOT_DEFINED","associationTypeId":204}]'
```

### 16. Lister les contacts récents (dernières 24h)
```bash
curl -s "https://api.hubapi.com/crm/v3/objects/contacts/search" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "filterGroups": [{
      "filters": [{
        "propertyName": "createdate",
        "operator": "GTE",
        "value": "'$(date -d '24 hours ago' +%s)000'"
      }]
    }],
    "sorts": [{"propertyName":"createdate","direction":"DESCENDING"}],
    "properties": ["firstname","lastname","email","phone","source","createdate"],
    "limit": 20
  }'
```

### 17. Lister les deals par stage
```bash
curl -s "https://api.hubapi.com/crm/v3/objects/deals/search" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "filterGroups": [{
      "filters": [{
        "propertyName": "dealstage",
        "operator": "EQ",
        "value": "STAGE_ID"
      }]
    }],
    "properties": ["dealname","dealstage","amount","closedate","pipeline"],
    "limit": 50
  }'
```

### 18. Compter les deals par pipeline
```bash
curl -s "https://api.hubapi.com/crm/v3/objects/deals/search" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "filterGroups": [{
      "filters": [{
        "propertyName": "pipeline",
        "operator": "EQ",
        "value": "PIPELINE_ID"
      }]
    }],
    "limit": 0
  }'
```
> Le champ `total` dans la réponse donne le nombre

### 19. Recherche globale de contacts
```bash
curl -s "https://api.hubapi.com/crm/v3/objects/contacts/search" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "TERME_RECHERCHE",
    "properties": ["firstname","lastname","email","phone","source"],
    "limit": 10
  }'
```

### 20. Supprimer un contact (archiver)
```bash
curl -s -X DELETE "https://api.hubapi.com/crm/v3/objects/contacts/CONTACT_ID" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN"
```
> Action irréversible — demander confirmation avant exécution

---

## Scénarios métier

### Nouveau prospect WhatsApp
1. Rechercher par téléphone (cmd 1) sur les 3 champs
2. Si inexistant → Créer contact (cmd 5) avec source="WhatsApp"
3. Créer deal VAE (cmd 8)
4. Associer contact au deal (cmd 11)
5. Créer note avec contexte conversation (cmd 12 + 13)

### Suivi candidat VAE
1. Rechercher contact (cmd 1/2/3)
2. Lister ses deals (cmd 7)
3. Récupérer détails deal (cmd 9)
4. Mettre à jour stage si progression (cmd 10)
5. Ajouter note de suivi (cmd 12 + 13)

### Rapport pipeline quotidien
1. Compter deals par pipeline (cmd 18)
2. Lister deals par stage (cmd 17) pour chaque stage actif
3. Lister contacts créés dernières 24h (cmd 16)

---

## Webhooks n8n (à configurer)
| Webhook | URL | Usage |
|---|---|---|
| Nouveau prospect | https://uscsynergy.app.n8n.cloud/webhook/hubspot-nouveau-prospect | Sync nouveau contact vers Digiforma |
| Sync Digiforma | https://uscsynergy.app.n8n.cloud/webhook/hubspot-sync-digiforma | Mise à jour bidirectionnelle |
| Enrichissement WhatsApp | https://uscsynergy.app.n8n.cloud/webhook/hubspot-enrichissement-whatsapp | Enrichir fiche depuis conversation WA |

> **Note** : Ces webhooks sont des placeholders. Les activer dans n8n quand les workflows seront prêts.
