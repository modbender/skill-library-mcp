---
name: phenosnap-phenotype-extractor
description: Extract clinical phenotypes and medication entities from user-provided text using PhenoSnap, producing a timestamped JSON output.
user-invocable: true
metadata: {"openclaw":{"requires":{"bins":["python3"],"anyBins":["git","curl","powershell"],"env":["HPO_OBO_PATH"]},"primaryEnv":"HPO_OBO_PATH"}}
---

## When to use
Use this skill when the user provides **their own**:
- clinical phenotypes / symptoms / diagnoses (free text, bullet lists, clinical note-like text), and/or
- drugs/medications (names, dosages, frequencies).

Examples that should trigger:
- “Symptoms: ataxia, seizures, developmental delay. Meds: levetiracetam 500 mg BID.”
- “I’m taking metformin 500mg daily and have fatigue, polyuria, blurry vision.”

## When NOT to use
Do **not** use this skill when:
- The user asks general questions (e.g., “What is HPO?”, “What is a phenotype?”, “What is GLP-1?”).
- The user provides text that is not personal clinical information (news articles, academic paragraphs, code, etc.).
- The user asks you to interpret *someone else’s* private clinical record (PHI) without clear permission.

## Safety & privacy
- Treat user input as potentially sensitive clinical information.
- **Do not upload** user text or extracted results anywhere (this skill is local-only).
- Before writing any input to disk, **redact obvious identifiers**:
  - emails, phone numbers, street addresses
  - MRN-like long numeric identifiers (e.g., 8+ digits)
  - names when clearly presented as “Name: …”
- If the message appears to include **highly identifying PHI** (e.g., name + DOB + address, or name + MRN), **pause and ask for confirmation** to proceed, recommending the user remove identifiers first.

## Requirements / setup
- Python: `python3` available on PATH.
- Network access (only for initial PhenoSnap download if missing).
- HPO OBO file:
  - Default expected path: `{baseDir}/resources/hp.obo`
  - Override path via environment variable: `HPO_OBO_PATH`
  - This skill **does not auto-download** `hp.obo`. You must supply it.

Recommended (best practice):
- Use a virtual environment (venv/conda) before running this skill, because it may install Python packages via `pip`.

## Inputs & outputs
- Input text file (redacted):
  - `{baseDir}/artifacts/phenosnap_inputs/input_<YYYYMMDD_HHMMSS>.txt`
- Output JSON file (timestamped):
  - `{baseDir}/artifacts/phenosnap_outputs/phenotypes_<YYYYMMDD_HHMMSS>.json`
- Third-party download cache:
  - `{baseDir}/third_party/phenosnap_main.zip`
  - `{baseDir}/third_party/get-pip.py`

## Detection heuristic (activation check)
Trigger if the user message contains **any** of:
- phenotype cues: `symptom(s)`, `phenotype(s)`, `Dx`, `diagnosis`, `PMH`, `Hx`, `history of`, or a symptom-like list
- medication cues: `meds`, `medications`, `taking`, `prescribed`, plus patterns like:
  - dosages: `\b\d+(\.\d+)?\s?(mg|mcg|g|ml|units)\b`
  - frequencies: `qd`, `q.d.`, `bid`, `b.i.d.`, `tid`, `t.i.d.`, `qhs`, `qAM`, `qPM`, `daily`, `weekly`

Do not trigger for purely informational questions without user-provided phenotype/medication content.

---

# Procedure

## 0) Create required directories
Create if missing:
- `{baseDir}/PhenoSnap/`
- `{baseDir}/artifacts/phenosnap_inputs/`
- `{baseDir}/artifacts/phenosnap_outputs/`
- `{baseDir}/resources/`
- `{baseDir}/third_party/`

## 1) Confirm / redact sensitive identifiers
1) Scan the user message for identifiers (email/phone/address/MRN/name fields).
2) If strongly identifying PHI is present (name + DOB/address/MRN):
   - Ask the user to confirm proceeding and recommend removing identifiers.
3) Produce a redacted version of the user text:
   - Replace emails with `[REDACTED_EMAIL]`
   - Replace phone numbers with `[REDACTED_PHONE]`
   - Replace long numeric IDs with `[REDACTED_ID]`
   - Replace address-like patterns with `[REDACTED_ADDRESS]`
   - Replace explicit “Name: …” fields with `Name: [REDACTED_NAME]`

## 2) Ensure PhenoSnap exists locally
Target location: `{baseDir}/PhenoSnap/`

### 2A) If `{baseDir}/PhenoSnap/` exists and contains `extract_phenotypes.py`
Proceed to dependency self-test.

### 2B) If `{baseDir}/PhenoSnap/` does NOT exist (or missing `extract_phenotypes.py`)
Prefer git; fallback to zip.

#### If `git` is available
Run:
- `git clone https://github.com/WGLab/PhenoSnap.git "{baseDir}/PhenoSnap"`

#### If `git` is NOT available
Download zip:
- URL: `https://github.com/WGLab/PhenoSnap/archive/refs/heads/main.zip`
- Destination: `{baseDir}/third_party/phenosnap_main.zip`

Download method (pick first available):
- If `curl` exists:
  - `curl -L "https://github.com/WGLab/PhenoSnap/archive/refs/heads/main.zip" -o "{baseDir}/third_party/phenosnap_main.zip"`
- Else on Windows PowerShell:
  - `Invoke-WebRequest -Uri "https://github.com/WGLab/PhenoSnap/archive/refs/heads/main.zip" -OutFile "{baseDir}/third_party/phenosnap_main.zip"`

Unzip (choose by OS/tools):
- Windows PowerShell:
  - `Expand-Archive -Path "{baseDir}/third_party/phenosnap_main.zip" -DestinationPath "{baseDir}/third_party/phenosnap_unzip" -Force`
- macOS/Linux with unzip:
  - `unzip -o "{baseDir}/third_party/phenosnap_main.zip" -d "{baseDir}/third_party/phenosnap_unzip"`

If neither unzip nor Expand-Archive is available, use Python:
- `python3 -c "import zipfile; z=zipfile.ZipFile(r'{baseDir}/third_party/phenosnap_main.zip'); z.extractall(r'{baseDir}/third_party/phenosnap_unzip')"`

Then rename/move the extracted folder to `{baseDir}/PhenoSnap/`:
- The extracted folder is typically `{baseDir}/third_party/phenosnap_unzip/PhenoSnap-main`
- Move/rename to `{baseDir}/PhenoSnap/`

Final check:
- Verify `{baseDir}/PhenoSnap/extract_phenotypes.py` exists.
- If not found, stop and report the directory listing of `{baseDir}/PhenoSnap/` and `{baseDir}/third_party/phenosnap_unzip/`.

## 3) Dependency self-test and auto-install
Run from inside `{baseDir}/PhenoSnap/`.

### 3A) Smoke test importability
Run:
- `python3 -c "import importlib.util; spec=importlib.util.spec_from_file_location('extract_phenotypes','extract_phenotypes.py'); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); print('ok')"`

If it prints `ok`, proceed.

### 3B) If smoke test fails with missing module (ModuleNotFoundError / ImportError)
#### Step 1: Ensure pip exists for python3
Check:
- `python3 -m pip --version`

If that fails, try:
- `python3 -m ensurepip --upgrade`

Check again:
- `python3 -m pip --version`

If still failing, bootstrap pip via get-pip.py:
- Download `https://bootstrap.pypa.io/get-pip.py` to `{baseDir}/third_party/get-pip.py`
  - with curl:
    - `curl -L "https://bootstrap.pypa.io/get-pip.py" -o "{baseDir}/third_party/get-pip.py"`
  - or PowerShell:
    - `Invoke-WebRequest -Uri "https://bootstrap.pypa.io/get-pip.py" -OutFile "{baseDir}/third_party/get-pip.py"`
- Install:
  - `python3 "{baseDir}/third_party/get-pip.py"`
- Verify:
  - `python3 -m pip --version`

If pip still cannot be used, stop and report the error output.

#### Step 2: Install PhenoSnap dependencies
From `{baseDir}/PhenoSnap/`, run:
- `python3 -m pip install -r requirements.txt`

#### Step 3: Re-run smoke test once
Re-run:
- `python3 -c "import importlib.util; spec=importlib.util.spec_from_file_location('extract_phenotypes','extract_phenotypes.py'); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); print('ok')"`

If still failing, stop and return:
- the missing module name (from error)
- the command output
- recommended fix (use a venv/conda env; verify python3/pip; rerun pip install)

## 4) Prepare HPO OBO path
Resolve HPO OBO path in this order:
1) If env var `HPO_OBO_PATH` is set and file exists, use that.
2) Else use `{baseDir}/resources/hp.obo` if it exists.

If the resolved file does not exist:
- Stop and tell the user to place `hp.obo` at `{baseDir}/resources/hp.obo` or set `HPO_OBO_PATH` to its full path.

## 5) Write input file (redacted)
- Timestamp format: `YYYYMMDD_HHMMSS` (local time).
- Write redacted user text to:
  - `{baseDir}/artifacts/phenosnap_inputs/input_<TS>.txt`

## 6) Run extraction
From `{baseDir}/PhenoSnap/`, run:
- `python3 extract_phenotypes.py --input-file "{baseDir}/artifacts/phenosnap_inputs/input_<TS>.txt" --hpo-obo "<HPO_OBO_PATH>" --output "{baseDir}/artifacts/phenosnap_outputs/phenotypes_<TS>.json" --format json`

Validate:
- Output file exists
- Output file is non-empty

If validation fails:
- Return stderr/stdout
- Provide troubleshooting steps (missing hp.obo, permission issues, dependency issues)

## 7) Respond to user
Return a concise confirmation:
- Detected content: “phenotypes” and/or “medications”
- Input file path (redacted)
- Output file path (timestamped JSON)
- Note: no data uploaded; local-only
- Any warnings (e.g., missing hp.obo, PHI redaction/confirmation)

---

# Troubleshooting
- **PhenoSnap folder exists but script missing:** confirm `{baseDir}/PhenoSnap/extract_phenotypes.py` exists.
- **No git:** zip fallback should run; ensure curl/PowerShell is available for download.
- **Unzip fails:** use Python zipfile fallback.
- **pip missing:** ensurepip then get-pip.py steps above; consider installing Python with “pip” included.
- **Permission errors installing packages:** use a virtual environment:
  - `python3 -m venv .venv` then activate and rerun skill.
- **hp.obo missing:** place file at `{baseDir}/resources/hp.obo` or set `HPO_OBO_PATH`.

---

# Examples

## Example 1 (phenotypes + meds)
User:
- “Symptoms: developmental delay, seizures, ataxia. Meds: valproate 250 mg BID.”

Action:
- Write redacted input → run PhenoSnap → output `phenotypes_<TS>.json`

## Example 2 (meds only)
User:
- “Current meds: metformin 500mg daily, atorvastatin 20 mg qhs.”

Action:
- Extract medication entities/phenotype-related terms supported by PhenoSnap → output JSON

## Example 3 (should NOT trigger)
User:
- “What is the Human Phenotype Ontology and how is it used?”

Action:
- Do not run extraction; answer informationally outside this skill.