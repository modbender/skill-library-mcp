#!/usr/bin/env python3
"""SMILES → 球棍模型 PNG 渲染器（POV-Ray 光线追踪）

Usage:
    python3 scripts/smiles_to_3d.py "CCO" -o ethanol.png
    python3 scripts/smiles_to_3d.py "c1ccccc1" -o benzene.png
"""

import argparse, sys, os, subprocess, tempfile
import numpy as np
from rdkit import Chem
from rdkit.Chem import AllChem

# ---------- constants ----------
ATOM_COLORS = {
    6:  (0.25, 0.25, 0.25),  # C - dark gray
    7:  (0.19, 0.31, 0.97),  # N - blue
    8:  (1.0,  0.05, 0.05),  # O - red
    9:  (0.56, 0.88, 0.31),  # F - green
    15: (1.0,  0.50, 0.0),   # P - orange
    16: (1.0,  1.0,  0.19),  # S - yellow
    17: (0.12, 0.94, 0.12),  # Cl - green
    35: (0.65, 0.16, 0.16),  # Br - brown
    53: (0.58, 0.0,  0.58),  # I - purple
    1:  (0.95, 0.95, 0.95),  # H - white
}
ATOM_RADII = {
    1: 0.40, 6: 0.76, 7: 0.71, 8: 0.66, 9: 0.57,
    15: 1.07, 16: 1.05, 17: 1.02, 35: 1.20, 53: 1.39,
}
DEFAULT_COLOR = (1.0, 0.41, 0.71)
DEFAULT_RADIUS = 0.77
SPHERE_SCALE = 0.35
BOND_RADIUS = 0.10


def smiles_to_mol3d(smiles: str):
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        raise ValueError(f"Invalid SMILES: {smiles}")
    mol = Chem.AddHs(mol)
    params = AllChem.ETKDGv3()
    params.randomSeed = 42
    if AllChem.EmbedMolecule(mol, params) < 0:
        AllChem.EmbedMolecule(mol, randomSeed=42)
    try:
        AllChem.MMFFOptimizeMolecule(mol, maxIters=500)
    except Exception:
        try:
            AllChem.UFFOptimizeMolecule(mol, maxIters=500)
        except Exception:
            pass
    return mol


def get_coords_and_info(mol):
    conf = mol.GetConformer()
    n = mol.GetNumAtoms()
    coords = np.array([conf.GetAtomPosition(i) for i in range(n)])
    atomic_nums = [mol.GetAtomWithIdx(i).GetAtomicNum() for i in range(n)]
    bonds = []
    for b in mol.GetBonds():
        bonds.append((b.GetBeginAtomIdx(), b.GetEndAtomIdx(), b.GetBondTypeAsDouble()))
    return coords, atomic_nums, bonds


def find_best_angle(coords, atomic_nums, n_theta=18, n_phi=36):
    """Find viewing angle using PCA + local refinement."""
    from numpy.linalg import svd
    radii = np.array([ATOM_RADII.get(z, DEFAULT_RADIUS) * SPHERE_SCALE for z in atomic_nums])
    coords_c = coords - coords.mean(axis=0)
    
    # PCA: third principal component (smallest variance) = best viewing direction
    U, S, Vt = svd(coords_c, full_matrices=False)
    view_dir = Vt[2]  # smallest variance direction
    norm = np.linalg.norm(view_dir)
    theta_pca = np.arccos(np.clip(view_dir[2] / norm, -1, 1))
    phi_pca = np.arctan2(view_dir[1], view_dir[0])
    
    def rotation_matrix(theta, phi):
        ct, st = np.cos(theta), np.sin(theta)
        cp, sp = np.cos(phi), np.sin(phi)
        Rz = np.array([[cp, sp, 0], [-sp, cp, 0], [0, 0, 1]])
        Rx = np.array([[1, 0, 0], [0, ct, st], [0, -st, ct]])
        return Rx @ Rz

    def overlap_score(theta, phi):
        R = rotation_matrix(theta, phi)
        xy = (coords_c @ R.T)[:, :2]
        score = 0.0
        for i in range(len(xy)):
            for j in range(i+1, len(xy)):
                d = np.linalg.norm(xy[i] - xy[j])
                md = radii[i] + radii[j]
                if d < md:
                    score += (md - d) / md
        return score

    # Fine search ±30° around PCA direction
    delta = np.radians(30)
    n_fine = 13  # steps in each direction
    best_score = float('inf')
    best_angles = (theta_pca, phi_pca)
    for i_t in range(n_fine):
        theta = theta_pca - delta + 2 * delta * i_t / (n_fine - 1)
        for i_p in range(n_fine):
            phi = phi_pca - delta + 2 * delta * i_p / (n_fine - 1)
            score = overlap_score(theta, phi)
            if score < best_score:
                best_score = score
                best_angles = (theta, phi)
                if score == 0:
                    return best_angles
    return best_angles


def generate_pov(coords, atomic_nums, bonds, theta, phi, width=1200, height=1200, bg_color=(1,1,1), ring_centers=None):
    """Generate POV-Ray scene string."""
    center_offset = coords.mean(axis=0)
    coords_c = coords - center_offset
    
    # Adjust ring centers to centered coordinates
    if ring_centers is not None:
        ring_centers = [(idx, atoms, rc - center_offset) for idx, atoms, rc in ring_centers]
    
    # Camera position from viewing angles
    dist = np.max(np.linalg.norm(coords_c, axis=1)) * 3.5 + 3
    cam_x = dist * np.sin(theta) * np.cos(phi)
    cam_y = dist * np.sin(theta) * np.sin(phi)
    cam_z = dist * np.cos(theta)
    
    lines = []
    lines.append(f"""
#version 3.7;
global_settings {{
  assumed_gamma 1.0
  radiosity {{
    pretrace_start 0.08
    pretrace_end 0.01
    count 80
    nearest_count 5
    error_bound 0.5
    recursion_limit 1
    brightness 0.6
  }}
}}

background {{ color rgb <{bg_color[0]}, {bg_color[1]}, {bg_color[2]}> }}

camera {{
  location <{cam_x:.4f}, {cam_z:.4f}, {cam_y:.4f}>
  look_at <0, 0, 0>
  up <0, 1, 0>
  right x * {width}/{height}
  angle 30
}}

// Key light (warm, from upper-left-front)
light_source {{
  <{cam_x*0.5 - dist*0.8:.4f}, {cam_z + dist*0.8:.4f}, {cam_y + dist*0.5:.4f}>
  color rgb <1.0, 0.95, 0.9> * 0.8
  area_light <2, 0, 0>, <0, 0, 2>, 5, 5
  adaptive 1
  jitter
}}

// Fill light (cool, from right)
light_source {{
  <{cam_x + dist*0.7:.4f}, {cam_z*0.3:.4f}, {cam_y - dist*0.5:.4f}>
  color rgb <0.7, 0.8, 1.0> * 0.3
  shadowless
}}

// Rim light (from behind)
light_source {{
  <{-cam_x*0.8:.4f}, {cam_z + dist*0.3:.4f}, {-cam_y*0.8:.4f}>
  color rgb <1, 1, 1> * 0.2
  shadowless
}}

// No ground plane
""")
    
    # Atoms
    for i, z in enumerate(atomic_nums):
        x, y_coord, z_coord = coords_c[i]
        r = ATOM_RADII.get(z, DEFAULT_RADIUS) * SPHERE_SCALE
        color = ATOM_COLORS.get(z, DEFAULT_COLOR)
        
        # Special finish for different atom types
        if z == 1:  # H - slightly translucent
            finish = "finish { ambient 0.08 diffuse 0.7 specular 0.6 roughness 0.02 reflection 0.05 }"
        else:
            finish = "finish { ambient 0.08 diffuse 0.65 specular 0.5 roughness 0.025 reflection 0.03 }"
        
        lines.append(f"""sphere {{
  <{x:.4f}, {z_coord:.4f}, {y_coord:.4f}>, {r:.4f}
  pigment {{ color rgb <{color[0]:.3f}, {color[1]:.3f}, {color[2]:.3f}> }}
  {finish}
}}""")
    
    # Bonds
    for i, j, bt in bonds:
        p1 = coords_c[i]
        p2 = coords_c[j]
        mid = (p1 + p2) / 2
        c1 = ATOM_COLORS.get(atomic_nums[i], DEFAULT_COLOR)
        c2 = ATOM_COLORS.get(atomic_nums[j], DEFAULT_COLOR)
        bond_finish = "finish { ambient 0.1 diffuse 0.7 specular 0.3 roughness 0.05 }"
        
        def add_cylinder(pa, pb, color, radius):
            lines.append(f"""cylinder {{
  <{pa[0]:.4f}, {pa[2]:.4f}, {pa[1]:.4f}>,
  <{pb[0]:.4f}, {pb[2]:.4f}, {pb[1]:.4f}>,
  {radius:.4f}
  pigment {{ color rgb <{color[0]:.3f}, {color[1]:.3f}, {color[2]:.3f}> }}
  {bond_finish}
}}""")
        
        if bt == 1.5:
            # Aromatic bond: solid outside + dashed inside (Chem3D style)
            d = p2 - p1
            bond_mid = mid
            # Find ring center for this bond
            inward = None
            if ring_centers is not None:
                for rc_idx, rc_atoms, rc_center in ring_centers:
                    if i in rc_atoms and j in rc_atoms:
                        # Direction from bond midpoint toward ring center
                        to_center = rc_center - bond_mid
                        # Project onto plane perpendicular to bond
                        along = d / (np.linalg.norm(d) + 1e-9)
                        to_center -= np.dot(to_center, along) * along
                        norm = np.linalg.norm(to_center)
                        if norm > 1e-9:
                            inward = to_center / norm * BOND_RADIUS * 1.2
                        break
            if inward is None:
                # Fallback: arbitrary perpendicular
                if abs(d[0]) < abs(d[1]):
                    perp = np.cross(d, [1, 0, 0])
                else:
                    perp = np.cross(d, [0, 1, 0])
                inward = perp / (np.linalg.norm(perp) + 1e-9) * BOND_RADIUS * 1.2
            # Solid bond on outside (away from ring center)
            off_out = -inward
            add_cylinder(p1 + off_out, mid + off_out, c1, BOND_RADIUS * 0.7)
            add_cylinder(mid + off_out, p2 + off_out, c2, BOND_RADIUS * 0.7)
            # Dashed bond on inside (toward ring center)
            off_in = inward
            n_segs = 3
            for s in range(n_segs):
                t_start = s / n_segs
                t_end = t_start + 0.5 / n_segs
                seg_a = p1 + (p2 - p1) * t_start + off_in
                seg_b = p1 + (p2 - p1) * t_end + off_in
                overall_t = (t_start + t_end) / 2
                seg_c = c1 if overall_t < 0.5 else c2
                add_cylinder(seg_a, seg_b, seg_c, BOND_RADIUS * 0.6)
        elif bt == 1:
            add_cylinder(p1, mid, c1, BOND_RADIUS)
            add_cylinder(mid, p2, c2, BOND_RADIUS)
        elif bt == 2:
            # Double bond: two solid lines, same offset logic as aromatic
            d = p2 - p1
            bond_mid = mid
            inward = None
            if ring_centers is not None:
                for rc_idx, rc_atoms, rc_center in ring_centers:
                    if i in rc_atoms and j in rc_atoms:
                        to_center = rc_center - bond_mid
                        along = d / (np.linalg.norm(d) + 1e-9)
                        to_center -= np.dot(to_center, along) * along
                        norm = np.linalg.norm(to_center)
                        if norm > 1e-9:
                            inward = to_center / norm * BOND_RADIUS * 1.2
                        break
            if inward is None:
                if abs(d[0]) < abs(d[1]):
                    perp = np.cross(d, [1, 0, 0])
                else:
                    perp = np.cross(d, [0, 1, 0])
                inward = perp / (np.linalg.norm(perp) + 1e-9) * BOND_RADIUS * 1.2
            # Two solid lines
            off_out = -inward
            off_in = inward
            add_cylinder(p1 + off_out, mid + off_out, c1, BOND_RADIUS * 0.7)
            add_cylinder(mid + off_out, p2 + off_out, c2, BOND_RADIUS * 0.7)
            add_cylinder(p1 + off_in, mid + off_in, c1, BOND_RADIUS * 0.7)
            add_cylinder(mid + off_in, p2 + off_in, c2, BOND_RADIUS * 0.7)
        elif bt == 3:
            d = p2 - p1
            if abs(d[0]) < abs(d[1]):
                perp = np.cross(d, [1, 0, 0])
            else:
                perp = np.cross(d, [0, 1, 0])
            perp = perp / (np.linalg.norm(perp) + 1e-9) * 0.1
            add_cylinder(p1, mid, c1, BOND_RADIUS * 0.6)
            add_cylinder(mid, p2, c2, BOND_RADIUS * 0.6)
            for sign in [1, -1]:
                off = perp * sign
                add_cylinder(p1 + off, mid + off, c1, BOND_RADIUS * 0.6)
                add_cylinder(mid + off, p2 + off, c2, BOND_RADIUS * 0.6)
    
    return '\n'.join(lines)


def render_povray(pov_scene, output_path, width=1200, height=1200):
    """Render POV-Ray scene to PNG."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.pov', delete=False) as f:
        f.write(pov_scene)
        pov_path = f.name
    
    png_path = pov_path.replace('.pov', '.png')
    
    try:
        cmd = [
            'povray',
            f'+I{pov_path}',
            f'+O{png_path}',
            f'+W{width}',
            f'+H{height}',
            '+A0.1',       # anti-aliasing
            '+AM2',        # AA method
            '+R3',         # AA depth
            '+Q9',         # quality
            '-D',          # no display
            '+UA',         # output alpha
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if result.returncode != 0:
            print(f"POV-Ray stderr: {result.stderr}", file=sys.stderr)
            raise RuntimeError(f"POV-Ray failed with code {result.returncode}")
        
        # Move to desired output
        import shutil
        shutil.move(png_path, output_path)
    finally:
        os.unlink(pov_path)
        if os.path.exists(png_path):
            os.unlink(png_path)


def main():
    parser = argparse.ArgumentParser(description='SMILES → Ball-and-Stick 3D PNG (POV-Ray)')
    parser.add_argument('smiles', help='SMILES string')
    parser.add_argument('-o', '--output', default='molecule.png', help='Output PNG path')
    parser.add_argument('--width', type=int, default=1200)
    parser.add_argument('--height', type=int, default=1200)
    parser.add_argument('--no-hydrogen', action='store_true', help='Remove explicit hydrogens')
    parser.add_argument('--kekulize', action='store_true', help='Kekulize aromatic bonds (draw as alternating single/double instead of aromatic)')
    parser.add_argument('--bg', default='blue', help='Background color (white/black/blue)')
    args = parser.parse_args()
    
    bg_map = {
        'white': (1, 1, 1),
        'black': (0, 0, 0),
        'blue': (0.85, 0.90, 0.95),
    }
    bg = bg_map.get(args.bg, (1, 1, 1))
    
    print(f"Parsing SMILES: {args.smiles}")
    mol = smiles_to_mol3d(args.smiles)
    
    if args.kekulize:
        try:
            Chem.Kekulize(mol, clearAromaticFlags=True)
            print("Kekulized: aromatic bonds converted to alternating single/double")
        except Exception as e:
            print(f"Kekulize failed ({e}), using original aromatic representation")
    
    if args.no_hydrogen:
        mol = Chem.RemoveHs(mol)
    
    coords, atomic_nums, bonds = get_coords_and_info(mol)
    print(f"Atoms: {len(atomic_nums)}, Bonds: {len(bonds)}")
    
    print("Finding best viewing angle...")
    theta, phi = find_best_angle(coords, atomic_nums)
    print(f"Best angle: θ={np.degrees(theta):.1f}°, φ={np.degrees(phi):.1f}°")
    
    # Compute ring centers for aromatic bond rendering
    ring_info = mol.GetRingInfo()
    ring_centers = []
    for idx, ring in enumerate(ring_info.AtomRings()):
        ring_atoms = set(ring)
        center = coords[list(ring)].mean(axis=0)
        ring_centers.append((idx, ring_atoms, center))
    
    print("Generating POV-Ray scene...")
    scene = generate_pov(coords, atomic_nums, bonds, theta, phi, 
                         width=args.width, height=args.height, bg_color=bg,
                         ring_centers=ring_centers)
    
    print("Rendering with POV-Ray (ray tracing)...")
    render_povray(scene, args.output, width=args.width, height=args.height)
    print(f"Saved to {args.output}")


if __name__ == '__main__':
    main()
