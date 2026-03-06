# GitHub Watch - Guide de scoring agent

## Profil cible
Ingenieur sysops/DevOps Linux senior. Pertinent : infra, containers, k8s, monitoring, CI/CD, securite systeme, reseau, automatisation, IaC, shell, performance systeme.

## Filtres automatiques (ecarter sans hesiter)
- Front-end pur (React, Vue, CSS frameworks)
- Mobile (iOS, Android, Flutter)
- Jeux video / game dev
- Data science pure, ML generique, LLM wrappers basiques
- Tutoriels "awesome-X" generiques sans valeur operationnelle

## Scoring par repo

**Highlight (inclure dans highlights[])** :
- Montee en stars inhabituellement rapide (ex: +500 en une semaine pour un outil infra)
- Outil veritablement nouveau qui adresse un vrai probleme ops
- Alternative credible a un outil etabli (remplace quelque chose de lourd)

**A conserver (inclure dans sections)** :
- Pertinent pour le profil sysops/devops
- Actif (recent commit ou stars > 50)
- Pas deja vu (filtre seen applique en amont)

**Ignorer (hors profil)** :
- Front, mobile, data, jeux
- Repos abandonnes (> 2 ans sans commit)
- Forks sans valeur ajoutee

## Caps stricts
- "En vogue cette semaine" : max 6 repos parmi trending
- "SysOps / DevOps" : max 6 repos parmi topic:sysops + topic:devops
- highlights : max 3 repos
- Un repo dans UNE seule section maximum

## Format de sortie (JSON strict)
```json
{
  "sections": [
    {
      "name": "En vogue cette semaine",
      "repos": [
        {
          "name": "owner/repo",
          "url": "https://github.com/owner/repo",
          "description": "...",
          "language": "Go",
          "stars_total": "12k",
          "stars_gained": "823",
          "reason": "Une phrase en francais expliquant pourquoi c'est pertinent."
        }
      ]
    },
    {
      "name": "SysOps / DevOps",
      "repos": [...]
    }
  ],
  "highlights": [
    {
      "name": "owner/repo",
      "url": "https://github.com/owner/repo",
      "reason": "Pourquoi c'est remarquable."
    }
  ]
}
```
