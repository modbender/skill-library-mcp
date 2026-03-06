---
name: AI 3D Model Generator
description: Génération automatique de modèles 3D détaillés à partir de
  descriptions textuelles.
---

# AI 3D Model Generator

Génération automatique de modèles 3D détaillés à partir de descriptions textuelles.

## Architecture

```
Prompt utilisateur → LLM (Kimi/Gemini) → Code Python/Trimesh → Génération STL → Export
```

## Pipeline Automatique

### 1. Prompt Engineering (template)

Crée un fichier `prompts/3d-generator.txt`:

```markdown
Tu es un expert en modélisation 3D paramétrique. Génère un script Python utilisant Trimesh 
pour créer le modèle 3D décrit ci-dessous.

RÈGLES:
- Utilise trimesh.creation (icosphere, cylinder, cone, torus, box)
- Pour les détails complexes: utiliser des boucles et paramètres
- Résolution élevée: subdivisions=4-5 pour les sphères, sections=32-64 pour cylindres
- Ajouter des détails de surface (panneaux, textures géométriques)
- Structure modulaire avec fonctions réutilisables
- Exporter en STL binaire à la fin

SCRIPT TEMPLATE:
```python
#!/usr/bin/env python3
import numpy as np
import trimesh
from trimesh.creation import icosphere, cylinder, cone, torus, box
from trimesh.transformations import rotation_matrix
import os

EXPORT_DIR = "/home/celluloid/.openclaw/workspace/stl-exports"

def save_mesh(mesh, filename):
    os.makedirs(EXPORT_DIR, exist_ok=True)
    filepath = os.path.join(EXPORT_DIR, filename)
    mesh.export(filepath)
    print(f"✓ Exporté: {filepath}")
    print(f"  Triangles: {len(mesh.faces):,}")
    return filepath

def rotate_mesh(mesh, angle, axis, point=None):
    if point is None:
        point = [0, 0, 0]
    mat = rotation_matrix(angle, axis, point)
    mesh.apply_transform(mat)
    return mesh

# === MODÈLE PRINCIPAL ===
def create_model():
    meshes = []
    
    # [GÉNÈRE LE MODÈLE ICI]
    
    # Fusion et optimisation
    combined = trimesh.util.concatenate(meshes)
    combined.merge_vertices()
    return combined

if __name__ == "__main__":
    mesh = create_model()
    save_mesh(mesh, "[NOM_DU_MODELE].stl")
```

DESCRIPTION DU MODÈLE À CRÉER:
{{USER_DESCRIPTION}}

Génère uniquement le code Python complet, sans explications.
```

## 2. Skill OpenClaw Automatisé

Crée le fichier `~/.openclaw/workspace/skills/ai-3d-generator/SKILL.md`:

### Utilisation

#### Génération simple
```bash
# Génère un modèle à partir d'une description
~/.openclaw/workspace/skills/ai-3d-generator/scripts/generate-from-prompt.sh "vaisseau spatial avec ailes delta et cockpit vitré"
```

#### Génération avec paramètres
```bash
# Avec spécifications techniques
~/.openclaw/workspace/skills/ai-3d-generator/scripts/generate-from-prompt.sh \
  "robot humanoïde articulé" \
  --scale=50mm \
  --detail=high \
  --output=robot.stl
```

### Processus

1. **Analyse du prompt** → Extraction entités (formes, dimensions, détails)
2. **Génération code** → LLM crée script Python/Trimesh
3. **Validation syntaxique** → Vérification imports et structure
4. **Exécution** → Génération mesh + export STL
5. **Post-traitement** → Optimisation, vérification manifold

## 3. Exemples de Prompts Efficaces

### Bon prompt (détaillé, technique):
```
Crée un château médiéval avec:
- Tours cylindriques aux 4 coins (diamètre 8mm, hauteur 25mm)
- Créneaux sur les tours
- Mur d'enceinte carré (40x40mm)
- Pont-levis à l'avant
- Texture de pierre avec des blocs individuels
- Échelle 1:100 pour impression 3D
```

### Mauvais prompt (trop vague):
```
Fais-moi un château
```

## 4. Automatisation Complète

### Cron job pour génération régulière
```json
{
  "name": "3d:generate-daily",
  "schedule": {"kind": "cron", "expr": "0 9 * * *"},
  "payload": {
    "message": "Génère un modèle 3D aléatoire du jour (animaux, architecture, véhicules) et exporte en STL",
    "model": "openrouter/moonshotai/kimi-k2.5"
  }
}
```

## 5. Optimisations pour Ultra-Détail

### Techniques Avancées

#### Sculpting procédural
```python
# Ajouter du bruit de surface pour texture
def add_surface_noise(mesh, amplitude=0.1):
    vertices = mesh.vertices.copy()
    noise = np.random.normal(0, amplitude, vertices.shape)
    mesh.vertices = vertices + noise
    return mesh
```

#### Détails paramétriques
```python
# Générer des détails répétitifs
for i in range(100):  # 100 panneaux de surface
    angle = i * 2 * np.pi / 100
    panel = create_detailed_panel()
    position_on_surface(panel, radius=20, angle=angle)
```

#### Boolean operations optimisées
```python
# Utiliser trimesh.boolean pour les découpes complexes
from trimesh.boolean import difference, union, intersection

result = difference(base_mesh, cutting_tool)
```

## 6. Workflow Complet Exemple

### Commande OpenClaw:
```
Génère un modèle 3D d'une station spatiale en anneau avec:
- Anneau principal de 80mm de diamètre
- 6 modules d'habitation sur l'anneau
- Sphère centrale de commande
- Antennes et panneaux solaires
- Style cyberpunk avec câbles et tuyaux
Exporte en STL haute résolution.
```

### Réponse Automatique:
1. LLM génère le script Python (~30s)
2. Exécution Trimesh (~1-2min)
3. Export STL optimisé
4. Rapport: triangles, volume, dimensions

## Notes

- Pour les modèles très complexes (>100k triangles), prévoir plus de temps
- Utiliser `trimesh.smoothing` pour lisser les surfaces si nécessaire
- Vérifier que le modèle est "manifold" (étanche) pour l'impression 3D
- Sauvegarder les scripts générés pour réutilisation/modification
