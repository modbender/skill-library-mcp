#!/usr/bin/env python3
"""
Exemple: Générateur de modèle 3D paramétrique avancé
Ce script peut être appelé automatiquement par OpenClaw avec des paramètres variables
"""

import numpy as np
import trimesh
from trimesh.creation import icosphere, cylinder, cone, torus, box
from trimesh.transformations import rotation_matrix
from trimesh.smoothing import filter_laplacian
import os
import sys

EXPORT_DIR = "/home/celluloid/.openclaw/workspace/stl-exports"

class Model3DGenerator:
    """Générateur de modèles 3D paramétriques"""
    
    def __init__(self, name):
        self.name = name
        self.meshes = []
        self.detail_level = "high"  # low, medium, high, ultra
        
    def set_detail_level(self, level):
        """Définit le niveau de détail"""
        self.detail_level = level
        
    def get_resolution(self):
        """Retourne les paramètres de résolution selon le niveau"""
        resolutions = {
            "low": {"sphere_sub": 2, "cyl_sections": 16, "torus_maj": 64},
            "medium": {"sphere_sub": 3, "cyl_sections": 24, "torus_maj": 96},
            "high": {"sphere_sub": 4, "cyl_sections": 32, "torus_maj": 128},
            "ultra": {"sphere_sub": 5, "cyl_sections": 64, "torus_maj": 256}
        }
        return resolutions.get(self.detail_level, resolutions["high"])
    
    def add_sphere(self, radius, position=(0,0,0), name="sphere"):
        """Ajoute une sphère avec détails de surface"""
        res = self.get_resolution()
        sphere = icosphere(radius=radius, subdivisions=res["sphere_sub"])
        sphere.apply_translation(position)
        sphere.metadata["name"] = name
        self.meshes.append(sphere)
        return sphere
    
    def add_cylinder(self, radius, height, position=(0,0,0), rotation=None, name="cylinder"):
        """Ajoute un cylindre avec orientation"""
        res = self.get_resolution()
        cyl = cylinder(radius=radius, height=height, sections=res["cyl_sections"])
        
        if rotation:
            angle, axis = rotation
            self._rotate_mesh(cyl, angle, axis)
        
        cyl.apply_translation(position)
        cyl.metadata["name"] = name
        self.meshes.append(cyl)
        return cyl
    
    def add_torus(self, major_r, minor_r, position=(0,0,0), rotation=None, name="torus"):
        """Ajoute un tore"""
        res = self.get_resolution()
        tor = torus(major_radius=major_r, minor_radius=minor_r, 
                    major_sections=res["torus_maj"], minor_sections=res["cyl_sections"])
        
        if rotation:
            angle, axis = rotation
            self._rotate_mesh(tor, angle, axis)
            
        tor.apply_translation(position)
        tor.metadata["name"] = name
        self.meshes.append(tor)
        return tor
    
    def add_surface_details(self, base_mesh, count=50, detail_size=0.5):
        """Ajoute des détails de surface (panneaux, rivets)"""
        import numpy as np
        
        # Obtenir les normales des faces
        face_centers = base_mesh.triangles_center
        face_normals = base_mesh.face_normals
        
        for i in range(min(count, len(face_centers))):
            if i % (len(face_centers) // count) == 0:
                center = face_centers[i]
                normal = face_normals[i]
                
                # Créer un petit détail
                detail = icosphere(radius=detail_size, subdivisions=1)
                
                # Positionner sur la surface
                detail.apply_translation(center + normal * detail_size * 0.5)
                self.meshes.append(detail)
    
    def _rotate_mesh(self, mesh, angle, axis):
        """Applique une rotation à un mesh"""
        mat = rotation_matrix(angle, axis)
        mesh.apply_transform(mat)
    
    def smooth_surfaces(self, iterations=2):
        """Lisse les surfaces (Laplacian smoothing)"""
        for mesh in self.meshes:
            if len(mesh.faces) > 100:  # Éviter de lisser les petits détails
                filter_laplacian(mesh, iterations=iterations)
    
    def export(self, filename=None, optimize=True):
        """Exporte le modèle final en STL"""
        if not filename:
            filename = f"{self.name}.stl"
        
        if not self.meshes:
            print("❌ Erreur: Aucun mesh à exporter")
            return None
        
        print(f"Fusion de {len(self.meshes)} composants...")
        
        # Fusionner tous les meshes
        combined = trimesh.util.concatenate(self.meshes)
        
        if optimize:
            print("Optimisation du mesh...")
            combined.merge_vertices()
            combined.remove_duplicate_faces()
            combined.remove_unreferenced_vertices()
            
            # Vérifier que c'est manifold (étanche)
            if not combined.is_watertight:
                print("⚠️  Attention: Le mesh n'est pas étanche (non-manifold)")
        
        # Export
        os.makedirs(EXPORT_DIR, exist_ok=True)
        filepath = os.path.join(EXPORT_DIR, filename)
        combined.export(filepath)
        
        print(f"\n✅ Exporté: {filepath}")
        print(f"   Triangles: {len(combined.faces):,}")
        print(f"   Volume: {combined.volume/1000:.1f} cm³")
        print(f"   Dimensions: {combined.extents}")
        
        return filepath


# === EXEMPLE D'UTILISATION ===
def create_advanced_space_station():
    """Crée une station spatiale avancée paramétrique"""
    
    gen = Model3DGenerator("advanced_space_station")
    gen.set_detail_level("high")
    
    print("🚀 Génération station spatiale avancée...\n")
    
    # Sphère centrale
    print("  → Sphère centrale")
    gen.add_sphere(radius=25, name="core_sphere")
    
    # Anneau principal
    print("  → Anneau orbital")
    gen.add_torus(major_r=70, minor_r=4, name="main_ring")
    
    # Modules sur l'anneau (12 modules)
    print("  → Modules d'habitation")
    for i in range(12):
        angle = i * 2 * np.pi / 12
        x = 70 * np.cos(angle)
        y = 70 * np.sin(angle)
        
        gen.add_cylinder(
            radius=6, height=15,
            position=(x, y, 0),
            rotation=(np.pi/2, [0, 1, 0]),
            rotation_angle=angle,
            name=f"module_{i}"
        )
    
    # Pylônes de communication
    print("  → Pylônes")
    for i in range(4):
        angle = i * np.pi / 2
        x = 50 * np.cos(angle)
        y = 50 * np.sin(angle)
        
        gen.add_cylinder(
            radius=3, height=40,
            position=(x, y, 20),
            name=f"pylon_{i}"
        )
    
    # Détails de surface
    print("  → Détails de surface")
    # Note: add_surface_details serait appelé ici sur la sphère centrale
    
    return gen


if __name__ == "__main__":
    # Exemple d'utilisation
    gen = create_advanced_space_station()
    gen.export("advanced_station.stl")
