# Progress log: med-info upgrades

## 2026-02-11/12
- Created planning files.
- Baseline: v0.1.1 already fixes NDC lookup correctness and prevents RxNorm fallback for NDC inputs.
- Implemented upgrades for v0.2.0:
  - Disambiguation: --candidates/--pick/--set-id
  - Recalls: --recalls (openFDA /drug/enforcement)
  - Shortages: --shortages (openFDA /drug/shortages)
  - Output shaping: --sections, --brief, --print-url
  - Debug URL log (api_key redacted)
- Tests:
  - metformin --candidates (prints 10 candidates, includes combo products)
  - metformin --pick 2 --brief --sections indications_and_usage,dosage_and_administration
  - set_id direct lookup: 05999192-ebc6-4198-bd1e-f46abbfb4f8a
  - metformin --recalls (returns multiple recalls)
  - amphetamine --shortages (returns current shortages)
  - Eliquis --sections contraindications,drug_interactions --brief --print-url
