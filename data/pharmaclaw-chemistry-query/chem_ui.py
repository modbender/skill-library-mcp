import gradio as gr
import subprocess
import json
import os
import pandas as pd
from PIL import Image

WORK_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scripts")

def _validate_smiles(smiles):
    """Validate SMILES before passing to subprocess."""
    if not smiles or not isinstance(smiles, str):
        raise ValueError("SMILES must be a non-empty string")
    smiles = smiles.strip()
    if len(smiles) > 2000:
        raise ValueError("SMILES too long (max 2000 chars)")
    if '\x00' in smiles:
        raise ValueError("Invalid SMILES: null bytes not allowed")
    # RDKit validation
    from rdkit import Chem
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        raise ValueError(f"Invalid SMILES: '{smiles}'")
    return Chem.MolToSmiles(mol, canonical=True)


def analyze(smiles):
    smiles = _validate_smiles(smiles)
    # Props
    proc = subprocess.run(["python3", "rdkit_mol.py", "--smiles", smiles, "--action", "props"], cwd=WORK_DIR, capture_output=True, text=True)
    props = json.loads(proc.stdout)
    
    # Draw PNG
    subprocess.run(["python3", "rdkit_mol.py", "--smiles", smiles, "--action", "draw", "--output", "mol.png"], cwd=WORK_DIR)
    img = Image.open(os.path.join(WORK_DIR, "mol.png"))
    
    # ADMET
    proc = subprocess.run(["python3", "admet_predict.py", "--smiles", smiles], cwd=WORK_DIR, capture_output=True, text=True)
    admet = json.loads(proc.stdout)
    
    return props, img, admet

iface = gr.Interface(
    fn=analyze,
    inputs=gr.Textbox(label="SMILES", value="CCO"),
    outputs=[gr.JSON(label="Props"), gr.Image(label="2D Viz"), gr.JSON(label="ADMET")],
    title="Chemistry Query Agent 🧪",
    description="PubChem/RDKit analysis"
)

if __name__ == "__main__":
    iface.launch(share=False)