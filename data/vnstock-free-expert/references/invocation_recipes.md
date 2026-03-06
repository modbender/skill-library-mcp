# Invocation Recipes

## 1) Quote history
```bash
python /Users/teahan/Projects/vscode-workspace/vn_stock_skill/skills/vnstock-free-expert/scripts/invoke_vnstock.py \
  --class-name Quote \
  --init-kwargs '{"source":"kbs","symbol":"VCB"}' \
  --method history \
  --method-kwargs '{"start":"2024-01-01","end":"2024-12-31","interval":"1D"}' \
  --outdir ./outputs
```

## 2) Company overview
```bash
python /Users/teahan/Projects/vscode-workspace/vn_stock_skill/skills/vnstock-free-expert/scripts/invoke_vnstock.py \
  --class-name Company \
  --init-kwargs '{"source":"kbs","symbol":"FPT"}' \
  --method overview \
  --method-kwargs '{}' \
  --outdir ./outputs
```

## 3) Finance ratio (year)
```bash
python /Users/teahan/Projects/vscode-workspace/vn_stock_skill/skills/vnstock-free-expert/scripts/invoke_vnstock.py \
  --class-name Finance \
  --init-kwargs '{"source":"kbs","symbol":"ACB"}' \
  --method ratio \
  --method-kwargs '{"period":"year"}' \
  --outdir ./outputs
```

## 4) Listing by group
```bash
python /Users/teahan/Projects/vscode-workspace/vn_stock_skill/skills/vnstock-free-expert/scripts/invoke_vnstock.py \
  --class-name Listing \
  --init-kwargs '{"source":"kbs"}' \
  --method symbols_by_group \
  --method-kwargs '{"group":"VN30"}' \
  --outdir ./outputs
```
