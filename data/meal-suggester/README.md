# Meal Suggester — Cuisine Intelligente

Un assistant de recettes qui apprend vos goûts et votre stock de cuisine au fil du temps. Chaque soir à 19h, reçois une idée de repas rapide (≤25 min) adaptée à vos préférences et ce que vous avez à la maison.

## 🎯 Fonctionnement

1. **Chaque soir à 19h** → tu reçois une suggestion de recette (jamais la même deux fois d'affilée)
2. **Tu essaies** → tu me dis si c'était bon, trop épicé, trop simple, etc.
3. **Tu me dis ce que tu as utilisé** → "on a consommé les lardons, les pois chiches, une courgette"
4. **J'apprends et je track** → je mémorise tes goûts, mets à jour le stock, et je suggère quoi acheter
5. **Ça s'améliore** → les suggestions deviennent de plus en plus pertinentes et variées

## 📁 Structure du Skill

```
meal-suggester/
├── SKILL.md                      # Documentation
├── README.md                     # Ce fichier
├── preferences/
│   ├── user1.md                  # First person's tastes, dislikes, favorites
│   └── user2.md                  # Second person's tastes, dislikes, favorites
├── inventory/
│   ├── stock.md                  # Ingrédients en stock (mise à jour régulière)
│   ├── history.md                # Historique des recettes essayées + feedback
│   └── shopping-list.md          # Ingrédients à acheter (auto-généré)
└── scripts/
    └── suggest-meal.sh           # Script qui génère les suggestions
```

## 🍳 Comment ça marche

### Recevoir une suggestion
Chaque soir à 19h, tu reçois une idée de recette. Il y a 15+ recettes différentes, donc jamais ennuyeux.

### Feedback après un repas
Après avoir essayé une recette, dis-moi:
- Ce que vous avez utilisé: "on a consommé les lardons, les pois chiches, une carotte"
- Ce que vous en avez pensé: "délicieux!", "trop épicé", "basique mais bon"
- Si vous referiez: "on pourrait refaire ça"

Je vais:
1. Mettre à jour `inventory/stock.md` automatiquement
2. Enregistrer dans `inventory/history.md`
3. Proposer des courses basées sur ce qui baisse
4. Adapter les prochaines suggestions

### Mise à jour du stock
Quand tu fais les courses:
- "J'ai acheté du poulet, des champignons, du lait"
- "On a fini les œufs, le riz"

Je mets à jour `inventory/stock.md` et les suggestions tiennent compte du nouveau stock.

### Shopping List (suggestions d'achats)
`inventory/shopping-list.md` se remplit automatiquement avec:
- Les ingrédients qui baissent régulièrement
- Ce qu'on utilise souvent
- Suggestions prioritaires

### Consulter ce que je sais de vous
- `preferences/user1.md` — First person's tastes, dislikes, allergies
- `preferences/user2.md` — Second person's tastes, dislikes, allergies
- `inventory/stock.md` — En ce moment vous avez...
- `inventory/shopping-list.md` — Vous devriez acheter...

## 🔧 Commandes

### Tester une suggestion maintenant
```bash
clawdbot skill run meal-suggester
```

### Voir l'historique complet
```bash
cat ~/.clawd/skills/meal-suggester/inventory/history.md
```

### Vérifier le stock
```bash
cat ~/.clawd/skills/meal-suggester/inventory/stock.md
```

### Voir la shopping list
```bash
cat ~/.clawd/skills/meal-suggester/inventory/shopping-list.md
```

## 📅 Planning

- ✅ Skill créé avec structure complète
- ✅ 15+ recettes prêtes avec variété
- ✅ Système de mémoire markdown en place
- ✅ Script de suggestion fonctionnel
- ✅ Cron job configuré (19h chaque jour)
- ✅ Tracking d'ingrédients utilisés
- ✅ Suggestions de shopping list
- 🔄 Apprentissage (à chaque feedback)

## 💡 Prochaines étapes

Voilà, c'est prêt! 

**Conseils d'utilisation:**
1. Ce soir à 19h, première suggestion arrive
2. Après avoir cuisiné, dis-moi simplement ce que vous avez utilisé
3. Si vous aimez/aimez pas, dis-le moi
4. Quand vous faites courses, mettez-moi à jour
5. Je vais apprendre et proposer des trucs de mieux en mieux adaptés

---

*Un ami cuisinier dans votre poche, sans allergies, avec bonne mémoire, et zéro jugement.*

