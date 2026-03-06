---
name: mol-render
description: Generate high-quality 3D ball-and-stick molecular renderings from SMILES strings or PDB structures using POV-Ray ray tracing.
metadata:
  openclaw:
    emoji: "🧪"
    requires:
      bins: ["povray", "python3"]
      pip: ["rdkit", "numpy"]
    optionalPip: ["biopython"]
---

# mol-render

Generate high-quality 3D ball-and-stick model PNG images from SMILES strings or PDB structures, rendered with POV-Ray ray tracing.

## Dependencies

**Required:**
- **rdkit** — SMILES parsing & 3D conformer generation
- **numpy** — coordinate transforms
- **povray** — ray tracing renderer

**Optional (PDB mode only):**
- **biopython** — PDB file parsing

Install:
```bash
pip install rdkit numpy
apt-get install -y povray

# For PDB support:
pip install biopython
```

## Usage

### SMILES Mode

```bash
python3 scripts/smiles_to_3d.py "SMILES" -o output.png
```

**Arguments:**
- `SMILES` — (positional) SMILES string (required)
- `-o`, `--output` — output PNG path (default: `molecule.png`)
- `--bg` — background color: `black` / `white` / `blue` (default: `blue`)
- `--no-hydrogen` — hide hydrogen atoms
- `--kekulize` — convert aromatic bonds to alternating single/double bonds

**Examples:**

```bash
# Ethanol
python3 scripts/smiles_to_3d.py "CCO" -o ethanol.png

# Benzene (white background, Kekulé style)
python3 scripts/smiles_to_3d.py "c1ccccc1" -o benzene.png --bg white --kekulize

# Caffeine
python3 scripts/smiles_to_3d.py "CN1C=NC2=C1C(=O)N(C(=O)N2C)C" -o caffeine.png

# Aspirin (no hydrogens)
python3 scripts/smiles_to_3d.py "CC(=O)OC1=CC=CC=C1C(=O)O" -o aspirin.png --no-hydrogen
```

### PDB Mode

```bash
python3 scripts/pdb_to_3d.py --pdb <PDB_ID_or_file> -o output.png
```

**Arguments:**
- `--pdb` — PDB file path or 4-character PDB ID (auto-downloads from RCSB) (required)
- `-o`, `--output` — output PNG path (default: `pdb_molecule.png`)
- `--chain` — select specific chain (e.g., `A`)
- `--residues` — residue range (e.g., `1-50` or `10,20,30-40`)
- `--ligand-only` — render only ligands (HETATM, excluding water)
- `--no-hydrogen` — hide hydrogen atoms
- `--no-water` / `--keep-water` — filter/keep water molecules (default: filter)
- `--bg` — background color: `black` / `white` / `blue` (default: `blue`)
- `--view` — viewing angle: `auto` / `side` / `top` / `front` or `θ,φ` in degrees (default: `auto`)
- `--resolution` — resolution multiplier, e.g., `0.5` for half, `2.0` for double (default: `1.0`)
- `--sphere-scale` — override sphere scale factor (default: auto)
- `--bond-radius` — override bond radius (default: auto)

**Examples:**

```bash
# Download and render G-quadruplex from RCSB
python3 scripts/pdb_to_3d.py --pdb 1KF1 --no-hydrogen -o g4.png

# Side view
python3 scripts/pdb_to_3d.py --pdb 1KF1 --no-hydrogen --view side -o g4_side.png

# Ligands only
python3 scripts/pdb_to_3d.py --pdb 1KF1 --ligand-only -o ligands.png

# Specific chain and residues
python3 scripts/pdb_to_3d.py --pdb 1KF1 --chain A --residues 1-12 -o partial.png

# Local PDB file
python3 scripts/pdb_to_3d.py --pdb structure.pdb -o out.png

# Large protein at lower resolution
python3 scripts/pdb_to_3d.py --pdb 2HYY --no-hydrogen --resolution 0.5 -o protein.png
```

## Output

- 1200×1200 PNG with POV-Ray ray tracing
- CPK color scheme (C=dark gray, O=red, N=blue, H=white, P=orange, S=yellow, K=purple, ...)
- Aromatic bonds rendered as solid + dashed lines (SMILES mode)
- Double bonds rendered as two parallel solid lines
- `--kekulize` option converts aromatic bonds to alternating single/double
- Metal ions displayed with ionic radius (large spheres), no coordination bonds drawn
- Auto-selects best viewing angle (PCA-based)
- Auto-scales sphere/bond sizes for large molecules
- Water molecules filtered by default (PDB mode)

## Known Limitations

- Very large molecules (>2000 atoms) may be slow to render (use `--resolution 0.5`)
- PDB mode renders all bonds as single bonds (no double/aromatic distinction)
- Metal coordination bonds are not rendered
- POV-Ray must be installed (`which povray`)
- `biopython` required only for PDB mode (optional dependency)

## License

MIT
