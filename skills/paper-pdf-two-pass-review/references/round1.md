You are doing FACT EXTRACTION ONLY.
Do not evaluate quality, do not conclude impact, and do not use external knowledge.
Use only the uploaded PDF.

Task: extract a structured fact sheet from this paper with evidence locations.
If information is missing, write `Not provided`.

Output format:

# A. Paper Basics
- Title:
- Task type (classification/detection/segmentation/generation/multimodal/etc.):
- One-sentence research question:
- Claimed contributions (as stated by authors):

# B. Method Facts
- End-to-end pipeline (input -> modules -> output):
- Key module 1:
  - Purpose:
  - Related equation:
  - Evidence:
- Key module 2:
- Key module 3:
- Training objectives/losses (list each):
- Inference procedure (if any):
- Time/space complexity statements (if any):

# C. Experiment Facts
- Datasets:
- Metrics:
- Baseline list:
- Main results (only key numbers):
- Ablation settings and numbers:
- Visualization experiment types:
- Efficiency results (params/FLOPs/speed):

# D. Reproducibility Facts
- Training hyperparameters (batch size/lr/epoch/optimizer):
- Data preprocessing and augmentation:
- Hardware setup:
- Random seeds/repeated runs:
- Code and model release status:

# E. Limitations and Failure Cases (author-stated)
- Limitation 1:
- Limitation 2:
- Failure scenarios:

Requirements:
1) Add evidence for each item when possible: [Evidence: p.X, Sec.Y, Fig/Table Z].
2) Record facts only. No judgments.
3) End with an "Information Gaps" list (missing details needed for faithful reproduction).
