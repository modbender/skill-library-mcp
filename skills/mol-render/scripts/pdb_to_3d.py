#!/usr/bin/env python3
"""PDB → 球棍模型 PNG 渲染器（POV-Ray 光线追踪）

Usage:
    python3 scripts/pdb_to_3d.py --pdb 1KF1 -o g4.png
    python3 scripts/pdb_to_3d.py --pdb structure.pdb -o out.png --chain A
    python3 scripts/pdb_to_3d.py --pdb 1KF1 -o ligand.png --ligand-only
"""

import argparse, sys, os, subprocess, tempfile, urllib.request, re
import numpy as np

# Reuse rendering infra from smiles_to_3d
sys.path.insert(0, os.path.dirname(__file__))
from smiles_to_3d import (
    ATOM_COLORS, ATOM_RADII, DEFAULT_COLOR, DEFAULT_RADIUS,
    SPHERE_SCALE, BOND_RADIUS,
    generate_pov, render_povray, find_best_angle,
)

# Element symbol → atomic number
ELEMENT_TO_Z = {
    'H': 1, 'HE': 2, 'LI': 3, 'BE': 4, 'B': 5, 'C': 6, 'N': 7, 'O': 8,
    'F': 9, 'NE': 10, 'NA': 11, 'MG': 12, 'AL': 13, 'SI': 14, 'P': 15,
    'S': 16, 'CL': 17, 'AR': 18, 'K': 19, 'CA': 20, 'TI': 22, 'V': 23,
    'CR': 24, 'MN': 25, 'FE': 26, 'CO': 27, 'NI': 28, 'CU': 29, 'ZN': 30,
    'SE': 34, 'BR': 35, 'MO': 42, 'I': 53, 'W': 74, 'PT': 78, 'AU': 79,
}

# Extend ATOM_COLORS for metals and other elements common in PDB
EXTRA_COLORS = {
    11: (0.67, 0.36, 0.95),  # Na - purple
    12: (0.54, 1.0,  0.0),   # Mg - green
    19: (0.56, 0.25, 0.83),  # K  - purple
    20: (0.24, 1.0,  0.0),   # Ca - green
    25: (0.61, 0.48, 0.78),  # Mn - purple
    26: (0.88, 0.40, 0.20),  # Fe - orange-brown
    27: (0.94, 0.56, 0.63),  # Co - pink
    28: (0.31, 0.82, 0.31),  # Ni - green
    29: (0.78, 0.50, 0.20),  # Cu - copper
    30: (0.49, 0.50, 0.69),  # Zn - slate
    34: (1.0,  0.63, 0.0),   # Se - orange
}

# Covalent radii (Å) for distance-based bond detection
COVALENT_RADII = {
    1: 0.31, 2: 0.28, 3: 1.28, 4: 0.96, 5: 0.84, 6: 0.76, 7: 0.71,
    8: 0.66, 9: 0.57, 10: 0.58, 11: 1.66, 12: 1.41, 13: 1.21, 14: 1.11,
    15: 1.07, 16: 1.05, 17: 1.02, 18: 1.06, 19: 2.03, 20: 1.76, 22: 1.60,
    23: 1.53, 24: 1.39, 25: 1.39, 26: 1.32, 27: 1.26, 28: 1.24, 29: 1.32,
    30: 1.22, 34: 1.20, 35: 1.20, 42: 1.54, 53: 1.39, 74: 1.62, 78: 1.36,
    79: 1.36,
}

BOND_TOLERANCE = 0.45  # Å tolerance for covalent bond detection

# Metal atoms that should not form covalent bonds (coordination only)
METAL_ELEMENTS = {11, 12, 19, 20, 22, 23, 24, 25, 26, 27, 28, 29, 30, 42, 74, 78, 79}


def download_pdb(pdb_id: str, out_dir: str = None) -> str:
    """Download PDB file from RCSB."""
    pdb_id = pdb_id.upper()
    url = f"https://files.rcsb.org/download/{pdb_id}.pdb"
    if out_dir is None:
        out_dir = tempfile.gettempdir()
    out_path = os.path.join(out_dir, f"{pdb_id}.pdb")
    if os.path.exists(out_path):
        print(f"Using cached PDB: {out_path}")
        return out_path
    print(f"Downloading PDB {pdb_id} from RCSB...")
    try:
        urllib.request.urlretrieve(url, out_path)
    except Exception as e:
        raise RuntimeError(f"Failed to download PDB {pdb_id}: {e}")
    print(f"Downloaded to {out_path}")
    return out_path


def parse_element(atom_name: str, line: str) -> str:
    """Extract element symbol from PDB line (cols 77-78) or atom name."""
    # Try columns 77-78 first (element field in PDB format)
    if len(line) >= 78:
        elem = line[76:78].strip()
        if elem and elem.upper() in ELEMENT_TO_Z:
            return elem.upper()
    # Fallback: parse from atom name
    name = atom_name.strip()
    if len(name) >= 2 and name[:2].upper() in ELEMENT_TO_Z:
        return name[:2].upper()
    if len(name) >= 1 and name[0].upper() in ELEMENT_TO_Z:
        return name[0].upper()
    return 'C'  # fallback


def parse_pdb(pdb_path: str, chain: str = None, residues: str = None,
              ligand_only: bool = False, no_hydrogen: bool = False,
              no_water: bool = True):
    """Parse PDB file, return atoms and bonds.
    
    Returns:
        atoms: list of dicts with keys: serial, name, resname, chain, resseq, x, y, z, element, z_num, is_hetatm
        bonds: list of (i, j) index pairs
    """
    atoms = []
    conect = {}  # serial -> list of bonded serials
    serial_to_idx = {}
    
    res_range = None
    if residues:
        # Parse "10-50" or "10,20,30" or "10-20,30-40"
        res_set = set()
        for part in residues.split(','):
            part = part.strip()
            if '-' in part:
                a, b = part.split('-', 1)
                for r in range(int(a), int(b) + 1):
                    res_set.add(r)
            else:
                res_set.add(int(part))
        res_range = res_set
    
    with open(pdb_path, 'r') as f:
        for line in f:
            rec = line[:6].strip()
            
            if rec in ('ATOM', 'HETATM'):
                is_hetatm = (rec == 'HETATM')
                atom_serial = int(line[6:11].strip())
                atom_name = line[12:16].strip()
                res_name = line[17:20].strip()
                chain_id = line[21]
                try:
                    res_seq = int(line[22:26].strip())
                except ValueError:
                    res_seq = 0
                x = float(line[30:38])
                y = float(line[38:46])
                z = float(line[46:54])
                element = parse_element(atom_name, line)
                z_num = ELEMENT_TO_Z.get(element, 6)
                
                # Filters
                if chain and chain_id != chain:
                    continue
                if res_range and res_seq not in res_range:
                    continue
                if ligand_only:
                    if not is_hetatm:
                        continue
                    if res_name == 'HOH':  # skip water
                        continue
                if no_water and res_name == 'HOH':
                    continue
                if no_hydrogen and z_num == 1:
                    continue
                
                idx = len(atoms)
                serial_to_idx[atom_serial] = idx
                atoms.append({
                    'serial': atom_serial,
                    'name': atom_name,
                    'resname': res_name,
                    'chain': chain_id,
                    'resseq': res_seq,
                    'x': x, 'y': y, 'z': z,
                    'element': element,
                    'z_num': z_num,
                    'is_hetatm': is_hetatm,
                })
            
            elif rec == 'CONECT':
                parts = line[6:].split()
                if len(parts) >= 2:
                    try:
                        src = int(parts[0])
                        if src not in conect:
                            conect[src] = []
                        for p in parts[1:]:
                            try:
                                dst = int(p)
                                conect[src].append(dst)
                            except ValueError:
                                break
                    except ValueError:
                        pass
    
    if not atoms:
        raise ValueError("No atoms found matching the given filters")
    
    print(f"Parsed {len(atoms)} atoms from PDB")
    
    # Build bonds
    bonds = []
    bond_set = set()
    
    # First try CONECT records
    conect_bonds = 0
    for src, dsts in conect.items():
        if src not in serial_to_idx:
            continue
        i = serial_to_idx[src]
        # Skip CONECT bonds involving metals (coordination, not covalent)
        if atoms[i]['z_num'] in METAL_ELEMENTS:
            continue
        for dst in dsts:
            if dst not in serial_to_idx:
                continue
            j = serial_to_idx[dst]
            if atoms[j]['z_num'] in METAL_ELEMENTS:
                continue
            pair = (min(i, j), max(i, j))
            if pair not in bond_set:
                bond_set.add(pair)
                bonds.append((i, j, 1.0))
                conect_bonds += 1
    
    if conect_bonds > 0:
        print(f"Found {conect_bonds} bonds from CONECT records")
    
    # Distance-based bond detection for atoms without CONECT bonds
    # Determine which atoms have bonds from CONECT
    atoms_with_conect = set()
    for i, j, _ in bonds:
        atoms_with_conect.add(i)
        atoms_with_conect.add(j)
    
    # For atoms without CONECT bonds (or if no CONECT at all), use distance
    coords_array = np.array([[a['x'], a['y'], a['z']] for a in atoms])
    z_nums = [a['z_num'] for a in atoms]
    
    need_distance = len(atoms_with_conect) < len(atoms) or conect_bonds == 0
    if need_distance:
        print("Using distance-based bond detection for remaining atoms...")
        dist_bonds = 0
        
        def should_bond(i, j):
            """Check if two atoms should be bonded by distance."""
            # Skip bonds involving metals (coordination, not covalent)
            if z_nums[i] in METAL_ELEMENTS or z_nums[j] in METAL_ELEMENTS:
                return False
            ri = COVALENT_RADII.get(z_nums[i], 0.77)
            rj = COVALENT_RADII.get(z_nums[j], 0.77)
            d = np.linalg.norm(coords_array[i] - coords_array[j])
            return d < ri + rj + BOND_TOLERANCE and d > 0.4
        
        # Use scipy for large molecules, fallback to brute force for small
        n = len(atoms)
        if n > 500:
            try:
                from scipy.spatial import cKDTree
                max_bond_dist = 2.5  # max reasonable covalent bond
                tree = cKDTree(coords_array)
                pairs = tree.query_pairs(max_bond_dist)
                for i, j in pairs:
                    if i in atoms_with_conect and j in atoms_with_conect:
                        continue
                    pair = (min(i, j), max(i, j))
                    if pair in bond_set:
                        continue
                    if should_bond(i, j):
                        bond_set.add(pair)
                        bonds.append((i, j, 1.0))
                        dist_bonds += 1
            except ImportError:
                for i in range(n):
                    if i in atoms_with_conect:
                        continue
                    for j in range(i + 1, n):
                        if j in atoms_with_conect and i in atoms_with_conect:
                            continue
                        pair = (i, j)
                        if pair in bond_set:
                            continue
                        if should_bond(i, j):
                            bond_set.add(pair)
                            bonds.append((i, j, 1.0))
                            dist_bonds += 1
        else:
            for i in range(n):
                if i in atoms_with_conect:
                    continue
                for j in range(i + 1, n):
                    if j in atoms_with_conect and i in atoms_with_conect:
                        continue
                    pair = (i, j)
                    if pair in bond_set:
                        continue
                    if should_bond(i, j):
                        bond_set.add(pair)
                        bonds.append((i, j, 1.0))
                        dist_bonds += 1
        
        print(f"Found {dist_bonds} bonds from distance detection")
    
    print(f"Total bonds: {len(bonds)}")
    return atoms, bonds, coords_array


def main():
    parser = argparse.ArgumentParser(description='PDB → Ball-and-Stick 3D PNG (POV-Ray)')
    parser.add_argument('--pdb', required=True,
                        help='PDB file path or 4-character PDB ID (e.g., 1KF1)')
    parser.add_argument('-o', '--output', default='pdb_molecule.png', help='Output PNG path')
    parser.add_argument('--width', type=int, default=1200)
    parser.add_argument('--height', type=int, default=1200)
    parser.add_argument('--chain', default=None, help='Select specific chain (e.g., A)')
    parser.add_argument('--residues', default=None,
                        help='Residue range (e.g., "1-50" or "10,20,30-40")')
    parser.add_argument('--ligand-only', action='store_true',
                        help='Only render ligands (HETATM, excluding water)')
    parser.add_argument('--no-hydrogen', action='store_true',
                        help='Hide hydrogen atoms')
    parser.add_argument('--no-water', action='store_true', default=True,
                        help='Remove water molecules (default: True)')
    parser.add_argument('--keep-water', action='store_true',
                        help='Keep water molecules')
    parser.add_argument('--bg', default='blue', help='Background color (white/black/blue)')
    parser.add_argument('--resolution', type=float, default=1.0,
                        help='Resolution multiplier (0.5 = half res, 2.0 = double)')
    parser.add_argument('--view', default='auto',
                        help='Viewing direction: auto/side/top/front or theta,phi in degrees')
    parser.add_argument('--sphere-scale', type=float, default=None,
                        help='Override sphere scale factor (default: auto based on atom count)')
    parser.add_argument('--bond-radius', type=float, default=None,
                        help='Override bond radius (default: auto based on atom count)')
    args = parser.parse_args()
    
    bg_map = {
        'white': (1, 1, 1),
        'black': (0, 0, 0),
        'blue': (0.85, 0.90, 0.95),
    }
    bg = bg_map.get(args.bg, (1, 1, 1))
    
    # Resolve PDB source
    pdb_input = args.pdb
    if len(pdb_input) == 4 and pdb_input.isalnum():
        # Looks like a PDB ID
        pdb_path = download_pdb(pdb_input)
    elif os.path.isfile(pdb_input):
        pdb_path = pdb_input
    else:
        print(f"Error: '{pdb_input}' is not a valid PDB file path or PDB ID", file=sys.stderr)
        sys.exit(1)
    
    no_water = args.no_water and not args.keep_water
    
    # Parse PDB
    atoms, bonds, coords = parse_pdb(
        pdb_path,
        chain=args.chain,
        residues=args.residues,
        ligand_only=args.ligand_only,
        no_hydrogen=args.no_hydrogen,
        no_water=no_water,
    )
    
    atomic_nums = [a['z_num'] for a in atoms]
    n_atoms = len(atoms)
    
    # Auto-adjust rendering params for large molecules
    global SPHERE_SCALE, BOND_RADIUS
    if args.sphere_scale is not None:
        sphere_scale = args.sphere_scale
    elif n_atoms > 1000:
        sphere_scale = 0.20
    elif n_atoms > 500:
        sphere_scale = 0.25
    elif n_atoms > 200:
        sphere_scale = 0.30
    else:
        sphere_scale = 0.35
    
    if args.bond_radius is not None:
        bond_radius = args.bond_radius
    elif n_atoms > 1000:
        bond_radius = 0.06
    elif n_atoms > 500:
        bond_radius = 0.07
    elif n_atoms > 200:
        bond_radius = 0.08
    else:
        bond_radius = 0.10
    
    print(f"Rendering {n_atoms} atoms with sphere_scale={sphere_scale}, bond_radius={bond_radius}")
    
    # Temporarily override module-level constants for generate_pov
    import smiles_to_3d as mol_mod
    orig_ss = mol_mod.SPHERE_SCALE
    orig_br = mol_mod.BOND_RADIUS
    mol_mod.SPHERE_SCALE = sphere_scale
    mol_mod.BOND_RADIUS = bond_radius
    
    # Also merge extra colors
    for z, c in EXTRA_COLORS.items():
        if z not in mol_mod.ATOM_COLORS:
            mol_mod.ATOM_COLORS[z] = c
    
    # Override ATOM_RADII for metals - make them bigger (ionic radii)
    METAL_DISPLAY_RADII = {
        19: 1.52,  # K+ ionic radius ~1.52 Å (big purple sphere)
        11: 1.16,  # Na+
        20: 1.14,  # Ca2+
        12: 0.86,  # Mg2+
        26: 0.92,  # Fe2+/3+
        30: 0.88,  # Zn2+
        29: 0.87,  # Cu2+
        25: 0.97,  # Mn2+
    }
    for z, r in METAL_DISPLAY_RADII.items():
        mol_mod.ATOM_RADII[z] = r
    
    # Apply resolution
    width = int(args.width * args.resolution)
    height = int(args.height * args.resolution)
    
    # Find best angle
    print("Finding best viewing angle...")
    view = args.view.lower()
    
    if view == 'auto':
        if n_atoms > 300:
            # For large molecules, use PCA but prefer side view (largest spread)
            from numpy.linalg import svd
            coords_c = coords - coords.mean(axis=0)
            U, S, Vt = svd(coords_c, full_matrices=False)
            # Use first principal component direction for side view  
            # (perpendicular to the axis of maximum extent gives side view)
            view_dir = Vt[2]  # smallest variance → looking along this sees max spread
            norm = np.linalg.norm(view_dir)
            theta = np.arccos(np.clip(view_dir[2] / norm, -1, 1))
            phi = np.arctan2(view_dir[1], view_dir[0])
            print(f"Using PCA angle: θ={np.degrees(theta):.1f}°, φ={np.degrees(phi):.1f}°")
        else:
            theta, phi = find_best_angle(coords, atomic_nums)
            print(f"Best angle: θ={np.degrees(theta):.1f}°, φ={np.degrees(phi):.1f}°")
    elif view == 'side':
        # Side view: look along Y axis
        from numpy.linalg import svd
        coords_c = coords - coords.mean(axis=0)
        U, S, Vt = svd(coords_c, full_matrices=False)
        # Look perpendicular to the longest axis
        view_dir = Vt[1]  # second principal component
        norm = np.linalg.norm(view_dir)
        theta = np.arccos(np.clip(view_dir[2] / norm, -1, 1))
        phi = np.arctan2(view_dir[1], view_dir[0])
        print(f"Side view angle: θ={np.degrees(theta):.1f}°, φ={np.degrees(phi):.1f}°")
    elif view == 'top':
        theta, phi = 0.01, 0.0
        print("Top view")
    elif view == 'front':
        theta, phi = np.pi / 2, 0.0
        print("Front view")
    elif ',' in view:
        parts = view.split(',')
        theta = np.radians(float(parts[0]))
        phi = np.radians(float(parts[1]))
        print(f"Custom angle: θ={float(parts[0]):.1f}°, φ={float(parts[1]):.1f}°")
    else:
        theta, phi = np.pi / 4, np.pi / 4
        print(f"Default angle: θ=45°, φ=45°")
    
    # Generate and render
    print("Generating POV-Ray scene...")
    scene = generate_pov(coords, atomic_nums, bonds, theta, phi,
                         width=width, height=height, bg_color=bg,
                         ring_centers=None)  # skip ring centers for PDB
    
    print(f"Rendering with POV-Ray ({width}×{height})...")
    render_povray(scene, args.output, width=width, height=height)
    print(f"Saved to {args.output}")
    
    # Restore
    mol_mod.SPHERE_SCALE = orig_ss
    mol_mod.BOND_RADIUS = orig_br


if __name__ == '__main__':
    main()
